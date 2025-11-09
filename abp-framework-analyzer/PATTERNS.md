# ABP Framework Grep Pattern Reference

Quick reference for detecting ABP anti-patterns, DDD violations, and Clean Architecture issues.

## Domain-Driven Design (DDD) Patterns

### Entity Design
```bash
# Anemic domain models (entities with only getters/setters)
rg "class.*Entity<Guid>.*\{" --type cs -A 10 | rg "public.*\{ get; set; \}" | rg -v "private set"

# Public setters in Domain layer (should be private)
rg "public.*\{ get; set; \}" --type cs -g "**/Domain/**/*.cs"

# Business logic in application services (should be in domain)
rg "if.*\.Status.*==|if.*\.State.*==" --type cs -g "**/*AppService.cs"

# Direct property manipulation in app services
rg "\.(Status|State).*=.*;" --type cs -g "**/*AppService.cs"
```

### Value Objects
```bash
# Mutable value objects (should be immutable)
rg "class.*ValueObject" --type cs -A 15 | rg "public set"

# Primitive obsession (using strings/ints instead of value objects)
rg "public string (Email|Phone|Url|PostalCode|Currency)" --type cs -g "**/Domain/**/*.cs"

# Missing value object validation
rg "class.*ValueObject" --type cs -A 20 | rg -v "Check\.|throw|Validate"
```

### Aggregates
```bash
# Large aggregates (many includes)
rg "Include.*Include.*Include" --type cs

# Repositories for non-aggregate roots
rg "interface I\w+Repository.*IRepository<(?!.*AggregateRoot)" --type cs

# Direct child entity manipulation (bypassing aggregate root)
rg "IRepository<\w+Item>|IRepository<\w+Line>|IRepository<\w+Detail>" --type cs

# Cross-aggregate references (should reference by ID)
rg "public.*AggregateRoot.*\{ get; set; \}" --type cs -g "**/Domain/**/*.cs"
```

### Domain Events
```bash
# Events published from application services (should be from entities)
rg "PublishAsync.*new.*Eto" --type cs -g "**/*AppService.cs"

# Missing domain events for state changes
rg "Status.*=.*Confirmed|Status.*=.*Approved" --type cs | rg -v "AddDistributed|AddLocal"

# Mutable event data
rg "class.*Eto.*\{" --type cs -A 10 | rg "public.*\{ get; set; \}"
```

### Domain Services
```bash
# Business logic in app services (should be domain services)
rg "class.*AppService" --type cs -A 30 | rg "if.*\(.*customer|product|order.*\)"

# Domain services with infrastructure dependencies
rg "class.*Manager.*DomainService" --type cs -A 5 | rg "IDistributedCache|HttpClient|IEmailSender"

# Missing domain services for complex operations
rg "AppService.*foreach.*Repository" --type cs
```

### Repository Pattern
```bash
# Repository interfaces in infrastructure layer (should be in domain)
rg "interface I\w+Repository" --type cs -g "**/EntityFrameworkCore/**/*.cs"

# Leaky abstractions (EF concepts in repository interface)
rg "Task.*Include|IQueryable" --type cs -g "**/Domain/**/I*Repository.cs"

# Generic repository used directly (should have domain-specific interface)
rg "IRepository<\w+,.*Guid>(?!.*:)" --type cs -g "**/*AppService.cs"
```

## Clean Architecture Patterns

### Dependency Rule Violations
```bash
# Domain depending on Infrastructure
rg "using.*EntityFrameworkCore" --type cs -g "**/Domain/**/*.cs"
rg "using.*HttpClient|using.*AspNetCore" --type cs -g "**/Domain/**/*.cs"

# Domain depending on Application
rg "using.*Application" --type cs -g "**/Domain/**/*.cs"

# Application depending on Infrastructure/Web
rg "using.*EntityFrameworkCore|using.*HttpApi" --type cs -g "**/Application/**/*.cs"

# EF attributes in domain entities
rg "\[Index\(|\[Table\(|\[Column\(" --type cs -g "**/Domain/**/*.cs"
```

