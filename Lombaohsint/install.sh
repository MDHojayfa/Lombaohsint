#!/bin/bash
# install.sh — Lombaohsint v2.0 Black Edition Installer
# Author: MDHojayfa | MDTOOLS
# License: MIT — Use freely. Own the consequences.
# DO NOT RUN ON UNAUTHORIZED SYSTEMS.

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
CYAN='\033[1;36m'
NC='\033[0m' # No Color

# ASCII BANNER
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

# LOGGING FUNCTION
log() {
    echo -e "${CYAN}[+] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[!] $1${NC}"
}

error() {
    echo -e "${RED}[-] $1${NC}"
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# EXIT ON ERROR
trap 'error "Installation failed."; exit 1' ERR

# --- START ---
echo -e "${RED}$BANNER${NC}"
echo -e "${YELLOW}[!] WARNING: This tool grants deep access to systems. Use only on targets you own or are authorized to test.${NC}"
sleep 3

# --- CHECK ROOT ACCESS (FOR LINUX) ---
if [[ "$EUID" -ne 0 ]] && [[ ! -f "/data/data/com.termux/files/usr/bin/pkg" ]]; then
    error "This script must be run as root on Linux! Try: sudo bash $0"
    exit 1
fi

# --- DETECT OS ---
if [ -f "/data/data/com.termux/files/usr/bin/pkg" ]; then
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
    exit 1
fi

# --- CREATE BASE DIR STRUCTURE ---
BASE_DIR="$HOME/lombaohsint"
mkdir -p "$BASE_DIR"
cd "$BASE_DIR" || { error "Failed to create base directory."; exit 1; }

log "Working directory: $BASE_DIR"

# --- CLONE REPO OR UPDATE ---
if [ -d ".git" ]; then
    log "Updating existing installation..."
    git pull origin master 2>/dev/null || { warn "Git repo corrupted. Re-cloning..."; rm -rf .git; }
fi

if [ ! -d ".git" ]; then
    log "Cloning repository from GitHub..."
    git clone https://github.com/MDHojayfa/lombaohsint.git . 2>/dev/null || {
        error "Failed to clone repo. Check internet connection."
        exit 1
    }
fi

# --- INSTALL DEPENDENCIES BY OS ---
case $OS in
    TERMUX)
        log "Installing Termux dependencies..."
        pkg update -y
        pkg install python git curl wget openssl-tool libffi clang make gcc -y

        # Install proot-distro if not present
        if ! command -v proot-distro &>/dev/null; then
            log "Installing proot-distro for Ubuntu chroot..."
            pkg install proot-distro -y
        fi

        # Ensure Ubuntu chroot exists and is updated
        if ! proot-distro list | grep -q "ubuntu"; then
            log "Installing Ubuntu chroot..."
            proot-distro install ubuntu
        fi

        # Update Ubuntu inside proot
        log "Updating Ubuntu chroot environment..."
        proot-distro login ubuntu -- sh -c "apt update && apt upgrade -y"

        # Symlink sdcard for file access
        if [ ! -L "$HOME/sdcard" ]; then
            log "Creating symlink to Android storage..."
            ln -sf /storage/emulated/0 "$HOME/sdcard"
        fi

        # Add alias for easy launch
        if ! grep -q "alias lombaohsint=" ~/.bashrc; then
            echo "alias lombaohsint='proot-distro login ubuntu -- bash -c \"cd $BASE_DIR && python3 main.py\"'" >> ~/.bashrc
            source ~/.bashrc
            success "Added alias: 'lombaohsint'"
        fi

        # Copy config.yaml into chroot
        if [ -f "config.yaml" ]; then
            cp config.yaml "$(proot-distro install-path ubuntu)/root/lombaohsint/config.yaml"
        fi

        log "Termux setup complete. Run: lombaohsint --target test@example.com --level BLACK --i-am-authorized"
        ;;

    KALI|UBUNTU|DEBIAN)
        log "Installing system dependencies..."
        apt-get update -y
        apt-get install python3 python3-pip git curl wget openssl libffi-dev libssl-dev build-essential clang tor proxychains-ng nmap hydra hashcat -y

        # Install pip packages
        log "Installing Python requirements (this may take 5–15 minutes)..."
        pip3 install --upgrade pip
        pip3 install -r requirements.txt --break-system-packages --no-cache-dir

        # Create symlinks for CLI access
        if [ ! -f "/usr/local/bin/lombaohsint" ]; then
            ln -sf "$BASE_DIR/main.py" /usr/local/bin/lombaohsint
            chmod +x /usr/local/bin/lombaohsint
            success "Created global command: lombaohsint"
        fi

        # Enable Tor service (if installed)
        if command -v tor &>/dev/null; then
            systemctl enable tor 2>/dev/null || true
            systemctl start tor 2>/dev/null || true
            log "Tor service enabled and started (port 9050)"
        fi

        # Verify all tools
        log "Verifying critical tools..."
        for tool in nmap amass subfinder shodan-cli hashcat; do
            if command -v "$tool" &>/dev/null; then
                success "✓ $tool installed"
            else
                warn "⚠️  $tool not found — manual install recommended"
            fi
        done

        log "Installation complete. Run: lombaohsint --target test@example.com --level BLACK --i-am-authorized"
        ;;
esac

# --- FINAL SETUP: COPY FILES INTO PLACE ---
log "Copying core files into place..."
cp -f assets/banner.txt assets/quotes.txt config.yaml requirements.txt ./
mkdir -p data/cache data/logs reports

# --- VERIFY CONFIG.YAML EXISTS ---
if [ ! -f "config.yaml" ]; then
    cat > config.yaml << 'EOF'
# ============================================================
# LOMBAOHSINT v2.0 BLACK EDITION — GLOBAL CONFIGURATION
# DO NOT EDIT UNLESS YOU KNOW WHAT YOU'RE DOING.
# ============================================================

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
EOF
    success "Generated default config.yaml"
fi

# --- FINAL MESSAGE ---
echo -e "\n${GREEN}✅ Installation Complete!${NC}"
echo -e "${YELLOW}To run: ${NC}"
echo -e "    lombaohsint --target john.doe@example.com --level BLACK --i-am-authorized"
echo -e "\n${RED}⚠️  WARNING:${NC}"
echo -e "This tool can expose private data. You are legally responsible for your actions."
echo -e "Use only with explicit authorization. Never scan without permission."
echo -e "\n${BLUE}For updates: cd $BASE_DIR && git pull${NC}"

# --- AUTO-LAUNCH TEST (OPTIONAL) ---
echo -e "\n${CYAN}Would you like to run a quick self-test? [y/N]: ${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo -e "\nRunning self-test..."
    python3 main.py --target test@mdtools.local --level GENTLE --i-am-authorized 2>/dev/null || {
        warn "Self-test failed — but this is normal on first run. Files will generate on next use."
    }
fi

echo -e "\n${CYAN}You now hold the keys to the kingdom.${NC}"
echo -e "${YELLOW}Stay sharp. The truth doesn't wait.${NC}"
