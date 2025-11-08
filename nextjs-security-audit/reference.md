# Security Vulnerability Reference Guide

## Common Vulnerability Examples

### 1. SQL Injection

#### ❌ Vulnerable Pattern
```typescript
// app/api/users/route.ts
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const userId = searchParams.get('id');

  // CRITICAL: SQL injection via string interpolation
  const user = await db.query(`SELECT * FROM users WHERE id = ${userId}`);
  return Response.json(user);
}
```

#### ✅ Secure Pattern
```typescript
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const userId = searchParams.get('id');

  // Validate input
  if (!userId || !/^\d+$/.test(userId)) {
    return Response.json({ error: 'Invalid ID' }, { status: 400 });
  }

  // Use parameterized query
  const user = await db.query('SELECT * FROM users WHERE id = $1', [userId]);
  return Response.json(user);
}
```

### 2. XSS in Server Components

#### ❌ Vulnerable Pattern
```typescript
// app/profile/page.tsx
export default async function ProfilePage({ searchParams }) {
  const message = searchParams.message; // User-controlled

  return (
    <div>
      {/* CRITICAL: Unescaped user input */}
      <div dangerouslySetInnerHTML={{ __html: message }} />
    </div>
  );
}
```

#### ✅ Secure Pattern
```typescript
import DOMPurify from 'isomorphic-dompurify';

export default async function ProfilePage({ searchParams }) {
  const message = searchParams.message;

  // Sanitize if HTML is necessary
  const cleanMessage = DOMPurify.sanitize(message, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong'],
    ALLOWED_ATTR: []
  });

  return (
    <div>
      <div dangerouslySetInnerHTML={{ __html: cleanMessage }} />
      {/* Or better: just use text */}
      <p>{message}</p> {/* Auto-escaped by React */}
    </div>
  );
}
```

### 3. Missing Auth in Server Actions

#### ❌ Vulnerable Pattern
```typescript
// app/actions.ts
'use server'

export async function deleteUser(userId: string) {
  // CRITICAL: No authentication check!
  await db.user.delete({ where: { id: userId } });
  return { success: true };
}
```

#### ✅ Secure Pattern
```typescript
'use server'

import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';

export async function deleteUser(userId: string) {
  // Validate authentication
  const session = await getServerSession(authOptions);
  if (!session?.user) {
    throw new Error('Unauthorized');
  }

  // Validate authorization
  if (session.user.id !== userId && session.user.role !== 'admin') {
    throw new Error('Forbidden');
  }

  // Validate input
  if (!userId || typeof userId !== 'string') {
    throw new Error('Invalid user ID');
  }

  await db.user.delete({ where: { id: userId } });
  return { success: true };
}
```

### 4. Exposed Secrets in Client Components

#### ❌ Vulnerable Pattern
```typescript
// app/components/Analytics.tsx
'use client'

export function Analytics() {
  const API_KEY = 'sk_live_abc123xyz'; // CRITICAL: Exposed to browser!

  useEffect(() => {
    fetch('https://api.example.com/track', {
      headers: { 'Authorization': `Bearer ${API_KEY}` }
    });
  }, []);

  return null;
}
```

#### ✅ Secure Pattern
```typescript
// app/components/Analytics.tsx
'use client'

export function Analytics() {
  useEffect(() => {
    // Call Server Action or Route Handler instead
    trackEvent({ page: window.location.pathname });
  }, []);

  return null;
}

// app/actions.ts (Server Action)
'use server'

export async function trackEvent(data: { page: string }) {
  const API_KEY = process.env.ANALYTICS_API_KEY; // Secure on server

  await fetch('https://api.example.com/track', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${API_KEY}` },
    body: JSON.stringify(data)
  });
}
```

### 5. Command Injection

#### ❌ Vulnerable Pattern
```typescript
// app/api/convert/route.ts
import { exec } from 'child_process';

export async function POST(request: Request) {
  const { filename } = await request.json();

  // CRITICAL: Command injection vulnerability
  exec(`convert ${filename} output.pdf`, (error, stdout) => {
    // ...
  });
}
```

#### ✅ Secure Pattern
```typescript
import { execFile } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execFileAsync = promisify(execFile);

export async function POST(request: Request) {
  const { filename } = await request.json();

  // Validate input
  if (!filename || typeof filename !== 'string') {
    return Response.json({ error: 'Invalid filename' }, { status: 400 });
  }

  // Sanitize filename (no path traversal)
  const sanitized = path.basename(filename);

  // Use execFile with array args (no shell interpretation)
  try {
    const { stdout } = await execFileAsync('convert', [sanitized, 'output.pdf']);
    return Response.json({ success: true });
  } catch (error) {
    return Response.json({ error: 'Conversion failed' }, { status: 500 });
  }
}
```

### 6. Insecure Deserialization

#### ❌ Vulnerable Pattern
```typescript
// app/api/webhook/route.ts
export async function POST(request: Request) {
  const body = await request.text();

  // CRITICAL: No validation before parsing
  const data = JSON.parse(body);

  // Using parsed data without type checking
  await processOrder(data);
}
```

#### ✅ Secure Pattern
```typescript
import { z } from 'zod';

// Define schema
const OrderSchema = z.object({
  orderId: z.string().uuid(),
  amount: z.number().positive().max(1000000),
  items: z.array(z.object({
    id: z.string(),
    quantity: z.number().int().positive()
  }))
});

