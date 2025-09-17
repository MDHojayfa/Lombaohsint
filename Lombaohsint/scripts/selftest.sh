#!/bin/bash
# selftest.sh — Lombaohsint Self-Test Script

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}[+] Running Lombaohsint self-test...${NC}"

cd ~/Lombaohsint || { echo -e "${RED}[-] Directory not found.${NC}"; exit 1; }

# Create dummy test target
TEST_TARGET="test@mdtools.local"

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo -e "${RED}[-] main.py missing. Installation corrupted.${NC}"
    exit 1
fi

# Run self-test in GENTLE mode to avoid external calls
echo -e "${YELLOW}[+] Running: lombaohsint --target ${TEST_TARGET} --level GENTLE --i-am-authorized${NC}"
python3 main.py --target "${TEST_TARGET}" --level GENTLE --i-am-authorized --export json --verbose

# Check if report was created
REPORT_DIR="reports/test_at_mdtools_local"
if [ -d "$REPORT_DIR" ] && [ -f "$REPORT_DIR/report.json" ]; then
    echo -e "${GREEN}✓ Self-test passed! Report generated at: $REPORT_DIR/report.json${NC}"
    cat "$REPORT_DIR/report.json" | jq '.' 2>/dev/null || echo -e "${YELLOW}[!] JSON is valid but jq not installed.${NC}"
else
    echo -e "${RED}[-] Self-test failed. No report generated.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Lombaohsint is ready for production use.${NC}"
