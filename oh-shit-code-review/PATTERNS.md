# Detection Patterns

Critical issue detection patterns for Next.js and .NET C# (ABP Framework) code reviews.

## Next.js Critical Patterns

### Security Vulnerabilities

#### Hardcoded Secrets (Client Code)

**Ripgrep patterns for client-side code**:

```bash
# API keys and tokens
rg -n "apiKey\s*[:=]\s*['\"][a-zA-Z0-9_-]{20,}" -t typescript -t js
rg -n "api_key\s*[:=]\s*['\"][a-zA-Z0-9_-]{20,}" -t typescript -t js
rg -n "token\s*[:=]\s*['\"][a-zA-Z0-9_-]{20,}" -t typescript -t js
rg -n "Bearer\s+[a-zA-Z0-9_-]{20,}" -t typescript -t js

# AWS/GCP/Azure keys
rg -n "AKIA[0-9A-Z]{16}" -t typescript -t js
rg -n "AIza[0-9A-Za-z\\-_]{35}" -t typescript -t js

# Stripe keys
rg -n "sk_live_[0-9a-zA-Z]{24,}" -t typescript -t js
rg -n "pk_live_[0-9a-zA-Z]{24,}" -t typescript -t js
```

**Validation**: Check if in client component (`'use client'` directive) or imported by client component.

#### Dangerous HTML Injection

```bash
# dangerouslySetInnerHTML without sanitization
rg -n "dangerouslySetInnerHTML" -t typescript -g "*.tsx" -g "*.jsx"
```

**Validation**:

- Check if DOMPurify or similar sanitizer is imported and used
- Check if content is from trusted static source
- If neither, mark as CRITICAL with confidence 100

#### eval() and Function() Constructor

```bash
# Dangerous code execution
rg -n "\beval\s*\(" -t typescript -t js
rg -n "new\s+Function\s*\(" -t typescript -t js
```

**Validation**: Always CRITICAL unless in build scripts or dev-only code.

#### Disabled Security Headers

```bash
# In next.config.js/ts
rg -n "contentSecurityPolicy\s*:\s*false" -g "next.config.*"
rg -n "X-Frame-Options.*false" -g "next.config.*"
rg -n "X-Content-Type-Options.*false" -g "next.config.*"
rg -n "Strict-Transport-Security.*false" -g "next.config.*"
```

**Validation**: Check if there's a comment explaining why (still flag but lower confidence).

### Breaking Changes

#### Deleted/Renamed API Routes

**Detection approach**:

1. Get list of deleted files: `git diff --diff-filter=D --name-only`
2. Check if any match: `*/api/**/*.ts`, `*/api/**/*.js`
3. For each deleted API route, mark as CRITICAL breaking change

#### Changed Route Parameters

```bash
# Look for changes in dynamic route segments
git diff | rg "(\[.*\]|\{.*\})" -g "**/app/**" -g "**/pages/**"
```

**Validation**:

- Check if parameter name changed: `[id]` → `[userId]`
- Check if parameter type changed: `[id]` → `[...id]`
- If changed, mark as CRITICAL breaking change

#### Removed Environment Variables

**Detection approach**:

1. Get all removed env var references: `git diff | rg "^-.*process\.env\." `
2. Check if other services might depend on these
3. If in shared config/constants, mark as HIGH severity

### Data Leaks

#### Server Secrets in Client Components

```bash
# Find 'use client' files
rg -l "'use client'" -t typescript -g "*.tsx" -g "*.ts"

# Then check for process.env usage in those files
rg -n "process\.env\." <client-component-files>
```

**Validation**:

- If env var is `NEXT_PUBLIC_*`, it's safe
- Otherwise, CRITICAL data leak (confidence 100)

#### Database Queries in Client Components

```bash
# Find 'use client' files with database imports
rg -l "'use client'" -t typescript -g "*.tsx" -g "*.ts" | xargs rg -l "from.*(prisma|db|database)"
```

**Validation**: Always CRITICAL if client component imports database client.

#### Exposed Secrets in getStaticProps/getServerSideProps

```bash
# Find these functions returning secrets
rg -A 20 "export.*(getStaticProps|getServerSideProps)" -t typescript -g "*.tsx" -g "*.ts" | rg "process\.env\." | rg -v "NEXT_PUBLIC_"
```

**Validation**: Check if env var is returned in props object.

