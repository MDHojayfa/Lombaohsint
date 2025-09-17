import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Import the module to test
from modules.email_harvest import run

# Mock config and dependencies
@pytest.fixture
def mock_config():
    return {
        "api_keys": {
            "haveibeenpwned": "test_key_123",
            "github": "ghp_testkey456",
            "hunterio": "hunter_test_key",
            "intelx": "intelx_test_key"
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
    cache_dir = tmp_path / "data" / "cache" / "email_cache"
    cache_dir.mkdir(parents=True)
    return cache_dir

def test_email_harvest_no_findings(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test when no breaches or leaks are found."""
    target = "nonexistent@domain.com"

    with patch('requests.get') as mock_get:
        # Simulate empty responses from all APIs
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {}

        result = run(target, "GENTLE", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) == 0
        mock_get.assert_called()

def test_email_harvest_hibp_breach(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test HaveIBeenPwned breach detection."""
    target = "test@example.com"

    hibp_response = [
        {
            "Name": "Adobe",
            "Domain": "adobe.com",
            "BreachDate": "2013-10-04",
            "PwnCount": 150000000,
            "IsVerified": True,
            "IsFabricated": False,
            "IsSensitive": False
        }
    ]

    with patch('requests.get') as mock_get:
        # Mock HIBP response
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: hibp_response),
            MagicMock(status_code=404),  # PSBDMP
            MagicMock(status_code=404),  # GitHub
            MagicMock(status_code=404),  # Hunter.io
            MagicMock(status_code=404),  # IntelX
        ]

        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) == 1
        assert result[0]["type"] == "EMAIL_BREACH"
        assert result[0]["source"] == "HaveIBeenPwned"
        assert result[0]["data"]["name"] == "Adobe"
        assert result[0]["risk"] == "HIGH"

def test_email_harvest_pastebin_leak(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test PSBDMP pastebin leak detection."""
    target = "test@example.com"

    psbdmp_response = {
        "count": 1,
        "data": [
            {
                "url": "https://pastebin.com/raw/abc123",
                "date": "2024-05-20",
                "text": "password: secret123\nemail: test@example.com"
            }
        ]
    }

    with patch('requests.get') as mock_get:
        mock_get.side_effect = [
            MagicMock(status_code=404),  # HIBP
            MagicMock(status_code=200, json=lambda: psbdmp_response),
            MagicMock(status_code=404),  # GitHub
            MagicMock(status_code=404),  # Hunter.io
            MagicMock(status_code=404),  # IntelX
        ]

        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) == 1
        assert result[0]["type"] == "PASTEBIN_LEAK"
        assert result[0]["source"] == "PSBDMP"
        assert "password" in result[0]["data"]["text"]
        assert result[0]["risk"] == "MEDIUM"

def test_email_harvest_github_secret(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test GitHub API secret detection."""
    target = "test@example.com"

    github_response = {
        "total_count": 1,
        "items": [
            {
                "name": ".env",
                "path": "repo/.env",
                "repository": {"full_name": "user/repo"},
                "html_url": "https://github.com/user/repo/blob/main/.env",
                "text": "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE"
            }
        ]
    }

    with patch('requests.get') as mock_get:
        mock_get.side_effect = [
            MagicMock(status_code=404),  # HIBP
            MagicMock(status_code=404),  # PSBDMP
            MagicMock(status_code=200, json=lambda: github_response),
            MagicMock(status_code=404),  # Hunter.io
            MagicMock(status_code=404),  # IntelX
        ]

        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) == 1
        assert result[0]["type"] == "GITHUB_SECRET"
        assert result[0]["source"] == "GitHub API"
        assert "AKIA" in result[0]["data"]["snippet"]
        assert result[0]["risk"] == "CRITICAL"

def test_email_harvest_hunterio_verified(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test Hunter.io email verification."""
    target = "john.doe@company.com"

    hunter_response = {
        "data": {
            "emails": [
                {
                    "value": "john.doe@company.com",
                    "confidence": 95,
                    "first_name": "John",
                    "last_name": "Doe",
                    "role": "developer"
                }
            ]
        }
    }

    with patch('requests.get') as mock_get:
        mock_get.side_effect = [
            MagicMock(status_code=404),  # HIBP
            MagicMock(status_code=404),  # PSBDMP
            MagicMock(status_code=404),  # GitHub
            MagicMock(status_code=200, json=lambda: hunter_response),
            MagicMock(status_code=404),  # IntelX
        ]

        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) == 1
        assert result[0]["type"] == "HUNTERIO_VERIFIED"
        assert result[0]["source"] == "Hunter.io"
        assert result[0]["data"]["confidence"] == 95
        assert result[0]["risk"] == "LOW"

def test_email_harvest_intelx_leak(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test IntelX public leak detection."""
    target = "test@example.com"

    intelx_response = {
        "results": [
            {
                "title": "Leaked DB - Company XYZ",
                "date": "2024-06-01",
                "source": "leaksource.org",
                "count": 12000
            }
        ]
    }

    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = intelx_response

        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) == 1
        assert result[0]["type"] == "INTELX_LEAK"
        assert result[0]["source"] == "IntelX"
        assert result[0]["data"]["title"] == "Leaked DB - Company XYZ"
        assert result[0]["risk"] == "HIGH"

def test_email_harvest_cache_usage(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test that cache is used when level != BLACK."""
    target = "cached@test.com"
    cache_file = tmp_path / "data" / "cache" / "email_cache" / f"{target.replace('@', '_at_')}.json"
    cache_file.parent.mkdir(parents=True)

    # Write fake cached data
    cached_data = [{"type": "CACHED_FINDING", "source": "CACHE", "data": {}, "risk": "LOW"}]
    with open(cache_file, 'w') as f:
        json.dump(cached_data, f)

    with patch('requests.get') as mock_get:
        # If cache is used, no HTTP requests should be made
        result = run(target, "GENTLE", mock_config, mock_api_wrapper, mock_proxy_rotator)
        mock_get.assert_not_called()
        assert result == cached_data

def test_email_harvest_black_mode_caches(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test that BLACK mode writes to cache."""
    target = "blackmode@test.com"
    cache_file = tmp_path / "data" / "cache" / "email_cache" / f"{target.replace('@', '_at_')}.json"

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = []

        result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert cache_file.exists()
        with open(cache_file, 'r') as f:
            saved = json.load(f)
            assert len(saved) == 0
