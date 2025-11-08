# Example Usage & Test Cases

This document provides example usage scenarios and test cases for the Secret Scanner skill.

## Example 1: Next.js Project with Exposed Keys

### Scenario
A Next.js project accidentally exposed API keys in `.env.production` file.

**File: `.env.production`**
```bash
# Database
DATABASE_URL=postgresql://user:RealP@ssw0rd123@prod-server:5432/mydb

# NextAuth
NEXTAUTH_SECRET=super-secret-key-for-production-use-only-2024

# Stripe (DANGER: Exposed to client!)
NEXT_PUBLIC_STRIPE_KEY=pk_live_51Abc123Def456Ghi789Jkl012

# AWS
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

### Expected Detection

```
🚨 CRITICAL Findings:
- DATABASE_URL: Postgres connection with password
- NEXTAUTH_SECRET: NextAuth secret key
- AWS_ACCESS_KEY_ID: AWS access key
- AWS_SECRET_ACCESS_KEY: AWS secret key

⚠️ HIGH Findings:
- NEXT_PUBLIC_STRIPE_KEY: Should be public test key, not secret
```

### Remediation

```bash
# 1. Move to .env.local (gitignored)
mv .env.production .env.local

# 2. Rotate all credentials
# - Generate new NextAuth secret
# - Rotate AWS keys in IAM console
# - Create new Stripe keys
# - Change database password

# 3. Update .env.production with placeholders
cat > .env.production << EOF
DATABASE_URL=YOUR_DATABASE_URL_HERE
NEXTAUTH_SECRET=YOUR_NEXTAUTH_SECRET_HERE
NEXT_PUBLIC_STRIPE_KEY=pk_test_YOUR_KEY_HERE
EOF

# 4. Add to .gitignore
echo ".env.local" >> .gitignore
```

---

## Example 2: .NET/ABP Project with appsettings.json

### Scenario
ABP Framework project with secrets in `appsettings.json`.

**File: `appsettings.json`**
```json
{
  "ConnectionStrings": {
    "Default": "Server=prod-sql;Database=MyApp;User ID=sa;Password=MyP@ssw0rd123;"
  },
  "Redis": {
    "Configuration": "localhost:6379,password=MyRedisPass123"
  },
  "Jwt": {
    "Secret": "ThisIsMyJwtSigningKeyForProduction2024",
    "Issuer": "MyApp",
    "Audience": "MyApp"
  },
  "AbpLicenseCode": "ABC123-DEF456-GHI789-JKL012-MNO345",
  "Email": {
    "Smtp": {
      "Host": "smtp.gmail.com",
      "Port": 587,
      "UserName": "myapp@gmail.com",
      "Password": "myEmailP@ssw0rd"
    }
  }
}
```

### Expected Detection

```
🚨 CRITICAL Findings:
- ConnectionStrings.Default: SQL Server connection with password
- Jwt.Secret: JWT signing key
- Email.Smtp.Password: SMTP credentials

⚠️ HIGH Findings:
- Redis.Configuration: Redis password

📋 MEDIUM Findings:
- AbpLicenseCode: Should be in User Secrets
```

### Remediation

```bash
# 1. Use User Secrets for development
cd MyProject.HttpApi.Host
dotnet user-secrets init

# 2. Move secrets to User Secrets
dotnet user-secrets set "ConnectionStrings:Default" "Server=...;Password=..."
dotnet user-secrets set "Redis:Configuration" "localhost:6379,password=..."
dotnet user-secrets set "Jwt:Secret" "..."
dotnet user-secrets set "AbpLicenseCode" "..."
dotnet user-secrets set "Email:Smtp:Password" "..."

# 3. Update appsettings.json with placeholders
# Remove all sensitive values

# 4. For production, use Azure Key Vault
# See REFERENCE.md for setup
```

---

## Example 3: Vite Project with Client-Exposed Secrets

### Scenario
Vite app exposes backend API secret to browser.

**File: `.env`**
```bash
# ❌ DANGER: All VITE_ prefixed vars are exposed to browser!
VITE_API_URL=https://api.myapp.com
VITE_API_SECRET_KEY=sk_live_abc123def456ghi789  # EXPOSED!

