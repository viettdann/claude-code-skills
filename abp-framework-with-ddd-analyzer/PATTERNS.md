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

# Parameterless constructors in domain entities (should be protected)
rg "public.*\(\).*\{\s*\}" --type cs -g "**/Domain/**/*Entity.cs"

# Missing invariant checks in constructors
rg "public.*Entity.*\(" --type cs -g "**/Domain/**/*.cs" -A 5 | rg -v "Check\.|Guard\.|throw"
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

# FirstOrDefault when Any is sufficient
rg "\.FirstOrDefault\(\).*!=.*null" --type cs
```

### N+1 Query Problems
```bash
# Repository calls inside loops (N+1 problem)
rg "foreach.*\{" --type cs -A 5 | rg "await.*Repository.*GetAsync"

# LINQ Select with repository access
rg "\.Select\(.*=>.*_.*Repository" --type cs

# Multiple GetAsync in sequence
rg "(await.*GetAsync.*\n.*){3,}" --type cs
```

### Caching Issues
```bash
# IMemoryCache usage (should use IDistributedCache in scaled apps)
rg "IMemoryCache" --type cs -g "**/*AppService.cs"

# ConcurrentDictionary for caching (not distributed)
rg "ConcurrentDictionary<.*>.*cache" --type cs --ignore-case

# Static cache fields (not distributed)
rg "private static.*Cache|private static.*Dictionary" --type cs

# Missing cache on frequent reads (config, settings)
rg "GetAsync.*Configuration|GetAsync.*Setting" --type cs | rg -v "Cache"

# Missing cache invalidation
rg "UpdateAsync|InsertAsync" --type cs -A 3 | rg -v "RemoveAsync.*cache|SetAsync"
```

### Unbounded Collections
```bash
# GetListAsync without pagination
rg "GetListAsync\(\)" --type cs -g "**/*AppService.cs" | rg -v "Skip|Take|Paged"

# GetAll without limits
rg "GetAll\(\)" --type cs | rg -v "Skip|Take|Top"

# Missing MaxResultCount enforcement
rg "IPagedAndSortedResultRequest" --type cs -A 10 | rg -v "Math\.Min.*MaxResultCount"

# Large collection loading in API
rg "Task<List<" --type cs -g "**/*AppService.cs" | rg -v "Paged"
```

### Magic Strings/Numbers
```bash
# Magic strings in authorization
rg '\[Authorize\("' --type cs | rg -v "Permissions\."

# Hardcoded error codes
rg 'BusinessException\("' --type cs | rg -v "ErrorCodes\."

# Magic numbers in business logic
rg ">\s*\d{2,}|<\s*\d{2,}" --type cs -g "**/Domain/**/*.cs" | rg -v "const"

# Configuration keys as literals
rg '\.GetSection\("' --type cs | rg -v "Consts\.|Settings\."
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

# Destructive operations without auth (Delete, Update, Create)
rg "public.*Task.*(Delete|Remove|Update|Create).*Async" --type cs -g "**/*AppService.cs" -B 1 | rg -v "Authorize"

# Sensitive data access without auth
rg "public.*Task.*Get.*Async" --type cs -g "**/*AppService.cs" -B 1 | rg -v "Authorize|AllowAnonymous"

# Client-side authorization (relying on UI)
rg "// UI.*hide|// Only.*admin|// Client.*check" --type cs -g "**/*AppService.cs" --ignore-case
```

### Input Validation
```bash
# DTOs without validation attributes
rg "public class.*Dto" --type cs -A 10 | rg -v "Required|MaxLength|Range|RegularExpression"

# Missing null checks in domain
rg "public.*\(.*string" --type cs -g "**/Domain/**/*.cs" -A 3 | rg -v "Check\.|Guard\.|ArgumentNullException"

# Accepting entities as input (should use DTOs)
rg "public.*Task.*(Entity<|AggregateRoot<)" --type cs -g "**/*AppService.cs"

