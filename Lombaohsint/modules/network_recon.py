import requests
import re
import json
import time
from pathlib import Path
from utils.obfuscation import get_random_ua
from utils.logger import logging

def run(target, level, config, api_wrapper, proxy_rotator):
    results = []
    cache_dir = Path("data/cache/phone_cache")
    cache_file = cache_dir / f"{target}_network.json"
    cache_dir.mkdir(parents=True, exist_ok=True)

    if cache_file.exists() and level != "BLACK":
        try:
            with open(cache_file, 'r') as f: return json.load(f)
        except: pass

    headers = {"User-Agent": get_random_ua()}
    proxies = proxy_rotator.get_current_proxy()

    # Extract domain from email or use as-is if it's a domain
    domain = target
    if "@" in target:
        domain = target.split("@")[1]

    # 1. Subdomain enumeration via Amass (simulated via API)
    if config['api_keys']['shodan']:
        try:
            resp = requests.get(
                f"https://api.shodan.io/dns/domain/{domain}?key={config['api_keys']['shodan']}",
                headers=headers, proxies=proxies, timeout=8
            )
            if resp.status_code == 200:
                data = resp.json()
                for sub in data.get('data', []):
                    if isinstance(sub, str) and "." in sub:
                        results.append({
                            "type": "SHODAN_SUBDOMAIN",
                            "source": "Shodan DNS",
                            "data": {
                                "subdomain": sub,
                                "ip": "",
                                "ports": [],
                                "service": "DNS Record"
                            },
                            "risk": "LOW"
                        })
        except: pass

    # 2. Censys Subdomains
    if config['api_keys']['censys']:
        try:
            resp = requests.get(
                f"https://search.censys.io/api/v2/hosts/search?q=names%3A{domain}&per_page=5",
                auth=(config['api_keys']['censys'], ""),
                headers=headers, proxies=proxies, timeout=8
            )
            if resp.status_code == 200:
                data = resp.json()
                for hit in data.get('results', []):
                    for name in hit.get('names', []):
                        results.append({
                            "type": "CENSYS_SUBDOMAIN",
                            "source": "Censys",
                            "data": {
                                "subdomain": name,
                                "ip": hit.get('ip'),
                                "services": hit.get('services', []),
                                "certificate": hit.get('certificates', [])
                            },
                            "risk": "MEDIUM"
                        })
        except: pass

    # 3. crt.sh (SSL Certificates)
    try:
        resp = requests.get(f"https://crt.sh/?q=%.{domain}&output=json", headers=headers, proxies=proxies, timeout=8)
        if resp.status_code == 200:
            certs = resp.json()
            seen = set()
            for cert in certs:
                name = cert.get('name_value', '').strip()
                if name.endswith(domain) and name not in seen:
                    seen.add(name)
                    results.append({
                        "type": "CRTSH_SUBDOMAIN",
                        "source": "crt.sh",
                        "data": {
                            "subdomain": name,
                            "issued": cert.get('minimum_not_before', ''),
                            "issuer": cert.get('issuer_name', '')
                        },
                        "risk": "LOW"
                    })
    except: pass

    # 4. AWS S3 Bucket Guessing
    s3_buckets = [
        f"{domain}",
        f"prod-{domain}",
        f"staging-{domain}",
        f"dev-{domain}",
        f"backup-{domain}",
        f"static-{domain}",
        f"cdn-{domain}"
    ]
    for bucket in s3_buckets:
        try:
            resp = requests.head(f"https://{bucket}.s3.amazonaws.com", timeout=5, proxies=proxies)
            if resp.status_code == 403:
                results.append({
                    "type": "S3_BUCKET_FOUND",
                    "source": "AWS S3",
                    "data": {
                        "bucket": bucket,
                        "status": "Access Denied (likely exists)"
                    },
                    "risk": "HIGH"
                })
            elif resp.status_code == 200:
                results.append({
                    "type": "S3_BUCKET_EXPOSED",
                    "source": "AWS S3",
                    "data": {
                        "bucket": bucket,
                        "status": "PUBLICLY ACCESSIBLE"
                    },
                    "risk": "CRITICAL"
                })
        except: pass

    # Cache results
    if level == "BLACK":
        with open(cache_file, 'w') as f: json.dump(results, f, indent=2)

    return results
