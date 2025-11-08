---
name: scanning-for-secrets
description: Scans codebase and git history for hardcoded secrets, API keys, tokens, and credentials in Next.js/Vite, .NET/ABP, Azure services, and Docker environments. Detects Azure SQL, Storage, DevOps PATs, Service Principal secrets, Docker registry credentials, and more. Use when auditing code security, checking for exposed secrets, reviewing environment files, or before commits/deployments.
---

# Secret Scanner Skill

Comprehensive security scanner for detecting hardcoded secrets in:
- **Frontend:** Next.js, Vite (client-exposed secrets)
- **.NET:** ABP Framework, Web API, Azure App Services
- **Azure:** SQL Database, Storage, Service Bus, Container Registry, DevOps PATs, Key Vault
- **Docker:** Compose files, Dockerfiles, registry credentials, Harbor

## Quick Start

When invoked, this skill:
1. Scans current files for secrets (environment files, config, source code)
2. Validates findings to reduce false positives
3. Checks git history for accidentally committed secrets
4. Generates actionable security report

## Detection Workflow

### Step 1: Quick File Scan

Run the file scanner to identify potential secrets in current codebase:

```bash
python3 scripts/scan_files.py
```

**What it scans:**
- **Frontend (Next.js/Vite):**
  - `.env`, `.env.local`, `.env.production`, `.env.development`
  - `next.config.js`, `next.config.mjs`
  - `vite.config.js`, `vite.config.ts`
  - `.vercel/` deployment configs
  - `public/` directory for exposed keys

- **.NET/ABP:**
  - `appsettings.json`, `appsettings.*.json`
  - `appsettings.secrets.json`
  - `*.csproj` (for embedded secrets)
  - `*.pubxml` (publish profiles)
  - `*.config` (Web.config, App.config)
  - ABP module configurations

- **Azure:**
  - `azure-pipelines.yml` (DevOps pipelines)
  - `local.settings.json` (Azure Functions)
  - `azuredeploy.parameters.json` (ARM templates)
  - `*.publishsettings` (App Service publish profiles)
  - `.azure/` configuration files

- **Docker:**
  - `Dockerfile`, `Dockerfile.*`
  - `docker-compose.yml`, `docker-compose.*.yml`
  - `.dockerconfigjson`
  - `.docker/config.json`

- **Common:**
  - CI/CD configs (`.github/workflows/`, `.gitlab-ci.yml`)
  - Package managers (`package.json`, `*.csproj`)

**Output:** JSON file with all matches including file paths, line numbers, pattern types.

### Step 2: Validate Findings

Reduce false positives by analyzing detected patterns:

```bash
python3 scripts/validate_findings.py
```

**Validation checks:**
- Detects placeholder patterns (`YOUR_API_KEY_HERE`, `xxx`, `example`, `changeme`)
- Identifies format placeholders (`<YOUR_...>`, `{API_KEY}`, `${...}`)
- Filters test/development/example credentials
- Assigns severity levels (CRITICAL/WARNING/INFO)
- Checks entropy and randomness of values

**Output:** Categorized findings with risk assessment.

### Step 3: Git History Scan

Check if secrets were committed to git history:

```bash
python3 scripts/scan_git_history.py
```

**What it checks:**
- All environment files ever committed
- Deleted but still in history secrets
- Configuration files across all branches
- Commit metadata (author, date, message)

**Output:** Historical findings with commit details for remediation.

### Step 4: Generate Report

Create comprehensive markdown report with:
- Executive summary (total files scanned, secrets found)
- Critical findings requiring immediate action
- Warnings for suspicious patterns
- Remediation recommendations per finding type
- Git history issues with commit hashes

## Usage Examples

**Scenario 1: Pre-commit security check**
```
User: "Check my code for secrets before I commit"
Claude: Runs full scan workflow, reports findings with severity
```

**Scenario 2: Environment file audit**
```
User: "Did I accidentally commit my .env file?"
Claude: Runs git history scan, checks for .env in commits
```

**Scenario 3: Next.js deployment review**
```
User: "Audit my Next.js app for exposed API keys"
Claude: Scans .env files, next.config.js, public/ directory
```

**Scenario 4: .NET API security review**
```
User: "Check my ABP application for hardcoded credentials"
Claude: Scans appsettings.json, connection strings, module configs
```

**Scenario 5: Full security audit**
```
User: "Run complete security scan for secrets"
Claude: Executes all steps, generates comprehensive report
```

## Detection Patterns by Platform

### Azure Services Detection

**Azure SQL Database:**
- Connection strings with `.database.windows.net` + passwords
- Exposed in `appsettings.json`, `.env`, `azure-pipelines.yml`

**Azure Service Principal:**
- `AZURE_CLIENT_SECRET` / `ClientSecret` (34-40 characters)
- Used for Azure AD authentication
- Critical if exposed in CI/CD or config files

**Azure DevOps:**
- Personal Access Tokens (PATs) - 52 character tokens
- `SYSTEM_ACCESSTOKEN` in pipeline YAML
- Full access to Azure DevOps resources

