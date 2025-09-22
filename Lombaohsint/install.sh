#!/bin/bash
# install.sh — Lombaohsint v2.0 Black Edition — ULTRA HACKER INSTALLER
# Carefully checked version — by assistant
set -euo pipefail
IFS=$'\n\t'

# ----------------------------
# Colors & helper functions
# ----------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
PURPLE='\033[0;35m'
WHITE='\033[1;37m'
NC='\033[0m'

log()     { printf "${CYAN}[+]${NC} %s\n" "$1"; }
warn()    { printf "${YELLOW}[!]${NC} %s\n" "$1"; }
error()   { printf "${RED}[-]${NC} %s\n" "$1"; exit 1; }
success() { printf "${GREEN}[✓]${NC} %s\n" "$1"; }

# ----------------------------
# Small glitch animation (safe)
# ----------------------------
glitch_line() {
  local txt="$1"
  local rounds=${2:-3}
  for ((r=0; r<rounds; r++)); do
    printf "${PURPLE}%s\r${NC}" "$(echo "$txt" | sed -E 's/./& /g')"
    sleep 0.04
    printf "${RED}%s\r${NC}" "$(echo "$txt" | rev)"
    sleep 0.04
    printf "${GREEN}%s\r${NC}" "$txt"
    sleep 0.04
  done
  printf "\n"
}

# ----------------------------
# Run a command with a spinner (shows while command runs)
# usage: run_with_spinner "long-command-here" "Message to show..."
# ----------------------------
run_with_spinner() {
  local cmd="$1"
  local msg="$2"
  local spinstr='|/-\'
  printf "%s " "$msg"
  bash -c "$cmd" & pid=$!
  # spinner loop
  while kill -0 "$pid" 2>/dev/null; do
    for ((i=0; i<${#spinstr}; i++)); do
      printf "%s" "${spinstr:i:1}"
      sleep 0.08
      printf "\b"
    done
  done
  wait "$pid"
  local rc=$?
  printf "\n"
  return $rc
}

# ----------------------------
# Banner (LOMBAOHSINT)
# ----------------------------
clear
echo -e "${WHITE}"
cat <<'BANNER'
 __      __  ____  __  __  ____    _    ____   _   _ _____ _   _ _____ 
 \ \    / / |  _ \|  \/  |/ ___|  / \  |  _ \ | | | |_   _| | | | ____|
  \ \  / /  | |_) | |\/| | |  _  / _ \ | |_) || | | | | | | | |  _|  
   \ \/ /   |  _ <| |  | | |_| |/ ___ \|  _ < | |_| | | | | |_| | |___ 
    \__/    |_| \_\_|  |_|\____/_/   \_\_| \_\ \___/  |_|  \___/|_____|

                      L O M B A O H S I N T
               by MDHojayfa — v2.0 BLACK EDITION
BANNER
echo -e "${NC}"
glitch_line "Booting LOMBAOHSINT installer..." 5

# ----------------------------
# Root / Termux check
# ----------------------------
if [[ "$EUID" -ne 0 ]] && [[ ! -f "/data/data/com.termux/files/usr/bin/pkg" ]]; then
  error "This script must be run as root. Use: sudo bash $0"
fi

# ----------------------------
# Prepare base dir
# ----------------------------
BASE_DIR="${HOME}/lombaohsint"
mkdir -p "$BASE_DIR"
cd "$BASE_DIR" || error "Failed to cd to $BASE_DIR"

# ----------------------------
# Detect OS (TERMUX / KALI / UBUNTU / DEBIAN)
# ----------------------------
OS=""
if [[ -n "${PREFIX-}" ]] && [[ "$PREFIX" == *"/data/data/com.termux/files/usr"* ]]; then
  OS="TERMUX"
  log "Platform: Termux (Android)"
elif [[ -f /etc/os-release ]]; then
  if grep -qi "kali" /etc/os-release; then OS="KALI"; log "Platform: Kali Linux"; fi
  if grep -qi "ubuntu" /etc/os-release; then OS="UBUNTU"; log "Platform: Ubuntu"; fi
  if grep -qi "debian" /etc/os-release; then OS="DEBIAN"; log "Platform: Debian"; fi
fi

if [[ -z "$OS" ]]; then
  error "Unsupported OS. Supported: Termux, Kali, Ubuntu, Debian."
fi

# ----------------------------
# Clone or update repo
# ----------------------------
if [[ -d .git ]]; then
  log "Updating repository..."
  if ! git pull --ff-only origin main 2>/dev/null; then
    warn "Git pull failed — will re-clone to ensure a clean repo."
    rm -rf .git
  fi
fi

if [[ ! -d .git ]]; then
  run_with_spinner "git clone https://github.com/MDHojayfa/Lombaohsint.git . 2>/dev/null" "Cloning repository..."
fi

# ----------------------------
# Install system dependencies
# ----------------------------
case "$OS" in
  TERMUX)
    log "Updating Termux packages..."
    run_with_spinner "pkg update -y >/dev/null 2>&1" "pkg update..."
    log "Installing Termux packages..."
    # clang, make present in Termux; don't attempt apt packages
    run_with_spinner "pkg install -y python git curl wget openssl-tool libffi clang make proot-distro dos2unix >/dev/null 2>&1" "pkg install..."
    ;;
  KALI|UBUNTU|DEBIAN)
    log "Updating APT and installing system dependencies... (may take time)"
    run_with_spinner "apt-get update -y >/dev/null 2>&1" "apt-get update..."
    # core packages: build-essential covers gcc/g++
    run_with_spinner "apt-get install -y python3 python3-venv python3-pip git curl wget tor nmap hydra hashcat amass subfinder shodan-cli censys dos2unix build-essential python3-dev libxml2-dev libxslt-dev libffi-dev libssl-dev libjpeg-dev zlib1g-dev >/dev/null 2>&1" "apt-get install..."
    ;;
  *)
    error "Unexpected OS value: $OS"
    ;;
