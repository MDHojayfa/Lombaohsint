import requests
from unittest.mock import patch, MagicMock
import pytest
from modules.api_wrapper import APIWrapper

@pytest.fixture
def mock_config():
    return {
        "max_retries": 2,
        "retry_delay_base_sec": 1,
        "api_keys": {
            "haveibeenpwned": "key123",
            "github": "ghp_testkey"
        }
    }

def test_api_wrapper_init(mock_config):
    """Test APIWrapper initializes with correct headers."""
    wrapper = APIWrapper(mock_config)
    assert wrapper.session.headers["User-Agent"]
    assert wrapper.max_retries == 2
    assert wrapper.retry_delay_base == 1

def test_api_wrapper_request_injects_key(mock_config):
    """Test API key injected into params or header."""
    wrapper = APIWrapper(mock_config)

    with patch.object(wrapper.session, 'request') as mock_request:
        mock_request.return_value.status_code = 200
        mock_request.return_value.json.return_value = {}

        wrapper.request("GET", "https://api.hibp.com/breached", "haveibeenpwned")

        mock_request.assert_called_once_with(
            "GET",
            "https://api.hibp.com/breached",
            params={"key": "key123"},
            json=None,
            timeout=8
        )

def test_api_wrapper_injects_github_token(mock_config):
    """Test GitHub token injected into Authorization header."""
    wrapper = APIWrapper(mock_config)

    with patch.object(wrapper.session, 'request') as mock_request:
        mock_request.return_value.status_code = 200
        mock_request.return_value.json.return_value = {}

        wrapper.request("GET", "https://api.github.com/search/code", "github")

        mock_request.assert_called_once_with(
            "GET",
            "https://api.github.com/search/code",
            params=None,
            json=None,
            timeout=8,
            headers={'User-Agent': mock.ANY, 'Accept': 'application/json', 'Accept-Language': 'en-US,en;q=0.9', 'Authorization': 'Bearer ghp_testkey'}
        )

def test_api_wrapper_retry_on_429(mock_config):
    """Test retry on rate limit (429)."""
    wrapper = APIWrapper(mock_config)

    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.text = "Too Many Requests"

    with patch.object(wrapper.session, 'request') as mock_request:
        mock_request.side_effect = [mock_response, mock_response, MagicMock(status_code=200, json=lambda: {})]

        result = wrapper.request("GET", "https://test.com", "haveibeenpwned")

        assert result == {}
        assert mock_request.call_count == 3

def test_api_wrapper_fails_after_max_retries(mock_config):
    """Test returns None after max retries."""
    wrapper = APIWrapper(mock_config)

    mock_response = MagicMock()
    mock_response.status_code = 429

    with patch.object(wrapper.session, 'request') as mock_request:
        mock_request.return_value = mock_response

        result = wrapper.request("GET", "https://test.com", "haveibeenpwned")

        assert result is None
        assert mock_request.call_count == 3  # 2 retries + 1 initial

def test_api_wrapper_no_key_no_injection(mock_config):
    """Test no injection if key not provided."""
    wrapper = APIWrapper(mock_config)

    with patch.object(wrapper.session, 'request') as mock_request:
        mock_request.return_value.status_code = 200
        mock_request.return_value.json.return_value = {}

        wrapper.request("GET", "https://test.com", "nonexistent_key")

        mock_request.assert_called_once_with(
            "GET",
            "https://test.com",
            params=None,
            json=None,
            timeout=8
      )
