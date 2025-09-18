import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Import the module to test
from modules.ai_synthesis import run

@pytest.fixture
def mock_config():
    return {
        "ai_summary_enabled": True,
        "ai_unethical_insights": True,
        "ai_model": "gpt-4o",
        "ai_endpoint": "https://api.openai.com/v1/chat/completions",
        "ai_api_key": "sk-testkey123",
        "ai_max_tokens": 1500,
        "ai_temperature": 0.7,
        "ai_local_mode": False,
        "ai_local_model_name": "llama-3-70b-instruct"
    }

@pytest.fixture
def mock_api_wrapper():
    return MagicMock()

@pytest.fixture
def mock_proxy_rotator():
    return MagicMock()

def test_ai_synthesis_empty_findings(mock_config, mock_api_wrapper, mock_proxy_rotator):
    """Test AI synthesis with no findings."""
    findings = []
    result = run(findings, mock_config)

    assert result["digital_twin"] == {
        "identity": {"emails": [], "phones": [], "usernames": []},
        "exposure": {"breaches": 0, "secrets": 0, "social_profiles": 0},
        "behavior": {"tech_exposure": "Low", "public_presence": "Minimal"}
    }
    assert "Ethical Insight" in result["ethical_insight"]
    assert "Unethical Awareness" in result["unethical_awareness"]

def test_ai_synthesis_gpt4o_response_success(mock_config, mock_api_wrapper, mock_proxy_rotator):
    """Test successful GPT-4o response with valid JSON."""
    findings = [
        {
            "type": "EMAIL_BREACH",
            "source": "HaveIBeenPwned",
            "data": {"name": "Adobe", "domain": "adobe.com"},
            "risk": "HIGH"
        },
        {
            "type": "USERNAME_FOUND",
            "source": "github",
            "data": {"url": "https://github.com/johndoe"},
            "risk": "LOW"
        },
        {
            "type": "PHONE_VALIDATION",
            "source": "NumVerify",
            "data": {"number": "+15551234567", "location": "New York"},
            "risk": "LOW"
        }
    ]

    mock_response = {
        "choices": [{
            "message": {
                "content": """
{
  "ethical_insight": "Review all exposed credentials. Enable MFA everywhere. Monitor for new breaches.",
  "unethical_awareness": "Attackers may combine breached passwords with social profiles to launch targeted phishing or credential stuffing attacks."
}
                """
            }
        }]
    }

    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response

        result = run(findings, mock_config)

        assert result["ethical_insight"] == "Review all exposed credentials. Enable MFA everywhere. Monitor for new breaches."
        assert result["unethical_awareness"] == "Attackers may combine breached passwords with social profiles to launch targeted phishing or credential stuffing attacks."
        assert result["digital_twin"]["identity"]["emails"] == []
        assert result["digital_twin"]["exposure"]["breaches"] == 1
        assert result["digital_twin"]["exposure"]["social_profiles"] == 1

def test_ai_synthesis_local_llm_success(mock_config, mock_api_wrapper, mock_proxy_rotator):
    """Test local LLM (Ollama) response format."""
    mock_config["ai_local_mode"] = True
    mock_config["ai_local_model_name"] = "llama-3-70b-instruct"

    findings = [
        {
            "type": "EMAIL_BREACH",
            "source": "HaveIBeenPwned",
            "data": {"name": "LinkedIn", "domain": "linkedin.com"},
            "risk": "HIGH"
        }
    ]

    mock_response = {
        "response": """
{
  "ethical_insight": "Force password reset and enable two-factor authentication immediately.",
  "unethical_awareness": "Threat actors often use LinkedIn profiles to craft convincing spear-phishing emails targeting employees."
}
        """
    }

    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response

        result = run(findings, mock_config)

        assert result["ethical_insight"] == "Force password reset and enable two-factor authentication immediately."
        assert result["unethical_awareness"] == "Threat actors often use LinkedIn profiles to craft convincing spear-phishing emails targeting employees."

def test_ai_synthesis_fallback_on_api_failure(mock_config, mock_api_wrapper, mock_proxy_rotator):
    """Test fallback to static message when API fails."""
    findings = [
        {
            "type": "EMAIL_BREACH",
            "source": "HaveIBeenPwned",
            "data": {"name": "Adobe", "domain": "adobe.com"},
            "risk": "HIGH"
        }
    ]

    mock_config["ai_api_key"] = "invalid_key"

    with patch('requests.post') as mock_post:
        mock_post.side_effect = Exception("API timeout")

        result = run(findings, mock_config)

        assert "Review all exposed credentials" in result["ethical_insight"]
        assert "attackers may combine" in result["unethical_awareness"]
        assert result["digital_twin"]["exposure"]["breaches"] == 1

def test_ai_synthesis_disabled(mock_config, mock_api_wrapper, mock_proxy_rotator):
    """Test AI synthesis disabled."""
    mock_config["ai_summary_enabled"] = False
    findings = [{"type": "EMAIL_BREACH", "data": {}, "risk": "HIGH"}]

    result = run(findings, mock_config)

    assert result["ethical_insight"] == ""
    assert result["unethical_awareness"] == ""
    assert result["digital_twin"] == {
        "identity": {"emails": [], "phones": [], "usernames": []},
        "exposure": {"breaches": 0, "secrets": 0, "social_profiles": 0},
        "behavior": {"tech_exposure": "Low", "public_presence": "Minimal"}
    }

def test_ai_synthesis_no_unethical_insights(mock_config, mock_api_wrapper, mock_proxy_rotator):
    """Test unethical insights disabled."""
    mock_config["ai_unethical_insights"] = False
    findings = [{"type": "EMAIL_BREACH", "data": {}, "risk": "HIGH"}]

    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "choices": [{
                "message": {
                    "content": """
{
  "ethical_insight": "Enable MFA.",
  "unethical_awareness": "Attackers might try credential stuffing."
}
                    """
                }
            }]
        }

        result = run(findings, mock_config)

        assert result["ethical_insight"] == "Enable MFA."
        assert result["unethical_awareness"] == ""  # Disabled

def test_ai_synthesis_digital_twin_building(mock_config, mock_api_wrapper, mock_proxy_rotator):
    """Test digital twin correctly builds identity and exposure data."""
    findings = [
        {
            "type": "EMAIL_BREACH",
            "source": "HaveIBeenPwned",
            "data": {"name": "Adobe", "domain": "adobe.com"},
            "risk": "HIGH"
        },
        {
            "type": "PHONE_VALIDATION",
            "source": "NumVerify",
            "data": {"number": "+15551234567", "location": "New York"},
            "risk": "LOW"
        },
        {
            "type": "USERNAME_FOUND",
            "source": "github",
            "data": {"url": "https://github.com/johndoe"},
            "risk": "LOW"
        },
        {
            "type": "TWILIO_LOOKUP",
            "source": "Twilio",
            "data": {"caller_name": "John Doe"},
            "risk": "LOW"
        }
    ]

    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "choices": [{
                "message": {
                    "content": """
{
  "ethical_insight": "Test insight.",
  "unethical_awareness": "Test awareness."
}
                    """
                }
            }]
        }

        result = run(findings, mock_config)

        dt = result["digital_twin"]
        assert dt["identity"]["emails"] == []
        assert dt["identity"]["phones"] == ["+15551234567"]
        assert dt["identity"]["usernames"] == ["johndoe"]
        assert dt["exposure"]["breaches"] == 1
        assert dt["exposure"]["social_profiles"] == 1
        assert dt["exposure"]["secrets"] == 0
        assert dt["behavior"]["tech_exposure"] == "High"
        assert dt["behavior"]["public_presence"] == "Active"
