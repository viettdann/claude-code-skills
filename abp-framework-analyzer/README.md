# ABP Framework Code Analyzer

Comprehensive code quality analyzer for ABP Framework .NET projects. Identifies anti-patterns, architectural violations, performance issues, and security risks.

## What This Skill Analyzes

### ABP Framework Specific
- **Async/Sync Violations**: Blocking async calls causing deadlocks
- **Repository Patterns**: Inefficient aggregate loading, N+1 queries
- **Unit of Work**: Manual transaction management
- **Application Services**: Inter-service calls, entity exposure
- **Event Bus**: Incorrect event publishing patterns
- **Caching**: Missing cache, improper invalidation
- **DbContext Usage**: Direct usage in wrong layers

### Domain-Driven Design
- **Anemic Domain Model**: Entities without behavior
- **Business Logic Placement**: Logic in wrong layers
- **Aggregate Design**: Incorrect boundaries and loading
- **Domain Events**: Improper usage patterns

### Performance
- **LINQ Issues**: ToList before filtering/projection
- **Query Optimization**: Missing database-level operations
- **Memory Leaks**: Undisposed resources, event handler leaks
- **Caching Strategies**: Missing or incorrect caching

### Security
- **Authorization**: Missing auth checks on sensitive operations
- **Input Validation**: Unvalidated user input
- **SQL Injection**: Raw SQL with string interpolation
- **Data Exposure**: Sensitive data in DTOs

### Code Quality
- **Exception Handling**: Empty catch blocks, wrong patterns
- **Type Safety**: Missing null checks, wrong types
- **Code Duplication**: Repeated validation/mapping logic
- **Dependency Injection**: Wrong service lifetimes

## Usage

### Basic Scan
```
User: "Scan my ABP project and report"
```

The skill will:
1. Explore project structure
2. Identify ABP version and modules
3. Run systematic scans for all anti-patterns
4. Generate prioritized report

### Focused Analysis
```
User: "Check this ABP project for repository performance issues"
```

Focuses on:
- Eager loading patterns
- N+1 query problems
- Aggregate loading efficiency
- Query optimization opportunities

### Security Audit
```
User: "Audit ABP application services for security issues"
```

Examines:
- Missing authorization attributes
- Input validation gaps
- SQL injection vectors
- Exposed sensitive data

## Report Format

Reports include:

```markdown
### [CRITICAL] Blocking Async Call in Application Service

**Location:** `src/Acme.BookStore.Application/Books/BookAppService.cs:45`

**Category:** ABP Anti-Pattern

**Problem:**
Application service uses `.Result` to block async repository call, risking deadlock.

**Impact:**
- Thread pool starvation under load
- Potential deadlocks in ASP.NET Core
- Violates ABP async-first principle

**Fix:**
```csharp
// ❌ Current (problematic)
public void UpdateBook(Guid id, UpdateBookDto input)
{
    var book = _bookRepository.GetAsync(id).Result; // DEADLOCK RISK
    ObjectMapper.Map(input, book);
}

// ✅ Recommended (ABP best practice)
public async Task UpdateBookAsync(Guid id, UpdateBookDto input)
{
    var book = await _bookRepository.GetAsync(id);
    ObjectMapper.Map(input, book);
}
```

**ABP Documentation:**
- https://abp.io/docs/latest/framework/architecture/best-practices
```

## Example Use Cases

### 1. Code Review
Before merging PR, scan for ABP anti-patterns:
```
"Analyze this ABP project for code quality issues"
```

### 2. Performance Investigation
App running slowly, identify bottlenecks:
```
"Find performance issues in this ABP codebase"
```

### 3. Security Audit
Pre-deployment security check:
```
"Scan ABP application for security vulnerabilities"
```

### 4. Migration Preparation
Before upgrading ABP version:
```
"Check ABP best practices violations before upgrading"
```

### 5. Architecture Review
Validate DDD implementation:
```
"Review domain model and repository patterns in ABP project"
```

## Common Issues Found

Based on ABP Framework patterns, most common issues are:

1. **Async/Sync Violations (CRITICAL)**: 60% of projects have blocking calls
2. **Inefficient Aggregate Loading (HIGH)**: 80% load too much data
3. **Missing Authorization (CRITICAL)**: 40% have unguarded operations
4. **Anemic Domain Models (MEDIUM)**: 70% have business logic in services
5. **Missing Caching (HIGH)**: 50% don't cache frequent reads
6. **Manual Transaction Management (MEDIUM)**: 30% bypass UoW
7. **Inter-Service Calls (MEDIUM)**: 25% have app service dependencies
8. **Entity Exposure (HIGH)**: 35% return entities instead of DTOs

## Severity Guide

- **CRITICAL**: Fix immediately (deadlocks, security, data corruption)
- **HIGH**: Fix before production (performance, auth, data exposure)
- **MEDIUM**: Fix in next sprint (code quality, maintainability)
- **LOW**: Address when convenient (style, minor optimizations)

## Skill Activation

Automatically activates when user mentions:
- "ABP" + "scan/analyze/audit/review/check"
- "ABP Framework" + "code quality"
- "ABP project" + "issues/problems/anti-patterns"
- "Review ABP best practices"

## Requirements

- ABP Framework project (any version 4.x+)
- .NET Core/NET 6+/NET 8+ codebase
- Access to source code (Application, Domain, EntityFrameworkCore layers)

## Limitations

- Analyzes C# code only (not JavaScript/TypeScript UI)
- Requires source code access (not compiled DLLs)
- Pattern-based detection (may have false positives)
- Cannot detect runtime-only issues

## References

- [ABP Framework Documentation](https://abp.io/docs)
- [ABP Best Practices](https://abp.io/docs/latest/framework/architecture/best-practices)
- [ABP GitHub Repository](https://github.com/abpframework/abp)
- [Domain-Driven Design Reference](https://www.domainlanguage.com/ddd/)

## Contributing Patterns

To add new detection patterns, update `PATTERNS.md` with:
1. Grep/regex pattern
2. Issue description
3. Example code (wrong vs right)
4. ABP documentation reference

## Version Compatibility

Supports ABP Framework versions:
- ABP 4.x (older patterns)
- ABP 5.x (current LTS)
- ABP 6.x
- ABP 7.x
- ABP 8.x+ (latest)

Some patterns may be version-specific (e.g., separate DbMigrations in 4.x).