**Azure Storage:**
- Storage Account Keys (88 character Base64)
- Connection strings with `AccountKey=`
- Blob, Queue, Table, File service access

**Azure Service Bus / Event Hub:**
- Connection strings with `SharedAccessKey=`
- Messaging and event streaming credentials

**Azure Container Registry:**
- ACR passwords for docker registry
- `ACR_PASSWORD` in docker-compose or pipelines

**Azure Functions:**
- Host keys (52+ characters)
- Function-level API keys
- Found in `local.settings.json` (should never commit)

**Azure Application Insights:**
- Instrumentation keys (UUID format)
- Telemetry data access

**Azure Key Vault:**
- Hardcoded secret versions in URLs
- Should use versionless references

### Docker Environment Detection

**Docker Hub / Registry:**
- Docker Hub access tokens (UUID format)
- `DOCKER_PASSWORD` / `REGISTRY_PASSWORD`
- Registry authentication credentials

**Docker Compose:**
- Hardcoded secrets in `environment:` sections
- Should use `.env` file or docker secrets instead
- Passwords, API keys, tokens in YAML

**Dockerfile:**
- `ARG` with secrets (visible in image history)
- `ENV` with secrets (visible in `docker inspect`)
- Should use build secrets or runtime injection

**Docker Config:**
- `.docker/config.json` with Base64 auth tokens
- Stored docker login credentials

**Harbor Registry:**
- Private registry passwords
- Alternative to Docker Hub

### Next.js / Vite Detection

**Environment variable exposure:**
- `NEXT_PUBLIC_*` keys with sensitive values (should only contain public data)
- `VITE_*` keys exposed to client bundle
- Server-side only vars accidentally prefixed with public markers

**Configuration secrets:**
- API keys in `next.config.js` exported to client
- OAuth secrets in config files
- Database URLs in public configs

**Build artifacts:**
- `.next/` directory with embedded secrets
- `dist/` or `build/` with exposed env vars
- Source maps leaking sensitive values

### .NET / ABP Detection

**Connection strings:**
- SQL Server credentials in `appsettings.json`
- Redis connection strings with passwords
- MongoDB credentials
- ABP multi-tenancy connection strings

**Authentication secrets:**
- JWT signing keys
- IdentityServer client secrets
- ABP encryption keys
- Cookie authentication keys

**External service credentials:**
- Azure Storage connection strings
- AWS credentials in config
- Email service API keys (SendGrid, Mailgun)
- Payment gateway secrets (Stripe, PayPal)

**ABP-specific:**
- `AbpLicenseCode` values (should use User Secrets)
- Tenant-specific secrets in multi-tenant configs
- Module settings with embedded credentials

## Pattern Categories

See [PATTERNS.md](PATTERNS.md) for detailed pattern definitions.

**High-severity patterns:**
- AWS access keys (`AKIA[0-9A-Z]{16}`)
- Private keys (RSA, EC, OpenSSH)
- JWT tokens with real signatures
- Database connection strings with credentials
- OAuth client secrets

**Medium-severity patterns:**
- Generic API keys (20+ character alphanumeric)
- Authentication tokens
- Password variables with values
- Slack/Discord webhooks
- GitHub personal access tokens

**Low-severity patterns:**
- Commented-out credentials (may indicate real values nearby)
- Environment variable references without values
- Configuration placeholders

## Validation Logic

**Placeholder indicators:**
- Terms: `example`, `your`, `xxx`, `test`, `sample`, `placeholder`, `changeme`, `todo`, `replace`
- Patterns: `<...>`, `{...}`, `${...}`, `[...]`, `***`, `...`
- Obvious fakes: `123456`, `password`, `secret`, `abcdef`, `000000`

**Real secret indicators:**
- High entropy (randomness)
- Base64 encoded values
- UUID/GUID format
- Cryptographic key formats
- Domain-specific patterns (AWS, Azure, etc.)

## Remediation Recommendations

**For Azure Services:**
1. Use Azure Key Vault for all secrets
2. Enable Managed Identity (no credentials needed)
3. Use Azure App Service Application Settings (not in code)
4. Azure DevOps: Use Variable Groups with Key Vault integration
5. Rotate exposed Storage Keys, SQL passwords, Service Principal secrets
6. Azure Functions: Never commit `local.settings.json`

**For Docker:**
1. Use `.env` files (gitignored) with docker-compose
2. Use Docker Secrets for Swarm mode
3. Use BuildKit `--mount=type=secret` for build-time secrets
4. Never use `ARG`/`ENV` for secrets (visible in image)
5. Rotate Docker Hub tokens and registry passwords
6. Multi-stage builds to keep secrets out of final image

**For Next.js/Vite:**
1. Move secrets to `.env.local` (gitignored by default)
2. Use `NEXT_PUBLIC_` prefix ONLY for truly public values
3. Never commit `.env.production` with real credentials
4. Use platform environment variables (Vercel, Netlify)
5. Implement secret rotation for exposed keys

**For .NET/ABP:**
1. Use User Secrets for development (`dotnet user-secrets`)
2. Use Azure Key Vault or AWS Secrets Manager for production
3. Enable Secret Manager in `.csproj`
4. Use environment-specific config transforms
5. Implement ABP `ISettingEncryptionService` for sensitive settings