#### Server Actions Without Validation (Next.js 13+)

```bash
# Server Actions without input validation
rg -l "'use server'" -t typescript -g "*.ts" -g "*.tsx" | xargs rg -B 2 -A 10 "export async function" | rg -v "(zod|yup|validate|schema|joi)"
```

**Validation**:

- Check if Server Action accepts user input
- Verify input validation library is used (Zod, Yup, etc.)
- If no validation found, CRITICAL (confidence 90)

**Why critical**: Server Actions execute on the server with direct database access. Missing validation = SQL injection, unauthorized access, data corruption.

#### Middleware Bypass

```bash
# Check middleware config matches all routes
rg "export.*config.*matcher" -t typescript -g "middleware.ts" -A 5

# Find API routes not covered by middleware
find app pages -name "route.ts" -o -name "*.tsx" | rg "/api/" | sort > /tmp/api-routes.txt
# Manually compare with middleware matcher patterns
```

**Validation**:

- Extract all API routes from file structure
- Compare with middleware matcher array
- If API route missing from matcher, HIGH severity
- Critical for: auth routes, payment endpoints, admin panels

**Why critical**: Middleware bypass = authentication/authorization skipped entirely.

#### Dynamic Imports Leaking Server Code

```bash
# Dynamic imports without ssr: false
rg "dynamic\(\(\) => import\(" -t typescript -g "*.tsx" -g "*.ts" | rg -v "ssr:\s*false"
```

**Validation**:

- Check if imported component uses server-only code
- Check if `ssr: false` option is set
- If server code without ssr:false, HIGH severity

**Why critical**: Can leak environment variables, database queries, API keys to client bundle.

### Environment Files

#### .env Files with Real Secrets

**Detection approach**:

1. Check if `.env`, `.env.local`, `.env.production` added to git: `git diff --name-only | rg "^\.env"`
2. If found, scan content for actual secrets (not placeholder values)

```bash
# Pattern for real secrets (not placeholders)
rg -n "=.{20,}" .env .env.local .env.production 2>/dev/null | rg -v "(your-.*-here|xxx|example|placeholder)"
```

**Validation**:

- If value looks like real secret (long random string), CRITICAL
- If value is "change-me" or similar, LOW confidence

---

## .NET C# (ABP Framework) Critical Patterns

### Security Vulnerabilities

#### SQL Injection (String Concatenation)

```bash
# Dangerous SQL concatenation
rg -n "ExecuteSqlRaw.*(\$\"|\+)" -t cs
rg -n "FromSqlRaw.*(\$\"|\+)" -t cs
rg -n "(SELECT.*FROM|INSERT.*INTO).*\$\"" -t cs
```

**Validation**:

- Check if using parameterized queries or interpolated strings
- If string concatenation with user input, CRITICAL (confidence 100)

#### [AllowAnonymous] on Sensitive Endpoints

```bash
# Find [AllowAnonymous] attribute
rg -B 5 "\[AllowAnonymous\]" -t cs
```

**Validation**:

- Check method/class name for sensitive operations: `Payment`, `Admin`, `Delete`, `Update`, `User`
- Check if endpoint modifies data (POST/PUT/DELETE)
- If sensitive, CRITICAL (confidence 90)

#### Hardcoded Connection Strings

```bash
# Hardcoded credentials in connection strings
rg -n "Server=.*Password=|User Id=.*Password=" -t cs
rg -n "ConnectionString.*Password=" -g "appsettings*.json"
```

**Validation**:

- If in appsettings.json (not appsettings.Development.json), HIGH severity
- If in .cs files, CRITICAL severity

#### Disabled HTTPS

```bash
# HTTPS enforcement removed
rg -n "UseHttpsRedirection" -t cs
```

**Detection approach**: Use `git diff` to check if `UseHttpsRedirection()` was removed.

#### Raw Password Storage

```bash
# Password stored without hashing
rg -n "(Password|password)\s*=\s*" -t cs | rg -v "(Hash|Encrypt|BCrypt|PBKDF2)"
```

**Validation**: Check if password is being hashed before storage.

#### Disabled CSRF Protection

```bash
# CSRF validation disabled
rg -n "(ValidateAntiForgeryToken.*false|IgnoreAntiforgeryToken)" -t cs
```

**Validation**: Always HIGH severity for data-modifying endpoints.

