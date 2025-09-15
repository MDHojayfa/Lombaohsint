import requests
import re
import json
import time
from pathlib import Path
from utils.obfuscation import get_random_ua
from utils.logger import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote

def run(target, level, config, api_wrapper, proxy_rotator):
    results = []
    cache_dir = Path("data/cache/username_cache")
    cache_file = cache_dir / f"{target}_social.json"
    cache_dir.mkdir(parents=True, exist_ok=True)

    if cache_file.exists() and level != "BLACK":
        try:
            with open(cache_file, 'r') as f: return json.load(f)
        except: pass

    headers = {"User-Agent": get_random_ua()}
    proxies = proxy_rotator.get_current_proxy()

    # Normalize target (remove @ if email)
    username = target
    if "@" in target:
        username = target.split("@")[0]

    # 1. LinkedIn — Search by name/email
    try:
        resp = requests.get(
            f"https://www.linkedin.com/search/results/all/?keywords={quote(username)}",
            headers=headers,
            proxies=proxies,
            timeout=8
        )
        if resp.status_code == 200 and "linkedin.com/in/" in resp.text:
            links = re.findall(r'https://www\.linkedin\.com/in/[^"\s]+', resp.text)
            for link in links[:3]:
                if "/in/" in link and len(link) > 50:
                    results.append({
                        "type": "LINKEDIN_PROFILE",
                        "source": "LinkedIn",
                        "data": {
                            "url": link,
                            "name": link.split("/")[-1].replace("-", " ").title(),
                            "status": "Public profile found"
                        },
                        "risk": "LOW"
                    })
    except: pass

    # 2. Twitter/X — Search
    try:
        resp = requests.get(
            f"https://twitter.com/{username}",
            headers=headers,
            proxies=proxies,
            timeout=8
        )
        if resp.status_code == 200 and "<title>" in resp.text and username.lower() in resp.text.lower():
            results.append({
                "type": "TWITTER_PROFILE",
                "source": "Twitter/X",
                "data": {
                    "url": f"https://twitter.com/{username}",
                    "bio": resp.text[resp.text.find("<p class=\"css-901oao r-hkyrab r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0\">"):][:300].split("</p>")[0] if "<p class=\"css-901oao" in resp.text else "",
                    "followers": re.search(r'(\d+\.?\d*[MK]?)\s*Followers', resp.text),
                    "following": re.search(r'(\d+\.?\d*[MK]?)\s*Following', resp.text)
                },
                "risk": "LOW"
            })
    except: pass

    # 3. Instagram — Public profile check
    try:
        resp = requests.get(
            f"https://instagram.com/{username}",
            headers=headers,
            proxies=proxies,
            timeout=8
        )
        if resp.status_code == 200 and '"edge_followed_by"' in resp.text:
            followers_match = re.search(r'"edge_followed_by":{"count":(\d+)}', resp.text)
            bio_match = re.search(r'"biography":"([^"]+)"', resp.text)
            results.append({
                "type": "INSTAGRAM_PROFILE",
                "source": "Instagram",
                "data": {
                    "url": f"https://instagram.com/{username}",
                    "followers": followers_match.group(1) if followers_match else "Unknown",
                    "bio": bio_match.group(1).replace("\\n", " ") if bio_match else ""
                },
                "risk": "LOW"
            })
    except: pass

    # 4. Facebook — Via mutuals (limited, no login)
    try:
        resp = requests.get(
            f"https://www.facebook.com/public/{username}",
            headers=headers,
            proxies=proxies,
            timeout=8
        )
        if resp.status_code == 200 and "facebook.com/" in resp.text and username.lower() in resp.text.lower():
            links = re.findall(r'https://www\.facebook\.com/[a-zA-Z0-9._-]+', resp.text)
            for link in links[:3]:
                if "/profile.php" not in link and "/pages/" not in link:
                    results.append({
                        "type": "FACEBOOK_PUBLIC",
                        "source": "Facebook",
                        "data": {
                            "url": link,
                            "note": "Public profile found via search — may require mutual connection to view full details"
                        },
                        "risk": "MEDIUM"
                    })
    except: pass

    # 5. GitHub Profile (if username matches)
    if username != target:
        try:
            resp = requests.get(f"https://github.com/{username}", headers=headers, proxies=proxies, timeout=8)
            if resp.status_code == 200 and "<title>" in resp.text and username in resp.text:
                avatar = re.search(r'<img.*?class="avatar".*?src="(.*?)"', resp.text)
                name = re.search(r'<span class="p-name vcard-fullname d-block overflow-hidden">([^<]+)</span>', resp.text)
                results.append({
                    "type": "GITHUB_SOCIAL",
                    "source": "GitHub",
                    "data": {
                        "url": f"https://github.com/{username}",
                        "name": name.group(1).strip() if name else "",
                        "avatar": avatar.group(1) if avatar else "",
                        "repos": re.search(r'(\d+)\s*repositories', resp.text),
                        "followers": re.search(r'(\d+)\s*followers', resp.text)
                    },
                    "risk": "LOW"
                })
        except: pass

    # 6. TikTok (if username is valid)
    try:
        resp = requests.get(f"https://www.tiktok.com/@{username}", headers=headers, proxies=proxies, timeout=8)
        if resp.status_code == 200 and '"userId"' in resp.text:
            results.append({
                "type": "TIKTOK_PROFILE",
                "source": "TikTok",
                "data": {
                    "url": f"https://tiktok.com/@{username}",
                    "status": "Profile exists"
                },
                "risk": "LOW"
            })
    except: pass

    # Cache results
    if level == "BLACK":
        with open(cache_file, 'w') as f: json.dump(results, f, indent=2)

    return results
