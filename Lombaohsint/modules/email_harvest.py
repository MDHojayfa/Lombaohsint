import requests
import re
import json
import time
from pathlib import Path
from utils.obfuscation import get_random_ua
from utils.logger import logging

def run(target, level, config, api_wrapper, proxy_rotator):
    results = []
    cache_dir = Path("data/cache/email_cache")
    cache_file = cache_dir / f"{target.replace('@', '_at_')}.json"
    cache_dir.mkdir(parents=True, exist_ok=True)

    if cache_file.exists() and level != "BLACK":
        try:
            with open(cache_file, 'r') as f: return json.load(f)
        except: pass

    headers = {"User-Agent": get_random_ua()}
    proxies = proxy_rotator.get_current_proxy()

    # 1. HaveIBeenPwned
    if config['api_keys']['haveibeenpwned']:
        try:
            resp = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{target}", headers=headers, proxies=proxies, timeout=8)
            if resp.status_code == 200:
                breaches = resp.json()
                for b in breaches:
                    results.append({
                        "type": "EMAIL_BREACH",
                        "source": "HaveIBeenPwned",
                        "data": {
                            "name": b["Name"],
                            "domain": b["Domain"],
                            "breach_date": b["BreachDate"],
                            "pwn_count": b["PwnCount"],
                            "is_verified": b["IsVerified"]
                        },
                        "risk": "HIGH"
                    })
        except: pass

    # 2. Pastebin (PSBDMP API)
    try:
        resp = requests.get(f"https://psbdmp.ws/api/search/{target}", headers=headers, proxies=proxies, timeout=8)
        if resp.status_code == 200 and resp.json().get('count', 0) > 0:
            for item in resp.json().get('data', []):
                results.append({
                    "type": "PASTEBIN_LEAK",
                    "source": "PSBDMP",
                    "data": {
                        "url": item["url"],
                        "date": item["date"],
                        "text": item["text"][:100] + "..."
                    },
                    "risk": "MEDIUM"
                })
    except: pass

    # 3. GitHub Secrets (if API key provided)
    if config['api_keys']['github']:
        try:
            resp = requests.get(
                f"https://api.github.com/search/code?q={target}+in:file+repo:openstack",
                headers={**headers, "Authorization": f"token {config['api_keys']['github']}"}, 
                proxies=proxies, timeout=8
            )
            if resp.status_code == 200:
                items = resp.json().get('items', [])
                for item in items[:5]:
                    results.append({
                        "type": "GITHUB_SECRET",
                        "source": "GitHub API",
                        "data": {
                            "file": item['name'],
                            "path": item['path'],
                            "repo": item['repository']['full_name'],
                            "url": item['html_url']
                        },
                        "risk": "CRITICAL"
                    })
        except: pass

    # 4. Hunter.io (email verification via domain)
    if config['api_keys']['hunterio'] and '@' in target:
        domain = target.split('@')[1]
        try:
            resp = requests.get(
                f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={config['api_keys']['hunterio']}",
                headers=headers, proxies=proxies, timeout=8
            )
            if resp.status_code == 200:
                emails = resp.json().get('data', {}).get('emails', [])
                for email in emails:
                    if email['value'] == target:
                        results.append({
                            "type": "HUNTERIO_VERIFIED",
                            "source": "Hunter.io",
                            "data": {
                                "confidence": email['confidence'],
                                "first_name": email['first_name'],
                                "last_name": email['last_name'],
                                "role": email['role']
                            },
                            "risk": "LOW"
                        })
        except: pass

    # 5. IntelX (public leaks)
    if config['api_keys']['intelx']:
        try:
            resp = requests.post(
                "https://intellx.io/api/search",
                json={"term": target, "type": "email", "limit": 5},
                headers={"x-key": config['api_keys']['intelx']},
                proxies=proxies,
                timeout=8
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("results"):
                    for result in data["results"]:
                        results.append({
                            "type": "INTELX_LEAK",
                            "source": "IntelX",
                            "data": {
                                "title": result.get("title", ""),
                                "date": result.get("date", ""),
                                "source": result.get("source", ""),
                                "count": result.get("count", 0)
                            },
                            "risk": "HIGH"
                        })
        except: pass

    # Cache results if BLACK mode
    if level == "BLACK":
        with open(cache_file, 'w') as f: json.dump(results, f, indent=2)

    return results