#### Unvalidated File Uploads

```bash
# File upload without validation
rg -B 10 "IFormFile" -t cs | rg -v "(ContentType|Length|Extension)"
```

**Validation**: Check for file type validation, size limits, virus scanning.

### ABP Framework-Specific Issues

#### Bypassed Permission System

```bash
# Methods missing [Authorize] attribute
rg -B 5 "public.*Task<.*>.*Async" -g "*AppService.cs" | rg -v "\[Authorize"
```

**Validation**:

- Check if method modifies data or accesses sensitive info
- If yes and no `[Authorize]`, HIGH severity

#### Disabled Audit Logging

```bash
# [DisableAuditing] on sensitive operations
rg -B 3 "\[DisableAuditing\]" -t cs
```

**Validation**: Check if method handles sensitive operations (payment, user data, permissions).

#### Direct DbContext Usage Breaking Multi-Tenancy

```bash
# Direct DbContext usage instead of repository
rg -n "DbContext" -g "*AppService.cs" -g "*DomainService.cs"
```

**Validation**:

- AppServices should use repositories, not DbContext directly
- If DbContext used, check for `IMultiTenant` filtering
- If missing, HIGH severity (breaks multi-tenancy)

#### Missing [UnitOfWork]

```bash
# Methods with transactions but no [UnitOfWork]
rg -B 5 "public.*async.*Task" -g "*AppService.cs" | rg -v "\[UnitOfWork\]" | rg -A 10 "await.*SaveChanges"
```

**Validation**: If method has multiple SaveChanges or transaction logic, needs `[UnitOfWork]`.

### Breaking Changes

#### Deleted/Renamed DTOs

**Detection approach**:

1. Get deleted DTO files: `git diff --diff-filter=D --name-only | grep "Application.Contracts.*Dto.cs"`
2. Get renamed DTOs: `git diff | grep "^-.*class.*Dto" `
3. Each deleted/renamed DTO is a CRITICAL breaking change

#### Breaking Database Migrations

```bash
# Migrations dropping columns
rg -n "(DropColumn|DropTable)" -g "*Migrations/*.cs"
```

**Validation**:

- Check if there's data migration logic
- If no data migration before drop, CRITICAL breaking change

#### Removed Required Config Keys

**Detection approach**:

1. Get removed config lines: `git diff appsettings.json | grep "^-.*:"`
2. Check if key was required (referenced in code without null check)
3. If required, HIGH severity breaking change

#### Changed API Endpoints

```bash
# Changed route attributes
git diff | rg "^\-.*(\[HttpGet\]|\[HttpPost\]|Route)"
```

**Validation**: Any route or HTTP method change is a breaking change for API clients.

### Data Exposure

#### Removed Multi-Tenant Filtering

```bash
# IMultiTenant interface removed from entities
git diff | rg "^-.*: IMultiTenant"
```

**Validation**: CRITICAL - breaks tenant data isolation.

#### Exposed Internal DTOs

```bash
# Domain entities returned directly without DTO mapping
rg -n "return.*(entity|entities)" -g "*AppService.cs" | rg -v "ObjectMapper.Map"
```

**Validation**: Check if domain entity is returned instead of DTO.

#### Disabled Soft-Delete Filtering

```bash
# IgnoreQueryFilters usage
rg -n "IgnoreQueryFilters" -t cs
```

**Validation**: Check if this exposes deleted data to users.

#### Insecure Deserialization

```bash
# Unsafe deserialization patterns
rg -n "(JsonConvert\.DeserializeObject|BinaryFormatter\.Deserialize|XmlSerializer\.Deserialize)" -t cs | rg -v "TypeNameHandling\.None"
```

**Validation**:

- Check if `TypeNameHandling` is set to `None` for JSON.NET
- Check if custom type validation exists
- If deserializing untrusted data without validation, CRITICAL (confidence 95)

**Why critical**: Insecure deserialization = Remote Code Execution (RCE). Attacker can execute arbitrary code on server.

#### Missing Input Length Validation

```bash
# DTOs without MaxLength attribute
rg "public string.*\{\s*get;\s*set;\s*\}" -t cs -g "*Dto.cs" -g "Application.Contracts/**/*.cs" -A 1 | rg -v "(MaxLength|StringLength)"
```

**Validation**:

