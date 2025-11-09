# Next.js Kits - Standalone Scanners

Quick pattern-based scanners for Next.js projects. These scripts provide fast, automated analysis without AI overhead.

## Scripts Overview

| Script | Purpose | Output |
|--------|---------|--------|
| `scan-performance.py` | Performance anti-patterns | `performance-scan-results.json` |
| `scan-security.py` | Security vulnerabilities | `security-scan-results.json` |
| `scan-debug.py` | Common debug issues | `debug-scan-results.json` |
| `scan-api-status.py` | **API status codes & console.log** | JSON to stdout |
| `scan-all.py` | Run all scans | `nextjs-audit-report.json` + `.md` |

## Installation

No external dependencies required - uses Python 3.7+ standard library.

```bash
# Make scripts executable
chmod +x *.py
```

## Usage

### Run Individual Scans

**Performance Scan:**
```bash
python3 scan-performance.py [directory]

# Examples:
python3 scan-performance.py .              # Scan current directory
python3 scan-performance.py ../my-app      # Scan specific directory
```

Detects:
- Large library imports (moment.js, full lodash)
- Missing dynamic imports for heavy components
- Inline functions and objects in JSX
- Native `<img>` tags instead of `next/image`
- Missing image dimensions
- Fetch calls without cache configuration
- Missing Next.js config optimizations

**Security Scan:**
```bash
python3 scan-security.py [directory]
```

Detects:
- XSS vulnerabilities (dangerouslySetInnerHTML, unsanitized input)
- Missing input validation in Server Actions
- Missing authorization checks
- CSRF protection issues
- API route security problems
- Environment variable exposure
- SQL injection vulnerabilities
- Hardcoded secrets

**Debug Scan:**
```bash
python3 scan-debug.py [directory]
```

Detects:
- Hydration error causes (Date(), Math.random(), window checks)
- TypeScript anti-patterns (any, @ts-ignore)
- Client hooks in Server Components
- Browser APIs in Server Components
- Missing error handling
- Potential null reference errors

**API Status Codes Scan (Fast!):**
```bash
python3 scan-api-status.py [directory]

# Examples:
python3 scan-api-status.py . > api-issues.json    # Save to file
python3 scan-api-status.py ../my-app              # Scan specific directory
```

**Why this scan is special:**
- **Lightweight & Fast**: Pre-filters files before LLM analysis
- **Targets API routes only**: Focuses on routes returning JSON responses
- **Production-critical issues**: Catches developers hiding errors!

Detects:
- **200 OK with error messages** (anti-pattern!) - `{ error: "..." }` without proper HTTP status
- **Hidden error fields**: `err`, `issue`, `problem`, `failure`, `fault`, `exception`, `warning`
- **Sneaky message fields**: `message`, `msg`, `messages` (might be errors)
- **Boolean failure flags**: `success: false`, `ok: false`, `failed: true`, `isError: true`, `hasError: true`
- **Status strings**: `status: "error"` instead of HTTP 400/500
- **Contradictory responses**: `{ ok: true, error: "..." }` (really?!)
- **Nested errors**: `{ data: { error: "..." } }` (extra sneaky!)
- **Error arrays**: `{ errors: [...] }`, `{ validationErrors: [...] }`
- **Console.log in production**: All console methods (`log`, `error`, `warn`, `debug`, `trace`, etc.)
- **Debugger statements**: `debugger;`
- **Missing error status codes**: Catch blocks without 4xx/5xx status

**Output:** Outputs JSON to stdout with:
- List of files with issues
- Line numbers for each finding
- Severity classification (HIGH/MEDIUM/LOW)
- Summary statistics

**Usage in workflow:**
```bash
# Step 1: Fast scan to find problematic files
python3 scan-api-status.py . > api-findings.json

# Step 2: LLM validates only flagged files (much faster!)
# Claude Code reads api-findings.json and validates context
```

### Run Comprehensive Scan

**All Scans:**
```bash
python3 scan-all.py [directory]
```

Runs all three scanners and generates:
- `nextjs-audit-report.json` - JSON report with all findings
- `nextjs-audit-report.md` - Formatted markdown report

## Output Format

### JSON Output

Each scanner produces JSON with this structure:

```json
{
  "total_files_scanned": 42,
  "total_issues": 15,
  "severity_breakdown": {
    "Critical": 2,
    "High": 5,
    "Medium": 6,
    "Low": 2
  },
  "findings": [
    {
      "file": "app/components/Header.tsx",
      "line": 42,
      "code": "import moment from 'moment'",
      "title": "Bundle Size: Large Import",
      "problem": "Importing moment.js increases bundle size",
      "fix": "Use date-fns or dayjs instead",
      "severity": "Medium"
    }
  ]
}
```

