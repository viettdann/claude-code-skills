# Secret Scanner Reference Guide

Complete reference for secret types, severity levels, and remediation strategies for Next.js/Vite and .NET/ABP projects.

---

## Table of Contents

1. [Secret Types by Framework](#secret-types-by-framework)
2. [Severity Matrix](#severity-matrix)
3. [Remediation Strategies](#remediation-strategies)
4. [Prevention Best Practices](#prevention-best-practices)
5. [Incident Response](#incident-response)
6. [Tools & Services](#tools--services)

---

## Secret Types by Framework

### Next.js Secrets

| Secret Type | Storage Location | Severity | Exposure Risk |
|-------------|------------------|----------|---------------|
| `NEXTAUTH_SECRET` | `.env.local` | CRITICAL | Session hijacking if exposed |
| `NEXT_PUBLIC_*` API keys | Any `.env` | HIGH | Always exposed to browser |
| Database URLs | `.env.local` | CRITICAL | Full database access |
| OAuth client secrets | `.env.local` | CRITICAL | Account takeover |
| Vercel tokens | `.vercel/` | CRITICAL | Deployment takeover |
| API route secrets | `.env.local` | HIGH | Backend API bypass |

**Common mistakes:**
- Using `NEXT_PUBLIC_` for secrets (always exposed to client)
- Committing `.env.production` with real credentials
- Hardcoding secrets in `next.config.js` (bundled into app)
- Storing secrets in `public/` directory (publicly accessible)

### Vite Secrets

| Secret Type | Storage Location | Severity | Exposure Risk |
|-------------|------------------|----------|---------------|
| `VITE_*` variables | `.env` | HIGH | Exposed to browser if prefixed |
| Backend API keys | `.env.local` | CRITICAL | API abuse |
| Build-time secrets | `vite.config.ts` | HIGH | Bundled into output |
| SSR secrets | `.env` (server-only) | CRITICAL | Server compromise |

**Common mistakes:**
- Prefixing sensitive vars with `VITE_` (auto-exposed)
- Storing secrets in `import.meta.env` without prefix check
- Committing `.env` instead of `.env.local`
- Using `define` in config for secret injection

### .NET / ABP Secrets

| Secret Type | Storage Location | Severity | Exposure Risk |
|-------------|------------------|----------|---------------|
| Connection strings | `appsettings.json` | CRITICAL | Database access |
| JWT signing keys | `appsettings.json` | CRITICAL | Token forgery |
| IdentityServer secrets | `appsettings.json` | CRITICAL | Authentication bypass |
| ABP license codes | `appsettings.json` | MEDIUM | License violation |
| Redis passwords | `appsettings.json` | HIGH | Cache poisoning |
| SMTP credentials | `appsettings.json` | HIGH | Email spoofing |
| Encryption keys | `appsettings.json` | CRITICAL | Data decryption |
| Azure Storage keys | `appsettings.json` | CRITICAL | Blob storage access |

**Common mistakes:**
- Not using User Secrets in development
- Committing `appsettings.Production.json`
- Hardcoding secrets in `Startup.cs` or `Program.cs`
- Storing tenant secrets in multi-tenant configs
- Including secrets in publish profiles (`.pubxml`)

---

## Severity Matrix

### CRITICAL (Immediate Action Required)

**Impact:** Full system compromise, data breach, financial loss

**Examples:**
- AWS/Azure/GCP credentials
- Database connection strings with passwords
- Private cryptographic keys (RSA, EC, SSH)
- Production payment gateway keys (Stripe live, PayPal)
- OAuth client secrets
- IdentityServer/Keycloak secrets
- JWT signing keys

**Response time:** Within 1 hour
**Actions:**
1. Rotate credentials immediately
2. Audit access logs for unauthorized usage
3. Remove from git history
4. Implement secret manager
5. Notify security team

### HIGH (Action Required Today)

**Impact:** Partial system access, service disruption, data exposure

**Examples:**
- Generic API keys (SendGrid, Twilio, Mailgun)
- `NEXT_PUBLIC_` or `VITE_` vars with sensitive data
- SMTP credentials
- Redis passwords
- GitHub personal access tokens
- Third-party service tokens

**Response time:** Within 24 hours
**Actions:**
1. Rotate credentials
2. Check for unauthorized access
3. Update `.gitignore`
4. Move to secure storage

### MEDIUM (Action Required This Week)

**Impact:** Limited access, potential information disclosure

**Examples:**
- ABP license codes (should be in User Secrets)
- Slack webhooks
- Development/staging credentials
- Data protection keys
- Non-critical third-party API keys

**Response time:** Within 7 days
**Actions:**
1. Move to appropriate secret storage
2. Document in security audit
3. Update development practices

### LOW / INFO (Review Recommended)

**Impact:** Minimal risk, likely false positive

**Examples:**
- Obvious placeholders (`YOUR_API_KEY_HERE`)
- Variable references (`${{ secrets.X }}`)
- Documentation examples
- Commented-out old credentials
- Test/mock data

**Response time:** Next sprint
**Actions:**
1. Verify placeholder status
2. Add comments to clarify
3. Update documentation

---

## Remediation Strategies

### Next.js Remediation

#### 1. Use Environment Variables Correctly

**Development:**
```bash
# .env.local (gitignored)
DATABASE_URL=postgresql://user:pass@localhost/db
NEXTAUTH_SECRET=your-secret-key-here
STRIPE_SECRET_KEY=sk_test_...

# .env (committed - only public/default values)
NEXT_PUBLIC_APP_NAME=MyApp
NEXT_PUBLIC_API_URL=http://localhost:3000
```

**Production (Vercel):**
```bash
# Set via Vercel dashboard or CLI
vercel env add DATABASE_URL
vercel env add NEXTAUTH_SECRET
```

#### 2. Separate Client/Server Code

```typescript
// ✅ Good - server-only
// app/api/checkout/route.ts
import Stripe from 'stripe';
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

// ❌ Bad - exposed to client
// components/Checkout.tsx
const stripe = new Stripe(process.env.NEXT_PUBLIC_STRIPE_KEY!); // Danger!
```

#### 3. Remove from Git History

```bash
# Install git-filter-repo
brew install git-filter-repo

# Remove .env.production from all history
git filter-repo --path .env.production --invert-paths

# Force push (coordinate with team!)
git push origin --force --all
```

#### 4. Rotate Exposed Credentials

**Example: Rotate NextAuth secret**
```bash
# Generate new secret
openssl rand -base64 32

# Update .env.local and Vercel
vercel env rm NEXTAUTH_SECRET
vercel env add NEXTAUTH_SECRET
```

### Vite Remediation

#### 1. Use Correct Environment Files

```bash
# .env.local (gitignored - secrets)
DATABASE_URL=postgresql://...
API_SECRET_KEY=xyz123

# .env (committed - public only)
VITE_APP_NAME=MyApp
VITE_API_URL=http://localhost:3000
```

#### 2. Server-Side Environment Variables

**Vite SSR:**
```typescript
// ✅ Server-only (not prefixed with VITE_)
export async function handler() {
  const dbUrl = process.env.DATABASE_URL; // Not exposed
}

// ❌ Client-exposed (prefixed with VITE_)
const apiKey = import.meta.env.VITE_API_KEY; // Exposed in bundle!
```

#### 3. Build-Time Secret Injection

```typescript
// vite.config.ts
// ❌ Bad - secrets in config
export default defineConfig({
  define: {
    'API_KEY': JSON.stringify('sk_live_abc123')
  }
});

// ✅ Good - reference from environment
export default defineConfig({
  define: {
    '__BUILD_TIME__': JSON.stringify(new Date().toISOString())
  }
});
```

### .NET / ABP Remediation

#### 1. Use User Secrets (Development)

```bash
# Initialize User Secrets
cd MyProject.HttpApi.Host
dotnet user-secrets init

# Add secrets
dotnet user-secrets set "ConnectionStrings:Default" "Server=...;Password=xyz"
dotnet user-secrets set "AbpLicenseCode" "ABC-123-DEF"

# Verify
dotnet user-secrets list
```

**Stored in:** `~/.microsoft/usersecrets/{id}/secrets.json` (not in repo)

#### 2. Use Azure Key Vault (Production)

```csharp
// Program.cs or Startup.cs
public class Program
{
    public static void Main(string[] args)
    {
        CreateHostBuilder(args).Build().Run();
    }

    public static IHostBuilder CreateHostBuilder(string[] args) =>
        Host.CreateDefaultBuilder(args)
            .ConfigureAppConfiguration((context, config) =>
            {
                if (context.HostingEnvironment.IsProduction())
                {
                    var builtConfig = config.Build();
                    var keyVaultUrl = builtConfig["AzureKeyVault:VaultUri"];

                    config.AddAzureKeyVault(
                        new Uri(keyVaultUrl),
                        new DefaultAzureCredential());
                }
            })
            .ConfigureWebHostDefaults(webBuilder =>
            {
                webBuilder.UseStartup<Startup>();
            });
}
```

**Install package:**
```bash
dotnet add package Azure.Extensions.AspNetCore.Configuration.Secrets
dotnet add package Azure.Identity
```

#### 3. Environment-Specific Configs

```json
// appsettings.json (committed - no secrets)
{
  "ConnectionStrings": {
    "Default": "Server=localhost;Database=MyDb;Trusted_Connection=True"
  },
  "Jwt": {
    "Issuer": "MyApp",
    "Audience": "MyApp"
  }
}

// appsettings.Production.json (NOT committed)
{
  "ConnectionStrings": {
    "Default": "Server=prod-server;Database=MyDb;User=sa;Password=RealPassword"
  }
}
```

**Add to `.gitignore`:**
```
appsettings.Production.json
appsettings.Staging.json
appsettings.*.local.json
```

#### 4. ABP String Encryption

```csharp
// Use ABP's built-in encryption for sensitive settings
public class MySettings
{
    [EncryptedString] // Automatically encrypted in database
    public string ApiKey { get; set; }
}

// Configure encryption key (store in Key Vault)
Configure<AbpStringEncryptionOptions>(options =>
{
    options.DefaultPassPhrase = configuration["StringEncryption:PassPhrase"];
});
```

#### 5. Remove from Git History

```bash
# Remove appsettings.Production.json from history
git filter-repo --path appsettings.Production.json --invert-paths

# Or use BFG Repo-Cleaner (faster)
bfg --delete-files appsettings.Production.json
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

#### 6. Rotate Database Credentials

```sql
-- SQL Server: Change password
ALTER LOGIN [myuser] WITH PASSWORD = 'NewStrongP@ssw0rd!';

-- Update connection string in Key Vault or User Secrets
-- No need to update appsettings.json if using secrets manager
```

---

## Azure Services Remediation

### For Azure App Services

**1. Use Azure App Service Application Settings:**
```bash
# Via Azure CLI
az webapp config appsettings set \
  --resource-group MyResourceGroup \
  --name MyAppName \
  --settings \
    "ConnectionStrings__Default=Server=..." \
    "Jwt__Secret=..."

# Via Azure Portal:
# App Service → Configuration → Application settings → New application setting
```

**2. Azure Key Vault Integration:**
```csharp
// appsettings.json
{
  "KeyVault": {
    "VaultUri": "https://myvault.vault.azure.net/"
  }
}

// Program.cs
builder.Configuration.AddAzureKeyVault(
    new Uri(builder.Configuration["KeyVault:VaultUri"]),
    new DefaultAzureCredential());
```

**3. Managed Identity (No Credentials Needed):**
```csharp
// Enable Managed Identity in Azure Portal
// App Service → Identity → System assigned → On

// Access Azure SQL without password
var connectionString = "Server=tcp:myserver.database.windows.net;Database=mydb;Authentication=Active Directory Default";

// Access Key Vault without credentials
var credential = new DefaultAzureCredential();
var client = new SecretClient(new Uri(vaultUri), credential);
```

**4. Rotate Azure SQL Database Password:**
```sql
-- Azure SQL
ALTER LOGIN [myuser] WITH PASSWORD = 'NewP@ssw0rd!';

-- Update connection string in Key Vault
az keyvault secret set \
  --vault-name MyVault \
  --name ConnectionString \
  --value "Server=tcp:myserver.database.windows.net;Database=mydb;User=myuser;Password=NewP@ssw0rd!"
```

### For Azure DevOps Pipelines

**1. Use Azure Pipeline Variables (Secret):**
```yaml
# azure-pipelines.yml
variables:
- group: my-variable-group  # Define in Azure DevOps UI

steps:
- task: AzureCLI@2
  inputs:
    azureSubscription: '$(AzureSubscription)'  # Service connection
    scriptType: 'bash'
    scriptLocation: 'inlineScript'
    inlineScript: |
      az storage account keys list --account-name $(StorageAccountName)
```

**In Azure DevOps UI:**
- Pipelines → Library → Variable groups → New variable group
- Check "Link secrets from Azure Key Vault"
- Or manually add with lock icon (secret variable)

**2. Service Connections (Recommended):**
```yaml
# No credentials in code - use service connection
- task: AzureWebApp@1
  inputs:
    azureSubscription: 'MyServiceConnection'  # Configured in UI
    appName: 'MyApp'
```

**3. Rotate Azure DevOps PAT:**
```
1. Sign in to Azure DevOps
2. User Settings → Personal access tokens
3. Revoke old token
4. Create new token
5. Update in secrets manager (GitHub Secrets, Key Vault, etc.)
```

### For Azure Functions

**1. Use local.settings.json (Development - NEVER commit):**
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "dotnet",
    "MyApiKey": "dev-key-here"
  }
}
```

**Add to .gitignore:**
```bash
echo "local.settings.json" >> .gitignore
```

**2. Production - Use Application Settings:**
```bash
# Via Azure CLI
az functionapp config appsettings set \
  --name MyFunctionApp \
  --resource-group MyResourceGroup \
  --settings "MyApiKey=@Microsoft.KeyVault(SecretUri=https://myvault.vault.azure.net/secrets/MyApiKey/)"
```

### Azure Storage Account Key Rotation

**1. Rotate keys:**
```bash
# Regenerate key
az storage account keys renew \
  --resource-group MyResourceGroup \
  --account-name mystorageaccount \
  --key key1

# List new keys
az storage account keys list \
  --resource-group MyResourceGroup \
  --account-name mystorageaccount
```

**2. Update connection strings:**
```bash
# Update in Key Vault
az keyvault secret set \
  --vault-name MyVault \
  --name StorageConnectionString \
  --value "DefaultEndpointsProtocol=https;AccountName=...;AccountKey=NEW_KEY"
```

**3. Use key rotation strategy:**
- Rotate key2 first
- Update all apps to use key2
- Wait 24-48 hours
- Rotate key1
- Update apps back to key1

### Azure Container Registry Authentication

**1. Use Admin Credentials (NOT recommended for production):**
```bash
# Disable admin user in production
az acr update --name myregistry --admin-enabled false
```

**2. Use Service Principal (Recommended):**
```bash
# Create service principal
az ad sp create-for-rbac \
  --name myAcrServicePrincipal \
  --scopes $(az acr show --name myregistry --query id -o tsv) \
  --role acrpull

# Output: appId, password, tenant
# Store in Key Vault
```

**3. Use Managed Identity (Best):**
```bash
# Enable managed identity on App Service
az webapp identity assign --resource-group MyRG --name MyApp

# Grant ACR pull permission
az role assignment create \
  --assignee <managed-identity-id> \
  --scope <acr-resource-id> \
  --role acrpull
```

---

## Docker Secrets Remediation

### For Docker Compose

**1. Use .env file (gitignored):**
```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    image: myapp
    environment:
      - DATABASE_PASSWORD=${DATABASE_PASSWORD}
      - API_KEY=${API_KEY}
```

**Create .env file (add to .gitignore):**
```bash
DATABASE_PASSWORD=MySecretP@ss
API_KEY=sk_live_abc123
```

**2. Use Docker Secrets (Swarm mode):**
```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    image: myapp
    secrets:
      - db_password
      - api_key
    environment:
      - DATABASE_PASSWORD_FILE=/run/secrets/db_password

secrets:
  db_password:
    external: true
  api_key:
    external: true
```

**Create secrets:**
```bash
echo "MySecretP@ss" | docker secret create db_password -
echo "sk_live_abc123" | docker secret create api_key -
```

**3. Use external secrets file:**
```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    env_file:
      - .env.local  # Gitignored
```

### For Dockerfile

**1. Use Build Secrets (BuildKit):**
```dockerfile
# Dockerfile
# syntax=docker/dockerfile:1

FROM node:18

# Mount secret during build (not stored in image)
RUN --mount=type=secret,id=npmtoken \
    echo "//registry.npmjs.org/:_authToken=$(cat /run/secrets/npmtoken)" > ~/.npmrc && \
    npm install && \
    rm ~/.npmrc

COPY . .
CMD ["npm", "start"]
```

**Build with secret:**
```bash
docker buildx build \
  --secret id=npmtoken,src=.npmtoken \
  --tag myapp:latest .
```

**2. Multi-stage builds (keep secrets out of final image):**
```dockerfile
# Build stage (secrets OK here, not in final image)
FROM node:18 AS builder
ARG NPM_TOKEN
RUN echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > ~/.npmrc
RUN npm install
RUN rm ~/.npmrc

# Production stage (clean image, no secrets)
FROM node:18-slim
COPY --from=builder /app/node_modules ./node_modules
COPY . .
CMD ["npm", "start"]
```

**Build:**
```bash
docker build --build-arg NPM_TOKEN=$(cat .npmtoken) -t myapp .
```

**3. Never use ENV/ARG for runtime secrets:**
```dockerfile
# ❌ BAD - visible in docker inspect
ENV DATABASE_PASSWORD=MyP@ss123
ENV API_KEY=sk_live_abc123

# ✅ GOOD - pass at runtime
# (no ENV/ARG, passed via docker run -e)
```

**Runtime:**
```bash
docker run -e DATABASE_PASSWORD="MyP@ss" -e API_KEY="sk_live" myapp
```

### Docker Hub / Registry Credentials

**1. Rotate Docker Hub tokens:**
```
1. Log in to hub.docker.com
2. Account Settings → Security → Access Tokens
3. Delete old token
4. Create new token
5. Update in CI/CD secrets
```

**2. Use docker login with stdin (safer):**
```bash
# ❌ BAD - password in shell history
docker login -u myuser -p MyP@ss

# ✅ GOOD - stdin
echo "$DOCKER_PASSWORD" | docker login -u myuser --password-stdin

# ✅ BEST - use credential helper
docker login  # Interactive prompt
```

**3. Azure Container Registry:**
```bash
# Use service principal
az acr login --name myregistry \
  --username $SERVICE_PRINCIPAL_ID \
  --password $SERVICE_PRINCIPAL_PASSWORD

# Or use managed identity
az acr login --name myregistry
```

### Remove Secrets from Docker Images

**1. Check if secrets in image:**
```bash
# View image history
docker history myapp:latest

# Check for secrets in layers
docker save myapp:latest | tar -xvf - -O | grep -i "password\|secret\|key"
```

**2. Rebuild without secrets:**
- Remove ARG/ENV with secrets
- Use build secrets instead
- Rebuild and re-push image
- Update deployments to use new tag

**3. Scan images for secrets:**
```bash
# Using trivy
trivy image myapp:latest

# Using grype
grype myapp:latest
```

### Docker in CI/CD

**GitHub Actions:**
```yaml
name: Build and Push

on: push

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: myapp:latest
          secrets: |
            "npmtoken=${{ secrets.NPM_TOKEN }}"
```

**Azure Pipelines:**
```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  - group: docker-credentials  # In Azure DevOps Library

steps:
- task: Docker@2
  inputs:
    command: 'login'
    containerRegistry: 'MyDockerServiceConnection'

- task: Docker@2
  inputs:
    command: 'buildAndPush'
    repository: 'myapp'
    tags: '$(Build.BuildId)'
```

---

## Prevention Best Practices

### For All Projects

#### 1. Use `.gitignore` Properly

```bash
# Environment files
.env
.env.local
.env.*.local
.env.production
.env.staging

# .NET
appsettings.*.json
!appsettings.json
!appsettings.Development.json
*.user
*.pubxml

# Secrets
secrets.json
*.key
*.pem
*.cer
*.pfx

# IDE
.vs/
.vscode/settings.json
.idea/

# Build outputs
.next/
dist/
build/
bin/
obj/
```

#### 2. Pre-Commit Hooks

**Using Husky (Next.js/Vite):**
```bash
npm install -D husky
npx husky init

# .husky/pre-commit
#!/bin/sh
python3 .claude/skills/scanning-for-secrets/scripts/scan_files.py
if [ $? -ne 0 ]; then
  echo "❌ Secret scan failed - commit blocked"
  exit 1
fi
```

**Using .NET Pre-Commit:**
```bash
# .git/hooks/pre-commit
#!/bin/bash
dotnet tool install -g dotnet-secrets-scanner
dotnet secrets-scanner scan --path ./

if [ $? -ne 0 ]; then
  echo "❌ Secrets detected - commit blocked"
  exit 1
fi
```

#### 3. CI/CD Pipeline Checks

**GitHub Actions:**
```yaml
name: Security Scan
on: [push, pull_request]

jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Scan for secrets
        run: |
          pip install gitpython
          python3 .claude/skills/scanning-for-secrets/scripts/scan_files.py
```

**GitLab CI:**
```yaml
secret-scan:
  stage: security
  script:
    - pip install gitpython
    - python3 .claude/skills/scanning-for-secrets/scripts/scan_files.py
  only:
    - merge_requests
```

#### 4. Secret Manager Services

**Recommended by framework:**

| Framework | Development | Production |
|-----------|-------------|------------|
| Next.js | `.env.local` | Vercel Env Vars / AWS Secrets Manager |
| Vite | `.env.local` | Netlify Env Vars / AWS Secrets Manager |
| .NET | User Secrets | Azure Key Vault / AWS Secrets Manager |
| ABP | User Secrets | Azure Key Vault + ABP SettingEncryptionService |

#### 5. Code Review Checklist

**Before approving PRs:**
- [ ] No `.env*` files committed (except `.env.example`)
- [ ] No `appsettings.*.json` with secrets
- [ ] `NEXT_PUBLIC_` / `VITE_` vars contain only public data
- [ ] Connection strings use placeholders or environment references
- [ ] No hardcoded API keys in source code
- [ ] Secrets referenced from environment/config, not inline
- [ ] `.gitignore` updated if new secret files added

---

## Incident Response

### If Secrets Are Exposed

#### Immediate Actions (Within 1 Hour)

**1. Assess Exposure:**
```bash
# Check if pushed to remote
git log --oneline origin/main..HEAD

# If pushed, assume compromised
# If only local, rotate as precaution
```

**2. Rotate Credentials:**

| Secret Type | Rotation Steps |
|-------------|----------------|
| AWS Keys | IAM Console → Users → Security Credentials → Deactivate + Create New |
| Database Password | `ALTER USER ... WITH PASSWORD '...';` |
| API Keys | Service dashboard → Regenerate keys |
| JWT Secret | Generate new + redeploy (invalidates all tokens) |
| OAuth Secrets | Provider dashboard → Rotate client secret |

**3. Revoke Access:**
```bash
# Check access logs
# AWS
aws cloudtrail lookup-events --lookup-attributes AttributeKey=AccessKeyId,AttributeValue=AKIA...

# Azure
az monitor activity-log list --resource-group MyRG

# Check application logs for unauthorized requests
```

#### Short-Term Actions (Within 24 Hours)

**4. Remove from Git History:**
```bash
# Option 1: git-filter-repo (recommended)
git filter-repo --path .env.production --invert-paths

# Option 2: BFG Repo-Cleaner (faster for large repos)
bfg --delete-files .env.production

# Force push to all branches
git push origin --force --all
git push origin --force --tags

# Notify team to re-clone repository
```

**5. Update Secret Storage:**

**Next.js/Vite:**
```bash
# Create .env.example template
cp .env.local .env.example
# Replace all values with placeholders
sed -i '' 's/=.*/=YOUR_VALUE_HERE/g' .env.example
git add .env.example
```

**.NET:**
```bash
# Migrate to User Secrets
dotnet user-secrets set "ConnectionStrings:Default" "real-value"

# Update appsettings.json to reference
{
  "ConnectionStrings": {
    "Default": "Server=localhost;Database=MyDb;Trusted_Connection=True"
  }
}
```

**6. Add to `.gitignore`:**
```bash
echo ".env.local" >> .gitignore
echo "appsettings.*.json" >> .gitignore
git add .gitignore
git commit -m "chore: prevent secret files from being committed"
```

#### Long-Term Actions (Within 1 Week)

**7. Implement Secret Manager:**

**Next.js (Vercel):**
```bash
vercel env add DATABASE_URL production
vercel env add NEXTAUTH_SECRET production
```

**.NET (Azure Key Vault):**
```csharp
// Install packages
dotnet add package Azure.Extensions.AspNetCore.Configuration.Secrets
dotnet add package Azure.Identity

// Configure in Program.cs
config.AddAzureKeyVault(
    new Uri("https://my-vault.vault.azure.net/"),
    new DefaultAzureCredential());
```

**8. Setup Monitoring:**

**AWS CloudTrail alerts:**
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "Suspicious-API-Key-Usage" \
  --alarm-description "Alert on API key usage from unknown IP" \
  --metric-name "UnauthorizedAPICall"
```

**Application logging:**
```csharp
// Log all authentication attempts
logger.LogWarning("Failed authentication from IP: {IP}", ipAddress);
```

**9. Security Audit:**
- Review all environment files
- Check CI/CD pipeline for hardcoded secrets
- Audit Dockerfile ARG/ENV usage
- Review third-party integrations

**10. Team Training:**
- Document secret management process
- Add to onboarding checklist
- Setup pre-commit hooks for new developers
- Quarterly security reviews

---

## Tools & Services

### Secret Scanning Tools

| Tool | Use Case | Cost |
|------|----------|------|
| **gitleaks** | Git history scanning | Free |
| **TruffleHog** | Entropy-based detection | Free |
| **git-secrets** | AWS-specific patterns | Free |
| **detect-secrets** | Pre-commit hooks | Free |
| **GitHub Secret Scanning** | Automatic detection on push | Free (public repos) |
| **GitGuardian** | Enterprise scanning + alerts | Paid |

### Secret Management Services

| Service | Best For | Pricing |
|---------|----------|---------|
| **Azure Key Vault** | .NET/ABP apps | $0.03 per 10k operations |
| **AWS Secrets Manager** | Next.js on AWS | $0.40 per secret/month |
| **HashiCorp Vault** | Multi-cloud, complex needs | Open source / Enterprise |
| **Vercel Env Variables** | Next.js deployments | Free with Vercel |
| **Netlify Env Variables** | Vite/SPA deployments | Free with Netlify |
| **.NET User Secrets** | Local development | Free (built-in) |

### Installation Commands

**gitleaks:**
```bash
# macOS
brew install gitleaks

# Scan repository
gitleaks detect --source . --verbose
```

**TruffleHog:**
```bash
# Install
pip install trufflehog

# Scan
trufflehog filesystem . --json > findings.json
```

**git-secrets:**
```bash
# Install
brew install git-secrets

# Setup in repo
git secrets --install
git secrets --register-aws
```

---

## Quick Reference Commands

### Rotate Credentials

```bash
# Generate strong password
openssl rand -base64 32

# Generate UUID
uuidgen

# Generate API key format
openssl rand -hex 32

# Generate JWT secret (256-bit)
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

### Remove Files from Git History

```bash
# Remove specific file
git filter-repo --path secrets.env --invert-paths

# Remove by pattern
git filter-repo --path-glob '*.env' --invert-paths

# Remove by content (specific secret)
git filter-repo --replace-text <(echo "sk_live_abc123==>REMOVED")
```

### Check Exposure

```bash
# Check if file was ever committed
git log --all --full-history -- .env.production

# Find when secret was added
git log -S"sk_live_abc123" --source --all

# List all commits affecting file
git log --follow -- appsettings.Production.json
```

---

## Compliance & Standards

### OWASP Guidelines
- [A02:2021 – Cryptographic Failures](https://owasp.org/Top10/A02_2021-Cryptographic_Failures/)
- Secrets should never be stored in source code
- Use secure secret storage mechanisms
- Rotate credentials regularly

### CIS Benchmarks
- Implement least privilege access
- Audit secret access logs
- Encrypt secrets at rest and in transit
- Regular vulnerability assessments

### Industry Standards
- **PCI DSS:** No storage of authentication data post-authorization
- **SOC 2:** Secure credential management and rotation
- **ISO 27001:** Access control and key management

---

## Emergency Contacts

**If you discover a serious exposure:**

1. **Internal:** Notify security team immediately
2. **External:** If customer data at risk, follow breach notification procedures
3. **Service Providers:** Contact API providers (AWS, Stripe, etc.) to report compromise

**Example notification template:**
```
Subject: Security Incident - Exposed Credentials

Credentials exposed: [Type, e.g., AWS Access Keys]
Exposure date: [When committed/pushed]
Exposure scope: [Public repo / Private repo / Team only]
Actions taken: [Rotated, removed from history, etc.]
Impact: [Estimated scope of potential unauthorized access]
```

---

**Document version:** 1.0.0
**Last updated:** 2025-01
**Maintained by:** Security Team
