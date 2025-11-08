#!/bin/bash
# Scan Next.js Server Actions for missing authentication and validation
# Usage: ./scripts/scan-server-actions.sh [directory]

set -e

TARGET_DIR="${1:-app}"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "🔍 Scanning Server Actions for security issues..."
echo "Target: $TARGET_DIR"
echo ""

if ! command -v rg &> /dev/null; then
    echo "Error: ripgrep (rg) required"
    exit 1
fi

# Find all files with 'use server'
SERVER_ACTION_FILES=$(rg -l "'use server'|\"use server\"" "$TARGET_DIR" 2>/dev/null || true)

if [ -z "$SERVER_ACTION_FILES" ]; then
    echo -e "${GREEN}✓ No Server Actions found${NC}"
    exit 0
fi

ISSUES_FOUND=0
FILES_CHECKED=0

while IFS= read -r file; do
    ((FILES_CHECKED++))

    # Read file content
    CONTENT=$(cat "$file")

    # Check for authentication
    HAS_AUTH=false
    if echo "$CONTENT" | grep -qE "getServerSession|auth\(\)|getSession|currentUser|requireAuth"; then
        HAS_AUTH=true
    fi

    # Check for validation
    HAS_VALIDATION=false
    if echo "$CONTENT" | grep -qE "\.parse\(|\.safeParse\(|schema\.|validate\(|z\."; then
        HAS_VALIDATION=true
    fi

    # Extract exported async functions (likely Server Actions)
    ACTIONS=$(grep -nE "export\s+(async\s+)?function\s+\w+" "$file" || true)

    if [ -z "$ACTIONS" ]; then
        continue
    fi

    # Report issues
    if [ "$HAS_AUTH" = false ]; then
        echo -e "${RED}[CRITICAL] Missing authentication:${NC} $file"
        echo "  No auth check found (getServerSession, auth(), etc.)"
        echo ""
        ((ISSUES_FOUND++))
    fi

    if [ "$HAS_VALIDATION" = false ]; then
        echo -e "${YELLOW}[HIGH] Missing input validation:${NC} $file"
        echo "  No validation found (Zod, schema.parse, etc.)"
        echo ""
        ((ISSUES_FOUND++))
    fi

    # Check for direct database operations without validation
    if echo "$CONTENT" | grep -qE "db\.|prisma\.|await.*\.(create|update|delete)\("; then
        if [ "$HAS_VALIDATION" = false ]; then
            echo -e "${YELLOW}[HIGH] Database operation without validation:${NC} $file"
            echo "  Direct DB operations found without input validation"
            echo ""
        fi
    fi

done <<< "$SERVER_ACTION_FILES"

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Summary:"
echo "  Files checked: $FILES_CHECKED"
echo "  Issues found: $ISSUES_FOUND"
echo ""

if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✓ All Server Actions look secure${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Found $ISSUES_FOUND security issues${NC}"
    echo ""
    echo "Recommended fixes:"
    echo "  1. Add authentication checks at start of each action"
    echo "  2. Use Zod or similar for input validation"
    echo "  3. Validate user permissions before mutations"
    echo ""
    echo "Example secure Server Action:"
    echo ""
    echo "  'use server'"
    echo "  import { getServerSession } from 'next-auth';"
    echo "  import { z } from 'zod';"
    echo ""
    echo "  const Schema = z.object({ name: z.string() });"
    echo ""
    echo "  export async function updateName(formData: FormData) {"
    echo "    // 1. Auth check"
    echo "    const session = await getServerSession();"
    echo "    if (!session) throw new Error('Unauthorized');"
    echo ""
    echo "    // 2. Validation"
    echo "    const data = Schema.parse({ name: formData.get('name') });"
    echo ""
    echo "    // 3. Safe operation"
    echo "    await db.user.update({ where: { id: session.user.id }, data });"
    echo "  }"
    exit 1
fi
