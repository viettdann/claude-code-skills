# Next.js Kits - Usage Examples

Real-world scenarios demonstrating how to use the nextjs-kits skill for performance optimization, security auditing, debugging, and code optimization.

## Table of Contents

1. [Performance Optimization](#performance-optimization)
2. [Security Auditing](#security-auditing)
3. [Debugging Issues](#debugging-issues)
4. [Code Optimization](#code-optimization)
5. [Comprehensive Analysis](#comprehensive-analysis)

---

## Performance Optimization

### Example 1: Optimizing Slow Page Loads

**Scenario**: E-commerce product page loading slowly (4+ seconds).

**User Query:**
```
My Next.js product page is loading very slowly. Can you analyze performance issues?
```

**Skill Workflow:**

1. **Exploration**: Task tool maps codebase structure
2. **Analysis**: Grep finds performance anti-patterns
3. **Validation**: Read examines context
4. **Reporting**: Generates prioritized findings

**Findings Example:**

```markdown
### High: Bundle Size Issue

**Location**: `app/products/[id]/page.tsx:3`

**Problem**: Importing entire lodash library adds 70KB to bundle

**Impact**: Increases initial bundle size and page load time

**Fix**:
\`\`\`typescript
// ❌ Before
import _ from 'lodash'

const sortedProducts = _.sortBy(products, 'price')

// ✅ After
import sortBy from 'lodash/sortBy'

const sortedProducts = sortBy(products, 'price')
\`\`\`

**References**:
- [Next.js Optimizing: Bundle Size](https://nextjs.org/docs/app/building-your-application/optimizing/bundle-size)

---

### High: Missing Dynamic Import

**Location**: `app/products/[id]/page.tsx:5`

**Problem**: Heavy chart component imported statically

**Impact**: 200KB chart library loaded even when chart not visible

**Fix**:
\`\`\`typescript
// ❌ Before
import ProductChart from '@/components/ProductChart'

export default function ProductPage() {
  return (
    <div>
      <ProductInfo />
      <ProductChart data={data} />
    </div>
  )
}

// ✅ After
import dynamic from 'next/dynamic'

const ProductChart = dynamic(() => import('@/components/ProductChart'), {
  loading: () => <ChartSkeleton />,
  ssr: false
})

export default function ProductPage() {
  return (
    <div>
      <ProductInfo />
      <Suspense fallback={<ChartSkeleton />}>
        <ProductChart data={data} />
      </Suspense>
    </div>
  )
}
\`\`\`

---

### Medium: Unoptimized Images

**Location**: `app/products/[id]/components/Gallery.tsx:15`

**Problem**: Using native img tags instead of next/image

**Impact**: Missing automatic image optimization, no lazy loading, poor Core Web Vitals

**Fix**:
\`\`\`typescript
// ❌ Before
<img src={product.image} alt={product.name} />

// ✅ After
import Image from 'next/image'

<Image
  src={product.image}
  alt={product.name}
  width={800}
  height={600}
  priority={false}
  placeholder="blur"
  blurDataURL={product.blurDataURL}
/>
\`\`\`
```

**Result**: Page load time reduced from 4.2s to 1.8s

---

### Example 2: Improving Core Web Vitals

**User Query:**
```
My Core Web Vitals scores are poor. Can you help optimize for LCP, FID, and CLS?
```

**Findings:**

1. **LCP Optimization**: Added `priority` to hero image
2. **FID Optimization**: Implemented code splitting for heavy components
3. **CLS Optimization**: Added explicit dimensions to all images and reserved space for dynamic content

**Before:**
- LCP: 4.2s
- FID: 180ms
- CLS: 0.25

**After:**
- LCP: 1.8s
- FID: 45ms
- CLS: 0.05

---

## Security Auditing

### Example 3: Securing Server Actions

**Scenario**: E-commerce app with user-submitted reviews.

**User Query:**
```
Audit my Server Actions for security vulnerabilities
```

**Findings Example:**

```markdown
### Critical: Missing Input Validation

**Location**: `app/actions/reviews.ts:5`

**Problem**: Server Action accepts user input without validation

**Impact**: Vulnerable to XSS, SQL injection, and data corruption

**Fix**:
\`\`\`typescript
// ❌ Before
"use server"

export async function createReview(formData: FormData) {
  const rating = formData.get('rating')
  const comment = formData.get('comment')

  await db.review.create({
    data: { rating, comment }
  })
}

// ✅ After
"use server"

import { z } from 'zod'

const reviewSchema = z.object({
  rating: z.number().min(1).max(5),
  comment: z.string().min(10).max(500).trim(),
  productId: z.string().uuid()
})

export async function createReview(formData: FormData) {
  const parsed = reviewSchema.safeParse({
    rating: Number(formData.get('rating')),
    comment: formData.get('comment'),
    productId: formData.get('productId')
  })

  if (!parsed.success) {
    return { error: 'Invalid input', details: parsed.error }
  }

  await db.review.create({
    data: parsed.data
  })

  return { success: true }
}
\`\`\`

---

### Critical: Missing Authorization

**Location**: `app/actions/reviews.ts:15`

**Problem**: Server Action allows deleting any review without ownership check

**Impact**: Users can delete other users' reviews

**Fix**:
\`\`\`typescript
// ❌ Before
"use server"

export async function deleteReview(reviewId: string) {
  await db.review.delete({ where: { id: reviewId } })
}

// ✅ After
"use server"

import { auth } from '@/lib/auth'

export async function deleteReview(reviewId: string) {
  const session = await auth()

  if (!session?.user) {
    throw new Error('Unauthorized')
  }

  // Check ownership
  const review = await db.review.findUnique({ where: { id: reviewId } })

  if (!review) {
    throw new Error('Review not found')
  }

  if (review.userId !== session.user.id && !session.user.isAdmin) {
    throw new Error('Forbidden: You can only delete your own reviews')
  }

  await db.review.delete({ where: { id: reviewId } })

  return { success: true }
}
\`\`\`
```

---

### Example 4: Fixing XSS Vulnerabilities

**User Query:**
```
Scan for XSS vulnerabilities in my Next.js app
```

**Finding:**

```markdown
### Critical: XSS via dangerouslySetInnerHTML

**Location**: `app/blog/[slug]/page.tsx:42`

**Problem**: Rendering user-generated HTML without sanitization

**Impact**: Attackers can inject malicious scripts

**Fix**:
\`\`\`typescript
// ❌ Before
export default function BlogPost({ post }) {
  return (
    <div dangerouslySetInnerHTML={{ __html: post.content }} />
  )
}

// ✅ After (Option 1: Sanitize)
import DOMPurify from 'isomorphic-dompurify'

export default function BlogPost({ post }) {
  const sanitizedContent = DOMPurify.sanitize(post.content)

  return (
    <div dangerouslySetInnerHTML={{ __html: sanitizedContent }} />
  )
}

// ✅ After (Option 2: Use Markdown)
import ReactMarkdown from 'react-markdown'

export default function BlogPost({ post }) {
  return <ReactMarkdown>{post.content}</ReactMarkdown>
}
\`\`\`

**References**:
- [OWASP XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
```

---

## Debugging Issues

### Example 5: Fixing Hydration Errors

**Scenario**: Dashboard showing hydration mismatch errors.

**User Query:**
```
I'm getting hydration errors in my Next.js dashboard. Can you help debug?
```

**Console Error:**
```
Error: Hydration failed because the initial UI does not match what was rendered on the server.
```

**Finding:**

```markdown
### High: Hydration Mismatch - Dynamic Date

**Location**: `app/dashboard/page.tsx:28`

**Problem**: Using new Date() in render causes server/client mismatch

**Impact**: React hydration errors, poor user experience

**Fix**:
\`\`\`typescript
// ❌ Before
export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <p>Current time: {new Date().toLocaleString()}</p>
    </div>
  )
}

// ✅ After
"use client"

import { useEffect, useState } from 'react'

export default function Dashboard() {
  const [currentTime, setCurrentTime] = useState('')

  useEffect(() => {
    setCurrentTime(new Date().toLocaleString())
  }, [])

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Current time: {currentTime || 'Loading...'}</p>
    </div>
  )
}
\`\`\`

---

### High: Hydration Mismatch - Window Check

**Location**: `app/dashboard/components/Sidebar.tsx:15`

**Problem**: Conditional rendering based on window object

**Fix**:
\`\`\`typescript
// ❌ Before
export default function Sidebar() {
  const isMobile = typeof window !== 'undefined' && window.innerWidth < 768

  return isMobile ? <MobileSidebar /> : <DesktopSidebar />
}

// ✅ After
"use client"

import { useEffect, useState } from 'react'

export default function Sidebar() {
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    setIsMobile(window.innerWidth < 768)

    const handleResize = () => setIsMobile(window.innerWidth < 768)
    window.addEventListener('resize', handleResize)

    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return isMobile ? <MobileSidebar /> : <DesktopSidebar />
}
\`\`\`
```

**Result**: Hydration errors eliminated

---

### Example 6: Debugging TypeScript Errors

**User Query:**
```
Help me fix TypeScript errors in my Next.js app
```

**Finding:**

```markdown
### Medium: Excessive use of 'any' type

**Location**: `app/utils/api.ts:12`

**Problem**: Using 'any' type reduces type safety

**Fix**:
\`\`\`typescript
// ❌ Before
async function fetchData(url: string): Promise<any> {
  const response = await fetch(url)
  return response.json()
}

// ✅ After
interface ApiResponse<T> {
  data: T
  error?: string
}

async function fetchData<T>(url: string): Promise<ApiResponse<T>> {
  const response = await fetch(url)
  return response.json()
}

// Usage with proper typing
interface User {
  id: string
  name: string
  email: string
}

const result = await fetchData<User[]>('/api/users')
// result.data is now properly typed as User[]
\`\`\`
```

---

## Code Optimization

### Example 7: Optimizing React Component Re-renders

**User Query:**
```
My product list is re-rendering too often. Can you optimize it?
```

**Finding:**

```markdown
### Medium: Unnecessary Re-renders

**Location**: `app/products/components/ProductList.tsx:8`

**Problem**: Inline functions and objects causing unnecessary re-renders

**Fix**:
\`\`\`typescript
// ❌ Before
export default function ProductList({ products }) {
  return (
    <div>
      {products.map(product => (
        <ProductCard
          key={product.id}
          product={product}
          onClick={() => handleClick(product.id)}  // New function every render
          style={{ padding: '20px' }}  // New object every render
        />
      ))}
    </div>
  )
}

// ✅ After
import { useCallback, useMemo } from 'react'

export default function ProductList({ products }) {
  const handleClick = useCallback((productId: string) => {
    // Handle click
  }, [])

  const cardStyle = useMemo(() => ({ padding: '20px' }), [])

  return (
    <div>
      {products.map(product => (
        <ProductCard
          key={product.id}
          product={product}
          onClick={() => handleClick(product.id)}
          style={cardStyle}
        />
      ))}
    </div>
  )
}

// Even better: Memoize ProductCard
import { memo } from 'react'

const ProductCard = memo(function ProductCard({ product, onClick, style }) {
  return (
    <div style={style} onClick={onClick}>
      {product.name}
    </div>
  )
})
\`\`\`
```

---

### Example 8: Optimizing Data Fetching

**User Query:**
```
My dashboard loads data slowly. Can you optimize data fetching?
```

**Finding:**

```markdown
### High: Waterfall Data Fetching

**Location**: `app/dashboard/page.tsx:15`

**Problem**: Sequential data fetches creating waterfall

**Fix**:
\`\`\`typescript
// ❌ Before (Sequential - 1.5s total)
export default async function Dashboard() {
  const user = await getUser()  // 500ms
  const stats = await getStats()  // 500ms
  const activities = await getActivities()  // 500ms

  return (
    <div>
      <UserInfo user={user} />
      <Stats stats={stats} />
      <Activities activities={activities} />
    </div>
  )
}

// ✅ After (Parallel - 500ms total)
export default async function Dashboard() {
  const [user, stats, activities] = await Promise.all([
    getUser(),
    getStats(),
    getActivities()
  ])

  return (
    <div>
      <UserInfo user={user} />
      <Stats stats={stats} />
      <Activities activities={activities} />
    </div>
  )
}

// ✅ Even Better (Streaming)
import { Suspense } from 'react'

export default function Dashboard() {
  return (
    <div>
      <Suspense fallback={<UserSkeleton />}>
        <UserInfo />
      </Suspense>
      <Suspense fallback={<StatsSkeleton />}>
        <Stats />
      </Suspense>
      <Suspense fallback={<ActivitiesSkeleton />}>
        <Activities />
      </Suspense>
    </div>
  )
}

// Components fetch their own data
async function UserInfo() {
  const user = await getUser()
  return <div>{user.name}</div>
}

async function Stats() {
  const stats = await getStats()
  return <div>{stats.total}</div>
}

async function Activities() {
  const activities = await getActivities()
  return <div>{activities.length}</div>
}
\`\`\`

**Result**: Page shows content progressively, perceived performance improved by 60%
```

---

## Comprehensive Analysis

### Example 9: Full App Audit

**User Query:**
```
Can you do a comprehensive audit of my Next.js e-commerce app covering performance, security, and best practices?
```

**Execution:**

1. **Initial Reconnaissance** (Task tool):
   - Scans app/ directory structure
   - Identifies Next.js 14 App Router
   - Maps components, API routes, Server Actions
   - Reviews package.json dependencies

2. **Systematic Analysis** (Grep patterns):
   - Performance: 8 issues found
   - Security: 4 critical, 3 high
   - Debug: 2 hydration errors
   - Optimization: 5 opportunities

3. **Validation** (Read tool):
   - Examines context for each finding
   - Filters false positives
   - Confirms framework-specific patterns

4. **Report Generation**:

```markdown
## Executive Summary

- **Files Scanned**: 127 files
- **Issues Found**: 22 total
  - Critical: 4
  - High: 7
  - Medium: 8
  - Low: 3
- **Categories**:
  - Security: 7 issues
  - Performance: 8 issues
  - Debugging: 2 issues
  - Optimization: 5 issues

---

## Priority Actions

### 1. Critical Security Issues (Fix Immediately)

1. **Server Action Missing Validation** - `app/actions/checkout.ts:12`
   - Risk: Payment amount manipulation
   - Fix: Add Zod schema validation

2. **XSS Vulnerability** - `app/products/[id]/reviews.tsx:45`
   - Risk: Script injection in reviews
   - Fix: Sanitize user-generated content

3. **Missing Authorization** - `app/actions/admin.ts:8`
   - Risk: Unauthorized access to admin functions
   - Fix: Add role-based access control

4. **Exposed API Secret** - `app/components/Checkout.tsx:23`
   - Risk: Stripe secret key exposed to client
   - Fix: Move to Server Component

### 2. High Priority Performance (Fix This Week)

1. **Large Bundle Size** - Moment.js (200KB)
   - Impact: +1.5s page load
   - Fix: Replace with date-fns

2. **Missing Image Optimization** - 15 product images
   - Impact: Poor LCP, high bandwidth
   - Fix: Use next/image with proper sizing

3. **Blocking Data Fetch in Layout**
   - Impact: Delays all page renders
   - Fix: Move to page-level or stream

[... detailed findings for each category ...]
```

**Outcome:**
- 4 critical security issues fixed
- Bundle size reduced by 40%
- Page load time improved from 4.2s to 1.6s
- Core Web Vitals all in "Good" range

---

### Example 10: CI/CD Integration

**Scenario**: Automated quality checks in GitHub Actions

**Setup:**

```yaml
# .github/workflows/nextjs-quality.yml
name: Next.js Quality Scan

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  scan:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Run comprehensive scan
        run: |
          chmod +x .claude/skills/nextjs-kits/scripts/*.py
          python3 .claude/skills/nextjs-kits/scripts/scan-all.py .

      - name: Upload scan results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: nextjs-audit-results
          path: |
            nextjs-audit-report.json
            nextjs-audit-report.md

      - name: Comment PR with results
        uses: actions/github-script@v6
        if: github.event_name == 'pull_request'
        with:
          script: |
            const fs = require('fs')
            const report = fs.readFileSync('nextjs-audit-report.md', 'utf8')

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Next.js Quality Scan Results\n\n${report}`
            })
```

**Result**: Automated quality checks on every PR, preventing issues from reaching production.

---

## Tips for Best Results

1. **Be Specific**: "Check my Server Actions for security issues" is better than "audit my app"

2. **Provide Context**: Mention framework version, specific errors, or problem areas

3. **Request Reports**: Ask for "detailed report" or "save to file" if you want written output

4. **Follow Up**: Ask for explanations: "Why is this a security issue?" or "Explain the fix"

5. **Combine with Scripts**: Run standalone scripts first for quick overview, then use AI for deep analysis

6. **Use in CI/CD**: Integrate scripts into automated pipelines for continuous quality checks

---

For more information, see:
- [README.md](README.md) - Installation and usage
- [SKILL.md](SKILL.md) - Implementation details
- [PATTERNS.md](PATTERNS.md) - Detection patterns
- [REFERENCE.md](REFERENCE.md) - Best practices
