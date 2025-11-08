# Secret Detection Patterns

Comprehensive pattern definitions for detecting hardcoded secrets in Next.js/Vite and .NET/ABP projects.

## Pattern Format

Each pattern includes:
- **Name:** Human-readable identifier
- **Regex:** Detection pattern
- **Severity:** CRITICAL | HIGH | MEDIUM | LOW
- **Context:** Where typically found
- **Example:** Real-world example (sanitized)

---

## Cloud Provider Credentials

### AWS Access Key ID
```python
{
    "name": "AWS Access Key ID",
    "pattern": r"AKIA[0-9A-Z]{16}",
    "severity": "CRITICAL",
    "context": [".env", "appsettings.json", "config files"],
    "example": "AKIAIOSFODNN7EXAMPLE"
}
```

### AWS Secret Access Key
```python
{
    "name": "AWS Secret Access Key",
    "pattern": r"aws[_-]?secret[_-]?access[_-]?key['\"\s:=]+[A-Za-z0-9/+=]{40}",
    "severity": "CRITICAL",
    "context": [".env", "appsettings.json"],
    "example": "aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}
```

### AWS Session Token
```python
{
    "name": "AWS Session Token",
    "pattern": r"aws[_-]?session[_-]?token['\"\s:=]+[A-Za-z0-9/+=]{100,}",
    "severity": "HIGH",
    "context": [".env", "temporary credentials"],
    "example": "aws_session_token=FwoGZXIvYXdzE..."
}
```

### Azure Storage Connection String
```python
{
    "name": "Azure Storage Connection String",
    "pattern": r"DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[A-Za-z0-9+/=]{88};",
    "severity": "CRITICAL",
    "context": ["appsettings.json", ".env", "Web.config"],
    "example": "DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=abc123...=="
}
```

### Azure Client Secret
```python
{
    "name": "Azure Client Secret",
    "pattern": r"[a-zA-Z0-9~_-]{32,}",
    "severity": "HIGH",
    "context": ["AzureAd:ClientSecret in appsettings.json"],
    "validation": "Check if key is 'ClientSecret' or 'Secret'"
}
```

### Google Cloud API Key
```python
{
    "name": "Google Cloud API Key",
    "pattern": r"AIza[0-9A-Za-z_-]{35}",
    "severity": "CRITICAL",
    "context": [".env", "next.config.js", "public configs"],
    "example": "AIzaSyDaGmWKa4JsXZ-HjGw7ISLn_3namBGewQe"
}
```

### Google OAuth Client Secret
```python
{
    "name": "Google OAuth Client Secret",
    "pattern": r"['\"]client_secret['\"]:\s*['\"]([A-Za-z0-9_-]{24})['\"]",
    "severity": "CRITICAL",
    "context": ["credentials.json", "appsettings.json"],
    "example": "\"client_secret\": \"GOCSPX-abc123def456\""
}
```

---

## Azure Specific Patterns

### Azure SQL Database Connection String
```python
{
    "name": "Azure SQL Database Connection String",
    "pattern": r"Server=tcp:[^;]+\.database\.windows\.net[^;]*;.*Password=([^;\"']+)",
    "severity": "CRITICAL",
    "context": ["appsettings.json", ".env", "azure-pipelines.yml"],
    "example": "Server=tcp:myserver.database.windows.net,1433;Database=mydb;User ID=admin;Password=MyP@ss123"
}
```

### Azure Service Principal Client Secret
```python
{
    "name": "Azure Service Principal Client Secret",
    "pattern": r"(?:AZURE_CLIENT_SECRET|ClientSecret)['\"\s:=]+[A-Za-z0-9~._-]{34,40}",
    "severity": "CRITICAL",
    "context": [".env", "appsettings.json", "azure-pipelines.yml"],
    "example": "AZURE_CLIENT_SECRET=abc~123.def456-ghi_789",
    "note": "Used for Azure AD authentication"
}
```

### Azure DevOps Personal Access Token
```python
{
    "name": "Azure DevOps PAT",
    "pattern": r"(?:AZURE_DEVOPS_PAT|ADO_PAT|SYSTEM_ACCESSTOKEN)['\"\s:=]+[A-Za-z0-9]{52}",
    "severity": "CRITICAL",
    "context": [".env", "azure-pipelines.yml"],
    "example": "AZURE_DEVOPS_PAT=abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmn",
    "note": "Grants full access to Azure DevOps resources"
}
```