# Missing input validation in constructors
rg "public.*Entity.*\(" --type cs -g "**/Domain/**/*.cs" -A 5 | rg -v "Check\.|throw.*Exception"
```

### SQL Injection Risks
```bash
# Raw SQL with string interpolation (CRITICAL)
rg "FromSqlRaw.*\$\{|FromSqlRaw.*\$\"" --type cs

# ExecuteSqlRaw with concatenation
rg "ExecuteSqlRaw.*\+" --type cs

# Dynamic SQL construction with user input
rg "\"SELECT.*\" \+|\"UPDATE.*\" \+|\"DELETE.*\" \+" --type cs

# String.Format in SQL queries
rg "String\.Format.*SELECT|String\.Format.*UPDATE" --type cs
```

### Data Exposure
```bash
# Exposing entities instead of DTOs
rg "Task<.*Entity>|Task<.*AggregateRoot>" --type cs -g "**/*AppService.cs"

# Sensitive data in DTOs (passwords, secrets)
rg "public.*Password.*\{ get; set; \}" --type cs -g "**/*Dto.cs"

# API returning entities
rg "ActionResult<.*Entity>|IActionResult.*Entity" --type cs

# Missing [DisableAuditing] on sensitive operations
rg "Password|Secret|Token" --type cs -g "**/*AppService.cs" -B 5 | rg -v "DisableAuditing"
```

### Insecure Configuration
```bash
# Hardcoded secrets in code
rg "password.*=.*\"|secret.*=.*\"|key.*=.*\"" --type cs --ignore-case | rg -v "password.*input|PasswordDto"

# Default JWT keys
rg "SecurityKey.*=.*\"MySecretKey|SecurityKey.*=.*\"123" --type cs --ignore-case

# Hardcoded connection strings
rg "Server=.*Password=|User.*=.*sa.*Password" --type json

# API keys in source
rg "api_key|apikey|api-key" --type cs --type json --ignore-case | rg "=.*\"[A-Za-z0-9]"
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

## Observability and Debugging

### Non-Structured Logging
```bash
# String interpolation in logging (not queryable)
rg "_logger\.Log.*\$\{|_logger\.Log.*\$\"" --type cs

# String concatenation in logging
rg "_logger\.Log.*\+.*\+" --type cs

# Missing structured placeholders
rg "LogInformation\(\".*\{0\}.*\"|LogInformation\(string\.Format" --type cs

# Correct structured logging (for reference)
rg "LogInformation\(\".*\{[A-Za-z]" --type cs
```

### Missing Exception Mapping
```bash
# Generic exceptions in domain/application layer (should use BusinessException)
rg "throw new Exception\(|throw new InvalidOperationException\(" --type cs -g "**/Domain/**/*.cs" -g "**/Application/**/*.cs"

# Not using ABP's BusinessException
rg "throw new.*Exception" --type cs -g "**/Domain/**/*.cs" | rg -v "BusinessException|UserFriendlyException"

# Missing error codes
rg "BusinessException\(\"" --type cs | rg -v "ErrorCodes\."

# ArgumentException in domain (should be BusinessException)
rg "throw new ArgumentException|throw new ArgumentNullException" --type cs -g "**/Domain/**/*.cs"
```

### Module and Configuration Issues
```bash
# Module dependency violations (Domain depending on Application)
# Check .csproj files manually or use:
find . -name "*.Domain.csproj" -exec grep -l "Application.csproj" {} \;

# Repository interfaces in wrong layer (should be in Domain)
rg "interface I\w+Repository.*:" --type cs -g "**/EntityFrameworkCore/**/*.cs"

# Configuration keys not centralized (magic strings)
rg '\.GetValue<.*>\("(?!.*:)' --type cs | sort | uniq -c | sort -rn

# Configuration key duplication
rg 'IConfiguration.*\["' --type cs -o | sort | uniq -c | sort -rn | head -20

# Explicit transaction management (ABP handles automatically)
rg "BeginTransaction\(|Commit\(|Rollback\(" --type cs -g "**/*AppService.cs"
```

## Maintainability Anti-Patterns

