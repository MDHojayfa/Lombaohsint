#!/bin/bash

# ███████╗███████╗██████╗ ██╗   ██╗██████╗ ███████╗
# ██╔════╝██╔════╝██╔══██╗██║   ██║██╔══██╗██╔════╝
# █████╗  █████╗  ██████╔╝██║   ██║██████╔╝█████╗  
# ██╔══╝  ██╔══╝  ██╔══██╗██║   ██║██╔══██╗██╔══╝  
# ██║     ███████╗██║  ██║╚██████╔╝██║  ██║███████╗
# ╚═╝     ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝
#            LOMBAOHSINT v2.0 BLACK EDITION
#       The Unrestricted OSINT Apocalypse
#          By MDHojayfa | MDTOOLS

# ██╗  ██╗ ██████╗ ███████╗███████╗ ██████╗ ███████╗
# ██║  ██║██╔═══██╗██╔════╝██╔════╝██╔═══██╗██╔════╝
# ███████║██║   ██║█████╗  █████╗  ██║   ██║███████╗
# ██╔══██║██║   ██║██╔══╝  ██╔══╝  ██║   ██║╚════██║
# ██║  ██║╚██████╔╝███████╗███████╗╚██████╔╝███████║
# ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝ ╚═════╝ ╚══════╝

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
MAGENTA='\033[1;35m'
BLUE='\033[1;34m'
WHITE='\033[1;37m'
GRAY='\033[1;90m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ███╗   ██╗ ██████╗ ████████╗ █████╗ ██╗   ██╗
# ████╗  ██║██╔═══██╗╚══██╔══╝██╔══██╗██║   ██║
# ██╔██╗ ██║██║   ██║   ██║   ███████║██║   ██║
# ██║╚██╗██║██║   ██║   ██║   ██╔══██║██║   ██║
# ██║ ╚████║╚██████╔╝   ██║   ██║  ██║╚██████╔╝
# ╚═╝  ╚═══╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝ ╚═════╝

# --- ANIMATED ASCII BANNER ---
print_banner() {
    clear
    echo -e "${RED}"
    cat << 'EOF'
██████╗ ██████╗ ███████╗███████╗███████╗ ██████╗ ███████╗
██╔══██╗██╔═══██╗██╔════╝██╔════╝██╔════╝██╔═══██╗██╔════╝
██████╔╝██║   ██║█████╗  █████╗  █████╗  ██║   ██║███████╗
██╔══██╗██║   ██║██╔══╝  ██╔══╝  ██╔══╝  ██║   ██║╚════██║
██████╔╝╚██████╔╝███████╗███████╗███████╗╚██████╔╝███████║
╚═════╝  ╚═════╝ ╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚══════╝
EOF
    echo -e "${CYAN}  [LombaoHsint v2.0 BLACK EDITION]${NC}"
    echo -e "${YELLOW}  [MDTOOLS — The Truth Doesn't Wait]${NC}"
    echo -e "${GRAY}  [No Root? No Problem. No Internet? No Excuse.]${NC}"
    echo -e "${NC}"
    sleep 1
}

# --- PROGRESS BAR WITH HACKER VIBE ---
hacker_progress() {
    local text="$1"
    local delay=${2:-0.05}
    echo -ne "${BLUE}[\e[5m${NC}${WHITE}█${NC}${BLUE}]\e[25m${NC} ${text} "
    for i in {1..40}; do
        echo -ne "${GREEN}█${NC}"
        sleep $delay
    done
    echo -e " ${GREEN}✓${NC}"
}

