# Next.js Security Audit Skill

Comprehensive security vulnerability scanner and code quality analyzer for TypeScript/Next.js codebases.

## What It Does

This skill performs deep security analysis of Next.js applications, identifying:

- **Security Vulnerabilities**: SQL injection, XSS, command injection, hardcoded secrets, auth bypass
- **Next.js Best Practices**: Proper use of Server/Client Components, App Router patterns, metadata API
- **Code Quality**: Type safety, error handling, performance issues, dead code

## Installation

### Project-Level (Recommended for Teams)

```bash
# From your Next.js project root
mkdir -p .claude/skills
cp -r nextjs-security-audit .claude/skills/

# Commit to git for team sharing
git add .claude/skills/nextjs-security-audit
git commit -m "Add security audit skill"
```

### Personal (All Projects)

```bash
# Install globally for your user
mkdir -p ~/.claude/skills
cp -r nextjs-security-audit ~/.claude/skills/
```

## Usage

The skill activates automatically when you ask Claude Code to:

- "Audit this codebase for security vulnerabilities"
- "Check for security issues in my Next.js app"
- "Review code quality and best practices"
- "Scan for dangerous patterns"
- "Find hardcoded secrets"
- "Check if we're following Next.js App Router best practices"

### Examples

#### Full Security Audit
```
Audit my Next.js e-commerce app for security vulnerabilities
```

Claude will:
1. Explore your codebase structure
2. Identify framework version and patterns
3. Scan for critical security issues (SQL injection, XSS, etc.)
4. Check Next.js best practices
5. Review code quality
6. Generate prioritized report with fixes

#### Quick Scans
```
Quick scan - just check for hardcoded API keys and secrets
```

```
Check if we're properly using Server vs Client Components
```

```
Find all type safety issues - any types and unsafe assertions
```

#### Focused Analysis
```
Review authentication and authorization patterns for security issues
```

```
Check Server Actions for missing validation
```

## What Gets Checked

### Security (OWASP Top 10 Focused)

- ✅ SQL/NoSQL Injection
- ✅ Cross-Site Scripting (XSS)
- ✅ Command Injection
- ✅ Hardcoded Secrets & Credentials
- ✅ Broken Authentication/Authorization
- ✅ Insecure Deserialization
- ✅ Path Traversal
- ✅ CSRF in Server Actions
- ✅ Sensitive Data Exposure

### Next.js Specific

- ✅ Server vs Client Component boundaries
- ✅ Data fetching patterns (App Router)
- ✅ Server Actions security
- ✅ Metadata API usage
- ✅ Error boundaries
- ✅ Route handler vs Server Action usage
- ✅ Dynamic route validation

### Code Quality

- ✅ TypeScript safety (any types, assertions)
- ✅ Error handling coverage
- ✅ Memory leak patterns
- ✅ Performance anti-patterns
- ✅ Dead code detection

## Output Format

Each finding includes:

1. **Severity**: Critical/High/Medium/Low
2. **Location**: Exact file path and line number
3. **Problem**: Clear description of the issue
4. **Risk**: Impact if exploited
5. **Fix**: Code example showing secure implementation
6. **References**: OWASP/Next.js documentation links

### Example Output

```markdown
### [CRITICAL] SQL Injection in Search

**Location:** `app/api/search/route.ts:23`

**Problem:**
User input directly interpolated into SQL query without sanitization.

**Risk:**
Attacker can execute arbitrary SQL commands, potentially:
- Stealing all database data
- Deleting tables
- Bypassing authentication

**Fix:**
```typescript
// ❌ Before (vulnerable)
const results = await db.query(`SELECT * FROM products WHERE name LIKE '%${searchTerm}%'`);

// ✅ After (secure)
const results = await db.query(
  'SELECT * FROM products WHERE name LIKE $1',
  [`%${searchTerm}%`]
);
```

**References:**
- https://owasp.org/www-community/attacks/SQL_Injection
- https://www.prisma.io/docs/concepts/components/prisma-client/raw-database-access
```

## Severity Levels

- **Critical**: Immediate exploitation risk (SQL injection, exposed secrets, RCE)
- **High**: Significant security impact (XSS, auth bypass, data exposure)
- **Medium**: Security concern or poor practice (missing validation, weak error handling)
- **Low**: Code quality/maintainability (type safety, code style)

## Integration Tips

### CI/CD Pipeline

Add to `.github/workflows/security.yml`:

```yaml
name: Security Audit

on:
  pull_request:
    branches: [main]

jobs:
  security-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Security Audit
        run: |
          # Run Claude Code with security audit skill
          npx claude-code -m "Run security audit and report critical/high issues"

      - name: Fail on Critical Issues
        run: |
          if grep -q "CRITICAL" audit-report.md; then
            echo "Critical security issues found!"
            exit 1
          fi
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running security audit on changed files..."

CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(ts|tsx|js|jsx)$')

if [ -n "$CHANGED_FILES" ]; then
  claude-code -m "Quick security scan on: $CHANGED_FILES"
fi
```

### Regular Scans

Schedule weekly audits:

```bash
# .github/workflows/weekly-audit.yml
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM

jobs:
  full-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Full Security Audit
        run: npx claude-code skill nextjs-security-audit
      - name: Create Issue if Issues Found
        # Create GitHub issue with findings
```

## Recommended Complementary Tools

This skill works great alongside:

- **ESLint**: `@next/eslint-plugin`, `eslint-plugin-security`
- **Zod**: Runtime type validation
- **DOMPurify**: HTML sanitization
- **Helmet**: Security headers
- **npm audit**: Dependency vulnerability scanning

## Limitations

- Does not run automated exploit tests (use DAST tools for that)
- Cannot detect business logic flaws without context
- May have false positives (review all findings)
- Best used with human security review for critical apps

## Privacy & Security

This skill:
- ✅ Runs locally in Claude Code
- ✅ Does not send code to external services
- ✅ Only uses tools: Task, Grep, Glob, Read, Bash
- ✅ Never modifies code without permission

## Contributing

Found a security pattern we should check? Open an issue or PR with:

1. Description of the vulnerability pattern
2. Example vulnerable code
3. Example secure code
4. Grep/search pattern to detect it

## Support

- **Documentation**: See `reference.md` for vulnerability examples
- **Examples**: See `examples.md` for usage patterns
- **Issues**: [GitHub Issues](https://github.com/anthropics/claude-code/issues)

## License

MIT - Use freely in your projects

---

**⚠️ Important**: This skill provides automated scanning but does not replace:
- Manual security code review
- Penetration testing
- Security audit by professionals

For production applications handling sensitive data, always conduct professional security audits.
