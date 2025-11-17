# Code Review Report

## Summary
- **Result**: CRITICAL_ISSUES_FOUND
- **Files Scanned**: 12
- **Critical Issues**: 3
- **High Issues**: 1

## Critical Issues

### SQL Injection via String Concatenation
- **File**: `src/Acme.BookStore.Application/Books/BookAppService.cs:45`
- **Severity**: CRITICAL
- **Confidence**: 100
- **Problem**: SQL query built using string concatenation with user-supplied search term parameter. The searchTerm variable is directly interpolated into the SQL command without any parameterization or escaping.
- **Why Critical**: Enables SQL injection attacks where malicious users can inject arbitrary SQL commands to extract, modify, or delete database data. Attackers can bypass application logic, dump entire databases, or execute administrative commands depending on database permissions. This is a textbook OWASP Top 10 vulnerability (A03:2021 - Injection).
- **Code Snippet**:
```csharp
public async Task<List<BookDto>> SearchBooksAsync(string searchTerm)
{
    var query = $"SELECT * FROM Books WHERE Title LIKE '%{searchTerm}%'";
    var books = await _dbContext.Database.ExecuteSqlRawAsync(query);
    return ObjectMapper.Map<List<Book>, List<BookDto>>(books);
}
```
- **Git Context**: Commit abc123f "Implement book search functionality" (Backend Dev, 2025-11-15 10:23:45)

---

### Multi-Tenancy Filtering Removed
- **File**: `src/Acme.BookStore.Domain/Orders/Order.cs:8`
- **Severity**: CRITICAL
- **Confidence**: 100
- **Problem**: The IMultiTenant interface and TenantId property were removed from the Order entity, breaking tenant isolation in a multi-tenant SaaS application.
- **Why Critical**: All tenants can now access each other's order data. This is a catastrophic data leak in multi-tenant architecture where tenant isolation is a fundamental security requirement. Violates data privacy regulations (GDPR, HIPAA if applicable) and breaks the core business model of isolated tenant environments. Every query will now return orders across all tenants.
- **Code Snippet**:
```csharp
// Before (implied from diff)
public class Order : AggregateRoot<Guid>, IMultiTenant
{
    public Guid? TenantId { get; set; }
    // ... other properties
}

// After (current code)
public class Order : AggregateRoot<Guid>
{
    // TenantId removed - no tenant isolation!
    public string OrderNumber { get; set; }
    public decimal TotalAmount { get; set; }
}
```
- **Git Context**: Commit def456g "Refactor Order entity for simplification" (Senior Dev, 2025-11-16 14:12:30)

---

### Hardcoded Production Database Password
- **File**: `src/Acme.BookStore.DbMigrator/appsettings.json:5`
- **Severity**: CRITICAL
- **Confidence**: 100
- **Problem**: Production database connection string containing real SQL Server admin credentials (sa user) committed directly to the repository.
- **Why Critical**: Production database credentials are now exposed to anyone with repository access and permanently stored in git history. Attackers gaining repo access can connect directly to production database, bypassing all application security. Credentials must be rotated immediately and moved to secure secret management (Azure Key Vault, environment variables, etc.).
- **Code Snippet**:
```json
{
  "ConnectionStrings": {
    "Default": "Server=prod-sql.company.com;Database=BookStore_Prod;User Id=sa;Password=P@ssw0rd123!Prod;Encrypt=true;TrustServerCertificate=false"
  }
}
```
- **Git Context**: Commit ghi789h "Add production config for deployment testing" (DevOps Engineer, 2025-11-13 09:45:12)

---

## High Issues

### [AllowAnonymous] on Payment Endpoint
- **File**: `src/Acme.BookStore.HttpApi/Controllers/PaymentController.cs:23`
- **Severity**: HIGH
- **Confidence**: 95
- **Problem**: Payment processing endpoint decorated with [AllowAnonymous] attribute, removing authentication requirement.
- **Why Critical**: Unauthenticated users can submit payment requests without proving identity. Prevents audit logging of who initiated payments, violates PCI DSS compliance requirements for authenticated transactions, and enables abuse such as fake payment submissions or payment information harvesting. Commit message suggests this was "temporary for testing" but was never reverted.
- **Code Snippet**:
```csharp
[HttpPost]
[Route("api/payment/process")]
[AllowAnonymous]  // ← Removed authentication
public async Task<PaymentResultDto> ProcessPaymentAsync(PaymentRequestDto request)
{
    var result = await _paymentService.ProcessAsync(request);
    return result;
}
```
- **Git Context**: Commit jkl012m "Temporarily remove auth for payment testing" (External Contractor, 2025-11-14 16:30:22)

---

## Files Changed

| File | Changes | Status |
|------|---------|--------|
| `src/Acme.BookStore.Application/Books/BookAppService.cs` | +8/-2 | Added SQL concatenation search method |
| `src/Acme.BookStore.Domain/Orders/Order.cs` | +0/-2 | Removed IMultiTenant interface and TenantId |
| `src/Acme.BookStore.DbMigrator/appsettings.json` | +5/-1 | Added production connection string |
| `src/Acme.BookStore.HttpApi/Controllers/PaymentController.cs` | +1/-0 | Added [AllowAnonymous] attribute |
| `src/Acme.BookStore.Application.Contracts/Books/BookDto.cs` | +3/-0 | Added search response fields |
| `src/Acme.BookStore.EntityFrameworkCore/Migrations/20251116_AddOrderIndex.cs` | +12/-0 | Added database index |

## Scan Coverage
- **Next.js files reviewed**: 0
- **.NET C# files reviewed**: 12
- **Total changed lines**: 467
- **False positives filtered**: 8 (Test files with mock credentials, development launchSettings.json)
