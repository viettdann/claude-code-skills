#!/bin/bash

# ABP Framework Async/Sync Issue Scanner
# Detects blocking async calls that can cause deadlocks

set -euo pipefail

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo -e "${BOLD}ABP Framework - Async/Sync Violation Scanner${NC}"
echo "=================================================="
echo ""

# Check if rg (ripgrep) is installed
if ! command -v rg &> /dev/null; then
    echo -e "${RED}Error: ripgrep (rg) is not installed${NC}"
    echo "Install: brew install ripgrep (macOS) or apt install ripgrep (Ubuntu)"
    exit 1
fi

# Determine search directory
SEARCH_DIR="${1:-.}"

if [ ! -d "$SEARCH_DIR" ]; then
    echo -e "${RED}Error: Directory '$SEARCH_DIR' not found${NC}"
    exit 1
fi

echo "Scanning directory: $SEARCH_DIR"
echo ""

# Initialize counters
CRITICAL_COUNT=0
HIGH_COUNT=0

# Function to report findings
report_finding() {
    local severity=$1
    local title=$2
    local pattern=$3
    local explanation=$4

    echo -e "${BOLD}[$severity] $title${NC}"
    echo "Pattern: $pattern"
    echo "Impact: $explanation"
    echo ""

    local results
    results=$(rg "$pattern" "$SEARCH_DIR" --type cs -n --heading --color=never 2>/dev/null || true)

    if [ -n "$results" ]; then
        echo "$results"
        echo ""

        local count
        count=$(echo "$results" | grep -c ":" || true)

        if [ "$severity" = "CRITICAL" ]; then
            CRITICAL_COUNT=$((CRITICAL_COUNT + count))
        else
            HIGH_COUNT=$((HIGH_COUNT + count))
        fi
    else
        echo -e "${GREEN}✓ No issues found${NC}"
        echo ""
    fi

    echo "---"
    echo ""
}

# Scan for async/sync violations
echo -e "${BOLD}Scanning for Critical Async/Sync Issues...${NC}"
echo ""

report_finding \
    "CRITICAL" \
    "Blocking .Wait() Call" \
    "\.Wait\(\)" \
    "Blocks thread, risks deadlock in ASP.NET Core"

report_finding \
    "CRITICAL" \
    "Blocking .Result Access" \
    "\.Result(?!\s*{)" \
    "Blocks thread, risks deadlock, violates async-first"

report_finding \
    "CRITICAL" \
    "Blocking GetAwaiter().GetResult()" \
    "\.GetAwaiter\(\)\.GetResult\(\)" \
    "Manual sync-over-async, causes thread pool starvation"

report_finding \
    "HIGH" \
    "Non-Async Application Service Methods" \
    "public void .*(AppService|DomainService)" \
    "Application/Domain services should be async-first (ABP 2.0+)"

report_finding \
    "HIGH" \
    "Task.Run Wrapping Async Code" \
    "Task\.Run\(.*await" \
    "Unnecessary thread pool usage, use direct await instead"

report_finding \
    "HIGH" \
    "Sync Repository Methods" \
    "I.*Repository.*\): void" \
    "Custom repository methods should return Task"

# Summary
echo ""
echo -e "${BOLD}========================================${NC}"
echo -e "${BOLD}Scan Summary${NC}"
echo -e "${BOLD}========================================${NC}"
echo ""

if [ $CRITICAL_COUNT -eq 0 ] && [ $HIGH_COUNT -eq 0 ]; then
    echo -e "${GREEN}✓ No async/sync violations found!${NC}"
else
    echo -e "${RED}Critical Issues: $CRITICAL_COUNT${NC}"
    echo -e "${YELLOW}High Priority Issues: $HIGH_COUNT${NC}"
    echo ""
    echo -e "${BOLD}Recommendation:${NC}"
    echo "Fix CRITICAL issues immediately - they can cause deadlocks in production"
    echo "Convert all application code to async-first pattern"
fi

echo ""
echo -e "${BOLD}Next Steps:${NC}"
echo "1. Convert blocking calls to async/await"
echo "2. Make all AppService methods return Task/Task<T>"
echo "3. Use async ABP repository methods (GetAsync, InsertAsync, etc.)"
echo "4. Test under load to verify deadlock resolution"
echo ""
echo "Documentation: https://abp.io/docs/latest/framework/architecture/best-practices"
