import requests
import phonenumbers
from phonenumbers import geocoder, carrier, parse, NumberParseException
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

    # --- STEP 1: PARSE AND VALIDATE PHONE NUMBER FOR ANY COUNTRY ---
    try:
        # Parse without assuming region — let phonenumbers auto-detect
        parsed = parse(target, None)
        if not phonenumbers.is_valid_number(parsed):
            return results
        normalized = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        country_code = phonenumbers.region_code_for_number(parsed)
        if not country_code:
            return results  # Invalid or unrecognizable number
    except NumberParseException:
        return results

    # --- STEP 2: USE NUMVERIFY (SUPPORTS 232 COUNTRIES) ---
    if config['api_keys']['numverify']:
        try:
            url = f"http://apilayer.net/api/validate?access_key={config['api_keys']['numverify']}&number={quote(normalized)}"
            resp = requests.get(url, headers=headers, proxies=proxies, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("valid"):
                    results.append({
                        "type": "NUMVERIFY_LOOKUP",
                        "source": "NumVerify",
                        "data": {
                            "number": data.get("number"),
                            "country_code": data.get("country_code", country_code),
                            "location": data.get("location", ""),
                            "carrier": data.get("carrier", ""),
                            "line_type": data.get("line_type", ""),
                            "is_valid": True,
                            "is_roaming": data.get("roaming", False),
                            "is_prepaid": data.get("prepaid", False),
                            "country_name": data.get("country_name", "")
                        },
                        "risk": "LOW"
                    })
        except Exception as e:
            logging.debug(f"NumVerify failed for {normalized}: {e}")

    # --- STEP 3: TWILIO LOOKUP (GLOBAL SUPPORT) ---
    if config['api_keys']['twilio']:
        try:
            url = f"https://lookups.twilio.com/v1/PhoneNumbers/{quote(normalized)}?Type=carrier&Type=caller-name"
            resp = requests.get(url, auth=(config['api_keys']['twilio'].split(':')[0], config['api_keys']['twilio'].split(':')[1]), headers=headers, proxies=proxies, timeout=8)
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
                            "caller_name": data.get("caller_name", {}).get("name") or "Unknown",
                            "country_code": data.get("country_code", country_code)
                        },
                        "risk": "LOW"
                    })
        except Exception as e:
            logging.debug(f"Twilio failed for {normalized}: {e}")

    # --- STEP 4: RISKSEAL (SIM SWAP + FRAUD DETECTION) ---
    if config['api_keys']['riskseal']:
        try:
            url = f"https://api.riskseal.com/v1/phone/{quote(normalized)}"
            resp = requests.get(url, headers={"Authorization": f"Bearer {config['api_keys']['riskseal']}"}, proxies=proxies, timeout=8)
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
                            "last_seen": data.get("last_seen"),
                            "country_code": country_code
                        },
                        "risk": "CRITICAL"
                    })
        except Exception as e:
            logging.debug(f"RiskSeal failed for {normalized}: {e}")

    # --- STEP 5: TRESTLE REVERSE PHONE (IDENTITY MATCH) ---
    if config['api_keys']['trestle']:
        try:
            url = f"https://api.trestle.io/v1/reverse-phone?number={quote(normalized)}"
            resp = requests.get(url, headers={"Authorization": f"Bearer {config['api_keys']['trestle']}"}, proxies=proxies, timeout=8)
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
                            "associated_emails": data.get("identity", {}).get("emails", []),
                            "country_code": country_code
                        },
                        "risk": "HIGH"
                    })
        except Exception as e:
            logging.debug(f"Trestle failed for {normalized}: {e}")

    # --- STEP 6: TRUECALLER WEB SCRAPE (WORLDWIDE) ---
    if level == "BLACK":
        try:
            # Remove + and leading zeros for URL
            clean_num = normalized[1:] if normalized.startswith('+') else normalized
            url = f"https://www.truecaller.com/search/{clean_num}"
            resp = requests.get(url, headers=headers, proxies=proxies, timeout=8)
            if resp.status_code == 200 and ("result" in resp.text.lower() or "profile" in resp.text.lower()):
                results.append({
                    "type": "TRUECALLER_DETECTED",
                    "source": "Truecaller (Web)",
                    "data": {
                        "status": "Possible match found on public site",
                        "note": "No direct API access — use with caution",
                        "country_code": country_code
                    },
                    "risk": "MEDIUM"
                })
        except Exception as e:
            logging.debug(f"Truecaller web scrape failed for {normalized}: {e}")

    # --- STEP 7: ADD COUNTRY NAME FROM PHONENUMBERS LIBRARY AS FALLBACK ---
    # If any API didn't return country name, add it from phonenumbers
    for result in results:
        if result["type"] == "NUMVERIFY_LOOKUP" and not result["data"].get("country_name"):
            try:
                country_name = geocoder.description_for_number(parsed, "en")
                if country_name:
                    result["data"]["country_name"] = country_name
            except:
                pass

    # --- CACHE RESULTS ONLY IN BLACK MODE ---
    if level == "BLACK":
        with open(cache_file, 'w') as f: json.dump(results, f, indent=2)

    return results
