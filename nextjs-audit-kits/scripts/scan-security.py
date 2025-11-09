#!/usr/bin/env python3
"""
Next.js Security Scanner

Scans Next.js projects for security vulnerabilities including:
- XSS vulnerabilities
- CSRF protection
- Server Actions security
- Environment variable exposure
- API route security
"""

import os
import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Set

class SecurityScanner:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.findings: List[Dict] = []
        self.scanned_files: Set[str] = set()

    def scan(self) -> Dict:
        """Run all security scans"""
        print(f"Scanning {self.root_dir} for security vulnerabilities...")

        # Scan TypeScript/JavaScript files
        for ext in ['.tsx', '.ts', '.jsx', '.js']:
            self._scan_files(f"**/*{ext}")

        # Scan environment files
        self._scan_env_files()

        return {
            'total_files_scanned': len(self.scanned_files),
            'total_issues': len(self.findings),
            'severity_breakdown': self._get_severity_breakdown(),
            'findings': self.findings
        }

    def _scan_files(self, pattern: str):
        """Scan files matching pattern"""
        for file_path in self.root_dir.glob(pattern):
            if self._should_skip(file_path):
                continue

            self.scanned_files.add(str(file_path))
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            self._scan_file_content(file_path, content)

    def _should_skip(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_dirs = {'node_modules', '.next', 'out', 'dist', 'build', '.git'}
        return any(skip_dir in file_path.parts for skip_dir in skip_dirs)

    def _scan_file_content(self, file_path: Path, content: str):
        """Scan file content for security issues"""
        lines = content.split('\n')
        is_client_component = '"use client"' in content or "'use client'" in content
        is_server_action = '"use server"' in content or "'use server'" in content

        for line_num, line in enumerate(lines, 1):
            # XSS vulnerabilities
            self._check_dangerous_html(file_path, line_num, line)
            self._check_unsanitized_input(file_path, line_num, line)

            # Server Actions security
            if is_server_action:
                self._check_server_action_validation(file_path, line_num, line, content)
                self._check_server_action_auth(file_path, line_num, line, content)

            # API route security
            if 'route.ts' in str(file_path) or 'route.js' in str(file_path):
                self._check_api_route_security(file_path, line_num, line, content)

            # Environment variable exposure
            if is_client_component:
                self._check_env_exposure(file_path, line_num, line)

            # SQL injection
            self._check_sql_injection(file_path, line_num, line)

            # Hardcoded secrets
            self._check_hardcoded_secrets(file_path, line_num, line)

    def _check_dangerous_html(self, file_path: Path, line_num: int, line: str):
        """Check for dangerous HTML rendering"""
        patterns = [
            (r'dangerouslySetInnerHTML', 'dangerouslySetInnerHTML'),
            (r'innerHTML\s*=', 'innerHTML'),
            (r'outerHTML\s*=', 'outerHTML'),
        ]

        for pattern, method in patterns:
            if re.search(pattern, line):
                self._add_finding(
                    file_path, line_num, line,
                    'XSS: Dangerous HTML Rendering',
                    f'Using {method} can introduce XSS vulnerabilities',
                    'Sanitize with DOMPurify or use React components',
                    'Critical'
                )

    def _check_unsanitized_input(self, file_path: Path, line_num: int, line: str):
        """Check for unsanitized user input in templates"""
        patterns = [
            r'\$\{.*params\.',
            r'\$\{.*searchParams\.',
            r'\$\{.*formData\.',
            r'\+.*req\.body',
        ]

        for pattern in patterns:
            if re.search(pattern, line):
                self._add_finding(
                    file_path, line_num, line,
                    'XSS: Unsanitized User Input',
                    'Template literal with unsanitized user input',
                    'Validate and sanitize user input before use',
                    'High'
                )

    def _check_server_action_validation(self, file_path: Path, line_num: int,
                                       line: str, content: str):
        """Check Server Actions for input validation"""
        if 'export async function' in line or 'export default async function' in line:
            # Check if function has validation
            has_validation = any(
                keyword in content
                for keyword in ['z.', 'validate', 'parse', 'schema', 'safeParse']
            )

            if not has_validation:
                self._add_finding(
                    file_path, line_num, line,
                    'Server Actions: Missing Input Validation',
                    'Server Action without input validation',
                    'Add validation using Zod or similar library',
                    'Critical'
                )

    def _check_server_action_auth(self, file_path: Path, line_num: int,
                                  line: str, content: str):
        """Check Server Actions for authorization"""
        if 'export async function' in line or 'export default async function' in line:
            # Check if function has auth
            has_auth = any(
                keyword in content
                for keyword in ['auth()', 'session', 'getServerSession', 'currentUser']
            )

            if not has_auth and any(
                keyword in content
                for keyword in ['delete', 'update', 'create', 'mutation']
            ):
                self._add_finding(
                    file_path, line_num, line,
                    'Server Actions: Missing Authorization',
                    'Server Action without authorization check',
                    'Add authentication and authorization checks',
                    'Critical'
                )

    def _check_api_route_security(self, file_path: Path, line_num: int,
                                  line: str, content: str):
        """Check API routes for security issues"""
        # Check for mutation handlers without CSRF protection
        if re.search(r'export async function (POST|PUT|DELETE|PATCH)', line):
            # Check for CSRF token validation
            has_csrf = any(
                keyword in content
                for keyword in ['csrf', 'x-csrf-token', 'verifyToken']
            )

            if not has_csrf:
                self._add_finding(
                    file_path, line_num, line,
                    'CSRF: Missing Protection',
                    'Mutation endpoint without CSRF protection',
                    'Add CSRF token validation',
                    'High'
                )

            # Check for rate limiting
            has_ratelimit = any(
                keyword in content
                for keyword in ['ratelimit', 'throttle', 'limit(']
            )

            if not has_ratelimit:
                self._add_finding(
                    file_path, line_num, line,
                    'API Security: Missing Rate Limiting',
                    'API endpoint without rate limiting',
                    'Add rate limiting to prevent abuse',
                    'Medium'
                )

        # Check for input validation
        if 'await request.json()' in line:
            has_validation = any(
                keyword in content
                for keyword in ['validate', 'parse', 'schema', 'z.']
            )

            if not has_validation:
                self._add_finding(
                    file_path, line_num, line,
                    'API Security: Missing Input Validation',
                    'Request body parsing without validation',
                    'Validate input with Zod or similar',
                    'High'
                )

    def _check_env_exposure(self, file_path: Path, line_num: int, line: str):
        """Check for environment variable exposure in client code"""
        # Check for non-public env vars in client components
        if re.search(r'process\.env\.(?!NEXT_PUBLIC_)', line):
            self._add_finding(
                file_path, line_num, line,
                'Secrets: Environment Variable Exposure',
                'Non-public environment variable used in client component',
                'Use NEXT_PUBLIC_ prefix or move to server component',
                'Critical'
            )

        # Check for secrets in public variables
        if re.search(r'NEXT_PUBLIC_.*(SECRET|PASSWORD|TOKEN|KEY)', line, re.IGNORECASE):
            self._add_finding(
                file_path, line_num, line,
                'Secrets: Secret in Public Variable',
                'Secret stored in public environment variable',
                'Never use NEXT_PUBLIC_ for secrets',
                'Critical'
            )

    def _check_sql_injection(self, file_path: Path, line_num: int, line: str):
        """Check for SQL injection vulnerabilities"""
        patterns = [
            r'query\(.*\$\{.*\}',
            r'execute\(.*\$\{.*\}',
            r'`SELECT.*\$\{',
            r'`INSERT.*\$\{',
            r'`UPDATE.*\$\{',
            r'`DELETE.*\$\{',
        ]

        for pattern in patterns:
            if re.search(pattern, line):
                self._add_finding(
                    file_path, line_num, line,
                    'SQL Injection: Template Literal SQL',
                    'SQL query with template literal interpolation',
                    'Use parameterized queries or ORM',
                    'Critical'
                )

    def _check_hardcoded_secrets(self, file_path: Path, line_num: int, line: str):
        """Check for hardcoded secrets"""
        # Skip if it's a comment or example
        if line.strip().startswith('//') or line.strip().startswith('*'):
            return

        patterns = [
            (r'apiKey\s*=\s*["\'][a-zA-Z0-9_-]{20,}["\']', 'API key'),
            (r'password\s*=\s*["\'][^"\']+["\']', 'password'),
            (r'secret\s*=\s*["\'][a-zA-Z0-9_-]{20,}["\']', 'secret'),
            (r'token\s*=\s*["\'][a-zA-Z0-9_-]{20,}["\']', 'token'),
        ]

        for pattern, secret_type in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                self._add_finding(
                    file_path, line_num, line,
                    f'Secrets: Hardcoded {secret_type.title()}',
                    f'Hardcoded {secret_type} detected',
                    'Move to environment variables',
                    'Critical'
                )

    def _scan_env_files(self):
        """Scan environment files for exposed secrets"""
        for env_file in ['.env', '.env.local', '.env.development', '.env.production']:
            env_path = self.root_dir / env_file
            if env_path.exists():
                self.scanned_files.add(str(env_path))
                content = env_path.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')

                for line_num, line in enumerate(lines, 1):
                    # Check for secrets in public variables
                    if re.search(r'NEXT_PUBLIC_.*(SECRET|PASSWORD|TOKEN|KEY|PRIVATE)', line, re.IGNORECASE):
                        self._add_finding(
                            env_path, line_num, line,
                            'Secrets: Secret in Public Variable',
                            'Secret key stored in NEXT_PUBLIC_ variable',
                            'Remove NEXT_PUBLIC_ prefix for secrets',
                            'Critical'
                        )

    def _add_finding(self, file_path: Path, line_num: int, line: str,
                     title: str, problem: str, fix: str, severity: str):
        """Add a finding to the results"""
        self.findings.append({
            'file': str(file_path.relative_to(self.root_dir)),
            'line': line_num,
            'code': line.strip(),
            'title': title,
            'problem': problem,
            'fix': fix,
            'severity': severity
        })

    def _get_severity_breakdown(self) -> Dict[str, int]:
        """Get count of findings by severity"""
        breakdown = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
        for finding in self.findings:
            breakdown[finding['severity']] += 1
        return breakdown


def main():
    """Main execution"""
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    scanner = SecurityScanner(root_dir)
    results = scanner.scan()

    # Print summary
    print(f"\n{'='*60}")
    print(f"Security Scan Complete")
    print(f"{'='*60}")
    print(f"Files Scanned: {results['total_files_scanned']}")
    print(f"Issues Found: {results['total_issues']}")
    print(f"\nSeverity Breakdown:")
    for severity, count in results['severity_breakdown'].items():
        if count > 0:
            print(f"  {severity}: {count}")

    # Save to JSON
    output_file = 'security-scan-results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nDetailed results saved to: {output_file}")

    # Exit with error code if critical issues found
    critical_count = results['severity_breakdown']['Critical']
    sys.exit(1 if critical_count > 0 else 0)


if __name__ == '__main__':
    main()