# --- LOGGING WITH HACKER STYLE ---
log() {
    echo -e "${BLUE}[+]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

error() {
    echo -e "${RED}[-]${NC} $1"
    exit 1
}

success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

# --- MAIN ---
print_banner

# --- CHECK ROOT ---
if [[ "$EUID" -ne 0 ]] && [[ ! -f "/data/data/com.termux/files/usr/bin/pkg" ]]; then
    error "ACCESS DENIED. This tool requires root privileges. Run: sudo bash $0"
fi

# --- DETECT OS ---
if [ -n "$PREFIX" ] && [[ "$PREFIX" == *"/data/data/com.termux/files/usr"* ]]; then
    OS="TERMUX"
    log "DETECTED: ${YELLOW}Termux (Android)${NC} — ${GREEN}Unrooted? Good. We don't need it.${NC}"
elif [ -f "/etc/os-release" ] && grep -q "Kali" /etc/os-release; then
    OS="KALI"
    log "DETECTED: ${RED}Kali Linux${NC} — ${GREEN}Welcome, predator.${NC}"
elif [ -f "/etc/os-release" ] && grep -q "Ubuntu" /etc/os-release; then
    OS="UBUNTU"
    log "DETECTED: ${CYAN}Ubuntu 22.04+${NC} — ${GREEN}System secured. Let's bypass it.${NC}"
elif [ -f "/etc/os-release" ] && grep -q "Debian" /etc/os-release; then
    OS="DEBIAN"
    log "DETECTED: ${CYAN}Debian 12+${NC} — ${GREEN}Quiet. Deadly. Efficient.${NC}"
else
    error "UNSUPPORTED OS. This tool runs on Kali, Ubuntu, Debian, or Termux."
fi

# --- CREATE BASE DIR ---
BASE_DIR="/root/lombaohsint"
mkdir -p "$BASE_DIR"
cd "$BASE_DIR" || error "Failed to enter base directory."

# --- CLEAN SLATE ---
log "CLEANING OLD INSTALLATIONS..."
rm -rf "$BASE_DIR"/lombaohsint 2>/dev/null

# --- CLONE REPO ---
log "CLONING REPOSITORY..."
hacker_progress "Fetching lombaohsint from GitHub" 0.02
git clone https://github.com/MDHojayfa/lombaohsint.git . 2>/dev/null || error "CLONE FAILED. Check internet or repo URL."

# --- FIX LINE ENDINGS ---
log "FIXING LINE ENDINGS (CRLF → LF)..."
hacker_progress "Converting files to Unix format" 0.01
if command -v dos2unix &>/dev/null; then
    find . -type f \( -name "*.py" -o -name "*.sh" \) -exec dos2unix {} \; >/dev/null 2>&1
else
    warn "dos2unix not found. Installing..."
    case $OS in
        TERMUX)
            pkg install dos2unix -y >/dev/null 2>&1
            ;;
        *)
            apt-get update -y >/dev/null 2>&1
            apt-get install dos2unix -y >/dev/null 2>&1
            ;;
    esac
    find . -type f \( -name "*.py" -o -name "*.sh" \) -exec dos2unix {} \; >/dev/null 2>&1
fi

# --- INSTALL SYSTEM DEPENDENCIES ---
log "INSTALLING SYSTEM DEPENDENCIES..."
case $OS in
    TERMUX)
        hacker_progress "Installing Termux core tools" 0.01
        pkg update -y >/dev/null 2>&1
        pkg install python git curl wget openssl-tool libffi clang make gcc proot-distro -y >/dev/null 2>&1
        if ! proot-distro list | grep -q "ubuntu"; then
            log "INSTALLING UBUNTU CHROOT..."
            proot-distro install ubuntu >/dev/null 2>&1
        fi
        proot-distro login ubuntu -- sh -c "apt update && apt upgrade -y" >/dev/null 2>&1
        if [ ! -L "$HOME/sdcard" ]; then
            ln -sf /storage/emulated/0 "$HOME/sdcard"
            success "SYMLINKED: ~/sdcard → Android Storage"
        fi
        echo "alias lombaohsint='proot-distro login ubuntu -- bash -c \"cd $BASE_DIR && python3 main.py\"'" >> ~/.bashrc
        source ~/.bashrc
        success "ALIAS CREATED: 'lombaohsint'"
        ;;

    KALI|UBUNTU|DEBIAN)
        hacker_progress "Installing system packages" 0.01
        apt-get update -y >/dev/null 2>&1
        apt-get install python3 python3-venv git curl wget tor nmap hydra hashcat amass subfinder shodan-cli censys dos2unix -y >/dev/null 2>&1

        # --- CREATE VIRTUAL ENVIRONMENT ---
        log "CREATING PYTHON VIRTUAL ENVIRONMENT..."
        python3 -m venv "$BASE_DIR/venv" || error "Failed to create virtual environment. Is python3-venv installed?"
        source "$BASE_DIR/venv/bin/activate" || error "Failed to activate virtual environment."

        # --- INSTALL PYTHON DEPENDENCIES ---
        hacker_progress "Installing Python packages" 0.01
        pip install --upgrade pip >/dev/null 2>&1
        pip install -r requirements.txt --break-system-packages >/dev/null 2>&1

        # --- CREATE GLOBAL ALIAS ---
        echo "alias lombaohsint='source \"$BASE_DIR/venv/bin/activate\" && python3 \"$BASE_DIR/main.py\"'" >> ~/.bashrc
        source ~/.bashrc
        success "ALIAS CREATED: 'lombaohsint'"

        # --- START TOR ---
        if command -v tor &>/dev/null; then
            systemctl enable tor >/dev/null 2>&1
            systemctl start tor >/dev/null 2>&1
            success "TOR SERVICE: ${GREEN}ACTIVE${NC} (port 9050)"
        fi
        ;;
