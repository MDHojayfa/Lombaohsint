import time
from unittest.mock import patch, MagicMock
import pytest

# Import the module to test
from modules.proxy_rotator import ProxyRotator

@pytest.fixture
def mock_config():
    return {
        "proxy_list": [
            "http://proxy1.example.com:8080",
            "http://proxy2.example.com:8080",
            "socks5://127.0.0.1:9050"
        ],
        "use_tor": True,
        "proxy_rotation_enabled": True
    }

def test_proxy_rotator_initialization(mock_config):
    """Test proxy rotator initializes with correct config."""
    rotator = ProxyRotator(mock_config)
    assert rotator.proxies == mock_config["proxy_list"]
    assert rotator.use_tor is True
    assert rotator.proxy_rotation_enabled is True
    assert rotator.current_index == -1
    assert rotator.last_rotation == 0

def test_proxy_rotator_get_current_proxy_first_call(mock_config):
    """Test first call returns first proxy."""
    rotator = ProxyRotator(mock_config)
    proxy = rotator.get_current_proxy()
    assert proxy == {"http": "http://proxy1.example.com:8080", "https": "http://proxy1.example.com:8080"}

def test_proxy_rotator_rotate_next_proxy(mock_config):
    """Test rotate moves to next proxy in list."""
    rotator = ProxyRotator(mock_config)
    proxy1 = rotator.get_current_proxy()
    proxy2 = rotator.get_current_proxy()
    proxy3 = rotator.get_current_proxy()
    proxy4 = rotator.get_current_proxy()

    assert proxy1 == {"http": "http://proxy1.example.com:8080", "https": "http://proxy1.example.com:8080"}
    assert proxy2 == {"http": "http://proxy2.example.com:8080", "https": "http://proxy2.example.com:8080"}
    assert proxy3 == {"http": "socks5://127.0.0.1:9050", "https": "socks5://127.0.0.1:9050"}
    assert proxy4 == {"http": "http://proxy1.example.com:8080", "https": "http://proxy1.example.com:8080"}  # Cycled back

def test_proxy_rotator_get_current_proxy_no_proxies(mock_config):
    """Test behavior when no proxies configured."""
    mock_config["proxy_list"] = []
    rotator = ProxyRotator(mock_config)
    proxy = rotator.get_current_proxy()
    assert proxy is None

def test_proxy_rotator_rotate_method(mock_config):
    """Test rotate() forces immediate rotation."""
    rotator = ProxyRotator(mock_config)
    proxy1 = rotator.get_current_proxy()
    rotator.rotate()  # Force rotation
    proxy2 = rotator.get_current_proxy()
    assert proxy1 != proxy2  # Should have changed due to force

def test_proxy_rotator_tor_rotation_disabled(mock_config):
    """Test Tor rotation is handled externally — only proxy rotation matters."""
    mock_config["use_tor"] = True
    rotator = ProxyRotator(mock_config)
    proxy1 = rotator.get_current_proxy()
    proxy2 = rotator.get_current_proxy()
    assert proxy1 != proxy2  # Rotates via proxy_list, not Tor
    # Tor circuit rotation is handled by darkweb_scrape.py — not here

def test_proxy_rotator_rotation_interval(mock_config):
    """Test internal timing doesn’t affect get_current_proxy() — rotation is manual or sequential."""
    rotator = ProxyRotator(mock_config)
    proxy1 = rotator.get_current_proxy()
    proxy2 = rotator.get_current_proxy()
    proxy3 = rotator.get_current_proxy()
    assert proxy1 != proxy2
    assert proxy2 != proxy3
    # Rotation is sequential, not timed — controlled by caller
