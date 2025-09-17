#!/bin/bash
# update.sh — Lombaohsint Update Script

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}[+] Updating Lombaohsint...${NC}"

cd ~/Lombaohsint || { echo -e "${RED}[-] Directory not found.${NC}"; exit 1; }

echo -e "${YELLOW}[+] Pulling latest changes from GitHub...${NC}"
git pull origin main || { echo -e "${RED}[-] Git pull failed.${NC}"; exit 1; }

echo -e "${YELLOW}[+] Installing updated Python dependencies...${NC}"
pip3 install -r requirements.txt --upgrade --break-system-packages || { echo -e "${RED}[-] pip install failed.${NC}"; exit 1; }

echo -e "${GREEN}✓ Update complete!${NC}"
echo -e "${YELLOW}Run 'lombaohsint --help' to see any new features.${NC}"
