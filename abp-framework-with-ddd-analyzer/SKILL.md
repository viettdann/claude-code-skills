---
name: abp-framework-with-ddd-analyzer
description: Comprehensive code quality analyzer and architectural auditor for ABP Framework .NET projects. Use when asked to audit, analyze, scan for issues, review code quality, check ABP best practices, find anti-patterns, identify architectural concerns, validate DDD patterns, or verify Clean Architecture compliance in ABP/.NET codebases.
allowed-tools: Task, Grep, Glob, Read, Bash, Write
---

# ABP Framework Code Analyzer

You are a specialized code auditor for ABP Framework .NET applications with deep expertise in Domain-Driven Design (DDD) and Clean Architecture principles. Your mission is to identify anti-patterns, architectural violations, DDD principle breaches, performance problems, and violations of ABP best practices following 2025 industry standards.

## Knowledge Base Resources

This skill includes comprehensive reference materials using progressive disclosure:

- **[REFERENCE.md](REFERENCE.md)** - Complete knowledge base with all 50+ anti-pattern detection rules, detailed tables, remediation guidance, and 2025 best practices (read when you need comprehensive understanding or detailed examples)
- **[PATTERNS.md](PATTERNS.md)** - Comprehensive grep patterns for all detection rules (reference for quick pattern syntax lookups during scans)
- **[README.md](README.md)** - User-facing documentation and usage examples

**Progressive Disclosure Strategy**: Load REFERENCE.md only when you need:
- Detailed remediation examples for specific anti-patterns
- Comprehensive tables of detection rules organized by category
- Deep-dive understanding of DDD/Clean Architecture principles
- Reference for severity classification and impact analysis

For quick pattern lookups during scans, use PATTERNS.md directly.

## Execution Strategy

1. **Initial Reconnaissance** (use Task tool with Explore agent, thoroughness: "very thorough")
   - Map project structure (Domain, Application, EntityFrameworkCore, DbMigrations layers)
   - Identify ABP version and module architecture (4.x, 5.x, 7.x, 8.x+)
   - Locate critical files: repositories, application services, entities, DbContext, domain services
   - Identify bounded contexts and module boundaries

2. **Systematic Analysis** (use patterns from PATTERNS.md)
   - Use Grep with appropriate patterns for anti-pattern detection
   - Read flagged files to confirm issues and understand context
   - Cross-reference with REFERENCE.md for detailed validation when needed
   - Document findings with file paths and line numbers (format: `path/to/file.cs:123`)

3. **Prioritized Reporting** (follow severity guide in REFERENCE.md)
   - Group by severity: Critical → High → Medium → Low
   - Categorize: DDD Violations | Clean Architecture | ABP Anti-Patterns | Performance | Security
   - Provide actionable fixes with ❌/✅ code examples (follow format in REFERENCE.md)
   - Reference official ABP documentation and DDD principles

4. **Deep Analysis** (when complex issues found)
   - Load REFERENCE.md for detailed anti-pattern tables and comprehensive remediation guidance
   - Provide architectural recommendations and refactoring strategies
   - Reference specific sections from REFERENCE.md for deep-dive understanding

## Domain-Driven Design (DDD) Tactical Patterns Validation

### 1. Entity Design Violations

**DDD Principle**: Entities have unique identity, encapsulate business logic, and protect invariants through behavior.

```
Grep patterns:
- "class.*Entity.*\\{.*public.*\\{ get; set; \\}.*\\}"  # Anemic entities
- "public set"                                           # Public setters in Domain layer
- "new Guid\\(\\)"                                       # Manual ID generation
- "Id.*=.*Guid"                                          # Direct ID assignment
```

**Check for:**
- Entities with only getters/setters (anemic domain model)
- Public setters exposing internal state
- Missing domain logic in entities
- Business rules in application services instead of entities
- Entities without invariant protection
- Parameterless constructors in domain entities

**Fix Pattern:**
```csharp
// ❌ Wrong: Anemic entity (DDD violation)
public class Order : Entity<Guid>
{
    public string CustomerName { get; set; }  // Public setter
    public OrderStatus Status { get; set; }   // No protection
    public decimal TotalAmount { get; set; }
    public List<OrderItem> Items { get; set; } // Mutable collection
}

// Application service doing domain logic (wrong layer):
public async Task ConfirmOrderAsync(Guid orderId)
{
    var order = await _repository.GetAsync(orderId);
    order.Status = OrderStatus.Confirmed;  // Direct manipulation
    order.ConfirmedDate = DateTime.UtcNow; // Logic in wrong layer
}

// ✅ Correct: Rich domain entity with behavior
public class Order : AggregateRoot<Guid>
{
    public string CustomerName { get; private set; }
    public OrderStatus Status { get; private set; }
    public decimal TotalAmount { get; private set; }

    private readonly List<OrderItem> _items = new();
    public IReadOnlyCollection<OrderItem> Items => _items.AsReadOnly();

    // Enforce invariants in constructor
    protected Order() { } // For EF Core

    public Order(Guid customerId, string customerName) : base(Guid.NewGuid())
    {
        Check.NotNullOrWhiteSpace(customerName, nameof(customerName));

        CustomerName = customerName;
        Status = OrderStatus.Pending;
        TotalAmount = 0;
    }

    // Business logic encapsulated in entity
    public void Confirm()
    {
        if (Status != OrderStatus.Pending)
            throw new BusinessException(OrderDomainErrorCodes.OrderNotPending);

        if (!_items.Any())
            throw new BusinessException(OrderDomainErrorCodes.OrderHasNoItems);

        Status = OrderStatus.Confirmed;

        AddDistributedEvent(new OrderConfirmedEto
        {
            OrderId = Id,
            ConfirmedAt = Clock.Now
        });
    }

    public void AddItem(Guid productId, int quantity, decimal price)
    {
        if (Status != OrderStatus.Pending)
            throw new BusinessException(OrderDomainErrorCodes.CannotModifyConfirmedOrder);

        var existingItem = _items.FirstOrDefault(x => x.ProductId == productId);
        if (existingItem != null)
        {
            existingItem.IncreaseQuantity(quantity);
        }
        else
        {
            _items.Add(new OrderItem(Id, productId, quantity, price));
        }

        RecalculateTotal();
    }

    private void RecalculateTotal()
    {
        TotalAmount = _items.Sum(x => x.Subtotal);
    }
}
```

### 2. Value Object Violations

**DDD Principle**: Value objects are immutable, identity-less, and defined by their attributes. They should be replaceable.

```
Grep patterns:
- "public.*set"                          # Setters in value objects
- "class.*:\\s*ValueObject.*public set"  # Mutable value objects
- "new.*\\(.*\\).*\\{.*=.*\\}"           # Object initializers
```

**Check for:**
- Value objects with public setters
- Mutable value objects
- Value objects with identity fields
- Missing equality comparison overrides
- Primitive obsession (using primitives instead of value objects)
- Missing validation in value object constructors

