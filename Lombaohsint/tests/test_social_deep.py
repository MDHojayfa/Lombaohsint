import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Import the module to test
from modules.social_deep import run

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

# -------------------------------
# 🌍 GLOBAL SOCIAL MEDIA TESTS
# -------------------------------

def test_social_deep_linkedin_global(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """LinkedIn - Global professional network"""
    target = "john.doe@example.com"
    username = "johndoe"

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<html><body><a href='https://linkedin.com/in/johndoe'>John Doe</a></body></html>"
        result = run(username, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) >= 1
        assert any(r["type"] == "LINKEDIN_PROFILE" and r["source"] == "LinkedIn" for r in result)
        assert result[0]["data"]["url"] == "https://linkedin.com/in/johndoe"
        assert result[0]["risk"] == "LOW"

def test_social_deep_twitter_x_global(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Twitter/X - Worldwide public microblogging"""
    target = "johndoe"
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<title>@johndoe on X</title><meta name='description' content='User from Tokyo'>"
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) >= 1
        assert any(r["type"] == "TWITTER_PROFILE" and r["source"] == "Twitter/X" for r in result)
        assert result[0]["data"]["url"] == "https://twitter.com/johndoe"
        assert result[0]["risk"] == "LOW"

def test_social_deep_instagram_global(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Instagram - Global photo sharing (public profile detection)"""
    target = "johndoe"
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '{"edge_followed_by":{"count":1234},"biography":"Traveler from Brazil"}'
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) >= 1
        assert any(r["type"] == "INSTAGRAM_PROFILE" and r["source"] == "Instagram" for r in result)
        assert result[0]["data"]["url"] == "https://instagram.com/johndoe"
        assert "Brazil" in result[0]["data"]["bio"]
        assert result[0]["risk"] == "LOW"

def test_social_deep_facebook_public_global(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Facebook Public Profile Search - Works in India, Brazil, Philippines, etc."""
    target = "johndoe"
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<div class='_2nlw'><a href='https://facebook.com/johndoe'>John Doe</a></div>"
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) >= 1
        assert any(r["type"] == "FACEBOOK_PUBLIC" and r["source"] == "Facebook" for r in result)
        assert "facebook.com" in result[0]["data"]["url"]
        assert result[0]["risk"] == "MEDIUM"

def test_social_deep_github_global(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """GitHub - Global developer identity"""
    target = "johndoe"
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<title>johndoe · GitHub</title><span class='p-name'>John Doe</span>"
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) >= 1
        assert any(r["type"] == "GITHUB_SOCIAL" and r["source"] == "GitHub" for r in result)
        assert result[0]["data"]["url"] == "https://github.com/johndoe"
        assert result[0]["risk"] == "LOW"

def test_social_deep_tiktok_global(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """TikTok - Global short-form video (USA, Indonesia, Mexico, Brazil, India)"""
    target = "johndoe"
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '{"userId":"12345","username":"johndoe","region":"ID"}'
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) >= 1
        assert any(r["type"] == "TIKTOK_PROFILE" and r["source"] == "TikTok" for r in result)
        assert result[0]["data"]["url"] == "https://tiktok.com/@johndoe"
        assert result[0]["risk"] == "LOW"

def test_social_deep_vk_russia(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """VKontakte (VK) - Russia's dominant social network"""
    target = "johndoe"
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<title>John Doe — ВКонтакте</title><div class='profile_name'>Иван Иванов</div>"
        result = run(target, "NORMAL", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) >= 1
        assert any(r["type"] == "VK_PROFILE" and r["source"] == "VK" for r in result)
        assert result[0]["data"]["url"] == "https://vk.com/johndoe"
        assert "ВКонтакте" in result[0]["data"]["bio"]
        assert result[0]["risk"] == "LOW"

def test_social_deep_wechat_china(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """WeChat - China’s all-in-one app (mobile-first, no public web search)"""
    target = "johndoe"
    # Simulate that WeChat has no public web presence — but we detect via other means
    # In reality: WeChat IDs are often linked via QR codes or leaked databases
    # Here we simulate detection from a third-party leak
    with patch('modules.social_deep.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '<div class="weixin-id">微信号: johndoe</div>'
        result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) >= 1
        assert any(r["type"] == "WECHAT_ID" and r["source"] == "WeChat" for r in result)
        assert result[0]["data"]["wechat_id"] == "johndoe"
        assert result[0]["risk"] == "LOW"

def test_social_deep_line_japan(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """LINE - Dominant in Japan, Thailand, Taiwan"""
    target = "johndoe"
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '<div class="line-id">ID: johndoe</div><img src="https://line.me/...">'
        result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) >= 1
        assert any(r["type"] == "LINE_ID" and r["source"] == "LINE" for r in result)
        assert result[0]["data"]["line_id"] == "johndoe"
        assert result[0]["risk"] == "LOW"

def test_social_deep_kakaotalk_korea(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """KakaoTalk - South Korea’s primary messaging app"""
    target = "johndoe"
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '<div class="kakao-id">카카오톡 ID: johndoe</div>'
        result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) >= 1
        assert any(r["type"] == "KAKAOTALK_ID" and r["source"] == "KakaoTalk" for r in result)
        assert result[0]["data"]["kakaotalk_id"] == "johndoe"
        assert "카카오톡" in result[0]["data"]["bio"]
        assert result[0]["risk"] == "LOW"

def test_social_deep_sina_weibo_china(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Sina Weibo - China’s Twitter equivalent"""
    target = "johndoe"
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '<title>微博 - johndoe</title><span class="nick-name">约翰·多伊</span>'
        result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) >= 1
        assert any(r["type"] == "SINA_WEIBO_PROFILE" and r["source"] == "Sina Weibo" for r in result)
        assert result[0]["data"]["url"] == "https://weibo.com/johndoe"
        assert "约翰·多伊" in result[0]["data"]["name"]
        assert result[0]["risk"] == "LOW"

def test_social_deep_douyin_china(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Douyin - Chinese version of TikTok"""
    target = "johndoe"
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '{"user":{"unique_id":"johndoe","region":"CN"}}'
        result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) >= 1
        assert any(r["type"] == "DOUYIN_PROFILE" and r["source"] == "Douyin" for r in result)
        assert result[0]["data"]["url"] == "https://douyin.com/@johndoe"
        assert result[0]["data"]["region"] == "CN"
        assert result[0]["risk"] == "LOW"

def test_social_deep_telegram_iran_russia(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Telegram - Used widely in Iran, Russia, Ukraine, Venezuela"""
    target = "johndoe"
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '<div class="tg-username">@johndoe</div><span>Iranian activist</span>'
        result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) >= 1
        assert any(r["type"] == "TELEGRAM_USERNAME" and r["source"] == "Telegram" for r in result)
        assert result[0]["data"]["username"] == "@johndoe"
        assert "Iranian" in result[0]["data"]["bio"]
        assert result[0]["risk"] == "MEDIUM"

def test_social_deep_whatsapp_nigeria_kenya(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """WhatsApp - Primary in Nigeria, Kenya, India, Brazil"""
    target = "+2348012345678"  # Nigerian number
    # WhatsApp doesn't have public profiles — we infer from linked numbers
    # Simulate detection via leaked contact lists or group invites
    with patch('modules.social_deep.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = 'Contact found: +2348012345678 (Nigeria)'
        result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) >= 1
        assert any(r["type"] == "WHATSAPP_NUMBER" and r["source"] == "WhatsApp" for r in result)
        assert result[0]["data"]["number"] == "+2348012345678"
        assert result[0]["data"]["country"] == "Nigeria"
        assert result[0]["risk"] == "LOW"

def test_social_deep_odnoklassniki_central_asia(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Odnoklassniki - Popular in Kazakhstan, Uzbekistan, Belarus"""
    target = "johndoe"
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '<title>Одноклассники — johndoe</title><span class="name">Иван Петров</span>'
        result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) >= 1
        assert any(r["type"] == "ODNOKLASSNIKI_PROFILE" and r["source"] == "Odnoklassniki" for r in result)
        assert result[0]["data"]["url"] == "https://ok.ru/johndoe"
        assert "Одноклассники" in result[0]["data"]["bio"]
        assert result[0]["risk"] == "LOW"

def test_social_deep_messenger_facebook_global(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Facebook Messenger — Indirect detection via profile links"""
    target = "johndoe"
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '<a href="fb-messenger://user/123456789">Message John</a>'
        result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert len(result) >= 1
        assert any(r["type"] == "MESSENGER_LINK" and r["source"] == "Facebook Messenger" for r in result)
        assert result[0]["data"]["messenger_id"] == "123456789"
        assert result[0]["risk"] == "LOW"

def test_social_deep_cache_usage(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """Cache usage works for any global platform."""
    target = "johndoe"
    cache_file = tmp_path / "data" / "cache" / "username_cache" / f"{target}.json"
    cache_file.parent.mkdir(parents=True)
    cached_data = [{"type": "CACHED_SOCIAL", "source": "CACHE", "data": {}, "risk": "LOW"}]
    with open(cache_file, 'w') as f:
        json.dump(cached_data, f)
    with patch('requests.get') as mock_get:
        result = run(target, "GENTLE", mock_config, mock_api_wrapper, mock_proxy_rotator)
        mock_get.assert_not_called()
        assert result == cached_data

def test_social_deep_black_mode_caches(mock_config, mock_api_wrapper, mock_proxy_rotator, tmp_path):
    """BLACK mode caches results for any global platform."""
    target = "johndoe"
    cache_file = tmp_path / "data" / "cache" / "username_cache" / f"{target}.json"

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<html><a href='https://vk.com/johndoe'>John Doe</a></html>"
        result = run(target, "BLACK", mock_config, mock_api_wrapper, mock_proxy_rotator)

        assert cache_file.exists()
        with open(cache_file, 'r') as f:
            saved = json.load(f)
            assert len(saved) >= 1
            assert any(r["type"] == "VK_PROFILE" for r in saved)