**General:**
1. Add exposed files to `.gitignore` immediately
2. Rotate all exposed credentials
3. Use git-filter-repo to remove from history (if already committed)
4. Enable pre-commit hooks for secret scanning
5. Implement secrets management solution

## Error Handling

Scripts gracefully handle:
- Non-git directories (skip history scan)
- Missing Python dependencies (clear install instructions)
- Binary files (automatically skipped)
- Large repositories (progress indicators)
- Concurrent file access (thread-safe operations)

## Dependencies

**Required:**
- Python 3.7+
- `gitpython` (for git history scanning)

**Install:**
```bash
pip install gitpython
```

**Standard library (no install needed):**
- `re`, `os`, `pathlib`, `json`, `multiprocessing`, `hashlib`, `base64`

## Performance

**Optimization features:**
- Multiprocessing for parallel file scanning
- Smart file filtering (skip node_modules, bin, obj, .git)
- Binary file detection and skip
- Incremental git history scanning
- Lazy loading of large files

**Typical performance:**
- Small project (< 1000 files): 2-5 seconds
- Medium project (1000-10000 files): 10-30 seconds
- Large project (> 10000 files): 30-120 seconds

## False Positive Reduction

**Techniques applied:**
1. Entropy analysis (low entropy = likely placeholder)
2. Pattern matching against known placeholders
3. Context awareness (comments, documentation files)
4. Format validation (UUID structure, Base64 validity)
5. Cross-reference with common example values

**Expected accuracy:**
- True positives: ~85-95% of flagged secrets are real
- False negatives: <5% of real secrets missed
- Info-level findings: Reviewed but low confidence

## Report Format

Generated reports include:

```markdown
# Secret Scanner Report
Generated: [timestamp]
Repository: [repo name]
Branch: [current branch]

## Executive Summary
- Total files scanned: X
- Potential secrets found: Y
- Critical findings: Z (require immediate action)
- Warnings: W (review recommended)

## Critical Findings

### [File path:line number]
- **Pattern:** [type of secret]
- **Severity:** CRITICAL
- **Value:** [partially redacted]
- **Recommendation:** [specific remediation]

## Git History Issues

### Commit [hash]
- **File:** [path]
- **Date:** [commit date]
- **Author:** [author]
- **Findings:** [secrets found]
- **Action:** Rewrite history or rotate credentials

## Remediation Checklist
- [ ] Rotate exposed credentials
- [ ] Add files to .gitignore
- [ ] Remove from git history (if committed)
- [ ] Update documentation
- [ ] Implement secrets manager
```

## Integration with CI/CD

Can be integrated into:
- **GitHub Actions:** Pre-commit and PR checks
- **GitLab CI:** Pipeline security stage
- **Azure Pipelines:** Build validation
- **Pre-commit hooks:** Local developer checks

Example pre-commit hook:
```bash
#!/bin/bash
python3 .claude/skills/scanning-for-secrets/scripts/scan_files.py
if [ $? -ne 0 ]; then
  echo "❌ Secret scan failed - commit blocked"
  exit 1
fi
```

## Skill Execution Flow

When this skill is activated:

1. **Understand request context:**
   - Determine scan scope (full, partial, specific files)
   - Identify project type (Next.js, Vite, .NET, ABP)

2. **Execute file scan:**
   - Run `scan_files.py` with appropriate filters
   - Parse JSON output

3. **Validate findings:**
   - Run `validate_findings.py` on results
   - Categorize by severity

4. **Check git history (if applicable):**
   - Run `scan_git_history.py` if repository detected
   - Cross-reference with current findings

5. **Generate report:**
   - Create markdown summary
   - Highlight critical issues first
   - Provide actionable remediation steps

6. **Present results:**
   - Show executive summary
   - Detail critical findings
   - Offer next steps

## Limitations

**Known limitations:**
- Cannot detect secrets in compiled binaries
- May miss obfuscated or encrypted secrets
- Requires file system access (cannot scan remote repos without clone)
- Git history scan limited to local clone depth
- Cannot validate if credentials are currently active

**Not covered:**
- Runtime secret exposure (memory dumps, logs)
- Network traffic analysis
- Database content scanning
- Third-party service audits

## Support & Troubleshooting

**Common issues:**

1. **"gitpython not found"**
   - Solution: `pip install gitpython`

2. **"Permission denied on .git"**
   - Solution: Ensure read permissions on repository

3. **"Too many false positives"**
   - Solution: Review PATTERNS.md, adjust validation thresholds

4. **"Scan too slow"**
   - Solution: Exclude large directories (node_modules, bin, obj)

## Reference Documentation

- [PATTERNS.md](PATTERNS.md) - Complete pattern definitions and regex
- [REFERENCE.md](REFERENCE.md) - Secret types, severity matrix, remediation guide

## Version

**Skill version:** 1.0.0
**Last updated:** 2025-01
**Supported frameworks:** Next.js 13+, Vite 4+, .NET 6+, ABP 7+