**Fix Pattern:**
```csharp
// ❌ Wrong: Mutable value object
public class Address : ValueObject
{
    public string Street { get; set; }     // Mutable!
    public string City { get; set; }
    public string PostalCode { get; set; }

    public void ChangeCity(string city)    // Value objects shouldn't change
    {
        City = city;
    }
}

// ❌ Wrong: Primitive obsession
public class Customer : Entity<Guid>
{
    public string Email { get; set; }      // Should be Email value object
    public string Phone { get; set; }      // Should be PhoneNumber value object
}

// ✅ Correct: Immutable value object with validation
public class Address : ValueObject
{
    public string Street { get; private set; }
    public string City { get; private set; }
    public string PostalCode { get; private set; }
    public string Country { get; private set; }

    private Address() { } // For EF Core

    public Address(string street, string city, string postalCode, string country)
    {
        Street = Check.NotNullOrWhiteSpace(street, nameof(street));
        City = Check.NotNullOrWhiteSpace(city, nameof(city));
        PostalCode = Check.NotNullOrWhiteSpace(postalCode, nameof(postalCode));
        Country = Check.NotNullOrWhiteSpace(country, nameof(country));

        ValidatePostalCode(postalCode, country);
    }

    private void ValidatePostalCode(string postalCode, string country)
    {
        // Country-specific validation logic
        if (country == "US" && !Regex.IsMatch(postalCode, @"^\d{5}(-\d{4})?$"))
            throw new BusinessException("Invalid US postal code");
    }

    protected override IEnumerable<object> GetAtomicValues()
    {
        yield return Street;
        yield return City;
        yield return PostalCode;
        yield return Country;
    }
}

// ✅ Correct: Email value object
public class Email : ValueObject
{
    public string Value { get; private set; }

    private Email() { }

    public Email(string value)
    {
        if (!IsValid(value))
            throw new BusinessException("Invalid email format");

        Value = value.ToLowerInvariant();
    }

    private static bool IsValid(string email)
    {
        return !string.IsNullOrWhiteSpace(email) &&
               Regex.IsMatch(email, @"^[^@\s]+@[^@\s]+\.[^@\s]+$");
    }

    protected override IEnumerable<object> GetAtomicValues()
    {
        yield return Value;
    }
}
```

### 3. Aggregate Design Violations

**DDD Principle**: Aggregates are consistency boundaries. Changes should go through the aggregate root. Keep aggregates small and focused.

```
Grep patterns:
- "Include.*Include.*Include"            # Large aggregate loading
- "public.*Repository.*Entity"           # Repositories for non-roots
- "DbSet<.*>.*Where"                     # Direct DbSet access
- "new.*Entity.*\\(\\)"                  # Bypassing aggregate root
```

**Check for:**
- Aggregates that are too large (>5-7 entities)
- Direct manipulation of child entities bypassing root
- Repositories for entities that aren't aggregate roots
- Missing transactional boundaries
- Cross-aggregate consistency enforcement
- Loading entire aggregate when subset needed

**Fix Pattern:**
```csharp
// ❌ Wrong: Large aggregate with weak boundaries
public class Order : AggregateRoot<Guid>
{
    public List<OrderItem> Items { get; set; }      // Public setter
    public List<Payment> Payments { get; set; }     // Separate aggregate!
    public Customer Customer { get; set; }          // Separate aggregate!
}

public class OrderItemRepository : IRepository<OrderItem> { }  // Wrong!

public async Task UpdateOrderItemAsync(Guid itemId, int quantity)
{
    var item = await _orderItemRepository.GetAsync(itemId);
    item.Quantity = quantity;  // Bypassing Order aggregate root
}

// ✅ Correct: Well-bounded aggregate
public class Order : AggregateRoot<Guid>
{
    // Reference other aggregates by ID only
    public Guid CustomerId { get; private set; }

    private readonly List<OrderItem> _items = new();
    public IReadOnlyCollection<OrderItem> Items => _items.AsReadOnly();

    // All modifications go through aggregate root
    public void UpdateItemQuantity(Guid orderItemId, int quantity)
    {
        var item = _items.FirstOrDefault(x => x.Id == orderItemId);
        if (item == null)
            throw new BusinessException("Order item not found");

        item.UpdateQuantity(quantity);  // Internal method
        RecalculateTotal();

        // Aggregate ensures consistency
        if (TotalAmount > MaxOrderAmount)
            throw new BusinessException("Order exceeds maximum amount");
    }
}

// OrderItem is part of Order aggregate, not an aggregate root
public class OrderItem : Entity
{
    public Guid OrderId { get; private set; }  // Foreign key to root
    public Guid ProductId { get; private set; } // Reference by ID
    public int Quantity { get; private set; }
    public decimal UnitPrice { get; private set; }
    public decimal Subtotal => Quantity * UnitPrice;

    internal void UpdateQuantity(int quantity)  // Internal to aggregate
    {
        if (quantity <= 0)
            throw new BusinessException("Quantity must be positive");

        Quantity = quantity;
    }
}

// Only aggregate roots have repositories
public interface IOrderRepository : IRepository<Order, Guid>
{
    Task<Order> GetWithItemsAsync(Guid id);  // Purpose-specific method
}
```

### 4. Domain Event Violations

**DDD Principle**: Domain events represent meaningful business occurrences. Use for decoupling and temporal coupling.

```
Grep patterns:
- "AddLocalEvent|AddDistributedEvent"    # Domain event usage
- "class.*Eto\\s*:\\s*\\{.*public"       # Event structure
- "PublishAsync.*new.*Eto"               # Direct publishing (should be from entity)
```

**Check for:**
- Domain events published directly from application services
- Missing domain events for significant state changes
- Events with mutable data
- Events without clear business meaning
- Cross-aggregate consistency without eventual consistency
- Lack of event versioning strategy

**Fix Pattern:**
```csharp
// ❌ Wrong: Publishing events from application service
public class OrderAppService : ApplicationService
{
    public async Task ConfirmOrderAsync(Guid orderId)
    {
        var order = await _orderRepository.GetAsync(orderId);
        order.Status = OrderStatus.Confirmed;  // Direct manipulation

        // Publishing from wrong layer
        await _distributedEventBus.PublishAsync(new OrderConfirmedEto
        {
            OrderId = order.Id
        });
    }
}

// ✅ Correct: Domain events from aggregate root
public class Order : AggregateRoot<Guid>
{
    public void Confirm()
    {
        if (Status != OrderStatus.Pending)
            throw new BusinessException(OrderDomainErrorCodes.OrderNotPending);

        Status = OrderStatus.Confirmed;
        ConfirmedDate = Clock.Now;

        // Domain event added from entity (published by ABP UoW)
        AddDistributedEvent(new OrderConfirmedEto
        {
            OrderId = Id,
            CustomerEmail = CustomerEmail,
            TotalAmount = TotalAmount,
            ConfirmedAt = ConfirmedDate.Value
        });
    }
}

// Application service just orchestrates
public class OrderAppService : ApplicationService
{
    public async Task ConfirmOrderAsync(Guid orderId)
    {
        var order = await _orderRepository.GetAsync(orderId);
        order.Confirm();  // Entity handles logic and events
        // ABP UoW publishes events automatically
    }
}

// ✅ Event handler for cross-aggregate consistency
public class OrderConfirmedEventHandler :
    IDistributedEventHandler<OrderConfirmedEto>,
    ITransientDependency
{
    private readonly IInventoryManager _inventoryManager;

    public async Task HandleEventAsync(OrderConfirmedEto eventData)
    {
        // Eventual consistency across aggregates
        await _inventoryManager.ReserveStockAsync(
            eventData.OrderId,
            eventData.Items
        );
    }
}
```

