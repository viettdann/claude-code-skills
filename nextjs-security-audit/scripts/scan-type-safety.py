#!/usr/bin/env python3
"""
TypeScript Type Safety Scanner
Finds 'any' types, unsafe assertions, and type ignores

Usage: ./scripts/scan-type-safety.py [directory] [--json] [--threshold N]
"""

import re
import sys
from pathlib import Path
from collections import defaultdict
import json

# Color codes
class Colors:
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'

class TypeSafetyScanner:
    def __init__(self, target_dir='.', threshold=10):
        self.target_dir = Path(target_dir)
        self.threshold = threshold
        self.findings = defaultdict(list)
        self.stats = {
            'any_types': 0,
            'non_null_assertions': 0,
            'ts_ignores': 0,
            'ts_expect_errors': 0,
            'files_checked': 0
        }

    def scan(self):
        """Scan all TypeScript files"""
        patterns = [
            ('*.ts', 'typescript'),
            ('*.tsx', 'tsx'),
        ]

        for pattern, file_type in patterns:
            for ts_file in self.target_dir.rglob(pattern):
                # Skip node_modules, dist, etc.
                if any(part in ts_file.parts for part in ['node_modules', '.next', 'dist', 'build']):
                    continue

                self.scan_file(ts_file)

    def scan_file(self, filepath):
        """Scan a single file for type safety issues"""
        try:
            content = filepath.read_text(encoding='utf-8')
        except (UnicodeDecodeError, PermissionError):
            return

        self.stats['files_checked'] += 1
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith('//') or line.strip().startswith('*'):
                continue

            self.check_any_types(filepath, line_num, line)
            self.check_non_null_assertions(filepath, line_num, line)
            self.check_ts_ignores(filepath, line_num, line)

    def check_any_types(self, filepath, line_num, line):
        """Check for 'any' type usage"""
        # Patterns that indicate 'any' type
        patterns = [
            r':\s*any\b',              # : any
            r'as\s+any\b',             # as any
            r'<any>',                  # <any>
            r'Array<any>',             # Array<any>
            r'Promise<any>',           # Promise<any>
            r'\bany\[\]',              # any[]
        ]

        for pattern in patterns:
            if re.search(pattern, line):
                # Skip false positives
                if 'typescript-eslint' in line or 'eslint-disable' in line:
                    continue

                severity = self.get_any_severity(line)
                self.findings['any_types'].append({
                    'file': str(filepath),
                    'line': line_num,
                    'content': line.strip(),
                    'severity': severity
                })
                self.stats['any_types'] += 1
                break

    def get_any_severity(self, line):
        """Determine severity of 'any' usage"""
        # Critical in function signatures
        if re.search(r'(function|=>\s*)\s*.*:\s*any', line):
            return 'critical'
        # High in type definitions
        if re.search(r'(type|interface).*any', line):
            return 'high'
        # Medium otherwise
        return 'medium'

    def check_non_null_assertions(self, filepath, line_num, line):
        """Check for non-null assertions (!)"""
        # Pattern: variable!.property or variable![index]
        pattern = r'\w+!\s*[\.\[]'

        matches = re.finditer(pattern, line)
        for match in matches:
            # Check if there's a null check nearby (same line or previous lines would need more context)
            # For now, just flag all non-null assertions

            self.findings['non_null_assertions'].append({
                'file': str(filepath),
                'line': line_num,
                'content': line.strip(),
                'match': match.group(0),
                'severity': 'medium'
            })
            self.stats['non_null_assertions'] += 1

    def check_ts_ignores(self, filepath, line_num, line):
        """Check for @ts-ignore and @ts-expect-error"""
        if '@ts-ignore' in line:
            self.findings['ts_ignores'].append({
                'file': str(filepath),
                'line': line_num,
                'content': line.strip(),
                'severity': 'medium'
            })
            self.stats['ts_ignores'] += 1

        if '@ts-expect-error' in line:
            self.findings['ts_expect_errors'].append({
                'file': str(filepath),
                'line': line_num,
                'content': line.strip(),
                'severity': 'low'
            })
            self.stats['ts_expect_errors'] += 1

    def report(self, json_output=False):
        """Generate report"""
        if json_output:
            return self.report_json()
        else:
            return self.report_text()

    def report_json(self):
        """Generate JSON report"""
        output = {
            'findings': dict(self.findings),
            'stats': self.stats,
            'summary': {
                'total_issues': sum([
                    self.stats['any_types'],
                    self.stats['non_null_assertions'],
                    self.stats['ts_ignores'],
                ]),
                'threshold_exceeded': self.stats['any_types'] > self.threshold
            }
        }
        print(json.dumps(output, indent=2))

    def report_text(self):
        """Generate text report"""
        print(f"{Colors.BLUE}🔍 TypeScript Type Safety Scan{Colors.NC}")
        print(f"Target: {self.target_dir}")
        print(f"Files checked: {self.stats['files_checked']}")
        print()

        total_issues = 0

        # Report 'any' types
        if self.findings['any_types']:
            any_count = len(self.findings['any_types'])
            print(f"{Colors.YELLOW}'any' Type Usage ({any_count} occurrences):{Colors.NC}")
            # Group by file
            by_file = defaultdict(list)
            for finding in self.findings['any_types']:
                by_file[finding['file']].append(finding)

            for filepath, findings in sorted(by_file.items()):
                print(f"\n  {filepath}")
                for finding in findings[:3]:  # Show first 3 per file
                    severity_color = Colors.RED if finding['severity'] == 'critical' else Colors.YELLOW
                    print(f"    {severity_color}[{finding['severity'].upper()}]{Colors.NC} Line {finding['line']}: {finding['content'][:80]}")
                if len(findings) > 3:
                    print(f"    ... and {len(findings) - 3} more")

            total_issues += len(self.findings['any_types'])
            print()

        # Report non-null assertions
        if self.findings['non_null_assertions']:
            assertion_count = len(self.findings['non_null_assertions'])
            print(f"{Colors.YELLOW}Non-null Assertions ({assertion_count} occurrences):{Colors.NC}")
            # Show top 10
            for finding in self.findings['non_null_assertions'][:10]:
                print(f"  {finding['file']}:{finding['line']}")
                print(f"    {finding['content'][:80]}")
            if len(self.findings['non_null_assertions']) > 10:
                print(f"  ... and {len(self.findings['non_null_assertions']) - 10} more")
            total_issues += len(self.findings['non_null_assertions'])
            print()

        # Report @ts-ignore
        if self.findings['ts_ignores']:
            ignore_count = len(self.findings['ts_ignores'])
            print(f"{Colors.YELLOW}@ts-ignore Usage ({ignore_count} occurrences):{Colors.NC}")
            for finding in self.findings['ts_ignores'][:5]:
                print(f"  {finding['file']}:{finding['line']}")
            if len(self.findings['ts_ignores']) > 5:
                print(f"  ... and {len(self.findings['ts_ignores']) - 5} more")
            total_issues += len(self.findings['ts_ignores'])
            print()

        # Summary
        print("━" * 50)
        print(f"Summary:")
        print(f"  'any' types: {self.stats['any_types']}")
        print(f"  Non-null assertions: {self.stats['non_null_assertions']}")
        print(f"  @ts-ignore: {self.stats['ts_ignores']}")
        print(f"  @ts-expect-error: {self.stats['ts_expect_errors']} (informational)")
        print(f"  Total issues: {total_issues}")
        print()

        # Threshold check
        if self.stats['any_types'] > self.threshold:
            print(f"{Colors.RED}⚠️  'any' type usage ({self.stats['any_types']}) exceeds threshold ({self.threshold}){Colors.NC}")
            print()
            print("Recommendations:")
            print("  1. Replace 'any' with proper types")
            print("  2. Use 'unknown' if type is truly dynamic, then narrow with type guards")
            print("  3. Define proper interfaces for complex objects")
            print()
            print("Example fix:")
            print(f"  {Colors.RED}❌ function process(data: any) {{ ... }}{Colors.NC}")
            print(f"  {Colors.GREEN}✅ function process(data: UserData) {{ ... }}{Colors.NC}")
            return 1

        if total_issues == 0:
            print(f"{Colors.GREEN}✓ No type safety issues found{Colors.NC}")
            return 0

        print(f"{Colors.YELLOW}ℹ️  Found {total_issues} type safety issues{Colors.NC}")
        return 0


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Scan TypeScript files for type safety issues')
    parser.add_argument('directory', nargs='?', default='.', help='Directory to scan (default: current)')
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    parser.add_argument('--threshold', type=int, default=10, help='Max allowed any types (default: 10)')

    args = parser.parse_args()

    scanner = TypeSafetyScanner(args.directory, args.threshold)
    scanner.scan()
    exit_code = scanner.report(args.json)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
