# Usage Examples

## Example 1: Full Security Audit

### User Request
```
"Audit my Next.js e-commerce app for security vulnerabilities"
```

### Skill Execution Flow

1. **Codebase Exploration**
```
Using Task tool (Explore agent, very thorough) to map:
- Next.js version: 14.2.0 (App Router)
- Key directories: app/, lib/, components/
- Auth system: NextAuth.js
- Database: Prisma + PostgreSQL
- Payment: Stripe integration
```

2. **Security Scan Results**

```markdown
# Security Audit Report

## Critical Issues (2)

### [CRITICAL] SQL Injection in Product Search

**Location:** `app/api/products/search/route.ts:12`

**Problem:**
User input from search query is directly interpolated into SQL:
```typescript
const query = searchParams.get('q');
const products = await db.$queryRaw`SELECT * FROM products WHERE name LIKE '%${query}%'`;
```

**Risk:**
Attacker can execute arbitrary SQL:
```
/api/products/search?q='; DROP TABLE products; --
```

**Fix:**
```typescript
// ✅ Use parameterized query
const query = searchParams.get('q');

if (!query || typeof query !== 'string') {
  return Response.json({ error: 'Invalid query' }, { status: 400 });
}

const products = await db.$queryRaw`
  SELECT * FROM products
  WHERE name LIKE ${`%${query}%`}
`;
```

**References:**
- https://owasp.org/www-community/attacks/SQL_Injection
- https://www.prisma.io/docs/concepts/components/prisma-client/raw-database-access

---

### [CRITICAL] Stripe Secret Key Exposed in Client Component

**Location:** `app/components/Checkout.tsx:8`

**Problem:**
```typescript
'use client'

const STRIPE_SECRET = 'sk_live_51abc...'; // Exposed to browser!
```

**Risk:**
Secret key visible in browser bundle = full account compromise. Attacker can:
- Create refunds
- Access customer data
- Issue payments

**Fix:**
```typescript
// ✅ Move to Server Action
// app/actions/checkout.ts
'use server'

import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function createPaymentIntent(amount: number) {
  const session = await getServerSession();
  if (!session) throw new Error('Unauthorized');

  return await stripe.paymentIntents.create({
    amount,
    currency: 'usd',
  });
}

// app/components/Checkout.tsx
'use client'

import { createPaymentIntent } from '@/actions/checkout';

export function Checkout() {
  const handlePay = async () => {
    const intent = await createPaymentIntent(1000);
    // Use intent.client_secret with Stripe.js
  };
}
```

---

## High Severity Issues (3)

### [HIGH] Missing Authentication in Delete Action

**Location:** `app/actions/products.ts:45`

**Problem:**
```typescript
'use server'

export async function deleteProduct(id: string) {
  await db.product.delete({ where: { id } });
  // No auth check - anyone can delete products!
}
```

**Fix:**
```typescript
'use server'

export async function deleteProduct(id: string) {
  const session = await getServerSession();

  if (!session?.user || session.user.role !== 'admin') {
    throw new Error('Unauthorized');
  }

  if (!id || typeof id !== 'string') {
    throw new Error('Invalid product ID');
  }

  await db.product.delete({ where: { id } });
  revalidatePath('/admin/products');
}
```

---

### [HIGH] XSS in Product Reviews

**Location:** `app/products/[id]/page.tsx:67`

**Problem:**
```typescript
<div dangerouslySetInnerHTML={{ __html: review.content }} />
```

User-submitted reviews rendered as raw HTML without sanitization.

**Fix:**
```typescript
import DOMPurify from 'isomorphic-dompurify';

// Sanitize on write to database
const cleanContent = DOMPurify.sanitize(reviewContent, {
  ALLOWED_TAGS: ['p', 'br', 'b', 'i', 'em', 'strong'],
  ALLOWED_ATTR: []
});

await db.review.create({
  data: { content: cleanContent, ... }
});

// Or better: just use plain text
<p className="whitespace-pre-wrap">{review.content}</p>
```

---

### [HIGH] Missing Input Validation in Server Action

**Location:** `app/actions/newsletter.ts:12`

**Problem:**
```typescript
'use server'

export async function subscribe(email: string) {
  await db.subscriber.create({ data: { email } });
  // No validation - can insert arbitrary data
}
```

**Fix:**
```typescript
'use server'