### Azure Storage Account Key
```python
{
    "name": "Azure Storage Account Key",
    "pattern": r"(?:AccountKey|AZURE_STORAGE_KEY)['\"\s:=]+[A-Za-z0-9+/=]{88}",
    "severity": "CRITICAL",
    "context": ["appsettings.json", ".env"],
    "example": "AZURE_STORAGE_KEY=abc123...xyz789=="
}
```

### Azure Cosmos DB Key
```python
{
    "name": "Azure Cosmos DB Key",
    "pattern": r"AccountEndpoint=https://[^;]+;AccountKey=([A-Za-z0-9+/=]{88})",
    "severity": "CRITICAL",
    "context": ["appsettings.json", ".env"],
    "example": "AccountEndpoint=https://mydb.documents.azure.com:443/;AccountKey=abc123...=="
}
```

### Azure Service Bus Connection String
```python
{
    "name": "Azure Service Bus Connection String",
    "pattern": r"Endpoint=sb://[^;]+;SharedAccessKeyName=[^;]+;SharedAccessKey=([A-Za-z0-9+/=]{43,})",
    "severity": "CRITICAL",
    "context": ["appsettings.json", ".env"],
    "example": "Endpoint=sb://mybus.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=abc123..."
}
```

### Azure Event Hub Connection String
```python
{
    "name": "Azure Event Hub Connection String",
    "pattern": r"Endpoint=sb://[^;]+\.servicebus\.windows\.net/;.*SharedAccessKey=([A-Za-z0-9+/=]{43,})",
    "severity": "CRITICAL",
    "context": ["appsettings.json", ".env"],
    "example": "Endpoint=sb://myhub.servicebus.windows.net/;EntityPath=myevent;SharedAccessKey=abc123..."
}
```

### Azure Redis Cache Connection String
```python
{
    "name": "Azure Redis Cache Connection String",
    "pattern": r"[a-z0-9-]+\.redis\.cache\.windows\.net[^,]*,password=([^,\"']+)",
    "severity": "HIGH",
    "context": ["appsettings.json", ".env"],
    "example": "myredis.redis.cache.windows.net:6380,password=MyRedisP@ss123,ssl=True"
}
```

### Azure Application Insights Instrumentation Key
```python
{
    "name": "Azure Application Insights Key",
    "pattern": r"(?:InstrumentationKey|APPINSIGHTS_INSTRUMENTATIONKEY)['\"\s:=]+[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}",
    "severity": "MEDIUM",
    "context": ["appsettings.json", ".env", "ApplicationInsights.config"],
    "example": "APPINSIGHTS_INSTRUMENTATIONKEY=12345678-1234-1234-1234-123456789012",
    "note": "Lower severity as it's for telemetry, but should still be protected"
}
```

### Azure Container Registry Password
```python
{
    "name": "Azure Container Registry Password",
    "pattern": r"(?:ACR_PASSWORD|acrPassword)['\"\s:=]+[A-Za-z0-9+/=]{43,}",
    "severity": "CRITICAL",
    "context": [".env", "docker-compose.yml", "azure-pipelines.yml"],
    "example": "ACR_PASSWORD=abc123def456ghi789..."
}
```

### Azure Functions Host Key
```python
{
    "name": "Azure Functions Host Key",
    "pattern": r"x-functions-key['\"\s:=]+[A-Za-z0-9_-]{52,}",
    "severity": "HIGH",
    "context": ["local.settings.json", ".env", "HTTP headers"],
    "example": "x-functions-key=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz"
}
```

### Azure App Services Publishing Password
```python
{
    "name": "Azure App Services Publishing Password",
    "pattern": r"<publishProfile.*userName=\"([^\"]+)\".*userPWD=\"([^\"]+)\"",
    "severity": "CRITICAL",
    "context": [".pubxml", "publish profiles"],
    "example": "<publishProfile userName=\"$myapp\" userPWD=\"MyP@ssw0rd123\"",
    "note": "Publishing profiles should never be committed"
}
```

### Azure Key Vault Secret URL (Hardcoded Version)
```python
{
    "name": "Azure Key Vault Secret (hardcoded version)",
    "pattern": r"https://[a-z0-9-]+\.vault\.azure\.net/secrets/[^/]+/([a-f0-9]{32})",
    "severity": "HIGH",
    "context": ["Any file"],
    "warning": "Secret version should not be hardcoded - use versionless URL",
    "example": "https://myvault.vault.azure.net/secrets/MySecret/abc123def456..."
}
```

