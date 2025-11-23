# Code Review Report

## Summary
- **Result**: CRITICAL_ISSUES_FOUND
- **Files Scanned**: 8
- **Critical Issues**: 2
- **High Issues**: 1

## Critical Issues

### Hardcoded Stripe Secret Key in Client Component
- **File**: `app/components/PaymentForm.tsx:15`
- **Severity**: CRITICAL
- **Confidence**: 100
- **Problem**: Stripe live secret key (sk_live_*) hardcoded directly in a client-side React component marked with 'use client' directive. This secret will be included in the client JavaScript bundle.
- **Why Critical**: The Stripe secret key is exposed in the browser bundle, making it accessible to anyone who inspects the production JavaScript. Attackers can extract this key and perform unauthorized API calls to create charges, refunds, or access customer payment data. This violates PCI DSS requirements and Stripe's security guidelines. The exposed key must be rotated immediately and moved to server-side environment variables.
- **Code Snippet**:
```tsx
'use client';

import { useState } from 'react';

const STRIPE_SECRET = 'sk_live_51MqK2xLkC9X8YhZj2Q1vN3pR4sT6uV8wA9bC2dE3fG4h...';

export default function PaymentForm() {
  const [loading, setLoading] = useState(false);

  const handlePayment = async () => {
    // Using secret key in client code
    const stripe = Stripe(STRIPE_SECRET);
  };
}
```
- **Git Context**: Commit abc123f "Add payment processing to checkout flow" (Frontend Dev, 2025-11-23)

---

### Database Query in Client Component
- **File**: `app/components/UserProfile.tsx:8`
- **Severity**: CRITICAL
- **Confidence**: 100
- **Problem**: Prisma database client imported and used directly in a 'use client' component to query sensitive user data including passwords and credit card information.
- **Why Critical**: Exposes database connection credentials and schema to the browser. Bypasses all server-side authentication and authorization checks, allowing any client to query the database directly. Leaks sensitive PII (passwords, credit cards) to the frontend. This breaks the fundamental security boundary between client and server in Next.js applications. Database queries must only occur in Server Components, API Routes, or Server Actions.
- **Code Snippet**:
```tsx
'use client';

import { prisma } from '@/lib/prisma';
import { useEffect, useState } from 'react';

export default function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const fetchUser = async () => {
      const user = await prisma.user.findUnique({
        where: { id: userId },
        select: { email: true, password: true, creditCard: true, ssn: true }
      });
      setUser(user);
    };
    fetchUser();
  }, [userId]);
}
```
- **Git Context**: Commit def456g "Add user profile component with direct DB access" (Junior Dev, 2025-11-23)

---

## High Issues

### Disabled Content Security Policy
- **File**: `next.config.js:12`
- **Severity**: HIGH
- **Confidence**: 90
- **Problem**: Content Security Policy headers have been disabled by setting the CSP value to an empty string in production configuration.
- **Why Critical**: Removes XSS (Cross-Site Scripting) protection layer. Without CSP, the application becomes vulnerable to script injection attacks where attackers can execute arbitrary JavaScript in user browsers, steal session tokens, or perform actions on behalf of users. The commit message "Temporarily disable CSP" suggests this was meant to be reverted but never was.
- **Code Snippet**:
```javascript
module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: '', // CSP disabled - was "default-src 'self'; script-src 'self'"
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
        ],
      },
    ];
  },
};
```
- **Git Context**: Commit ghi789h "Temporarily disable CSP for third-party widget testing" (Admin, 2025-11-23)

---

## Files Changed

| File | Changes | Status |
|------|---------|--------|
| `app/components/PaymentForm.tsx` | +45 | Added payment form with hardcoded Stripe secret |
| `app/components/UserProfile.tsx` | +32 | Added client component with Prisma queries |
| `next.config.js` | +1/-1 | Disabled Content Security Policy |
| `app/api/users/route.ts` | +12/-3 | Added pagination to user API |
| `lib/utils/validation.ts` | +8 | Added input validation helpers |

## Scan Coverage
- **Next.js files reviewed**: 8
- **.NET C# files reviewed**: 0
- **Total changed lines**: 284
- **False positives filtered**: 5 (Development .env.local, test utilities with mock secrets)
