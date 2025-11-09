# ABP Framework Code Analyzer

Comprehensive code quality analyzer and architectural auditor for ABP Framework .NET projects. Validates Domain-Driven Design (DDD) tactical patterns, Clean Architecture principles, and ABP best practices following 2025 industry standards.

## What This Skill Analyzes

### Domain-Driven Design (DDD) Tactical Patterns ⭐ NEW
- **Entity Design**: Rich vs anemic domain models, invariant protection
- **Value Objects**: Immutability, validation, primitive obsession detection
- **Aggregates**: Consistency boundaries, aggregate roots, size validation
- **Domain Events**: Placement in entities, event-driven architecture
- **Domain Services**: Multi-aggregate coordination, business logic placement
- **Repository Pattern**: Collection-like interfaces, domain layer placement
- **Bounded Contexts**: Natural domain boundaries identification

### Clean Architecture Principles ⭐ NEW
- **Dependency Rule**: Inward-pointing dependencies validation
- **Layer Separation**: Domain, Application, Infrastructure, Web concerns
- **Interface Adapters**: DTO usage, entity boundary protection
- **Use Cases**: Application service as orchestrators, not business logic containers
- **Infrastructure Isolation**: Zero infrastructure dependencies in domain

### ABP Framework Specific
- **Async/Sync Violations**: Blocking async calls causing deadlocks
- **Repository Patterns**: Inefficient aggregate loading, N+1 queries
- **Unit of Work**: Manual transaction management
- **Application Services**: Inter-service calls, entity exposure
- **Event Bus**: Incorrect event publishing patterns
- **Caching**: Missing cache, improper invalidation
- **DbContext Usage**: Direct usage in wrong layers

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

### Comprehensive DDD & Clean Architecture Audit ⭐ NEW
```
User: "Analyze this ABP project for DDD violations and Clean Architecture compliance"
```

The skill will:
1. Explore project structure and identify bounded contexts
2. Validate DDD tactical patterns (entities, value objects, aggregates)
3. Check Clean Architecture dependency rules
4. Verify layer responsibilities and boundaries
5. Generate comprehensive architectural report

### Domain Model Validation ⭐ NEW
```
User: "Check if my domain entities are anemic"
User: "Validate my aggregate boundaries"
User: "Review value object implementations"
```

Examines:
- Entity richness (behavior vs data)
- Value object immutability
- Aggregate consistency boundaries
- Domain event usage
- Business logic placement

### Clean Architecture Compliance ⭐ NEW
```
User: "Verify Clean Architecture layers in my ABP project"
User: "Check for dependency rule violations"
```