---

## Docker Specific Patterns

### Docker Hub Access Token
```python
{
    "name": "Docker Hub Access Token",
    "pattern": r"(?:DOCKER_HUB_TOKEN|DOCKERHUB_TOKEN)['\"\s:=]+[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}",
    "severity": "CRITICAL",
    "context": [".env", "docker-compose.yml", ".github/workflows"],
    "example": "DOCKER_HUB_TOKEN=12345678-1234-1234-1234-123456789012"
}
```

### Docker Registry Password
```python
{
    "name": "Docker Registry Password",
    "pattern": r"(?:DOCKER_PASSWORD|REGISTRY_PASSWORD)['\"\s:=]+[^\s\"']{8,}",
    "severity": "CRITICAL",
    "context": [".env", "docker-compose.yml", "Dockerfile"],
    "example": "DOCKER_PASSWORD=MyDockerP@ss123",
    "note": "Used for docker login to private registries"
}
```

### Docker Compose Environment Secret
```python
{
    "name": "Docker Compose Environment Secret",
    "pattern": r"environment:\s*(?:\n\s+)?(?:.*\n\s+)*?[A-Z_]+(?:PASSWORD|SECRET|KEY|TOKEN):\s*['\"]?([^'\"\s]{8,})['\"]?",
    "severity": "HIGH",
    "context": ["docker-compose.yml"],
    "warning": "Use docker secrets or .env file instead of hardcoding",
    "example": "environment:\n  DB_PASSWORD: MyP@ssw0rd123"
}
```

### Dockerfile ARG with Secret
```python
{
    "name": "Dockerfile ARG with Secret",
    "pattern": r"ARG\s+(?:PASSWORD|SECRET|TOKEN|KEY|API_KEY)=([^\s]+)",
    "severity": "HIGH",
    "context": ["Dockerfile"],
    "warning": "ARG values are visible in docker history - use build secrets instead",
    "example": "ARG API_KEY=sk_live_abc123"
}
```

### Dockerfile ENV with Secret
```python
{
    "name": "Dockerfile ENV with Secret",
    "pattern": r"ENV\s+(?:PASSWORD|SECRET|TOKEN|KEY|API_KEY)\s*=?\s*([^\s]+)",
    "severity": "HIGH",
    "context": ["Dockerfile"],
    "warning": "ENV values are visible in docker inspect - use runtime secrets",
    "example": "ENV DATABASE_PASSWORD=MyP@ss123"
}
```

### Harbor Registry Password
```python
{
    "name": "Harbor Registry Password",
    "pattern": r"harbor[_-]?password['\"\s:=]+[^\s\"']{8,}",
    "severity": "CRITICAL",
    "context": [".env", "docker-compose.yml"],
    "example": "HARBOR_PASSWORD=MyHarborP@ss123"
}
```

### Docker Config.json Auth
```python
{
    "name": "Docker Config Auth Token",
    "pattern": r"\"auth\":\s*\"([A-Za-z0-9+/=]{20,})\"",
    "severity": "CRITICAL",
    "context": [".docker/config.json", "config.json"],
    "example": "\"auth\": \"dXNlcm5hbWU6cGFzc3dvcmQ=\"",
    "note": "Base64 encoded username:password"
}
```

---

## Next.js / Vite Specific Patterns

### NEXT_PUBLIC_ with Sensitive Data
```python
{
    "name": "NEXT_PUBLIC with API Key",
    "pattern": r"NEXT_PUBLIC_[A-Z_]*(?:API|SECRET|KEY|TOKEN)['\"\s:=]+[A-Za-z0-9+/=-]{20,}",
    "severity": "HIGH",
    "context": [".env.local", ".env.production"],
    "warning": "NEXT_PUBLIC_ vars are exposed to browser - should not contain secrets",
    "example": "NEXT_PUBLIC_API_SECRET=sk_live_abc123"
}
```

### VITE_ with Sensitive Data
```python
{
    "name": "VITE with API Key",
    "pattern": r"VITE_[A-Z_]*(?:API|SECRET|KEY|TOKEN)['\"\s:=]+[A-Za-z0-9+/=-]{20,}",
    "severity": "HIGH",
    "context": [".env", ".env.production"],
    "warning": "VITE_ vars are exposed to browser - should not contain secrets",
    "example": "VITE_API_KEY=pk_live_xyz789"
}
```

