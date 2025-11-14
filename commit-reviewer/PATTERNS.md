# Code Review Detection Patterns

This document contains grep patterns used by the Code Reviewer skill to detect security vulnerabilities, code quality issues, and anti-patterns.

## Security Vulnerabilities

### SQL Injection

**JavaScript/TypeScript:**
```
Grep patterns:
- "query.*=.*`.*\\$\\{" - Template literal SQL with interpolation
- "query.*\\+.*req\\." - String concatenation with request data
- "execute.*\\+.*params" - Query execution with concatenation
- "\\.query\\(.*\\+.*\\)" - Database query with concatenation
- "WHERE.*\\$\\{" - WHERE clause with template interpolation
```

**C#/.NET:**
```
Grep patterns:
- "SqlCommand.*\\+.*" - SQL command with string concatenation
- "ExecuteRaw.*\\+.*" - Raw SQL execution with concatenation
- "FromSqlRaw.*\\+.*" - Entity Framework raw SQL with concatenation
- "WHERE.*\\+.*" - WHERE clause concatenation
```

**Python:**
```
Grep patterns:
- "execute\\(f\"" - f-string in SQL execute
- "execute\\(.*\\+.*\\)" - String concatenation in execute
- "WHERE.*%s.*%.*" - Old-style string formatting in WHERE
```

### Cross-Site Scripting (XSS)

**JavaScript/TypeScript:**
```
Grep patterns:
- "\\.innerHTML.*=" - Direct innerHTML assignment
- "dangerouslySetInnerHTML" - React dangerous HTML
- "document\\.write" - Document write (dangerous)
- "\\.html\\(.*\\+.*\\)" - jQuery html with concatenation
- "eval\\(" - Eval usage (code injection)
- "Function\\(.*\\)" - Function constructor (code injection)
```

**React/Next.js specific:**
```
Grep patterns:
- "dangerouslySetInnerHTML.*\\{.*\\}" - Check if sanitized
- "<script.*\\{.*\\}.*</script>" - Script tags with variables
- "onClick.*=.*\\{.*eval" - Event handlers with eval
```

### Command Injection

**All languages:**
```
Grep patterns:
- "exec\\(.*\\+.*\\)" - Command execution with concatenation
- "spawn\\(.*\\+.*\\)" - Process spawn with concatenation
- "system\\(.*\\$" - System calls with variables
- "shell_exec" - Shell execution
- "passthru" - PHP passthru
- "Process\\.Start.*\\+.*" - C# process start with concatenation
```

### Path Traversal

```
Grep patterns:
- "readFile\\(.*\\+.*\\)" - File read with concatenation
- "writeFile\\(.*req\\." - File write with request data
- "\\..\\/\\.\\.\\/" - Literal path traversal in code
- "path.*\\+.*params" - Path construction with params
```

### Hardcoded Secrets

```
Grep patterns:
- "password.*=.*[\"'].*[\"']" - Hardcoded passwords
- "api[_-]?key.*=.*[\"'][A-Za-z0-9]{20,}" - API keys
- "secret.*=.*[\"'][A-Za-z0-9]{20,}" - Secrets
- "token.*=.*[\"'][A-Za-z0-9]{20,}" - Tokens
- "private[_-]?key.*=.*[\"']" - Private keys
- "connectionString.*Password=" - Connection strings with passwords
- "aws_secret_access_key" - AWS credentials
- "AKIA[0-9A-Z]{16}" - AWS access key pattern
```

### Authentication/Authorization

```
Grep patterns:
- "if.*role.*==.*[\"']admin" - Hardcoded role checks
- "isAuthenticated.*=.*true" - Hardcoded auth bypass
- "bypass.*auth" - Auth bypass comments/code
- "TODO.*security" - Security TODOs
- "FIXME.*auth" - Auth fixmes
```

### Insecure Cryptography

```
Grep patterns:
- "MD5\\(" - Weak hash (MD5)
- "SHA1\\(" - Weak hash (SHA-1)
- "DES\\(" - Weak encryption (DES)
- "ECB" - Weak cipher mode
- "Random\\(" - Weak random (not crypto-secure)
- "Math\\.random" - Non-cryptographic random
```

### CSRF Vulnerabilities

```
Grep patterns:
- "method.*POST.*cors.*\\*" - CORS wildcard on POST
- "csrf.*=.*false" - CSRF protection disabled
- "verify.*=.*false" - Verification disabled
```

## Code Quality Issues

### Error Handling

```
Grep patterns:
- "catch.*\\{\\s*\\}" - Empty catch blocks
- "catch.*console\\.log" - Catch with only console.log
- "catch.*\\(\\)" - Catch with empty handler
- "catch.*TODO" - TODO in catch block
- "catch.*pass" - Python empty except pass
- "throw new Error\\(\\)" - Error with no message
```

### Null Safety

**TypeScript/JavaScript:**
```
Grep patterns:
- "!.*\\." - Non-null assertion (be careful)
- "as any" - Type assertion to any
- "\\@ts-ignore" - TypeScript ignore
- "\\[0\\](?!\\s*\\?)" - Array access without optional chaining
```

**C#:**
```
Grep patterns:
- "!(?!.*null)" - Null-forgiving operator misuse
- "\\.Value(?!.*HasValue)" - Nullable .Value without check
```

### Async/Await Issues

**JavaScript/TypeScript:**
```
Grep patterns:
- "async.*forEach" - Async forEach (doesn't wait)
- "new Promise.*setTimeout" - Promise with setTimeout (use delay)
- "await.*await" - Double await
- "Promise\\.all.*forEach" - Should use map, not forEach
- "async.*\\{\\s*return(?!.*await)" - Async without await
```

**C#/.NET:**
```
Grep patterns:
- "\\.Result(?!.*await)" - Blocking on async (.Result)
- "\\.Wait\\(\\)(?!.*await)" - Blocking wait
- "async void(?!.*EventHandler)" - Async void (should be async Task)
- "Task\\.Run.*async" - Task.Run wrapping async
```

### Performance Issues

```
Grep patterns:
- "for.*length" - Loop without caching length
- "\\+.*=.*[\"'].*[\"']" - String concatenation in loop
- "SELECT \\*" - SELECT * (specify columns)
- "N\\+1" - N+1 query comment/pattern
- "ToList\\(\\)\\.Count" - ToList before Count (inefficient)
- "Any\\(\\).*Count" - Any when Count>0 better
```

### Code Duplication

```
Grep patterns:
- "TODO.*duplicate" - Duplicate code TODO
- "FIXME.*DRY" - DRY violation fixme
- "copy.*paste" - Copy-paste comments
```

### Magic Numbers

```
Grep patterns:
- "if.*>.*[0-9]{2,}" - Comparison with magic numbers
- "sleep\\([0-9]{4,}\\)" - Sleep with magic number
- "timeout.*[0-9]{4,}" - Timeout with magic number
```

## Best Practices Violations

### React/Next.js

```
Grep patterns:
- "useState.*\\[\\].*map" - Array state mutation
- "useEffect.*\\[\\].*set" - Missing dependencies
- "key.*=.*index" - Using index as key
- "onClick.*\\{.*\\(\\).*=>" - Creating functions in render
- "style.*\\{\\{" - Inline styles (consider CSS)
```

### TypeScript

```
Grep patterns:
- ": any" - Any type usage
- "as any" - Casting to any
- "\\@ts-expect-error" - TypeScript error suppression
- "\\@ts-nocheck" - TypeScript check disabled
```

### C#/.NET ABP Framework

```
Grep patterns:
- "new.*Repository" - Manual repository instantiation
- "DbContext.*new" - Manual DbContext creation
- "[Authorize].*AllowAnonymous" - Conflicting attributes
- "IRepository.*Delete" - Direct delete (use soft delete)
```

### General OOP

```
Grep patterns:
- "class.*\\{[\\s\\S]{2000,}\\}" - Large classes (>2000 chars)
- "function.*\\{[\\s\\S]{500,}\\}" - Large functions
- "if.*if.*if.*if.*if" - Deep nesting (>5 levels)
```

## Dangerous Functions

### JavaScript/TypeScript

```
Grep patterns:
- "eval\\(" - Code evaluation
- "Function\\(" - Dynamic function creation
- "setTimeout\\(.*[\"']" - setTimeout with string
- "setInterval\\(.*[\"']" - setInterval with string
- "__proto__" - Prototype pollution risk
- "document\\.write" - Document write
```

### Python

```
Grep patterns:
- "eval\\(" - Code evaluation
- "exec\\(" - Code execution
- "compile\\(" - Code compilation
- "pickle\\.loads" - Unsafe deserialization
- "yaml\\.load\\(" - Unsafe YAML load (use safe_load)
```

### PHP

```
Grep patterns:
- "eval\\(" - Code evaluation
- "assert\\(" - Assert (can execute code)
- "unserialize" - Unsafe deserialization
- "extract\\(" - Variable extraction (dangerous)
```

## Framework-Specific Patterns

### Next.js App Router

```
Grep patterns:
- "use client.*fetch" - Client component with fetch (use server)
- "use server.*useState" - Server action with state
- "cookies\\(\\).*not.*await" - Cookies without await
- "headers\\(\\).*not.*await" - Headers without await
```

### React Server Actions

```
Grep patterns:
- "use server.*export const" - Inline server actions (prefer separate file)
- "action.*.*redirect.*try" - Redirect in try block
- "formData\\.get.*!=" - FormData without validation
```

### Entity Framework

```
Grep patterns:
- "AsEnumerable\\(\\).*Where" - Client evaluation after AsEnumerable
- "ToList\\(\\).*Where" - Filtering after ToList
- "Include.*Include.*Include" - Deep eager loading (N+1 risk)
- "var.*=.*context\\." - DbContext queries not async
```

### ABP Framework

```
Grep patterns:
- "new.*AppService" - Manual service instantiation
- "new.*DomainService" - Manual domain service creation
- "IRepository.*AsQueryable.*ToList" - Sync query on async repo
- "[UnitOfWork].*Requires = UnitOfWorkTransactionBehavior\\.Disabled" - UOW disabled
```

## Test Code Patterns

Patterns that are acceptable in test code but not production:

```
Acceptable in tests:
- "as any" - Type assertions okay in tests
- "setTimeout" - Delays acceptable in integration tests
- "console\\.log" - Debugging in tests okay
- "\\@ts-ignore" - Okay for testing edge cases
```

## Configuration File Issues

```
Grep patterns:
- "\\.env.*commit" - .env file committed
- "credentials.*\\.json" - Credentials file
- "config.*password.*=" - Passwords in config
- "token.*=.*[A-Za-z0-9]{20,}" - Tokens in config files
```

## Logging Issues

```
Grep patterns:
- "console\\.log.*password" - Logging passwords
- "console\\.log.*token" - Logging tokens
- "console\\.log.*secret" - Logging secrets
- "logger.*password" - Logger with password
- "print.*password" - Print statements with passwords
```

## Usage Guidelines

### Running Pattern Searches

```bash
# Search for SQL injection patterns in TypeScript files
grep -r "query.*=.*\`.*\${" --include="*.ts" --include="*.tsx" .

# Search for hardcoded secrets
grep -rE "(password|api[_-]?key|secret).*=.*[\"'][A-Za-z0-9]{20,}" .

# Search for XSS vulnerabilities
grep -r "dangerouslySetInnerHTML" --include="*.tsx" .
```

### Context Reading

**Always read context** around matches:
```bash
# Use -B (before) and -A (after) for context
grep -B 3 -A 3 "pattern" file.ts
```

### False Positive Mitigation

Before reporting:
1. Read the full file with Read tool
2. Understand the surrounding logic
3. Check for validation/sanitization
4. Verify framework conventions
5. Consider if it's test code

### Pattern Priority

1. **Critical**: Security patterns (SQL injection, XSS, secrets)
2. **High**: Logic errors, auth issues
3. **Medium**: Code quality, performance
4. **Low**: Style, conventions

## Adding New Patterns

To add new patterns:

1. Test the pattern with grep/ripgrep
2. Verify it catches real issues
3. Check false positive rate
4. Document what it detects
5. Add to appropriate category
6. Update SKILL.md if workflow changes

## Pattern Testing

Test patterns before using:

```bash
# Test pattern on known vulnerable code
echo 'const query = `SELECT * FROM users WHERE id = ${userId}`;' | grep 'query.*=.*`.*\${'

# Test on safe code (should not match)
echo 'const query = "SELECT * FROM users WHERE id = ?";' | grep 'query.*=.*`.*\${'
```

## References

- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **CWE List**: https://cwe.mitre.org/
- **SANS Top 25**: https://www.sans.org/top25-software-errors/
- **SonarQube Rules**: https://rules.sonarsource.com/

## Version

- **Version**: 1.0.0
- **Last Updated**: 2025-01-13
- **Pattern Count**: 100+ patterns across all categories
