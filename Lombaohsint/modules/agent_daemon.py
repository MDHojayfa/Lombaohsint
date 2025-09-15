import time
import json
import threading
from pathlib import Path
from utils.logger import logging
from datetime import datetime

def run(config):
    """
    Runs as background daemon. Checks for new breaches every X minutes.
    Sends Telegram alert if enabled.
    This module is NOT called by main.py — it's designed to be launched separately.
    """
    if not config.get("agent_enabled", False):
        return

    log = logging.getLogger("lombaohsint")
    log.info("Agent daemon started.")

    breach_db_path = Path("data/breaches.sqlite")
    if not breach_db_path.exists():
        log.warning("breaches.sqlite not found. Daemon will not function.")
        return

    interval_minutes = config.get("agent_interval_minutes", 120)
    notify_telegram = config.get("agent_notify_telegram", False)
    telegram_bot_token = config.get("telegram_bot_token", "")
    telegram_chat_id = config.get("telegram_chat_id", "")

    while True:
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log.info(f"Daemon tick at {now}. Checking for new breaches...")

            # Simulate checking for new leaks (in real use: query HaveIBeenPwned or IntelX API)
            # For demo: just check if any new email appears in breaches.sqlite
            # In practice, this would compare against latest breach feeds.

            # Placeholder: simulate a new breach match
            # This would normally compare against an external feed
            new_match = {
                "email": "test@example.com",
                "leak_name": "NewLeak_2025",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "source": "daemon_check"
            }

            # If we had a way to detect NEW breaches, we'd alert here
            if new_match and notify_telegram and telegram_bot_token and telegram_chat_id:
                try:
                    import requests
                    msg = f"[ALERT] New breach detected: {new_match['email']} in {new_match['leak_name']}"
                    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
                    requests.post(url, data={"chat_id": telegram_chat_id, "text": msg}, timeout=5)
                    log.info(f"Telegram alert sent: {msg}")
                except Exception as e:
                    log.error(f"Failed to send Telegram alert: {e}")

            time.sleep(interval_minutes * 60)

        except KeyboardInterrupt:
            log.info("Agent daemon stopped by user.")
            break
        except Exception as e:
            log.error(f"Agent daemon error: {e}")
            time.sleep(60)
