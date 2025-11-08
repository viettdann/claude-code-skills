# Secret Scanner - Claude Code Skill

Comprehensive security scanner for detecting hardcoded secrets, API keys, tokens, and credentials in codebases. Optimized for **Next.js/Vite**, **.NET/ABP**, **Azure Services**, and **Docker** environments.

## Features

✅ **Multi-platform support**: Next.js, Vite, .NET, ABP, Azure, Docker
✅ **Comprehensive patterns**: 50+ secret detection patterns including Azure & Docker
✅ **Azure-specific**: SQL Database, Storage, DevOps PATs, Service Principal, Container Registry
✅ **Docker-specific**: Compose files, Dockerfiles, registry credentials, build secrets
✅ **Git history scanning**: Find secrets in commit history
✅ **False positive reduction**: Entropy analysis and placeholder detection
✅ **Actionable reports**: Markdown reports with remediation steps
✅ **Fast scanning**: Multiprocessing for large codebases
✅ **CI/CD ready**: Exit codes for pipeline integration

## Quick Start

### Installation

1. **Copy skill to Claude Code skills directory:**
   ```bash
   cp -r scanning-for-secrets ~/.claude/skills/
   # or for project-specific:
   cp -r scanning-for-secrets .claude/skills/
   ```

2. **Install dependencies:**
   ```bash
   pip install gitpython
   ```

### Usage

**Option 1: Use with Claude Code (recommended)**

Simply ask Claude:
- "Check my code for secrets"
- "Scan for API keys in this project"
- "Did I commit any .env files to git?"
- "Audit my Next.js app for exposed credentials"

**Option 2: Run standalone scripts**

```bash
# Full scan with all steps
./scan-secrets.sh

# Quick scan (skip git history)
./scan-secrets.sh --quick

# Only git history
./scan-secrets.sh --git-only

# Scan specific directory
./scan-secrets.sh /path/to/project
```

**Option 3: Run individual scripts**

```bash
# Scan files
python3 scripts/scan_files.py

# Validate findings
python3 scripts/validate_findings.py secret-scan-results.json

# Scan git history
python3 scripts/scan_git_history.py
```

## What It Detects

### Azure Services (NEW!)

- **Azure SQL Database**: Connection strings with `.database.windows.net` + passwords
- **Service Principal**: `AZURE_CLIENT_SECRET` / `ClientSecret` (34-40 chars)
- **Azure DevOps**: Personal Access Tokens (PATs), `SYSTEM_ACCESSTOKEN`
- **Storage Account**: Account keys (88-char Base64), connection strings
- **Cosmos DB**: Account endpoints with keys
- **Service Bus/Event Hub**: Shared access keys
- **Container Registry**: ACR passwords for Docker
- **Azure Functions**: Host keys, function keys
- **App Services**: Publishing passwords in `.pubxml` files
- **Application Insights**: Instrumentation keys

### Docker (NEW!)

- **Docker Hub**: Access tokens, registry passwords
- **Docker Compose**: Hardcoded secrets in `environment:` sections
- **Dockerfile**: `ARG`/`ENV` with secrets (visible in image history)
- **Docker Config**: `.docker/config.json` auth tokens
- **Harbor Registry**: Private registry credentials

### Next.js / Vite

- `NEXT_PUBLIC_*` / `VITE_*` vars with sensitive data (exposed to browser)
- NextAuth secrets (`NEXTAUTH_SECRET`)
- Vercel deployment tokens
- API keys in `next.config.js` or `vite.config.ts`
- Secrets in `.env.production`, `.env.local`

### .NET / ABP

- SQL Server connection strings with passwords
- IdentityServer client secrets
- JWT signing keys
- ABP license codes
- Redis passwords
- SMTP credentials

### Cloud & Generic

- AWS keys (Access Key ID, Secret Access Key)
- GCP API keys
- Private keys (RSA, EC, SSH)
- JWT tokens
- Database URLs with passwords (PostgreSQL, MySQL, MongoDB)
- GitHub/GitLab tokens
- Stripe, SendGrid, Twilio, Mailgun API keys
- NPM auth tokens

## Output Files

After scanning, you'll get:

```
project/
├── secret-scan-results.json       # Raw scan results
├── validated-findings.json        # Validated with false positive reduction
├── git-history-scan-results.json  # Git history findings
└── secret-scan-report.md          # Human-readable report
```

## Example Report

