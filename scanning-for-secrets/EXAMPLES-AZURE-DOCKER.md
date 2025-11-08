# Azure & Docker Secret Scanner Examples

Comprehensive examples for detecting and remediating secrets in Azure and Docker environments.

---

## Example 1: Azure App Service with appsettings.json

### Scenario
.NET app deployed to Azure App Service with secrets in `appsettings.json`.

**File: `appsettings.json`**
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=tcp:myapp.database.windows.net,1433;Database=ProductionDB;User ID=sqladmin;Password=MyAzureDB_P@ss2024!;Encrypt=True;"
  },
  "AzureStorage": {
    "ConnectionString": "DefaultEndpointsProtocol=https;AccountName=myappstorage;AccountKey=abc123XYZ789...Base64Key88Chars==;EndpointSuffix=core.windows.net"
  },
  "ServiceBus": {
    "ConnectionString": "Endpoint=sb://myapp-bus.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=MySharedAccessKey123456=="
  },
  "ApplicationInsights": {
    "InstrumentationKey": "12345678-1234-1234-1234-123456789012"
  },
  "AzureAd": {
    "ClientSecret": "abc~123.def456-ghi_789jkl012mno"
  }
}
```

### Expected Detection

```
🚨 CRITICAL Findings:
- Azure SQL Database Connection String (line 3)
  Pattern: Server=tcp:*.database.windows.net with Password
  Value: MyAzureDB_P@ss2024!

- Azure Storage Account Key (line 6)
  Pattern: AccountKey with 88-char Base64
  Value: abc123XYZ789...==

- Azure Service Bus Connection String (line 9)
  Pattern: SharedAccessKey
  Value: MySharedAccessKey123456==

- Azure Service Principal Client Secret (line 14)
  Pattern: ClientSecret (34-40 chars)
  Value: abc~123.def456-ghi_789jkl012mno

📋 MEDIUM Findings:
- Application Insights Instrumentation Key (line 12)
  Severity: Lower (telemetry only, but should protect)
```

### Remediation

**Step 1: Use Azure Key Vault**
```csharp
// Program.cs
using Azure.Identity;
using Azure.Extensions.AspNetCore.Configuration.Secrets;

var builder = WebApplication.CreateBuilder(args);

// Add Azure Key Vault
var keyVaultUri = new Uri(builder.Configuration["KeyVault:VaultUri"]);
builder.Configuration.AddAzureKeyVault(keyVaultUri, new DefaultAzureCredential());

var app = builder.Build();
```

**Step 2: Store secrets in Key Vault**
```bash
# Create Key Vault
az keyvault create \
  --name myapp-vault \
  --resource-group MyResourceGroup \
  --location eastus

# Add secrets
az keyvault secret set \
  --vault-name myapp-vault \
  --name ConnectionStrings--DefaultConnection \
  --value "Server=tcp:myapp.database.windows.net,1433;..."

az keyvault secret set \
  --vault-name myapp-vault \
  --name AzureStorage--ConnectionString \
  --value "DefaultEndpointsProtocol=https;..."
```

**Step 3: Enable Managed Identity**
```bash
# Enable on App Service
az webapp identity assign \
  --resource-group MyResourceGroup \
  --name myapp

# Grant Key Vault access
az keyvault set-policy \
  --name myapp-vault \
  --object-id <managed-identity-id> \
  --secret-permissions get list
```

**Step 4: Update appsettings.json (no secrets)**
```json
{
  "KeyVault": {
    "VaultUri": "https://myapp-vault.vault.azure.net/"
  },
  "ApplicationInsights": {
    "ConnectionString": "InstrumentationKey=12345678-1234-1234-1234-123456789012"
  }
}
```

---

## Example 2: Azure DevOps Pipeline with Hardcoded Secrets

### Scenario
Azure Pipeline with exposed PAT and Service Principal credentials.

**File: `azure-pipelines.yml`**
```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  AZURE_CLIENT_ID: '12345678-1234-1234-1234-123456789012'
  AZURE_CLIENT_SECRET: 'abc~123.def456-ghi_789jkl012mno'  # ❌ EXPOSED!
  AZURE_TENANT_ID: '87654321-4321-4321-4321-210987654321'
  AZURE_DEVOPS_PAT: 'abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmn'  # ❌ EXPOSED!
  ACR_PASSWORD: 'MyAzureContainerRegistryP@ssw0rd123'  # ❌ EXPOSED!

