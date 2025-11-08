# ABP Framework Grep Pattern Reference

Quick reference for detecting ABP anti-patterns and code issues.

## ABP-Specific Patterns

### Async/Sync Issues
```bash
# Blocking async calls (CRITICAL)
rg "\.Wait\(\)" --type cs
rg "\.Result(?!\s*{)" --type cs
rg "\.GetAwaiter\(\)\.GetResult\(\)" --type cs

# Non-async application services
rg "public void.*AppService" --type cs

# Non-async repository methods
rg "public.*Repository.*\): void" --type cs
```

### Repository & Data Access
```bash
# Eager loading chains (performance)
rg "Include\(.*\)\.Include" --type cs
rg "ThenInclude" --type cs

# Generic gets with includes (inefficient)
rg "GetAsync.*Include" --type cs

# Auto-include everything
rg "IncludeDetails.*=.*true" --type cs

# Direct DbContext usage (violation)
rg "private.*DbContext" --type cs
rg "_dbContext\.Set<" --type cs
```

### Unit of Work Issues
```bash
# Manual SaveChanges (unnecessary)
rg "SaveChanges(Async)?\(" --type cs

# Manual transactions (ABP handles this)
rg "BeginTransaction" --type cs
rg "using.*transaction.*Database" --type cs
```

### Application Layer Anti-Patterns
```bash
# App service calling app service
rg "private.*I\w+AppService" --type cs

# Exposing entities instead of DTOs
rg "Task<\w+Entity>" --type cs
rg "public.*Entity>" --type cs

# Missing authorization
rg "public async Task.*AppService" --type cs -A 2 | rg -v "Authorize|CheckPolicy"
```

### Event Bus Issues
```bash
# Distributed event publishing
rg "PublishAsync.*publishAsync:\s*true" --type cs

# Event subscriptions (check for cleanup)
rg "Subscribe<" --type cs
```

### Caching
```bash
# Cache usage
rg "IDistributedCache" --type cs

# Cache invalidation
rg "RemoveAsync.*[Cc]ache" --type cs

# Missing cache on frequent reads
rg "GetAsync.*Config|Setting" --type cs | rg -v "Cache"
```

## Domain-Driven Design Violations

### Anemic Domain Model
```bash
# Entities with only properties
rg "class.*Entity.*\{(\s*public.*\{ get; set; \})+\s*\}" --type cs

# Public setters (should be private/protected)
rg "public.*\{ get; set; \}" --type cs -g "**/Domain/**/*.cs"
```

### Business Logic in Wrong Layer
```bash
# Logic in application services that should be in domain
rg "if.*Status.*==.*\|\|" --type cs -g "**/*AppService.cs"

# Direct state manipulation
rg "\.Status\s*=\s*" --type cs -g "**/*AppService.cs"
```

## Performance Issues

### LINQ Anti-Patterns
```bash
# ToList before filtering (loads all to memory)
rg "\.ToList\(\)\.Where" --type cs

# ToList before Select (inefficient)
rg "\.ToList\(\)\.Select" --type cs

# Count when Any is sufficient
rg "\.Count\(\)\s*>\s*0" --type cs

# Count in loop condition
rg "for.*\.Count\(\)" --type cs
```

### Query Issues
```bash
# In-memory filtering (should be DB-side)
rg "ToListAsync\(\).*Where" --type cs

# Missing pagination
rg "GetListAsync\(\)" --type cs | rg -v "Skip|Take|PagedResult"
```

### Memory & Resources
```bash
# IDisposable not disposed
rg "new.*Stream|Reader|Writer|HttpClient" --type cs | rg -v "using"

# Event handlers not unsubscribed
rg "\+=.*Handler" --type cs

# Large collections
rg "new List<.*>\(.*\)" --type cs
```

## Security & Validation

### Missing Authorization
```bash
# Public methods without authorization
rg "public async Task" --type cs -g "**/*AppService.cs" -A 1 | rg -v "\[Authorize"

# Destructive operations without auth
rg "public.*Delete|Remove|Clear" --type cs | rg -v "Authorize"
```

### Input Validation
```bash
# DTOs without validation attributes
rg "public class.*Dto" --type cs -A 10 | rg -v "Required|MaxLength|Range"

# Missing null checks
rg "Check\.NotNull" --type cs
```

### SQL Injection Risks
```bash
# Raw SQL with interpolation
rg "FromSqlRaw.*\$" --type cs
rg "ExecuteSqlRaw.*\+" --type cs

# Dynamic SQL construction
rg "\"SELECT.*\" \+ " --type cs
```

## Exception Handling

```bash
# Empty catch blocks
rg "catch.*\{\s*\}" --type cs

# Catching and rethrowing (wrong)
rg "catch.*Exception.*\s+throw;" --type cs

# Losing stack trace
rg "throw ex;" --type cs

# Missing try-catch on async operations
rg "await.*Async\(" --type cs -A 2 | rg -v "try|catch"
```

## Code Quality

### String Performance
```bash
# String concatenation in loops
rg "for.*\+.*\+.*\+" --type cs

# Should use StringBuilder
rg "while.*string.*\+=" --type cs
```

### Type Safety
```bash
# 'any' type usage (wrong language, but similar)
rg ": object" --type cs -g "**/*Dto.cs"

# Non-null assertion without checks
rg "!\." --type cs

# Suppression comments
rg "#pragma warning disable|#nullable disable" --type cs
```

### Duplicate Code
```bash
# Repeated validation patterns
rg "ValidationException.*email" --type cs

# Duplicate authorization checks
rg "CheckPolicyAsync\(\"" --type cs | sort | uniq -c | sort -nr

# Repeated mapping logic
rg "ObjectMapper\.Map<" --type cs | sort | uniq -c | sort -nr
```

## Dependency Injection Issues

```bash
# Wrong lifetimes
rg "AddSingleton<.*Repository" --type cs
rg "AddTransient<.*DbContext" --type cs

# Service locator anti-pattern
rg "GetRequiredService<" --type cs -g "**/Domain/**"
```

## Migration & DbContext

```bash
# Multiple DbContext for migrations (old pattern)
rg "class.*MigrationsDbContext" --type cs

# Missing migration configuration
rg "modelBuilder\.Entity<" --type cs -g "**/*DbContext.cs"
```

## Usage Examples

### Scan for Critical Issues
```bash
# All async/sync violations
rg "\.Wait\(\)|\.Result(?!\s*{)|GetAwaiter\(\)\.GetResult\(\)" --type cs

# All DbContext violations
rg "private.*DbContext|_dbContext\.Set<" --type cs -g "**/*AppService.cs"

# All missing authorization
rg "public async Task.*Delete|Update|Create" --type cs -g "**/*AppService.cs" | rg -v "Authorize"
```

### Performance Scan
```bash
# All LINQ inefficiencies
rg "\.ToList\(\)\.(Where|Select|OrderBy)|Count\(\)\s*>\s*0" --type cs

# All eager loading chains
rg "Include.*Include|ThenInclude" --type cs
```

### Security Scan
```bash
# SQL injection vectors
rg "FromSqlRaw.*\$|ExecuteSqlRaw.*\+" --type cs

# Missing input validation
rg "public class.*Dto" --type cs -A 5 | rg -v "Required|MaxLength"
```

## Tips

- Use `-g` to limit search to specific layers (e.g., `-g "**/*AppService.cs"`)
- Combine with `-v` to exclude false positives
- Use `-A` (after) and `-B` (before) for context
- Pipe to `sort | uniq -c | sort -nr` to find most common issues
- Use `--type cs` to search only C# files
