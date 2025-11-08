# Security Patterns Quick Reference

Quick reference for grep patterns and what they detect.

## Critical Security Patterns

### SQL Injection
```bash
# Grep patterns
query.*\$\{.*\}           # Template literal SQL
raw\(.*\$\{.*\}           # Prisma raw with interpolation
execute\(.*\+.*\)         # String concatenation in SQL
\.query\(.*params         # Direct param insertion

# Example vulnerable code
db.query(`SELECT * FROM users WHERE id = ${userId}`)
db.$queryRaw`DELETE FROM posts WHERE id = ${postId}`
```

### XSS
```bash
# Grep patterns
dangerouslySetInnerHTML   # React's innerHTML
innerHTML\s*=             # Direct innerHTML assignment
eval\(                    # Code execution
new Function\(            # Dynamic function creation
createObjectURL.*blob     # Blob XSS

# Example vulnerable code
<div dangerouslySetInnerHTML={{ __html: userInput }} />
element.innerHTML = userComment;
```

### Command Injection
```bash
# Grep patterns
exec\(.*\$\{.*\}         # Template literal in exec
spawn\(.*\$\{.*\}        # Template literal in spawn
execSync\(               # Synchronous execution
child_process            # Process execution module

# Example vulnerable code
exec(`convert ${filename} output.pdf`)
spawn('git', [`clone ${userRepo}`])
```

### Hardcoded Secrets
```bash
# Grep patterns (case-insensitive)
api_key\s*=\s*['\"]\w+              # API key assignment
password\s*=\s*['\"]                # Password in code
secret\s*=\s*['\"]                  # Secret assignment
token\s*=\s*['\"]\w{20,}            # Long token strings
private_key                          # Private keys
sk_live|sk_test                     # Stripe keys
AKIA[0-9A-Z]{16}                    # AWS access keys

# Example vulnerable code
const API_KEY = 'sk_live_abc123xyz';
const password = 'admin123';
```

### Path Traversal
```bash
# Grep patterns
readFile.*params\.|req\.           # File reads from user input
\.\.\/                             # Parent directory references
path\.join\(.*params               # Path joins with user input

# Example vulnerable code
fs.readFile(`./uploads/${req.query.filename}`)
path.join(baseDir, userProvidedPath)  // If userProvidedPath = '../../../etc/passwd'
```

## Next.js Specific Patterns

### Server vs Client Components
```bash
# Grep patterns
'use client'|"use client"          # Client component marker
'use server'|"use server"          # Server actions
useState|useEffect                  # Client hooks
getServerSideProps                  # Pages Router (wrong in App Router)

# Files to check
app/**/*.tsx                       # Should default to Server Components
'use client' in presentational     # Often unnecessary
```

### Server Actions
```bash
# Grep patterns
'use server'                       # Server action files
export async function \w+Action    # Action functions

# Required checks
getServerSession                   # Auth check needed
\.parse\(|\.safeParse\(           # Input validation (Zod)
revalidatePath|revalidateTag      # Cache invalidation

# Example secure Server Action
'use server'
const session = await getServerSession();
if (!session) throw new Error('Unauthorized');
const data = schema.parse(formData);
```

### Metadata API (App Router)
```bash
# Grep patterns
Head from 'next/head'              # Wrong in App Router
export const metadata              # Correct static metadata
export.*generateMetadata           # Correct dynamic metadata

# Migration
❌ import Head from 'next/head'
✅ export const metadata = { title: '...' }
```

### Data Fetching
```bash
# Grep patterns
getServerSideProps                 # Pages Router only
getStaticProps                     # Pages Router only
getInitialProps                    # Legacy
fetch.*cache:                      # App Router caching

# App Router correct patterns
fetch(url, { next: { revalidate: 3600 } })
fetch(url, { cache: 'force-cache' })
fetch(url, { cache: 'no-store' })
```

## Authentication/Authorization

### Missing Auth Checks
```bash
# Files requiring auth
app/api/**/route.ts               # All API routes
app/actions.ts                    # All Server Actions
app/dashboard/**/page.tsx         # Protected pages

# Required patterns in above files
getServerSession                  # NextAuth
auth\(\)                         # Clerk/other
verify.*token                     # JWT verification

# Anti-pattern
export async function DELETE(req: Request) {
  await db.user.delete(...);      # No auth check!
}
```

### Weak Session Management
```bash
# Grep patterns
cookie.*httpOnly.*false           # Insecure cookies
cookie.*secure.*false             # Non-HTTPS cookies
cookie.*sameSite.*none            # CSRF risk
localStorage.*token               # Token in localStorage (XSS risk)

# Secure patterns
httpOnly: true
secure: true
sameSite: 'strict'
```

## Input Validation

### Missing Validation
```bash
# Grep patterns
JSON\.parse\(.*req\.              # Parsing user input
formData\.get\(                   # Form data without validation
searchParams\.get\(               # URL params without validation

# Should be followed by
z\.|schema\.parse                 # Zod validation
typeof.*===                       # Type checking
/^\d+$/.test                      # Regex validation

# Example secure pattern
const userId = searchParams.get('id');
if (!userId || !/^\d+$/.test(userId)) {
  return Response.json({ error: 'Invalid ID' }, { status: 400 });
}
```

## Type Safety Issues

