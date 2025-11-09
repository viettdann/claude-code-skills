# Detection Patterns for Next.js Kits

This file contains grep patterns for detecting performance issues, security vulnerabilities, common bugs, and optimization opportunities in Next.js applications.

## Performance Patterns

### Bundle Size Issues

**Large Client-Side Dependencies**
```
Grep patterns:
- "import.*moment"  # Moment.js is large, use date-fns or dayjs
- "import.*lodash['\"]"  # Import specific functions, not entire library
- "import.*@mui/material['\"]"  # Import specific components
- "import.*antd['\"]"  # Import specific components
- "import.*\* as"  # Avoid namespace imports for large libraries
```

**Missing Dynamic Imports**
```
Grep patterns:
- "import.*Modal.*from"  # Modals should be lazy loaded
- "import.*Chart.*from"  # Charts should be lazy loaded
- "import.*Editor.*from"  # Editors should be lazy loaded
- "import.*Map.*from"  # Maps should be lazy loaded
```

**Client-Only Libraries in Server Components**
```
Grep patterns:
- "window\\.|document\\."  # Browser APIs in Server Components
- "localStorage\\.|sessionStorage\\."  # Client-only storage
- "navigator\\."  # Browser navigator API
```

### Rendering Performance

**Missing Suspense Boundaries**
```
Grep patterns:
- "async function.*\\{[^}]*await"  # Async Server Components without Suspense
- "use.*fetch\\("  # Data fetching without loading states
```

**Blocking Renders**
```
Grep patterns:
- "await.*fetch.*layout"  # Blocking fetch in layouts
- "export default async function Layout"  # Async layouts can block rendering
```