steps:
- task: Docker@2
  inputs:
    containerRegistry: 'myregistry.azurecr.io'
    repository: 'myapp'
    command: 'buildAndPush'
    Dockerfile: '**/Dockerfile'
    tags: |
      $(Build.BuildId)
  env:
    DOCKER_PASSWORD: $(ACR_PASSWORD)
```

### Expected Detection

```
🚨 CRITICAL Findings:
- Azure Service Principal Client Secret (line 9)
- Azure DevOps Personal Access Token (line 11)
- Azure Container Registry Password (line 12)
```

### Remediation

**Step 1: Use Variable Groups with Key Vault**
```yaml
# azure-pipelines.yml (FIXED)
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

variables:
- group: azure-credentials  # Link to Key Vault in Azure DevOps

steps:
- task: AzureCLI@2
  inputs:
    azureSubscription: 'MyServiceConnection'  # Service connection (no credentials)
    scriptType: 'bash'
    scriptLocation: 'inlineScript'
    inlineScript: |
      az acr login --name myregistry
      docker build -t myregistry.azurecr.io/myapp:$(Build.BuildId) .
      docker push myregistry.azurecr.io/myapp:$(Build.BuildId)
```

**Step 2: Create Variable Group in Azure DevOps**
```
1. Azure DevOps → Pipelines → Library
2. Variable groups → + Variable group
3. Name: azure-credentials
4. Link secrets from Azure Key Vault → Toggle ON
5. Select Azure subscription & Key Vault
6. Authorize
7. Select secrets to expose as variables
```

**Step 3: Use Service Connections (Best Practice)**
```
1. Project Settings → Service connections
2. New service connection → Azure Resource Manager
3. Service principal (automatic) → Next
4. Select subscription & resource group
5. Name: MyServiceConnection
6. Save
7. Use in pipeline: azureSubscription: 'MyServiceConnection'
```

---

## Example 3: Docker Compose with Hardcoded Secrets

### Scenario
`docker-compose.yml` with database passwords and API keys hardcoded.

**File: `docker-compose.yml`**
```yaml
version: '3.8'

services:
  web:
    image: myapp:latest
    ports:
      - "80:80"
    environment:
      DATABASE_HOST: db
      DATABASE_PASSWORD: MyPostgresP@ssw0rd123  # ❌ EXPOSED!
      API_KEY: sk_live_abc123def456ghi789  # ❌ EXPOSED!
      STRIPE_SECRET: sk_live_xyz789abc456def123  # ❌ EXPOSED!
      REDIS_PASSWORD: MyRedisP@ss456  # ❌ EXPOSED!
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: MyPostgresP@ssw0rd123  # ❌ EXPOSED!
      POSTGRES_USER: admin
      POSTGRES_DB: myappdb

  redis:
    image: redis:7
    command: redis-server --requirepass MyRedisP@ss456  # ❌ EXPOSED!
```

### Expected Detection

```
🚨 HIGH Findings:
- Docker Compose Environment Secret: DATABASE_PASSWORD (line 9)
- Docker Compose Environment Secret: API_KEY (line 10)
- Docker Compose Environment Secret: STRIPE_SECRET (line 11)
- Docker Compose Environment Secret: REDIS_PASSWORD (line 12)
- Docker Compose Environment Secret: POSTGRES_PASSWORD (line 20)
```

### Remediation

**Option 1: Use .env file (Simple)**

**File: `.env` (add to .gitignore)**
```bash
DATABASE_PASSWORD=MyPostgresP@ssw0rd123
API_KEY=sk_live_abc123def456ghi789
STRIPE_SECRET=sk_live_xyz789abc456def123
REDIS_PASSWORD=MyRedisP@ss456
POSTGRES_PASSWORD=MyPostgresP@ssw0rd123
POSTGRES_USER=admin
POSTGRES_DB=myappdb
```

**File: `docker-compose.yml` (FIXED)**
```yaml
version: '3.8'

