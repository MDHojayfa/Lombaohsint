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

# --- CONVERT LINE ENDINGS (CRLF → LF) — CRITICAL FOR LINUX/TERMUX ---
log "Converting file line endings from CRLF to LF..."
if command -v dos2unix &>/dev/null; then
    find . -type f \( -name "*.py" -o -name "*.sh" \) -exec dos2unix {} \;
else
    warn "dos2unix not found. Installing now..."
    case $OS in
        TERMUX)
            pkg install dos2unix -y
            find . -type f \( -name "*.py" -o -name "*.sh" \) -exec dos2unix {} \;
            ;;
        KALI|UBUNTU|DEBIAN)
            apt-get update -y
            apt-get install dos2unix -y
            find . -type f \( -name "*.py" -o -name "*.sh" \) -exec dos2unix {} \;
            ;;
    esac
fi

# --- INSTALL DEPENDENCIES BY OS ---
case $OS in
    TERMUX)
        log "Installing Termux dependencies..."
        pkg update -y
        pkg install python git curl wget openssl-tool libffi clang make gcc proot-distro -y

        # Install proot-distro Ubuntu if needed
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
        apt-get install python3 python3-venv git curl wget openssl libffi-dev libssl-dev build-essential clang tor proxychains-ng nmap hydra hashcat amass subfinder shodan-cli censys -y

        # Create virtual environment
        log "Creating Python virtual environment at $BASE_DIR/venv..."
        python3 -m venv "$BASE_DIR/venv"

        # Activate venv and install requirements
        log "Installing Python requirements inside virtual environment..."
        source "$BASE_DIR/venv/bin/activate"
        pip install --upgrade pip
        pip install -r requirements.txt --break-system-packages

        # Create global alias to run via venv
        if ! grep -q "alias lombaohsint=" ~/.bashrc; then
            echo "alias lombaohsint='source \"$BASE_DIR/venv/bin/activate\" && python3 \"$BASE_DIR/main.py\"'" >> ~/.bashrc
            source ~/.bashrc
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
mkdir -p data/cache/email_cache data/cache/phone_cache data/cache/username_cache data/cache/darkweb_cache data/logs reports

# --- VERIFY CONFIG.YAML EXISTS ---
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
    if [ "$OS" = "TERMUX" ]; then
        proot-distro login ubuntu -- bash -c "cd $BASE_DIR && python3 main.py --target test@mdtools.local --level GENTLE --i-am-authorized" 2>/dev/null || {
            warn "Self-test failed — but this is normal on first run. Files will generate on next use."
        }
    else
        source "$BASE_DIR/venv/bin/activate" && python3 main.py --target test@mdtools.local --level GENTLE --i-am-authorized 2>/dev/null || {
            warn "Self-test failed — but this is normal on first run. Files will generate on next use."
        }
    fi
fi

echo -e "\n${CYAN}You now hold the keys to the kingdom.${NC}"
echo -e "${YELLOW}Stay sharp. The truth doesn't wait.${NC}"
