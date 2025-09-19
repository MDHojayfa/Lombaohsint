import pytest
import os
from pathlib import Path

@pytest.fixture(autouse=True)
def setup_test_env(tmp_path):
    """Set up clean test environment before each test."""
    # Create project root structure in temp dir
    os.chdir(tmp_path)
    Path("lombaohsint").mkdir()
    os.chdir("lombaohsint")

    # Create required directories
    dirs = [
        "data/cache/email_cache",
        "data/cache/phone_cache",
        "data/cache/username_cache",
        "data/cache/darkweb_cache",
        "data/logs",
        "reports",
        "modules",
        "utils",
        "templates",
        "scripts",
        "tests",
        "docs",
        "assets"
    ]
    for d in dirs:
        Path(d).mkdir(parents=True)

    # Create empty files
    files = [
        "main.py",
        "config.yaml",
        "requirements.txt",
        "assets/banner.txt",
        "assets/quotes.txt",
        "templates/report.md.jinja2",
        "templates/report.html.jinja2",
        "templates/report.json.schema",
        "scripts/update.sh",
        "scripts/cleanup.sh",
        "scripts/selftest.sh",
        "docs/architecture.md",
        "docs/api-keys.md",
        "docs/legal-notes.md",
        "docs/troubleshooting.md",
        "data/breaches.sqlite",
        "reports/.gitkeep",
        "data/cache/email_cache/.gitkeep",
        "data/cache/phone_cache/.gitkeep",
        "data/cache/username_cache/.gitkeep",
        "data/cache/darkweb_cache/.gitkeep",
        "data/logs/.gitkeep",
        "modules/__init__.py",
        "utils/__init__.py",
        "templates/__init__.py",
        "scripts/__init__.py",
        "tests/__init__.py",
        "docs/__init__.py",
        "data/__init__.py",
        "assets/__init__.py"
    ]

    for f in files:
        Path(f).touch()

    # Write minimal config
    with open("config.yaml", "w") as f:
        f.write("""
level: "GENTLE"
output_dir: "reports"
export_formats:
  - "md"
  - "html"
  - "json"
verbose: false
log_file: "data/logs/lombaohsint.log"
max_log_size_mb: 100
log_retention_days: 7
request_timeout: 10
delay_between_requests_sec: 0.5
max_retries: 3
retry_delay_base_sec: 2
use_tor: false
tor_port: 9050
tor_control_port: 9051
proxy_rotation_enabled: false
proxy_list: []
api_keys:
  twilio: ""
  numverify: ""
  hunterio: ""
  intelx: ""
  shodan: ""
  censys: ""
  haveibeenpwned: ""
  github: ""
  clearbit: ""
  pipl: ""
  truecaller: ""
  trestle: ""
  riskseal: ""
ai_model: "gpt-4o"
ai_endpoint: "https://api.openai.com/v1/chat/completions"
ai_api_key: ""
ai_summary_enabled: true
ai_unethical_insights: true
ai_max_tokens: 1500
ai_temperature: 0.7
ai_local_mode: false
ai_local_model_name: "llama-3-70b-instruct"
cache_ttl_hours: 24
use_sqlite_cache: true
sqlite_db_path: "data/breaches.sqlite"
termux_fix_enabled: false
sdcard_mount_path: "/storage/emulated/0"
termux_bin_path: "/data/data/com.termux/files/usr/bin"
agent_enabled: false
agent_interval_minutes: 120
agent_notify_telegram: false
telegram_bot_token: ""
telegram_chat_id: ""
skip_public_apis: false
force_new_scan: false
enable_debug_mode: false
""")
