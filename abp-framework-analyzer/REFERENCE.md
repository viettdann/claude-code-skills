# ABP Framework Anti-Pattern Reference

Comprehensive reference for AI Code Scanning Agent, providing specific rules and patterns to identify anti-patterns, code weaknesses, and architectural violations in .NET applications built on the ABP Framework.

This document follows the official ABP Framework 2025 best practices and Domain-Driven Design tactical patterns.

## Table of Contents

- [I. Performance and Scalability Anti-Patterns](#i-performance-and-scalability-anti-patterns)
- [II. Security Anti-Patterns and Weaknesses](#ii-security-anti-patterns-and-weaknesses)
- [III. Architectural Violations](#iii-architectural-violations-abp-specific)
- [IV. Maintainability and Over-Engineering Anti-Patterns](#iv-maintainability-and-over-engineering-anti-patterns)
- [V. Additional Considerations](#v-additional-considerations-for-ai-agent)

---

## I. Performance and Scalability Anti-Patterns

These patterns directly impact the application's throughput, latency, and ability to scale horizontally.

| Pattern Name | Description | Detection Rule | Severity | Remediation |
| :--- | :--- | :--- | :--- | :--- |
| **Synchronous I/O Block** | Blocking the thread pool by calling synchronous I/O methods (e.g., database access, file I/O, network calls) in ASP.NET Core/ABP Application Services. This severely limits scalability. | Look for `Task.Wait()`, `Task.Result`, or synchronous I/O methods (e.g., `Read()`, `Write()`, `SaveChanges()`, `GetAwaiter().GetResult()`) within `Controller` or `ApplicationService` methods that are not marked `async`. | Critical | Replace synchronous calls with their `async`/`await` counterparts (e.g., `SaveAsync()`, `ReadAsync()`). Ensure the entire call stack is asynchronous. |
| **Busy Database / N+1 Query** | Executing a query to retrieve a list of entities (N) and then executing N additional queries to retrieve related data for each entity. | Look for `foreach` loops or LINQ projections immediately following a collection retrieval from a repository, where an additional repository call (e.g., `_repository.GetAsync(id)`) is made inside the loop. | High | Use eager loading (`.Include()` in EF Core) or projection queries (`.Select()`) to fetch all necessary data in a single database query. |
| **In-Memory Cache in Scaled App** | Using the default `IMemoryCache` or a static dictionary for caching in an application designed to run on multiple instances (e.g., microservices or scaled monolith). | Look for direct usage of `IMemoryCache` or `ConcurrentDictionary` in projects configured for multi-instance deployment (e.g., projects with a `Volo.Abp.AspNetCore.Mvc` dependency). | Medium | Replace with ABP's `IDistributedCache<T>` abstraction, configured to use a distributed store like Redis or Memcached. |
| **Unbounded Collection Retrieval** | Retrieving an entire table or a very large collection of data without pagination, filtering, or limits. | Look for repository methods (e.g., `GetListAsync()`, `GetAll()`) without any `skip`, `take`, `limit`, or `maxResultCount` parameters, especially in Application Service methods exposed via API. | High | Implement pagination using `IPagedAndSortedResultRequest` and enforce a maximum page size. Use `WithDetails()` only when necessary. |
| **Magic Strings/Numbers** | Using hardcoded strings or numbers for configuration, error messages, or domain logic without a constant or enum definition. | Look for literal strings or numbers used as keys for configuration, cache, or authorization checks (e.g., `[Authorize("AdminRole")]`) that are not defined in a `const` or `enum` within a `Domain.Shared` project. | Low | Define all such literals in the module's `Domain.Shared` project as constants or enums for centralized management. |

### Detailed Examples

#### Synchronous I/O Block

```csharp
// ❌ Wrong: Blocking async call
public void UpdateOrder(Guid id)
{
    var order = _orderRepository.GetAsync(id).Result; // DEADLOCK RISK
    order.Status = OrderStatus.Confirmed;
}

// ✅ Correct: Async-first approach
public async Task UpdateOrderAsync(Guid id)
{
    var order = await _orderRepository.GetAsync(id);
    order.Confirm(); // Business logic in entity
}
```

#### N+1 Query Problem

```csharp
// ❌ Wrong: N+1 queries
public async Task<List<OrderDto>> GetOrdersAsync()
{
    var orders = await _orderRepository.GetListAsync();
    var result = new List<OrderDto>();

    foreach (var order in orders) // N iterations
    {
        var customer = await _customerRepository.GetAsync(order.CustomerId); // N queries!
        result.Add(new OrderDto
        {
            OrderNumber = order.OrderNumber,
            CustomerName = customer.Name
        });
    }

    return result;
}

// ✅ Correct: Single query with projection
public async Task<List<OrderDto>> GetOrdersAsync()
{
    var queryable = await _orderRepository.GetQueryableAsync();

    return await queryable
        .Select(o => new OrderDto
        {
            OrderNumber = o.OrderNumber,
            CustomerName = o.Customer.Name // JOIN in database
        })
        .ToListAsync();
}
```

#### In-Memory Cache in Scaled App

```csharp
// ❌ Wrong: In-memory cache in multi-instance app
public class ProductAppService : ApplicationService
{
    private readonly IMemoryCache _memoryCache; // Not shared across instances

    public async Task<ProductDto> GetAsync(Guid id)
    {
        if (_memoryCache.TryGetValue(id, out ProductDto cached))
            return cached;

        var product = await _repository.GetAsync(id);
        var dto = ObjectMapper.Map<Product, ProductDto>(product);

        _memoryCache.Set(id, dto, TimeSpan.FromMinutes(10));
        return dto;
    }
}

// ✅ Correct: Distributed cache
public class ProductAppService : ApplicationService
{
    private readonly IDistributedCache<ProductDto> _distributedCache;

    public async Task<ProductDto> GetAsync(Guid id)
    {
        return await _distributedCache.GetOrAddAsync(
            id.ToString(),
            async () =>
            {
                var product = await _repository.GetAsync(id);
                return ObjectMapper.Map<Product, ProductDto>(product);
            },
            () => new DistributedCacheEntryOptions
            {
                AbsoluteExpiration = DateTimeOffset.Now.AddMinutes(10)
            }
        );
    }
}
```

#### Unbounded Collection Retrieval

```csharp
// ❌ Wrong: Loading entire table
public async Task<List<ProductDto>> GetProductsAsync()
{
    var products = await _productRepository.GetListAsync(); // Loads ALL products
    return ObjectMapper.Map<List<Product>, List<ProductDto>>(products);
}

// ✅ Correct: Pagination enforced
public async Task<PagedResultDto<ProductDto>> GetProductsAsync(PagedAndSortedResultRequestDto input)
{
    var queryable = await _productRepository.GetQueryableAsync();

    var totalCount = await queryable.CountAsync();

    var products = await queryable
        .OrderBy(input.Sorting ?? "Name")
        .Skip(input.SkipCount)
        .Take(Math.Min(input.MaxResultCount, 100)) // Enforce max page size
        .ToListAsync();

    return new PagedResultDto<ProductDto>(
        totalCount,
        ObjectMapper.Map<List<Product>, List<ProductDto>>(products)
    );
}
```

#### Magic Strings/Numbers

```csharp
// ❌ Wrong: Magic strings scattered
public class OrderAppService : ApplicationService
{
    [Authorize("OrderManagement.Orders.Create")] // Hardcoded permission
    public async Task CreateAsync(CreateOrderDto input)
    {
        if (input.TotalAmount > 10000) // Magic number
            throw new BusinessException("OrderTooLarge"); // Magic error code
    }
}

// ✅ Correct: Constants in Domain.Shared
// In Domain.Shared/OrderConsts.cs
public static class OrderConsts
{
    public const decimal MaxOrderAmount = 10000m;
}

// In Domain.Shared/OrderDomainErrorCodes.cs
public static class OrderDomainErrorCodes
{
    public const string OrderTooLarge = "Order:TooLarge";
}

// In Application.Contracts/Permissions/OrderPermissions.cs
public static class OrderPermissions
{
    public const string Create = "OrderManagement.Orders.Create";
}

// In Application/OrderAppService.cs
[Authorize(OrderPermissions.Create)]
public async Task CreateAsync(CreateOrderDto input)
{
    if (input.TotalAmount > OrderConsts.MaxOrderAmount)
        throw new BusinessException(OrderDomainErrorCodes.OrderTooLarge);
}
```

---

## II. Security Anti-Patterns and Weaknesses

These patterns expose the application to common security risks, particularly those listed in the OWASP Top 10.

| Pattern Name | Description | Detection Rule | Severity | Remediation |
| :--- | :--- | :--- | :--- | :--- |
| **Raw SQL Injection Risk** | Using string concatenation to build SQL queries, bypassing the protection of parameterized queries. | Look for `DbContext.Database.ExecuteSqlRaw()` or `FromSqlRaw()` calls where the SQL string is constructed using string interpolation (`$"{...}"`) or concatenation with user-supplied input. | Critical | Always use parameterized methods like `ExecuteSqlInterpolated()` or `FromSqlInterpolated()`, or rely on the ORM's safe query methods. |
| **Missing Authorization Check** | Exposing an Application Service method or Controller endpoint without any authorization attribute. | Look for public methods in classes inheriting from `ApplicationService` or `Controller` that are missing the `[Authorize]`, `[AllowAnonymous]`, or `[DisableAuditing]` attributes. | High | Apply the appropriate `[Authorize]` attribute to enforce access control. If the method is intended to be public, explicitly use `[AllowAnonymous]`. |
| **Exposing Entity/Domain Object** | Returning a Domain Entity directly from an Application Service method to the Presentation Layer (Controller/API). | Look for `ApplicationService` methods where the return type is a class that inherits from `AggregateRoot` or `Entity` (e.g., `Task<User> GetUserAsync(...)`). | Medium | Always map Domain Entities to Data Transfer Objects (DTOs) before returning them. Use AutoMapper or manual mapping within the Application Service. |
| **Client-Side Authorization** | Relying solely on UI-level checks (e.g., hiding a button) to enforce security rules, while the underlying API remains unprotected. | Look for `ApplicationService` methods that perform sensitive operations (e.g., `Delete`, `Update`) but lack an explicit `[Authorize]` attribute, assuming the UI will handle access control. | High | Enforce authorization checks on the server-side at the Application Service layer, regardless of the client implementation. |
| **Insecure Default Configuration** | Using default, insecure settings for sensitive components (e.g., default secret keys, weak CORS policies). | Look for configuration files (e.g., `appsettings.json`) or startup code where sensitive settings (e.g., JWT secret, connection strings) are set to default or hardcoded values. | High | Use the .NET Secret Manager for development and environment variables or a secure vault (e.g., Azure Key Vault) for production secrets. |

### Detailed Examples

#### Raw SQL Injection Risk

```csharp
// ❌ Wrong: SQL injection vulnerability
public async Task<List<Order>> SearchOrdersAsync(string customerName)
{
    var sql = $"SELECT * FROM Orders WHERE CustomerName = '{customerName}'"; // DANGEROUS
    return await _dbContext.Orders.FromSqlRaw(sql).ToListAsync();
}

// ✅ Correct: Parameterized query
public async Task<List<Order>> SearchOrdersAsync(string customerName)
{
    return await _dbContext.Orders
        .FromSqlInterpolated($"SELECT * FROM Orders WHERE CustomerName = {customerName}")
        .ToListAsync();
}

// ✅ Better: Use ORM
public async Task<List<Order>> SearchOrdersAsync(string customerName)
{
    var queryable = await _orderRepository.GetQueryableAsync();
    return await queryable
        .Where(o => o.CustomerName == customerName)
        .ToListAsync();
}
```

#### Client-Side Authorization

```csharp
// ❌ Wrong: No server-side auth (relying on UI)
public async Task DeleteOrderAsync(Guid id)
{
    // No [Authorize] attribute - assumes UI hides button
    await _orderRepository.DeleteAsync(id);
}

// ✅ Correct: Server-side authorization
[Authorize(OrderPermissions.Delete)]
public async Task DeleteOrderAsync(Guid id)
{
    var order = await _orderRepository.GetAsync(id);

    // Additional business rule check
    if (order.IsProcessed)
        throw new BusinessException(OrderDomainErrorCodes.CannotDeleteProcessedOrder);

    await _orderRepository.DeleteAsync(order);
}
```

#### Insecure Default Configuration

```csharp
// ❌ Wrong: Hardcoded secrets in appsettings.json
{
  "ConnectionStrings": {
    "Default": "Server=localhost;Database=MyDb;User=sa;Password=123456;" // INSECURE
  },
  "JwtBearer": {
    "SecurityKey": "MySecretKey123" // DEFAULT KEY - INSECURE
  }
}

// ✅ Correct: Use User Secrets (development) and Environment Variables (production)
// In appsettings.json
{
  "ConnectionStrings": {
    "Default": "" // Override from User Secrets or Environment
  }
}

// In secrets.json (development - not in source control)
{
  "ConnectionStrings": {
    "Default": "Server=localhost;Database=MyDb;Integrated Security=true;"
  }
}

// In production (Azure App Service configuration or Key Vault)
Environment.GetEnvironmentVariable("ConnectionStrings__Default")
```

---

## III. Architectural Violations (ABP Specific)

These patterns violate the core principles of Clean Architecture, leading to tight coupling and poor maintainability.

| Pattern Name | Description | Detection Rule | Severity | Remediation |
| :--- | :--- | :--- | :--- | :--- |
| **Domain Service Persistence Access** | A Domain Service directly calls a repository's `SaveChanges()` or `UnitOfWork.Complete()`, violating the principle that persistence should be managed by the Application Layer's Unit of Work. | Look for classes inheriting from `DomainService` where methods contain calls to `IRepository.Update()`, `IRepository.Insert()`, or any explicit Unit of Work completion method. | High | Domain Services should only manipulate the state of Aggregates. The Application Service is responsible for calling the repository's update/insert methods and allowing the Unit of Work to commit changes. |
| **Application Service Domain Logic** | Placing complex business rules, invariants, or cross-aggregate logic directly within an Application Service implementation. | Look for Application Service methods with complex `if/else` blocks, loops, or calculations that should belong to an Entity or a Domain Service. | Medium | Extract the business logic into the relevant **Aggregate Root** (for single-entity logic) or a **Domain Service** (for cross-aggregate or external service logic). |
| **Controller Repository Access** | The Presentation Layer (Controller) directly injects and uses a Repository, bypassing the Application Service layer. | Look for classes inheriting from `Controller` or `AbpController` that have a dependency injected of type `IRepository<T, TKey>`. | High | Controllers must only communicate with the Application Layer (Application Services). All business logic and data access orchestration must be delegated to the Application Service. |
| **Domain Layer External Dependency** | The Domain Layer takes a direct dependency on an external infrastructure concern (e.g., `System.IO.File`, `HttpClient`, or a specific ORM class). | Look for `using` statements or injected dependencies in the `*.Domain` project that reference packages or namespaces related to Infrastructure (e.g., `Microsoft.EntityFrameworkCore`, `System.Net.Http`). | High | Use an **Interface Segregation** pattern: define an interface in the Domain Layer (e.g., `IEmailSender`) and implement it in the Infrastructure Layer (e.g., `SmtpEmailSender`). |
| **Missing DTO for Application Service** | An Application Service method takes a Domain Entity as an input parameter, allowing the client to potentially over-post data or bypass domain validation. | Look for `ApplicationService` methods where an input parameter is a class that inherits from `AggregateRoot` or `Entity` (e.g., `Task UpdateUserAsync(User user)`). | Medium | Always use a dedicated Input DTO (e.g., `UpdateUserInput`) for all Application Service methods that accept data from the client. |

### Detailed Examples

#### Domain Service Persistence Access

```csharp
// ❌ Wrong: Domain service managing persistence
public class OrderManager : DomainService
{
    private readonly IOrderRepository _orderRepository;

    public async Task CreateOrderAsync(Guid customerId, List<OrderItemInput> items)
    {
        var order = new Order(customerId);

        foreach (var item in items)
        {
            order.AddItem(item.ProductId, item.Quantity, item.Price);
        }

        await _orderRepository.InsertAsync(order); // Wrong layer for persistence
        await CurrentUnitOfWork.SaveChangesAsync(); // Domain service shouldn't commit

        return order.Id;
    }
}

// ✅ Correct: Domain service handles domain logic only
public class OrderManager : DomainService
{
    private readonly IRepository<Customer> _customerRepository;
    private readonly IRepository<Product> _productRepository;

    public async Task<Order> CreateOrderAsync(Guid customerId, List<OrderItemInput> items)
    {
        // Domain validation and logic
        var customer = await _customerRepository.GetAsync(customerId);

        if (!customer.IsActive)
            throw new BusinessException(OrderDomainErrorCodes.CustomerNotActive);

        var order = new Order(customer.Id, customer.Name);

        foreach (var item in items)
        {
            var product = await _productRepository.GetAsync(item.ProductId);
            order.AddItem(product.Id, item.Quantity, product.Price);
        }

        return order; // Return the aggregate, don't persist
    }
}

// Application service handles persistence
public class OrderAppService : ApplicationService
{
    private readonly OrderManager _orderManager;
    private readonly IOrderRepository _orderRepository;

    public async Task<OrderDto> CreateAsync(CreateOrderDto input)
    {
        var order = await _orderManager.CreateOrderAsync(input.CustomerId, input.Items);
        await _orderRepository.InsertAsync(order); // Persistence in app layer
        // ABP UoW commits automatically

        return ObjectMapper.Map<Order, OrderDto>(order);
    }
}
```

#### Controller Repository Access

```csharp
// ❌ Wrong: Controller accessing repository directly
[ApiController]
[Route("api/orders")]
public class OrderController : AbpController
{
    private readonly IOrderRepository _orderRepository; // WRONG LAYER

    [HttpGet("{id}")]
    public async Task<OrderDto> Get(Guid id)
    {
        var order = await _orderRepository.GetAsync(id);
        return ObjectMapper.Map<Order, OrderDto>(order);
    }
}

// ✅ Correct: Controller delegates to application service
[ApiController]
[Route("api/orders")]
public class OrderController : AbpController
{
    private readonly IOrderAppService _orderAppService;

    [HttpGet("{id}")]
    public async Task<OrderDto> Get(Guid id)
    {
        return await _orderAppService.GetAsync(id);
    }
}
```

---

## IV. Maintainability and Over-Engineering Anti-Patterns

These patterns are common developer mistakes that lead to code complexity, reduced readability, and increased maintenance costs.

| Pattern Name | Description | Detection Rule | Severity | Remediation |
| :--- | :--- | :--- | :--- | :--- |
| **Anemic Domain Model** | Entities contain only data (getters/setters) and no business logic, forcing all logic into Application Services. This violates separation of concerns and makes code harder to maintain. | Look for classes inheriting from `Entity` or `AggregateRoot` that contain only properties and no public methods that enforce business invariants or perform state changes. | High | Move business logic from Application Services into the Entities/Aggregate Roots themselves. Entities should protect their own state. |
| **Overly Large Aggregate** | An Aggregate Root that manages too many entities, leading to complex transaction boundaries and high locking contention. | Look for classes inheriting from `AggregateRoot` that have more than 5-7 direct child collections or properties referencing other entities, or where the root class exceeds 200 lines of code. | Medium | Decompose the large aggregate into smaller, more focused aggregates. Use eventual consistency for communication between aggregates. |
| **Over-Abstraction / YAGNI Violation** | Introducing unnecessary layers, interfaces, or patterns (e.g., Generic Repository on top of ABP Repository) for functionality that is not required (You Ain't Gonna Need It). | Look for interfaces with only one implementation, or base classes with no derived classes, especially in the Application or Domain layers. Look for custom generic repository implementations that simply wrap ABP's built-in `IRepository`. | Medium | Remove the unnecessary abstraction. Follow the principle of "Simple is better" and only introduce complexity when a concrete problem demands it. |
| **Catch-All Exception Handling** | Catching a generic exception (`catch (Exception e)`) and either logging it and continuing, or re-throwing it without adding context, losing the original stack trace. | Look for `catch (Exception e)` blocks that do not use `throw;` to re-throw (instead using `throw e;` or just logging and exiting), or that catch and log without providing meaningful context. | Medium | Catch specific exceptions. If catching `Exception`, ensure the original stack trace is preserved using `throw;` or wrap it in a new exception with the original as the inner exception. |
| **Premature Microservices** | Splitting a system into microservices before the domain is well-understood, leading to a distributed monolith with high communication overhead. | *Requires architectural context:* Look for a large number of small, tightly coupled services (e.g., 10+ services with only 1-2 Aggregate Roots each) that communicate synchronously via HTTP. | High | Consolidate tightly coupled services into a Modular Monolith (which ABP supports well) until the domain boundaries are clearer. |

### Detailed Examples

#### Over-Abstraction / YAGNI Violation

```csharp
// ❌ Wrong: Unnecessary abstraction layer
public interface IGenericRepository<TEntity, TKey> : IRepository<TEntity, TKey>
    where TEntity : Entity<TKey>
{
    // Just wrapping ABP's IRepository with no additional value
    Task<TEntity> GetByIdAsync(TKey id);
    Task<List<TEntity>> GetAllAsync();
}

public class GenericRepository<TEntity, TKey> : IGenericRepository<TEntity, TKey>
    where TEntity : Entity<TKey>
{
    private readonly IRepository<TEntity, TKey> _abpRepository;

    public async Task<TEntity> GetByIdAsync(TKey id)
    {
        return await _abpRepository.GetAsync(id); // Just delegating
    }

    public async Task<List<TEntity>> GetAllAsync()
    {
        return await _abpRepository.GetListAsync(); // Just delegating
    }
}

// Then every service uses IGenericRepository instead of IRepository

// ✅ Correct: Use ABP's IRepository directly
public class OrderAppService : ApplicationService
{
    private readonly IOrderRepository _orderRepository; // Domain-specific interface

    public async Task<OrderDto> GetAsync(Guid id)
    {
        var order = await _orderRepository.GetAsync(id); // Use ABP repository
        return ObjectMapper.Map<Order, OrderDto>(order);
    }
}

// Only create custom repository interfaces when you need domain-specific methods
public interface IOrderRepository : IRepository<Order, Guid>
{
    Task<Order> GetByOrderNumberAsync(string orderNumber);
    Task<List<Order>> GetPendingOrdersAsync();
}
```

#### Catch-All Exception Handling

```csharp
// ❌ Wrong: Losing stack trace
public async Task ProcessOrderAsync(Guid orderId)
{
    try
    {
        var order = await _orderRepository.GetAsync(orderId);
        order.Process();
    }
    catch (Exception ex)
    {
        _logger.LogError(ex.Message); // Only message, no context
        throw ex; // Loses original stack trace!
    }
}

// ✅ Correct: Preserve stack trace and add context
public async Task ProcessOrderAsync(Guid orderId)
{
    try
    {
        var order = await _orderRepository.GetAsync(orderId);
        order.Process();
    }
    catch (BusinessException)
    {
        throw; // Re-throw business exceptions as-is
    }
    catch (EntityNotFoundException ex)
    {
        _logger.LogWarning(ex, "Order {OrderId} not found", orderId);
        throw; // Preserve stack trace
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "Failed to process order {OrderId}", orderId);
        throw new ApplicationException($"Failed to process order {orderId}", ex); // Wrap with inner
    }
}
```

---

## V. Additional Considerations for AI Agent

To enhance the AI Agent's effectiveness, the following contextual and structural checks should be integrated.

### A. Contextual Checks (ABP Framework)

| Check Name | Description | Detection Rule | Severity |
| :--- | :--- | :--- | :--- |
| **Module Dependency Check** | Ensuring that modules only depend on lower-level layers (e.g., `Application` depends on `Domain`, but not vice-versa). | Scan project references: Flag any reference from a `*.Domain` project to a `*.Application`, `*.HttpApi`, or `*.Web` project. | High |
| **Repository Interface Location** | Verifying that all repository interfaces are defined in the Domain Layer, adhering to the Dependency Inversion Principle. | Look for interfaces inheriting from `IRepository<T, TKey>` defined outside of the `*.Domain` project. | High |
| **Configuration Key Centralization** | Checking if configuration keys are defined as constants, rather than being scattered across the codebase. | Look for repeated usage of the same literal string (e.g., `"MySettingKey"`) in multiple files, especially in `ConfigureServices` methods, that is not defined as a `const` in a shared location. | Low |
| **Explicit Transaction Management** | Explicitly starting or committing transactions (e.g., `_unitOfWork.BeginTransaction()`) in Application Services, which is usually unnecessary due to ABP's automatic Unit of Work. | Look for direct calls to `IUnitOfWork` methods like `BeginTransaction()` or `Commit()` within `ApplicationService` methods. | Low |

### B. Debugging and Observability Checks

| Check Name | Description | Detection Rule | Severity |
| :--- | :--- | :--- | :--- |
| **Non-Structured Logging** | Using simple string concatenation for logging messages, making them difficult to query and analyze in a centralized log system. | Look for `ILogger.LogInformation()` or similar calls where the message template is a simple interpolated string (e.g., `_logger.LogInformation($"User {userId} updated")`) instead of a structured template (e.g., `_logger.LogInformation("User {UserId} updated", userId)`). | Medium |
| **Missing Exception Mapping** | Throwing raw, unhandled exceptions (e.g., `NullReferenceException`, `ArgumentException`) from the Domain or Application Layer without using ABP's exception handling system. | Look for `throw new ...Exception(...)` calls in Domain or Application Services that are not one of ABP's recognized exception types (e.g., `UserFriendlyException`, `BusinessException`). | Medium |

### Detailed Examples

#### Module Dependency Check

```bash
# Check project references to ensure proper layering
# ❌ Wrong: Domain depending on Application
<Project Sdk="Microsoft.NET.Sdk">
  <ItemGroup>
    <!-- Domain.csproj -->
    <ProjectReference Include="..\Acme.BookStore.Application\Acme.BookStore.Application.csproj" /> <!-- WRONG -->
  </ItemGroup>
</Project>

# ✅ Correct: Proper dependency direction
<Project Sdk="Microsoft.NET.Sdk">
  <ItemGroup>
    <!-- Application.csproj -->
    <ProjectReference Include="..\Acme.BookStore.Domain\Acme.BookStore.Domain.csproj" /> <!-- Correct -->
  </ItemGroup>
</Project>
```

#### Non-Structured Logging

```csharp
// ❌ Wrong: String interpolation (not queryable)
_logger.LogInformation($"User {userId} created order {orderId} with total {total}");
// Cannot query by specific userId or orderId in log aggregation systems

// ✅ Correct: Structured logging
_logger.LogInformation(
    "User {UserId} created order {OrderId} with total {TotalAmount}",
    userId,
    orderId,
    total
);
// Can query: UserId="abc123" in log systems
```

#### Missing Exception Mapping

```csharp
// ❌ Wrong: Generic exceptions from domain
public class Order : AggregateRoot<Guid>
{
    public void Confirm()
    {
        if (Status != OrderStatus.Pending)
            throw new InvalidOperationException("Order cannot be confirmed"); // Generic exception
    }
}

// ✅ Correct: Use ABP's BusinessException
public class Order : AggregateRoot<Guid>
{
    public void Confirm()
    {
        if (Status != OrderStatus.Pending)
            throw new BusinessException(OrderDomainErrorCodes.OrderNotPending)
                .WithData("CurrentStatus", Status);
    }
}
```

---

## Severity Classification

- **Critical**:
  - Data corruption risks, deadlocks, security vulnerabilities
  - Clean Architecture dependency rule violations (domain depending on infrastructure)
  - SQL injection vulnerabilities
  - Missing authorization on sensitive operations
  - Business logic in wrong layers (services instead of entities)

- **High**:
  - Performance degradation, memory leaks, N+1 queries
  - Missing authorization or input validation
  - Repository pattern violations (interfaces in wrong layer)
  - Exposing entities instead of DTOs
  - Async/sync violations

- **Medium**:
  - Code duplication
  - Inefficient queries, primitive obsession
  - Missing value objects for domain concepts
  - Coupling issues between application services
  - Incomplete aggregate design
  - Missing purpose-specific repository methods
  - Over-abstraction and unnecessary complexity
  - Poor exception handling patterns
  - Non-structured logging

- **Low**:
  - Code style inconsistencies
  - Minor optimizations
  - Documentation gaps
  - Magic strings/numbers
  - Missing XML comments on public APIs
  - Configuration key duplication

---

## Conclusion

The successful implementation of a code scanning agent requires a clear, rule-based approach. By focusing on these specific anti-patterns and architectural violations, particularly within the opinionated structure of the ABP Framework, the AI Agent can provide high-value feedback that directly improves the maintainability, scalability, and security of the codebase.

**Prioritization for AI Agent:**
1. **Critical** and **High** severity findings (immediate risks)
2. **Clean Architecture violations** (long-term architectural health)
3. **Performance issues** (user experience impact)
4. **Medium** and **Low** findings (technical debt reduction)

---

*This reference document is based on ABP Framework 2025 best practices and Clean Architecture principles.*
