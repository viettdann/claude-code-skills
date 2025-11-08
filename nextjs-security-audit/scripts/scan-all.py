#!/usr/bin/env python3
"""
Security Scanner Orchestrator
Runs all security scans and aggregates results

Usage: ./scripts/scan-all.py [directory] [--json] [--critical-only]
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

# Colors
class Colors:
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    BOLD = '\033[1m'
    NC = '\033[0m'


class SecurityScanner:
    def __init__(self, target_dir='.', critical_only=False, json_output=False):
        self.target_dir = target_dir
        self.critical_only = critical_only
        self.json_output = json_output
        self.script_dir = Path(__file__).parent
        self.results = {}
        self.summary = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'total_issues': 0,
            'scans_run': 0,
            'scans_failed': 0
        }

    def run_scan(self, name, script_path, *args):
        """Run a single scan script"""
        print(f"{Colors.BLUE}▶ Running {name}...{Colors.NC}", file=sys.stderr)

        try:
            result = subprocess.run(
                [script_path, self.target_dir, *args],
                capture_output=True,
                text=True,
                timeout=60
            )

            self.results[name] = {
                'exitcode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }

            self.summary['scans_run'] += 1

            # Parse output for severity
            if result.returncode != 0:
                if 'CRITICAL' in result.stdout or 'Critical' in result.stdout:
                    self.summary['critical'] += 1
                if 'HIGH' in result.stdout or 'High' in result.stdout:
                    self.summary['high'] += 1
                self.summary['total_issues'] += 1

            return True

        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}✗ {name} timed out{Colors.NC}", file=sys.stderr)
            self.summary['scans_failed'] += 1
            return False
        except FileNotFoundError:
            print(f"{Colors.RED}✗ {name} script not found: {script_path}{Colors.NC}", file=sys.stderr)
            self.summary['scans_failed'] += 1
            return False
        except Exception as e:
            print(f"{Colors.RED}✗ {name} failed: {e}{Colors.NC}", file=sys.stderr)
            self.summary['scans_failed'] += 1
            return False

    def run_all_scans(self):
        """Execute all security scans"""
        scans = [
            ('Secrets Scanner', 'scan-secrets.sh'),
            ('Server Actions', 'scan-server-actions.sh'),
            ('Type Safety', 'scan-type-safety.py'),
        ]

        print(f"{Colors.BOLD}🔒 Security Scan Suite{Colors.NC}")
        print(f"Target: {self.target_dir}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print()

        for name, script in scans:
            script_path = self.script_dir / script

            # Make sure script is executable
            if script_path.exists():
                script_path.chmod(0o755)

            self.run_scan(name, str(script_path))
            print(file=sys.stderr)  # Blank line between scans

    def report(self):
        """Generate final report"""
        if self.json_output:
            self.report_json()
        else:
            self.report_text()

    def report_json(self):
        """Output JSON report"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'target': self.target_dir,
            'summary': self.summary,
            'scans': self.results
        }
        print(json.dumps(output, indent=2))

    def report_text(self):
        """Output text report"""
        print()
        print("=" * 60)
        print(f"{Colors.BOLD}📊 SCAN RESULTS{Colors.NC}")
        print("=" * 60)
        print()

        # Show each scan result
        for name, result in self.results.items():
            if result['success']:
                print(f"{Colors.GREEN}✓{Colors.NC} {name}: PASSED")
            else:
                print(f"{Colors.RED}✗{Colors.NC} {name}: ISSUES FOUND")

                # Show output if failed
                if result['stdout']:
                    print()
                    print(result['stdout'])
                    print()

        # Summary
        print()
        print("=" * 60)
        print(f"{Colors.BOLD}SUMMARY{Colors.NC}")
        print("=" * 60)
        print(f"Scans run: {self.summary['scans_run']}")
        print(f"Scans failed: {self.summary['scans_failed']}")
        print()

        if self.summary['critical'] > 0:
            print(f"{Colors.RED}Critical issues: {self.summary['critical']}{Colors.NC}")
        if self.summary['high'] > 0:
            print(f"{Colors.YELLOW}High severity: {self.summary['high']}{Colors.NC}")

        print()

        # Overall status
        if self.summary['critical'] > 0:
            print(f"{Colors.RED}⚠️  CRITICAL ISSUES FOUND - IMMEDIATE ACTION REQUIRED{Colors.NC}")
            print()
            print("Next steps:")
            print("  1. Review critical findings above")
            print("  2. Remove hardcoded secrets")
            print("  3. Fix SQL injection vulnerabilities")
            print("  4. Add authentication to Server Actions")
            return 1
        elif self.summary['total_issues'] > 0:
            print(f"{Colors.YELLOW}⚠️  Security issues found - review and fix{Colors.NC}")
            return 1
        else:
            print(f"{Colors.GREEN}✓ All scans passed - no critical issues detected{Colors.NC}")
            return 0


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Run comprehensive security scans')
    parser.add_argument('directory', nargs='?', default='.', help='Directory to scan (default: current)')
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    parser.add_argument('--critical-only', action='store_true', help='Only run critical scans')

    args = parser.parse_args()

    scanner = SecurityScanner(
        target_dir=args.directory,
        critical_only=args.critical_only,
        json_output=args.json
    )

    scanner.run_all_scans()
    exit_code = scanner.report()

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