services:
  web:
    image: myapp:latest
    ports:
      - "80:80"
    environment:
      DATABASE_HOST: db
      DATABASE_PASSWORD: ${DATABASE_PASSWORD}
      API_KEY: ${API_KEY}
      STRIPE_SECRET: ${STRIPE_SECRET}
      REDIS_PASSWORD: ${REDIS_PASSWORD}
    env_file:
      - .env
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_DB: ${POSTGRES_DB}

  redis:
    image: redis:7
    command: redis-server --requirepass ${REDIS_PASSWORD}
```

**Add to .gitignore:**
```bash
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
```

**Option 2: Use Docker Secrets (Swarm mode)**

**File: `docker-compose.yml` (Swarm mode)**
```yaml
version: '3.8'

services:
  web:
    image: myapp:latest
    ports:
      - "80:80"
    secrets:
      - db_password
      - api_key
      - stripe_secret
    environment:
      DATABASE_HOST: db
      DATABASE_PASSWORD_FILE: /run/secrets/db_password
      API_KEY_FILE: /run/secrets/api_key
      STRIPE_SECRET_FILE: /run/secrets/stripe_secret

secrets:
  db_password:
    external: true
  api_key:
    external: true
  stripe_secret:
    external: true
```

**Create secrets:**
```bash
# Initialize swarm
docker swarm init

# Create secrets
echo "MyPostgresP@ssw0rd123" | docker secret create db_password -
echo "sk_live_abc123def456ghi789" | docker secret create api_key -
echo "sk_live_xyz789abc456def123" | docker secret create stripe_secret -

# Deploy stack
docker stack deploy -c docker-compose.yml myapp
```

---

## Example 4: Dockerfile with Build-time Secrets

### Scenario
Dockerfile with NPM token in `ARG` (visible in image history).

**File: `Dockerfile`**
```dockerfile
FROM node:18

WORKDIR /app

# ❌ BAD - ARG visible in docker history
ARG NPM_TOKEN=abc123-def456-ghi789-jkl012
ENV API_KEY=sk_live_xyz789  # ❌ BAD - ENV visible in docker inspect

RUN echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > ~/.npmrc && \
    npm install && \
    rm ~/.npmrc

COPY . .

CMD ["npm", "start"]
```

### Expected Detection

```
🚨 HIGH Findings:
- Dockerfile ARG with Secret: NPM_TOKEN (line 5)
- Dockerfile ENV with Secret: API_KEY (line 6)

⚠️ Warning: ARG values are visible in docker history
⚠️ Warning: ENV values are visible in docker inspect
```

### Remediation

**Option 1: Use BuildKit Secrets (Recommended)**

**File: `Dockerfile`** (FIXED)
```dockerfile
# syntax=docker/dockerfile:1

FROM node:18

WORKDIR /app

# ✅ GOOD - Mount secret during build (not stored in image)
RUN --mount=type=secret,id=npmtoken \
    echo "//registry.npmjs.org/:_authToken=$(cat /run/secrets/npmtoken)" > ~/.npmrc && \
    npm install && \
    rm ~/.npmrc

COPY . .

# ✅ GOOD - No ENV for API_KEY, pass at runtime
CMD ["npm", "start"]
```

**Build:**
```bash
# Create .npmtoken file (add to .gitignore)
echo "abc123-def456-ghi789-jkl012" > .npmtoken

