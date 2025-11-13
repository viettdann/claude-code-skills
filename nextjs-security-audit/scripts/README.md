# Security Scan Scripts

Standalone security scanning tools that work independently or alongside the Claude Code skill.

## Quick Start

```bash
# Run all scans
./scripts/scan-all.py

# Or run individual scans
./scripts/scan-secrets.sh
./scripts/scan-server-actions.sh
./scripts/scan-type-safety.py
./scripts/scan-quick.py
```

## Prerequisites

- **ripgrep** (rg): `brew install ripgrep` or `apt install ripgrep`
- **Python 3.6+**: For Python scripts
- **Bash**: For shell scripts

## Individual Scanners

### 1. Secrets Scanner (`scan-secrets.sh`)

Finds hardcoded API keys, passwords, and credentials.

```bash
# Scan current directory
./scripts/scan-secrets.sh

# Scan specific directory
./scripts/scan-secrets.sh /path/to/project

# Example output:
# [CRITICAL] app/api/stripe/route.ts:8
#   const API_KEY = 'sk_live_abc123xyz...';
```

**What it finds:**
- Stripe keys (sk_live_, sk_test_)
- AWS credentials (AKIA...)
- GitHub tokens (ghp_, gho_)
- OpenAI keys (sk-...)
- Generic API keys and passwords
- Database connection strings with credentials

**Exit codes:**
- `0`: No secrets found
- `1`: Critical secrets detected

---

### 2. Server Actions Scanner (`scan-server-actions.sh`)

Checks Next.js Server Actions for missing auth and validation.

```bash
# Scan app directory (default)
./scripts/scan-server-actions.sh

# Scan custom directory
./scripts/scan-server-actions.sh src/app

# Example output:
# [CRITICAL] Missing authentication: app/actions/users.ts
#   No auth check found (getServerSession, auth(), etc.)
#
# [HIGH] Missing input validation: app/actions/users.ts
#   No validation found (Zod, schema.parse, etc.)
```

**What it checks:**
- ✅ Authentication (getServerSession, auth(), etc.)
- ✅ Input validation (Zod, schema.parse, etc.)
- ✅ Database operations without validation

**Exit codes:**
- `0`: All Server Actions secure
- `1`: Issues found

---

### 3. Type Safety Scanner (`scan-type-safety.py`)

Finds TypeScript type safety violations.

```bash
# Basic scan
./scripts/scan-type-safety.py

# Scan with custom threshold
./scripts/scan-type-safety.py --threshold 5

# JSON output
./scripts/scan-type-safety.py --json

# Example output:
# 'any' Type Usage (23 occurrences):
#
#   lib/api.ts
#     [CRITICAL] Line 45: export function fetchData(): Promise<any>
#     [HIGH] Line 67: const data: any = JSON.parse(response)
```

**What it finds:**
- `any` types (with severity levels)
- Non-null assertions (`!.`)
- `@ts-ignore` usage
- `@ts-expect-error` (informational)

**Options:**
- `--threshold N`: Fail if 'any' count exceeds N (default: 10)
- `--json`: Output structured JSON

**Exit codes:**
- `0`: Type safety OK or threshold not exceeded
- `1`: Threshold exceeded

---

### 4. All-in-One Scanner (`scan-all.py`)

Orchestrates all scans and provides unified report.

```bash
# Run everything
./scripts/scan-all.py

# JSON output
./scripts/scan-all.py --json

# Scan specific directory
./scripts/scan-all.py /path/to/project

# Example output:
# 🔒 Security Scan Suite
# Target: .
# Time: 2025-01-15 10:30:00
# ==========================================================
#
# ▶ Running Secrets Scanner...
# ▶ Running Server Actions...
# ▶ Running Type Safety...
#
# ==========================================================
# 📊 SCAN RESULTS
# ==========================================================
# ✓ Secrets Scanner: PASSED
# ✗ Server Actions: ISSUES FOUND
# ✓ Type Safety: PASSED
#
# SUMMARY
# Scans run: 3
# Critical issues: 1
```

**Exit codes:**
- `0`: All scans passed
- `1`: Issues found

---

## Pattern Files

Located in `patterns/` directory:

- `secrets.txt` - Hardcoded credential patterns
- `sql-injection.txt` - SQL injection patterns
- `xss.txt` - Cross-site scripting patterns
- `command-injection.txt` - Command injection patterns
- `type-safety.txt` - TypeScript issues

You can use these directly with ripgrep:

```bash
# Find all secrets
rg -i -n -f scripts/patterns/secrets.txt

# Find SQL injection patterns
rg -f scripts/patterns/sql-injection.txt --type ts

# Find XSS vulnerabilities
rg -f scripts/patterns/xss.txt --type tsx
```

