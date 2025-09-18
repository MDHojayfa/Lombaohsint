import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Import the module to test
from modules.report_generator import generate_markdown, generate_html, generate_json

@pytest.fixture
def sample_findings():
    return [
        {
            "type": "EMAIL_BREACH",
            "source": "HaveIBeenPwned",
            "data": {"name": "Adobe", "domain": "adobe.com", "pwn_count": 150000000},
            "risk": "HIGH"
        },
        {
            "type": "GITHUB_SECRET",
            "source": "GitHub API",
            "data": {
                "file": ".env",
                "path": "repo/.env",
                "repo": "user/repo",
                "url": "https://github.com/user/repo/blob/main/.env",
                "snippet": "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE"
            },
            "risk": "CRITICAL"
        },
        {
            "type": "AI_SUMMARY",
            "source": "AI_SYNTHESIS",
            "data": {
                "digital_twin": {
                    "identity": {"emails": ["test@example.com"], "phones": [], "usernames": ["johndoe"]},
                    "exposure": {"breaches": 1, "secrets": 1, "social_profiles": 0},
                    "behavior": {"tech_exposure": "High", "public_presence": "Active"}
                },
                "ethical_insight": "Enable MFA and monitor for new breaches.",
                "unethical_awareness": "Attackers may use exposed keys to access cloud resources."
            }
        }
    ]

@pytest.fixture
def mock_timestamp():
    return "2025-09-15T10:30:00Z"

def test_generate_markdown(sample_findings, mock_timestamp, tmp_path):
    """Test Markdown report generation."""
    filepath = tmp_path / "report.md"
    generate_markdown(sample_findings, filepath, level="BLACK", timestamp=mock_timestamp)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    assert "# Lombaohsint Report" in content
    assert "Generated on: 2025-09-15T10:30:00Z" in content
    assert "## AI Digital Twin" in content
    assert "test@example.com" in content
    assert "johndoe" in content
    assert "Adobe" in content
    assert "AWS_ACCESS_KEY_ID" in content
    assert "```json" in content
    assert "Risk Level: CRITICAL" in content

def test_generate_html(sample_findings, mock_timestamp, tmp_path):
    """Test HTML report generation."""
    filepath = tmp_path / "report.html"
    generate_html(sample_findings, filepath, level="BLACK", timestamp=mock_timestamp)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    assert "<title>Lombaohsint Report</title>" in content
    assert "Generated on: 2025-09-15T10:30:00Z" in content
    assert "<h1><i class=\"fas fa-search\"></i> Lombaohsint v2.0 Black Edition</h1>" in content
    assert "Enable MFA and monitor for new breaches." in content
    assert "Attackers may use exposed keys to access cloud resources." in content
    assert "badge-risk-critical" in content
    assert "badge-risk-high" in content
    assert "https://github.com/user/repo/blob/main/.env" in content
    assert "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE" in content

def test_generate_json(sample_findings, mock_timestamp, tmp_path):
    """Test JSON report generation."""
    filepath = tmp_path / "report.json"
    generate_json(sample_findings, filepath, level="BLACK", timestamp=mock_timestamp)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["target"] == "unknown"
    assert data["timestamp"] == "2025-09-15T10:30:00Z"
    assert data["total_findings"] == 3
    assert len(data["findings"]) == 3
    assert data["findings"][0]["type"] == "EMAIL_BREACH"
    assert data["findings"][1]["type"] == "GITHUB_SECRET"
    assert data["findings"][2]["type"] == "AI_SUMMARY"
    assert data["ai_summary"]["ethical_insight"] == "Enable MFA and monitor for new breaches."
    assert data["ai_summary"]["unethical_awareness"] == "Attackers may use exposed keys to access cloud resources."

def test_generate_json_schema_validation(sample_findings, mock_timestamp, tmp_path):
    """Test generated JSON conforms to schema (basic validation)."""
    filepath = tmp_path / "report.json"
    generate_json(sample_findings, filepath, level="BLACK", timestamp=mock_timestamp)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    required_fields = ["target", "timestamp", "total_findings", "findings"]
    for field in required_fields:
        assert field in data

    assert isinstance(data["findings"], list)
    assert isinstance(data["ai_summary"], dict)
    assert isinstance(data["ai_summary"]["digital_twin"], dict)
