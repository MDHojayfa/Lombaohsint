import requests
import phonenumbers
from phonenumbers import geocoder, carrier, parse
from urllib.parse import quote
import json
import time
from pathlib import Path
from utils.obfuscation import get_random_ua
from utils.logger import logging

def run(target, level, config, api_wrapper, proxy_rotator):
    results = []
    cache_dir = Path("data/cache/phone_cache")
    cache_file = cache_dir / f"{target.replace('+', '').replace('-', '').replace(' ', '')}.json"
    cache_dir.mkdir(parents=True, exist_ok=True)

    if cache_file.exists() and level != "BLACK":
        try:
            with open(cache_file, 'r') as f: return json.load(f)
        except: pass

    headers = {"User-Agent": get_random_ua()}
    proxies = proxy_rotator.get_current_proxy()

    # Normalize phone number
    try:
        parsed = parse(target, None)
        if not phonenumbers.is_valid_number(parsed):
            return results
        normalized = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except:
        return results

    # 1. NumVerify
    if config['api_keys']['numverify']:
        try:
            resp = requests.get(
                f"http://apilayer.net/api/validate?access_key={config['api_keys']['numverify']}&number={quote(normalized)}",
                headers=headers, proxies=proxies, timeout=8
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("valid"):
                    results.append({
                        "type": "NUMVERIFY_LOOKUP",
                        "source": "NumVerify",
                        "data": {
                            "number": data.get("number"),
                            "country_code": data.get("country_code"),
                            "location": data.get("location"),
                            "carrier": data.get("carrier"),
                            "line_type": data.get("line_type"),
                            "is_valid": True,
                            "is_roaming": data.get("roaming", False),
                            "is_prepaid": data.get("prepaid", False)
                        },
                        "risk": "LOW"
                    })
        except: pass

    # 2. Twilio Lookup
    if config['api_keys']['twilio']:
        try:
            resp = requests.get(
                f"https://lookups.twilio.com/v1/PhoneNumbers/{quote(normalized)}?Type=carrier&Type=caller-name",
                auth=(config['api_keys']['twilio'], ""),
                headers=headers, proxies=proxies, timeout=8
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("carrier"):
                    results.append({
                        "type": "TWILIO_LOOKUP",
                        "source": "Twilio",
                        "data": {
                            "number": data.get("phone_number"),
                            "carrier_name": data.get("carrier", {}).get("name"),
                            "carrier_type": data.get("carrier", {}).get("type"),
                            "caller_name": data.get("caller_name", {}).get("name") or "Unknown"
                        },
                        "risk": "LOW"
                    })
        except: pass

    # 3. RiskSeal (SIM Swap Detection)
    if config['api_keys']['riskseal']:
        try:
            resp = requests.get(
                f"https://api.riskseal.com/v1/phone/{quote(normalized)}",
                headers={"Authorization": f"Bearer {config['api_keys']['riskseal']}"},
                proxies=proxies,
                timeout=8
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("risk_score", 0) > 70:
                    results.append({
                        "type": "RISKSEAL_RISK",
                        "source": "RiskSeal",
                        "data": {
                            "risk_score": data.get("risk_score"),
                            "sim_swap_risk": data.get("sim_swap_risk", False),
                            "fraud_indicators": data.get("fraud_indicators", []),
                            "last_seen": data.get("last_seen")
                        },
                        "risk": "CRITICAL"
                    })
        except: pass

    # 4. Trestle Reverse Phone (Identity Match)
    if config['api_keys']['trestle']:
        try:
            resp = requests.get(
                f"https://api.trestle.io/v1/reverse-phone?number={quote(normalized)}",
                headers={"Authorization": f"Bearer {config['api_keys']['trestle']}"},
                proxies=proxies,
                timeout=8
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("identity"):
                    results.append({
                        "type": "TRESTLE_IDENTITY",
                        "source": "Trestle",
                        "data": {
                            "name": data.get("identity", {}).get("name"),
                            "address": data.get("identity", {}).get("address"),
                            "age": data.get("identity", {}).get("age"),
                            "associated_emails": data.get("identity", {}).get("emails", [])
                        },
                        "risk": "HIGH"
                    })
        except: pass

    # 5. Truecaller (via web scraping fallback — limited)
    if level == "BLACK":
        try:
            resp = requests.get(f"https://www.truecaller.com/search/{normalized[1:]}", headers=headers, proxies=proxies, timeout=8)
            if resp.status_code == 200 and "result" in resp.text.lower():
                results.append({
                    "type": "TRUECALLER_DETECTED",
                    "source": "Truecaller (Web)",
                    "data": {
                        "status": "Possible match found on public site",
                        "note": "No direct API access — use with caution"
                    },
                    "risk": "MEDIUM"
                })
        except: pass

    # Cache results if BLACK mode
    if level == "BLACK":
        with open(cache_file, 'w') as f: json.dump(results, f, indent=2)

    return results