## Git Hooks Integration

### Pre-commit Hook

Prevent committing secrets:

```bash
#!/bin/bash
# .git/hooks/pre-commit

STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(ts|tsx|js|jsx)$')

if [ -n "$STAGED_FILES" ]; then
  echo "🔍 Scanning staged files for secrets..."

  for file in $STAGED_FILES; do
    if rg -q -f .claude/skills/nextjs-security-audit/scripts/patterns/secrets.txt "$file"; then
      echo "❌ Possible secret detected in: $file"
      echo "Run: ./scripts/scan-secrets.sh"
      exit 1
    fi
  done
fi

exit 0
```

### Pre-push Hook

Run full security scan:

```bash
#!/bin/bash
# .git/hooks/pre-push

echo "🔒 Running security scans before push..."

./.claude/skills/nextjs-security-audit/scripts/scan-all.py

if [ $? -ne 0 ]; then
  echo ""
  echo "❌ Security issues found. Fix before pushing."
  echo "Override with: git push --no-verify"
  exit 1
fi

exit 0
```

## NPM Scripts Integration

Add to `package.json`:

```json
{
  "scripts": {
    "security:scan": "./scripts/scan-all.py",
    "security:quick": "./scripts/scan-quick.py",
    "security:secrets": "./scripts/scan-secrets.sh",
    "security:actions": "./scripts/scan-server-actions.sh",
    "security:types": "./scripts/scan-type-safety.py"
  }
}
```

Usage:

```bash
npm run security:scan
npm run security:secrets
```

## Output Formats

### Text Output (Default)

Human-readable with colors and severity markers:

```
[CRITICAL] app/api/auth.ts:23
  const SECRET = 'sk_live_abc123';

[HIGH] app/actions.ts:45
  Missing authentication
```

### JSON Output

Machine-readable for integration:

```json
{
  "timestamp": "2025-01-15T10:30:00",
  "summary": {
    "critical": 2,
    "high": 5,
    "medium": 12,
    "total_issues": 19
  },
  "findings": [
    {
      "severity": "critical",
      "file": "app/api/auth.ts",
      "line": 23,
      "category": "hardcoded_secret",
      "match": "sk_live_abc123"
    }
  ]
}
```

## False Positives

### Expected Patterns

Some patterns are OK:

```typescript
// ✅ OK - Type definition
interface Config {
  apiKey: string;
}

// ✅ OK - Environment variable
const key = process.env.API_KEY;

// ✅ OK - Comment
// Example: const SECRET = 'sk_test_...';

// ❌ REAL ISSUE
const SECRET = 'sk_live_abc123';
```

### Excluding False Positives

Create `.securityignore` file:

```
# Ignore example files
**/*.example.ts
**/*.test.ts

# Ignore specific patterns
**/mocks/**
```

Then modify scripts to respect it (add to scan scripts):

```bash
EXCLUDE_ARGS+=(-g '!**/*.example.ts' -g '!**/*.test.ts')
```

## Customizing Patterns

### Add Custom Pattern

Edit pattern files in `patterns/`:

```bash
# Add to patterns/secrets.txt
my_custom_api_key_\w{32}

# Test it
rg -f scripts/patterns/secrets.txt
```

### Create Custom Severity Rules

Edit `lib/severity.json`:

```json
{
  "critical": {
    "patterns": ["sk_live_", "production_db_password"]
  }
}
```

## Performance

Scan times (typical Next.js app):

| Scanner | Files | Time |
|---------|-------|------|
| Secrets | 500 | ~2s |
| Server Actions | 50 | ~1s |
| Type Safety | 500 | ~5s |
| **Total** | - | **~8s** |

For large codebases (5000+ files), consider:

1. Scan only changed files in git hooks
2. Cache results between runs
3. Run in parallel (scripts already do this in `scan-all.py`)

## Troubleshooting

### "ripgrep not found"

```bash
# macOS
brew install ripgrep

# Ubuntu/Debian
sudo apt install ripgrep

# Fedora
sudo dnf install ripgrep
```

### "Permission denied"

```bash
chmod +x scripts/*.sh scripts/*.py
```

### Scripts not finding patterns

Ensure you're in the project root or provide full path:

```bash
# From project root
./scripts/scan-all.py

# Or specify full path
/path/to/.claude/skills/nextjs-security-audit/scripts/scan-all.py
```

## Advanced Usage

### Scan Only Changed Files

