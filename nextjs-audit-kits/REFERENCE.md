# Next.js Best Practices & Technical Reference

Comprehensive reference guide for Next.js development covering App Router, Pages Router, performance optimization, security, and debugging.

## Table of Contents

- [Architecture Patterns](#architecture-patterns)
- [Performance Optimization](#performance-optimization)
- [Security Best Practices](#security-best-practices)
- [Debugging Strategies](#debugging-strategies)
- [Data Fetching](#data-fetching)
- [Caching & Revalidation](#caching--revalidation)
- [SEO & Metadata](#seo--metadata)
- [TypeScript Best Practices](#typescript-best-practices)

---

## Architecture Patterns

### App Router vs Pages Router

**App Router (Next.js 13+)**
- Server Components by default
- File-based routing with `app/` directory
- Layouts and nested routing
- Streaming and Suspense support
- Server Actions for mutations

**Pages Router (Next.js 12 and below)**
- Client-side rendering by default
- File-based routing with `pages/` directory
- getServerSideProps, getStaticProps for data fetching
- API routes for backend logic

### Server Components vs Client Components

**Server Components (default in App Router)**
```typescript
// app/components/ServerComponent.tsx
// No "use client" directive = Server Component

export default async function ServerComponent() {
  // Can directly access databases
  const data = await db.query(...)

  // Benefits:
  // - Zero JavaScript sent to client
  // - Direct database/API access
  // - Better performance
  // - Improved security

  return <div>{data}</div>
}
```

**Client Components**
```typescript
// app/components/ClientComponent.tsx
"use client"

import { useState } from 'react'

export default function ClientComponent() {
  // Can use React hooks
  const [count, setCount] = useState(0)

  // Can access browser APIs
  useEffect(() => {
    localStorage.setItem('count', count)
  }, [count])

  // Use when you need:
  // - useState, useEffect, useContext
  // - Browser APIs (window, localStorage)
  // - Event listeners
  // - Interactive components

  return <button onClick={() => setCount(c => c + 1)}>{count}</button>
}
```

**Composition Pattern (Recommended)**
```typescript
// app/page.tsx (Server Component)
import ClientCounter from './ClientCounter'
import ServerData from './ServerData'

export default async function Page() {
  // Fetch data on server
  const data = await getData()

  // Compose: Server Component wrapping Client Components
  return (
    <div>
      <ServerData data={data} />
      <ClientCounter />
    </div>
  )
}
```

### File Structure Best Practices

**App Router Structure**
```
app/
├── (auth)/                    # Route group
│   ├── login/
│   │   └── page.tsx
│   └── register/
│       └── page.tsx
├── (dashboard)/
│   ├── layout.tsx            # Shared layout
│   ├── analytics/
│   │   └── page.tsx
│   └── settings/
│       └── page.tsx
├── api/                      # API routes
│   └── users/
│       └── route.ts
├── layout.tsx                # Root layout
├── page.tsx                  # Home page
├── loading.tsx               # Loading UI
├── error.tsx                 # Error boundary
└── not-found.tsx             # 404 page
```

**Component Organization**
```
app/
├── _components/              # Private components (not routes)
│   ├── ui/                   # Reusable UI components
│   ├── forms/                # Form components
│   └── layouts/              # Layout components
└── _lib/                     # Utility functions
    ├── utils.ts
    └── db.ts
```

---

## Performance Optimization

### Bundle Size Optimization

**1. Tree Shaking and Code Splitting**

```typescript
// ❌ Bad: Import entire library
import _ from 'lodash'
import * as MUI from '@mui/material'

// ✅ Good: Import specific functions
import debounce from 'lodash/debounce'
import { Button, TextField } from '@mui/material'
```

**2. Dynamic Imports for Heavy Components**

```typescript
// ❌ Bad: Static import
import HeavyChart from './HeavyChart'

// ✅ Good: Dynamic import
import dynamic from 'next/dynamic'

const HeavyChart = dynamic(() => import('./HeavyChart'), {
  loading: () => <p>Loading chart...</p>,
  ssr: false // Disable SSR if component uses browser APIs
})
```

**3. Replace Large Libraries**

```typescript
// ❌ Bad: moment.js (heavy)
import moment from 'moment'

// ✅ Good: date-fns (lightweight, tree-shakeable)
import { format, parseISO } from 'date-fns'
```

**4. Analyze Bundle Size**

```bash
# Install analyzer
npm install @next/bundle-analyzer

# next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

module.exports = withBundleAnalyzer({
  // your next config
})

# Run analysis
ANALYZE=true npm run build
```

### Rendering Performance

**1. Avoid Blocking in Layouts**

```typescript
// ❌ Bad: Blocking fetch in layout
export default async function Layout({ children }) {
  const user = await fetchUser() // Blocks all pages
  return <div>{children}</div>
}

// ✅ Good: Fetch in individual pages or use streaming
export default async function Page() {
  const user = await fetchUser() // Only blocks this page
  return <UserProfile user={user} />
}
```

**2. Use Suspense Boundaries**

```typescript
// ✅ Good: Streaming with Suspense
import { Suspense } from 'react'

export default function Page() {
  return (
    <div>
      <Suspense fallback={<Skeleton />}>
        <SlowComponent />
      </Suspense>
      <FastComponent />  {/* Renders immediately */}
    </div>
  )
}
```

**3. Optimize Re-renders**

```typescript
// ❌ Bad: Inline objects and functions
export default function Component() {
  return (
    <Child
      style={{ color: 'red' }}  // New object every render
      onClick={() => console.log('click')}  // New function every render
    />
  )
}

// ✅ Good: Memoize values
import { useMemo, useCallback } from 'react'

export default function Component() {
  const style = useMemo(() => ({ color: 'red' }), [])
  const handleClick = useCallback(() => console.log('click'), [])

  return <Child style={style} onClick={handleClick} />
}
```

**4. Use React.memo for Expensive Components**

```typescript
// ✅ Good: Memoize expensive components
import { memo } from 'react'

const ExpensiveList = memo(function ExpensiveList({ items }) {
  return (
    <ul>
      {items.map(item => (
        <ExpensiveItem key={item.id} item={item} />
      ))}
    </ul>
  )
})
```

### Image Optimization

**1. Use next/image**

```typescript
// ❌ Bad: Native img tag
<img src="/photo.jpg" />

// ✅ Good: next/image with optimization
import Image from 'next/image'

<Image
  src="/photo.jpg"
  alt="Description"
  width={500}
  height={300}
  placeholder="blur"
  blurDataURL="data:image/..." // or import from static
/>
```

**2. Responsive Images**

```typescript
// ✅ Good: Responsive with sizes
<Image
  src="/photo.jpg"
  alt="Description"
  fill
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  priority={false} // Set true for LCP images
/>
```

**3. Image Configuration**

```javascript
// next.config.js
module.exports = {
  images: {
    formats: ['image/avif', 'image/webp'], // Modern formats
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'example.com',
        pathname: '/images/**',
      },
    ],
  },
}
```

### Font Optimization

**1. Use next/font**

```typescript
// app/layout.tsx
import { Inter, Roboto_Mono } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

const robotoMono = Roboto_Mono({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-roboto-mono',
})

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${inter.variable} ${robotoMono.variable}`}>
      <body>{children}</body>
    </html>
  )
}
```

**2. Local Fonts**

```typescript
import localFont from 'next/font/local'

const myFont = localFont({
  src: './my-font.woff2',
  display: 'swap',
  variable: '--font-my',
})
```

### Core Web Vitals Optimization

**1. Largest Contentful Paint (LCP)**
- Use `priority` prop on above-the-fold images
- Optimize server response time
- Remove render-blocking resources
- Use Suspense for non-critical content

**2. First Input Delay (FID)**
- Minimize JavaScript execution time
- Use dynamic imports for heavy components
- Break up long tasks

**3. Cumulative Layout Shift (CLS)**
- Always set image dimensions
- Reserve space for ads
- Avoid inserting content above existing content

---

## Security Best Practices

### XSS Prevention

**1. Avoid dangerouslySetInnerHTML**

```typescript
// ❌ Bad: XSS vulnerability
function Component({ userContent }) {
  return <div dangerouslySetInnerHTML={{ __html: userContent }} />
}

// ✅ Good: Sanitize with DOMPurify
import DOMPurify from 'isomorphic-dompurify'

function Component({ userContent }) {
  const sanitized = DOMPurify.sanitize(userContent)
  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />
}

// ✅ Better: Use markdown library with XSS protection
import ReactMarkdown from 'react-markdown'

function Component({ userContent }) {
  return <ReactMarkdown>{userContent}</ReactMarkdown>
}
```

**2. Sanitize User Input**

```typescript
// ❌ Bad: Direct use of URL parameters
function SearchPage({ searchParams }) {
  return <h1>Results for: {searchParams.query}</h1>
}

// ✅ Good: Sanitize and validate
import { z } from 'zod'

const searchSchema = z.object({
  query: z.string().max(100).regex(/^[a-zA-Z0-9\s]+$/),
})

function SearchPage({ searchParams }) {
  const validated = searchSchema.safeParse(searchParams)

  if (!validated.success) {
    return <div>Invalid search query</div>
  }

  return <h1>Results for: {validated.data.query}</h1>
}
```

### Server Actions Security

**1. Input Validation**

```typescript
// ❌ Bad: No validation
"use server"

export async function createUser(formData: FormData) {
  const name = formData.get('name')
  const email = formData.get('email')

  await db.user.create({ name, email })
}

// ✅ Good: Validate with Zod
"use server"

import { z } from 'zod'

const userSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
})

export async function createUser(formData: FormData) {
  const parsed = userSchema.safeParse({
    name: formData.get('name'),
    email: formData.get('email'),
  })

  if (!parsed.success) {
    return { error: 'Invalid input' }
  }

  await db.user.create(parsed.data)
  return { success: true }
}
```

**2. Authorization Checks**

```typescript
// ❌ Bad: No authorization
"use server"

export async function deleteUser(userId: string) {
  await db.user.delete({ where: { id: userId } })
}

// ✅ Good: Check authorization
"use server"

import { auth } from '@/lib/auth'

export async function deleteUser(userId: string) {
  const session = await auth()

  if (!session?.user) {
    throw new Error('Unauthorized')
  }

  // Check if user can delete this resource
  const user = await db.user.findUnique({ where: { id: userId } })
  if (user.id !== session.user.id && !session.user.isAdmin) {
    throw new Error('Forbidden')
  }

  await db.user.delete({ where: { id: userId } })
}
```

### API Route Security

**1. CSRF Protection**

```typescript
// app/api/users/route.ts
import { NextRequest } from 'next/server'
import { verifyCSRFToken } from '@/lib/csrf'

export async function POST(request: NextRequest) {
  // Verify CSRF token
  const csrfToken = request.headers.get('x-csrf-token')
  if (!await verifyCSRFToken(csrfToken)) {
    return Response.json({ error: 'Invalid CSRF token' }, { status: 403 })
  }

  // Process request
  const data = await request.json()
  // ...
}
```

**2. Rate Limiting**

```typescript
// app/api/login/route.ts
import { ratelimit } from '@/lib/redis'

export async function POST(request: NextRequest) {
  const ip = request.ip ?? '127.0.0.1'

  const { success } = await ratelimit.limit(ip)

  if (!success) {
    return Response.json({ error: 'Too many requests' }, { status: 429 })
  }

  // Process login
  // ...
}
```

**3. Input Validation**

```typescript
// app/api/users/route.ts
import { z } from 'zod'

const userSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  age: z.number().min(0).max(150),
})

export async function POST(request: NextRequest) {
  const body = await request.json()

  const validated = userSchema.safeParse(body)
  if (!validated.success) {
    return Response.json({ error: validated.error }, { status: 400 })
  }

  // Use validated.data
  await createUser(validated.data)
  return Response.json({ success: true })
}
```

### Environment Variables

**1. Never Expose Secrets**

```typescript
// ❌ Bad: Secret in client code
"use client"

const apiKey = process.env.API_SECRET // Exposed!

// ✅ Good: Use in Server Components or API routes
// app/api/data/route.ts
export async function GET() {
  const apiKey = process.env.API_SECRET // Safe, server-only
  const data = await fetch(`https://api.example.com?key=${apiKey}`)
  return Response.json(data)
}
```

**2. Proper Variable Naming**

```bash
# .env.local

# ❌ Bad: Secret in public variable
NEXT_PUBLIC_API_SECRET=abc123

# ✅ Good: Secrets are private, public vars are safe
DATABASE_URL=postgresql://...
API_SECRET=abc123
NEXT_PUBLIC_API_URL=https://api.example.com
```

### Security Headers

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const response = NextResponse.next()

  // Security headers
  response.headers.set('X-Frame-Options', 'DENY')
  response.headers.set('X-Content-Type-Options', 'nosniff')
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')

  // Content Security Policy
  response.headers.set(
    'Content-Security-Policy',
    "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
  )

  return response
}
```

---

## Debugging Strategies

### Hydration Errors

**Common Causes:**

1. **Date/Time Mismatches**
```typescript
// ❌ Bad: Server and client render different times
function Component() {
  return <div>{new Date().toLocaleString()}</div>
}

// ✅ Good: Use client-side rendering for dynamic dates
"use client"
import { useEffect, useState } from 'react'

function Component() {
  const [date, setDate] = useState('')

  useEffect(() => {
    setDate(new Date().toLocaleString())
  }, [])

  return <div>{date || 'Loading...'}</div>
}
```

2. **Window/Document Access**
```typescript
// ❌ Bad: Accessing window during render
function Component() {
  const width = window.innerWidth
  return <div>{width}</div>
}

// ✅ Good: Use useEffect
"use client"
import { useEffect, useState } from 'react'

function Component() {
  const [width, setWidth] = useState(0)

  useEffect(() => {
    setWidth(window.innerWidth)
  }, [])

  return <div>{width}</div>
}
```

### Build Errors

**TypeScript Strict Mode**

Enable strict checks:
```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

### Runtime Debugging

**1. Server Component Logs**
```typescript
// Server Components log to terminal, not browser
export default async function Page() {
  console.log('This logs in terminal') // Server-side
  const data = await getData()
  return <div>{data}</div>
}
```

**2. Client Component Logs**
```typescript
"use client"

export default function Component() {
  console.log('This logs in browser') // Client-side
  return <div>Component</div>
}
```

---

## Data Fetching

### Server Components Data Fetching

**1. Async/Await in Server Components**

```typescript
// app/posts/page.tsx
export default async function PostsPage() {
  // Direct database query (no API needed)
  const posts = await db.post.findMany()

  return (
    <ul>
      {posts.map(post => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
```

**2. Parallel Data Fetching**

```typescript
// ❌ Bad: Sequential (waterfall)
export default async function Page() {
  const user = await getUser()
  const posts = await getPosts() // Waits for user
  return <div>...</div>
}

// ✅ Good: Parallel
export default async function Page() {
  const [user, posts] = await Promise.all([
    getUser(),
    getPosts()
  ])
  return <div>...</div>
}
```

**3. Streaming with Suspense**

```typescript
// app/page.tsx
import { Suspense } from 'react'

export default function Page() {
  return (
    <div>
      <h1>Page Title</h1>
      <Suspense fallback={<div>Loading posts...</div>}>
        <Posts />
      </Suspense>
      <Suspense fallback={<div>Loading comments...</div>}>
        <Comments />
      </Suspense>
    </div>
  )
}

async function Posts() {
  const posts = await getPosts() // Streams independently
  return <div>{/* posts */}</div>
}

async function Comments() {
  const comments = await getComments() // Streams independently
  return <div>{/* comments */}</div>
}
```

### Client-Side Data Fetching

**Use SWR or React Query**

```typescript
"use client"
import useSWR from 'swr'

const fetcher = (url: string) => fetch(url).then(r => r.json())

export default function Profile() {
  const { data, error, isLoading } = useSWR('/api/user', fetcher)

  if (error) return <div>Failed to load</div>
  if (isLoading) return <div>Loading...</div>

  return <div>Hello {data.name}!</div>
}
```

---

## Caching & Revalidation

### Fetch Cache Options

**1. Force Cache (default in App Router)**
```typescript
// Cached indefinitely (until build or revalidate)
fetch('https://api.example.com/data')

// Explicit cache
fetch('https://api.example.com/data', { cache: 'force-cache' })
```

**2. No Store (always fresh)**
```typescript
// Never cached, always fetches fresh
fetch('https://api.example.com/data', { cache: 'no-store' })
```

**3. Revalidate (time-based)**
```typescript
// Revalidate every 60 seconds
fetch('https://api.example.com/data', {
  next: { revalidate: 60 }
})
```

### Route Segment Config

```typescript
// app/page.tsx

// Revalidate every 60 seconds
export const revalidate = 60

// Force dynamic rendering
export const dynamic = 'force-dynamic'

// Force static rendering
export const dynamic = 'force-static'

// Runtime edge or nodejs
export const runtime = 'edge'

export default async function Page() {
  const data = await getData()
  return <div>{data}</div>
}
```

### React Cache

```typescript
// lib/data.ts
import { cache } from 'react'

// Deduplicate requests within same render
export const getUser = cache(async (id: string) => {
  const user = await db.user.findUnique({ where: { id } })
  return user
})

// Can be called multiple times, only executes once per render
export default async function Page() {
  const user1 = await getUser('123')
  const user2 = await getUser('123') // Uses cached result

  return <div>...</div>
}
```

### Revalidation Strategies

**1. Time-based Revalidation**
```typescript
// Revalidate every hour
export const revalidate = 3600

export default async function Page() {
  const data = await getData()
  return <div>{data}</div>
}
```

**2. On-demand Revalidation**
```typescript
// app/api/revalidate/route.ts
import { revalidatePath, revalidateTag } from 'next/cache'

export async function POST(request: Request) {
  const path = request.nextUrl.searchParams.get('path')

  if (path) {
    revalidatePath(path)
    return Response.json({ revalidated: true })
  }

  return Response.json({ error: 'Missing path' }, { status: 400 })
}
```

**3. Tag-based Revalidation**
```typescript
// Fetch with tags
fetch('https://api.example.com/posts', {
  next: { tags: ['posts'] }
})

// Revalidate by tag
import { revalidateTag } from 'next/cache'

export async function createPost(data: FormData) {
  'use server'

  await db.post.create(...)
  revalidateTag('posts')
}
```

---

## SEO & Metadata

### Static Metadata

```typescript
// app/page.tsx
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Page Title',
  description: 'Page description',
  keywords: ['next.js', 'react', 'seo'],
  authors: [{ name: 'Author Name' }],
  openGraph: {
    title: 'Page Title',
    description: 'Page description',
    images: ['/og-image.jpg'],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Page Title',
    description: 'Page description',
    images: ['/twitter-image.jpg'],
  },
}

export default function Page() {
  return <div>Content</div>
}
```

### Dynamic Metadata

```typescript
// app/posts/[id]/page.tsx
import { Metadata } from 'next'

export async function generateMetadata({ params }): Promise<Metadata> {
  const post = await getPost(params.id)

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: [post.coverImage],
    },
  }
}

export default function PostPage({ params }) {
  return <div>Post {params.id}</div>
}
```

### Sitemap Generation

```typescript
// app/sitemap.ts
import { MetadataRoute } from 'next'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const posts = await getAllPosts()

  const postEntries = posts.map(post => ({
    url: `https://example.com/posts/${post.slug}`,
    lastModified: post.updatedAt,
    changeFrequency: 'weekly' as const,
    priority: 0.8,
  }))

  return [
    {
      url: 'https://example.com',
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1,
    },
    ...postEntries,
  ]
}
```

### Robots.txt

```typescript
// app/robots.ts
import { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: '/private/',
    },
    sitemap: 'https://example.com/sitemap.xml',
  }
}
```

---

## TypeScript Best Practices

### Component Props Typing

```typescript
// ✅ Good: Explicit prop types
interface ButtonProps {
  label: string
  onClick: () => void
  variant?: 'primary' | 'secondary'
  disabled?: boolean
}

