# Troubleshooting Guide — Lombaohsint v2.0

## ❌ Problem: `install.sh` fails on Termux

### ✅ Fix:
```bash
pkg update -y
pkg install proot-distro -y
proot-distro install ubuntu
proot-distro login ubuntu -- sh -c "apt update && apt install python3-pip git curl wget -y"
