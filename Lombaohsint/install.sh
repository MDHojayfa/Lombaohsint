#!/bin/bash
# install.sh — Lombaohsint v2.0 Black Edition — ULTRA HACKER INSTALLER
# Author: MDHojayfa | MDTOOLS (modified)
# Run as root (or in Termux). Tested flow & improved error handling + hacker vibe.

set -euo pipefail
IFS=$'\n\t'

# ----------------------
# Colors & helpers
# ----------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
PURPLE='\033[0;35m'
WHITE='\033[1;37m'
NC='\033[0m'

log()    { echo -e "${CYAN}[+]${NC} $1"; }
warn()   { echo -e "${YELLOW}[!]${NC} $1"; }
error()  { echo -e "${RED}[-]${NC} $1"; exit 1; }
success(){ echo -e "${GREEN}[✓]${NC} $1"; }

# ----------------------
# Glitch / small effects
# ----------------------
glitch_line(){
  local txt="$1"
  local rounds=${2:-4}
  for i in $(seq 1 $rounds); do
    printf "${PURPLE}%s\r${NC}" "$(echo "$txt" | sed -E 's/./& /g' | tr 'A-Za-z' 'N-ZA-Mn-za-m')"  # small rotate
    sleep 0.03
    printf "${RED}%s\r${NC}" "$(echo "$txt" | rev)"
    sleep 0.03
    printf "${GREEN}%s\r${NC}" "$txt"
    sleep 0.03
  done
  printf "\n"
}

# spinner for long commands (run command in background)
run_with_spinner(){
  local cmd="$1"
  local msg="$2"
  local delay=0.08
  local spinstr='|/-\'
  printf "%s " "$msg"
  bash -c "$cmd" & pid=$!
  while kill -0 $pid 2>/dev/null; do
    for c in $spinstr; do
      printf "%s" "$c"
      sleep $delay
      printf "\b"
    done
  done
  wait $pid || return $?
  printf "\n"
  return 0
}

# ----------------------
# Main banner (big)
# ----------------------
clear
echo -e "${GREEN}"
cat <<'ASCII'
 __      __  ____  __  __  ____    _    ____   _   _ _____ _   _ _____ 
 \ \    / / |  _ \|  \/  |/ ___|  / \  |  _ \ | | | |_   _| | | | ____|
  \ \  / /  | |_) | |\/| | |  _  / _ \ | |_) || | | | | | | | | |  _|  
   \ \/ /   |  _ <| |  | | |_| |/ ___ \|  _ < | |_| | | | | |_| | |___ 
    \__/    |_| \_\_|  |_|\____/_/   \_\_| \_\ \___/  |_|  \___/|_____|

                      L O M B A O H S I N T
               by MDHojayfa — v2.0 BLACK EDITION
ASCII
echo -e "${NC}"
glitch_line "Initializing LOMBAOHSINT ..." 6

# ----------------------
# Check root / termux
# ----------------------
if [[ "$EUID" -ne 0 ]] && [[ ! -f "/data/data/com.termux/files/usr/bin/pkg" ]]; then
  error "Run as root. Use: sudo bash $0"
fi

BASE_DIR="${HOME}/lombaohsint"
mkdir -p "$BASE_DIR"
cd "$BASE_DIR" || error "Cannot cd to $BASE_DIR"

# ----------------------
# Detect OS
# ----------------------
OS=""
if [[ -n "${PREFIX-}" ]] && [[ "$PREFIX" == *"/data/data/com.termux/files/usr"* ]]; then
  OS="TERMUX"
  log "Detected platform: Termux (Android)"
elif [[ -f /etc/os-release ]]; then
  if grep -qi "kali" /etc/os-release; then OS="KALI"; log "Detected: Kali Linux"; fi
  if grep -qi "ubuntu" /etc/os-release; then OS="UBUNTU"; log "Detected: Ubuntu"; fi
  if grep -qi "debian" /etc/os-release; then OS="DEBIAN"; log "Detected: Debian"; fi
fi

if [[ -z "$OS" ]]; then
  error "Unsupported OS. This installer supports: Termux, Kali, Ubuntu, Debian."
fi

# ----------------------
# Clone or update repo
# ----------------------
if [[ -d .git ]]; then
  log "Updating repository..."
  git pull --ff-only origin main 2>/dev/null || { warn "Git pull failed; re-cloning..."; rm -rf .git; fi
fi

if [[ ! -d .git ]]; then
  log "Cloning repository..."
  run_with_spinner "git clone https://github.com/MDHojayfa/Lombaohsint.git . 2>/dev/null" "Cloning repo..."
fi

# ensure dos2unix available (fix CRLF)
case "$OS" in
  TERMUX)
    : # handled below
    ;;
  *)
    if ! command -v dos2unix >/dev/null 2>&1; then
      log "Installing dos2unix..."
      apt-get update -y >/dev/null 2>&1 || warn "apt-get update failed"
      run_with_spinner "apt-get install -y dos2unix >/dev/null 2>&1" "Installing dos2unix..."
    fi
    ;;
esac

