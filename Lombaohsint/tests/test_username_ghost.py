import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from modules.username_ghost import run

@pytest.fixture
def mock_config():
    return {
        "api_keys": {},
        "use_tor": False,
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
    cache_dir = tmp_path / "data" / "cache" / "username_cache"
    cache_dir.mkdir(parents=True)
    return cache_dir

def test_username_ghost_maigret_found(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test Maigret finds username on multiple platforms."""
    target = "john_doe"

    maigret_results = {
        "github": {"exists": True, "url": "https://github.com/john_doe", "timestamp": "2024-05-10"},
        "instagram": {"exists": True, "url": "https://instagram.com/john_doe", "timestamp": "2024-05-11"},
        "twitter": {"exists": True, "url": "https://twitter.com/john_doe", "timestamp": "2024-05-12"},
        "linkedin": {"exists": False, "error": "Profile not found"},
        "facebook": {"exists": False, "error": "Account disabled"}
    }

    with patch('maigret.maigret.check_username') as mock_check:
        mock_check.return_value = maigret_results

        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) == 3  # github, instagram, twitter
        assert any(r["type"] == "USERNAME_FOUND" and r["source"] == "github" for r in result)
        assert any(r["type"] == "USERNAME_FOUND" and r["source"] == "instagram" for r in result)
        assert any(r["type"] == "USERNAME_FOUND" and r["source"] == "twitter" for r in result)
        assert all(r["risk"] == "LOW" for r in result)

def test_username_ghost_maigret_deleted(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test Maigret reports deleted accounts."""
    target = "old_user"

    maigret_results = {
        "tumblr": {"exists": False, "error": "User not found"},
        "reddit": {"exists": False, "error": "Account deleted"}
    }

    with patch('maigret.maigret.check_username') as mock_check:
        mock_check.return_value = maigret_results

        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) == 2
        assert result[0]["type"] == "USERNAME_NOT_FOUND"
        assert result[0]["source"] == "tumblr"
        assert "not found" in result[0]["data"]["reason"].lower()
        assert result[1]["type"] == "USERNAME_NOT_FOUND"
        assert result[1]["source"] == "reddit"
        assert "deleted" in result[1]["data"]["reason"].lower()

def test_username_ghost_wayback_archived(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test Wayback Machine archive detection (BLACK mode)."""
    target = "john_doe"

    with patch('maigret.maigret.check_username') as mock_check:
        mock_check.return_value = {}

    with patch('waybackpy.WaybackMachineSaveAPI') as mock_save_api:
        mock_instance = MagicMock()
        mock_save_api.return_value = mock_instance
        mock_instance.save.return_value = "https://web.archive.org/web/20230101000000/https://github.com/john_doe"
        mock_instance.snapshots.return_value = [
            type('obj', (object,), {'url': 'https://github.com/john_doe', 'timestamp': '20230101000000', 'archive_url': 'https://web.archive.org/web/20230101000000/https://github.com/john_doe'})()
        ]

        result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) >= 1
        assert any(r["type"] == "WAYBACK_ARCHIVED" for r in result)
        assert "web.archive.org" in result[0]["data"]["archive_link"]

def test_username_ghost_google_dork_match(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test Google Dorking finds matches."""
    target = "john_doe"

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<html><body>...john_doe...<a href='https://github.com/john_doe'>...</a></body></html>"

        result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) >= 1
        assert any(r["type"] == "GOOGLE_DORK_MATCH" for r in result)
        assert "github.com" in result[0]["data"]["url"]

def test_username_ghost_cache_usage(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test cache usage in non-BLACK mode."""
    target = "cached_user"
    cache_file = tmp_path / "data" / "cache" / "username_cache" / f"{target}.json"
    cache_file.parent.mkdir(parents=True)
    cached_data = [{"type": "CACHED_USER", "source": "CACHE", "data": {}, "risk": "LOW"}]
    with open(cache_file, 'w') as f:
        json.dump(cached_data, f)
    with patch('maigret.maigret.check_username') as mock_check:
        with patch('requests.get') as mock_get:
            result = run(target, "GENTLE", mock_config, mock_api_wrapper, mock_proxy_rotator)
            mock_check.assert_not_called()
            mock_get.assert_not_called()
            assert result == cached_data

def test_username_ghost_black_mode_caches(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test BLACK mode writes to cache."""
    target = "blackmode_user"
    cache_file = tmp_path / "data" / "cache" / "username_cache" / f"{target}.json"

    with patch('maigret.maigret.check_username') as mock_check:
        mock_check.return_value = {
            "github": {"exists": True, "url": "https://github.com/blackmode_user", "timestamp": "2024-06-01"}
        }

        result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert cache_file.exists()
        with open(cache_file, 'r') as f:
            saved = json.load(f)
            assert len(saved) == 1
            assert saved[0]["type"] == "USERNAME_FOUND"
            assert saved[0]["source"] == "github"