Validates:
- Domain layer purity (no infrastructure dependencies)
- Application layer boundaries (no infrastructure leakage)
- DTO usage (entities don't cross boundaries)
- Interface adapters implementation

### Basic Scan
```
User: "Scan my ABP project and report"
```

The skill will:
1. Explore project structure
2. Identify ABP version and modules
3. Run systematic DDD, Clean Architecture, and ABP scans
4. Generate prioritized report with architectural recommendations

### Focused Analysis
```
User: "Check this ABP project for repository performance issues"
```

Focuses on:
- Repository pattern violations (DDD)
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
- Input validation gaps (including value object validation)
- SQL injection vectors
- Exposed sensitive data

## Report Format

Reports include DDD violations, Clean Architecture issues, and ABP anti-patterns:

### Example 1: DDD Violation (Anemic Domain Model)
```markdown
### [CRITICAL] Anemic Domain Model - Business Logic in Application Service

**Location:** `src/Acme.BookStore.Application/Orders/OrderAppService.cs:67`

**Category:** DDD Violation

**DDD Principle:** Entities should encapsulate behavior and protect invariants

**Problem:**
Order confirmation logic is implemented in application service instead of Order entity,
resulting in an anemic domain model. Business rules are scattered across services.

**Impact:**
- Violates DDD tactical patterns (2025 best practice)
- Business logic not reusable or testable in isolation
- Entity can be put in invalid state
- Difficult to maintain consistency

**Fix:**
```csharp
// ❌ Current (anemic entity)
public class Order : AggregateRoot<Guid>
{
    public OrderStatus Status { get; set; } // Public setter
    public decimal Total { get; set; }
}

public class OrderAppService : ApplicationService
{
    public async Task ConfirmAsync(Guid id)
    {
        var order = await _repository.GetAsync(id);
        if (order.Status != OrderStatus.Pending) // Business logic here!
            throw new BusinessException("Cannot confirm");
        order.Status = OrderStatus.Confirmed;
    }
}

// ✅ Recommended (rich domain entity - 2025 DDD best practice)
public class Order : AggregateRoot<Guid>
{
    public OrderStatus Status { get; private set; } // Private setter
    public decimal Total { get; private set; }

    public void Confirm() // Business logic in entity
    {
        if (Status != OrderStatus.Pending)
            throw new BusinessException(OrderDomainErrorCodes.OrderNotPending);

        Status = OrderStatus.Confirmed;
        AddDistributedEvent(new OrderConfirmedEto { OrderId = Id });
    }
}

public class OrderAppService : ApplicationService
{
    public async Task ConfirmAsync(Guid id)
    {
        var order = await _repository.GetAsync(id);
        order.Confirm(); // Thin orchestration
    }
}
```

**References:**
- [ABP Domain Entities](https://abp.io/docs/latest/framework/architecture/domain-driven-design/entities)
- [DDD Tactical Patterns](https://martinfowler.com/bliki/AnemicDomainModel.html)
```

### Example 2: Clean Architecture Violation
```markdown
### [CRITICAL] Domain Layer Depends on Infrastructure

**Location:** `src/Acme.BookStore.Domain/Orders/Order.cs:12`

**Category:** Clean Architecture Violation

**Clean Architecture Principle:** Dependencies must point inward. Domain should not depend on outer layers.

**Problem:**
Domain entity has `using Microsoft.EntityFrameworkCore` and uses `[Index]` attribute,
creating coupling to infrastructure layer.

**Impact:**
- Violates Clean Architecture dependency rule
- Domain logic coupled to specific ORM
- Cannot switch persistence technology without changing domain
- Reduces testability of domain model

**Fix:**
```csharp
// ❌ Current (infrastructure in domain)
using Microsoft.EntityFrameworkCore; // Infrastructure!

[Index(nameof(OrderNumber))] // EF attribute in domain!
public class Order : AggregateRoot<Guid>
{
    public string OrderNumber { get; set; }
}

// ✅ Recommended (pure domain, infrastructure in EF layer)
// In Domain/Orders/Order.cs - Pure domain
public class Order : AggregateRoot<Guid>
{
    public string OrderNumber { get; private set; }
}

// In EntityFrameworkCore/OrderConfiguration.cs - Infrastructure concern
public class OrderConfiguration : IEntityTypeConfiguration<Order>
{
    public void Configure(EntityTypeBuilder<Order> builder)
    {
        builder.HasIndex(x => x.OrderNumber); // Index here
    }
}
```

**References:**
- [Clean Architecture by Uncle Bob](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [ABP Architecture](https://abp.io/docs/latest/framework/architecture)
```

### Example 3: ABP Anti-Pattern
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

// ✅ Recommended (2025 best practice)
public async Task UpdateBookAsync(Guid id, UpdateBookDto input)
{
    var book = await _bookRepository.GetAsync(id);
    ObjectMapper.Map(input, book);
}
```

**References:**
- [ABP Best Practices](https://abp.io/docs/latest/framework/architecture/best-practices)
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

Based on 2025 ABP Framework analysis, most common issues are:

### DDD Violations (2025 Focus Areas)
1. **Anemic Domain Models (CRITICAL)**: 75% have business logic in application services instead of entities
2. **Missing Value Objects (HIGH)**: 85% use primitive types instead of value objects (primitive obsession)
3. **Improper Aggregate Boundaries (HIGH)**: 60% have aggregates that are too large or cross-reference
4. **Domain Events from Wrong Layer (MEDIUM)**: 45% publish events from application services
5. **Missing Domain Services (MEDIUM)**: 50% have multi-entity logic in application layer
6. **Repository Interfaces in Infrastructure (HIGH)**: 40% violate repository pattern placement

### Clean Architecture Violations
7. **Domain Depending on Infrastructure (CRITICAL)**: 30% have EF Core dependencies in domain
8. **Entity Boundary Violations (HIGH)**: 35% return entities instead of DTOs from application services
9. **Application Logic in Controllers (MEDIUM)**: 25% have business rules in web layer
10. **Missing DTO Mapping (HIGH)**: 40% expose domain entities to external consumers

### ABP Anti-Patterns
11. **Async/Sync Violations (CRITICAL)**: 60% of projects have blocking async calls
12. **Inefficient Aggregate Loading (HIGH)**: 80% load too much data from repositories
13. **Missing Authorization (CRITICAL)**: 40% have unguarded operations
14. **Missing Caching (HIGH)**: 50% don't cache frequent reads
15. **Manual Transaction Management (MEDIUM)**: 30% bypass ABP Unit of Work
16. **Inter-Service Calls (MEDIUM)**: 25% have application service dependencies

## Severity Guide

- **CRITICAL**: Fix immediately (deadlocks, security, data corruption)
- **HIGH**: Fix before production (performance, auth, data exposure)
- **MEDIUM**: Fix in next sprint (code quality, maintainability)
- **LOW**: Address when convenient (style, minor optimizations)

## Skill Activation

Automatically activates when user mentions:
- "ABP" + "scan/analyze/audit/review/check"
- "ABP Framework" + "code quality/DDD/Clean Architecture"
- "ABP project" + "issues/problems/anti-patterns"
- "Review ABP best practices"
- "Domain-driven design" + "ABP"
- "Clean Architecture" + "ABP/.NET"
- "Anemic domain model" + "check/validate"
- "Aggregate boundaries" + "review"
- "Value objects" + "validation"
- "Repository pattern" + "ABP"

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

### ABP Framework
- [ABP Framework Documentation](https://abp.io/docs)
- [ABP Best Practices](https://abp.io/docs/latest/framework/architecture/best-practices)
- [ABP Domain-Driven Design](https://abp.io/docs/latest/framework/architecture/domain-driven-design)
- [ABP GitHub Repository](https://github.com/abpframework/abp)

### Domain-Driven Design
- [Domain-Driven Design Reference](https://www.domainlanguage.com/ddd/) - Eric Evans
- [Implementing Domain-Driven Design](https://vaughnvernon.com/) - Vaughn Vernon
- [Anemic Domain Model](https://martinfowler.com/bliki/AnemicDomainModel.html) - Martin Fowler
- [Aggregates in DDD](https://martinfowler.com/bliki/DDD_Aggregate.html)
- [Domain Events Pattern](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/domain-events-design-implementation)

### Clean Architecture
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) - Robert C. Martin
- [Clean Architecture in .NET](https://github.com/jasontaylordev/CleanArchitecture)
- [Dependency Rule](https://blog.cleancoder.com/uncle-bob/2011/09/30/Screaming-Architecture.html)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)

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
