import requests
import time
from utils.logger import logging
from utils.obfuscation import get_random_ua

class APIWrapper:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": get_random_ua(),
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9"
        })
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay_base = config.get("retry_delay_base_sec", 2)

    def request(self, method, url, api_key_name=None, params=None, json_data=None, timeout=8):
        """
        Unified HTTP wrapper with retry logic, auth injection, and proxy support.
        Uses external proxy_rotator for dynamic proxy rotation.
        """
        if api_key_name and self.config.get("api_keys", {}).get(api_key_name):
            key = self.config["api_keys"][api_key_name]
            if "Authorization" in url or "token" in url.lower():
                self.session.headers["Authorization"] = f"Bearer {key}"
            elif "x-key" in url.lower():
                self.session.headers["x-key"] = key
            else:
                if params is None:
                    params = {}
                param_key = api_key_name.replace("_key", "")
                params[param_key] = key

        for attempt in range(self.max_retries + 1):
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
                    wait_time = self.retry_delay_base * (2 ** attempt)
                    logging.warning(f"Rate limited on {url}. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                if attempt == self.max_retries:
                    logging.warning(f"API request failed after {self.max_retries+1} attempts: {e}")
                    return None
                time.sleep(self.retry_delay_base * (2 ** attempt))
        return None