export default function Button({
  label,
  onClick,
  variant = 'primary',
  disabled = false
}: ButtonProps) {
  return (
    <button onClick={onClick} disabled={disabled}>
      {label}
    </button>
  )
}
```

### Server Component Props

```typescript
// app/posts/[id]/page.tsx
interface PageProps {
  params: { id: string }
  searchParams: { [key: string]: string | string[] | undefined }
}

export default async function PostPage({ params, searchParams }: PageProps) {
  const post = await getPost(params.id)
  return <div>{post.title}</div>
}
```

### API Route Types

```typescript
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server'

interface User {
  id: string
  name: string
  email: string
}

export async function GET(request: NextRequest): Promise<NextResponse<User[]>> {
  const users = await getUsers()
  return NextResponse.json(users)
}

export async function POST(
  request: NextRequest
): Promise<NextResponse<{ user: User } | { error: string }>> {
  const body = await request.json()

  try {
    const user = await createUser(body)
    return NextResponse.json({ user })
  } catch (error) {
    return NextResponse.json({ error: 'Failed to create user' }, { status: 500 })
  }
}
```

---

## References

- **Next.js Documentation**: https://nextjs.org/docs
- **React Documentation**: https://react.dev
- **Web.dev Performance**: https://web.dev/performance
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **TypeScript Handbook**: https://www.typescriptlang.org/docs/