```bash
# Git diff
CHANGED_FILES=$(git diff --name-only HEAD | grep -E '\.(ts|tsx)$')

for file in $CHANGED_FILES; do
  rg -f scripts/patterns/secrets.txt "$file"
done
```

### Custom Reporting

Parse JSON output:

```bash
./scripts/scan-all.py --json | jq '.summary'

# Output:
# {
#   "critical": 2,
#   "high": 5,
#   "total_issues": 7
# }
```

### Fail Build on Critical

```bash
./scripts/scan-all.py --json > scan.json

CRITICAL=$(jq '.summary.critical' scan.json)

if [ "$CRITICAL" -gt 0 ]; then
  echo "Build failed: Critical security issues"
  exit 1
fi
```

## Contributing

To add a new scanner:

1. Create script in `scripts/`
2. Add patterns to `patterns/`
3. Update `scan-all.py` to include it
4. Document usage above

## License

MIT - Use freely in your projects

---

## Additional Quick-Scan Commands (Heuristics)

These commands can be run with ripgrep to pre-flag potential issues. Always confirm by reading code in context. Exclude node_modules and generated code; respect .gitignore.

1) SSRF
```bash
rg -n --no-ignore --hidden -g '!node_modules/**' -e "fetch\(.*(req\.query|req\.body|params|searchParams|URLSearchParams)\.(get|\[)" -e "axios\.(get|post|put|delete)\(.*(req\.query|req\.body|params|searchParams)" -e "new URL\(.*(req\.query|req\.body|params|searchParams)" .
```

2) Path traversal & unsafe file access
```bash
rg -n --no-ignore --hidden -g '!node_modules/**' -e "fs\.(readFile|createReadStream|writeFile|unlink|readdir)\(" -e "path\.(join|resolve)\(" -e "(multer|busboy|formidable|FormData)" .
```

3) Open redirect
```bash
rg -n --no-ignore --hidden -g '!node_modules/**' -e "redirect\(.*(searchParams|get|query|body)" -e "NextResponse\.redirect\(" -e "res\.redirect\(" .
```

4) CORS misconfiguration
```bash
rg -n --no-ignore --hidden -g '!node_modules/**' -e "Access-Control-Allow-Origin\s*:\s*\*" -e "NextResponse\.(json|redirect|rewrite).*headers" -e "new Response\(.*headers" -e "cors\(" .
```

5) Security headers & CSP
```bash
rg -n --no-ignore --hidden -g '!node_modules/**' -e "Content-Security-Policy|X-Frame-Options|X-Content-Type-Options|Referrer-Policy|Strict-Transport-Security|Permissions-Policy" -e "headers\(\)" -e "next\.config\.js" .
```

6) Cookie & session flags (NextAuth/custom)
```bash
rg -n --no-ignore --hidden -g '!node_modules/**' -e "cookies\(|setCookie|NextResponse\.cookies" -e "next-auth" -e "getServerSession|getSession" .
```

7) Webhook signature verification
```bash
rg -n --no-ignore --hidden -g '!node_modules/**' -e "Stripe-Signature|svix|x-hub-signature|x-github-event" -e "stripe\(" -e "@stripe/stripe-node|@stripe/stripe-js" -e "crypto\.createHmac|verifySignature|verifyWebhook" .
```

8) Exposed environment variables in client code
```bash
rg -n --no-ignore --hidden -g '!node_modules/**' -e "process\.env\.NEXT_PUBLIC_.*(KEY|SECRET|TOKEN|PASSWORD)" -e "'use client'[\s\S]*process\.env\." -e "publicRuntimeConfig|serverRuntimeConfig" .
```

9) Logging sensitive data
```bash
rg -n --no-ignore --hidden -g '!node_modules/**' -e "console\.log\(.*(token|password|secret|api[_-]?key|authorization|cookie|set-cookie|bearer)" -e "logger\.(info|debug)\(.*(token|secret|password)" .
```

10) Rate limiting presence on mutation endpoints
```bash
rg -n --no-ignore --hidden -g '!node_modules/**' -e "ratelimit|rateLimit|Upstash|Bottleneck|express-rate-limit" -e "export async function (POST|PUT|DELETE)" app/**/route\.(ts|js|tsx)
```

11) Privacy-aware caching & revalidation
```bash
rg -n --no-ignore --hidden -g '!node_modules/**' -e "fetch\(.*\{[\s\S]*cache:\s*'force-cache'|next:\s*\{[\s\S]*revalidate:" -e "cookies\(\)|headers\(\)" .
```

12) next/image remote domains
```bash
rg -n --no-ignore --hidden -g '!node_modules/**' -e "next/image" -e "images:\s*\{[\s\S]*domains:" next.config.js
```
