#!/usr/bin/env python3
"""
Next.js Debug Scanner

Scans Next.js projects for common debugging issues including:
- Hydration errors
- TypeScript issues
- Build errors
- Runtime error patterns
"""

import os
import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Set

class DebugScanner:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.findings: List[Dict] = []
        self.scanned_files: Set[str] = set()

    def scan(self) -> Dict:
        """Run all debug scans"""
        print(f"Scanning {self.root_dir} for common debug issues...")

        # Scan TypeScript/JavaScript files
        for ext in ['.tsx', '.ts', '.jsx', '.js']:
            self._scan_files(f"**/*{ext}")

        # Scan TypeScript config
        self._scan_tsconfig()

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
        """Scan file content for debug issues"""
        lines = content.split('\n')
        is_client_component = '"use client"' in content or "'use client'" in content

        for line_num, line in enumerate(lines, 1):
            # Hydration error patterns
            self._check_hydration_issues(file_path, line_num, line)

            # TypeScript issues
            self._check_typescript_issues(file_path, line_num, line)

            # Client/Server mismatch
            if not is_client_component:
                self._check_server_component_issues(file_path, line_num, line)

            # Runtime error patterns
            self._check_runtime_errors(file_path, line_num, line)

            # Missing error boundaries
            self._check_error_handling(file_path, line_num, line, content)

    def _check_hydration_issues(self, file_path: Path, line_num: int, line: str):
        """Check for common hydration error causes"""
        patterns = [
            (r'new Date\(\)', 'new Date()',
             'Date objects cause hydration mismatches - use useEffect'),
            (r'Math\.random\(\)', 'Math.random()',
             'Random values cause hydration mismatches - use useEffect'),
            (r'Date\.now\(\)', 'Date.now()',
             'Timestamps cause hydration mismatches - use useEffect'),
            (r'typeof window !== ["\']undefined["\']', 'window check in render',
             'Move to useEffect to avoid hydration mismatch'),
            (r'window &&', 'window check in render',
             'Move to useEffect to avoid hydration mismatch'),
        ]

        for pattern, issue, fix in patterns:
            if re.search(pattern, line):
                self._add_finding(
                    file_path, line_num, line,
                    'Hydration: Client/Server Mismatch',
                    f'{issue} in render can cause hydration errors',
                    fix,
                    'High'
                )

    def _check_typescript_issues(self, file_path: Path, line_num: int, line: str):
        """Check for TypeScript anti-patterns"""
        patterns = [
            (r':\s*any\s*[,;=)]', 'any type',
             'Use specific types instead of any', 'Medium'),
            (r'as\s+any', 'any type assertion',
             'Use proper type definitions', 'Medium'),
            (r'@ts-ignore', '@ts-ignore comment',
             'Fix the underlying type error', 'High'),
            (r'@ts-nocheck', '@ts-nocheck comment',
             'Enable type checking for this file', 'High'),
            (r'!\s*[.;]', 'non-null assertion',
             'Use optional chaining or proper type guards', 'Low'),
        ]

        for pattern, issue, fix, severity in patterns:
            if re.search(pattern, line):
                self._add_finding(
                    file_path, line_num, line,
                    f'TypeScript: {issue.title()}',
                    f'Using {issue} reduces type safety',
                    fix,
                    severity
                )

    def _check_server_component_issues(self, file_path: Path, line_num: int, line: str):
        """Check for issues in Server Components"""
        # Check for client-only hooks in Server Components
        client_hooks = [
            'useState', 'useEffect', 'useContext', 'useReducer',
            'useCallback', 'useMemo', 'useRef', 'useLayoutEffect'
        ]

        for hook in client_hooks:
            if re.search(rf'\b{hook}\s*\(', line):
                self._add_finding(
                    file_path, line_num, line,
                    'Server Component: Client Hook Usage',
                    f'{hook} cannot be used in Server Components',
                    'Add "use client" directive or move to Client Component',
                    'Critical'
                )

        # Check for browser APIs in Server Components
        browser_apis = ['window', 'document', 'localStorage', 'sessionStorage', 'navigator']

        for api in browser_apis:
            if re.search(rf'\b{api}\s*\.', line):
                self._add_finding(
                    file_path, line_num, line,
                    'Server Component: Browser API Usage',
                    f'{api} is not available in Server Components',
                    'Add "use client" directive or use conditional rendering',
                    'High'
                )

    def _check_runtime_errors(self, file_path: Path, line_num: int, line: str):
        """Check for common runtime error patterns"""
        # Check for API routes without error handling
        if 'export async function' in line and 'route.ts' in str(file_path):
            self._check_api_error_handling(file_path, line_num, line)

        # Check for missing null checks
        if re.search(r'\.\w+\(.*\)(?!.*\?\.)', line):
            if 'null' in line or 'undefined' in line:
                self._add_finding(
                    file_path, line_num, line,
                    'Runtime: Potential Null Reference',
                    'Possible null/undefined dereference',
                    'Use optional chaining (?.) or null checks',
                    'Low'
                )

    def _check_api_error_handling(self, file_path: Path, line_num: int, line: str):
        """Check API routes for error handling"""
        # Read context to check for try-catch
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            # Simple check for try-catch in same function
            if 'try' not in content or 'catch' not in content:
                self._add_finding(
                    file_path, line_num, line,
                    'Runtime: Missing Error Handling',
                    'API route without try-catch block',
                    'Wrap async operations in try-catch',
                    'Medium'
                )
        except:
            pass

    def _check_error_handling(self, file_path: Path, line_num: int, line: str, content: str):
        """Check for missing error handling"""
        # Check for fetch without error handling
        if 'fetch(' in line:
            # Simple heuristic: check if there's error handling nearby
            has_error_handling = any(
                keyword in content
                for keyword in ['.catch(', 'try', 'catch', 'error']
            )

            if not has_error_handling:
                self._add_finding(
                    file_path, line_num, line,
                    'Runtime: Missing Fetch Error Handling',
                    'Fetch without error handling',
                    'Add .catch() or try-catch for fetch errors',
                    'Low'
                )

    def _scan_tsconfig(self):
        """Scan TypeScript configuration"""
        tsconfig_path = self.root_dir / 'tsconfig.json'
        if tsconfig_path.exists():
            self.scanned_files.add(str(tsconfig_path))

            try:
                content = tsconfig_path.read_text(encoding='utf-8')

                # Check for strict mode
                if '"strict": false' in content:
                    self._add_finding(
                        tsconfig_path, 1, '',
                        'TypeScript: Strict Mode Disabled',
                        'Strict mode is disabled',
                        'Enable strict mode for better type safety',
                        'Medium'
                    )

                # Check for noImplicitAny
                if '"noImplicitAny": false' in content:
                    self._add_finding(
                        tsconfig_path, 1, '',
                        'TypeScript: noImplicitAny Disabled',
                        'noImplicitAny is disabled',
                        'Enable noImplicitAny to catch missing types',
                        'Medium'
                    )
            except:
                pass

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
    # Capture the original working directory where command was executed
    original_cwd = os.getcwd()
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    scanner = DebugScanner(root_dir)
    results = scanner.scan()

    # Print summary
    print(f"\n{'='*60}")
    print(f"Debug Scan Complete")
    print(f"{'='*60}")
    print(f"Files Scanned: {results['total_files_scanned']}")
    print(f"Issues Found: {results['total_issues']}")
    print(f"\nSeverity Breakdown:")
    for severity, count in results['severity_breakdown'].items():
        if count > 0:
            print(f"  {severity}: {count}")

    # Save to JSON in the execution directory
    output_file = os.path.join(original_cwd, 'debug-scan-results.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nDetailed results saved to: {output_file}")

    # Exit with error code if issues found
    sys.exit(1 if results['total_issues'] > 0 else 0)


if __name__ == '__main__':
    main()
