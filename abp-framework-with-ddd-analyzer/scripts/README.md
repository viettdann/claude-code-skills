# ABP Framework Analyzer Scripts

Quick standalone scripts for pattern-based scanning of ABP Framework projects.

## Available Scripts

### 1. `scan-async-issues.sh`

**Purpose**: Detect async/sync violations (blocking calls, deadlock risks)

**What it finds:**
- `.Wait()` calls on Tasks
- `.Result` access on Tasks
- `.GetAwaiter().GetResult()` patterns
- Non-async application/domain service methods
- Sync repository methods

**Usage:**
```bash
bash scripts/scan-async-issues.sh [directory]

# Examples
bash scripts/scan-async-issues.sh .
bash scripts/scan-async-issues.sh ../my-abp-project
```

**Output:**
- Critical issues (deadlock risks)
- High priority issues (async-first violations)
- File paths and line numbers
- Issue counts by severity

---

### 2. `scan-repository-issues.sh`

**Purpose**: Detect inefficient data access patterns and repository violations

**What it finds:**
- Eager loading chains (Include().Include())
- Auto-include all relations
- Direct DbContext usage in application layer
- ToList before Where/Select
- Manual SaveChanges/transactions
- Missing purpose-built repository methods

**Usage:**
```bash
bash scripts/scan-repository-issues.sh [directory]

# Examples
bash scripts/scan-repository-issues.sh .
bash scripts/scan-repository-issues.sh src/Acme.BookStore.Application
```

**Output:**
- High priority performance issues
- Medium priority architectural violations
- Statistics on repository method patterns
- Best practice recommendations

---

## Requirements

Both scripts require **ripgrep** (`rg`):

**macOS:**
```bash
brew install ripgrep
```

**Ubuntu/Debian:**
```bash
apt install ripgrep
```

**Windows:**
```bash
choco install ripgrep
```

## Quick Start

Run all scans on current directory:
```bash
bash scripts/scan-async-issues.sh
bash scripts/scan-repository-issues.sh
```

## Understanding Results

### Severity Levels

- **CRITICAL**: Fix immediately (deadlocks, data corruption risks)
- **HIGH**: Fix before production (performance, architectural violations)
- **MEDIUM**: Address in next sprint (code quality, maintainability)
- **LOW**: Optional improvements

### Common False Positives

1. **Test Code**: Scripts may flag test methods - tests can use `.Result` safely
2. **Migration Code**: DbContext in migrations is acceptable
3. **Comments**: May match code in comments (manual verification needed)

### Filtering Results

To exclude directories:
```bash
# Exclude tests and migrations
rg "pattern" --type cs -g "!**/*Test*" -g "!**/*Migration*"
```

## Integration

### Pre-commit Hook
```bash
#!/bin/bash
echo "Running ABP code quality checks..."

if bash scripts/scan-async-issues.sh | grep -q "CRITICAL"; then
    echo "❌ Critical async/sync issues found. Commit blocked."
    exit 1
fi

echo "✅ Code quality checks passed"
```

### CI/CD Pipeline

**GitHub Actions:**
```yaml
- name: ABP Code Quality Scan
  run: |
    bash scripts/scan-async-issues.sh
    bash scripts/scan-repository-issues.sh
```

**Azure DevOps:**
```yaml
- script: |
    bash scripts/scan-async-issues.sh
    bash scripts/scan-repository-issues.sh
  displayName: 'ABP Code Quality Check'
```

## Limitations

- **Pattern-based**: May have false positives/negatives
- **Static analysis**: Cannot detect runtime issues
- **C# only**: Doesn't analyze UI code
- **No context**: Cannot understand business logic reasoning

For comprehensive analysis, use the full ABP Framework Analyzer skill with AI-powered context understanding.

## Example Output

```
ABP Framework - Async/Sync Violation Scanner
==================================================

Scanning directory: .

[CRITICAL] Blocking .Wait() Call
Pattern: \.Wait\(\)
Impact: Blocks thread, risks deadlock in ASP.NET Core

src/Acme.BookStore.Application/Books/BookAppService.cs
45:    var book = _repository.GetAsync(id).Wait();
67:    _cache.SetAsync(key, value).Wait();

---

[CRITICAL] Blocking .Result Access
Pattern: \.Result(?!\s*{)
Impact: Blocks thread, risks deadlock, violates async-first

src/Acme.BookStore.Application/Orders/OrderAppService.cs
23:    var order = _orderRepository.GetAsync(orderId).Result;

---

========================================
Scan Summary
========================================

Critical Issues: 3
High Priority Issues: 0

Recommendation:
Fix CRITICAL issues immediately - they can cause deadlocks in production
Convert all application code to async-first pattern
```

## Adding Custom Patterns

To add new patterns to scripts:

1. Copy existing `report_finding` call
2. Update pattern, title, and explanation
3. Choose appropriate severity level
4. Test with sample code

Example:
```bash
report_finding \
    "HIGH" \
    "Your Issue Title" \
    "your-regex-pattern" \
    "Why this is problematic"
```

## Support

For issues or feature requests:
- Check [PATTERNS.md](../PATTERNS.md) for grep pattern reference
- Review [README.md](../README.md) for full skill documentation
- Consult [ABP Documentation](https://abp.io/docs)
