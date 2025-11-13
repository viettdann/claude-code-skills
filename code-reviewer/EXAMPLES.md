# Code Reviewer Skill - Usage Examples

This document provides real-world examples of using the Code Reviewer skill for various scenarios.

## Table of Contents

1. [Automatic Report Generation](#automatic-report-generation)
2. [Basic Usage](#basic-usage)
3. [Security-Focused Reviews](#security-focused-reviews)
4. [Framework-Specific Reviews](#framework-specific-reviews)
5. [Merge Commit Reviews](#merge-commit-reviews)
6. [Performance Reviews](#performance-reviews)
7. [Incremental Reviews](#incremental-reviews)

---

## Automatic Report Generation

**NEW**: The Code Reviewer skill now automatically generates comprehensive markdown reports for every review!

### Example: Report Generation Output

**User Request:**
```
Review my latest commit
```

**Terminal Output (User sees this):**

```
🔍 Analyzing code changes...

Checking commit: abc1234 - Add user authentication endpoint
Files changed: 2 files (+57 lines)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Analyzing security vulnerabilities...
  ✓ Checked SQL injection patterns
  ✗ Found 1 critical issue

Analyzing code quality...
  ✓ Checked error handling
  ✓ Checked async patterns
  ✗ Found 1 high priority issue

Analyzing best practices...
  ✗ Found 1 medium priority issue
  ✓ Identified 3 strengths

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Code review complete!
📄 Report saved to: CODE-REVIEW-REPORT-abc1234-2025-01-13.md

📊 Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Files Reviewed: 2 files
Lines Changed: +57 -0
Issues Found: 3 total

🚨 Critical: 1 (Must fix immediately)
🔴 High: 1 (Fix before production)
⚠️ Medium: 1 (Technical debt)
ℹ️ Low: 0
✅ Strengths: 3 best practices identified

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Grade: B+
Verdict: Needs Changes - Fix critical issue before merge
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ Top Priority Items:
1. SQL Injection Vulnerability - src/api/auth.ts:23 (5 min fix)
2. Missing Password Hashing - src/api/auth.ts:34 (10 min fix)

📖 Full details in the report file.

Next steps:
1. Open CODE-REVIEW-REPORT-abc1234-2025-01-13.md to see detailed findings
2. Fix critical SQL injection issue immediately
3. Implement password hashing before deploying
```

**Generated Report File** (`CODE-REVIEW-REPORT-abc1234-2025-01-13.md`):

```markdown
# 🔍 MyApp Code Review Report

**Project:** MyApp
**Framework:** Node.js with Express
**Language:** TypeScript
**Analysis Date:** 2025-01-13
**Analyzed By:** Code Reviewer Skill
**Commit:** abc1234 - Add user authentication endpoint

---

## 📊 Executive Summary

### Overall Assessment: **B+ (Good with Security Concerns)**

This commit adds user authentication functionality to the API. While the implementation demonstrates good TypeScript usage and follows Express best practices, there is **1 critical security vulnerability (SQL injection)** and **1 high priority issue (password storage)** that must be addressed before deploying to production.

**Key Highlights:**
- ✅ Clean TypeScript with proper type definitions
- ✅ Good async/await patterns throughout
- ✅ Proper error handling structure
- 🚨 **Critical SQL injection vulnerability** requiring immediate fix
- 🔴 **Passwords stored in plain text** - must implement hashing

### Quick Stats

| Category | Status |
|----------|--------|
| Security | 🔴 Critical Issues - SQL injection, no password hashing |
| Code Quality | ✅ Excellent - Clean code, good patterns |
| Performance | ✅ Excellent - Proper async, no obvious issues |
| Best Practices | ⚠️ Good - Missing input validation |
| Test Coverage | N/A - No tests in this commit |

---

## Table of Contents

1. [Critical Issues](#critical-issues) (1)
2. [High Priority Issues](#high-priority-issues) (1)
3. [Medium Priority Issues](#medium-priority-issues) (1)
4. [Low Priority Issues](#low-priority-issues) (0)
5. [Strengths & Best Practices](#strengths--best-practices) (3)
6. [Summary & Priority Roadmap](#summary--priority-roadmap)
7. [Recommended Immediate Actions](#recommended-immediate-actions)
8. [References & Resources](#references--resources)

---

## 🚨 CRITICAL ISSUES (1)

### 🚨 CRITICAL #1: SQL Injection Vulnerability

**Location:** `src/api/auth.ts:23`
**Severity:** CRITICAL
**Category:** Security
**Estimated Fix Time:** 5 minutes

#### Problem

User input (`email`) is directly concatenated into SQL query without sanitization or parameterization, allowing attackers to execute arbitrary SQL commands.

#### Impact

- 🔴 **Complete database compromise** - Attackers can read, modify, or delete all data
- 🔴 **Authentication bypass** - Attackers can login as any user
- 🔴 **Data breach** - User credentials and sensitive data exposed

[... rest of the detailed issue ...]

---

[... complete report with all sections ...]
```

### What Gets Generated

The skill creates a comprehensive report including:

1. **Executive Summary** - Grade, key findings, quick stats table
2. **All Issues** - Detailed analysis with code examples and fixes
3. **Strengths** - What the code does well
4. **Priority Roadmap** - Time estimates, fix order
5. **Immediate Actions** - Step-by-step fix guide
6. **References** - Links to documentation
7. **Conclusion** - Production readiness assessment

### Report Benefits

**For Developers:**
- Detailed reference to work through fixes systematically
- Learn from strengths identified in their code
- Time estimates help with planning
- Code examples show exactly what to change

**For Teams:**
- Shareable documentation for PR discussions
- Audit trail of code quality over time
- Training material for junior developers
- Evidence of due diligence for compliance

**For Managers:**
- Clear production readiness assessment
- Prioritized fix lists with time estimates
- Quality metrics across the codebase
- Track improvement over time

### Customizing Reports

The skill automatically adjusts report content based on:
- **Review type**: Commit review vs full codebase audit
- **Severity of findings**: More detail for critical issues
- **Framework detected**: Framework-specific references and patterns
- **Scope**: Focused reports for specific files vs comprehensive reviews

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
