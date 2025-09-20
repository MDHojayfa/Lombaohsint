#!/bin/bash
# install_1.sh — Lombaohsint v2.0 Black Edition — ONE-COMMAND INSTALLER
# Author: MDHojayfa | MDTOOLS
# DO NOT EDIT. RUN AS ROOT. NO QUESTIONS ASKED.

echo "Don't forget to run the install.sh after this"



RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
NC='\033[0m'

BANNER="
┌──────────────────────────────────────────────────┐
│                                                  │
│   ▄▄▌  ▪  .▄▄ · ▪   ▐▄• ▄▌▄▄▄ .▄▄· ▄▄▄▄▄       ▄▄ • │
│   ██• ▪██ ▐█ ▀. ██ •█▌█▌▐█ ▀ ▪▐█ ▌▪•██  ▪     ▐█ ▀ ▪ │
│   ██▪ ▬▐█·▄▀▀▀█▄▐█· █▐█•▄█ ▀▀▄██ ▄▄ ▐Doc· ▄█▀▄ ▄▀▀▀█▄ │
│   ▐██▌▐█▌▐▀▀▀▀ █▐█▌███▌ ▐█▄▪▐▐█▌▐▀ ▐█.▪▐█▌.▐▌▐█▄▪▐▐ │
│   ▐▄██▀ █▪▪▄▄▪ ▀▪▀•▀ █• ·▀▀▀ ·▀ •  ▀▀▀  ▀█▄▀▪ ▀▀▀▪▪ │
│                             by MDHojayfa v2.0-BLACK  │
└──────────────────────────────────────────────────┘
"

log() { echo -e "${CYAN}[+] $1${NC}"; }
warn() { echo -e "${YELLOW}[!] $1${NC}"; }
error() { echo -e "${RED}[-] $1${NC}"; exit 1; }
success() { echo -e "${GREEN}✓ $1${NC}"; }

echo -e "${RED}$BANNER${NC}"
sleep 1

# --- CHECK ROOT ---
if [[ "$EUID" -ne 0 ]] && [[ ! -f "/data/data/com.termux/files/usr/bin/pkg" ]]; then
    error "This script must be run as root! Run: sudo bash $0"
fi

BASE_DIR="$HOME/lombaohsint"
mkdir -p "$BASE_DIR"
cd "$BASE_DIR" || error "Failed to create directory."

# --- DETECT OS ---
if [ -n "$PREFIX" ] && [[ "$PREFIX" == *"/data/data/com.termux/files/usr"* ]]; then
    OS="TERMUX"
    log "Detected: Termux (Android)"
elif [ -f "/etc/os-release" ] && grep -q "Kali" /etc/os-release; then
    OS="KALI"
    log "Detected: Kali Linux"
elif [ -f "/etc/os-release" ] && grep -q "Ubuntu" /etc/os-release; then
    OS="UBUNTU"
    log "Detected: Ubuntu"
elif [ -f "/etc/os-release" ] && grep -q "Debian" /etc/os-release; then
    OS="DEBIAN"
    log "Detected: Debian"
else
    error "Unsupported OS. This tool requires Kali, Ubuntu, Debian, or Termux."
fi

# --- CLONE OR UPDATE REPO ---
if [ -d ".git" ]; then
    log "Updating existing installation..."
    git pull origin main 2>/dev/null || { warn "Re-cloning..."; rm -rf .git; }
fi

if [ ! -d ".git" ]; then
    log "Cloning repository from GitHub..."
    git clone https://github.com/MDHojayfa/lombaohsint.git . 2>/dev/null || error "Git clone failed."
fi

# --- FIX LINE ENDINGS — SILENTLY ---
log "Fixing file line endings (CRLF → LF)..."
command -v dos2unix >/dev/null 2>&1 || {
    case $OS in
        TERMUX)
            pkg install dos2unix -y >/dev/null 2>&1
            ;;
        *)
            apt-get update -y >/dev/null 2>&1
            apt-get install dos2unix -y >/dev/null 2>&1
            ;;
    esac
}
find . -type f \( -name "*.py" -o -name "*.sh" \) -exec dos2unix {} \; >/dev/null 2>&1

