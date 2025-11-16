# Detection Patterns

Critical issue detection patterns for Next.js and .NET C# (ABP Framework) code reviews.

## Next.js Critical Patterns

### Security Vulnerabilities

#### Hardcoded Secrets (Client Code)

**Grep patterns for client-side code**:
```bash
# API keys and tokens
grep -n "apiKey\s*[:=]\s*['\"][a-zA-Z0-9_-]{20,}" --include="*.tsx" --include="*.ts" --include="*.jsx" --include="*.js"
grep -n "api_key\s*[:=]\s*['\"][a-zA-Z0-9_-]{20,}" --include="*.tsx" --include="*.ts" --include="*.jsx" --include="*.js"
grep -n "token\s*[:=]\s*['\"][a-zA-Z0-9_-]{20,}" --include="*.tsx" --include="*.ts" --include="*.jsx" --include="*.js"
grep -n "Bearer\s+[a-zA-Z0-9_-]{20,}" --include="*.tsx" --include="*.ts" --include="*.jsx" --include="*.js"

# AWS/GCP/Azure keys
grep -n "AKIA[0-9A-Z]{16}" --include="*.tsx" --include="*.ts" --include="*.jsx" --include="*.js"
grep -n "AIza[0-9A-Za-z\\-_]{35}" --include="*.tsx" --include="*.ts" --include="*.jsx" --include="*.js"

# Stripe keys
grep -n "sk_live_[0-9a-zA-Z]{24,}" --include="*.tsx" --include="*.ts" --include="*.jsx" --include="*.js"
grep -n "pk_live_[0-9a-zA-Z]{24,}" --include="*.tsx" --include="*.ts" --include="*.jsx" --include="*.js"
```

**Validation**: Check if in client component (`'use client'` directive) or imported by client component.

#### Dangerous HTML Injection

```bash
# dangerouslySetInnerHTML without sanitization
grep -n "dangerouslySetInnerHTML" --include="*.tsx" --include="*.jsx"
```

**Validation**:
- Check if DOMPurify or similar sanitizer is imported and used
- Check if content is from trusted static source
- If neither, mark as CRITICAL with confidence 100

#### eval() and Function() Constructor

```bash
# Dangerous code execution
grep -n "\beval\s*(" --include="*.tsx" --include="*.ts" --include="*.jsx" --include="*.js"
grep -n "new\s+Function\s*(" --include="*.tsx" --include="*.ts" --include="*.jsx" --include="*.js"
```

**Validation**: Always CRITICAL unless in build scripts or dev-only code.

#### Disabled Security Headers

```bash
# In next.config.js/ts
grep -n "contentSecurityPolicy\s*:\s*false" --include="next.config.*"
grep -n "X-Frame-Options.*false" --include="next.config.*"
grep -n "X-Content-Type-Options.*false" --include="next.config.*"
grep -n "Strict-Transport-Security.*false" --include="next.config.*"
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
git diff | grep -E "(\[.*\]|{.*})" --include="*/app/**" --include="*/pages/**"
```

**Validation**:
- Check if parameter name changed: `[id]` → `[userId]`
- Check if parameter type changed: `[id]` → `[...id]`
- If changed, mark as CRITICAL breaking change

#### Removed Environment Variables

**Detection approach**:
1. Get all removed env var references: `git diff | grep "^-.*process\.env\." `
2. Check if other services might depend on these
3. If in shared config/constants, mark as HIGH severity

### Data Leaks

#### Server Secrets in Client Components

```bash
# Find 'use client' files
grep -l "'use client'" --include="*.tsx" --include="*.ts"

# Then check for process.env usage in those files
grep -n "process\.env\." <client-component-files>
```

**Validation**:
- If env var is `NEXT_PUBLIC_*`, it's safe
- Otherwise, CRITICAL data leak (confidence 100)

#### Database Queries in Client Components

```bash
# Find 'use client' files with database imports
grep -l "'use client'" --include="*.tsx" --include="*.ts" | xargs grep -l "from.*prisma\|from.*db\|from.*database"
```

**Validation**: Always CRITICAL if client component imports database client.

#### Exposed Secrets in getStaticProps/getServerSideProps

```bash
# Find these functions returning secrets
grep -A 20 "export.*getStaticProps\|export.*getServerSideProps" --include="*.tsx" --include="*.ts" | grep "process\.env\." | grep -v "NEXT_PUBLIC_"
```

**Validation**: Check if env var is returned in props object.

### Environment Files

#### .env Files with Real Secrets

**Detection approach**:
1. Check if `.env`, `.env.local`, `.env.production` added to git: `git diff --name-only | grep "^\.env"`
2. If found, scan content for actual secrets (not placeholder values)

```bash
# Pattern for real secrets (not placeholders)
grep -n "=.{20,}" .env .env.local .env.production 2>/dev/null | grep -v "your-.*-here\|xxx\|example\|placeholder"
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
grep -n "ExecuteSqlRaw.*\$\"\|ExecuteSqlRaw.*\+" --include="*.cs"
grep -n "FromSqlRaw.*\$\"\|FromSqlRaw.*\+" --include="*.cs"
grep -n "SELECT.*FROM.*\$\"\|INSERT.*INTO.*\$\"" --include="*.cs"
```