import { z } from 'zod';

const EmailSchema = z.string().email().max(255);

export async function subscribe(email: string) {
  try {
    const validEmail = EmailSchema.parse(email);

    await db.subscriber.create({
      data: { email: validEmail }
    });

    return { success: true };
  } catch (error) {
    if (error instanceof z.ZodError) {
      throw new Error('Invalid email address');
    }
    throw error;
  }
}
```

---

## Medium Severity Issues (5)

### [MEDIUM] Missing Error Boundaries

**Location:** `app/dashboard/*`

**Problem:**
No `error.tsx` files in critical routes. Unhandled errors will crash entire app.

**Fix:**
```typescript
// app/dashboard/error.tsx
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

---

### [MEDIUM] Excessive 'use client' Directives

**Location:** Multiple files

**Problem:**
23 components marked 'use client' but only 8 actually use client hooks.

**Impact:**
- Larger bundle size
- Lost Server Component benefits (streaming, data fetching)

**Fix:**
Remove 'use client' from:
- `components/ProductCard.tsx` (purely presentational)
- `components/Footer.tsx` (static)
- `app/about/page.tsx` (no interactivity)

---

## Summary

- **Critical:** 2 issues (fix immediately)
- **High:** 3 issues (fix within 24h)
- **Medium:** 5 issues (fix within week)
- **Low:** 7 issues (backlog)

**Priority Actions:**
1. Remove hardcoded Stripe secret → move to Server Action
2. Fix SQL injection in product search
3. Add auth checks to all Server Actions
4. Implement input validation with Zod
```

---

## Example 2: Quick Security Check

### User Request
```
"Quick security scan - just check for hardcoded secrets"
```

### Focused Execution

```markdown
# Hardcoded Secrets Scan

Scanning for API keys, tokens, and credentials...

## Findings

### ❌ `lib/analytics.ts:5`
```typescript
const GA_ID = 'UA-123456789-1'; // ✅ OK - Public tracking ID
```
**Status:** False positive - Google Analytics IDs are meant to be public.

---

### ❌ `app/api/webhook/route.ts:8`
```typescript
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET || 'fallback_secret_123';
```
**Issue:** Hardcoded fallback defeats env var security.

**Fix:**
```typescript
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET;
if (!WEBHOOK_SECRET) {
  throw new Error('WEBHOOK_SECRET must be set');
}
```

---

### ❌ `.env.local` (committed to git!)
```
DATABASE_URL="postgresql://user:password123@localhost:5432/db"
STRIPE_SECRET_KEY="sk_live_..."
```
**CRITICAL:** Secrets committed to repository!

**Fix:**
1. Add `.env.local` to `.gitignore`
2. Remove from git history:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env.local" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. Rotate all exposed credentials
4. Use `.env.example` for template

---

## Summary
- 1 critical exposure (committed .env.local)
- 1 medium issue (hardcoded fallback)
- 1 false positive (public GA ID)

**Immediate action:** Rotate all secrets in `.env.local` and remove from git history.
```

---

## Example 3: Next.js Best Practices Review

### User Request
```
"Check if we're following Next.js 14 App Router best practices"
```

### Focused Analysis

```markdown
# Next.js App Router Best Practices Review

## ✅ Good Patterns Found

1. **Server Components by default** - 85% of components are Server Components
2. **Proper metadata usage** - Using `generateMetadata` in all route pages
3. **Parallel routes** - Using `@modal` slot for intercepting routes
4. **Route groups** - Good organization with `(marketing)` and `(dashboard)`

---

## ❌ Issues Found

### [HIGH] Using Pages Router APIs in App Router

**Location:** `app/blog/page.tsx:23`

```typescript
// ❌ Wrong - getServerSideProps doesn't work in App Router
export async function getServerSideProps() {
  const posts = await getPosts();
  return { props: { posts } };
}
```

**Fix:**
```typescript
// ✅ Server Component with async fetch
async function getPosts() {
  const res = await fetch('...', {
    next: { revalidate: 60 }
  });
  return res.json();
}

export default async function BlogPage() {
  const posts = await getPosts();
  return <PostList posts={posts} />;
}
```

---

### [MEDIUM] Client Component Fetching Data

**Location:** `app/dashboard/page.tsx:12`

```typescript
'use client'

export default function Dashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch('/api/stats').then(r => r.json()).then(setStats);
  }, []);

  // ...
}
```

**Issue:** Missing Server Component benefits - slower, no streaming, waterfall requests.

**Fix:**
```typescript
// ✅ Server Component
async function getStats() {
  const res = await fetch('https://api.example.com/stats', {
    next: { revalidate: 300 }
  });
  return res.json();
}

export default async function Dashboard() {
  const stats = await getStats();
  return <StatsDisplay data={stats} />;
}

// Only make chart interactive
'use client'
function StatsDisplay({ data }) {
  const [view, setView] = useState('graph');
  // Client-side interactivity here
}
```

---

### [MEDIUM] Missing Dynamic Route Validation

**Location:** `app/products/[id]/page.tsx`

```typescript
export default async function ProductPage({ params }) {
  const product = await db.product.findUnique({
    where: { id: params.id } // No validation!
  });

  return <ProductDetail product={product} />;
}
```

**Issue:** If invalid ID, crashes instead of 404.

**Fix:**
```typescript
import { notFound } from 'next/navigation';
import { z } from 'zod';

const ParamsSchema = z.object({
  id: z.string().uuid()
});

export default async function ProductPage({ params }) {
  const result = ParamsSchema.safeParse(params);

  if (!result.success) {
    notFound();
  }

  const product = await db.product.findUnique({
    where: { id: result.data.id }
  });

  if (!product) {
    notFound();
  }

  return <ProductDetail product={product} />;
}
```

---

## Recommendations

1. **Remove all `getServerSideProps`** - Migrate to Server Components
2. **Reduce client components** - Convert 15 components from client to server
3. **Add route validation** - Validate all dynamic params
4. **Add error boundaries** - Create `error.tsx` for main routes
5. **Implement loading states** - Add `loading.tsx` for better UX

**Migration Priority:**
- Week 1: Remove Pages Router APIs (breaking)
- Week 2: Convert client components (performance win)
- Week 3: Add validation + error handling (stability)
```

---

## Example 4: Type Safety Audit

### User Request
```
"Check TypeScript type safety - find all 'any' types and unsafe assertions"
```

### Focused Type Safety Scan

```markdown
# TypeScript Safety Audit

## 'any' Type Usage (18 instances)

### High Priority

**`lib/api.ts:45`**
```typescript
export async function fetchData(endpoint: string): Promise<any> {
  //                                                         ^^^
  const res = await fetch(endpoint);
  return res.json();
}
```

**Fix:**
```typescript
// Define proper return types
export async function fetchData<T>(endpoint: string): Promise<T> {
  const res = await fetch(endpoint);
  if (!res.ok) throw new Error('Fetch failed');
  return res.json();
}

// Usage with validation
const schema = z.object({ id: z.string(), name: z.string() });
const data = await fetchData<z.infer<typeof schema>>('/api/users');
const validated = schema.parse(data);
```

---

### Non-null Assertions Without Checks (12 instances)

**`app/profile/page.tsx:34`**
```typescript
const user = users.find(u => u.id === userId);
const email = user!.email; // ⚠️ Could be undefined
//                ^
```

**Fix:**
```typescript
const user = users.find(u => u.id === userId);
if (!user) {
  notFound();
}
const email = user.email; // ✅ Type-safe
```

---

### @ts-ignore Usage (5 instances)

**`components/Chart.tsx:23`**
```typescript
// @ts-ignore - Chart library types are wrong
chart.updateData(newData);
```

**Better approach:**
```typescript
// Properly type the library
import type { Chart as ChartType } from 'chart.js';

const chart = chartRef.current as ChartType;
if (chart && 'updateData' in chart) {
  chart.updateData(newData);
}

// Or create proper type definition
declare module 'chart.js' {
  interface Chart {
    updateData(data: unknown): void;
  }
}
```

---

## Summary
- 18 'any' types → Define proper types
- 12 unsafe non-null assertions → Add null checks
- 5 @ts-ignore → Fix root cause or use @ts-expect-error with explanation
```

---

## Integration with CI/CD

You can automate this skill in CI:

```yaml
# .github/workflows/security-audit.yml
name: Security Audit

on: [pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Security Audit
        run: |
          npx claude-code skill nextjs-security-audit

      - name: Comment PR
        uses: actions/github-script@v6
        with:
          script: |
            // Post audit results to PR
```