export async function POST(request: Request) {
  try {
    const body = await request.json();

    // Validate with schema
    const data = OrderSchema.parse(body);

    // Type-safe and validated
    await processOrder(data);

    return Response.json({ success: true });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return Response.json({ error: error.errors }, { status: 400 });
    }
    throw error;
  }
}
```

### 7. Path Traversal

#### ❌ Vulnerable Pattern
```typescript
// app/api/files/route.ts
import fs from 'fs/promises';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const filename = searchParams.get('file');

  // CRITICAL: Path traversal vulnerability
  const content = await fs.readFile(`./uploads/${filename}`, 'utf-8');
  return Response.json({ content });
}
```

#### ✅ Secure Pattern
```typescript
import fs from 'fs/promises';
import path from 'path';

const UPLOAD_DIR = path.resolve('./uploads');

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const filename = searchParams.get('file');

  if (!filename || typeof filename !== 'string') {
    return Response.json({ error: 'Invalid filename' }, { status: 400 });
  }

  // Sanitize and resolve path
  const safePath = path.resolve(UPLOAD_DIR, path.basename(filename));

  // Ensure path is within UPLOAD_DIR (prevent traversal)
  if (!safePath.startsWith(UPLOAD_DIR)) {
    return Response.json({ error: 'Access denied' }, { status: 403 });
  }

  try {
    const content = await fs.readFile(safePath, 'utf-8');
    return Response.json({ content });
  } catch (error) {
    return Response.json({ error: 'File not found' }, { status: 404 });
  }
}
```

## Next.js Specific Anti-patterns

### 1. Wrong Data Fetching (App Router)

#### ❌ Anti-pattern
```typescript
// app/posts/page.tsx
// Using Pages Router pattern in App Router!
export async function getServerSideProps() {
  const posts = await fetchPosts();
  return { props: { posts } };
}

export default function Posts({ posts }) {
  return <PostList posts={posts} />;
}
```

#### ✅ Correct Pattern
```typescript
// app/posts/page.tsx
async function getPosts() {
  const res = await fetch('https://api.example.com/posts', {
    next: { revalidate: 3600 } // Revalidate every hour
  });

  if (!res.ok) throw new Error('Failed to fetch');
  return res.json();
}

export default async function Posts() {
  const posts = await getPosts();
  return <PostList posts={posts} />;
}
```

### 2. Client Component Overuse

#### ❌ Anti-pattern
```typescript
// app/dashboard/page.tsx
'use client' // Unnecessary!

export default function Dashboard() {
  // No client-side hooks or event handlers
  // Could be Server Component
  return (
    <div>
      <h1>Dashboard</h1>
      <Stats />
      <RecentActivity />
    </div>
  );
}
```

#### ✅ Correct Pattern
```typescript
// app/dashboard/page.tsx (Server Component)
export default async function Dashboard() {
  const stats = await getStats();
  const activity = await getActivity();

  return (
    <div>
      <h1>Dashboard</h1>
      <Stats data={stats} />
      <RecentActivity data={activity} />
    </div>
  );
}

// components/InteractiveChart.tsx (only this needs client)
'use client'

export function InteractiveChart({ data }) {
  const [selectedRange, setSelectedRange] = useState('week');
  // Client-side interactivity here
}
```

### 3. Missing Input Validation in Server Actions

#### ❌ Anti-pattern
```typescript
// app/actions.ts
'use server'

export async function updateProfile(formData: FormData) {
  const name = formData.get('name');
  const email = formData.get('email');

  // No validation!
  await db.user.update({
    where: { id: userId },
    data: { name, email }
  });
}
```

#### ✅ Correct Pattern
```typescript
'use server'

import { z } from 'zod';
import { getServerSession } from 'next-auth';

const ProfileSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
});

export async function updateProfile(formData: FormData) {
  const session = await getServerSession();
  if (!session?.user?.id) {
    throw new Error('Unauthorized');
  }

  const rawData = {
    name: formData.get('name'),
    email: formData.get('email'),
  };

  // Validate
  const data = ProfileSchema.parse(rawData);

  await db.user.update({
    where: { id: session.user.id },
    data
  });

  revalidatePath('/profile');
  return { success: true };
}
```

## OWASP Top 10 Mapping

1. **Broken Access Control** → Check auth in Server Actions, API routes
2. **Cryptographic Failures** → Look for hardcoded secrets, weak hashing
3. **Injection** → SQL, command, XSS patterns
4. **Insecure Design** → Missing rate limiting, no CSRF protection
5. **Security Misconfiguration** → Exposed error details, debug mode in prod
6. **Vulnerable Components** → Check package.json for known CVEs
7. **Authentication Failures** → Weak session management, missing MFA
8. **Data Integrity Failures** → Insecure deserialization, missing signatures
9. **Logging Failures** → Missing audit logs for sensitive operations
10. **SSRF** → User-controlled URLs in fetch calls

## Tools Integration

Consider suggesting these tools if not already in use:

- **zod** - Runtime type validation
- **DOMPurify** - HTML sanitization
- **helmet** - Security headers
- **rate-limiter-flexible** - Rate limiting
- **@next/eslint-plugin** - Next.js specific linting
- **typescript-eslint** - Type safety enforcement
