import os
import subprocess
import sys
from utils.logger import logging

def fix_termux():
    """
    Fixes Termux environment to support heavy OSINT tools.
    Must be called only if running in Termux (detected via PREFIX).
    """
    if "com.termux" not in os.environ.get("PREFIX", ""):
        return

    log = logging.getLogger("lombaohsint")

    # Ensure required packages are installed
    required_pkgs = [
        "python", "git", "curl", "wget", "openssl-tool", "libffi", "clang", "make", "gcc",
        "proot-distro", "tor", "nmap", "hydra", "hashcat", "amass", "subfinder", "shodan-cli"
    ]

    for pkg in required_pkgs:
        try:
            result = subprocess.run(["pkg", "list-installed"], capture_output=True, text=True)
            if pkg not in result.stdout:
                log.info(f"Installing Termux package: {pkg}")
                subprocess.run(["pkg", "install", "-y", pkg], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            log.warning(f"Failed to install {pkg}: {e}")

    # Ensure Ubuntu chroot is installed and updated
    try:
        result = subprocess.run(["proot-distro", "list"], capture_output=True, text=True)
        if "ubuntu" not in result.stdout:
            log.info("Installing Ubuntu chroot...")
            subprocess.run(["proot-distro", "install", "ubuntu"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        log.info("Updating Ubuntu chroot...")
        subprocess.run([
            "proot-distro", "login", "ubuntu", "--", "sh", "-c",
            "apt update && apt upgrade -y && apt install python3 python3-pip git curl wget tor nmap hydra hashcat amass subfinder -y"
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        log.warning(f"Failed to setup Ubuntu chroot: {e}")

    # Create symlink to Android storage
    sdcard_path = "/storage/emulated/0"
    home_sdcard = os.path.expanduser("~/sdcard")
    if not os.path.islink(home_sdcard) and os.path.exists(sdcard_path):
        try:
            os.symlink(sdcard_path, home_sdcard)
            log.info(f"Symlink created: {home_sdcard} -> {sdcard_path}")
        except Exception as e:
            log.warning(f"Failed to create symlink: {e}")

    # Ensure pip3 uses correct path
    try:
        subprocess.run(["pip3", "install", "--upgrade", "pip"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

    log.info("Termux environment patched successfully.")