**Inefficient Re-renders**
```
Grep patterns:
- "\\{\\.\\.\\."  # Spread props can cause unnecessary re-renders
- "onClick=\\{\\(\\) => "  # Inline arrow functions in JSX
- "style=\\{\\{"  # Inline style objects
- "className=\\{`.*\\$\\{"  # Dynamic className without memoization
```

### Caching Issues

**Missing Cache Configuration**
```
Grep patterns:
- "fetch\\([^)]*\\)"  # Fetch without explicit cache option
- "fetch\\([^)]*cache: ['\"]no-store"  # Overuse of no-store
```

**Revalidation Problems**
```
Grep patterns:
- "revalidate:\\s*0"  # Disabled revalidation
- "export const revalidate"  # Route segment revalidation
- "next: \\{ revalidate:"  # Fetch-level revalidation
```

### Image Optimization

**Unoptimized Images**
```
Grep patterns:
- "<img\\s"  # Native img tags instead of next/image
- "<img.*src=\\{[^}]*\\}"  # Dynamic images without next/image
- "background-image:.*url\\("  # CSS background images
```

**Missing Image Dimensions**
```
Grep patterns:
- "<Image.*src=.*(?!.*width)"  # Image without width
- "<Image.*src=.*(?!.*height)"  # Image without height
- "<Image.*fill.*(?!.*sizes)"  # Fill images without sizes prop
```

**Unoptimized Image Formats**
```
Grep patterns:
- "\\.png['\"]"  # PNG images (consider WebP/AVIF)
- "\\.jpg['\"]|\\.jpeg['\"]"  # JPEG images (consider WebP/AVIF)
```

### Font Optimization

**Unoptimized Font Loading**
```
Grep patterns:
- "@import.*fonts\\.googleapis"  # CSS font imports instead of next/font
- "<link.*fonts\\.googleapis"  # Link tag font imports
- "font-face"  # Manual @font-face definitions
```

### Code Splitting

**Missing Dynamic Imports**
```
Grep patterns:
- "import\\s+.*Modal.*from"  # Heavy components not lazy loaded
- "import\\s+.*Chart.*from"
- "import\\s+.*Markdown.*from"
- "import\\s+.*CodeEditor.*from"
```

## Security Patterns

### XSS Vulnerabilities

**Dangerous HTML Rendering**
```
Grep patterns:
- "dangerouslySetInnerHTML"  # Potential XSS vector
- "innerHTML\\s*="  # Direct innerHTML manipulation
- "outerHTML\\s*="  # Direct outerHTML manipulation
- "\\.html\\("  # jQuery-style HTML insertion
```

**Unsanitized User Input**
```
Grep patterns:
- "\\$\\{.*params\\."  # Template literals with URL params
- "\\$\\{.*searchParams\\."  # Template literals with search params
- "\\$\\{.*formData\\."  # Template literals with form data
- "\\+.*req\\.body"  # String concatenation with request body
```

### CSRF Protection

**Unprotected API Routes**
```
Grep patterns:
- "export async function POST\\("  # POST handler without CSRF check
- "export async function PUT\\("  # PUT handler without CSRF check
- "export async function DELETE\\("  # DELETE handler without CSRF check
- "export async function PATCH\\("  # PATCH handler without CSRF check
```

### Server Actions Security

**Missing Input Validation**
```
Grep patterns:
- "['\"]use server['\"]"  # Server Actions
- "export async function.*formData: FormData"  # Server Action without validation
```

**Missing Authorization**
```
Grep patterns:
- "['\"]use server['\"].*(?!.*auth|.*session|.*user)"  # Server Action without auth check
```

### Environment Variable Exposure

**Secrets in Client Code**
```
Grep patterns:
- "process\\.env\\.(?!NEXT_PUBLIC_)"  # Non-public env vars in client code
- "API_KEY|SECRET|PASSWORD|TOKEN"  # Hardcoded secrets
- "NEXT_PUBLIC_.*SECRET|NEXT_PUBLIC_.*PASSWORD|NEXT_PUBLIC_.*TOKEN"  # Secrets in public vars
```

**Missing Environment Variables**
```
Grep patterns:
- "process\\.env\\.[A-Z_]+"  # Environment variable usage (check .env files)
```

### API Route Security

**Missing Rate Limiting**
```
Grep patterns:
- "export async function (POST|PUT|DELETE|PATCH)\\((?!.*ratelimit)"  # API routes without rate limiting
```

**Missing Input Validation**
```
Grep patterns:
- "req\\.json\\(\\)(?!.*validate|.*parse|.*schema)"  # JSON parsing without validation
- "searchParams\\.get\\((?!.*validate)"  # Query params without validation
```

**SQL Injection Risk**
```
Grep patterns:
- "query\\(.*\\$\\{.*\\}"  # Template literal SQL
- "execute\\(.*\\$\\{.*\\}"  # Template literal SQL
- "\\`SELECT.*\\$\\{"  # String interpolation in SQL
```

### Authentication Issues

**Missing Auth Checks**
```
Grep patterns:
- "export default async function.*Page.*(?!.*auth|.*session)"  # Pages without auth
- "export async function (GET|POST).*(?!.*auth|.*session)"  # API routes without auth
```

**Insecure Session Handling**
```
Grep patterns:
- "localStorage\\.setItem.*token|session"  # Storing auth tokens in localStorage
- "sessionStorage\\.setItem.*token|session"  # Storing auth tokens in sessionStorage
```

### Content Security Policy

**Missing Security Headers**
```
Grep patterns:
- "export.*function middleware"  # Middleware (check for security headers)
```

## Debugging Patterns

### Hydration Errors

**Client/Server Mismatches**
```
Grep patterns:
- "new Date\\(\\)"  # Dynamic dates cause hydration mismatches
- "Math\\.random\\(\\)"  # Random values cause mismatches
- "Date\\.now\\(\\)"  # Timestamps cause mismatches
- "useEffect\\(\\(\\) => \\{[^}]*innerHTML"  # Direct DOM manipulation
```

**Conditional Rendering Issues**
```
Grep patterns:
- "typeof window !== ['\"]undefined['\"]"  # Client-side checks in render
- "window &&"  # Window checks in render
- "document &&"  # Document checks in render
```

### Build Errors

**TypeScript Issues**
```
Grep patterns:
- ": any"  # Any type usage
- "as any"  # Type assertions to any
- "@ts-ignore"  # TypeScript ignore comments
- "@ts-nocheck"  # TypeScript nocheck
```

**Module Resolution**
```
Grep patterns:
- "import.*\\.\\./"  # Relative imports (consider path aliases)
- "require\\("  # CommonJS requires in ESM context
```

### Runtime Errors

**API Route Errors**
```
Grep patterns:
- "export async function (GET|POST|PUT|DELETE|PATCH)(?!.*try)"  # API routes without try-catch
```

**Server Component Errors**
```
Grep patterns:
- "['\"]use client['\"].*useState|useEffect|createContext"  # Client hooks
- "(?<!use client).*useState|useEffect"  # Client hooks in Server Components
```

### Layout and Metadata Issues

**Missing Metadata**
```
Grep patterns:
- "export default function.*Page(?!.*metadata|.*generateMetadata)"  # Pages without metadata
```

**Layout Nesting Issues**
```
Grep patterns:
- "export default function Layout\\((?!.*children)"  # Layouts without children prop
```

### Routing Issues

**Dynamic Route Issues**
```
Grep patterns:
- "\\[.*\\]\\.tsx"  # Dynamic route files
- "\\[\\.\\.\\..*\\]\\.tsx"  # Catch-all route files
```

**Route Group Issues**
```
Grep patterns:
- "\\(.*\\)"  # Route groups (check for proper structure)
```

## Code Optimization Patterns

### Component Optimization

**Missing Memoization**
```
Grep patterns:
- "export default function.*\\{[^}]*\\.map\\("  # Components with map (consider memo)
- "export default function.*\\{[^}]*props\\."  # Components with props (consider memo)
```

**Missing useMemo/useCallback**
```
Grep patterns:
- "const.*=.*\\{.*:.*\\}"  # Object literals in components
- "const.*=.*\\[.*\\]"  # Array literals in components
- "const.*=.*\\(\\).*=>"  # Function definitions in components
```

### Data Fetching Optimization

**Waterfall Requests**
```
Grep patterns:
- "await fetch.*await fetch"  # Sequential fetches (use Promise.all)
```

**Missing Parallel Fetching**
```
Grep patterns:
- "const.*=.*await fetch.*const.*=.*await fetch"  # Sequential fetches
```

**Missing Streaming**
```
Grep patterns:
- "export default async function.*Page.*await.*(?!.*Suspense)"  # Async pages without streaming
```

### SEO Optimization

**Missing Metadata**
```
Grep patterns:
- "export default function.*Page(?!.*metadata)"  # Pages without metadata
```

**Missing Sitemap**
```
Grep patterns:
- "sitemap\\.xml|sitemap\\.ts"  # Check for sitemap
```

**Missing Robots.txt**
```
Grep patterns:
- "robots\\.txt|robots\\.ts"  # Check for robots.txt
```

**Missing Structured Data**
```
Grep patterns:
- "application/ld\\+json"  # JSON-LD structured data
- "schema\\.org"  # Schema.org markup
```

### Accessibility Patterns

**Missing Alt Text**
```
Grep patterns:
- "<img(?!.*alt=)"  # Images without alt
- "<Image(?!.*alt=)"  # next/image without alt
```

**Missing ARIA Labels**
```
Grep patterns:
- "<button(?!.*aria-label)"  # Buttons without ARIA labels
- "onClick(?!.*aria-label|.*children)"  # Click handlers without labels
```

**Missing Semantic HTML**
```
Grep patterns:
- "<div.*onClick"  # Clickable divs (use button)
- "<div.*role=['\"]button"  # Divs styled as buttons
```

### TypeScript Best Practices

**Type Safety Issues**
```
Grep patterns:
- ": any"  # Any type usage
- "as any"  # Type assertions to any
- "!"  # Non-null assertions
- "// @ts-"  # TypeScript disable comments
```

**Missing Generic Types**
```
Grep patterns:
- "useState\\(\\)"  # useState without type parameter
- "useRef\\(\\)"  # useRef without type parameter
```

## Middleware Patterns

### Security Headers

**Missing Headers**
```
Grep patterns:
- "export function middleware(?!.*X-Frame-Options)"  # Missing X-Frame-Options
- "export function middleware(?!.*X-Content-Type-Options)"  # Missing X-Content-Type-Options
- "export function middleware(?!.*Strict-Transport-Security)"  # Missing HSTS
```

### Rate Limiting

**Missing Rate Limits**
```
Grep patterns:
- "export function middleware(?!.*ratelimit|.*throttle)"  # Middleware without rate limiting
```

## Configuration Patterns

### Next.js Config Issues

**Missing Optimizations**
```
Grep patterns in next.config.js:
- "(?!.*images)"  # Missing image configuration
- "(?!.*compress)"  # Missing compression
- "(?!.*swcMinify)"  # Missing SWC minification
```

**Security Issues in Config**
```
Grep patterns in next.config.js:
- "reactStrictMode:\\s*false"  # Disabled strict mode
- "poweredByHeader:\\s*true"  # Exposing Next.js version
```

### TypeScript Config Issues

**Missing Strict Checks**
```
Grep patterns in tsconfig.json:
- "\"strict\":\\s*false"  # Disabled strict mode
- "\"noImplicitAny\":\\s*false"  # Disabled noImplicitAny
```

## Docker & Azure Deployment Patterns

### Container Security

**Running as Root**
```
Grep patterns in Dockerfile:
- "^USER root"  # Running as root user
- "^(?!.*USER)"  # Missing USER directive (defaults to root)
```

**Exposed Secrets**
```
Grep patterns in Dockerfile:
- "ENV.*PASSWORD|SECRET|KEY|TOKEN"  # Secrets in ENV
- "ARG.*PASSWORD|SECRET|KEY|TOKEN"  # Secrets in build args
- "COPY \\.env"  # Copying .env into image
```

**Insecure Base Images**
```
Grep patterns in Dockerfile:
- "FROM.*:latest"  # Using latest tag (unpinned)
- "FROM node:.*(?!alpine)"  # Not using slim/alpine variants
```

**Missing Security Updates**
```
Grep patterns in Dockerfile:
- "(?!.*apt-get.*upgrade)"  # Missing security updates
- "(?!.*apk.*upgrade)"  # Missing apk upgrades
```

### Response Time & Performance Issues

**Blocking File I/O**
```
Grep patterns in API routes and Server Components:
- "fs\\.readFileSync"  # Synchronous file read
- "fs\\.writeFileSync"  # Synchronous file write
- "fs\\.existsSync"  # Synchronous existence check
- "fs\\.statSync"  # Synchronous stat
```

**Missing Timeouts**
```
Grep patterns:
- "fetch\\([^)]*(?!.*signal|.*timeout)"  # Fetch without timeout
- "axios\\.get\\((?!.*timeout)"  # Axios without timeout
- "http\\.request\\((?!.*timeout)"  # HTTP request without timeout
```

**Blocking Crypto Operations**
```
Grep patterns:
- "crypto\\.pbkdf2Sync"  # Synchronous password hashing
- "crypto\\.scryptSync"  # Synchronous key derivation
- "bcrypt\\.hashSync"  # Synchronous bcrypt
```

**Slow Startup**
```
Grep patterns:
- "import.*\\.json"  # Large JSON imports at startup
- "fs\\.readFileSync.*package\\.json"  # Reading files at startup
- "new.*connection"  # Database connections at module level
```

### Unresponsive Code Patterns

**Infinite Loops Risk**
```
Grep patterns:
- "while\\s*\\(true\\)"  # Infinite while loop
- "for\\s*\\(;;\\)"  # Infinite for loop
- "setInterval\\("  # Intervals without cleanup
```

**Missing Async/Await**
```
Grep patterns:
- "\\.then\\(.*\\.then\\("  # Promise chains (use async/await)
- "function.*\\{[^}]*fetch\\("  # Non-async functions with fetch
```

**CPU-Intensive Operations**
```
Grep patterns:
- "\\.sort\\(\\)(?!.*worker)"  # Large array sorting
- "\\.map\\(.*\\.map\\(.*\\.map\\("  # Nested map operations
- "JSON\\.parse\\(.*(?!.*stream)"  # Large JSON parsing
- "Buffer\\.from\\(.*base64(?!.*stream)"  # Large base64 operations
```

**Missing Request Timeouts**
```
Grep patterns:
- "export async function (GET|POST|PUT|DELETE|PATCH)\\((?!.*timeout)"  # API routes without timeouts
```

### Docker Build Configuration

**Missing Multi-Stage Build**
```
Grep patterns in Dockerfile:
- "FROM node.*(?!.*AS)"  # Single stage build
```

**Inefficient Layer Caching**
```
Grep patterns in Dockerfile:
- "COPY \\. \\."  # Copying everything (breaks layer cache)
- "COPY.*(?!package)"  # Copying before npm install
```

**Missing .dockerignore**
```
Check for file existence:
- .dockerignore file missing
```

**Incorrect NODE_ENV**
```
Grep patterns in Dockerfile:
- "NODE_ENV=development"  # Development mode in production
- "(?!.*NODE_ENV=production)"  # Missing production setting
```

**Missing Health Check**
```
Grep patterns in Dockerfile:
- "(?!.*HEALTHCHECK)"  # Missing HEALTHCHECK directive
```

### Environment & Configuration Issues

**Missing Standalone Output**
```
Grep patterns in next.config.js:
- "(?!.*output.*standalone)"  # Missing standalone output for Docker
```

**Wrong Port Configuration**
```
Grep patterns:
- "listen\\(3000\\)"  # Hardcoded port instead of process.env.PORT
- "listen\\(.*(?!process\\.env\\.PORT)"  # Not using Azure's PORT env var
```

**Missing Health Check Endpoint**
```
Grep patterns:
- "(?!.*api/health|/health)"  # No health check endpoint
```

**Secrets in Client Code**
```
Grep patterns in app/, components/, pages/:
- "process\\.env\\.(?!NEXT_PUBLIC_)"  # Server-only env vars in client
- "NEXT_PUBLIC_.*SECRET|PASSWORD|KEY"  # Secrets with public prefix
```

### Resource Management Issues

**Memory Leaks**
```
Grep patterns:
- "global\\.|window\\."  # Global variable accumulation
- "addEventListener\\((?!.*removeEventListener)"  # Event listeners without cleanup
- "setInterval\\((?!.*clearInterval)"  # Intervals without cleanup
- "cache\\.set\\((?!.*maxSize|.*ttl)"  # Unbounded caching
```

**Unbounded Operations**
```
Grep patterns:
- "SELECT \\*(?!.*LIMIT)"  # Database queries without LIMIT
- "\\.find\\(\\)(?!.*limit)"  # MongoDB queries without limit
- "formidable.*(?!.*maxFileSize)"  # File uploads without size limit
- "\\.map\\(.*(?!.*slice)"  # Large array operations
```

**Missing Payload Limits**
```
Grep patterns in API routes:
- "export const config.*(?!.*bodyParser|.*maxFileSize)"  # Missing body size limits
```

### Azure App Services Specific

**Missing Startup Command**
```
Grep patterns in package.json:
- "(?!.*\"start\":|.*\"server\")"  # Missing start script
```

**CORS Issues**
```
Grep patterns in next.config.js or middleware:
- "(?!.*Access-Control-Allow-Origin)"  # Missing CORS headers
```

**Missing Application Insights**
```
Grep patterns:
- "(?!.*applicationinsights|.*@azure/monitor)"  # No App Insights integration
```

**ARR Affinity Issues**
```
Grep patterns in next.config.js:
- "(?!.*ARR_DISABLE_COOL_DOWN)"  # ARR affinity not configured
```

### Production Readiness

**Missing Error Handlers**
```
Grep patterns:
- "export async function (GET|POST|PUT|DELETE|PATCH)\\((?!.*try|.*catch)"  # API routes without error handling
```

**Missing Graceful Shutdown**
```
Grep patterns:
- "(?!.*process\\.on\\(['\"]SIGTERM)"  # Missing SIGTERM handler
- "(?!.*process\\.on\\(['\"]SIGINT)"  # Missing SIGINT handler
```

**Console Logging & Debug Statements in Production**
```
Grep patterns:
- "console\\.log\\("  # Console.log (use proper logger)
- "console\\.error\\("  # Console.error (use proper logger)
- "console\\.warn\\("  # Console.warn (use proper logger)
- "console\\.info\\("  # Console.info (use proper logger)
- "console\\.debug\\("  # Console.debug (use proper logger)
- "console\\.trace\\("  # Console.trace (use proper logger)
- "console\\.dir\\("  # Console.dir (use proper logger)
- "console\\.table\\("  # Console.table (use proper logger)
- "console\\.time\\("  # Performance debugging
- "console\\.timeEnd\\("  # Performance debugging
- "debugger;"  # JavaScript debugger statement
```

**Missing Structured Logging**
```
Grep patterns:
- "console\\.(?!.*JSON\\.stringify)"  # Non-JSON logging
- "(?!.*winston|.*pino|.*bunyan)"  # No structured logging library
```

**Incorrect HTTP Status Codes (Anti-Pattern)**
```
Grep patterns in API routes and Server Actions:
# Explicit 200 with error indicators
- "return.*Response.*200.*\\{.*error"  # 200 OK with error field
- "return.*Response.*200.*\\{.*err"  # 200 OK with err field
- "return.*new Response\\(.*\\{.*error.*\\}.*\\{.*status.*200"  # Explicit 200 with error
- "status.*200.*\\{.*(error|err|issue|problem|failure|exception)"  # 200 with error fields

# Error fields without proper status codes
- "return.*NextResponse\\.json\\(.*\\{.*error.*\\}\\)(?!.*status)"  # error field without status
- "return.*NextResponse\\.json\\(.*\\{.*err.*\\}\\)(?!.*status)"  # err field without status
- "return.*NextResponse\\.json\\(.*\\{.*issue.*\\}\\)(?!.*status)"  # issue field without status
- "return.*NextResponse\\.json\\(.*\\{.*problem.*\\}\\)(?!.*status)"  # problem field without status
- "return.*NextResponse\\.json\\(.*\\{.*failure.*\\}\\)(?!.*status)"  # failure field without status
- "return.*NextResponse\\.json\\(.*\\{.*exception.*\\}\\)(?!.*status)"  # exception field without status
- "return.*NextResponse\\.json\\(.*\\{.*fault.*\\}\\)(?!.*status)"  # fault field without status
- "return.*NextResponse\\.json\\(.*\\{.*warning.*\\}\\)(?!.*status)"  # warning field without status

# Message fields that might hide errors
- "return.*NextResponse\\.json\\(.*\\{.*message.*\\}\\)(?!.*status)"  # message without status (check context)
- "return.*NextResponse\\.json\\(.*\\{.*msg.*\\}\\)(?!.*status)"  # msg without status (check context)
- "return.*NextResponse\\.json\\(.*\\{.*messages.*\\}\\)(?!.*status)"  # messages without status

# Boolean flags indicating failure with 200
- "NextResponse\\.json\\(.*\\{.*success.*false.*\\}\\)(?!.*status.*[45])"  # success: false without 4xx/5xx
- "NextResponse\\.json\\(.*\\{.*ok.*false.*\\}\\)(?!.*status.*[45])"  # ok: false without 4xx/5xx
- "NextResponse\\.json\\(.*\\{.*valid.*false.*\\}\\)(?!.*status.*[45])"  # valid: false without 4xx/5xx
- "NextResponse\\.json\\(.*\\{.*failed.*true.*\\}\\)(?!.*status.*[45])"  # failed: true without 4xx/5xx
- "NextResponse\\.json\\(.*\\{.*isError.*true.*\\}\\)(?!.*status.*[45])"  # isError: true without 4xx/5xx
- "NextResponse\\.json\\(.*\\{.*hasError.*true.*\\}\\)(?!.*status.*[45])"  # hasError: true without 4xx/5xx

# Contradictory responses
- "\\{.*ok.*true.*error.*\\}"  # ok: true but with error field
- "\\{.*success.*true.*(error|err|issue|problem).*\\}"  # success: true with error fields
- "\\{.*ok.*true.*(error|err|issue|problem).*\\}"  # ok: true with error fields

# Status field with error values (not HTTP status)
- "\\{.*status.*['\"]error['\"].*\\}(?!.*status.*[45])"  # status: "error" without HTTP 4xx/5xx
- "\\{.*status.*['\"]fail(ed)?['\"].*\\}(?!.*status.*[45])"  # status: "fail" without HTTP error code
- "\\{.*status.*['\"]invalid['\"].*\\}(?!.*status.*[45])"  # status: "invalid" without HTTP error code

# Error message text in 200 responses
- "status.*200.*message.*['\"]error|fail|invalid|denied|forbidden|unauthorized"  # 200 with error message text
```

**Missing Error Status Codes in API Routes**
```
Grep patterns:
- "catch.*\\{[^}]*return.*Response(?!.*status.*[45])"  # Error catch without 4xx/5xx status
- "catch.*\\{[^}]*NextResponse\\.json(?!.*status.*[45])"  # Error catch without proper status
- "throw.*new Error(?!.*status)"  # Throwing errors without status metadata
- "if.*error.*return.*NextResponse\\.json\\((?!.*status)"  # Error condition without status
- "if.*(error|err|fail).*return.*Response\\((?!.*status.*[45])"  # Error check without proper status
```

**Nested or Array Error Fields (sneaky hiding)**
```
Grep patterns:
- "\\{.*data.*\\{.*error"  # Nested error in data field
- "\\{.*result.*\\{.*error"  # Nested error in result field
- "\\{.*response.*\\{.*error"  # Nested error in response field
- "\\{.*errors.*\\["  # Array of errors
- "\\{.*issues.*\\["  # Array of issues
- "\\{.*problems.*\\["  # Array of problems
- "\\{.*validationErrors.*\\["  # Validation errors array
```

**Missing Success Status Codes**
```
Grep patterns:
- "export async function POST.*return.*Response(?!.*status.*20[01])"  # POST without 200/201
- "export async function PUT.*return.*Response(?!.*status.*20[0-4])"  # PUT without 2xx
- "export async function DELETE.*return.*Response(?!.*status.*20[0-4])"  # DELETE without 2xx
```

**Missing Monitoring**
```
Grep patterns:
- "(?!.*@sentry|.*newrelic|.*datadog)"  # No error tracking
```

## Usage Notes

1. **Combine patterns**: Use multiple patterns for comprehensive detection
2. **Read context**: Always examine surrounding code to validate findings
3. **Version-specific**: Some patterns apply to specific Next.js versions
4. **Framework conventions**: Consider App Router vs Pages Router differences
5. **False positives**: Validate each match - patterns may catch legitimate code

## Pattern Priority

**Critical Priority** (Security & Production Blockers):
- Container security (running as root, exposed secrets)
- XSS vulnerabilities
- CSRF protection
- Server Actions security
- Environment variable exposure
- SQL injection
- Unresponsive code patterns
- Missing graceful shutdown

**High Priority** (Performance & Deployment):
- Incorrect HTTP status codes (200 OK with errors) - API anti-pattern
- Blocking operations (file I/O, crypto)
- Missing timeouts
- Memory leaks and unbounded operations
- Docker build configuration issues
- Bundle size issues
- Rendering performance
- Image optimization
- Caching issues
- Missing health checks
- Azure App Services configuration
- Missing error status codes in catch blocks

**Medium Priority** (Code Quality & Optimization):
- Console.log and console.error in production
- TypeScript best practices
- Component optimization
- Accessibility
- SEO optimization
- Resource management
- Missing structured logging

**Low Priority** (Style & Minor Issues):
- Debugger statements
- console.time/timeEnd performance debugging
- Docker image size optimizations
- Code refactoring opportunities
