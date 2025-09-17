#!/bin/bash
# cleanup.sh — Lombaohsint Cleanup Script

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}[!] WARNING: This will delete all cache, logs, and reports.${NC}"
read -p "Are you sure? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Cancelled.${NC}"
    exit 1
fi

cd ~/Lombaohsint || { echo -e "${RED}[-] Directory not found.${NC}"; exit 1; }

echo -e "${YELLOW}[+] Deleting cache files...${NC}"
rm -rf data/cache/* 2>/dev/null

echo -e "${YELLOW}[+] Deleting log files...${NC}"
rm -rf data/logs/*.log 2>/dev/null

echo -e "${YELLOW}[+] Deleting report folders...${NC}"
rm -rf reports/* 2>/dev/null

echo -e "${GREEN}✓ Cleanup complete. All temporary files removed.${NC}"