# Build with BuildKit
DOCKER_BUILDKIT=1 docker build \
  --secret id=npmtoken,src=.npmtoken \
  --tag myapp:latest .

# Run with runtime secret
docker run -e API_KEY="sk_live_xyz789" myapp:latest
```

**Option 2: Multi-stage Build (Keep Secrets Out of Final Image)**

**File: `Dockerfile`** (Multi-stage)
```dockerfile
# Build stage - secrets OK here (not in final image)
FROM node:18 AS builder

WORKDIR /app

ARG NPM_TOKEN
RUN echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > ~/.npmrc
COPY package*.json ./
RUN npm install
RUN rm ~/.npmrc

COPY . .
RUN npm run build

# Production stage - clean image, no secrets
FROM node:18-slim

WORKDIR /app

COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY package*.json ./

# No secrets in this layer
CMD ["npm", "start"]
```

**Build:**
```bash
docker build \
  --build-arg NPM_TOKEN=$(cat .npmtoken) \
  --target production \
  --tag myapp:latest .

# Verify no secrets in final image
docker history myapp:latest  # Should not show NPM_TOKEN
```

---

## Example 5: Azure Functions with local.settings.json

### Scenario
Azure Functions project with `local.settings.json` committed to git.

**File: `local.settings.json`** (❌ Should NEVER be committed)
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "DefaultEndpointsProtocol=https;AccountName=myappstorage;AccountKey=abc123XYZ789...==;",
    "FUNCTIONS_WORKER_RUNTIME": "dotnet",
    "CosmosDbConnectionString": "AccountEndpoint=https://mydb.documents.azure.com:443/;AccountKey=xyz789ABC123...==;",
    "ServiceBusConnection": "Endpoint=sb://mybus.servicebus.windows.net/;SharedAccessKey=MyKey123==",
    "MyApiKey": "sk_live_abc123def456",
    "DatabasePassword": "MyFunctionDB_P@ss!"
  },
  "Host": {
    "LocalHttpPort": 7071
  }
}
```

### Expected Detection

```
🚨 CRITICAL Findings:
- Azure Storage Connection String (line 4)
- Azure Cosmos DB Connection String (line 6)
- Azure Service Bus Connection String (line 7)
- Generic API Key (line 8)
- Password Variable (line 9)
```

### Remediation

**Step 1: Add to .gitignore**
```bash
echo "local.settings.json" >> .gitignore
git rm --cached local.settings.json
git commit -m "Remove local.settings.json from tracking"
```

**Step 2: Create template file (commit this)**

**File: `local.settings.json.example`**
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "dotnet",
    "CosmosDbConnectionString": "YOUR_COSMOS_CONNECTION_STRING",
    "ServiceBusConnection": "YOUR_SERVICEBUS_CONNECTION_STRING",
    "MyApiKey": "YOUR_API_KEY",
    "DatabasePassword": "YOUR_DATABASE_PASSWORD"
  }
}
```

**Step 3: Production - Use Azure Function App Settings**
```bash
# Set application settings via Azure CLI
az functionapp config appsettings set \
  --name MyFunctionApp \
  --resource-group MyResourceGroup \
  --settings \
    "CosmosDbConnectionString=@Microsoft.KeyVault(SecretUri=https://myvault.vault.azure.net/secrets/CosmosDbConnectionString/)" \
    "ServiceBusConnection=@Microsoft.KeyVault(SecretUri=https://myvault.vault.azure.net/secrets/ServiceBusConnection/)" \
    "MyApiKey=@Microsoft.KeyVault(SecretUri=https://myvault.vault.azure.net/secrets/MyApiKey/)"
```

**Step 4: Rotate all exposed keys**
```bash
# Rotate Storage Account Key
az storage account keys renew \
  --resource-group MyResourceGroup \
  --account-name myappstorage \
  --key key1

# Rotate Cosmos DB keys
az cosmosdb keys regenerate \
  --resource-group MyResourceGroup \
  --name mydb \
  --key-kind primary
