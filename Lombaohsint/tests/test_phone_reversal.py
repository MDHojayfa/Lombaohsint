import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Import the module to test
from modules.phone_reversal import run

@pytest.fixture
def mock_config():
    return {
        "api_keys": {
            "numverify": "numverify_test_key",
            "twilio": "twilio_test_sid:twilio_test_token",
            "riskseal": "riskseal_test_apikey",
            "trestle": "trestle_test_bearer"
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

# --- TESTS FOR ALL MAJOR COUNTRIES (E.164 FORMAT) ---

def test_phone_reversal_invalid_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Test with invalid phone number format."""
    target = "not-a-phone"

    result = run(target, "GENTLE", mock_config, mock_api_wrapper, mock_proxy_rotator)

    assert len(result) == 0

# -------------------------------
# 🌍 GLOBAL PHONE NUMBER TESTS
# -------------------------------

def test_phone_reversal_us_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """United States (+1)"""
    target = "+15551234567"
    numverify_response = {
        "number": "+15551234567",
        "country_code": "US",
        "location": "New York",
        "carrier": "Verizon Wireless",
        "line_type": "mobile",
        "valid": True,
        "country_name": "United States"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "US"
        assert result[0]["data"]["country_name"] == "United States"

def test_phone_reversal_uk_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """United Kingdom (+44)"""
    target = "+447700900123"
    numverify_response = {
        "number": "+447700900123",
        "country_code": "GB",
        "location": "London",
        "carrier": "Vodafone UK",
        "line_type": "mobile",
        "valid": True,
        "country_name": "United Kingdom"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "GB"
        assert result[0]["data"]["country_name"] == "United Kingdom"

def test_phone_reversal_germany_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Germany (+49)"""
    target = "+4915712345678"
    numverify_response = {
        "number": "+4915712345678",
        "country_code": "DE",
        "location": "Berlin",
        "carrier": "Deutsche Telekom",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Germany"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "DE"
        assert result[0]["data"]["country_name"] == "Germany"

def test_phone_reversal_india_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """India (+91)"""
    target = "+919876543210"
    numverify_response = {
        "number": "+919876543210",
        "country_code": "IN",
        "location": "Mumbai",
        "carrier": "Jio",
        "line_type": "mobile",
        "valid": True,
        "country_name": "India"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "IN"
        assert result[0]["data"]["country_name"] == "India"

def test_phone_reversal_brazil_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Brazil (+55)"""
    target = "+5511987654321"
    numverify_response = {
        "number": "+5511987654321",
        "country_code": "BR",
        "location": "São Paulo",
        "carrier": "Claro",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Brazil"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "BR"
        assert result[0]["data"]["country_name"] == "Brazil"

def test_phone_reversal_japan_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Japan (+81)"""
    target = "+819012345678"
    numverify_response = {
        "number": "+819012345678",
        "country_code": "JP",
        "location": "Tokyo",
        "carrier": "NTT Docomo",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Japan"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "JP"
        assert result[0]["data"]["country_name"] == "Japan"

def test_phone_reversal_south_africa_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """South Africa (+27)"""
    target = "+27821234567"
    numverify_response = {
        "number": "+27821234567",
        "country_code": "ZA",
        "location": "Johannesburg",
        "carrier": "MTN",
        "line_type": "mobile",
        "valid": True,
        "country_name": "South Africa"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "ZA"
        assert result[0]["data"]["country_name"] == "South Africa"

def test_phone_reversal_mexico_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Mexico (+52)"""
    target = "+525512345678"
    numverify_response = {
        "number": "+525512345678",
        "country_code": "MX",
        "location": "Mexico City",
        "carrier": "Telcel",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Mexico"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "MX"
        assert result[0]["data"]["country_name"] == "Mexico"

def test_phone_reversal_canada_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Canada (+1) — different area code"""
    target = "+14165550123"
    numverify_response = {
        "number": "+14165550123",
        "country_code": "CA",
        "location": "Toronto",
        "carrier": "Rogers",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Canada"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "CA"
        assert result[0]["data"]["country_name"] == "Canada"

def test_phone_reversal_australia_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Australia (+61)"""
    target = "+61412345678"
    numverify_response = {
        "number": "+61412345678",
        "country_code": "AU",
        "location": "Sydney",
        "carrier": "Telstra",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Australia"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "AU"
        assert result[0]["data"]["country_name"] == "Australia"

def test_phone_reversal_china_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """China (+86)"""
    target = "+8613812345678"
    numverify_response = {
        "number": "+8613812345678",
        "country_code": "CN",
        "location": "Beijing",
        "carrier": "China Mobile",
        "line_type": "mobile",
        "valid": True,
        "country_name": "China"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "CN"
        assert result[0]["data"]["country_name"] == "China"

def test_phone_reversal_russia_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Russia (+7)"""
    target = "+79123456789"
    numverify_response = {
        "number": "+79123456789",
        "country_code": "RU",
        "location": "Moscow",
        "carrier": "MTS",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Russian Federation"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "RU"
        assert result[0]["data"]["country_name"] == "Russian Federation"

def test_phone_reversal_saudi_arabia_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Saudi Arabia (+966)"""
    target = "+966501234567"
    numverify_response = {
        "number": "+966501234567",
        "country_code": "SA",
        "location": "Riyadh",
        "carrier": "STC",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Saudi Arabia"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "SA"
        assert result[0]["data"]["country_name"] == "Saudi Arabia"

def test_phone_reversal_united_arab_emirates_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """UAE (+971)"""
    target = "+971501234567"
    numverify_response = {
        "number": "+971501234567",
        "country_code": "AE",
        "location": "Dubai",
        "carrier": "Etisalat",
        "line_type": "mobile",
        "valid": True,
        "country_name": "United Arab Emirates"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "AE"
        assert result[0]["data"]["country_name"] == "United Arab Emirates"

def test_phone_reversal_turkey_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Turkey (+90)"""
    target = "+905321234567"
    numverify_response = {
        "number": "+905321234567",
        "country_code": "TR",
        "location": "Istanbul",
        "carrier": "Turkcell",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Turkey"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "TR"
        assert result[0]["data"]["country_name"] == "Turkey"

def test_phone_reversal_nigeria_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Nigeria (+234)"""
    target = "+2348012345678"
    numverify_response = {
        "number": "+2348012345678",
        "country_code": "NG",
        "location": "Lagos",
        "carrier": "MTN Nigeria",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Nigeria"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "NG"
        assert result[0]["data"]["country_name"] == "Nigeria"

def test_phone_reversal_egypt_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Egypt (+20)"""
    target = "+201001234567"
    numverify_response = {
        "number": "+201001234567",
        "country_code": "EG",
        "location": "Cairo",
        "carrier": "Vodafone Egypt",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Egypt"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "EG"
        assert result[0]["data"]["country_name"] == "Egypt"

def test_phone_reversal_thailand_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Thailand (+66)"""
    target = "+66812345678"
    numverify_response = {
        "number": "+66812345678",
        "country_code": "TH",
        "location": "Bangkok",
        "carrier": "AIS",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Thailand"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "TH"
        assert result[0]["data"]["country_name"] == "Thailand"

def test_phone_reversal_philippines_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Philippines (+63)"""
    target = "+639123456789"
    numverify_response = {
        "number": "+639123456789",
        "country_code": "PH",
        "location": "Manila",
        "carrier": "Globe Telecom",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Philippines"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "PH"
        assert result[0]["data"]["country_name"] == "Philippines"

def test_phone_reversal_indonesia_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Indonesia (+62)"""
    target = "+6281234567890"
    numverify_response = {
        "number": "+6281234567890",
        "country_code": "ID",
        "location": "Jakarta",
        "carrier": "Telkomsel",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Indonesia"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "ID"
        assert result[0]["data"]["country_name"] == "Indonesia"

def test_phone_reversal_malaysia_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Malaysia (+60)"""
    target = "+60123456789"
    numverify_response = {
        "number": "+60123456789",
        "country_code": "MY",
        "location": "Kuala Lumpur",
        "carrier": "Maxis",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Malaysia"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "MY"
        assert result[0]["data"]["country_name"] == "Malaysia"

def test_phone_reversal_singapore_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Singapore (+65)"""
    target = "+6581234567"
    numverify_response = {
        "number": "+6581234567",
        "country_code": "SG",
        "location": "Singapore",
        "carrier": "Singtel",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Singapore"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "SG"
        assert result[0]["data"]["country_name"] == "Singapore"

def test_phone_reversal_vietnam_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Vietnam (+84)"""
    target = "+84912345678"
    numverify_response = {
        "number": "+84912345678",
        "country_code": "VN",
        "location": "Hanoi",
        "carrier": "Vinaphone",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Viet Nam"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "VN"
        assert result[0]["data"]["country_name"] == "Viet Nam"

def test_phone_reversal_pakistan_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Pakistan (+92)"""
    target = "+923001234567"
    numverify_response = {
        "number": "+923001234567",
        "country_code": "PK",
        "location": "Karachi",
        "carrier": "Jazz",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Pakistan"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "PK"
        assert result[0]["data"]["country_name"] == "Pakistan"

def test_phone_reversal_bangladesh_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Bangladesh (+880)"""
    target = "+8801712345678"
    numverify_response = {
        "number": "+8801712345678",
        "country_code": "BD",
        "location": "Dhaka",
        "carrier": "Grameenphone",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Bangladesh"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "BD"
        assert result[0]["data"]["country_name"] == "Bangladesh"

def test_phone_reversal_sri_lanka_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Sri Lanka (+94)"""
    target = "+94712345678"
    numverify_response = {
        "number": "+94712345678",
        "country_code": "LK",
        "location": "Colombo",
        "carrier": "Dialog",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Sri Lanka"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "LK"
        assert result[0]["data"]["country_name"] == "Sri Lanka"

def test_phone_reversal_korea_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """South Korea (+82)"""
    target = "+821012345678"
    numverify_response = {
        "number": "+821012345678",
        "country_code": "KR",
        "location": "Seoul",
        "carrier": "SK Telecom",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Korea, Republic of"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "KR"
        assert result[0]["data"]["country_name"] == "Korea, Republic of"

def test_phone_reversal_kenya_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Kenya (+254)"""
    target = "+254712345678"
    numverify_response = {
        "number": "+254712345678",
        "country_code": "KE",
        "location": "Nairobi",
        "carrier": "Safaricom",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Kenya"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "KE"
        assert result[0]["data"]["country_name"] == "Kenya"

def test_phone_reversal_ghana_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Ghana (+233)"""
    target = "+233241234567"
    numverify_response = {
        "number": "+233241234567",
        "country_code": "GH",
        "location": "Accra",
        "carrier": "MTN Ghana",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Ghana"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "GH"
        assert result[0]["data"]["country_name"] == "Ghana"

def test_phone_reversal_tanzania_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Tanzania (+255)"""
    target = "+255712345678"
    numverify_response = {
        "number": "+255712345678",
        "country_code": "TZ",
        "location": "Dar es Salaam",
        "carrier": "Vodacom Tanzania",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Tanzania, United Republic of"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "TZ"
        assert result[0]["data"]["country_name"] == "Tanzania, United Republic of"

def test_phone_reversal_argentina_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Argentina (+54)"""
    target = "+5491112345678"
    numverify_response = {
        "number": "+5491112345678",
        "country_code": "AR",
        "location": "Buenos Aires",
        "carrier": "Claro Argentina",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Argentina"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "AR"
        assert result[0]["data"]["country_name"] == "Argentina"

def test_phone_reversal_colombia_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Colombia (+57)"""
    target = "+573001234567"
    numverify_response = {
        "number": "+573001234567",
        "country_code": "CO",
        "location": "Bogotá",
        "carrier": "Claro Colombia",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Colombia"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "CO"
        assert result[0]["data"]["country_name"] == "Colombia"

def test_phone_reversal_peru_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Peru (+51)"""
    target = "+51912345678"
    numverify_response = {
        "number": "+51912345678",
        "country_code": "PE",
        "location": "Lima",
        "carrier": "Movistar Peru",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Peru"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "PE"
        assert result[0]["data"]["country_name"] == "Peru"

def test_phone_reversal_chile_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Chile (+56)"""
    target = "+56912345678"
    numverify_response = {
        "number": "+56912345678",
        "country_code": "CL",
        "location": "Santiago",
        "carrier": "Entel Chile",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Chile"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "CL"
        assert result[0]["data"]["country_name"] == "Chile"

def test_phone_reversal_cuba_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Cuba (+53)"""
    target = "+5351234567"
    numverify_response = {
        "number": "+5351234567",
        "country_code": "CU",
        "location": "Havana",
        "carrier": "ETECSA",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Cuba"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "CU"
        assert result[0]["data"]["country_name"] == "Cuba"

def test_phone_reversal_haiti_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Haiti (+509)"""
    target = "+50933123456"
    numverify_response = {
        "number": "+50933123456",
        "country_code": "HT",
        "location": "Port-au-Prince",
        "carrier": "Natcom",
        "line_type": "mobile",
        "valid": True,
        "country_name": "Haiti"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "HT"
        assert result[0]["data"]["country_name"] == "Haiti"

def test_phone_reversal_new_zealand_number(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """New Zealand (+64)"""
    target = "+64211234567"
    numverify_response = {
        "number": "+64211234567",
        "country_code": "NZ",
        "location": "Auckland",
        "carrier": "Spark",
        "line_type": "mobile",
        "valid": True,
        "country_name": "New Zealand"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = numverify_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["data"]["country_code"] == "NZ"
        assert result[0]["data"]["country_name"] == "New Zealand"

# --- OTHER TESTS (Twilio, RiskSeal, Trestle, Truecaller, Cache) ---
# These remain unchanged — they work with any +XX number

def test_phone_reversal_twilio_lookup(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Twilio Lookup works with international numbers."""
    target = "+447700900123"  # UK
    twilio_response = {
        "phone_number": "+447700900123",
        "carrier": {
            "name": "Vodafone UK",
            "type": "mobile"
        },
        "caller_name": {
            "name": "John Smith"
        }
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = twilio_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["type"] == "TWILIO_LOOKUP"
        assert result[0]["data"]["country_code"] == "GB"

def test_phone_reversal_riskseal_high_risk(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """RiskSeal works globally."""
    target = "+819012345678"  # Japan
    riskseal_response = {
        "risk_score": 85,
        "sim_swap_risk": True,
        "fraud_indicators": ["unusual login"],
        "last_seen": "2024-06-15T10:30:00Z"
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = riskseal_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["type"] == "RISKSEAL_RISK"
        assert result[0]["data"]["country_code"] == "JP"

def test_phone_reversal_trestle_identity_match(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Trestle identity match works internationally."""
    target = "+919876543210"  # India
    trestle_response = {
        "identity": {
            "name": "Priya Sharma",
            "address": "Mumbai, Maharashtra",
            "age": 29,
            "emails": ["priya.sharma@example.com"]
        }
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = trestle_response
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["type"] == "TRESTLE_IDENTITY"
        assert result[0]["data"]["country_code"] == "IN"

def test_phone_reversal_truecaller_web_fallback(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Truecaller web fallback works for non-US numbers."""
    target = "+4915712345678"  # Germany
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<html><body>Result for +4915712345678 found</body></html>"
        result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert len(result) == 1
        assert result[0]["type"] == "TRUECALLER_DETECTED"
        assert result[0]["data"]["country_code"] == "DE"

def test_phone_reversal_cache_usage(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Cache usage works for any country."""
    target = "+61412345678"  # Australia
    cache_file = tmp_path / "data" / "cache" / "phone_cache" / "61412345678.json"
    cache_file.parent.mkdir(parents=True)
    cached_data = [{"type": "CACHED_PHONE", "source": "CACHE", "data": {}, "risk": "LOW"}]
    with open(cache_file, 'w') as f:
        json.dump(cached_data, f)
    with patch('requests.get') as mock_get:
        result = run(target, "GENTLE", mock_config, mock_api_wrapper, mock_proxy_rotator)
        mock_get.assert_not_called()
        assert result == cached_data

def test_phone_reversal_black_mode_caches(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """BLACK mode caches results for any country."""
    target = "+5511987654321"  # Brazil
    cache_file = tmp_path / "data" / "cache" / "phone_cache" / "5511987654321.json"
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "number": "+5511987654321",
            "country_code": "BR",
            "location": "São Paulo",
            "carrier": "Claro",
            "line_type": "mobile",
            "valid": True
        }
        result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)
        assert cache_file.exists()
        with open(cache_file, 'r') as f:
            saved = json.load(f)
            assert len(saved) == 1
            assert saved[0]["data"]["country_code"] == "BR"