### Over-Abstraction and YAGNI Violations
```bash
# Generic repositories wrapping ABP's IRepository (unnecessary)
rg "interface.*IGenericRepository<|class.*GenericRepository<" --type cs

# Interfaces with only one implementation
rg "interface I\w+Service|interface I\w+Manager" --type cs -o | sort | uniq -c | grep "^\s*1 "

# Base classes with no derived classes
rg "public abstract class \w+Base" --type cs

# Unnecessary service layers
rg "I\w+Helper.*interface|I\w+Util.*interface" --type cs
```

### Duplicate Code Detection
```bash
# Repeated validation patterns
rg "if.*string\.IsNullOrEmpty|if.*string\.IsNullOrWhiteSpace" --type cs | wc -l

# Repeated authorization checks
rg "CheckPolicyAsync|AuthorizationService\.AuthorizeAsync" --type cs -o | sort | uniq -c | sort -rn

# Repeated mapping configurations
rg "CreateMap<.*,.*>\(\)" --type cs -o | sort | uniq -c | sort -rn | head -20

# Repeated null checks
rg "if.*==.*null.*throw" --type cs | wc -l
```

### Premature Microservices Indicators
```bash
# Small services with few aggregates
find . -name "*DomainModule.cs" | wc -l  # Count modules
rg "class.*AggregateRoot<" --type cs | wc -l  # Count aggregates

# Synchronous HTTP calls between services
rg "HttpClient.*GetAsync|HttpClient.*PostAsync" --type cs -g "**/*AppService.cs"

# Distributed transactions indicators
rg "TransactionScope|DistributedTransaction" --type cs

# Tight coupling between services
rg "I\w+AppService" --type cs -g "**/*AppService.cs" | rg -v "private readonly.*= null"
```

## Usage Examples

### Comprehensive Security Scan
```bash
# All security issues
echo "=== SQL Injection Risks ==="
rg "FromSqlRaw.*\$|ExecuteSqlRaw.*\+" --type cs

echo "=== Missing Authorization ==="
rg "public async Task.*(Delete|Update|Create)" --type cs -g "**/*AppService.cs" -B 1 | rg -v "Authorize"

echo "=== Insecure Configuration ==="
rg "password.*=.*\"|Server=.*Password=" --type cs --type json --ignore-case

echo "=== Data Exposure ==="
rg "Task<.*Entity>|Task<.*AggregateRoot>" --type cs -g "**/*AppService.cs"
```

### Comprehensive Performance Scan
```bash
# All performance issues
echo "=== Async/Sync Violations ==="
rg "\.Wait\(\)|\.Result(?!\s*{)|GetAwaiter\(\)\.GetResult\(\)" --type cs

echo "=== N+1 Query Problems ==="
rg "foreach.*\{" --type cs -A 5 | rg "await.*Repository.*GetAsync"

echo "=== LINQ Inefficiencies ==="
rg "\.ToList\(\)\.(Where|Select)|\.Count\(\)\s*>\s*0" --type cs

echo "=== Eager Loading Chains ==="
rg "Include.*Include|ThenInclude" --type cs

echo "=== Missing Caching ==="
rg "GetAsync.*Configuration|GetAsync.*Setting" --type cs | rg -v "Cache"

echo "=== Unbounded Collections ==="
rg "GetListAsync\(\)" --type cs -g "**/*AppService.cs" | rg -v "Skip|Take|Paged"
```

### Scan for Critical Issues Only
```bash
# Critical issues that need immediate attention
echo "=== CRITICAL: Async/Sync Violations ==="
rg "\.Wait\(\)|\.Result(?!\s*{)|GetAwaiter\(\)\.GetResult\(\)" --type cs

echo "=== CRITICAL: SQL Injection Risks ==="
rg "FromSqlRaw.*\$\{|ExecuteSqlRaw.*\+" --type cs

echo "=== CRITICAL: Missing Authorization on Delete ==="
rg "public async Task.*Delete" --type cs -g "**/*AppService.cs" -B 1 | rg -v "Authorize"

# All DbContext violations
rg "private.*DbContext|_dbContext\.Set<" --type cs -g "**/*AppService.cs"
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