### Vercel Deployment Token
```python
{
    "name": "Vercel Token",
    "pattern": r"vercel[_-]?token['\"\s:=]+[A-Za-z0-9]{24}",
    "severity": "CRITICAL",
    "context": [".vercel/", ".env"],
    "example": "VERCEL_TOKEN=abc123def456ghi789xyz"
}
```

### Next.js API Route Secret
```python
{
    "name": "Next.js API Secret",
    "pattern": r"(?:NEXTAUTH_SECRET|API_SECRET|APP_SECRET)['\"\s:=]+[A-Za-z0-9+/=-]{32,}",
    "severity": "CRITICAL",
    "context": [".env.local", "next.config.js"],
    "example": "NEXTAUTH_SECRET=your-super-secret-key-here"
}
```

### Vite Build-time Secret Injection
```python
{
    "name": "Vite Config Secret",
    "pattern": r"define:\s*\{[^}]*(?:API|SECRET|KEY)['\"]:\s*['\"]([A-Za-z0-9+/=-]{20,})['\"]",
    "severity": "HIGH",
    "context": ["vite.config.js", "vite.config.ts"],
    "example": "define: { API_KEY: 'sk_live_abc123' }"
}
```

---

## .NET / ABP Specific Patterns

### SQL Server Connection String
```python
{
    "name": "SQL Server Connection String",
    "pattern": r"(?:Server|Data Source)=[^;]+;(?:Database|Initial Catalog)=[^;]+;(?:User ID|UID)=([^;]+);(?:Password|PWD)=([^;]+)",
    "severity": "CRITICAL",
    "context": ["appsettings.json", "Web.config", "connectionStrings"],
    "example": "Server=myserver;Database=mydb;User ID=sa;Password=MyP@ssw0rd"
}
```

### Entity Framework Connection String
```python
{
    "name": "EF Connection String with Password",
    "pattern": r"ConnectionStrings['\"\s:]*\{[^}]*['\"](?:Default|[A-Za-z]+)['\"]:\s*['\"].*Password=([^;\"']+)",
    "severity": "CRITICAL",
    "context": ["appsettings.json", "appsettings.Production.json"],
    "example": "\"ConnectionStrings\": { \"Default\": \"Server=...;Password=secret\" }"
}
```

### ABP License Code
```python
{
    "name": "ABP License Code",
    "pattern": r"AbpLicenseCode['\"\s:=]+[A-Za-z0-9+/=-]{50,}",
    "severity": "MEDIUM",
    "context": ["appsettings.json", "*.csproj"],
    "note": "Should use User Secrets, not committed",
    "example": "\"AbpLicenseCode\": \"ABC123-DEF456-...\""
}
```

### IdentityServer Client Secret
```python
{
    "name": "IdentityServer Client Secret",
    "pattern": r"ClientSecrets['\"\s:]*\[[^\]]*Value['\"\s:]*['\"]([A-Za-z0-9+/=-]{16,})['\"]",
    "severity": "CRITICAL",
    "context": ["appsettings.json", "IdentityServerConfig.cs"],
    "example": "ClientSecrets = { new Secret(\"my-secret\".Sha256()) }"
}
```

### JWT Signing Key
```python
{
    "name": "JWT Signing Key (.NET)",
    "pattern": r"(?:JwtBearer|Jwt).*['\"](?:Secret|SigningKey|IssuerSigningKey)['\"]:\s*['\"]([A-Za-z0-9+/=-]{32,})['\"]",
    "severity": "CRITICAL",
    "context": ["appsettings.json", "Startup.cs"],
    "example": "\"Jwt\": { \"Secret\": \"your-256-bit-secret-key-here\" }"
}
```

### Redis Connection String with Password
```python
{
    "name": "Redis Connection with Password",
    "pattern": r"(?:localhost|[0-9.]+|[a-z0-9.-]+):\d+,password=([^,\s\"']+)",
    "severity": "HIGH",
    "context": ["appsettings.json", "Redis configuration"],
    "example": "\"Redis\": { \"Configuration\": \"localhost:6379,password=myRedisPass\" }"
}
```

