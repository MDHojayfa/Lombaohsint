import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Import the module to test
from modules.credential_crack import run

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
    cache_dir = tmp_path / "data" / "cache" / "phone_cache"
    cache_dir.mkdir(parents=True)
    return cache_dir

def test_credential_crack_no_breaches(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test when no breach data is available."""
    target = "test@example.com"
    result = run(target, "GENTLE", mock_config, mock_api_wrapper, mock_proxy_rotator)
    assert len(result) == 0

def test_credential_crack_simulated_password_match(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test password matching from common patterns."""
    target = "john.doe@example.com"

    # Simulate that this email was found in a breach with password 'Password123!'
    # We don't need real hashes — we simulate the cracking engine's logic
    result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)

    assert len(result) >= 1
    found = False
    for r in result:
        if r["type"] == "CREDENTIAL_SIMULATED_CRACK":
            found = True
            assert r["source"] == "Simulated Crack Engine"
            assert r["risk"] == "CRITICAL"
            assert r["data"]["password"] in [
                "password123", "Password123!", "123456", "qwerty", "admin",
                "welcome", "letmein", "monkey", "dragon", "baseball",
                "iloveyou", "trustno1", "123123", "abc123", "football",
                "1234567", "12345678", "123456789", "sunshine", "princess",
                "1234567890", "password", "john.doe123", "john.doe2024",
                "john.doe!", "john.doe@", "john.doe#", "john.doe$", "john.doe%",
                "example2024", "example!", "example@2024"
            ]
            assert r["data"]["reuse_score"] >= 0.7
            break
    assert found, "No credential match found in results"

def test_credential_crack_email_based_variants(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test username-based password variants (e.g., john.doe + year/symbol)."""
    target = "jane.smith@company.com"

    result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)

    variants_found = 0
    for r in result:
        if r["type"] == "CREDENTIAL_VARIATION":
            variants_found += 1
            assert r["source"] == "Password Variation Guess"
            assert r["risk"] == "HIGH"
            assert r["data"]["guess"] in [
                "janesmith1", "janesmith2023", "janesmith2024",
                "JaneSmith", "janesmith!", "janesmith@", "janesmith#",
                "company2024", "company!", "company@2024"
            ]

    assert variants_found >= 5, f"Expected at least 5 variations, got {variants_found}"

def test_credential_crack_domain_based_guesses(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test password guesses based on domain name."""
    target = "bob@acme.org"

    result = run(target, "NORMAL", mock_api_wrapper, mock_proxy_rotator, mock_config)

    found_domain_variants = False
    for r in result:
        if r["type"] == "CREDENTIAL_VARIATION" and "acme" in r["data"]["guess"]:
            found_domain_variants = True
            assert r["data"]["guess"] in [
                "acme2024", "Acme2024!", "acme!", "acme@2024", "acme123"
            ]
            break

    assert found_domain_variants, "Domain-based password guess not found"

def test_credential_crack_cache_usage(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test cache usage in non-BLACK mode."""
    target = "cacheduser@test.com"
    cache_file = tmp_path / "data" / "cache" / "phone_cache" / f"{target.replace('@', '_at_')}_cracked.json"
    cache_file.parent.mkdir(parents=True)

    cached_data = [{"type": "CACHED_CRED", "source": "CACHE", "data": {}, "risk": "LOW"}]
    with open(cache_file, 'w') as f:
        json.dump(cached_data, f)

    with patch('modules.credential_crack.time') as mock_time:
        result = run(target, "GENTLE", mock_config, mock_api_wrapper, mock_proxy_rotator)
        mock_time.sleep.assert_not_called()  # No API calls made
        assert result == cached_data

def test_credential_crack_black_mode_caches(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test BLACK mode writes to cache."""
    target = "blackmode@test.com"
    cache_file = tmp_path / "data" / "cache" / "phone_cache" / f"{target.replace('@', '_at_')}_cracked.json"

    result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)

    assert cache_file.exists()
    with open(cache_file, 'r') as f:
        saved = json.load(f)
        assert len(saved) >= 1
        assert any(r["type"] == "CREDENTIAL_SIMULATED_CRACK" for r in saved)
        assert any(r["type"] == "CREDENTIAL_VARIATION" for r in saved)