**Validation**:
- Check if using parameterized queries or interpolated strings
- If string concatenation with user input, CRITICAL (confidence 100)

#### [AllowAnonymous] on Sensitive Endpoints

```bash
# Find [AllowAnonymous] attribute
grep -B 5 "\[AllowAnonymous\]" --include="*.cs"
```

**Validation**:
- Check method/class name for sensitive operations: `Payment`, `Admin`, `Delete`, `Update`, `User`
- Check if endpoint modifies data (POST/PUT/DELETE)
- If sensitive, CRITICAL (confidence 90)

#### Hardcoded Connection Strings

```bash
# Hardcoded credentials in connection strings
grep -n "Server=.*Password=\|User Id=.*Password=" --include="*.cs"
grep -n "ConnectionString.*Password=" --include="appsettings*.json"
```

**Validation**:
- If in appsettings.json (not appsettings.Development.json), HIGH severity
- If in .cs files, CRITICAL severity

#### Disabled HTTPS

```bash
# HTTPS enforcement removed
grep -n "UseHttpsRedirection" --include="*.cs"
```

**Detection approach**: Use `git diff` to check if `UseHttpsRedirection()` was removed.

#### Raw Password Storage

```bash
# Password stored without hashing
grep -n "Password\s*=\s*.*\|password\s*=\s*.*" --include="*.cs" | grep -v "Hash\|Encrypt\|BCrypt\|PBKDF2"
```

**Validation**: Check if password is being hashed before storage.

#### Disabled CSRF Protection

```bash
# CSRF validation disabled
grep -n "ValidateAntiForgeryToken.*false\|IgnoreAntiforgeryToken" --include="*.cs"
```

**Validation**: Always HIGH severity for data-modifying endpoints.

#### Unvalidated File Uploads

```bash
# File upload without validation
grep -B 10 "IFormFile" --include="*.cs" | grep -L "ContentType\|Length\|Extension"
```

**Validation**: Check for file type validation, size limits, virus scanning.

### ABP Framework-Specific Issues

#### Bypassed Permission System

```bash
# Methods missing [Authorize] attribute
grep -B 5 "public.*Task<.*>.*Async" --include="*AppService.cs" | grep -L "\[Authorize"
```

**Validation**:
- Check if method modifies data or accesses sensitive info
- If yes and no `[Authorize]`, HIGH severity

#### Disabled Audit Logging

```bash
# [DisableAuditing] on sensitive operations
grep -B 3 "\[DisableAuditing\]" --include="*.cs"
```

**Validation**: Check if method handles sensitive operations (payment, user data, permissions).

#### Direct DbContext Usage Breaking Multi-Tenancy

```bash
# Direct DbContext usage instead of repository
grep -n "DbContext" --include="*AppService.cs" --include="*DomainService.cs"
```

**Validation**:
- AppServices should use repositories, not DbContext directly
- If DbContext used, check for `IMultiTenant` filtering
- If missing, HIGH severity (breaks multi-tenancy)

#### Missing [UnitOfWork]

```bash
# Methods with transactions but no [UnitOfWork]
grep -B 5 "public.*async.*Task" --include="*AppService.cs" | grep -L "\[UnitOfWork\]" | grep -A 10 "await.*SaveChanges"
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
grep -n "DropColumn\|DropTable" --include="*Migrations/*.cs"
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
git diff | grep "^\-.*\[HttpGet\]\|^\-.*\[HttpPost\]\|^\-.*Route"
```

**Validation**: Any route or HTTP method change is a breaking change for API clients.

### Data Exposure

#### Removed Multi-Tenant Filtering

```bash
# IMultiTenant interface removed from entities
git diff | grep "^-.*: IMultiTenant"
```

**Validation**: CRITICAL - breaks tenant data isolation.

#### Exposed Internal DTOs

```bash
# Domain entities returned directly without DTO mapping
grep -n "return.*entity\|return.*entities" --include="*AppService.cs" | grep -v "ObjectMapper.Map"
```

**Validation**: Check if domain entity is returned instead of DTO.

#### Disabled Soft-Delete Filtering

```bash
# IgnoreQueryFilters usage
grep -n "IgnoreQueryFilters" --include="*.cs"
```

**Validation**: Check if this exposes deleted data to users.

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
grep -n "apiKey\s*[:=]\s*['\"][a-zA-Z0-9_-]{20,}" /tmp/diff.txt | grep -E "\.(tsx|ts|jsx|js):"

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
git diff --diff-filter=D --name-only | grep "/api/"

# Find renamed routes
git diff | grep "^-.*\[HttpGet\]\|^-.*Route"

# For each change, check if public API
# If public, mark as CRITICAL breaking change
```

### Example 3: Multi-Tenant Filter Removal

```bash
# Find entities with removed IMultiTenant
git diff | grep "^-.*: IMultiTenant" -B 3

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

Optimize grep patterns:
- Use `--include` to limit file types
- Avoid overly broad regex
- Combine patterns when possible
- Use `grep -l` first, then `grep -n` for matches

### Framework Updates

When Next.js or ABP Framework updates:
- Review changelog for new security features
- Update patterns for deprecated APIs
- Add patterns for new vulnerability types
- Test against new framework versions