```markdown
# Secret Scanner Validation Report

## Summary
- **Total findings:** 12
- **Critical:** 2 (require immediate action)
- **High:** 3 (require action)
- **Medium:** 4 (review recommended)
- **Info:** 3 (likely false positives)

## 🚨 Critical Findings

### .env.production:15
- **Pattern:** AWS Access Key
- **Confidence:** HIGH
- **Value:** `AKIAIOSFODNN7ABC1234`
- **Recommendation:** Rotate immediately, remove from file

### appsettings.json:42
- **Pattern:** SQL Server Connection String
- **Confidence:** HIGH
- **Value:** `Server=prod;...;Password=RealP@ss`
- **Recommendation:** Move to User Secrets or Azure Key Vault
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Secret Scan
on: [push, pull_request]

jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: pip install gitpython
      - name: Scan for secrets
        run: |
          cd ${{ github.workspace }}
          ~/.claude/skills/scanning-for-secrets/scan-secrets.sh --quick
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

~/.claude/skills/scanning-for-secrets/scan-secrets.sh --quick

if [ $? -ne 0 ]; then
  echo "❌ Secret scan failed - commit blocked"
  exit 1
fi
```

## Configuration

### Customizing Patterns

Edit `scripts/scan_files.py` to add custom patterns:

```python
PATTERNS.append({
    "name": "My Custom API Key",
    "pattern": re.compile(r"MY_API_[A-Z0-9]{32}"),
    "severity": "HIGH",
    "context": [".env"],
})
```

### Excluding Directories

Add to `SKIP_DIRS` in `scripts/scan_files.py`:

```python
SKIP_DIRS = {
    "node_modules", ".git", "bin", "obj",
    "my_custom_dir",  # Add your directory
}
```

## Validation & False Positives

The validator (`validate_findings.py`) reduces false positives using:

1. **Entropy analysis**: Low entropy = likely placeholder
2. **Placeholder detection**: `YOUR_API_KEY`, `xxx`, `changeme`, etc.
3. **Format matching**: `<...>`, `{...}`, `${...}` patterns
4. **Known examples**: Filters official documentation examples
5. **Context awareness**: Comments, test files, example files

**Accuracy:**
- True positives: ~85-95%
- False negatives: <5%

## Performance

| Project Size | Files | Time |
|--------------|-------|------|
| Small (< 1k files) | 500 | 2-5s |
| Medium (1k-10k) | 5,000 | 10-30s |
| Large (> 10k) | 50,000 | 30-120s |

**Optimization features:**
- Multiprocessing (uses CPU count - 1)
- Binary file detection and skip
- Smart directory filtering
- Incremental git history scanning

## Remediation Guide

See [REFERENCE.md](REFERENCE.md) for detailed remediation steps.

### Quick Actions

**For Next.js:**
```bash
# Move secrets to .env.local (gitignored)
mv .env.production .env.local

# Add to .gitignore
echo ".env.local" >> .gitignore
echo ".env.production" >> .gitignore

# Rotate exposed keys
# (Update in Vercel dashboard or AWS console)
```

**For .NET:**
```bash
# Use User Secrets
cd MyProject.HttpApi.Host
dotnet user-secrets init
dotnet user-secrets set "ConnectionStrings:Default" "Server=..."

# For production: Azure Key Vault
# See REFERENCE.md for setup
```

**Remove from git history:**
```bash
# Install git-filter-repo
brew install git-filter-repo

# Remove file from all history
git filter-repo --path .env.production --invert-paths

# Force push (coordinate with team!)
git push origin --force --all
```

## Troubleshooting

### "gitpython not found"
```bash
pip install gitpython
```

### "Permission denied"
```bash
chmod +x scan-secrets.sh scripts/*.py
```

### "Too many false positives"
Review `PATTERNS.md` and adjust validation thresholds in `validate_findings.py`.

### "Scan too slow"
Exclude large directories or use `--quick` mode to skip git history.

## Files Structure

```
scanning-for-secrets/
├── SKILL.md              # Main skill file (Claude reads this)
├── README.md             # This file
├── PATTERNS.md           # Pattern definitions
├── REFERENCE.md          # Remediation guide
├── scan-secrets.sh       # Wrapper script
└── scripts/
    ├── scan_files.py         # File scanner
    ├── scan_git_history.py   # Git history scanner
    └── validate_findings.py  # Findings validator
```

## Contributing

To add new patterns:

1. Edit `scripts/scan_files.py` → `PATTERNS` list
2. Update `PATTERNS.md` with documentation
3. Test with: `python3 scripts/scan_files.py`

## Security Note

This tool detects **patterns** that look like secrets. It cannot:
- Determine if credentials are still active
- Detect obfuscated or encrypted secrets
- Scan runtime memory or logs
- Validate credentials with services

**Always assume detected secrets are compromised and rotate them.**

## License

This skill is provided as-is for security auditing purposes.

## Support

For issues or questions:
1. Check [REFERENCE.md](REFERENCE.md) for remediation help
2. Review [PATTERNS.md](PATTERNS.md) for pattern details
3. Open an issue in your project repository

---

**Version:** 1.0.0
**Last Updated:** 2025-01
**Frameworks:** Next.js 13+, Vite 4+, .NET 6+, ABP 7+
