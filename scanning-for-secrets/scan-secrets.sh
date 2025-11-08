#!/bin/bash
#
# Secret Scanner - Wrapper Script
# Runs the complete secret scanning workflow
#
# Usage:
#   ./scan-secrets.sh [directory]
#   ./scan-secrets.sh --quick [directory]      # Skip git history
#   ./scan-secrets.sh --git-only [directory]   # Only scan git history
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SCRIPTS_DIR="${SCRIPT_DIR}/scripts"

# Parse arguments
MODE="full"
TARGET_DIR="${PWD}"

while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            MODE="quick"
            shift
            ;;
        --git-only)
            MODE="git-only"
            shift
            ;;
        --help|-h)
            echo "Secret Scanner - Comprehensive security scanner for Next.js/Vite and .NET/ABP projects"
            echo ""
            echo "Usage:"
            echo "  $0 [options] [directory]"
            echo ""
            echo "Options:"
            echo "  --quick       Skip git history scan (faster)"
            echo "  --git-only    Only scan git history"
            echo "  --help, -h    Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Full scan of current directory"
            echo "  $0 /path/to/project   # Full scan of specified directory"
            echo "  $0 --quick            # Quick scan (no git history)"
            echo "  $0 --git-only         # Only check git history"
            exit 0
            ;;
        *)
            TARGET_DIR="$1"
            shift
            ;;
    esac
done

# Verify target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${RED}❌ Error: Directory $TARGET_DIR does not exist${NC}"
    exit 1
fi

# Convert to absolute path
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

echo -e "${BLUE}🔍 Secret Scanner${NC}"
echo -e "${BLUE}=================${NC}"
echo -e "Target: ${TARGET_DIR}"
echo -e "Mode: ${MODE}"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: python3 is required but not installed${NC}"
    exit 1
fi

# Check dependencies
echo -e "${BLUE}📦 Checking dependencies...${NC}"

# Check if gitpython is installed (only if git scan will be performed)
if [ "$MODE" = "full" ] || [ "$MODE" = "git-only" ]; then
    if ! python3 -c "import git" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  gitpython not installed${NC}"
        echo -e "Install with: ${GREEN}pip install gitpython${NC}"

        # Ask user if they want to continue without git scan
        read -p "Continue without git history scan? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            MODE="quick"
        else
            exit 1
        fi
    fi
fi

echo ""

# Step 1: Scan files (unless git-only mode)
if [ "$MODE" != "git-only" ]; then
    echo -e "${BLUE}📂 Step 1: Scanning files for secrets...${NC}"
    if python3 "${SCRIPTS_DIR}/scan_files.py" "$TARGET_DIR"; then
        echo -e "${GREEN}✅ File scan complete${NC}"
    else
        echo -e "${YELLOW}⚠️  File scan completed with warnings${NC}"
    fi
    echo ""
fi

# Step 2: Validate findings (unless git-only mode)
if [ "$MODE" != "git-only" ]; then
    SCAN_RESULTS="${TARGET_DIR}/secret-scan-results.json"

    if [ -f "$SCAN_RESULTS" ]; then
        echo -e "${BLUE}🔎 Step 2: Validating findings...${NC}"
        if python3 "${SCRIPTS_DIR}/validate_findings.py" "$SCAN_RESULTS"; then
            echo -e "${GREEN}✅ Validation complete${NC}"
        else
            echo -e "${YELLOW}⚠️  Validation completed with warnings${NC}"
        fi
        echo ""
    else
        echo -e "${YELLOW}⚠️  No scan results found, skipping validation${NC}"
        echo ""
    fi
fi

# Step 3: Scan git history (unless quick mode)
if [ "$MODE" = "full" ] || [ "$MODE" = "git-only" ]; then
    # Check if directory is a git repository
    if git -C "$TARGET_DIR" rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "${BLUE}📜 Step 3: Scanning git history...${NC}"
        if python3 "${SCRIPTS_DIR}/scan_git_history.py" "$TARGET_DIR"; then
            echo -e "${GREEN}✅ Git history scan complete${NC}"
        else
            echo -e "${YELLOW}⚠️  Git history scan completed with warnings${NC}"
        fi
        echo ""
    else
        echo -e "${YELLOW}⚠️  Not a git repository, skipping git history scan${NC}"
        echo ""
    fi