### 5. Domain Service Violations

**DDD Principle**: Domain services contain domain logic that doesn't naturally fit in a single entity or spans multiple aggregates.

```
Grep patterns:
- "class.*Manager.*ApplicationService"   # Manager in app layer
- "class.*DomainService.*private.*Repository" # DomainService with repository
- "I.*AppService.*I.*AppService"         # App service dependencies
```

**Check for:**
- Business logic in application services instead of domain services
- Domain services with infrastructure dependencies
- Missing domain services for multi-entity operations
- Domain services that are actually application services
- Stateful domain services

**Fix Pattern:**
```csharp
// ❌ Wrong: Business logic in application service
public class OrderAppService : ApplicationService
{
    private readonly IRepository<Order> _orderRepository;
    private readonly IRepository<Customer> _customerRepository;
    private readonly IRepository<Product> _productRepository;

    public async Task<OrderDto> CreateOrderAsync(CreateOrderInput input)
    {
        // Complex business logic in app service (wrong layer!)
        var customer = await _customerRepository.GetAsync(input.CustomerId);

        if (!customer.IsActive)
            throw new BusinessException("Customer is not active");

        if (customer.CreditLimit < input.TotalAmount)
            throw new BusinessException("Insufficient credit limit");

        var order = new Order(customer.Id, customer.Name);

        foreach (var item in input.Items)
        {
            var product = await _productRepository.GetAsync(item.ProductId);

            if (product.Stock < item.Quantity)
                throw new BusinessException("Insufficient stock");

            order.AddItem(product.Id, item.Quantity, product.Price);
        }

        await _orderRepository.InsertAsync(order);
        return ObjectMapper.Map<Order, OrderDto>(order);
    }
}

// ✅ Correct: Business logic in domain service
public class OrderManager : DomainService
{
    private readonly IRepository<Customer> _customerRepository;
    private readonly IRepository<Product> _productRepository;

    public OrderManager(
        IRepository<Customer> customerRepository,
        IRepository<Product> productRepository)
    {
        _customerRepository = customerRepository;
        _productRepository = productRepository;
    }

    // Domain service for multi-aggregate coordination
    public async Task<Order> CreateOrderAsync(
        Guid customerId,
        List<OrderItemInput> items)
    {
        // Domain validation logic
        var customer = await _customerRepository.GetAsync(customerId);

        if (!customer.IsActive)
            throw new BusinessException(OrderDomainErrorCodes.CustomerNotActive);

        var order = new Order(customer.Id, customer.Name);
        decimal estimatedTotal = 0;

        foreach (var item in items)
        {
            var product = await _productRepository.GetAsync(item.ProductId);

            if (product.Stock < item.Quantity)
                throw new BusinessException(
                    OrderDomainErrorCodes.InsufficientStock,
                    product.Name);

            order.AddItem(product.Id, item.Quantity, product.Price);
            estimatedTotal += item.Quantity * product.Price;
        }

        // Multi-entity business rule
        if (!customer.CanPlaceOrder(estimatedTotal))
            throw new BusinessException(
                OrderDomainErrorCodes.ExceedsCreditLimit);

        return order;
    }
}

// Application service becomes thin orchestrator
public class OrderAppService : ApplicationService
{
    private readonly OrderManager _orderManager;
    private readonly IRepository<Order> _orderRepository;

    public async Task<OrderDto> CreateOrderAsync(CreateOrderInput input)
    {
        // Delegate to domain service
        var order = await _orderManager.CreateOrderAsync(
            input.CustomerId,
            input.Items);

        await _orderRepository.InsertAsync(order);

        return ObjectMapper.Map<Order, OrderDto>(order);
    }
}
```

### 6. Repository Pattern Violations

**DDD Principle**: Repositories provide collection-like interface for aggregate roots. Repository interfaces belong in domain layer.

```
Grep patterns:
- "interface.*Repository.*EntityFramework"  # Repository in infra layer
- "class.*Repository.*Include"              # EF-specific code in interface
- "IRepository<.*Entity.*>"                 # Repository for non-roots
- "GetQueryable.*Where.*Select"             # Query logic in app service
```

**Check for:**
- Repository interfaces in infrastructure layer
- Generic repositories used directly without domain abstraction
- Query logic scattered in application services
- Repositories exposing IQueryable directly
- Missing specification pattern for complex queries
- Repository methods that aren't collection-like

**Fix Pattern:**
```csharp
// ❌ Wrong: Repository in infrastructure layer, leaky abstraction
// In EntityFrameworkCore layer
public interface IOrderRepository
{
    Task<Order> GetWithIncludesAsync(Guid id);  // Leaks EF concept
}

public class OrderRepository : IOrderRepository
{
    public async Task<Order> GetWithIncludesAsync(Guid id)
    {
        return await _dbSet
            .Include(x => x.Items)
            .Include(x => x.Customer)  // Loading other aggregate!
            .FirstOrDefaultAsync(x => x.Id == id);
    }
}

// ✅ Correct: Domain-focused repository interface in Domain layer
// In Domain layer
public interface IOrderRepository : IRepository<Order, Guid>
{
    // Intent-revealing, purpose-specific methods
    Task<Order> GetByOrderNumberAsync(string orderNumber);
    Task<List<Order>> GetCustomerOrdersAsync(Guid customerId, OrderStatus? status = null);
    Task<Order> GetWithItemsAsync(Guid id);  // Explicit about loading items
    Task<bool> IsOrderNumberUniqueAsync(string orderNumber);
}

// In EntityFrameworkCore layer (infrastructure)
public class EfCoreOrderRepository :
    EfCoreRepository<YourDbContext, Order, Guid>,
    IOrderRepository
{
    public EfCoreOrderRepository(IDbContextProvider<YourDbContext> dbContextProvider)
        : base(dbContextProvider)
    {
    }

    public async Task<Order> GetByOrderNumberAsync(string orderNumber)
    {
        return await (await GetDbSetAsync())
            .FirstOrDefaultAsync(x => x.OrderNumber == orderNumber);
    }

    public async Task<List<Order>> GetCustomerOrdersAsync(
        Guid customerId,
        OrderStatus? status = null)
    {
        var query = (await GetQueryableAsync())
            .Where(x => x.CustomerId == customerId);

        if (status.HasValue)
            query = query.Where(x => x.Status == status.Value);

        return await query
            .OrderByDescending(x => x.CreationTime)
            .ToListAsync();
    }

    public async Task<Order> GetWithItemsAsync(Guid id)
    {
        return await (await GetDbSetAsync())
            .Include(x => x.Items)  // Only Items (part of aggregate)
            .FirstOrDefaultAsync(x => x.Id == id);
    }

    public async Task<bool> IsOrderNumberUniqueAsync(string orderNumber)
    {
        return !await (await GetDbSetAsync())
            .AnyAsync(x => x.OrderNumber == orderNumber);
    }
}
```

## Clean Architecture Principles Validation

### 1. Dependency Rule Violations

**Clean Architecture Principle**: Dependencies must point inward. Domain layer should have zero dependencies on outer layers.

```
Grep patterns:
- "using.*EntityFrameworkCore"           # EF in Domain
- "using.*Application"                   # App layer in Domain
- "using.*HttpApi|AspNetCore"            # Web in App/Domain
- "Domain.*csproj.*PackageReference.*EntityFramework" # EF in Domain csproj
```

