# Code Review Report

## Summary
- **Result**: CRITICAL_ISSUES_FOUND
- **Files Scanned**: 12
- **Critical Issues**: 4
- **High-Confidence Issues**: 4

## Critical Issues

### SQL Injection via String Concatenation
- **File**: `src/Acme.BookStore.Application/Books/BookAppService.cs:45`
- **Severity**: CRITICAL
- **Confidence**: 100
- **Problem**: SQL query built using string concatenation with user input
- **Why Critical**: Allows SQL injection, attackers can extract/modify/delete database data
- **Code Snippet**:
```csharp
var query = $"SELECT * FROM Books WHERE Title LIKE '%{searchTerm}%'";
var books = await _dbContext.Database.ExecuteSqlRawAsync(query);
```
- **Git Context**: Added by backend-dev@company.com on 2025-11-15 in commit jkl012i "Implement book search"
---

### [AllowAnonymous] on Payment Endpoint
- **File**: `src/Acme.BookStore.HttpApi/Controllers/PaymentController.cs:23`
- **Severity**: CRITICAL
- **Confidence**: 95
- **Problem**: Payment processing endpoint allows unauthenticated access
- **Why Critical**: Anyone can submit payments, no audit trail, violates PCI compliance
- **Code Snippet**:
```csharp
[HttpPost]
[Route("api/payment/process")]
[AllowAnonymous]
public async Task<PaymentResultDto> ProcessPaymentAsync(PaymentRequestDto request)
```
- **Git Context**: Modified by contractor@external.com on 2025-11-14 in commit mno345p "Temporarily remove auth for testing" - NOTE: This appears to be temporary test code that wasn't reverted
---

### Multi-Tenancy Filtering Removed
- **File**: `src/Acme.BookStore.Domain/Orders/Order.cs:8`
- **Severity**: CRITICAL
- **Confidence**: 100
- **Problem**: `IMultiTenant` interface and TenantId property removed from Order entity
- **Why Critical**: Tenant data isolation broken, all tenants can see each other's orders
- **Code Snippet**:
```diff
-public class Order : AggregateRoot<Guid>, IMultiTenant
+public class Order : AggregateRoot<Guid>
-    public Guid? TenantId { get; set; }
```
- **Git Context**: Modified by senior-dev@company.com on 2025-11-16 in commit qrs678t "Refactor Order entity" - **CRITICAL**: Author may not have understood multi-tenancy implications
---

### Hardcoded Production Database Password
- **File**: `src/Acme.BookStore.DbMigrator/appsettings.json:5`
- **Severity**: CRITICAL
- **Confidence**: 100
- **Problem**: Production database connection string with real password in git
- **Why Critical**: Production DB credentials exposed to anyone with repo access, persists in git history
- **Code Snippet**:
```json
"ConnectionStrings": {
  "Default": "Server=prod-sql.company.com;Database=BookStore_Prod;User Id=sa;Password=P@ssw0rd123!Prod;..."
}
```
- **Git Context**: Added by devops@company.com on 2025-11-13 in commit uvw901x "Add production config for deployment"
---

## Scan Coverage
- **Next.js files reviewed**: 0
- **.NET C# files reviewed**: 12
- **Total changed lines**: 467
- **False positives filtered**: 8
## Immediate Actions Required
1. **Rotate database password** immediately (exposed in git commit uvw901x)
2. **Revert multi-tenancy change** in Order entity (commit qrs678t)
3. **Audit database access logs** since 2025-11-16 for unauthorized tenant data access
4. **Disable payment endpoint** until authentication is restored