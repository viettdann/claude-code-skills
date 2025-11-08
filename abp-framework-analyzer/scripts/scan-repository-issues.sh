#!/bin/bash

# ABP Framework Repository & Data Access Issue Scanner
# Detects inefficient aggregate loading, N+1 queries, and DbContext violations

set -euo pipefail

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'
BOLD='\033[1m'

echo -e "${BOLD}ABP Framework - Repository & Data Access Scanner${NC}"
echo "=================================================="
echo ""

if ! command -v rg &> /dev/null; then
    echo -e "${RED}Error: ripgrep (rg) is not installed${NC}"
    exit 1
fi

SEARCH_DIR="${1:-.}"

if [ ! -d "$SEARCH_DIR" ]; then
    echo -e "${RED}Error: Directory '$SEARCH_DIR' not found${NC}"
    exit 1
fi

echo "Scanning directory: $SEARCH_DIR"
echo ""

HIGH_COUNT=0
MEDIUM_COUNT=0

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

        if [ "$severity" = "HIGH" ]; then
            HIGH_COUNT=$((HIGH_COUNT + count))
        else
            MEDIUM_COUNT=$((MEDIUM_COUNT + count))
        fi
    else
        echo -e "${GREEN}✓ No issues found${NC}"
        echo ""
    fi

    echo "---"
    echo ""
}

echo -e "${BOLD}Scanning for Repository Issues...${NC}"
echo ""

report_finding \
    "HIGH" \
    "Eager Loading Chains" \
    "Include\(.*\)\.Include" \
    "Multiple JOINs load unnecessary data, causes performance degradation"

report_finding \
    "HIGH" \
    "ThenInclude Usage" \
    "ThenInclude" \
    "Nested eager loading, may load too much data"

report_finding \
    "HIGH" \
    "Auto-Include All Relations" \
    "IncludeDetails.*=.*true" \
    "Loads all navigation properties, severe performance impact"

report_finding \
    "HIGH" \
    "Direct DbContext in Application Layer" \
    "private.*DbContext|_dbContext" \
    "Violates repository abstraction, breaks DDD layer separation"

report_finding \
    "MEDIUM" \
    "DbSet Direct Access" \
    "_dbContext\.Set<|\.Set<.*>\..*Async" \
    "Should use repository pattern, not direct DbSet access"

report_finding \
    "HIGH" \
    "ToList Before Filtering" \
    "\.ToList\(\)\.Where" \
    "Loads all records to memory before filtering, database should filter"

report_finding \
    "HIGH" \
    "ToList Before Projection" \
    "\.ToList\(\)\.Select" \
    "Loads all columns before projection, inefficient data transfer"

report_finding \
    "MEDIUM" \
    "Manual SaveChanges Calls" \
    "SaveChanges(Async)?\(" \
    "ABP handles auto-save via Unit of Work, manual calls unnecessary"

report_finding \
    "MEDIUM" \
    "Manual Transaction Management" \
    "BeginTransaction|CommitTransaction" \
    "ABP provides automatic transaction handling via UnitOfWork"

# Check for missing purpose-built repository methods
echo -e "${BOLD}[INFO] Checking for Purpose-Built Repository Methods${NC}"
echo ""

generic_gets=$(rg "GetAsync\(" "$SEARCH_DIR" --type cs -g "**/*Repository.cs" -c 2>/dev/null || echo "0")
custom_methods=$(rg "GetFor.*Async|GetBy.*Async" "$SEARCH_DIR" --type cs -g "**/*Repository.cs" -c 2>/dev/null || echo "0")

echo "Generic GetAsync calls: $generic_gets"
echo "Purpose-built methods: $custom_methods"
echo ""

if [ "$custom_methods" -lt "$((generic_gets / 2))" ]; then
    echo -e "${YELLOW}⚠ Consider adding purpose-built repository methods${NC}"
    echo "  Instead of: GetAsync(id) with Include"
    echo "  Use: GetForConfirmationAsync(id) - loads only needed data"
    echo ""
fi

echo "---"
echo ""

# Summary
echo -e "${BOLD}========================================${NC}"
echo -e "${BOLD}Scan Summary${NC}"
echo -e "${BOLD}========================================${NC}"
echo ""

if [ $HIGH_COUNT -eq 0 ] && [ $MEDIUM_COUNT -eq 0 ]; then
    echo -e "${GREEN}✓ No repository or data access violations found!${NC}"
else
    echo -e "${YELLOW}High Priority Issues: $HIGH_COUNT${NC}"
    echo -e "${BLUE}Medium Priority Issues: $MEDIUM_COUNT${NC}"
    echo ""
    echo -e "${BOLD}Recommendations:${NC}"
    echo "1. Replace eager loading with purpose-built repository methods"
    echo "2. Use database-level filtering (Where in query, not after ToList)"
    echo "3. Project to DTOs at database level (Select before ToList)"
    echo "4. Remove direct DbContext usage from application layer"
    echo "5. Let ABP handle transactions via UnitOfWork"
fi

echo ""
echo -e "${BOLD}Best Practices:${NC}"
echo "• Create GetForXAsync methods that load only required data"
echo "• Use IQueryable projections for read operations"
echo "• Avoid Include for simple operations (status updates, etc.)"
echo "• Repository pattern for writes, query projection for reads"
echo ""
echo "Documentation: https://abp.io/docs/latest/framework/architecture/best-practices"