### ABP Encryption Key
```python
{
    "name": "ABP Encryption String Encryption Key",
    "pattern": r"StringEncryption['\"\s:]*\{[^}]*['\"]DefaultPassPhrase['\"]:\s*['\"]([^\"']+)['\"]",
    "severity": "HIGH",
    "context": ["appsettings.json"],
    "example": "\"StringEncryption\": { \"DefaultPassPhrase\": \"myEncryptionKey123\" }"
}
```

### ASP.NET Core Data Protection Key
```python
{
    "name": "Data Protection Key",
    "pattern": r"DataProtection['\"\s:]*\{[^}]*['\"](?:Key|ApplicationName)['\"]:\s*['\"]([^\"']+)['\"]",
    "severity": "MEDIUM",
    "context": ["appsettings.json"],
    "example": "\"DataProtection\": { \"ApplicationName\": \"MyApp\", \"Key\": \"mykey\" }"
}
```

### SMTP Credentials
```python
{
    "name": "SMTP Password",
    "pattern": r"Smtp['\"\s:]*\{[^}]*['\"](?:Password|UserName)['\"]:\s*['\"]([^\"']{8,})['\"]",
    "severity": "HIGH",
    "context": ["appsettings.json", "EmailSettings"],
    "example": "\"Smtp\": { \"UserName\": \"user\", \"Password\": \"myEmailPass\" }"
}
```

### Azure KeyVault Credentials
```python
{
    "name": "Azure KeyVault Secret",
    "pattern": r"(?:KeyVault|AzureKeyVault)['\"\s:]*\{[^}]*['\"](?:ClientSecret|TenantId|ClientId)['\"]:\s*['\"]([A-Za-z0-9-]{32,})['\"]",
    "severity": "CRITICAL",
    "context": ["appsettings.json"],
    "example": "\"AzureKeyVault\": { \"ClientSecret\": \"abc-123-def\" }"
}
```

---

## Generic Patterns (All Frameworks)

### Private Keys
```python
{
    "name": "RSA Private Key",
    "pattern": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "severity": "CRITICAL",
    "context": ["Any file - should never be committed"],
    "example": "-----BEGIN RSA PRIVATE KEY-----"
}
```

### JWT Token
```python
{
    "name": "JWT Token",
    "pattern": r"eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",
    "severity": "HIGH",
    "context": [".env", "config files", "test files"],
    "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
}
```

### Generic API Key
```python
{
    "name": "Generic API Key",
    "pattern": r"(?:api[_-]?key|apikey|api[_-]?secret)['\"\s:=]+([A-Za-z0-9_-]{20,})",
    "severity": "HIGH",
    "context": [".env", "config files"],
    "example": "API_KEY=sk_live_abc123def456xyz789"
}
```

### Password in Variable
```python
{
    "name": "Password Variable",
    "pattern": r"(?:password|passwd|pwd)['\"\s:=]+['\"]?([^'\"\s]{8,})['\"]?",
    "severity": "HIGH",
    "context": ["Any config file"],
    "validation": "Check if not placeholder",
    "example": "password=MySecureP@ssw0rd123"
}
```

### Database URL with Credentials
```python
{
    "name": "Database URL with Password",
    "pattern": r"(?:postgres|mysql|mongodb(?:\+srv)?)://[a-zA-Z0-9_-]+:([^@\s]+)@",
    "severity": "CRITICAL",
    "context": [".env", "DATABASE_URL"],
    "example": "postgresql://user:password123@localhost:5432/dbname"
}
```

### Bearer Token
```python
{
    "name": "Bearer Token",
    "pattern": r"Bearer\s+[A-Za-z0-9_-]{20,}",
    "severity": "HIGH",
    "context": ["HTTP headers in code", "test files"],
    "example": "Authorization: Bearer abc123def456..."
}
```

### Slack Webhook
```python
{
    "name": "Slack Webhook",
    "pattern": r"https://hooks\.slack\.com/services/T[A-Z0-9]{8,}/B[A-Z0-9]{8,}/[A-Za-z0-9]{24}",
    "severity": "MEDIUM",
    "context": [".env", "notification configs"],
    "example": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
}
```

### GitHub Personal Access Token
```python
{
    "name": "GitHub Token",
    "pattern": r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}",
    "severity": "CRITICAL",
    "context": [".env", "CI/CD configs"],
    "example": "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
}
```

