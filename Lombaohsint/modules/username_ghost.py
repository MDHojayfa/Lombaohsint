import requests
import re
import json
import time
from pathlib import Path
from utils.obfuscation import get_random_ua
from utils.logger import logging
from maigret.maigret import check_username
import waybackpy  # Only import the main package

def run(target, level, config, api_wrapper, proxy_rotator):
    results = []
    cache_dir = Path("data/cache/username_cache")
    cache_file = cache_dir / f"{target}.json"
    cache_dir.mkdir(parents=True, exist_ok=True)

    if cache_file.exists() and level != "BLACK":
        try:
            with open(cache_file, 'r') as f: return json.load(f)
        except: pass

    headers = {"User-Agent": get_random_ua()}
    proxies = proxy_rotator.get_current_proxy()

    # Maigret — scans 1200+ sites
    try:
        results_list = check_username(target, silent=True, timeout=5)
        for site, data in results_list.items():
            if data.get("exists"):
                url = data.get("url")
                status = "active"

                # Archive via Wayback Machine (correct usage)
                archived_url = None
                if level == "BLACK":
                    try:
                        w = waybackpy.WaybackMachine(url, headers["User-Agent"])
                        archived_url = w.save().archive_url
                    except Exception as e:
                        logging.warning(f"Wayback save failed for {url}: {e}")

                results.append({
                    "type": "USERNAME_FOUND",
                    "source": site,
                    **"data": {
                        "url": url,
                        "status": status,
                        "last_seen": data.get("timestamp", ""),
                        "archived_url": archived_url,
                        "bio": data.get("description", "")
                    },
                    "risk": "LOW"
                })
            elif data.get("error") and "not found" in str(data.get("error")).lower():
                results.append({
                    "type": "USERNAME_NOT_FOUND",
                    "source": site,
                    "data": {
                        "status": "deleted",
                        "reason": data.get("error", "Not found")
                    },
                    "risk": "LOW"
                })
    except Exception as e:
        logging.warning(f"Maigret failed for {target}: {e}")

    # Search for deleted profiles on Wayback Machine
    if level == "BLACK":
        domains = ["facebook.com", "instagram.com", "twitter.com", "linkedin.com", "github.com"]
        for domain in domains:
            try:
                url = f"https://{domain}/{target}"
                w = waybackpy.WaybackMachine(url, headers["User-Agent"])
                snapshots = w.archives()
                for snap in snapshots[:3]:
                    results.append({
                        "type": "WAYBACK_ARCHIVED",
                        "source": "Wayback Machine",
                        "data": {
                            "url": snap.original(),
                            "timestamp": snap.timestamp(),
                            "archive_link": snap.archive_url()
                        },
                        "risk": "MEDIUM"
                    })
            except Exception as e:
                logging.debug(f"Wayback archive search failed for {domain}/{target}: {e}")
                continue

    # Google Dorking for username
    if level == "BLACK":
        dorks = [
            f"intitle:\"{target}\"",
            f"site:github.com \"{target}\"",
            f"site:twitter.com \"{target}\"",
            f"site:instagram.com \"{target}\"",
            f"\"{target}\" \"email\"",
            f"\"{target}\" \"phone\""
        ]
        for dork in dorks:
            try:
                resp = requests.get(
                    f"https://www.google.com/search?q={dork}",
                    headers=headers, proxies=proxies, timeout=8
                )
                if resp.status_code == 200 and target in resp.text:
                    urls = re.findall(r'(https?://[^\s"<>\]]+)', resp.text)
                    for url in urls[:3]:
                        results.append({
                            "type": "GOOGLE_DORK_MATCH",
                            "source": "Google",
                            "data": {
                                "dork": dork,
                                "url": url,
                                "snippet": resp.text[resp.text.find(target):resp.text.find(target)+200]
                            },
                            "risk": "LOW"
                        })
            except Exception as e:
                logging.debug(f"Google dork failed for '{dork}': {e}")
                continue

    # Cache results
    if level == "BLACK":
        with open(cache_file, 'w') as f: json.dump(results, f, indent=2)

    return results
