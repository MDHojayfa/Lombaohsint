import requests
import re
import json
import time
from pathlib import Path
from utils.obfuscation import get_random_ua
from utils.logger import logging

def run(target, level, config, api_wrapper, proxy_rotator):
    results = []
    cache_dir = Path("data/cache/username_cache")
    cache_file = cache_dir / f"{target.replace('@', '_at_')}_git.json"
    cache_dir.mkdir(parents=True, exist_ok=True)

    if cache_file.exists() and level != "BLACK":
        try:
            with open(cache_file, 'r') as f: return json.load(f)
        except: pass

    headers = {"User-Agent": get_random_ua()}
    proxies = proxy_rotator.get_current_proxy()

    # GitHub API search for secrets tied to email/username
    if config['api_keys']['github']:
        queries = [
            f"{target} in:file repo:openstack",
            f"{target} in:file repo:github",
            f"{target} type:commit",
            f"{target} extension:env",
            f"{target} extension:yaml",
            f"{target} extension:yml",
            f"{target} extension:conf",
            f"{target} extension:ini",
            f"{target} extension:json",
            f"{target} password",
            f"{target} token",
            f"{target} key",
            f"{target} secret"
        ]

        for query in queries:
            try:
                resp = requests.get(
                    f"https://api.github.com/search/code?q={query}",
                    headers={**headers, "Authorization": f"token {config['api_keys']['github']}"},
                    proxies=proxies,
                    timeout=8
                )
                if resp.status_code == 200:
                    items = resp.json().get('items', [])
                    for item in items[:5]:
                        path = item['path']
                        repo = item['repository']['full_name']
                        url = item['html_url']
                        content = item['name']

                        # Extract potential secrets from context
                        snippet = item.get('text', '')[:200].strip()
                        if any(k in snippet.lower() for k in ['key', 'token', 'secret', 'password', 'api', 'auth']):
                            risk = "CRITICAL"
                        else:
                            risk = "HIGH"

                        results.append({
                            "type": "GITHUB_LEAK",
                            "source": "GitHub API",
                            "data": {
                                "file": path,
                                "repo": repo,
                                "url": url,
                                "snippet": snippet,
                                "commit_sha": item.get('sha', '')
                            },
                            "risk": risk
                        })
            except Exception as e:
                logging.warning(f"GitHub scan failed for '{query}': {e}")
                continue

    # If no API key, try public GitHub search (limited)
    elif level == "BLACK":
        queries = [f"{target} site:github.com"]
        for query in queries:
            try:
                resp = requests.get(
                    f"https://www.google.com/search?q={query}",
                    headers=headers,
                    proxies=proxies,
                    timeout=8
                )
                if resp.status_code == 200 and "github.com" in resp.text:
                    urls = re.findall(r'https?://github\.com/[^\s"<>]+', resp.text)
                    for url in urls[:3]:
                        if "/blob/" in url or "/tree/" in url:
                            results.append({
                                "type": "GOOGLE_GITHUB_MATCH",
                                "source": "Google",
                                "data": {
                                    "url": url,
                                    "note": "Public exposure detected via Google index"
                                },
                                "risk": "MEDIUM"
                            })
            except: pass

    # Cache results
    if level == "BLACK":
        with open(cache_file, 'w') as f: json.dump(results, f, indent=2)

    return results
