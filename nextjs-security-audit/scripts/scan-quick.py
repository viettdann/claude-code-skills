#!/usr/bin/env python3
"""
Next.js Quick Security Heuristics Scanner

Purpose:
- Super-fast, pattern-based scan to flag likely security hotspots
- Helps AI Agent and developers jump to relevant files without a full deep analysis

Usage:
  ./scripts/scan-quick.py [directory] [--json]

Exit codes:
  0 - No findings
  1 - Findings present

Notes:
  - Uses ripgrep (rg). Please install ripgrep.
  - Heuristics can be noisy; confirm findings by reading code.
"""

import sys
import os
import json
import subprocess
from pathlib import Path

DEFAULT_EXCLUDES = [
    'node_modules', '.next', 'dist', 'build', '.git', 'coverage'
]

PATTERNS = {
    'SSRF': [
        r"fetch\(.*(req\.query|req\.body|params|searchParams|URLSearchParams)\.(get|\[)",
        r"axios\.(get|post|put|delete)\(.*(req\.query|req\.body|params|searchParams)",
        r"new URL\(.*(req\.query|req\.body|params|searchParams)"
    ],
    'Path Traversal': [
        r"fs\.(readFile|createReadStream|writeFile|unlink|readdir)\(",
        r"path\.(join|resolve)\(",
        r"(multer|busboy|formidable|FormData)"
    ],
    'Open Redirect': [
        r"redirect\(.*(searchParams|get|query|body)",
        r"NextResponse\.redirect\(",
        r"res\.redirect\("
    ],
    'CORS': [
        r"Access-Control-Allow-Origin\s*:\s*\*",
        r"NextResponse\.(json|redirect|rewrite).*headers",
        r"new Response\(.*headers",
        r"cors\("
    ],
    'Security Headers & CSP': [
        r"Content-Security-Policy|X-Frame-Options|X-Content-Type-Options|Referrer-Policy|Strict-Transport-Security|Permissions-Policy",
        r"headers\(\)",
        r"next\.config\.js"
    ],
    'Cookie & Session': [
        r"cookies\(|setCookie|NextResponse\.cookies",
        r"next-auth",
        r"getServerSession|getSession"
    ],
    'Webhook Signature': [
        r"Stripe-Signature|svix|x-hub-signature|x-github-event",
        r"stripe\(",
        r"@stripe/stripe-node|@stripe/stripe-js",
        r"crypto\.createHmac|verifySignature|verifyWebhook"
    ],
    'Env Exposure (Client)': [
        r"process\.env\.NEXT_PUBLIC_.*(KEY|SECRET|TOKEN|PASSWORD)",
        r"'use client'[\s\S]*process\.env\.",
        r"publicRuntimeConfig|serverRuntimeConfig"
    ],
    'Sensitive Logging': [
        r"console\.log\(.*(token|password|secret|api[_-]?key|authorization|cookie|set-cookie|bearer)",
        r"logger\.(info|debug)\(.*(token|secret|password)"
    ],
    'Rate Limiting': [
        r"ratelimit|rateLimit|Upstash|Bottleneck|express-rate-limit",
        r"export async function (POST|PUT|DELETE)"
    ],
    'Privacy-aware Caching': [
        r"fetch\(.*\{[\s\S]*cache:\s*'force-cache'|next:\s*\{[\s\S]*revalidate:",
        r"cookies\(\)|headers\(\)"
    ],
    'next/image domains': [
        r"next/image",
        r"images:\s*\{[\s\S]*domains:"
    ]
}

def run_rg(patterns, target_dir):
    args = [
        'rg', '-n', '--no-ignore', '--hidden',
    ]

    # Exclude directories
    for ex in DEFAULT_EXCLUDES:
        args.extend(['-g', f'!{ex}/**'])

    # Add patterns
    for p in patterns:
        args.extend(['-e', p])

    args.append(target_dir)

    try:
        out = subprocess.run(args, capture_output=True, text=True)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip().split('\n')
        return []
    except FileNotFoundError:
        print('Error: ripgrep (rg) is required')
        sys.exit(2)

def scan(target_dir):
    results = {}
    total = 0
    for name, pats in PATTERNS.items():
        lines = run_rg(pats, target_dir)
        results[name] = lines
        total += len(lines)
    return results, total

def print_text(results):
    found_any = False
    for name, lines in results.items():
        if lines:
            found_any = True
            print(f"[FLAG] {name} ({len(lines)} matches)")
            for l in lines[:50]:  # cap output to avoid noise
                print(f"  {l}")
            if len(lines) > 50:
                print(f"  ... ({len(lines)-50} more)")
            print()
    if not found_any:
        print("✓ No quick-scan findings")
    return 1 if found_any else 0

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Next.js quick security heuristics scanner')
    parser.add_argument('directory', nargs='?', default='.', help='Directory to scan (default: current)')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    args = parser.parse_args()

    results, total = scan(args.directory)

    if args.json:
        print(json.dumps({ 'target': args.directory, 'total_matches': total, 'categories': results }, indent=2))
        sys.exit(0 if total == 0 else 1)
    else:
        exit_code = print_text(results)
        sys.exit(exit_code)

if __name__ == '__main__':
    main()