### TypeScript Anti-patterns
```bash
# Grep patterns
\bany\b                           # Any type usage
as any                            # Type assertion to any
\!\.                              # Non-null assertion
@ts-ignore                        # Ignoring errors
@ts-expect-error                  # Suppressing errors

# Context matters
any in function return            # High priority
any in function params            # High priority
any in variable declaration       # Medium priority
```

### Unsafe Assertions
```bash
# Pattern
variableName!\.<property>         # Non-null assertion

# Check for
if (variableName)                 # Proper null check before
?.                                # Optional chaining instead

# Example
❌ const email = user!.email;
✅ if (!user) throw new Error();
✅ const email = user.email;
```

## Performance Anti-patterns

### Client-Side Fetching in Server Components
```bash
# Anti-pattern
'use client'
useEffect(() => {
  fetch('/api/data')              # Should be Server Component
    .then(r => r.json())
    .then(setData);
}, []);

# Correct pattern
// No 'use client'
async function getData() {
  const res = await fetch('...', { next: { revalidate: 60 } });
  return res.json();
}
```

### Blocking Operations
```bash
# Grep patterns
fs\.readFileSync                  # Sync file operations
execSync                          # Sync process execution
while\(true\)                     # Infinite loops

# Should use async versions
fs.readFile (async)
exec/execFile (async with promisify)
```

## Error Handling

### Missing Try-Catch
```bash
# Grep patterns
await.*fetch\(                    # Async operations
await.*prisma\.                   # Database calls
await.*\.\$queryRaw               # Raw queries

# Should be wrapped in
try {
  await riskyOperation();
} catch (error) {
  // Handle error
}
```

### Information Disclosure
```bash
# Anti-pattern
catch (error) {
  return Response.json({ error: error.message }, { status: 500 });
}
# Exposes stack traces, SQL errors, etc.

# Secure pattern
catch (error) {
  console.error(error);  // Log full error
  return Response.json({ error: 'Internal server error' }, { status: 500 });
}
```

## Quick Scan Commands

### Critical Issues Only
```bash
# SQL Injection
rg "query.*\$\{.*\}" --type ts

# Hardcoded Secrets
rg -i "api_key\s*=\s*['\"]" --type ts

# XSS
rg "dangerouslySetInnerHTML" --type tsx

# Command Injection
rg "exec\(.*\$\{.*\}" --type ts
```

### Next.js Patterns
```bash
# Wrong data fetching in App Router
rg "getServerSideProps|getStaticProps" app/

# Missing 'use client' with hooks
rg "useState|useEffect" app/ -l | xargs rg -L "'use client'"

# Client components that should be Server
rg "'use client'" app/ -l | xargs rg -L "useState|useEffect|onClick|onChange"
```

### Auth Issues
```bash
# Server Actions without auth
rg "'use server'" -A 10 | rg -v "getServerSession|auth\(\)"

# API routes without auth
rg "export async function (GET|POST|PUT|DELETE)" app/api/ -A 5 | rg -v "getServerSession"
```

## Priority Matrix

```
┌─────────────────┬──────────────────────────────────────┐
│ CRITICAL        │ - SQL Injection                      │
│ (Fix Now)       │ - Hardcoded Secrets in Client Code   │
│                 │ - Auth Bypass                        │
│                 │ - RCE/Command Injection              │
├─────────────────┼──────────────────────────────────────┤
│ HIGH            │ - XSS                                │
│ (Fix Today)     │ - Missing Auth Checks                │
│                 │ - Insecure Deserialization           │
│                 │ - Path Traversal                     │
├─────────────────┼──────────────────────────────────────┤
│ MEDIUM          │ - Missing Input Validation           │
│ (Fix This Week) │ - Weak Error Handling                │
│                 │ - Performance Issues                 │
│                 │ - Type Safety Violations             │
├─────────────────┼──────────────────────────────────────┤
│ LOW             │ - Code Style                         │
│ (Backlog)       │ - Dead Code                          │
│                 │ - Minor Optimizations                │
└─────────────────┴──────────────────────────────────────┘
```

## Testing Patterns

### Test for False Positives

```typescript
// ✅ OK - Commented code
// const API_KEY = 'example_key';

// ✅ OK - Type definition
interface Config {
  apiKey: string;
}

// ✅ OK - Env var reference
const key = process.env.API_KEY;

// ❌ REAL ISSUE - Hardcoded
const key = 'sk_live_abc123';
```

### Context Matters

```typescript
// Pattern: any type
// ❌ Critical in function signature
export function processData(data: any): any { }

// ⚠️ Medium in type assertion
const data = response as any;

// ℹ️ Low in generic constraint
function wrap<T = any>(value: T) { }
```

## Quick Reference Card

**Most Critical Checks (Run First)**
1. `rg "'use server'" -A 20 | rg -v "getServerSession"` - Unprotected Server Actions
2. `rg "sk_live|sk_test|AKIA|password\s*=\s*['\"]"` - Hardcoded secrets
3. `rg "query.*\$\{.*\}|raw.*\$\{.*\}"` - SQL injection
4. `rg "exec\(.*\$\{.*\}|spawn\(.*\$\{.*\}"` - Command injection
5. `rg "dangerouslySetInnerHTML"` - XSS vectors

**Quick Health Check**
- `rg "getServerSideProps" app/` - Should be empty (App Router)
- `rg "'use client'" app/ | wc -l` - Should be minimal
- `rg "\bany\b" --type ts | wc -l` - Lower is better
- `rg "@ts-ignore" | wc -l` - Should be near zero