# ✅ OK: Not prefixed, server-only
DATABASE_URL=postgresql://user:pass@localhost/db
API_SECRET=my-backend-secret
```

**File: `vite.config.ts`**
```typescript
// ❌ DANGER: This secret is bundled into client code!
export default defineConfig({
  define: {
    'API_SECRET': JSON.stringify('sk_live_abc123def456')
  }
});
```

### Expected Detection

```
🚨 HIGH Findings:
- VITE_API_SECRET_KEY: Exposed to browser (VITE_ prefix)
- vite.config.ts define.API_SECRET: Bundled into client

⚠️ Info:
- VITE_API_URL: OK (public URL)
```

### Remediation

```bash
# 1. Remove VITE_ prefix from secrets
# .env.local (gitignored)
API_URL=https://api.myapp.com  # Public, can be VITE_ prefixed
API_SECRET_KEY=sk_live_abc123def456ghi789  # Server-only!

# 2. Use server-side environment variables
# Access in server code only, never in client components

# 3. Remove define from vite.config.ts
# Use runtime config instead

# 4. Rotate exposed API key
```

---

## Example 4: Git History Exposure

### Scenario
Developer accidentally committed `.env` file, then removed it.

**Git History:**
```bash
commit abc123 (main)
  Remove .env file

commit def456
  Add environment configuration
  + .env (with real secrets!)
```

### Detection

```bash
# Run git history scan
./scan-secrets.sh

# Output:
🚨 CRITICAL: Found secrets in git history!
   Commit: def456
   File: .env
   Secrets: 3 (AWS keys, database password)
```

### Remediation

```bash
# 1. Rotate all exposed credentials immediately
# (Even though file was removed, it's still in history)

# 2. Remove from git history
brew install git-filter-repo
git filter-repo --path .env --invert-paths

# 3. Force push (coordinate with team!)
git push origin --force --all
git push origin --force --tags

# 4. Team must re-clone repository
# Old clones still have secrets in history!
```

---

## Example 5: False Positives (Placeholders)

### Scenario
Documentation with example values.

**File: `.env.example`**
```bash
# Example configuration - replace with your values
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
API_KEY=YOUR_API_KEY_HERE
STRIPE_SECRET=sk_test_YOUR_STRIPE_KEY
AWS_ACCESS_KEY=<YOUR_AWS_ACCESS_KEY>
```

### Expected Detection

```
📋 INFO (Likely False Positives):
- DATABASE_URL: Placeholder pattern detected ("password")
- API_KEY: Placeholder text ("YOUR_API_KEY_HERE")
- STRIPE_SECRET: Placeholder text ("YOUR_STRIPE_KEY")
- AWS_ACCESS_KEY: Format placeholder ("<...>")
```

**Validation Result:**
```json
{
  "confidence": "LOW",
  "is_placeholder": true,
  "is_example": true,
  "updated_severity": "INFO"
}
```

---

## Example 6: CI/CD Pipeline Integration

### GitHub Actions Workflow

**File: `.github/workflows/security.yml`**
```yaml
name: Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for git scan

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install gitpython

      - name: Run secret scanner
        run: |
          chmod +x .claude/skills/scanning-for-secrets/scan-secrets.sh
          .claude/skills/scanning-for-secrets/scan-secrets.sh --quick

      - name: Upload scan results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: secret-scan-results
          path: |
            secret-scan-report.md
            validated-findings.json
```

**Expected Behavior:**
- ✅ Pass: No critical secrets found
- ❌ Fail: Critical secrets detected (blocks PR merge)

---

## Example 7: Pre-Commit Hook

### Setup

**File: `.git/hooks/pre-commit`**
```bash
#!/bin/bash

echo "🔍 Running secret scanner..."

# Run quick scan (no git history for speed)
.claude/skills/scanning-for-secrets/scan-secrets.sh --quick