**Check for:**
- Domain layer referencing Application, Infrastructure, or Web layers
- Application layer referencing Infrastructure or Web layers
- Infrastructure concerns leaking into domain (DbContext, HttpClient, etc.)
- Framework-specific attributes in domain entities
- Domain logic depending on external libraries

**Fix Pattern:**
```csharp
// ❌ Wrong: Domain layer with infrastructure dependencies
// In YourProject.Domain/Orders/Order.cs
using Microsoft.EntityFrameworkCore;  // EF Core in domain!
using YourProject.EntityFrameworkCore;

[Index(nameof(OrderNumber))]  // EF attribute in domain!
public class Order : AggregateRoot<Guid>
{
    private readonly YourDbContext _dbContext;  // DbContext in domain!

    public async Task ValidateAsync()
    {
        var exists = await _dbContext.Orders
            .AnyAsync(x => x.OrderNumber == OrderNumber);  // Wrong layer!
    }
}

// ✅ Correct: Pure domain model with abstractions
// In YourProject.Domain/Orders/Order.cs
// No infrastructure using statements!

public class Order : AggregateRoot<Guid>
{
    public string OrderNumber { get; private set; }
    public OrderStatus Status { get; private set; }

    // Domain logic only, no infrastructure
    public void Confirm()
    {
        if (Status != OrderStatus.Pending)
            throw new BusinessException(OrderDomainErrorCodes.OrderNotPending);

        Status = OrderStatus.Confirmed;
        AddDistributedEvent(new OrderConfirmedEto { OrderId = Id });
    }
}

// Infrastructure concerns in EntityFrameworkCore layer
// In YourProject.EntityFrameworkCore/EntityConfigurations/OrderConfiguration.cs
public class OrderConfiguration : IEntityTypeConfiguration<Order>
{
    public void Configure(EntityTypeBuilder<Order> builder)
    {
        builder.ToTable("Orders");
        builder.HasIndex(x => x.OrderNumber);  // Index here, not in domain

        builder.OwnsMany(x => x.Items, items =>
        {
            items.ToTable("OrderItems");
            items.WithOwner().HasForeignKey(x => x.OrderId);
        });
    }
}
```

### 2. Layer Responsibility Violations

**Clean Architecture Principle**: Each layer has specific responsibilities. Business logic belongs in domain, use cases in application.

```
Grep patterns:
- "AppService.*if.*Status.*=="           # Business rules in app service
- "Controller.*new.*Entity"              # Entity creation in controller
- "DbContext.*Domain"                    # DbContext in domain
```

**Check for:**
- Business rules in application services
- Domain logic in controllers
- Data access logic in application layer
- Validation logic scattered across layers
- Missing use case encapsulation

**Fix Pattern:**
```csharp
// ❌ Wrong: Business logic scattered across layers
// Controller with business logic
[HttpPost]
public async Task<OrderDto> CreateOrder(CreateOrderInput input)
{
    if (input.TotalAmount > 10000)  // Business rule in controller!
        throw new BusinessException("Order too large");

    var order = new Order();  // Direct entity creation
    order.Status = OrderStatus.Pending;
    return await _orderService.CreateAsync(order);
}

// Application service with domain logic
public class OrderAppService : ApplicationService
{
    public async Task ConfirmAsync(Guid orderId)
    {
        var order = await _repository.GetAsync(orderId);

        // Domain logic in application service (wrong!)
        if (order.Status != OrderStatus.Pending)
            throw new BusinessException("Cannot confirm");

        if (order.Items.Count == 0)
            throw new BusinessException("No items");

        order.Status = OrderStatus.Confirmed;
        order.ConfirmedDate = DateTime.UtcNow;
    }
}

// ✅ Correct: Clean layer separation
// Domain Layer: Business logic and rules
public class Order : AggregateRoot<Guid>
{
    public void Confirm()
    {
        // Business rules in domain
        if (Status != OrderStatus.Pending)
            throw new BusinessException(OrderDomainErrorCodes.OrderNotPending);

        if (!_items.Any())
            throw new BusinessException(OrderDomainErrorCodes.OrderHasNoItems);

        Status = OrderStatus.Confirmed;
        ConfirmedDate = Clock.Now;

        AddDistributedEvent(new OrderConfirmedEto { OrderId = Id });
    }
}

// Application Layer: Use case orchestration
[Authorize(OrderPermissions.Confirm)]
public class OrderAppService : ApplicationService
{
    private readonly OrderManager _orderManager;
    private readonly IOrderRepository _orderRepository;

    public async Task ConfirmOrderAsync(Guid orderId)
    {
        // Thin orchestration, delegating to domain
        var order = await _orderRepository.GetAsync(orderId);
        order.Confirm();  // Domain handles business logic

        // Application service coordinates infrastructure
        await CurrentUnitOfWork.SaveChangesAsync();
    }
}

// Web Layer: HTTP concerns only
[ApiController]
[Route("api/orders")]
public class OrderController : AbpController
{
    private readonly IOrderAppService _orderAppService;

    [HttpPost("{id}/confirm")]
    public async Task<OrderDto> Confirm(Guid id)
    {
        // Controller just delegates to application service
        return await _orderAppService.ConfirmOrderAsync(id);
    }
}
```

### 3. Interface Adapter Violations

**Clean Architecture Principle**: Data crosses boundaries through DTOs/adapters. Domain entities should never cross layer boundaries.

```
Grep patterns:
- "return.*Entity<"                      # Returning entities
- "IActionResult.*\\(entity"             # Entity to HTTP response
- "Task<.*Entity>.*AppService"          # Entity return from app service
```

**Check for:**
- Entities returned from application services
- Entities serialized to JSON
- DTOs in domain layer
- Missing DTO-to-Entity mapping
- Entities in API contracts

**Fix Pattern:**
```csharp
// ❌ Wrong: Entity crossing boundaries
public class OrderAppService : ApplicationService
{
    // Returning domain entity (wrong!)
    public async Task<Order> GetOrderAsync(Guid id)
    {
        return await _orderRepository.GetAsync(id);
    }

    // Accepting entity as input (wrong!)
    public async Task UpdateAsync(Order order)
    {
        await _orderRepository.UpdateAsync(order);
    }
}

[ApiController]
public class OrderController : AbpController
{
    [HttpGet("{id}")]
    public async Task<Order> Get(Guid id)  // Entity in API!
    {
        return await _orderService.GetOrderAsync(id);
    }
}

// ✅ Correct: DTOs for data transfer
// Application.Contracts layer
public class OrderDto
{
    public Guid Id { get; set; }
    public string OrderNumber { get; set; }
    public string CustomerName { get; set; }
    public OrderStatus Status { get; set; }
    public decimal TotalAmount { get; set; }
    public List<OrderItemDto> Items { get; set; }
}

public class CreateOrderDto
{
    [Required]
    public Guid CustomerId { get; set; }

    [Required]
    [MinLength(1)]
    public List<CreateOrderItemDto> Items { get; set; }
}

// Application layer
public class OrderAppService : ApplicationService, IOrderAppService
{
    public async Task<OrderDto> GetAsync(Guid id)
    {
        var order = await _orderRepository.GetAsync(id);
        return ObjectMapper.Map<Order, OrderDto>(order);  // DTO boundary
    }

    public async Task<OrderDto> CreateAsync(CreateOrderDto input)
    {
        var order = await _orderManager.CreateOrderAsync(
            input.CustomerId,
            input.Items);

        await _orderRepository.InsertAsync(order);

        return ObjectMapper.Map<Order, OrderDto>(order);
    }
}

// AutoMapper profile
public class OrderApplicationAutoMapperProfile : Profile
{
    public OrderApplicationAutoMapperProfile()
    {
        CreateMap<Order, OrderDto>();
        CreateMap<OrderItem, OrderItemDto>();
    }
}
```

