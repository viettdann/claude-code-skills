#!/usr/bin/env python3
"""
Next.js Performance Scanner

Scans Next.js projects for performance anti-patterns including:
- Bundle size issues
- Missing dynamic imports
- Inefficient rendering
- Image optimization issues
- Caching problems
"""

import os
import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Set

class PerformanceScanner:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.findings: List[Dict] = []
        self.scanned_files: Set[str] = set()

    def scan(self) -> Dict:
        """Run all performance scans"""
        print(f"Scanning {self.root_dir} for performance issues...")

        # Scan TypeScript/JavaScript files
        for ext in ['.tsx', '.ts', '.jsx', '.js']:
            self._scan_files(f"**/*{ext}")

        # Scan configuration files
        self._scan_config_files()

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
        """Scan file content for issues"""
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Bundle size issues
            self._check_large_imports(file_path, line_num, line)
            self._check_missing_dynamic_imports(file_path, line_num, line)

            # Rendering performance
            self._check_inline_functions(file_path, line_num, line)
            self._check_inline_objects(file_path, line_num, line)

            # Image optimization
            self._check_native_img_tags(file_path, line_num, line)
            self._check_image_dimensions(file_path, line_num, line)

            # Caching issues
            self._check_fetch_caching(file_path, line_num, line)

    def _check_large_imports(self, file_path: Path, line_num: int, line: str):
        """Check for large library imports"""
        patterns = [
            (r'import\s+.*\s+from\s+["\']moment["\']', 'moment.js', 'date-fns or dayjs'),
            (r'import\s+.*\s+from\s+["\']lodash["\']', 'lodash', 'specific lodash functions'),
            (r'import\s+\*\s+as\s+\w+\s+from', 'namespace import', 'specific imports'),
        ]

        for pattern, library, suggestion in patterns:
            if re.search(pattern, line):
                self._add_finding(
                    file_path, line_num, line,
                    'Bundle Size: Large Import',
                    f'Importing {library} increases bundle size',
                    f'Use {suggestion} instead',
                    'Medium'
                )

    def _check_missing_dynamic_imports(self, file_path: Path, line_num: int, line: str):
        """Check for heavy components that should be lazy loaded"""
        patterns = [
            'Modal', 'Chart', 'Editor', 'Map', 'Calendar', 'CodeEditor'
        ]

        if 'import' in line and 'dynamic' not in line:
            for pattern in patterns:
                if pattern in line and not re.search(r'next/dynamic', line):
                    self._add_finding(
                        file_path, line_num, line,
                        'Code Splitting: Missing Dynamic Import',
                        f'{pattern} component should be lazy loaded',
                        'Use next/dynamic for heavy components',
                        'Medium'
                    )

    def _check_inline_functions(self, file_path: Path, line_num: int, line: str):
        """Check for inline arrow functions in JSX"""
        if re.search(r'onClick=\{\(\)\s*=>', line) or re.search(r'onChange=\{\(\)\s*=>', line):
            self._add_finding(
                file_path, line_num, line,
                'Rendering: Inline Arrow Function',
                'Inline arrow functions create new references on each render',
                'Use useCallback to memoize event handlers',
                'Low'
            )

    def _check_inline_objects(self, file_path: Path, line_num: int, line: str):
        """Check for inline object literals in JSX"""
        if re.search(r'style=\{\{', line) or re.search(r'className=\{`.*\$\{', line):
            self._add_finding(
                file_path, line_num, line,
                'Rendering: Inline Object',
                'Inline objects create new references on each render',
                'Use useMemo or move object outside component',
                'Low'
            )

    def _check_native_img_tags(self, file_path: Path, line_num: int, line: str):
        """Check for native img tags instead of next/image"""
        if re.search(r'<img\s', line):
            self._add_finding(
                file_path, line_num, line,
                'Image Optimization: Native img Tag',
                'Using native <img> tag misses Next.js optimizations',
                'Use next/image Image component',
                'High'
            )

    def _check_image_dimensions(self, file_path: Path, line_num: int, line: str):
        """Check for images without dimensions"""
        if '<Image' in line:
            if not re.search(r'width=', line) or not re.search(r'height=', line):
                if not re.search(r'fill', line):
                    self._add_finding(
                        file_path, line_num, line,
                        'Image Optimization: Missing Dimensions',
                        'Images without width/height cause layout shift',
                        'Add width and height props or use fill',
                        'Medium'
                    )

    def _check_fetch_caching(self, file_path: Path, line_num: int, line: str):
        """Check for fetch calls without cache configuration"""
        if re.search(r'fetch\([^)]+\)', line):
            if 'cache:' not in line and 'next:' not in line:
                self._add_finding(
                    file_path, line_num, line,
                    'Caching: Missing Cache Configuration',
                    'Fetch without explicit cache option may not behave as expected',
                    'Add cache option or next.revalidate',
                    'Low'
                )

    def _scan_config_files(self):
        """Scan Next.js configuration files"""
        config_path = self.root_dir / 'next.config.js'
        if config_path.exists():
            content = config_path.read_text(encoding='utf-8', errors='ignore')

            # Check for missing SWC minification
            if 'swcMinify' not in content:
                self._add_finding(
                    config_path, 1, '',
                    'Config: Missing SWC Minification',
                    'SWC minification is faster than Terser',
                    'Add swcMinify: true to next.config.js',
                    'Low'
                )

            # Check for image optimization config
            if 'images' not in content or 'formats' not in content:
                self._add_finding(
                    config_path, 1, '',
                    'Config: Missing Image Optimization',
                    'Modern image formats not configured',
                    'Add images.formats: ["image/avif", "image/webp"]',
                    'Medium'
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

    scanner = PerformanceScanner(root_dir)
    results = scanner.scan()

    # Print summary
    print(f"\n{'='*60}")
    print(f"Performance Scan Complete")
    print(f"{'='*60}")
    print(f"Files Scanned: {results['total_files_scanned']}")
    print(f"Issues Found: {results['total_issues']}")
    print(f"\nSeverity Breakdown:")
    for severity, count in results['severity_breakdown'].items():
        if count > 0:
            print(f"  {severity}: {count}")

    # Save to JSON
    output_file = 'performance-scan-results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nDetailed results saved to: {output_file}")

    # Exit with error code if issues found
    sys.exit(1 if results['total_issues'] > 0 else 0)


if __name__ == '__main__':
    main()
