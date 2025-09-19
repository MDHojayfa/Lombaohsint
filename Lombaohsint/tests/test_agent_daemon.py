import time
import threading
from unittest.mock import patch, MagicMock
import pytest
from modules.agent_daemon import run

@pytest.fixture
def mock_config():
    return {
        "agent_enabled": True,
        "agent_interval_minutes": 1,
        "agent_notify_telegram": False,
        "telegram_bot_token": "",
        "telegram_chat_id": ""
    }

def test_agent_daemon_disabled(mock_config):
    """Test daemon does nothing if disabled."""
    mock_config["agent_enabled"] = False
    with patch('time.sleep') as mock_sleep:
        run(mock_config)
        mock_sleep.assert_not_called()

def test_agent_daemon_no_telegram(mock_config):
    """Test daemon runs without Telegram alerting."""
    with patch('time.sleep') as mock_sleep, \
         patch('modules.agent_daemon.datetime') as mock_datetime:

        mock_datetime.now.return_value.strftime.return_value = "2025-09-15 10:30:00"
        mock_sleep.side_effect = KeyboardInterrupt()  # simulate stop after one loop

        run(mock_config)

        mock_sleep.assert_called_once_with(60)  # 1 minute

def test_agent_daemon_telegram_alert(mock_config):
    """Test Telegram alert sent when enabled."""
    mock_config["agent_notify_telegram"] = True
    mock_config["telegram_bot_token"] = "123:ABC"
    mock_config["telegram_chat_id"] = "789"

    with patch('time.sleep') as mock_sleep, \
         patch('modules.agent_daemon.requests.post') as mock_post, \
         patch('modules.agent_daemon.datetime') as mock_datetime:

        mock_datetime.now.return_value.strftime.return_value = "2025-09-15 10:30:00"
        mock_sleep.side_effect = KeyboardInterrupt()

        run(mock_config)

        mock_post.assert_called_once_with(
            "https://api.telegram.org/bot123:ABC/sendMessage",
            data={"chat_id": "789", "text": "[ALERT] New breach detected: test@example.com in NewLeak_2025"},
            timeout=5
        )

def test_agent_daemon_error_handling(mock_config):
    """Test daemon continues on API error."""
    mock_config["agent_notify_telegram"] = True
    mock_config["telegram_bot_token"] = "123:ABC"
    mock_config["telegram_chat_id"] = "789"

    with patch('time.sleep') as mock_sleep, \
         patch('modules.agent_daemon.requests.post') as mock_post, \
         patch('modules.agent_daemon.logging.warning') as mock_log:

        mock_post.side_effect = Exception("Network error")
        mock_sleep.side_effect = KeyboardInterrupt()

        run(mock_config)

        mock_log.assert_called_with("Failed to send Telegram alert: Network error")