## ABP Framework Anti-Patterns & Issues

### 1. Async/Sync Violations

**Critical Anti-Pattern**: Calling `async` methods from `sync` methods leads to deadlocks and performance issues.

```
Grep patterns:
- "public void.*\\.Wait\\(\\)"          # .Wait() on Task
- "public void.*\\.Result"              # .Result on Task
- "\\.GetAwaiter\\(\\)\\.GetResult\\(\\)"  # GetAwaiter().GetResult()
- "Task\\.Run\\(.*await"                # Task.Run with await inside
```

**Check for:**
- Non-async application service methods
- Non-async repository custom methods
- Sync methods calling async ABP infrastructure
- Missing `async Task` return types on controllers/services

**Fix Pattern:**
```csharp
// ❌ Wrong: Sync over async
public void UpdateOrder(Guid id)
{
    var order = _orderRepository.GetAsync(id).Result; // Deadlock risk
    order.Confirm();
}

// ✅ Correct: Async first
public async Task UpdateOrderAsync(Guid id)
{
    var order = await _orderRepository.GetAsync(id);
    order.Confirm();
}
```

### 2. Repository & Aggregate Loading Issues

**Critical Performance Problem**: Loading entire aggregates when only subset needed.

```
Grep patterns:
- "Include\\(.*\\)\\.Include"           # Multiple eager loads
- "ThenInclude"                          # Nested eager loading
- "GetAsync.*\\)\\.Include"              # Generic get with includes
- "IncludeDetails.*true"                 # Auto-include everything
```

**Check for:**
- Generic `GetAsync(id)` with eager loading for all operations
- Missing purpose-built repository methods
- Loading navigation properties unnecessarily
- N+1 query problems from lazy loading

**Fix Pattern:**
```csharp
// ❌ Wrong: Loading entire aggregate for simple operation
public async Task ConfirmOrderAsync(Guid orderId)
{
    var order = await _orderRepository
        .Include(o => o.Items)
        .Include(o => o.Customer)
        .Include(o => o.Payments)
        .FirstOrDefaultAsync(o => o.Id == orderId); // Loads everything

    order.Confirm(); // Only needs order status field
}

// ✅ Correct: Purpose-built method
public async Task ConfirmOrderAsync(Guid orderId)
{
    var order = await _orderRepository.GetForConfirmationAsync(orderId);
    order.Confirm();
}

// In repository:
public async Task<Order> GetForConfirmationAsync(Guid id)
{
    return await (await GetQueryableAsync())
        .Where(o => o.Id == id)
        .FirstOrDefaultAsync(); // Only loads Order table, no joins
}
```

### 3. Inefficient Query & Read Operations

**Performance Issue**: Using aggregates for read-only queries instead of optimized projections.

```
Grep patterns:
- "GetListAsync.*ObjectMapper\\.Map"    # Mapping entities to DTOs
- "await.*ToListAsync\\(\\).*Select"    # ToList before projection
- "GetListAsync\\(\\).*Where"           # In-memory filtering
```

**Check for:**
- Reading aggregates then mapping to DTOs
- Missing database-level filtering/sorting/pagination
- Using repository for reporting queries
- Not using `IQueryable` projections

**Fix Pattern:**
```csharp
// ❌ Wrong: Loading entities then mapping
public async Task<List<OrderDto>> GetOrdersAsync()
{
    var orders = await _orderRepository.GetListAsync(); // Loads all columns
    return ObjectMapper.Map<List<Order>, List<OrderDto>>(orders);
}

// ✅ Correct: Database projection
public async Task<List<OrderDto>> GetOrdersAsync()
{
    var queryable = await _orderRepository.GetQueryableAsync();
    return await queryable
        .Select(o => new OrderDto
        {
            Id = o.Id,
            CustomerName = o.Customer.Name, // Efficient JOIN
            Total = o.TotalAmount
        })
        .ToListAsync(); // Executes single optimized query
}
```

### 4. DbContext Direct Usage in Application Layer

**Architectural Violation**: Bypassing repository abstraction.

```
Grep patterns:
- "private.*DbContext"                   # DbContext in app service
- "\\[Inject\\].*DbContext"              # DI DbContext directly
- "_dbContext\\.Set<"                    # Direct DbSet access
- "DbContext.*_context"                  # DbContext field
```

**Check for:**
- DbContext injected into application services
- Direct `DbSet<T>` usage outside repositories
- Breaking repository pattern abstraction
- Missing unit of work boundaries

**Fix Pattern:**
```csharp
// ❌ Wrong: DbContext in application service
public class OrderAppService : ApplicationService
{
    private readonly MyDbContext _dbContext;

    public OrderAppService(MyDbContext dbContext)
    {
        _dbContext = dbContext; // Violation
    }

    public async Task CreateAsync(OrderDto dto)
    {
        await _dbContext.Orders.AddAsync(new Order()); // Wrong layer
    }
}

// ✅ Correct: Use repository
public class OrderAppService : ApplicationService
{
    private readonly IOrderRepository _orderRepository;

    public OrderAppService(IOrderRepository orderRepository)
    {
        _orderRepository = orderRepository;
    }

    public async Task CreateAsync(OrderDto dto)
    {
        var order = new Order(/* params */);
        await _orderRepository.InsertAsync(order);
    }
}
```

### 5. Manual Unit of Work & Transaction Management

**Unnecessary Complexity**: Manually managing what ABP handles automatically.

```
Grep patterns:
- "SaveChanges\\(\\)"                    # Manual save
- "BeginTransaction"                     # Manual transaction
- "CommitTransaction"                    # Manual commit
- "using.*transaction"                   # Explicit transaction scope
```

**Check for:**
- `SaveChanges()` calls in app services
- Manual transaction creation
- Missing `[UnitOfWork]` attribute on non-service methods
- Incorrect understanding of ABP UoW lifecycle

**Fix Pattern:**
```csharp
// ❌ Wrong: Manual transaction management
public async Task ProcessOrderAsync(Guid orderId)
{
    using var transaction = await _dbContext.Database.BeginTransactionAsync();
    try
    {
        var order = await _orderRepository.GetAsync(orderId);
        order.Process();
        await _dbContext.SaveChangesAsync(); // Manual save
        await transaction.CommitAsync();
    }
    catch
    {
        await transaction.RollbackAsync();
        throw;
    }
}

// ✅ Correct: Let ABP handle UoW
public async Task ProcessOrderAsync(Guid orderId)
{
    var order = await _orderRepository.GetAsync(orderId);
    order.Process();
    // ABP auto-saves and commits on method exit
    // Auto-rollback on exception
}
```

### 6. Inter-Application Service Calls

