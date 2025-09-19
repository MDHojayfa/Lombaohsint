import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from modules.darkweb_scrape import run

@pytest.fixture
def mock_config():
    return {
        "api_keys": {},
        "use_tor": True,
        "proxy_rotation_enabled": False,
        "level": "BLACK"
    }

@pytest.fixture
def mock_api_wrapper():
    return MagicMock()

@pytest.fixture
def mock_proxy_rotator():
    return MagicMock()

@pytest.fixture
def mock_cache_dir(tmp_path):
    cache_dir = tmp_path / "data" / "cache" / "darkweb_cache"
    cache_dir.mkdir(parents=True)
    return cache_dir

def test_darkweb_scrape_disabled_no_tor(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test no scraping if Tor is disabled."""
    mock_config["use_tor"] = False
    result = run("test@example.com", "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)
    assert len(result) == 0

def test_darkweb_scrape_onion_site_found(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test successful scrape from onion mirror."""
    target = "test@example.com"

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = """
        <html>
            <div class="snippet">Email: test@example.com | Password: P@ssw0rd123</div>
            <a href="http://pastebinsxq3l3o.onion/view/abc123">View Leak</a>
        </html>
        """

        result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) == 1
        assert result[0]["type"] == "DARKWEB_LEAK"
        assert result[0]["source"] == "http://pastebinsxq3l3o.onion/search?q="
        assert "test@example.com" in result[0]["data"]["snippet"]
        assert "abc123" in result[0]["data"]["link"]
        assert result[0]["risk"] == "CRITICAL"

def test_darkweb_scrape_multiple_sites(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test scanning multiple .onion sites."""
    target = "test@example.com"

    def side_effect(url, **kwargs):
        if "pastebinsxq3l3o" in url:
            return MagicMock(status_code=200, text="<html><div class='snippet'>Leak 1</div><a href='http://pastebinsxq3l3o.onion/view/1'>Link</a></html>")
        elif "breachforum" in url:
            return MagicMock(status_code=200, text="<html><div class='snippet'>Leak 2</div><a href='http://breachforum24n6z.onion/view/2'>Link</a></html>")
        else:
            return MagicMock(status_code=404)

    with patch('requests.get') as mock_get:
        mock_get.side_effect = side_effect

        result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) == 2
        assert any(r["source"] == "http://pastebinsxq3l3o.onion/search?q=" for r in result)
        assert any(r["source"] == "http://breachforum24n6z.onion/search?q=" for r in result)

def test_darkweb_scrape_cache_usage(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test cache usage in non-BLACK mode."""
    target = "cached_email@example.com"
    cache_file = tmp_path / "data" / "cache" / "darkweb_cache" / f"{target.replace('@', '_at_')}.json"
    cache_file.parent.mkdir(parents=True)
    cached_data = [{"type": "CACHED_DARKWEB", "source": "CACHE", "data": {}, "risk": "LOW"}]
    with open(cache_file, 'w') as f:
        json.dump(cached_data, f)
    with patch('requests.get') as mock_get:
        result = run(target, "GENTLE", mock_config, mock_api_wrapper, mock_proxy_rotator)
        mock_get.assert_not_called()
        assert result == cached_data

def test_darkweb_scrape_black_mode_caches(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test BLACK mode writes to cache."""
    target = "blackmode@example.com"
    cache_file = tmp_path / "data" / "cache" / "darkweb_cache" / f"{target.replace('@', '_at_')}.json"
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<html><div class='snippet'>Found it</div><a href='http://example.onion/view/1'>Link</a></html>"
        result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert cache_file.exists()
        with open(cache_file, 'r') as f:
            saved = json.load(f)
            assert len(saved) == 1
            assert saved[0]["type"] == "DARKWEB_LEAK"
            assert "Found it" in saved[0]["data"]["snippet"]
