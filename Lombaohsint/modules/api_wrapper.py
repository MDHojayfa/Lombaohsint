import requests
import time
from utils.logger import logging
from utils.obfuscation import get_random_ua

class APIWrapper:
    def __init__(self, config):
        self.config = config
        self.headers = {"User-Agent": get_random_ua()}
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def request(self, method, url, api_key_name=None, params=None, json_data=None, timeout=8):
        """
        Unified HTTP wrapper with retry, auth, proxy support.
        Uses proxy_rotator from main.py externally.
        """
        if api_key_name and self.config.get("api_keys", {}).get(api_key_name):
            if "Authorization" in url or "token" in url.lower():
                self.session.headers["Authorization"] = f"Bearer {self.config['api_keys'][api_key_name]}"
            elif "x-key" in url.lower():
                self.session.headers["x-key"] = self.config['api_keys'][api_key_name]
            else:
                if params is None:
                    params = {}
                params[api_key_name.replace("_key", "")] = self.config['api_keys'][api_key_name]

        retries = self.config.get("max_retries", 3)
        delay_base = self.config.get("retry_delay_base_sec", 2)

        for attempt in range(retries + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    timeout=timeout
                )
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    wait = delay_base * (2 ** attempt)
                    time.sleep(wait)
                    continue
                else:
                    raise Exception(f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                if attempt == retries:
                    logging.warning(f"API request failed after {retries+1} attempts: {e}")
                    return None
                time.sleep(delay_base * (2 ** attempt))

        return None
