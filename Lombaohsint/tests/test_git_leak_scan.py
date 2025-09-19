import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from modules.git_leak_scan import run

@pytest.fixture
def mock_config():
    return {
        "api_keys": {
            "github": "ghp_testkey"
        },
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

def test_git_leak_scan_no_api_key(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test without GitHub API key."""
    mock_config["api_keys"]["github"] = ""
    target = "test@example.com"
    with patch('requests.get') as mock_get:
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        mock_get.assert_not_called()
        assert len(result) == 0

def test_git_leak_scan_github_secret_found(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test GitHub API returns secret leak."""
    target = "test@example.com"
    github_resp = {
        "total_count": 1,
        "items": [{
            "name": ".env",
            "path": "repo/.env",
            "repository": {"full_name": "user/repo"},
            "html_url": "https://github.com/user/repo/blob/main/.env",
            "text": "AWS_SECRET_ACCESS_KEY=abcd1234efgh5678ijkl9012mnop3456"
        }]
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = github_resp
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["type"] == "GITHUB_LEAK"
        assert result[0]["source"] == "GitHub API"
        assert "AWS_SECRET_ACCESS_KEY" in result[0]["data"]["snippet"]
        assert result[0]["risk"] == "CRITICAL"

def test_git_leak_scan_github_low_risk(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test GitHub search without sensitive keywords."""
    target = "test@example.com"
    github_resp = {
        "total_count": 1,
        "items": [{
            "name": "README.md",
            "path": "repo/README.md",
            "repository": {"full_name": "user/repo"},
            "html_url": "https://github.com/user/repo/blob/main/README.md",
            "text": "This is a public project by test@example.com"
        }]
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = github_resp
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["type"] == "GITHUB_LEAK"
        assert result[0]["risk"] == "HIGH"

def test_git_leak_scan_google_dork_fallback(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test Google Dork fallback when no API key or rate limit."""
    mock_config["api_keys"]["github"] = ""
    target = "test@example.com"
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = """
        <html>
            <h3>Results for "test@example.com site:github.com"</h3>
            <a href="https://github.com/user/repo/blob/main/config.ini">config.ini</a>
        </html>
        """
        result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["type"] == "GOOGLE_GITHUB_MATCH"
        assert "github.com" in result[0]["data"]["url"]
        assert result[0]["risk"] == "MEDIUM"

def test_git_leak_scan_cache_usage(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test cache usage in non-BLACK mode."""
    target = "cached_user@example.com"
    cache_file = tmp_path / "data" / "cache" / "username_cache" / f"{target.replace('@', '_at_')}_git.json"
    cache_file.parent.mkdir(parents=True)
    cached_data = [{"type": "CACHED_GIT", "source": "CACHE", "data": {}, "risk": "LOW"}]
    with open(cache_file, 'w') as f:
        json.dump(cached_data, f)
    with patch('requests.get') as mock_get:
        result = run(target, "GENTLE", mock_config, mock_api_wrapper, mock_proxy_rotator)
        mock_get.assert_not_called()
        assert result == cached_data

def test_git_leak_scan_black_mode_caches(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test BLACK mode writes to cache."""
    target = "blackmode@example.com"
    cache_file = tmp_path / "data" / "cache" / "username_cache" / f"{target.replace('@', '_at_')}_git.json"
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "total_count": 1,
            "items": [{
                "name": "secrets.txt",
                "path": "repo/secrets.txt",
                "repository": {"full_name": "user/repo"},
                "html_url": "https://github.com/user/repo/blob/main/secrets.txt",
                "text": "KEY=abc123"
            }]
        }
        result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert cache_file.exists()
        with open(cache_file, 'r') as f:
            saved = json.load(f)
            assert len(saved) == 1
            assert saved[0]["type"] == "GITHUB_LEAK"
            assert "KEY=abc123" in saved[0]["data"]["snippet"]