if [ $? -ne 0 ]; then
  echo ""
  echo "❌ Secret scan detected issues!"
  echo "❌ Commit blocked for security."
  echo ""
  echo "To bypass (NOT recommended):"
  echo "  git commit --no-verify"
  exit 1
fi

echo "✅ No secrets detected"
exit 0
```

**Make executable:**
```bash
chmod +x .git/hooks/pre-commit
```

**Usage:**
```bash
# Try to commit with secrets
git add .env.production  # Contains real secrets
git commit -m "Update config"

# Output:
🔍 Running secret scanner...
🚨 CRITICAL: Found 3 critical secrets!
❌ Secret scan detected issues!
❌ Commit blocked for security.

# Fix issues
rm .env.production
git commit -m "Update config"

# Output:
🔍 Running secret scanner...
✅ No secrets detected
[main abc123] Update config
```

---

## Testing the Skill

### Test 1: Create Test Files

```bash
# Create test directory
mkdir test-scan
cd test-scan

# Create .env with fake AWS keys (for testing)
cat > .env << 'EOF'
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
DATABASE_URL=postgresql://user:password123@localhost/db
EOF

# Run scanner
python3 ../scanning-for-secrets/scripts/scan_files.py .

# Check results
cat secret-scan-results.json
```

### Test 2: Validate Placeholders

```bash
# Create .env.example with placeholders
cat > .env.example << 'EOF'
DATABASE_URL=YOUR_DATABASE_URL_HERE
API_KEY=<YOUR_API_KEY>
STRIPE_SECRET=sk_test_XXXXXXXXXXXXXXXX
EOF

# Run scanner
python3 ../scanning-for-secrets/scripts/scan_files.py .

# Validate findings
python3 ../scanning-for-secrets/scripts/validate_findings.py secret-scan-results.json

# Check that examples are marked as INFO
cat validated-findings.json | grep -A5 '"severity": "INFO"'
```

### Test 3: Performance Test

```bash
# Test on large codebase
time ./scanning-for-secrets/scan-secrets.sh /path/to/large/project

# Expected:
# Small project: 2-5 seconds
# Medium project: 10-30 seconds
```

---

## Common Patterns & Solutions

### Pattern 1: Stripe Keys in Frontend

**Problem:**
```typescript
// ❌ Bad: Secret key exposed
const stripe = new Stripe('sk_live_abc123...');
```

**Solution:**
```typescript
// ✅ Good: Use public key in frontend
const stripe = loadStripe('pk_live_abc123...');

// Backend only (API route)
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);
```

### Pattern 2: Database URLs in Docker Compose

**Problem:**
```yaml
# ❌ Bad: docker-compose.yml
version: '3'
services:
  db:
    environment:
      POSTGRES_PASSWORD: MyRealP@ssw0rd123
```

**Solution:**
```yaml
# ✅ Good: Use .env file
version: '3'
services:
  db:
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}

# .env (gitignored)
POSTGRES_PASSWORD=MyRealP@ssw0rd123
```

### Pattern 3: JWT Secrets in Code

**Problem:**
```csharp
// ❌ Bad: Hardcoded secret
var key = Encoding.ASCII.GetBytes("my-super-secret-jwt-key");
```

**Solution:**
```csharp
// ✅ Good: From configuration
var key = Encoding.ASCII.GetBytes(configuration["Jwt:Secret"]);

// User Secrets
dotnet user-secrets set "Jwt:Secret" "..."
```

---

## Skill Activation Examples

When using with Claude Code, the skill auto-activates on queries like:

1. **"Check my code for secrets"**
   → Full scan + report

2. **"Scan for API keys"**
   → Quick file scan focusing on API key patterns

3. **"Did I commit .env to git?"**
   → Git history scan for .env files

4. **"Audit my Next.js app security"**
   → Next.js-focused scan (NEXT_PUBLIC_ vars, etc.)

5. **"Check appsettings.json for credentials"**
   → .NET-focused scan (connection strings, etc.)

---

**Document Version:** 1.0.0
**Last Updated:** 2025-01