esac

# ----------------------------
# dos2unix fix for scripts (if available)
# ----------------------------
if command -v dos2unix >/dev/null 2>&1; then
  log "Fixing CRLF -> LF for .py/.sh files..."
  find . -type f \( -name "*.py" -o -name "*.sh" \) -exec dos2unix {} \; >/dev/null 2>&1 || warn "dos2unix run had issues (non-fatal)."
fi

# ----------------------------
# Python venv & pip install
# ----------------------------
if [[ "$OS" != "TERMUX" ]]; then
  # venv check
  if ! python3 -m venv --help >/dev/null 2>&1; then
    error "python3-venv missing. Install: apt install python3-venv"
  fi

  log "Creating Python virtual environment..."
  if [[ ! -d "$BASE_DIR/venv" ]]; then
    python3 -m venv "$BASE_DIR/venv"
  fi

  # shellcheck disable=SC1091
  source "$BASE_DIR/venv/bin/activate"

  log "Upgrading pip, setuptools, wheel..."
  run_with_spinner "pip install --upgrade pip setuptools wheel >/dev/null 2>&1" "Upgrading pip..."

  if [[ -f requirements.txt ]]; then
    log "Installing Python packages from requirements.txt (prefer binary wheels first)..."
    # try prefer-binary first to reduce local builds
    if run_with_spinner "pip install --prefer-binary -r requirements.txt >/dev/null 2>&1" "pip installing (prefer-binary)..."; then
      success "Python packages installed (binary preferred)."
    else
      warn "Prefer-binary install failed — retrying without suppressing errors to show root cause."
      # show install output so user can debug missing system libs
      pip install -r requirements.txt || warn "pip install failed. See messages above for missing deps / conflicts."
    fi
  else
    warn "requirements.txt not found in repository root."
  fi

  # add alias to .bashrc if not present
  if ! grep -q "alias lombaohsint=" "$HOME/.bashrc" 2>/dev/null; then
    echo "alias lombaohsint='source \"$BASE_DIR/venv/bin/activate\" && python3 \"$BASE_DIR/main.py\"'" >> "$HOME/.bashrc"
    log "Alias 'lombaohsint' added to ~/.bashrc"
  fi
else
  # Termux note: dependencies that need apt (Debian libs) should be used inside proot-distro ubuntu if needed
  log "Termux detected — Python requirements should be installed inside Ubuntu proot-distro for best compatibility."
  if command -v proot-distro >/dev/null 2>&1; then
    log "You can run: proot-distro login ubuntu -- bash -c 'cd $BASE_DIR && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt'"
  fi
fi

# ----------------------------
# Create folders, copy defaults
# ----------------------------
log "Creating data directories and copying default assets..."
mkdir -p data/cache/email_cache data/cache/phone_cache data/cache/username_cache data/cache/darkweb_cache data/logs reports
touch data/cache/email_cache/.gitkeep data/cache/phone_cache/.gitkeep data/cache/username_cache/.gitkeep data/cache/darkweb_cache/.gitkeep data/logs/.gitkeep reports/.gitkeep data/breaches.sqlite

for f in assets/banner.txt assets/quotes.txt config.yaml requirements.txt; do
  if [[ -f "$f" ]]; then
    cp -f "$f" .
  fi
done

# create default config.yaml if missing
if [[ ! -f config.yaml ]]; then
  cat > config.yaml <<'YAML'
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
YAML
  log "Default config.yaml created."
fi

# ----------------------------
# Start tor service (if possible)
# ----------------------------
if [[ "$OS" != "TERMUX" ]] && command -v tor >/dev/null 2>&1; then
  run_with_spinner "systemctl enable tor >/dev/null 2>&1 || true" "Enabling tor..."
  run_with_spinner "systemctl start tor >/dev/null 2>&1 || true" "Starting tor..."
  log "Tor started (if available)."
fi

# ----------------------------
# Light self-test (non-blocking, safe)
# ----------------------------
log "Performing light self-test (non-blocking)..."
if [[ "$OS" = "TERMUX" ]]; then
  if command -v proot-distro >/dev/null 2>&1; then
    proot-distro login ubuntu -- bash -c "cd $BASE_DIR && python3 main.py --target test@mdtools.local --level GENTLE --i-am-authorized" >/dev/null 2>&1 || warn "Termux self-test skipped/failed."
  else
    warn "Termux proot-distro not found; skipping Termux self-test."
  fi
else
  if [[ -f "$BASE_DIR/venv/bin/activate" ]]; then
    ( source "$BASE_DIR/venv/bin/activate" && python3 "$BASE_DIR/main.py" --target test@mdtools.local --level GENTLE --i-am-authorized ) >/dev/null 2>&1 || warn "Self-test skipped or failed."
  fi
fi

# ----------------------------
# Finish
# ----------------------------
success "Installation completed."
echo -e "${YELLOW}How to run:${NC} lombaohsint --target test@example.com --level BLACK --i-am-authorized"
echo -e "${PURPLE}⚠️  Use only with authorization. Respect laws and privacy.${NC}"