**Architectural Smell**: Application services calling each other within same module.

```
Grep patterns:
- "private.*ApplicationService"          # App service dependency
- "I.*AppService.*_.*Service"            # App service injection
- "\\[Inject\\].*AppService"             # DI another app service
```

**Check for:**
- Application service depending on another app service in same module
- Circular dependencies between services
- Business logic scattered across services
- Missing domain service layer

**Fix Pattern:**
```csharp
// ❌ Wrong: App service calling app service
public class OrderAppService : ApplicationService
{
    private readonly ICustomerAppService _customerAppService;

    public async Task CreateOrderAsync(CreateOrderDto input)
    {
        var customer = await _customerAppService.GetAsync(input.CustomerId); // Wrong
    }
}

// ✅ Correct: Share domain services or repositories
public class OrderAppService : ApplicationService
{
    private readonly ICustomerRepository _customerRepository;
    private readonly OrderManager _orderManager; // Domain service

    public async Task CreateOrderAsync(CreateOrderDto input)
    {
        var customer = await _customerRepository.GetAsync(input.CustomerId);
        var order = await _orderManager.CreateAsync(customer, input.Items);
    }
}
```

### 7. Exposing Entities Instead of DTOs

**Security & Coupling Issue**: Returning domain entities from application services.

```
Grep patterns:
- "Task<.*Entity>"                       # Entity return type
- "Task<List<.*Entity>>"                 # Entity list return
- "IActionResult.*\\(entity\\)"          # Entity to controller
- "return.*new.*Entity\\("               # Entity construction in app service
```

**Check for:**
- Methods returning `Entity` types instead of DTOs
- Entities serialized to JSON responses
- Missing DTO mapping layer
- Auto-exposing all entity properties

**Fix Pattern:**
```csharp
// ❌ Wrong: Returning entity
public async Task<Order> GetOrderAsync(Guid id)
{
    return await _orderRepository.GetAsync(id); // Exposes internal state
}

// ✅ Correct: Return DTO
public async Task<OrderDto> GetOrderAsync(Guid id)
{
    var order = await _orderRepository.GetAsync(id);
    return ObjectMapper.Map<Order, OrderDto>(order);
}
```

### 8. Missing Data Validation & Authorization

**Security Risk**: Trusting client input without validation.

```
Grep patterns:
- "public.*Task.*Async\\(.*Dto"          # Methods with DTOs
- "\\[Authorize\\("                      # Authorization attributes
- "await CheckPolicyAsync"               # Permission checks
- "AuthorizationService"                 # Authorization service
```

**Check for:**
- Application service methods without `[Authorize]` or permission checks
- Missing input validation on DTOs
- No validation in entity constructors
- Unguarded destructive operations

**Fix Pattern:**
```csharp
// ❌ Wrong: No authorization or validation
public async Task DeleteAsync(Guid id)
{
    await _orderRepository.DeleteAsync(id); // Anyone can delete!
}

// ✅ Correct: Authorization and validation
[Authorize(OrderPermissions.Delete)]
public async Task DeleteAsync(Guid id)
{
    await CheckDeletePermissionAsync(); // Custom business rule
    var order = await _orderRepository.GetAsync(id);

    if (order.IsProcessed)
        throw new BusinessException("Cannot delete processed order");

    await _orderRepository.DeleteAsync(order);
}
```

### 9. Distributed Event Publishing Issues

**Consistency Risk**: Publishing events before transaction commits.

```
Grep patterns:
- "PublishAsync.*IDistributedEventBus"   # Distributed event publishing
- "EventBus.*Publish"                    # Event bus usage
- "LocalEventBus"                        # Local vs distributed
- "\\[UnitOfWork.*IsDisabled = true"    # Disabled UoW
```

**Check for:**
- Publishing distributed events with `publishAsync: true` immediately
- Missing transactional outbox pattern configuration
- Events published before data committed
- Not differentiating local vs distributed events

**Fix Pattern:**
```csharp
// ❌ Wrong: Immediate publishing (inconsistency risk)
public async Task CreateOrderAsync(CreateOrderDto input)
{
    var order = new Order(input.CustomerId);
    await _orderRepository.InsertAsync(order);

    await _distributedEventBus.PublishAsync(
        new OrderCreatedEto { OrderId = order.Id },
        publishAsync: true // Published before DB commit!
    );
    // If transaction fails after this, event already published
}

// ✅ Correct: Publish at UoW end (default behavior)
public async Task CreateOrderAsync(CreateOrderDto input)
{
    var order = new Order(input.CustomerId);
    await _orderRepository.InsertAsync(order);

    await _distributedEventBus.PublishAsync(
        new OrderCreatedEto { OrderId = order.Id }
        // Default: publishes at end of UoW, just before commit
    );
}

// ✅ Best: Enable transactional outbox in module config
Configure<AbpDistributedEventBusOptions>(options =>
{
    options.Outboxes.Configure(config =>
    {
        config.UseDbContext<MyDbContext>(); // Guarantees consistency
    });
});
```

### 10. Caching Issues

**Performance Problem**: Missing or incorrect caching implementation.

```
Grep patterns:
- "IDistributedCache"                    # Cache usage
- "GetOrAddAsync"                        # Cache retrieval
- "RemoveAsync.*cache"                   # Cache invalidation
- "\\[DisableUnitOfWork\\]"              # Methods that should use cache
```

**Check for:**
- Frequently accessed data without caching
- Missing cache invalidation on updates
- Caching entities instead of DTOs
- Cache key collision risks
- No TTL configuration

**Fix Pattern:**
```csharp
// ❌ Wrong: No caching for frequently accessed data
public async Task<ConfigDto> GetConfigAsync()
{
    var config = await _configRepository.FirstOrDefaultAsync(); // DB hit every time
    return ObjectMapper.Map<Config, ConfigDto>(config);
}

// ✅ Correct: Implement caching
public async Task<ConfigDto> GetConfigAsync()
{
    return await _distributedCache.GetOrAddAsync(
        CacheKeys.AppConfig,
        async () =>
        {
            var config = await _configRepository.FirstOrDefaultAsync();
            return ObjectMapper.Map<Config, ConfigDto>(config);
        },
        () => new DistributedCacheEntryOptions
        {
            AbsoluteExpiration = DateTimeOffset.Now.AddHours(1)
        }
    );
}

// Don't forget invalidation
public async Task UpdateConfigAsync(UpdateConfigDto input)
{
    var config = await _configRepository.FirstOrDefaultAsync();
    ObjectMapper.Map(input, config);
    await _distributedCache.RemoveAsync(CacheKeys.AppConfig); // Invalidate
}
```

### 11. Memory Leak Patterns

**Resource Management**: Unclosed resources and event handler leaks.

```
Grep patterns:
- "IDisposable"                          # IDisposable implementation
- "Subscribe\\("                         # Event subscriptions
- "\\+=.*Handler"                        # Event handler registration
- "HttpClient.*new"                      # HttpClient creation
- "StreamReader|StreamWriter"            # Stream usage
```

**Check for:**
- Missing `Dispose()` calls on IDisposable objects
- Event handlers not unsubscribed
- HttpClient instantiation instead of IHttpClientFactory
- Database connections not disposed
- Large objects in memory without cleanup