# --- INSTALL SYSTEM DEPENDENCIES ---
case $OS in
    TERMUX)
        log "Installing Termux dependencies..."
        pkg update -y >/dev/null 2>&1
        pkg install python git curl wget openssl-tool libffi clang make gcc proot-distro -y >/dev/null 2>&1
        if ! proot-distro list | grep -q "ubuntu"; then
            log "Installing Ubuntu chroot..."
            proot-distro install ubuntu >/dev/null 2>&1
        fi
        proot-distro login ubuntu -- sh -c "apt update && apt upgrade -y" >/dev/null 2>&1
        if [ ! -L "$HOME/sdcard" ]; then
            ln -sf /storage/emulated/0 "$HOME/sdcard"
        fi
        echo "alias lombaohsint='proot-distro login ubuntu -- bash -c \"cd $BASE_DIR && python3 main.py\"'" >> ~/.bashrc
        source ~/.bashrc
        success "Alias 'lombaohsint' added. Run: lombaohsint --target test@example.com --level BLACK --i-am-authorized"
        ;;

    KALI|UBUNTU|DEBIAN)
        log "Installing system dependencies..."
        apt-get update -y >/dev/null 2>&1
        apt-get install python3 python3-venv git curl wget tor nmap hydra hashcat amass subfinder shodan-cli censys dos2unix -y >/dev/null 2>&1

        # Create and activate venv
        log "Creating Python virtual environment..."
        python3 -m venv "$BASE_DIR/venv" >/dev/null 2>&1
        source "$BASE_DIR/venv/bin/activate" >/dev/null 2>&1
        pip install --upgrade pip >/dev/null 2>&1
        pip install -r requirements.txt --break-system-packages >/dev/null 2>&1

        # Create global alias
        echo "alias lombaohsint='source \"$BASE_DIR/venv/bin/activate\" && python3 \"$BASE_DIR/main.py\"'" >> ~/.bashrc
        source ~/.bashrc
        success "Alias 'lombaohsint' added. Run: lombaohsint --target test@example.com --level BLACK --i-am-authorized"

        # Start Tor if installed
        if command -v tor &>/dev/null; then
            systemctl enable tor >/dev/null 2>&1
            systemctl start tor >/dev/null 2>&1
            log "Tor service started (port 9050)"
        fi
        ;;
esac

# --- COPY CONFIG AND CREATE DIRS ---
cp -f assets/banner.txt assets/quotes.txt config.yaml requirements.txt ./
mkdir -p data/cache/email_cache data/cache/phone_cache data/cache/username_cache data/cache/darkweb_cache data/logs reports
touch data/cache/email_cache/.gitkeep data/cache/phone_cache/.gitkeep data/cache/username_cache/.gitkeep data/cache/darkweb_cache/.gitkeep data/logs/.gitkeep reports/.gitkeep data/breaches.sqlite

if [ ! -f "config.yaml" ]; then
    cat > config.yaml << 'EOF'
level: "BLACK"
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
use_tor: true
tor_port: 9050
tor_control_port: 9051
proxy_rotation_enabled: true
proxy_list:
  - "http://proxy1.example.com:8080"
  - "http://proxy2.example.com:8080"
  - "socks5://127.0.0.1:9050"
api_keys:
  haveibeenpwned: ""
  numverify: ""
  twilio: ""
  riskseal: ""
  trestle: ""
  intelx: ""
  shodan: ""
  censys: ""
  github: ""
  hunterio: ""
  clearbit: ""
  pipl: ""
  truecaller: ""
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
termux_fix_enabled: true
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
EOF
fi

# --- FINAL MESSAGE ---
echo -e "\n${GREEN}✅ Installation Complete!${NC}"
echo -e "${YELLOW}To run:${NC}"
echo -e "    lombaohsint --target john.doe@example.com --level BLACK --i-am-authorized"
echo -e "\n${RED}⚠️  WARNING:${NC}"
echo -e "This tool can expose private data. You are legally responsible for your actions."
echo -e "Use only with explicit authorization. Never scan without permission."
echo -e "\n${BLUE}For updates: cd $BASE_DIR && git pull${NC}"

# --- SELF-TEST ---
echo -e "\n${CYAN}Running self-test...${NC}"
if [ "$OS" = "TERMUX" ]; then
    proot-distro login ubuntu -- bash -c "cd $BASE_DIR && python3 main.py --target test@mdtools.local --level GENTLE --i-am-authorized" 2>/dev/null || warn "Self-test skipped (no internet or slow)."
else
    source "$BASE_DIR/venv/bin/activate" && python3 main.py --target test@mdtools.local --level GENTLE --i-am-authorized 2>/dev/null || warn "Self-test skipped (no internet or slow)."
fi

echo -e "\n${CYAN}You now hold the keys to the kingdom.${NC}"
echo -e "${YELLOW}Stay sharp. The truth doesn't wait.${NC}"

echo "Don't forget to run the installer after this"