esac

# --- VERIFY CORE FILES ---
log "VERIFYING CORE FILES..."
required_files=(
    "assets/banner.txt"
    "assets/quotes.txt"
    "config.yaml"
    "requirements.txt"
    "main.py"
    "modules/email_harvest.py"
    "utils/progress.py"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        error "CRITICAL FILE MISSING: $file. Repository is corrupted."
    fi
done

# --- CREATE DATA STRUCTURE ---
log "CREATING DATA STRUCTURE..."
hacker_progress "Initializing data directories" 0.01
mkdir -p data/cache/email_cache data/cache/phone_cache data/cache/username_cache data/cache/darkweb_cache data/logs reports
touch data/cache/email_cache/.gitkeep data/cache/phone_cache/.gitkeep data/cache/username_cache/.gitkeep data/cache/darkweb_cache/.gitkeep data/logs/.gitkeep reports/.gitkeep data/breaches.sqlite

# --- GENERATE DEFAULT CONFIG IF MISSING ---
if [ ! -f "config.yaml" ]; then
    log "GENERATING DEFAULT CONFIG.YAML..."
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
    success "CONFIG.YAML GENERATED — FILL YOUR KEYS."
fi

# --- SELF-TEST ---
log "RUNNING SELF-TEST..."
hacker_progress "Verifying tool functionality" 0.03
if [ "$OS" = "TERMUX" ]; then
    proot-distro login ubuntu -- bash -c "cd $BASE_DIR && python3 main.py --target test@mdtools.local --level GENTLE --i-am-authorized" 2>/dev/null || warn "Self-test skipped (no internet or slow)."
else
    source "$BASE_DIR/venv/bin/activate" && python3 main.py --target test@mdtools.local --level GENTLE --i-am-authorized 2>/dev/null || warn "Self-test skipped (no internet or slow)."
fi

# --- FINAL BANNER ---
echo -e "\n${MAGENTA}████████████████████████████████████████████████████████████████████████████${NC}"
echo -e "${GREEN}████████████████████████████████████████████████████████████████████████████${NC}"
echo -e "${WHITE}█████  LOMBAOHSINT v2.0 BLACK EDITION — INSTALLATION COMPLETE  █████${NC}"
echo -e "${GREEN}████████████████████████████████████████████████████████████████████████████${NC}"
echo -e "${MAGENTA}████████████████████████████████████████████████████████████████████████████${NC}"
echo -e "${YELLOW}█████  RUN: lombaohsint --target john.doe@example.com --level BLACK --i-am-authorized  █████${NC}"
echo -e "${WHITE}█████  YOU NOW HOLD THE KEYS TO THE DARKNET. USE WISELY.  █████${NC}"
echo -e "${RED}█████  THIS TOOL IS A WEAPON. YOU ARE RESPONSIBLE.  █████${NC}"
echo -e "${MAGENTA}████████████████████████████████████████████████████████████████████████████${NC}"
echo -e "${GREEN}████████████████████████████████████████████████████████████████████████████${NC}"

echo -e "\n${BLUE}┌────────────────────────────────────────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│ ${WHITE}Next Steps:                                                                  ${BLUE}│${NC}"
echo -e "${BLUE}│ ${WHITE}1. Edit config.yaml and add your API keys                                    ${BLUE}│${NC}"
echo -e "${BLUE}│ ${WHITE}2. Run: lombaohsint --target target@example.com --level BLACK --i-am-authorized  ${BLUE}│${NC}"
echo -e "${BLUE}│ ${WHITE}3. Check reports/ folder for HTML/MD/JSON reports                            ${BLUE}│${NC}"
echo -e "${BLUE}│ ${WHITE}4. Use 'update.sh' to pull latest updates                                    ${BLUE}│${NC}"
echo -e "${BLUE}└────────────────────────────────────────────────────────────────────────────┘${NC}"

echo -e "\n${GRAY}███  The truth doesn't wait. You do.  ███${NC}"
