import requests
import re
import json
import time
from stem import Signal
from stem.control import Controller
from utils.obfuscation import get_random_ua
from utils.logger import logging
from pathlib import Path

def renew_tor_ip():
    """Renew Tor circuit"""
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
            time.sleep(5)
    except:
        pass

def run(target, level, config, api_wrapper, proxy_rotator):
    results = []
    cache_dir = Path("data/cache/darkweb_cache")
    cache_file = cache_dir / f"{target.replace('@', '_at_')}.json"
    cache_dir.mkdir(parents=True, exist_ok=True)

    if cache_file.exists() and level != "BLACK":
        try:
            with open(cache_file, 'r') as f: return json.load(f)
        except: pass

    if not config.get("use_tor", False):
        return results

    headers = {"User-Agent": get_random_ua()}
    proxies = {
        "http": "socks5h://127.0.0.1:9050",
        "https": "socks5h://127.0.0.1:9050"
    }

    # Onion search endpoints (public mirrors)
    dark_sites = [
        "http://pastebinsxq3l3o.onion/search?q=",
        "http://breachforum24n6z.onion/search?q=",
        "http://leakbase2v3y4g.onion/search?q=",
        "http://darksearchio2u5m.onion/search?q="
    ]

    for site in dark_sites:
        try:
            query = target.replace("@", "%40").replace(".", "%2E")
            url = site + query
            resp = requests.get(url, headers=headers, proxies=proxies, timeout=15)
            if resp.status_code == 200 and len(resp.text) > 100:
                links = re.findall(r'(https?://[^\s"<>\]]+)', resp.text)
                snippets = re.findall(r'<div class="snippet">([^<]+)</div>', resp.text)
                for link in links[:3]:
                    snippet = snippets[0] if snippets else ""
                    results.append({
                        "type": "DARKWEB_LEAK",
                        "source": site,
                        "data": {
                            "link": link,
                            "snippet": snippet[:150] + "..." if len(snippet) > 150 else snippet,
                            "content_hash": hash(link + snippet)
                        },
                        "risk": "CRITICAL"
                    })
                renew_tor_ip()
                time.sleep(2)
        except Exception as e:
            logging.debug(f"Darkweb scrape failed on {site}: {e}")
            continue

    # Cache results
    if level == "BLACK":
        with open(cache_file, 'w') as f: json.dump(results, f, indent=2)

    return results
