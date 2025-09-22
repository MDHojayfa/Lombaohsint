#!/bin/bash
# install.sh — Lombaohsint v2.0 Black Edition — ULTRA HACKER INSTALLER
# Author: MDHojayfa | MDTOOLS
# ⚡ Custom Glitched Installer ⚡

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

glitch() {
    text="$1"
    for i in {1..3}; do
        echo -ne "${PURPLE}$text\r${NC}"
        sleep 0.05
        echo -ne "${RED}$text\r${NC}"
        sleep 0.05
        echo -ne "${GREEN}$text\r${NC}"
        sleep 0.05
    done
    echo -e "${CYAN}$text${NC}"
}

BANNER="
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   ▄▄▌  ▪  .▄▄ · ▪   ▐▄• ▄▌▄▄▄ .▄▄· ▄▄▄▄▄       ▄▄ •     │
│   ██• ▪██ ▐█ ▀. ██ •█▌█▌▐█ ▀ ▪▐█ ▌▪•██  ▪     ▐█ ▀ ▪    │
│   ██▪ ▬▐█·▄▀▀▀█▄▐█· █▐█•▄█ ▀▀▄██ ▄▄ ▐Doc· ▄█▀▄ ▄▀▀▀█▄   │
│   ▐██▌▐█▌▐▀▀▀▀ █▐█▌███▌ ▐█▄▪▐▐█▌▐▀ ▐█.▪▐█▌.▐▌▐█▄▪▐▐    │
│   ▐▄██▀ █▪▪▄▄▪ ▀▪▀•▀ █• ·▀▀▀ ·▀ •  ▀▀▀  ▀█▄▀▪ ▀▀▀▪▪    │
│               by MDHojayfa v2.0-BLACK                  │
└─────────────────────────────────────────────────────────┘
"

log() { echo -e "${CYAN}[+] $1${NC}"; }
warn() { echo -e "${YELLOW}[!] $1${NC}"; }
error() { echo -e "${RED}[-] $1${NC}"; exit 1; }
success() { echo -e "${GREEN}✓ $1${NC}"; }

clear
glitch "$BANNER"
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
    OS="TERMUX"; log "Detected: Termux (Android)"
elif grep -qi "Kali" /etc/os-release; then
    OS="KALI"; log "Detected: Kali Linux"
elif grep -qi "Ubuntu" /etc/os-release; then
    OS="UBUNTU"; log "Detected: Ubuntu"
elif grep -qi "Debian" /etc/os-release; then
    OS="DEBIAN"; log "Detected: Debian"
else
    error "Unsupported OS. Requires Kali, Ubuntu, Debian, or Termux."
fi

# --- CLONE OR UPDATE REPO ---
if [ -d ".git" ]; then
    log "Updating repo..."; git pull origin main 2>/dev/null || { warn "Re-cloning..."; rm -rf .git; }
fi
if [ ! -d ".git" ]; then
    log "Cloning repository..."; git clone https://github.com/MDHojayfa/lombaohsint.git . || error "Git clone failed."
fi

# --- INSTALL SYSTEM DEPENDENCIES ---
case $OS in
    TERMUX)
        log "Installing Termux dependencies..."
        pkg update -y
        pkg install python git curl wget openssl-tool libffi clang make gcc proot-distro -y
        ;;

    KALI|UBUNTU|DEBIAN)
        log "Installing system dependencies..."
        apt-get update -y
        apt-get install -y python3 python3-venv git curl wget tor nmap hydra hashcat amass subfinder \
            shodan-cli censys dos2unix build-essential python3-dev libxml2-dev libxslt-dev libffi-dev \
            libssl-dev libjpeg-dev zlib1g-dev
        ;;
esac

# --- PYTHON VENV ---
if [[ "$OS" != "TERMUX" ]]; then
    log "Creating Python venv..."
    python3 -m venv "$BASE_DIR/venv" || error "venv failed."
    source "$BASE_DIR/venv/bin/activate"
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
    success "Python deps installed."
fi

# --- HACKER VIBE SPINNER ---
spinner() {
    local pid=$!
    local delay=0.1
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

(glitch "Initializing DarkNet Protocols..."; sleep 3) & spinner
(glitch "Injecting Dependencies..."; sleep 2) & spinner
(glitch "Finalizing Installation..."; sleep 2) & spinner

success "✅ Installation Complete!"
echo -e "${YELLOW}Run:${NC} lombaohsint --target test@example.com --level BLACK --i-am-authorized"