```

---

## Example 6: Azure Container Registry in CI/CD

### Scenario
GitHub Actions workflow with ACR credentials hardcoded.

**File: `.github/workflows/deploy.yml`**
```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Login to Azure Container Registry
        run: |
          docker login myregistry.azurecr.io \
            --username myregistry \
            --password MyAzureACR_P@ssw0rd123  # ❌ EXPOSED!

      - name: Build and Push
        run: |
          docker build -t myregistry.azurecr.io/myapp:${{ github.sha }} .
          docker push myregistry.azurecr.io/myapp:${{ github.sha }}
```

### Expected Detection

```
🚨 CRITICAL Findings:
- Password in docker login command (line 17)
- Azure Container Registry credentials exposed
```

### Remediation

**Option 1: Use GitHub Secrets + Service Principal**

**File: `.github/workflows/deploy.yml`** (FIXED)
```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}  # Service Principal JSON

      - name: ACR Login
        uses: azure/docker-login@v1
        with:
          login-server: myregistry.azurecr.io
          username: ${{ secrets.ACR_USERNAME }}
          password: ${{ secrets.ACR_PASSWORD }}

      - name: Build and Push
        run: |
          docker build -t myregistry.azurecr.io/myapp:${{ github.sha }} .
          docker push myregistry.azurecr.io/myapp:${{ github.sha }}
```

**Setup GitHub Secrets:**
```bash
# Create Service Principal for ACR
az ad sp create-for-rbac \
  --name github-actions-acr \
  --role acrpush \
  --scopes $(az acr show --name myregistry --query id -o tsv) \
  --sdk-auth

# Output JSON - add to GitHub Secrets as AZURE_CREDENTIALS

# Or use ACR admin credentials (not recommended for production)
az acr credential show --name myregistry
# Add username/password to GitHub Secrets
```

**Add secrets in GitHub:**
```
Repository → Settings → Secrets and variables → Actions → New repository secret
- AZURE_CREDENTIALS: <service principal JSON>
- ACR_USERNAME: <username>
- ACR_PASSWORD: <password>
```

**Option 2: Use OpenID Connect (No secrets!)**

**File: `.github/workflows/deploy.yml`** (OIDC)
```yaml
name: Build and Deploy

permissions:
  id-token: write  # Required for OIDC
  contents: read

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Azure Login (OIDC - no secrets!)
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: ACR Build and Push
        run: |
          az acr build \
            --registry myregistry \
            --image myapp:${{ github.sha }} \
            .
```

---

## Summary

### Azure Secrets - Common Mistakes

1. ❌ Committing `appsettings.Production.json`
2. ❌ Hardcoding `AZURE_CLIENT_SECRET` in pipeline YAML
3. ❌ Committing `local.settings.json` (Azure Functions)
4. ❌ Publishing `.pubxml` files with passwords
5. ❌ Using admin credentials for ACR (should use Service Principal)

### Docker Secrets - Common Mistakes

1. ❌ Hardcoding passwords in `docker-compose.yml` `environment:` sections
2. ❌ Using `ARG` for secrets (visible in `docker history`)
3. ❌ Using `ENV` for secrets (visible in `docker inspect`)
4. ❌ Committing `.docker/config.json` with auth tokens
5. ❌ Not using `.env` files or docker secrets

### Best Practices

✅ **Azure:**
- Use Azure Key Vault for all secrets
- Enable Managed Identity (no credentials needed)
- Use service connections in Azure DevOps
- Never commit `local.settings.json`
- Rotate keys if exposed

✅ **Docker:**
- Use `.env` files (gitignored) for compose
- Use BuildKit `--mount=type=secret` for builds
- Use multi-stage builds
- Never use `ARG`/`ENV` for secrets
- Use Docker Secrets in Swarm mode

---

**Document Version:** 1.0.0 (Azure & Docker Edition)
**Last Updated:** 2025-01
