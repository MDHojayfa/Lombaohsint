#!/bin/bash

# ███████╗███████╗██████╗ ██╗   ██╗██████╗ ███████╗
# ██╔════╝██╔════╝██╔══██╗██║   ██║██╔══██╗██╔════╝
# █████╗  █████╗  ██████╔╝██║   ██║██████╔╝█████╗  
# ██╔══╝  ██╔══╝  ██╔══██╗██║   ██║██╔══██╗██╔══╝  
# ██║     ███████╗██║  ██║╚██████╔╝██║  ██║███████╗
# ╚═╝     ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝
#            LOMBAOHSINT v2.0 BLACK EDITION
#          THE ONLY INSTALLER YOU WILL EVER NEED
#               By MDHojayfa | MDTOOLS

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
BLUE='\033[1;34m'
WHITE='\033[1;37m'
GRAY='\033[1;90m'
BOLD='\033[1m'
NC='\033[0m'

print_banner() {
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
}

log() { echo -e "${BLUE}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[-]${NC} $1"; exit 1; }
success() { echo -e "${GREEN}[✓]${NC} $1"; }

print_banner

# --- FIND THE REPO ROOT — NO MATTER WHERE YOU ARE ---
REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
while [[ "$REPO_ROOT" != "/" ]]; do
    if [[ -f "$REPO_ROOT/main.py" ]] && [[ -d "$REPO_ROOT/modules" ]] && [[ -f "$REPO_ROOT/config.yaml" ]]; then
        break
    fi
    REPO_ROOT=$(dirname "$REPO_ROOT")
done

if [[ ! -f "$REPO_ROOT/main.py" ]]; then
    error "Could not locate Lombaohsint repo. Make sure you cloned it and are running this from inside it."
fi

cd "$REPO_ROOT" || error "Failed to enter repo root: $REPO_ROOT"

log "REPO ROOT DETECTED: $REPO_ROOT"

# --- DETECT OS ---
if [ -n "$PREFIX" ] && [[ "$PREFIX" == *"/data/data/com.termux/files/usr"* ]]; then
    OS="TERMUX"
    log "DETECTED: ${YELLOW}Termux (Android)${NC}"
elif [ -f "/etc/os-release" ] && grep -q "Kali" /etc/os-release; then
    OS="KALI"
    log "DETECTED: ${RED}Kali Linux${NC}"
elif [ -f "/etc/os-release" ] && grep -q "Ubuntu" /etc/os-release; then
    OS="UBUNTU"
    log "DETECTED: ${CYAN}Ubuntu 22.04+${NC}"
elif [ -f "/etc/os-release" ] && grep -q "Debian" /etc/os-release; then
    OS="DEBIAN"
    log "DETECTED: ${CYAN}Debian 12+${NC}"
else
    error "Unsupported OS. This tool requires Kali, Ubuntu, Debian, or Termux."
fi

# --- FIX LINE ENDINGS (CRLF → LF) ---
log "FIXING LINE ENDINGS (CRLF → LF)..."
if ! command -v dos2unix &>/dev/null; then
    case $OS in
        TERMUX)
            pkg install dos2unix -y >/dev/null 2>&1
            ;;
        *)
            apt-get update -y >/dev/null 2>&1
            apt-get install dos2unix -y >/dev/null 2>&1
            ;;
    esac
fi
find . -type f \( -name "*.py" -o -name "*.sh" \) -exec dos2unix {} \; >/dev/null 2>&1

# --- CREATE VIRTUAL ENVIRONMENT INSIDE REPO ---
VENV_DIR="$REPO_ROOT/venv"
if [[ ! -d "$VENV_DIR" ]]; then
    log "CREATING PYTHON VIRTUAL ENVIRONMENT..."
    case $OS in
        TERMUX)
            # Termux has python3, but we use proot-distro for full Python
            if ! proot-distro list | grep -q "ubuntu"; then
                log "INSTALLING UBUNTU CHROOT..."
                proot-distro install ubuntu >/dev/null 2>&1
            fi
            proot-distro login ubuntu -- sh -c "apt update && apt install python3 python3-venv -y" >/dev/null 2>&1
            # We'll run the tool inside proot later
            ;;
        *)
            # Ubuntu/Kali/Debian
            if ! python3 -m venv --help >/dev/null 2>&1; then
                log "INSTALLING python3-venv..."
                apt-get install python3-venv -y >/dev/null 2>&1
            fi
            python3 -m venv "$VENV_DIR" || error "Failed to create virtual environment."
            ;;
    esac
fi

# --- INSTALL DEPENDENCIES ---
if [[ -d "$VENV_DIR" ]]; then
    log "INSTALLING PYTHON DEPENDENCIES..."
    case $OS in
        TERMUX)
            # In Termux, we use proot-distro to run the tool inside Ubuntu
            # We don't install pip here — we let Ubuntu do it
            ;;
        *)
            # Ubuntu/Kali/Debian
            source "$VENV_DIR/bin/activate" >/dev/null 2>&1
            pip install --upgrade pip >/dev/null 2>&1
            pip install -r requirements.txt --break-system-packages >/dev/null 2>&1
            deactivate >/dev/null 2>&1
            ;;
    esac
fi

# --- RUN THE TOOL — BASED ON OS ---
log "RUNNING LOMBAOHSINT..."

case $OS in
    TERMUX)
        # Run inside Ubuntu chroot — where pip and venv work properly
        log "LAUNCHING TOOL INSIDE UBUNTU CHROOT..."
        proot-distro login ubuntu -- sh -c "
            cd $REPO_ROOT &&
            source venv/bin/activate &&
            python3 main.py \"\$@\"
        " -- "$@"
        exit $?
        ;;

    KALI|UBUNTU|DEBIAN)
        # Run inside venv — no root needed
        source "$VENV_DIR/bin/activate" >/dev/null 2>&1
        python3 main.py "$@"
        exit $?
        ;;
esac
