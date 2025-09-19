import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from modules.network_recon import run

@pytest.fixture
def mock_config():
    return {
        "api_keys": {
            "shodan": "shodan_key",
            "censys": "censys_id:censys_secret"
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
    cache_dir = tmp_path / "data" / "cache" / "phone_cache"
    cache_dir.mkdir(parents=True)
    return cache_dir

def test_network_recon_domain_from_email(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test domain extraction from email."""
    target = "user@company.com"
    result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
    assert len(result) > 0

def test_network_recon_shodan_subdomains(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test Shodan DNS subdomain enumeration."""
    target = "company.com"
    shodan_resp = {
        "data": [
            "mail.company.com",
            "www.company.com",
            "admin.company.com"
        ]
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = shodan_resp
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 3
        assert all(r["type"] == "SHODAN_SUBDOMAIN" for r in result)
        assert any(r["data"]["subdomain"] == "mail.company.com" for r in result)
        assert all(r["risk"] == "LOW" for r in result)

def test_network_recon_censys_subdomains(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test Censys subdomain discovery."""
    target = "company.com"
    censys_resp = {
        "results": [
            {
                "names": ["api.company.com", "dev.company.com"],
                "ip": "93.184.216.34",
                "services": [{"port": 443, "protocol": "tcp"}],
                "certificates": []
            }
        ]
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = censys_resp
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 2
        assert any(r["data"]["subdomain"] == "api.company.com" for r in result)
        assert any(r["data"]["ip"] == "93.184.216.34" for r in result)
        assert all(r["risk"] == "MEDIUM" for r in result)

def test_network_recon_crtsh_certificates(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test crt.sh certificate-based subdomain discovery."""
    target = "company.com"
    crtsh_resp = [
        {
            "name_value": "*.company.com",
            "minimum_not_before": "2023-01-01",
            "issuer_name": "Let's Encrypt"
        },
        {
            "name_value": "app.company.com",
            "minimum_not_before": "2023-02-01",
            "issuer_name": "DigiCert"
        }
    ]
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = crtsh_resp
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 2
        assert any(r["type"] == "CRTSH_SUBDOMAIN" for r in result)
        assert any(r["data"]["subdomain"] == "*.company.com" for r in result)

def test_network_recon_s3_bucket_found(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test S3 bucket guess with 403 status (likely exists)."""
    target = "company.com"
    with patch('requests.head') as mock_head:
        mock_head.side_effect = [
            MagicMock(status_code=403),  # company.s3.amazonaws.com
            MagicMock(status_code=404),  # prod-company.s3.amazonaws.com
        ]
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["type"] == "S3_BUCKET_FOUND"
        assert result[0]["data"]["bucket"] == "company"
        assert result[0]["risk"] == "HIGH"

def test_network_recon_s3_bucket_exposed(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test S3 bucket guess with 200 status (publicly accessible)."""
    target = "company.com"
    with patch('requests.head') as mock_head:
        mock_head.side_effect = [
            MagicMock(status_code=200),  # company.s3.amazonaws.com
        ]
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["type"] == "S3_BUCKET_EXPOSED"
        assert result[0]["data"]["bucket"] == "company"
        assert result[0]["risk"] == "CRITICAL"

def test_network_recon_cache_usage(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test cache usage in non-BLACK mode."""
    target = "cached.domain.com"
    cache_file = tmp_path / "data" / "cache" / "phone_cache" / f"{target}_network.json"
    cache_file.parent.mkdir(parents=True)
    cached_data = [{"type": "CACHED_NETWORK", "source": "CACHE", "data": {}, "risk": "LOW"}]
    with open(cache_file, 'w') as f:
        json.dump(cached_data, f)
    with patch('requests.get') as mock_get:
        result = run(target, "GENTLE", mock_config, mock_api_wrapper, mock_proxy_rotator)
        mock_get.assert_not_called()
        assert result == cached_data

def test_network_recon_black_mode_caches(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test BLACK mode writes to cache."""
    target = "blackmode.com"
    cache_file = tmp_path / "data" / "cache" / "phone_cache" / f"{target}_network.json"
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "data": ["api.blackmode.com"]
        }
        result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert cache_file.exists()
        with open(cache_file, 'r') as f:
            saved = json.load(f)
            assert len(saved) >= 1
            assert saved[0]["type"] == "SHODAN_SUBDOMAIN"
