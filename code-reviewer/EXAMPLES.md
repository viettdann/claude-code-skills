# Code Reviewer Skill - Usage Examples

This document provides real-world examples of using the Code Reviewer skill for various scenarios.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Security-Focused Reviews](#security-focused-reviews)
3. [Framework-Specific Reviews](#framework-specific-reviews)
4. [Merge Commit Reviews](#merge-commit-reviews)
5. [Performance Reviews](#performance-reviews)
6. [Incremental Reviews](#incremental-reviews)

---

## Basic Usage

### Example 1: Review Latest Commit

**User Request:**
```
Review my latest commit
```

**What Happens:**

1. Skill checks latest commit:
```bash
git log -1 --oneline
# abc1234 Add user authentication endpoint

git show --stat HEAD
# src/api/auth.ts | 45 ++++++++++++++++++++++++++++++++
# src/types/user.ts | 12 +++++++++
# 2 files changed, 57 insertions(+)
```

2. Reviews changed files
3. Provides detailed feedback

**Sample Output:**

```markdown
# Code Review: abc1234 - Add user authentication endpoint

## Summary
- **Files Reviewed**: 2 files
- **Lines Changed**: +57
- **Issues Found**: 3 (Critical: 1, High: 1, Medium: 1)
- **Overall Assessment**: Needs changes - critical security issue found

## Critical Issues

### [CRITICAL] SQL Injection Vulnerability
**File**: `src/api/auth.ts:23`
**Category**: Security
**Problem**: User input directly concatenated into SQL query without sanitization
**Impact**: Attackers can execute arbitrary SQL commands, leading to data breach

**Fix**:
```typescript
// ❌ Current (vulnerable)
const query = `SELECT * FROM users WHERE email = '${email}'`;
const user = await db.execute(query);

// ✅ Recommended (parameterized)
const query = 'SELECT * FROM users WHERE email = ?';
const user = await db.execute(query, [email]);
```

**References**:
- https://owasp.org/www-community/attacks/SQL_Injection
- https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html

---

## High Priority Issues

### [HIGH] Password Stored in Plain Text
**File**: `src/api/auth.ts:34`
**Category**: Security
**Problem**: Password stored without hashing
**Impact**: Database breach would expose all user passwords

**Fix**:
```typescript
// ❌ Current (insecure)
await db.execute('INSERT INTO users (email, password) VALUES (?, ?)',
  [email, password]);

// ✅ Recommended (hashed)
import bcrypt from 'bcrypt';
const hashedPassword = await bcrypt.hash(password, 10);
await db.execute('INSERT INTO users (email, password) VALUES (?, ?)',
  [email, hashedPassword]);
```

**References**: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

---

## Medium Priority Issues

### [MEDIUM] Missing Error Handling
**File**: `src/api/auth.ts:15`
**Category**: Code Quality
**Problem**: No try-catch block for database operations
**Impact**: Unhandled errors could crash the application or leak sensitive info

**Fix**:
```typescript
// ❌ Current (no error handling)
export async function loginUser(email: string, password: string) {
  const user = await db.execute(query, [email]);
  return user;
}

// ✅ Recommended (with error handling)
export async function loginUser(email: string, password: string) {
  try {
    const user = await db.execute(query, [email]);
    return user;
  } catch (error) {
    logger.error('Login failed:', { email, error: error.message });
    throw new Error('Login failed. Please try again.');
  }
}
```

---

## Positive Observations

- Good use of TypeScript types in `src/types/user.ts`
- Proper async/await usage
- Clear function naming

## Recommendations

1. **Immediate**: Fix SQL injection vulnerability before deploying
2. **Before merge**: Implement password hashing
3. **Soon**: Add comprehensive error handling
4. **Future**: Consider using an ORM like Prisma to prevent SQL issues

## Next Steps

- [ ] Fix critical SQL injection issue
- [ ] Implement bcrypt password hashing
- [ ] Add try-catch blocks for all async operations
- [ ] Add input validation for email format
- [ ] Write unit tests for authentication logic
```

---

## Security-Focused Reviews

### Example 2: Security Audit

**User Request:**
```
Review my code for security vulnerabilities
```

**Focus Areas:**
- SQL injection
- XSS vulnerabilities
- Hardcoded secrets
- Authentication/authorization issues
- Insecure cryptography

**Sample Finding:**

```markdown
### [CRITICAL] Hardcoded API Key
**File**: `src/config/api.ts:8`
**Category**: Security
**Problem**: API key hardcoded in source code
**Impact**: If code is leaked or repo made public, API key is compromised

**Fix**:
```typescript
// ❌ Current (hardcoded)
export const STRIPE_API_KEY = 'sk_live_51HxYz...';

// ✅ Recommended (environment variable)
export const STRIPE_API_KEY = process.env.STRIPE_API_KEY;

if (!STRIPE_API_KEY) {
  throw new Error('STRIPE_API_KEY environment variable is required');
}
```

**Additional Steps**:
1. Move key to `.env` file
2. Add `.env` to `.gitignore`
3. Rotate the exposed API key immediately
4. Use secret management service for production

**References**: https://owasp.org/www-project-top-ten/
```

---

## Framework-Specific Reviews

### Example 3: Next.js App Router Review

**User Request:**
```
Review my Next.js Server Actions for security
```

**Sample Finding:**

```markdown
### [HIGH] Unvalidated Form Input in Server Action
**File**: `app/actions/create-post.ts:12`
**Category**: Security
**Problem**: FormData values used without validation
**Impact**: Malicious input could cause XSS or data corruption

**Fix**:
```typescript
// ❌ Current (no validation)
'use server';

export async function createPost(formData: FormData) {
  const title = formData.get('title');
  const content = formData.get('content');

  await db.post.create({
    data: { title, content }
  });
}

// ✅ Recommended (with validation)
'use server';

import { z } from 'zod';

const PostSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(1).max(10000),
});

export async function createPost(formData: FormData) {
  // Validate input
  const rawData = {
    title: formData.get('title'),
    content: formData.get('content'),
  };

  const validationResult = PostSchema.safeParse(rawData);

  if (!validationResult.success) {
    return {
      error: 'Invalid input',
      details: validationResult.error.flatten()
    };
  }

  const { title, content } = validationResult.data;

  try {
    await db.post.create({
      data: { title, content }
    });
    return { success: true };
  } catch (error) {
    console.error('Failed to create post:', error);
    return { error: 'Failed to create post' };
  }
}
```

**References**:
- https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions
- https://github.com/colinhacks/zod
```

### Example 4: ABP Framework Review

**User Request:**
```
Review my ABP application service for best practices
```

**Sample Finding:**

```markdown
### [MEDIUM] Repository Pattern Violation
**File**: `src/services/OrderAppService.cs:45`
**Category**: Architecture
**Problem**: Direct DbContext usage instead of repository pattern
**Impact**: Breaks ABP architecture, makes testing difficult, bypasses UnitOfWork

**Fix**:
```csharp
// ❌ Current (direct DbContext)
public class OrderAppService : ApplicationService
{
    private readonly MyDbContext _dbContext;

    public OrderAppService(MyDbContext dbContext)
    {
        _dbContext = dbContext;
    }

    public async Task<OrderDto> GetOrderAsync(Guid id)
    {
        var order = await _dbContext.Orders
            .FirstOrDefaultAsync(x => x.Id == id);
        return ObjectMapper.Map<Order, OrderDto>(order);
    }
}

// ✅ Recommended (repository pattern)
public class OrderAppService : ApplicationService
{
    private readonly IRepository<Order, Guid> _orderRepository;

    public OrderAppService(IRepository<Order, Guid> orderRepository)
    {
        _orderRepository = orderRepository;
    }

    public async Task<OrderDto> GetOrderAsync(Guid id)
    {
        var order = await _orderRepository.GetAsync(id);
        return ObjectMapper.Map<Order, OrderDto>(order);
    }
}
```

**Benefits of Fix**:
- Follows ABP conventions
- Enables automatic UnitOfWork management
- Simplifies testing with mock repositories
- Maintains architectural consistency

**References**: https://docs.abp.io/en/abp/latest/Repositories
```

---

## Merge Commit Reviews

### Example 5: Reviewing Merge Commits

**User Request:**
```
Review the merge commit for integration issues
```

**What Happens:**

1. Skill detects merge commit:
```bash
git log -1 --merges
# commit def5678
# Merge: abc1234 xyz9876
# Merge branch 'feature/payment' into main

git diff HEAD^1 HEAD --stat
# Shows all changes from the merged branch
```

2. Reviews integration points
3. Checks for conflict resolution issues

**Sample Finding:**

```markdown
### [HIGH] Merge Conflict Resolution Error
**File**: `src/api/checkout.ts:67`
**Category**: Integration
**Problem**: Merge conflict resolved incorrectly - both versions kept causing duplicate code
**Impact**: Duplicate payment processing would charge customers twice

**Fix**:
```typescript
// ❌ Current (after merge - duplicate logic)
async function processPayment(orderId: string) {
  // Version from main branch
  await stripe.charges.create({
    amount: order.total,
    currency: 'usd',
  });

  // Version from feature branch (conflict marker removed but code kept)
  await stripe.charges.create({
    amount: order.total,
    currency: 'usd',
    metadata: { orderId },
  });
}

// ✅ Recommended (single call with metadata)
async function processPayment(orderId: string) {
  await stripe.charges.create({
    amount: order.total,
    currency: 'usd',
    metadata: { orderId },
  });
}
```

**Conflict Resolution Check**:
```bash
# Review original conflict
git show :1:src/api/checkout.ts  # common ancestor
git show :2:src/api/checkout.ts  # HEAD (main)
git show :3:src/api/checkout.ts  # feature branch
```
```

---

## Performance Reviews

### Example 6: Performance-Focused Review

**User Request:**
```
Review my code for performance issues
```

**Sample Finding:**

```markdown
### [HIGH] N+1 Query Problem
**File**: `src/api/posts.ts:34`
**Category**: Performance
**Problem**: Loading comments in a loop causes N+1 queries
**Impact**: 100 posts = 101 database queries; slow response time

**Fix**:
```typescript
// ❌ Current (N+1 queries)
async function getPostsWithComments() {
  const posts = await db.post.findMany();

  for (const post of posts) {
    post.comments = await db.comment.findMany({
      where: { postId: post.id }
    });
  }

  return posts;
}

// ✅ Recommended (single query with join)
async function getPostsWithComments() {
  const posts = await db.post.findMany({
    include: {
      comments: true
    }
  });

  return posts;
}
```

**Performance Impact**:
- Before: 101 queries for 100 posts
- After: 1 query with JOIN
- Expected improvement: 50-100x faster

**References**:
- https://www.prisma.io/docs/guides/performance-and-optimization/query-optimization-performance
```

---

## Incremental Reviews

### Example 7: Review Specific Files Only

**User Request:**
```
Review only the authentication files for security
```

**What Happens:**

1. Skill focuses on auth-related files:
```bash
# Find auth files
find . -name "*auth*" -o -name "*login*" -o -name "*session*"
```

2. Provides targeted review
3. Skips non-auth files

**Sample Output:**

```markdown
# Security Review: Authentication Files

## Scope
Reviewing authentication-related files for security vulnerabilities.

## Files Reviewed
- `src/api/auth.ts`
- `src/middleware/session.ts`
- `src/utils/token.ts`

## Findings

### [CRITICAL] Weak JWT Secret
**File**: `src/utils/token.ts:5`
[... detailed finding ...]

### [HIGH] Session Token Not HTTPOnly
**File**: `src/middleware/session.ts:18`
[... detailed finding ...]
```

---

## Example 8: Review Before Merge

**User Request:**
```
I'm about to merge my feature branch. Can you review it?
```

**Workflow:**

```bash
# Check current branch
git branch --show-current
# feature/user-profile

# Review all commits in feature branch
git log main..HEAD

# Review all changes vs main
git diff main...HEAD
```

**Output:**

```markdown
# Pre-Merge Review: feature/user-profile

## Summary
Reviewing feature branch before merge to main.

## Changes Overview
- **Commits**: 8
- **Files Changed**: 15
- **Lines Added**: +456
- **Lines Removed**: -123

## Issues Found
Critical: 0, High: 2, Medium: 5, Low: 3

## Merge Recommendation
⚠️ **Address 2 high-priority issues before merging**

## High Priority Issues

[... detailed issues ...]

## Approval Checklist

- [ ] All critical issues resolved (✅ None found)
- [ ] High priority issues addressed (⚠️ 2 remaining)
- [ ] Tests passing (not verified in this review)
- [ ] No merge conflicts (verified)

## Next Steps
1. Fix the 2 high-priority issues
2. Run full test suite
3. Request human code review
4. Merge when approved
```

---

## Tips for Effective Reviews

### Getting the Best Results

1. **Be Specific**: "Review authentication for security" vs "Review my code"
2. **Provide Context**: Mention framework/language if not obvious
3. **Set Priorities**: "Focus on critical security issues only"
4. **Iterative**: Review, fix, review again

### Common Workflows

**Daily Development:**
```
# After implementing a feature
git add .
git commit -m "Add feature"
"Review my latest commit"
```

**Before Merging:**
```
# On feature branch
git add .
git commit -m "Final changes"
"Review all changes in this branch vs main"
```

**Security Audit:**
```
# Periodic security check
"Review entire codebase for security vulnerabilities"
```

**Performance Optimization:**
```
# When performance matters
"Review my database queries for performance issues"
```

---

## Version

- **Version**: 1.0.0
- **Last Updated**: 2025-01-13

For more information, see:
- [README.md](README.md) - User documentation
- [SKILL.md](SKILL.md) - Technical implementation
- [PATTERNS.md](PATTERNS.md) - Detection patterns