### Layer Boundaries
```bash
# Entities crossing boundaries (returned from app services)
rg "Task<\w+Entity>|Task<List<\w+Entity>>" --type cs -g "**/*AppService.cs"

# Domain concepts in controllers
rg "new.*Entity\(|new.*AggregateRoot\(" --type cs -g "**/Controllers/**/*.cs"

# DbContext in wrong layers
rg "DbContext" --type cs -g "**/Domain/**/*.cs"
rg "DbContext" --type cs -g "**/Application/**/*.cs"
```

### Interface Adapters
```bash
# Missing DTOs (entities in API)
rg "IActionResult<\w+Entity>|ActionResult<.*Entity>" --type cs

# DTOs in domain layer
rg "Dto\.cs" -g "**/Domain/**/*.cs"

# Missing AutoMapper profiles
rg "class.*AppService" --type cs | rg -v "AutoMapper|ObjectMapper"
```

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

## Comprehensive Scans

### Full DDD Validation Scan
```bash
# Scan for all DDD tactical pattern violations
echo "=== Anemic Domain Models ==="
rg "class.*Entity<Guid>" --type cs -g "**/Domain/**/*.cs" -A 10 | rg "public.*\{ get; set; \}" | rg -v "private set"

echo "=== Value Object Violations ==="
rg "class.*ValueObject" --type cs -A 15 | rg "public set"

echo "=== Aggregate Boundary Issues ==="
rg "IRepository<\w+(Item|Line|Detail)" --type cs

echo "=== Domain Events Misplaced ==="
rg "PublishAsync.*Eto" --type cs -g "**/*AppService.cs"

echo "=== Repository Pattern Violations ==="
rg "interface I\w+Repository" --type cs -g "**/EntityFrameworkCore/**/*.cs"
```

### Full Clean Architecture Scan
```bash
# Scan for all Clean Architecture violations
echo "=== Domain Layer Dependency Violations ==="
rg "using.*(EntityFrameworkCore|AspNetCore|Application)" --type cs -g "**/Domain/**/*.cs"

echo "=== Application Layer Dependency Violations ==="
rg "using.*(EntityFrameworkCore|HttpApi)" --type cs -g "**/Application/**/*.cs"

echo "=== Entity Boundary Violations ==="
rg "Task<\w+Entity>|ActionResult<.*Entity>" --type cs -g "**/*AppService.cs" -g "**/*Controller.cs"

echo "=== Infrastructure in Domain ==="
rg "\[Index\(|\[Table\(|DbContext" --type cs -g "**/Domain/**/*.cs"
```

### Domain Model Health Check
```bash
# Assess domain model richness
echo "=== Domain Entities Count ==="
rg "class.*: (Entity<|AggregateRoot<)" --type cs -g "**/Domain/**/*.cs" -c

echo "=== Value Objects Count ==="
rg "class.*: ValueObject" --type cs -g "**/Domain/**/*.cs" -c

echo "=== Domain Services Count ==="
rg "class.*Manager.*: DomainService" --type cs -g "**/Domain/**/*.cs" -c

echo "=== Domain Events Count ==="
rg "class.*Eto" --type cs -g "**/Domain/**/*.cs" -c

echo "=== Business Logic in App Services (Should be minimal) ==="
rg "if.*\.(Status|State|IsActive)" --type cs -g "**/*AppService.cs" -c
```

### Architecture Layer Compliance
```bash
# Verify layer separation
echo "=== Domain Layer Dependencies ==="
ls **/Domain/**/*.csproj | xargs grep "PackageReference" | grep -v "Volo.Abp"

echo "=== Application Layer Dependencies ==="
ls **/Application/**/*.csproj | xargs grep "PackageReference" | grep -v "Volo.Abp|AutoMapper"

echo "=== Repository Interface Locations ==="
rg "interface I\w+Repository" --type cs -g "**/Domain/**/*.cs" --count-matches
rg "interface I\w+Repository" --type cs -g "**/EntityFrameworkCore/**/*.cs" --count-matches
```

## Tips

- Use `-g` to limit search to specific layers (e.g., `-g "**/*AppService.cs"`)
- Combine with `-v` to exclude false positives
- Use `-A` (after) and `-B` (before) for context
- Pipe to `sort | uniq -c | sort -nr` to find most common issues
- Use `--type cs` to search only C# files
- Use `--count-matches` or `-c` for quantitative analysis
- Combine multiple patterns with `|` for broader searches
- Use `-g "**/Domain/**/*.cs"` to focus on specific layers