- Check if DTO string properties have length constraints
- Properties without limits can cause: database errors, DoS attacks, buffer overflows
- If public-facing DTO without limits, HIGH severity

**Why critical**: Missing length validation = DoS via large payloads, database column overflow errors in production.

#### Background Jobs Without Retry Logic

```bash
# Background jobs missing retry configuration
rg "\[BackgroundJob.*\]" -t cs -A 10 | rg -v "(MaxTryCount|RetryStrategy|BackgroundJobPriority)"
```

**Validation**:

- Check if background job has retry configuration
- Look for `MaxTryCount` or custom retry strategy
- If processing critical data (payments, notifications) without retry, HIGH severity

**Why critical**: Failed jobs without retry = data loss, incomplete transactions, angry customers. Especially critical for: payment processing, email sending, data synchronization.

---

## Pattern Matching Best Practices

### Avoid False Positives

1. **Read context**: Always read 5-10 lines before and after match
2. **Check file type**: Client vs server, production vs development
3. **Validate with git history**: New code vs pre-existing
4. **Framework conventions**: ABP/Next.js may have safe patterns

### Confidence Scoring Rules

**100 (Critical certainty)**:

- Hardcoded production credentials
- SQL injection with user input
- Secrets in client components
- [AllowAnonymous] on payment/admin endpoints

**90 (Very high confidence)**:

- Missing auth on sensitive endpoints
- Breaking changes in public DTOs
- Deleted API routes

**75 (High confidence - threshold for reporting)**:

- Potential data leaks (need validation)
- Possibly breaking changes
- Security headers disabled with no comment

**50 (Medium - DO NOT REPORT)**:

- Pattern matches but context unclear
- Might be safe framework pattern
- Need more investigation

**25 (Low - DO NOT REPORT)**:

- Weak pattern match
- Likely false positive
- Framework boilerplate

### Multi-Pattern Validation

Some issues require multiple patterns to confirm:

**Example: Server secret in client component**

1. Pattern 1: Find `'use client'` files
2. Pattern 2: Find `process.env` usage in those files
3. Pattern 3: Verify env var is NOT `NEXT_PUBLIC_*`
4. Result: If all 3 match, confidence = 100

### Exclusion Patterns

**Always exclude**:

- `node_modules/`, `bin/`, `obj/`, `dist/`, `build/`
- `*.test.ts`, `*.spec.ts` (unless security tests)
- `*.generated.cs`, `*.Designer.cs`
- Migration files (unless breaking)
- Example files, documentation

---

## Usage Examples

### Example 1: Scan Git Diff for Hardcoded Secrets

```bash
# Get diff
git diff --cached > /tmp/diff.txt

# Scan for API keys in Next.js files
rg -n "apiKey\s*[:=]\s*['\"][a-zA-Z0-9_-]{20,}" /tmp/diff.txt -g "*.{tsx,ts,jsx,js}"

# Validate each match
for match in $matches; do
  # Read file context
  # Check if in client component
  # Assign confidence score
  # If confidence >= 75, report
done
```

### Example 2: Detect Breaking API Changes

```bash
# Find deleted API routes
git diff --diff-filter=D --name-only | rg "/api/"

# Find renamed routes
git diff | rg "^-.*(\[HttpGet\]|Route)"

# For each change, check if public API
# If public, mark as CRITICAL breaking change
```

### Example 3: Multi-Tenant Filter Removal

```bash
# Find entities with removed IMultiTenant
git diff | rg "^-.*: IMultiTenant" -B 3

# Extract entity name
# Check impact (how widely used)
# Mark as CRITICAL with confidence 100
```

---

## Pattern Maintenance

### Adding New Patterns

When adding new detection patterns:

1. Test pattern on known true positives
2. Test pattern on known false positives
3. Document validation steps
4. Set appropriate confidence threshold
5. Add to this file with examples

### Pattern Performance

Optimize ripgrep patterns:

- Use `-t` (type) or `-g` (glob) to limit file types
- Avoid overly broad regex
- Combine patterns with alternation `(pattern1|pattern2)`
- Use `rg -l` first, then `rg -n` for matches
- Ripgrep is 30x faster than grep for large codebases

### Framework Updates

When Next.js or ABP Framework updates:

- Review changelog for new security features
- Update patterns for deprecated APIs
- Add patterns for new vulnerability types
- Test against new framework versions