# ----------------------
# Install system deps
# ----------------------
case "$OS" in
  TERMUX)
    log "Installing Termux packages..."
    run_with_spinner "pkg update -y >/dev/null 2>&1" "pkg update..."
    # Avoid installing 'gcc' separately; use clang/build tools available in Termux
    run_with_spinner "pkg install -y python git curl wget openssl-tool libffi clang make proot-distro dos2unix >/dev/null 2>&1" "pkg install (Termux)..."
    # ensure proot ubuntu chroot exists for heavier deps if needed
    if ! proot-distro list 2>/dev/null | grep -qi ubuntu; then
      log "Installing Ubuntu proot-distro (Termux)..."
      run_with_spinner "proot-distro install ubuntu >/dev/null 2>&1" "proot-distro install ubuntu..."
    fi
    ;;

  KALI|UBUNTU|DEBIAN)
    log "Installing APT packages (this may take a while)..."
    apt-get update -y >/dev/null 2>&1 || warn "apt-get update failed"
    run_with_spinner "apt-get install -y python3 python3-venv python3-pip git curl wget tor nmap hydra hashcat amass subfinder shodan-cli censys dos2unix build-essential python3-dev libxml2-dev libxslt-dev libffi-dev libssl-dev libjpeg-dev zlib1g-dev >/dev/null 2>&1" "apt-get install (core deps)..."
    ;;
esac

# ----------------------
# Create venv & install python deps
# ----------------------
if [[ "$OS" != "TERMUX" ]]; then
  if ! python3 -m venv --help >/dev/null 2>&1; then
    error "python3-venv missing. Install: apt install python3-venv"
  fi

  log "Creating/activating Python virtualenv..."
  python3 -m venv "$BASE_DIR/venv" >/dev/null 2>&1 || warn "venv creation warning"
  # shellcheck disable=SC1091
  source "$BASE_DIR/venv/bin/activate"

  log "Upgrading pip, setuptools, wheel..."
  run_with_spinner "pip install --upgrade pip setuptools wheel >/dev/null 2>&1" "Upgrading pip..."

  if [[ -f requirements.txt ]]; then
    log "Installing Python packages from requirements.txt (prefer binary builds)..."
    # prefer binary wheels to avoid local compiling; fallback if needed
    if ! run_with_spinner "pip install --prefer-binary -r requirements.txt >/dev/null 2>&1" "pip install -r requirements.txt..."; then
      warn "pip install failed first time — trying without --prefer-binary to get full error output..."
      # Show the error to user (no redirection) so they can debug if compile fails
      pip install -r requirements.txt || { warn "pip install still failed. See error above for missing system libs or conflicts."; }
    fi
    success "Python dependencies installed (or attempted)."
  else
    warn "requirements.txt not found in repo root."
  fi

  # create convenient alias
  if ! grep -q "alias lombaohsint=" "$HOME/.bashrc" 2>/dev/null; then
    echo "alias lombaohsint='source \"$BASE_DIR/venv/bin/activate\" && python3 \"$BASE_DIR/main.py\"'" >> "$HOME/.bashrc"
    log "Alias 'lombaohsint' added to ~/.bashrc"
  fi
fi

# ----------------------
# Copy defaults, create dirs
# ----------------------
log "Setting up data folders and config..."
mkdir -p data/cache/email_cache data/cache/phone_cache data/cache/username_cache data/cache/darkweb_cache data/logs reports
touch data/cache/email_cache/.gitkeep data/cache/phone_cache/.gitkeep data/cache/username_cache/.gitkeep data/cache/darkweb_cache/.gitkeep data/logs/.gitkeep reports/.gitkeep data/breaches.sqlite

# copy default files if existing in repo root
for f in assets/banner.txt assets/quotes.txt config.yaml requirements.txt; do
  if [[ -f "$f" ]]; then
    cp -f "$f" .
  fi
done

# default config creation (if absent)
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

# ----------------------
# Start tor (if installed)
# ----------------------
if command -v tor >/dev/null 2>&1 && [[ "$OS" != "TERMUX" ]]; then
  run_with_spinner "systemctl enable tor >/dev/null 2>&1 || true" "Enabling tor service..."
  run_with_spinner "systemctl start tor >/dev/null 2>&1 || true" "Starting tor..."
  log "Tor service: started (if available)"
fi

# ----------------------
# Self-test (non-blocking)
# ----------------------
log "Running light self-test (non-blocking)..."
if [[ "$OS" = "TERMUX" ]]; then
  if command -v proot-distro >/dev/null 2>&1; then
    proot-distro login ubuntu -- bash -c "cd $BASE_DIR && python3 main.py --target test@mdtools.local --level GENTLE --i-am-authorized" >/dev/null 2>&1 || warn "Self-test skipped or failed (Termux chroot)."
  else
    warn "proot-distro missing — skipping Termux self-test."
  fi
else
  if [[ -f "$BASE_DIR/venv/bin/activate" ]]; then
    ( source "$BASE_DIR/venv/bin/activate" && python3 "$BASE_DIR/main.py" --target test@mdtools.local --level GENTLE --i-am-authorized ) >/dev/null 2>&1 || warn "Self-test skipped (no internet or failure)."
  fi
fi

# ----------------------
# Fin
# ----------------------
success "Installation finished."
echo -e "${YELLOW}Run:${NC} lombaohsint --target test@example.com --level BLACK --i-am-authorized"
echo -e "${PURPLE}Remember: Use responsibly. Only scan with authorization.${NC}"