### Console Output

```
============================================================
Performance Scan Complete
============================================================
Files Scanned: 42
Issues Found: 15

Severity Breakdown:
  Critical: 2
  High: 5
  Medium: 6
  Low: 2

Detailed results saved to: performance-scan-results.json
```

## Exit Codes

- `0` - Scan completed successfully, no issues found (or only low/medium issues)
- `1` - Issues found (performance/debug scans) OR critical issues found (security scan)

Use in CI/CD pipelines:

```bash
# Fail build on critical security issues
python3 scan-security.py . || exit 1

# Run all scans but don't fail build
python3 scan-all.py . || true
```

## Integration Examples

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running Next.js security scan..."
python3 scripts/scan-security.py .

if [ $? -eq 1 ]; then
  echo "❌ Critical security issues found!"
  echo "Fix issues or use 'git commit --no-verify' to bypass"
  exit 1
fi
```

### GitHub Actions

```yaml
name: Next.js Scan

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Run Next.js comprehensive scan
        run: |
          chmod +x scripts/*.py
          python3 scripts/scan-all.py .

      - name: Upload scan results
        uses: actions/upload-artifact@v3
        with:
          name: scan-results
          path: |
            nextjs-audit-report.json
            nextjs-audit-report.md
```

### NPM Scripts

Add to `package.json`:

```json
{
  "scripts": {
    "scan": "python3 scripts/scan-all.py .",
    "scan:perf": "python3 scripts/scan-performance.py .",
    "scan:security": "python3 scripts/scan-security.py .",
    "scan:debug": "python3 scripts/scan-debug.py .",
    "scan:api": "python3 scripts/scan-api-status.py .",
    "prescan": "python3 scripts/scan-api-status.py . > api-findings.json"
  }
}
```

Then run:

```bash
npm run scan           # Run all scans
npm run scan:perf      # Performance only
npm run scan:security  # Security only
npm run scan:debug     # Debug only
npm run scan:api       # API status codes (fast!)
npm run prescan        # Quick API pre-scan
```

## Limitations

These scanners use pattern matching and may have:

- **False positives**: Flagging legitimate code patterns
- **False negatives**: Missing complex vulnerabilities
- **Limited context**: No semantic code analysis

For comprehensive analysis, use Claude Code with the nextjs-kits skill which provides:
- Context-aware validation
- Framework version-specific checks
- Detailed remediation guidance
- Cross-file analysis

## Customization

### Adding Custom Patterns

Edit the scanner files to add your own patterns:

```python
# scan-performance.py

def _check_custom_pattern(self, file_path: Path, line_num: int, line: str):
    """Check for custom pattern"""
    if re.search(r'your-pattern-here', line):
        self._add_finding(
            file_path, line_num, line,
            'Custom: Issue Title',
            'Problem description',
            'Fix recommendation',
            'Medium'
        )
```

Then call it in `_scan_file_content()`:

```python
def _scan_file_content(self, file_path: Path, content: str):
    # ... existing checks ...
    self._check_custom_pattern(file_path, line_num, line)
```

### Adjusting Severity Levels

Modify the severity parameter in `_add_finding()` calls:

- `'Critical'` - Security vulnerabilities, broken functionality
- `'High'` - Significant issues, missing best practices
- `'Medium'` - Suboptimal patterns, performance issues
- `'Low'` - Style issues, minor optimizations

### Excluding Files/Directories

Add to `_should_skip()` method:

```python
def _should_skip(self, file_path: Path) -> bool:
    """Check if file should be skipped"""
    skip_dirs = {
        'node_modules', '.next', 'out', 'dist', 'build', '.git',
        'your-custom-dir'  # Add your exclusions
    }
    return any(skip_dir in file_path.parts for skip_dir in skip_dirs)
```

## Troubleshooting

**Script not executable:**
```bash
chmod +x scan-*.py
```

**Python not found:**
```bash
# Use python instead of python3
python scan-all.py .
```

**Permission denied:**
```bash
# Run with explicit python
python3 scan-all.py .
```

**JSON decode error:**
- Check that previous scans completed successfully
- Remove existing `*-results.json` files and re-run

## Support

For issues or feature requests related to these scripts:
1. Check the main skill README.md
2. Review the PATTERNS.md for detection logic
3. Consult REFERENCE.md for Next.js best practices

For AI-assisted analysis with better context understanding, use Claude Code with the nextjs-kits skill.
