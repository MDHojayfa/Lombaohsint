#!/usr/bin/env bash
# ============================================================
# LOMBAOHSINT — Ultra Hacker Installer v3.0
# Carefully checked, logs outputs, auto-installs lxml deps,
# supports Termux & Debian/Ubuntu/Kali. Shows outputs & errors.
# ============================================================

set -uo pipefail
IFS=$'\n\t'

# -----------------------
# Colors
# -----------------------
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[1;36m'; PURPLE='\033[0;35m'; WHITE='\033[1;37m'; NC='\033[0m'

# -----------------------
# Globals & logs
# -----------------------
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$BASE_DIR/.install_logs"
mkdir -p "$LOG_DIR"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
MASTER_LOG="$LOG_DIR/install_$TIMESTAMP.log"
ERRORS=()      # array of "label::logfile"
SUCCESS=()     # array of success messages

# -----------------------
# Helpers
# -----------------------
info()    { printf "${CYAN}[+]${NC} %s\n" "$1"; }
warn()    { printf "${YELLOW}[!]%s${NC}\n" "$1"; }
err()     { printf "${RED}[-] %s${NC}\n" "$1"; }
ok()      { printf "${GREEN}[✓] %s${NC}\n" "$1"; }

# write header to master log
echo "LOMBAOHSINT installer log - $TIMESTAMP" > "$MASTER_LOG"
echo "base_dir: $BASE_DIR" >> "$MASTER_LOG"
echo "" >> "$MASTER_LOG"

# -----------------------
# Small glitch banner
# -----------------------
glitch_line() {
  local txt="$1"
  local rounds=${2:-4}
  for ((r=0; r<rounds; r++)); do
    printf "${PURPLE}%s\r${NC}" "$(echo "$txt" | sed -E 's/./& /g')"
    sleep 0.03
    printf "${RED}%s\r${NC}" "$(echo "$txt" | rev)"
    sleep 0.03
    printf "${GREEN}%s\r${NC}" "$txt"
    sleep 0.03
  done
  printf "\n"
}

# -----------------------
# Banner (LOMBAOHSINT)
# -----------------------
clear
cat <<'BANNER'
 __      __  ____  __  __  ____    _    ____   _   _ _____ _   _ _____ 
 \ \    / / |  _ \|  \/  |/ ___|  / \  |  _ \ | | | |_   _| | | | ____|
  \ \  / /  | |_) | |\/| | |  _  / _ \ | |_) || | | | | | | | |  _|  
   \ \/ /   |  _ <| |  | | |_| |/ ___ \|  _ < | |_| | | | | |_| | |___ 
    \__/    |_| \_\_|  |_|\____/_/   \_\_| \_\ \___/  |_|  \___/|_____|

                      L O M B A O H S I N T
               by MDHojayfa — v3.0 BLACK EDITION
BANNER

glitch_line "Booting LOMBAOHSINT installer..." 6
info "Script location: $BASE_DIR"
echo "" >> "$MASTER_LOG"

# -----------------------
# Run command and log output (streams to terminal and logfile)
# Usage: run_and_log "label" "command..."
# returns the command's exit code
# -----------------------
run_and_log() {
  local label="$1"
  shift
  local cmd=( "$@" )
  local safe_label
  safe_label="$(echo "$label" | tr ' /' '__')"
  local logfile="$LOG_DIR/${TIMESTAMP}_${safe_label}.log"

  printf "%s " "${CYAN}[*]${NC} $label..."
  # run command, stream stdout/stderr to both terminal and logfile
  # We use bash -c to preserve user's command string behavior
  {
    echo "[$(date '+%F %T')] === START: $label ==="
    echo "Command: ${cmd[*]}"
  } >> "$logfile"
  # run and tee
  if "${cmd[@]}" 2>&1 | tee -a "$logfile"; then
    printf "\r${GREEN}[✓]${NC} %s\n" "$label"
    echo "[$(date '+%F %T')] === END: $label (OK) ===" >> "$logfile"
    echo "=== $label ===" >> "$MASTER_LOG"
    tail -n 20 "$logfile" >> "$MASTER_LOG"
    SUCCESS+=("$label::$logfile")
    return 0
  else
    printf "\r${RED}[✗]${NC} %s\n" "$label"
    echo "[$(date '+%F %T')] === END: $label (FAILED) ===" >> "$logfile"
    ERRORS+=("$label::$logfile")
    echo "=== $label (FAILED) ===" >> "$MASTER_LOG"
    tail -n 40 "$logfile" >> "$MASTER_LOG"
    return 1
  fi
}

# -----------------------
# Platform detect
# -----------------------
OS_TYPE=""
if [[ -n "${PREFIX-}" ]] && [[ "$PREFIX" == *"/data/data/com.termux/files/usr"* ]]; then
  OS_TYPE="TERMUX"
  info "Detected platform: Termux (Android)"
elif [[ -f /etc/os-release ]]; then
  if grep -qi "kali" /etc/os-release; then OS_TYPE="KALI"; info "Detected platform: Kali Linux"; fi
  if grep -qi "ubuntu" /etc/os-release; then OS_TYPE="UBUNTU"; info "Detected platform: Ubuntu"; fi
  if grep -qi "debian" /etc/os-release; then OS_TYPE="DEBIAN"; info "Detected platform: Debian"; fi
fi

if [[ -z "$OS_TYPE" ]]; then
  warn "Cannot reliably detect OS. Attempting best-effort using apt/pkg."
  # still proceed, but later package installs may fail
fi

# -----------------------
# Ensure we operate in repo root (don't clone new dir)
# -----------------------
info "Ensuring working directory is repository root (script dir)."
cd "$BASE_DIR" || { err "Cannot cd to $BASE_DIR"; exit 1; }

# -----------------------
# Helper: use_sudo
# -----------------------
use_sudo() {
  # returns "" or "sudo"
  if [[ "$EUID" -ne 0 ]]; then
    if command -v sudo >/dev/null 2>&1; then
      printf "sudo"
    else
      warn "Not running as root and sudo not available — some installs may fail."
      printf ""
    fi
  else
    printf ""
  fi
}

# -----------------------
# Install system packages (Termux/Apt wrapper)
# -----------------------
install_system_packages() {
  local label="$1"
  shift
  local pkgs=( "$@" )
  if [[ "${#pkgs[@]}" -eq 0 ]]; then
    warn "No packages passed to install_system_packages"
    return 0
  fi

  if [[ "$OS_TYPE" == "TERMUX" ]]; then
    run_and_log "$label" pkg install -y "${pkgs[@]}"
  else
    local SUDO
    SUDO="$(use_sudo)"
    run_and_log "$label" $SUDO apt-get install -y "${pkgs[@]}"
  fi
}

# -----------------------
# Ensure x packages (safe checks) - example usage later
# -----------------------
ensure_basic_system_packages() {
  info "Installing core system packages (python3, venv, build deps)..."
  if [[ "$OS_TYPE" == "TERMUX" ]]; then
    # Termux: install core packages
    install_system_packages "Termux core packages" python git curl wget proot-distro clang make pkg-config libxml2 libxslt zlib openssl
  else
    # Debian/Ubuntu/Kali
    local apt_pkgs=(python3 python3-venv python3-pip build-essential python3-dev libxml2-dev libxslt-dev libffi-dev libssl-dev libjpeg-dev zlib1g-dev pkg-config dos2unix)
    install_system_packages "APT core packages" "${apt_pkgs[@]}"
  fi
}

# -----------------------
# Automatic lxml deps installer (tries apt or pkg)
# -----------------------
install_lxml_deps() {
  info "Ensuring lxml build dependencies (libxml2-dev, libxslt-dev, python3-dev)..."
  if [[ "$OS_TYPE" == "TERMUX" ]]; then
    install_system_packages "lxml Termux deps" libxml2 libxslt pkg-config
  else
    install_system_packages "lxml APT deps" libxml2-dev libxslt-dev python3-dev build-essential pkg-config
  fi
}

# -----------------------
# Venv & pip requirements
# -----------------------
setup_python_and_requirements() {
  # create venv if missing
  if [[ ! -d "$BASE_DIR/venv" ]]; then
    info "Creating Python virtualenv..."
    if python3 -m venv "$BASE_DIR/venv" 2>&1 | tee "$LOG_DIR/venv_create_$TIMESTAMP.log"; then
      ok "Virtualenv created"
      SUCCESS+=("venv_create::$LOG_DIR/venv_create_$TIMESTAMP.log")
    else
      warn "Virtualenv creation produced warnings/errors (see log)"
      ERRORS+=("venv_create::$LOG_DIR/venv_create_$TIMESTAMP.log")
    fi
  else
    info "Virtualenv found at $BASE_DIR/venv"
  fi

  # activate
  # shellcheck disable=SC1090
  source "$BASE_DIR/venv/bin/activate"

  run_and_log "Upgrading pip/setuptools/wheel" pip install --upgrade pip setuptools wheel

  # ensure lxml deps BEFORE pip install
  install_lxml_deps

  if [[ -f "$BASE_DIR/requirements.txt" ]]; then
    info "Installing Python packages from requirements.txt (first try prefer-binary)..."
    # try prefer-binary first to minimize local compiling
    if run_and_log "pip install (prefer-binary) requirements" pip install --prefer-binary -r "$BASE_DIR/requirements.txt"; then
      ok "Python requirements installed (binary preferred)."
    else
      warn "Prefer-binary attempt failed; retrying with full output to show root-cause."
      if run_and_log "pip install requirements (detailed)" pip install -r "$BASE_DIR/requirements.txt"; then
        ok "Python requirements installed on retry."
      else
        warn "pip install failed — see logs for details."
      fi
    fi
  else
    warn "requirements.txt not found in repo root: $BASE_DIR"
  fi
}

# -----------------------
# Copy defaults & create folders (no duplication)
# -----------------------
prepare_repo_files() {
  info "Creating data folders and copying default assets (if found)..."
  mkdir -p "$BASE_DIR/data/cache/email_cache" "$BASE_DIR/data/cache/phone_cache" \
           "$BASE_DIR/data/cache/username_cache" "$BASE_DIR/data/cache/darkweb_cache" \
           "$BASE_DIR/data/logs" "$BASE_DIR/reports" >/dev/null 2>&1 || true

  touch "$BASE_DIR/data/cache/email_cache/.gitkeep" "$BASE_DIR/data/cache/phone_cache/.gitkeep" \
        "$BASE_DIR/data/cache/username_cache/.gitkeep" "$BASE_DIR/data/cache/darkweb_cache/.gitkeep" \
        "$BASE_DIR/data/logs/.gitkeep" "$BASE_DIR/reports/.gitkeep" "$BASE_DIR/data/breaches.sqlite" >/dev/null 2>&1 || true

  # Copy default assets only if different
  for f in assets/banner.txt assets/quotes.txt config.yaml requirements.txt; do
    if [[ -f "$BASE_DIR/$f" ]]; then
      # it's already in repo root — nothing to do
      continue
    elif [[ -f "$BASE_DIR/../$f" ]]; then
      # if user runs from subdir, copy; but avoid copying same file onto itself
      if [[ "$(readlink -f "$BASE_DIR/../$f")" != "$(readlink -f "$BASE_DIR/$f" 2>/dev/null)" ]]; then
        cp -f "$BASE_DIR/../$f" "$BASE_DIR/" 2>/dev/null || warn "Failed to copy $f from parent"
      fi
    fi
  done
}

# -----------------------
# Optional: proot-distro chroot flow for Termux (interactive)
# -----------------------
termux_chroot_flow() {
  # recommend using Ubuntu chroot to install heavy deps like lxml reliably
  if [[ "$OS_TYPE" != "TERMUX" ]]; then
    return 0
  fi

  info "Termux detected. Installing inside Ubuntu proot-distro is recommended for heavy builds (lxml)."
  if ! command -v proot-distro >/dev/null 2>&1; then
    run_and_log "Install proot-distro in Termux" pkg install -y proot-distro
  fi

  if ! proot-distro list 2>/dev/null | grep -qi ubuntu; then
    info "Ubuntu image not found in proot-distro. Installing (this will download ~100+MB). Proceed? (y/N)"
    read -r -p "> " yn
    if [[ "$yn" =~ ^[Yy]$ ]]; then
      run_and_log "proot-distro install ubuntu" proot-distro install ubuntu
    else
      warn "Skipped proot-distro install. You can still try native Termux install, but lxml may fail."
      return 0
    fi
  fi

  info "Running apt installs inside Ubuntu chroot and pip install there (non-interactive)."
  # Build chroot script (makes sure path is correct)
  CHROOT_SCRIPT="/tmp/lombaohsint_chroot_install.sh"
  cat > "$CHROOT_SCRIPT" <<'EOCH'
set -euo pipefail
apt-get update -y
DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-venv python3-pip build-essential python3-dev libxml2-dev libxslt-dev libffi-dev libssl-dev zlib1g-dev libjpeg-dev pkg-config dos2unix
# try apt python3-lxml to avoid building
apt-get install -y python3-lxml || true
# create venv and install requirements (path substitution)
cd REPO_PATH
python3 -m venv venv || true
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install --prefer-binary -r requirements.txt || pip install -r requirements.txt
EOCH

  # replace REPO_PATH placeholder with actual repo path inside Termux
  sed -i "s|REPO_PATH|$BASE_DIR|g" "$CHROOT_SCRIPT"

  run_and_log "Running chroot script in Ubuntu (proot-distro login ubuntu -- ...)" proot-distro login ubuntu -- bash -lc "bash $CHROOT_SCRIPT"
}

# -----------------------
# MAIN FLOW
# -----------------------
info "Starting installation flow..."

prepare_repo_files

ensure_basic_system_packages || warn "Core system package step produced warnings."

# If Termux: offer chroot (recommended)
if [[ "$OS_TYPE" == "TERMUX" ]]; then
  info "Termux environment detected. Recommended action: install inside proot-distro (Ubuntu) for best compatibility."
  echo "Would you like to attempt automatic proot-distro Ubuntu install now? (recommended) (y/N)"
  read -r -p "> " choice
  if [[ "$choice" =~ ^[Yy]$ ]]; then
    termux_chroot_flow || warn "proot-distro flow had warnings/errors (check logs)."
  else
    warn "Skipping proot-distro flow. Will attempt native Termux installs (may fail for packages like lxml)."
    # still try native lxml deps, but warn user
    install_lxml_deps || warn "install_lxml_deps failed on Termux (see logs)."
    setup_python_and_requirements || warn "Python requirements step produced warnings."
  fi
else
  # Non-Termux: do everything in current system/venv
  setup_python_and_requirements || warn "Python setup or requirements installation produced warnings."
fi

# -----------------------
# Final summary
# -----------------------
echo ""
echo "==================== INSTALLATION SUMMARY ===================="
echo "Master log: $MASTER_LOG"
echo ""

if [[ ${#SUCCESS[@]} -gt 0 ]]; then
  echo "Succeeded steps:"
  for s in "${SUCCESS[@]}"; do
    IFS='::' read -r lab lf <<< "$s"
    printf "  ${GREEN}✓${NC} %s (log: %s)\n" "$lab" "$lf"
  done
  echo ""
fi

if [[ ${#ERRORS[@]} -gt 0 ]]; then
  echo -e "${RED}Some steps failed:${NC}"
  for e in "${ERRORS[@]}"; do
    IFS='::' read -r lab lf <<< "$e"
    printf "  ${RED}✗%s${NC} — log: %s\n" "$lab" "$lf"
  done
  echo ""
  echo "---- Last 40 lines of each error log (for quick debug) ----"
  for e in "${ERRORS[@]}"; do
    IFS='::' read -r lab lf <<< "$e"
    echo ""
    echo -e "${YELLOW}== $lab — tail of $lf ==${NC}"
    tail -n 40 "$lf" || true
  done
  echo ""
  echo -e "${YELLOW}Tip:${NC} If lxml fails, ensure libxml2-dev & libxslt-dev are installed (or use the proot-distro Ubuntu chroot on Termux)."
else
  echo -e "${GREEN}All major steps completed without fatal errors.${NC}"
fi

echo "=============================================================="
echo ""
echo -e "${CYAN}Next: open a NEW shell or run:${NC} source \"$BASE_DIR/venv/bin/activate\" && python3 \"$BASE_DIR/main.py\" --target test@example.com --level BLACK --i-am-authorized"
echo -e "${PURPLE}Use responsibly. Only scan with explicit authorization.${NC}"