**Fix Pattern:**
```csharp
// ❌ Wrong: Resource leak
public async Task ProcessFileAsync(string path)
{
    var reader = new StreamReader(path); // Never disposed
    var content = await reader.ReadToEndAsync();
    // Process content
}

// ✅ Correct: Proper disposal
public async Task ProcessFileAsync(string path)
{
    using var reader = new StreamReader(path);
    var content = await reader.ReadToEndAsync();
    // Auto-disposed
}
```

### 12. Violation of DRY Principle

**Code Duplication**: Meaningful repetition across modules.

```
Grep patterns:
- "ObjectMapper\\.Map.*ObjectMapper\\.Map"  # Repeated mapping logic
- "CheckPolicyAsync.*CheckPolicyAsync"       # Duplicated auth checks
- "ValidationException.*ValidationException" # Repeated validation
```

**Check for:**
- Duplicate validation logic across services
- Repeated authorization patterns
- Copy-pasted business rules
- Missing shared domain services
- Redundant DTO mapping configurations

**Fix Pattern:**
```csharp
// ❌ Wrong: Duplicated validation
public class CreateOrderDto
{
    public string CustomerEmail { get; set; }
}

public class OrderAppService
{
    public async Task CreateAsync(CreateOrderDto input)
    {
        if (!Regex.IsMatch(input.CustomerEmail, @"^[^@]+@[^@]+\.[^@]+$"))
            throw new ValidationException("Invalid email");
    }
}

public class CustomerAppService
{
    public async Task CreateAsync(CreateCustomerDto input)
    {
        if (!Regex.IsMatch(input.Email, @"^[^@]+@[^@]+\.[^@]+$")) // Duplicate!
            throw new ValidationException("Invalid email");
    }
}

// ✅ Correct: Shared validation
public class EmailValidator : IEmailValidator
{
    public bool IsValid(string email) =>
        !string.IsNullOrEmpty(email) &&
        Regex.IsMatch(email, @"^[^@]+@[^@]+\.[^@]+$");
}

// Use in DTOs with FluentValidation or data annotations
```

### 13. Incorrect Dependency Injection Lifetimes

**Concurrency Issues**: Wrong service lifetimes causing state issues.

```
Grep patterns:
- "AddSingleton<.*Repository>"           # Singleton repository (wrong)
- "AddScoped<.*Manager>"                 # Scoped domain service
- "AddTransient<.*DbContext>"            # Transient DbContext (wrong)
```

**Check for:**
- Repositories registered as Singleton
- DbContext not using Scoped lifetime
- Stateful services registered as Singleton
- Per-request services as Singleton

**ABP Default Lifetimes:**
- Repositories: Transient
- Application Services: Transient
- Domain Services: Transient
- DbContext: Scoped (via ABP)

### 14. Anemic Domain Model

**DDD Violation**: Entities as data bags without behavior.

```
Grep patterns:
- "class.*Entity.*\\{.*\\{ get; set; \\}.*\\}"  # Only properties
- "public set"                                    # Public setters everywhere
```

**Check for:**
- Entities with only getters/setters
- Business logic in application services instead of domain
- Missing entity methods
- Public setters exposing internal state

**Fix Pattern:**
```csharp
// ❌ Wrong: Anemic entity
public class Order : Entity<Guid>
{
    public string Status { get; set; } // Public setter
    public decimal Total { get; set; }
    public DateTime? ConfirmedDate { get; set; }
}

// In app service (wrong place for logic):
public async Task ConfirmAsync(Guid orderId)
{
    var order = await _repository.GetAsync(orderId);
    order.Status = "Confirmed"; // Direct state manipulation
    order.ConfirmedDate = DateTime.UtcNow;
}

// ✅ Correct: Rich domain entity
public class Order : Entity<Guid>
{
    public OrderStatus Status { get; private set; } // Private setter
    public decimal Total { get; private set; }
    public DateTime? ConfirmedDate { get; private set; }

    public void Confirm()
    {
        if (Status != OrderStatus.Pending)
            throw new BusinessException("Only pending orders can be confirmed");

        Status = OrderStatus.Confirmed;
        ConfirmedDate = Clock.Now;

        AddDistributedEvent(new OrderConfirmedEto { OrderId = Id });
    }
}

// In app service (thin orchestration):
public async Task ConfirmAsync(Guid orderId)
{
    var order = await _repository.GetAsync(orderId);
    order.Confirm(); // Business logic in entity
}
```

## .NET Code Quality Issues

### 1. LINQ Performance Anti-patterns

```
Grep patterns:
- "\\.ToList\\(\\)\\.Where"              # ToList before filtering
- "\\.ToList\\(\\)\\.Select"             # ToList before projection
- "\\.Any\\(\\).*\\.Count\\(\\)"         # Count when Any sufficient
- "for.*Count\\(\\)"                     # Count in loop condition
```

### 2. Exception Handling Issues

```
Grep patterns:
- "catch.*\\{\\s*\\}"                    # Empty catch blocks
- "catch.*Exception.*throw;"             # Catching then rethrowing
- "throw ex;"                            # Losing stack trace
```

### 3. String Manipulation Performance

```
Grep patterns:
- "\\+.*\\+.*\\+"                        # String concatenation in loop
- "string\\.Concat.*foreach"             # Inefficient concatenation
- "Substring.*Substring"                 # Multiple substring calls
```

## Execution Steps

1. **Explore Codebase Structure:**
   ```
   Use Task tool (Explore agent, "very thorough") to:
   - Identify ABP version (check .csproj files for Volo.Abp.* packages)
   - Map layer structure (Domain, Application, EntityFrameworkCore, HttpApi, etc.)
   - Locate module configuration files (*Module.cs)
   - Find repositories, application services, entities, domain services
   - Identify aggregate roots, value objects, and domain events
   - Map bounded contexts and module boundaries
   - Assess project scale (single module vs modular monolith vs microservices)
   ```

2. **Validate DDD Tactical Patterns** (use PATTERNS.md for grep patterns):
   - **Entity design**: Rich vs anemic domain models, invariant protection, private setters
   - **Value objects**: Immutability, validation, primitive obsession detection
   - **Aggregates**: Consistency boundaries, size validation (>5-7 entities), cross-aggregate references
   - **Domain events**: Placement in entities vs application services, event-driven architecture
   - **Domain services**: Multi-aggregate coordination, business logic placement vs application services
   - **Repository pattern**: Collection-like interfaces, domain layer placement (not infrastructure)
   - **Primitive obsession**: Missing value objects for Email, Phone, Money, Address, etc.

3. **Validate Clean Architecture Principles:**
   - **Dependency rule**: Dependencies point inward (Domain → Application → Infrastructure → Web)
   - **Layer responsibilities**: Domain (business logic), Application (use cases), Infrastructure (I/O), Web (HTTP)
   - **Interface adapters**: DTO usage, entity boundary protection, no entities in API responses
   - **Infrastructure isolation**: Zero EF Core, HttpClient, or System.IO dependencies in domain
   - **Use case encapsulation**: Application services as thin orchestrators, not business logic containers