### Stripe API Key
```python
{
    "name": "Stripe API Key",
    "pattern": r"(?:sk|pk)_(?:live|test)_[0-9a-zA-Z]{24,}",
    "severity": "CRITICAL",
    "context": [".env", "payment configs"],
    "example": "sk_live_4eC39HqLyjWDarjtT1zdp7dc"
}
```

### SendGrid API Key
```python
{
    "name": "SendGrid API Key",
    "pattern": r"SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}",
    "severity": "HIGH",
    "context": [".env", "appsettings.json"],
    "example": "SG.abc123def456...xyz789"
}
```

### Mailgun API Key
```python
{
    "name": "Mailgun API Key",
    "pattern": r"key-[0-9a-zA-Z]{32}",
    "severity": "HIGH",
    "context": [".env", "email configs"],
    "example": "key-abc123def456ghi789jkl012"
}
```

### Twilio API Key
```python
{
    "name": "Twilio API Key",
    "pattern": r"SK[0-9a-fA-F]{32}",
    "severity": "HIGH",
    "context": [".env", "SMS configs"],
    "example": "SK1234567890abcdef1234567890abcdef"
}
```

---

## CI/CD Specific Patterns

### GitHub Actions Secret
```python
{
    "name": "GitHub Actions Secret Reference",
    "pattern": r"\$\{\{\s*secrets\.[A-Z_]+\s*\}\}",
    "severity": "INFO",
    "context": [".github/workflows/*.yml"],
    "note": "Reference is OK, hardcoded value is not",
    "example": "${{ secrets.API_KEY }}"
}
```

### GitLab CI Variable
```python
{
    "name": "GitLab CI Hardcoded Secret",
    "pattern": r"(?:variables|environment):\s*\n\s+[A-Z_]+:\s*['\"]?([A-Za-z0-9+/=-]{20,})['\"]?",
    "severity": "HIGH",
    "context": [".gitlab-ci.yml"],
    "note": "Should use GitLab CI/CD variables instead",
    "example": "variables:\n  API_KEY: sk_live_abc123"
}
```

### Azure DevOps Pipeline Secret
```python
{
    "name": "Azure Pipeline Secret",
    "pattern": r"\$\(([A-Z_]+)\)",
    "severity": "INFO",
    "context": ["azure-pipelines.yml"],
    "note": "Variable reference - check if properly configured",
    "example": "$(MY_SECRET)"
}
```

---

## File-Specific Patterns

### Docker Secrets
```python
{
    "name": "Docker ARG with Secret",
    "pattern": r"ARG\s+(?:API_KEY|SECRET|PASSWORD|TOKEN)=([^\s]+)",
    "severity": "HIGH",
    "context": ["Dockerfile"],
    "warning": "ARG values visible in image history",
    "example": "ARG API_KEY=sk_live_abc123"
}
```

### NPM Token
```python
{
    "name": "NPM Auth Token",
    "pattern": r"//registry\.npmjs\.org/:_authToken=([A-Za-z0-9-_]+)",
    "severity": "CRITICAL",
    "context": [".npmrc"],
    "example": "//registry.npmjs.org/:_authToken=abc123-def456-..."
}
```

### NuGet API Key
```python
{
    "name": "NuGet API Key",
    "pattern": r"<add\s+key=['\"]apiKey['\"]\s+value=['\"]([A-Za-z0-9-]+)['\"]",
    "severity": "HIGH",
    "context": ["NuGet.Config"],
    "example": "<add key=\"apiKey\" value=\"oy2abc123def456...\" />"
}
```

---

## Placeholder Detection Patterns

### Common Placeholder Terms
```python
PLACEHOLDER_TERMS = [
    "example", "sample", "test", "demo", "placeholder", "changeme",
    "your_", "my_", "xxx", "todo", "replace", "insert", "enter",
    "fake", "dummy", "mock", "default", "temp", "temporary",
    "12345", "abcde", "secret", "password", "token", "key"
]
```

### Format Placeholders
```python
FORMAT_PLACEHOLDERS = [
    r"<[A-Z_]+>",                    # <YOUR_API_KEY>
    r"\{[A-Z_]+\}",                  # {API_KEY}
    r"\$\{[A-Z_]+\}",                # ${API_KEY}
    r"\[[A-Z_]+\]",                  # [API_KEY]
    r"\.\.\.+",                      # ...
    r"\*\*\*+",                      # ***
    r"xxx+",                         # xxx
    r"000+",                         # 000
    r"123456+",                      # 123456
]
```

