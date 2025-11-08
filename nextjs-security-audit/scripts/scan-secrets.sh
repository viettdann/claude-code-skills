#!/bin/bash
# Scan for hardcoded secrets, API keys, and credentials
# Usage: ./scripts/scan-secrets.sh [directory]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATTERN_FILE="$SCRIPT_DIR/patterns/secrets.txt"
TARGET_DIR="${1:-.}"

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "🔍 Scanning for hardcoded secrets..."
echo "Target: $TARGET_DIR"
echo ""

# Check if ripgrep is available
if ! command -v rg &> /dev/null; then
    echo "Error: ripgrep (rg) is required but not installed."
    echo "Install: brew install ripgrep (macOS) or apt install ripgrep (Linux)"
    exit 1
fi

# Exclude common directories
EXCLUDES=(
    "node_modules"
    ".next"
    "dist"
    "build"
    ".git"
    "coverage"
    "*.min.js"
    "*.bundle.js"
)

EXCLUDE_ARGS=()
for exclude in "${EXCLUDES[@]}"; do
    EXCLUDE_ARGS+=(-g "!$exclude")
done

# Files to check
FILE_TYPES=(
    --type ts
    --type tsx
    --type js
    --type jsx
    --type json
    --type yaml
    --type env
)

# Run scan
FINDINGS=$(rg -i -n \
    "${FILE_TYPES[@]}" \
    "${EXCLUDE_ARGS[@]}" \
    -f "$PATTERN_FILE" \
    "$TARGET_DIR" \
    2>/dev/null || true)

if [ -z "$FINDINGS" ]; then
    echo -e "${GREEN}✓ No hardcoded secrets detected${NC}"
    exit 0
fi

# Parse and display findings
CRITICAL_COUNT=0
WARNING_COUNT=0

echo -e "${RED}⚠️  Potential hardcoded secrets found:${NC}"
echo ""

while IFS= read -r line; do
    # Extract file:line:match
    FILE=$(echo "$line" | cut -d: -f1)
    LINE_NUM=$(echo "$line" | cut -d: -f2)
    MATCH=$(echo "$line" | cut -d: -f3-)

    # Check severity
    IS_CRITICAL=false

    # Critical patterns (live keys, AWS keys)
    if echo "$MATCH" | grep -qE "sk_live_|AKIA[0-9A-Z]{16}|ghp_|gho_"; then
        IS_CRITICAL=true
        ((CRITICAL_COUNT++))
    else
        ((WARNING_COUNT++))
    fi

    # Display finding
    if [ "$IS_CRITICAL" = true ]; then
        echo -e "${RED}[CRITICAL]${NC} $FILE:$LINE_NUM"
    else
        echo -e "${YELLOW}[WARNING]${NC} $FILE:$LINE_NUM"
    fi

    # Show the match (truncate if too long)
    MATCH_DISPLAY=$(echo "$MATCH" | head -c 100)
    echo "  $MATCH_DISPLAY"
    echo ""
done <<< "$FINDINGS"

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Summary:"
echo -e "  ${RED}Critical: $CRITICAL_COUNT${NC}"
echo -e "  ${YELLOW}Warnings: $WARNING_COUNT${NC}"
echo ""

if [ $CRITICAL_COUNT -gt 0 ]; then
    echo -e "${RED}⚠️  CRITICAL: Found live API keys or credentials!${NC}"
    echo "Action required:"
    echo "  1. Remove secrets from code"
    echo "  2. Move to environment variables"
    echo "  3. Rotate exposed credentials"
    echo "  4. Check git history: git log -p -S 'secret_pattern'"
    exit 1
fi

exit 0
