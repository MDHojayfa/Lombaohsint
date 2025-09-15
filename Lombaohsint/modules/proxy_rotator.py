import random
import time
from utils.logger import logging

class ProxyRotator:
    def __init__(self, config):
        self.config = config
        self.proxies = config.get("proxy_list", [])
        self.use_tor = config.get("use_tor", False)
        self.current_index = -1
        self.last_rotation = 0
        self.rotation_interval = 30  # seconds

    def get_current_proxy(self):
        now = time.time()
        if self.use_tor and (now - self.last_rotation) > self.rotation_interval:
            # Tor rotation handled externally via stem
            self.last_rotation = now

        if not self.proxies:
            return None

        if len(self.proxies) == 1:
            return {"http": self.proxies[0], "https": self.proxies[0]}

        # Rotate index
        self.current_index = (self.current_index + 1) % len(self.proxies)
        proxy_url = self.proxies[self.current_index]
        return {"http": proxy_url, "https": proxy_url}

    def rotate(self):
        """Force immediate proxy rotation"""
        self.last_rotation = 0