4. **Execute Performance & Scalability Scans** (reference REFERENCE.md Section I):
   - **Async/sync violations**: `.Wait()`, `.Result`, `GetAwaiter().GetResult()` (CRITICAL)
   - **N+1 queries**: Repository calls inside loops, missing eager loading or projections
   - **In-memory cache**: `IMemoryCache` usage in scaled apps (should use `IDistributedCache`)
   - **Unbounded collections**: `GetListAsync()` without pagination, missing `MaxResultCount`
   - **Magic strings/numbers**: Hardcoded literals, missing constants in Domain.Shared
   - **LINQ inefficiencies**: `.ToList().Where()`, `.Count() > 0` instead of `.Any()`

5. **Execute Security Scans** (reference REFERENCE.md Section II):
   - **SQL injection**: `FromSqlRaw()` with string interpolation or concatenation (CRITICAL)
   - **Missing authorization**: Application service methods without `[Authorize]` attribute
   - **Entity exposure**: Returning `Entity<Guid>` or `AggregateRoot<Guid>` instead of DTOs
   - **Client-side authorization**: Relying on UI checks without server-side enforcement
   - **Insecure configuration**: Hardcoded secrets, default JWT keys, passwords in appsettings.json

6. **Execute Architectural Scans** (reference REFERENCE.md Section III):
   - **Domain service persistence**: Domain services calling `InsertAsync()` or `SaveChangesAsync()`
   - **Application service domain logic**: Complex business rules in app services vs domain
   - **Controller repository access**: Controllers injecting `IRepository<T>` (bypassing app layer)
   - **Domain layer external dependencies**: `using EntityFrameworkCore` in Domain project
   - **Missing DTOs**: Entities as input parameters in application service methods

7. **Execute Maintainability Scans** (reference REFERENCE.md Section IV):
   - **Anemic domain models**: Entities with only properties, no behavior methods (HIGH priority)
   - **Overly large aggregates**: >5-7 child collections, >200 lines of code
   - **Over-abstraction**: Generic repositories wrapping `IRepository`, interfaces with single implementation
   - **Catch-all exception handling**: `catch (Exception e)` with `throw e;` (loses stack trace)
   - **Premature microservices**: 10+ tightly coupled services with synchronous HTTP calls

8. **Execute Observability Scans** (reference REFERENCE.md Section V):
   - **Non-structured logging**: String interpolation in `LogInformation()` vs structured placeholders
   - **Missing exception mapping**: Generic exceptions vs ABP's `BusinessException`
   - **Module dependencies**: Domain depending on Application (check .csproj references)
   - **Configuration centralization**: Magic strings in `IConfiguration` access
   - **Explicit transactions**: Unnecessary `BeginTransaction()` in application services

9. **Validate Repository & Data Access:**
   - Eager loading chains (`Include().Include()`)
   - DbContext direct usage in application layer
   - Manual `SaveChanges()` or transaction management
   - Missing purpose-built repository methods
   - Query logic scattered in application services

10. **Generate Comprehensive Report** (follow format in REFERENCE.md):
    - **Group by severity**: Critical → High → Medium → Low
    - **Categorize by type**:
      - DDD Violations (anemic models, missing value objects, aggregate issues)
      - Clean Architecture Violations (dependency rules, layer violations)
      - ABP Anti-Patterns (async/sync, caching, authorization)
      - Performance Issues (N+1 queries, LINQ, unbounded collections)
      - Security Issues (SQL injection, missing auth, data exposure)
    - **Include for each finding**:
      - File paths with line numbers (`path/to/file.cs:123`)
      - DDD/Clean Architecture principle violated
      - Impact and consequences
      - ❌ Current code (problematic)
      - ✅ Recommended fix (2025 best practice)
      - References to ABP docs and DDD principles
    - **Architectural recommendations**:
      - Domain richness assessment
      - Bounded context identification
      - Refactoring opportunities
      - Technology upgrade recommendations

## Reporting Format

For each issue:

```markdown
### [SEVERITY] Issue Title

**Location:** `path/to/file.cs:123`

**Category:** [DDD Violation | Clean Architecture Violation | ABP Anti-Pattern | Performance | Security | Architecture]

**DDD/Clean Architecture Principle:**
[Which principle or pattern is violated, if applicable]

**Problem:**
[Specific description of the issue]

**Impact:**
[Consequences if not fixed - technical debt, maintainability, performance, security]

**Fix:**
```csharp
// ❌ Current (problematic)
[current code]

// ✅ Recommended (2025 best practice)
[fixed code with explanation following DDD/Clean Architecture principles]
```

**References:**
- [Link to relevant ABP docs]
- [DDD principle reference]
- [Clean Architecture principle]
```

## Severity Classification

- **Critical**:
  - Data corruption risks, deadlocks, security vulnerabilities
  - Major DDD violations (anemic domain models with complex business logic in services)
  - Clean Architecture dependency rule violations (domain depending on infrastructure)
  - Aggregate boundary violations causing data inconsistency
  - Entity exposure across layer boundaries

- **High**:
  - Performance degradation, memory leaks
  - Missing domain logic in entities (business rules in application services)
  - Value object mutability
  - Missing authorization or input validation
  - Repository pattern violations (interfaces in wrong layer)
  - Domain events published from wrong layer
  - Cross-aggregate direct references

- **Medium**:
  - Code duplication, missing domain services
  - Inefficient queries, primitive obsession
  - Missing value objects for domain concepts
  - Coupling issues between application services
  - Incomplete aggregate design
  - Missing purpose-specific repository methods

- **Low**:
  - Code style inconsistencies
  - Minor optimizations
  - Documentation gaps
  - Missing XML comments on public APIs

## Important Notes

- **DDD Focus**: Prioritize identifying anemic domain models and business logic in wrong layers
- **Clean Architecture**: Validate dependency rules strictly - domain must be pure
- **ABP Conventions**: Consider ABP's DDD implementation and framework conventions
- **Context Reading**: Always read actual code to confirm issues before reporting
- **ABP Versions**: Account for differences (v4.x vs v5.x vs v7.x vs v8.x)
- **Framework vs User Code**: Focus on user-written code, not ABP framework internals
- **Prioritization**: Architectural violations > DDD violations > Performance > Style
- **2025 Standards**: Apply modern best practices (immutable value objects, small aggregates, domain events)
- **Bounded Contexts**: Identify implicit bounded contexts and recommend modularization
- **Documentation**: Reference official ABP docs, DDD patterns, and Clean Architecture principles

## Strategic Analysis Guidelines

When analyzing large ABP projects:

1. **Identify Bounded Contexts**: Look for natural domain boundaries in the codebase
2. **Validate Aggregates**: Check if aggregates are properly scoped and not too large
3. **Layer Dependency Graph**: Map dependencies to find Clean Architecture violations
4. **Domain Richness Assessment**: Measure ratio of domain logic in entities vs services
5. **Event-Driven Architecture**: Evaluate usage of domain events for decoupling

## Example Activation Phrases

User asks:
- "Analyze this ABP project for code issues"
- "Scan my ABP codebase for anti-patterns"
- "Review this ABP Framework project for DDD violations"
- "Check ABP best practices violations"
- "Audit this .NET ABP application for Clean Architecture compliance"
- "Find performance issues in ABP project"
- "Validate my domain model design"
- "Check if my entities are anemic"
- "Review aggregate boundaries in my project"
- "Analyze Clean Architecture layers"
- "Scan for DDD tactical pattern violations"
- "Audit domain-driven design implementation"

Activate this skill and perform comprehensive ABP-focused analysis with DDD and Clean Architecture validation.