fi

# Final summary
echo -e "${BLUE}=================${NC}"
echo -e "${BLUE}📊 Scan Complete${NC}"
echo -e "${BLUE}=================${NC}"
echo ""

# Check for critical findings
CRITICAL_FOUND=0
VALIDATED_FILE="${TARGET_DIR}/validated-findings.json"
GIT_SCAN_FILE="${TARGET_DIR}/git-history-scan-results.json"
REPORT_FILE="${TARGET_DIR}/secret-scan-report.md"

# Check validated findings
if [ -f "$VALIDATED_FILE" ]; then
    CRITICAL_COUNT=$(python3 -c "
import json
with open('${VALIDATED_FILE}', 'r') as f:
    data = json.load(f)
    print(data.get('validation_summary', {}).get('critical', 0))
" 2>/dev/null || echo "0")

    if [ "$CRITICAL_COUNT" -gt 0 ]; then
        CRITICAL_FOUND=1
        echo -e "${RED}🚨 CRITICAL: Found ${CRITICAL_COUNT} critical secrets in current files!${NC}"
    fi
fi

# Check git history findings
if [ -f "$GIT_SCAN_FILE" ]; then
    GIT_CRITICAL=$(python3 -c "
import json
with open('${GIT_SCAN_FILE}', 'r') as f:
    data = json.load(f)
    print(data.get('summary', {}).get('severity_counts', {}).get('CRITICAL', 0))
" 2>/dev/null || echo "0")

    if [ "$GIT_CRITICAL" -gt 0 ]; then
        CRITICAL_FOUND=1
        echo -e "${RED}🚨 CRITICAL: Found ${GIT_CRITICAL} critical secrets in git history!${NC}"
    fi
fi

# Output file locations
echo ""
echo -e "${BLUE}📄 Output files:${NC}"

if [ -f "$REPORT_FILE" ]; then
    echo -e "   📝 Report: ${GREEN}secret-scan-report.md${NC}"
fi

if [ -f "$VALIDATED_FILE" ]; then
    echo -e "   📋 Validated findings: ${GREEN}validated-findings.json${NC}"
fi

if [ -f "$GIT_SCAN_FILE" ]; then
    echo -e "   📜 Git history: ${GREEN}git-history-scan-results.json${NC}"
fi

echo ""

# Recommendations
if [ $CRITICAL_FOUND -eq 1 ]; then
    echo -e "${RED}⚠️  IMMEDIATE ACTION REQUIRED:${NC}"
    echo -e "   1. ${YELLOW}Rotate all exposed credentials immediately${NC}"
    echo -e "   2. ${YELLOW}Remove secrets from codebase${NC}"
    echo -e "   3. ${YELLOW}Add sensitive files to .gitignore${NC}"
    echo -e "   4. ${YELLOW}Check access logs for unauthorized usage${NC}"
    echo -e "   5. ${YELLOW}If in git history, use git-filter-repo to remove${NC}"
    echo ""
    echo -e "See ${BLUE}REFERENCE.md${NC} for detailed remediation steps"
    echo ""
    exit 1
else
    echo -e "${GREEN}✅ No critical secrets detected${NC}"
    echo ""

    # Check for warnings
    if [ -f "$VALIDATED_FILE" ]; then
        HIGH_COUNT=$(python3 -c "
import json
with open('${VALIDATED_FILE}', 'r') as f:
    data = json.load(f)
    print(data.get('validation_summary', {}).get('high', 0))
" 2>/dev/null || echo "0")

        if [ "$HIGH_COUNT" -gt 0 ]; then
            echo -e "${YELLOW}⚠️  Found ${HIGH_COUNT} high-severity findings - review recommended${NC}"
            echo ""
        fi
    fi

    exit 0
fi