### Entropy Thresholds
```python
ENTROPY_THRESHOLDS = {
    "low": 2.5,      # Likely placeholder (e.g., "password", "123456")
    "medium": 3.5,   # Possibly real (e.g., "mypassword123")
    "high": 4.5      # Likely real secret (e.g., random alphanumeric)
}
```

---

## Severity Assignment Logic

### CRITICAL
- Cloud provider credentials (AWS, Azure, GCP)
- Database connection strings with passwords
- Private cryptographic keys
- Production API keys (Stripe live, payment gateways)
- OAuth client secrets
- IdentityServer secrets

### HIGH
- Generic API keys (20+ characters, high entropy)
- SMTP credentials
- Redis passwords
- GitHub tokens
- Email service API keys
- Public environment variables with sensitive data

### MEDIUM
- ABP license codes (should be in User Secrets)
- Slack webhooks
- Development/test tokens
- Data protection keys
- Commented-out credentials

### LOW / INFO
- Variable references (`${{ secrets.X }}`)
- Obvious placeholders
- Documentation examples
- Empty or null values

---

## Special Considerations

### Next.js/Vite Public Variables
Variables prefixed with `NEXT_PUBLIC_` or `VITE_` are **always exposed to the browser**. Any secret-like pattern in these should be flagged as **HIGH severity** even if the key name suggests it's public.

Example of dangerous pattern:
```bash
NEXT_PUBLIC_STRIPE_SECRET_KEY=sk_live_abc123  # ❌ CRITICAL - exposed to browser!
```

### .NET User Secrets
If scanning detects secrets in `appsettings.json` but the project has `UserSecretsId` in `.csproj`, recommend migrating:

```bash
dotnet user-secrets set "ConnectionStrings:Default" "Server=...;Password=xyz"
```

### ABP Multi-Tenancy
ABP projects may have tenant-specific connection strings. Scan all `appsettings.{tenant}.json` files and tenant configuration sections.

---

## Exclusion Patterns

### Files to Always Skip
- `node_modules/`
- `bin/`, `obj/` (.NET build outputs)
- `.git/` (scanned separately by git history tool)
- `dist/`, `build/`, `.next/` (build artifacts - scan with caution)
- `*.min.js`, `*.bundle.js` (minified - too many false positives)
- Test files with `// @ts-ignore` or `/* eslint-disable */` (may contain mock data)

### Context-Aware Exclusions
- Comments containing URLs to documentation (often have example keys)
- README.md sections showing "Example configuration"
- Test fixtures with `__mocks__` or `fixtures` in path
- Migration files with sample data

---

## Validation Rules

### Rule 1: Entropy Check
Calculate Shannon entropy. If < 2.5 bits, likely placeholder.

### Rule 2: Placeholder Term Match
If value contains any term from `PLACEHOLDER_TERMS`, downgrade severity to INFO.

### Rule 3: Format Check
If value matches `FORMAT_PLACEHOLDERS` regex, mark as placeholder.

### Rule 4: Length Check
- Very short (< 8 chars): Likely placeholder
- Very long (> 200 chars): Validate format (JWT, Base64, etc.)

### Rule 5: Context Check
If found in:
- `*.test.js`, `*.spec.ts`: Downgrade severity (likely test data)
- `.example` files: Mark as INFO (intentional example)
- Comments: MEDIUM (may indicate real value nearby)

### Rule 6: Common Examples
Maintain database of known example values from official docs:
- AWS: `AKIAIOSFODNN7EXAMPLE`
- Stripe: `sk_test_4eC39HqLyjWDarjtT1zdp7dc`
- Google: `AIzaSyDaGmWKa4JsXZ-HjGw7ISLn_3namBGewQe` (docs example)

---

## Performance Optimization

### Compiled Regex
Pre-compile all regex patterns at script initialization for 3-5x speedup.

### Parallel Scanning
Use multiprocessing to scan files in parallel. Recommended: `cpu_count() - 1` processes.

### Smart File Reading
- Detect binary files by reading first 8192 bytes
- Skip files > 10MB (likely binary or generated)
- Use buffered reading for large files

### Incremental Scanning
Cache file hashes. On subsequent scans, skip unchanged files.

---

## Updates & Maintenance

**Pattern updates:**
- Review quarterly for new cloud providers
- Monitor security blogs for new secret types
- Update placeholder database from user feedback

**Version tracking:**
This patterns file: v1.0.0 (2025-01)
