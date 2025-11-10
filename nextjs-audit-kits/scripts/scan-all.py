#!/usr/bin/env python3
"""
Next.js Comprehensive Scanner

Runs all Next.js scans (performance, security, debug) and generates a combined report.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List

def run_scanner(script_name: str, root_dir: str, execution_dir: str) -> Dict:
    """Run a scanner script and return results"""
    script_path = Path(__file__).parent / script_name

    print(f"\n{'='*60}")
    print(f"Running {script_name}...")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            [sys.executable, str(script_path), root_dir],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            cwd=execution_dir  # Ensure subprocess runs in execution directory
        )

        # Print output
        print(result.stdout)

        # Load JSON results from execution directory
        output_file = os.path.join(execution_dir, script_name.replace('.py', '-results.json'))
        with open(output_file, 'r') as f:
            return json.load(f)

    except subprocess.TimeoutExpired:
        print(f"ERROR: {script_name} timed out")
        return None
    except FileNotFoundError:
        print(f"ERROR: {script_name} output file not found")
        return None
    except json.JSONDecodeError:
        print(f"ERROR: {script_name} produced invalid JSON")
        return None
    except Exception as e:
        print(f"ERROR: {script_name} failed: {e}")
        return None


def generate_combined_report(results: Dict[str, Dict]) -> Dict:
    """Generate combined report from all scanner results"""
    total_files = set()
    all_findings = []
    severity_totals = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
    category_breakdown = {}

    for category, data in results.items():
        if data is None:
            continue

        # Collect files
        total_files.update(data.get('scanned_files', []))

        # Collect findings with category tag
        for finding in data.get('findings', []):
            finding['category'] = category.replace('-scan', '')
            all_findings.append(finding)

        # Sum severity counts
        for severity, count in data.get('severity_breakdown', {}).items():
            severity_totals[severity] += count

        # Category breakdown
        category_breakdown[category.replace('-scan', '')] = data.get('total_issues', 0)

    # Sort findings by severity
    severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
    all_findings.sort(key=lambda x: severity_order.get(x.get('severity', 'Low'), 4))

    return {
        'scan_date': datetime.now().isoformat(),
        'total_files_scanned': len(total_files),
        'total_issues': len(all_findings),
        'severity_breakdown': severity_totals,
        'category_breakdown': category_breakdown,
        'findings': all_findings
    }


def print_summary(report: Dict):
    """Print executive summary"""
    print(f"\n{'='*60}")
    print(f"NEXT.JS COMPREHENSIVE SCAN RESULTS")
    print(f"{'='*60}")
    print(f"Scan Date: {report['scan_date']}")
    print(f"Files Scanned: {report['total_files_scanned']}")
    print(f"Total Issues: {report['total_issues']}")

    print(f"\nSeverity Breakdown:")
    for severity, count in report['severity_breakdown'].items():
        if count > 0:
            print(f"  {severity}: {count}")

    print(f"\nCategory Breakdown:")
    for category, count in report['category_breakdown'].items():
        if count > 0:
            print(f"  {category.title()}: {count}")

    # Show top critical issues
    critical_findings = [f for f in report['findings'] if f['severity'] == 'Critical']
    if critical_findings:
        print(f"\n{'='*60}")
        print(f"CRITICAL ISSUES ({len(critical_findings)})")
        print(f"{'='*60}")
        for i, finding in enumerate(critical_findings[:5], 1):
            print(f"\n{i}. {finding['title']}")
            print(f"   File: {finding['file']}:{finding['line']}")
            print(f"   Problem: {finding['problem']}")
            print(f"   Fix: {finding['fix']}")

        if len(critical_findings) > 5:
            print(f"\n... and {len(critical_findings) - 5} more critical issues")


def generate_markdown_report(report: Dict, output_file: str):
    """Generate markdown report"""
    with open(output_file, 'w') as f:
        f.write("# Next.js Comprehensive Scan Report\n\n")
        f.write(f"**Scan Date:** {report['scan_date']}\n\n")

        # Executive Summary
        f.write("## Executive Summary\n\n")
        f.write(f"- **Files Scanned:** {report['total_files_scanned']}\n")
        f.write(f"- **Total Issues:** {report['total_issues']}\n\n")

        # Severity Breakdown
        f.write("### Severity Breakdown\n\n")
        for severity, count in report['severity_breakdown'].items():
            if count > 0:
                f.write(f"- **{severity}:** {count}\n")

        # Category Breakdown
        f.write("\n### Category Breakdown\n\n")
        for category, count in report['category_breakdown'].items():
            if count > 0:
                f.write(f"- **{category.title()}:** {count}\n")

        # Detailed Findings
        f.write("\n---\n\n## Detailed Findings\n\n")

        for severity in ['Critical', 'High', 'Medium', 'Low']:
            findings = [f for f in report['findings'] if f['severity'] == severity]

            if findings:
                f.write(f"\n### {severity} Issues ({len(findings)})\n\n")

                for i, finding in enumerate(findings, 1):
                    f.write(f"#### {i}. {finding['title']}\n\n")
                    f.write(f"**Location:** `{finding['file']}:{finding['line']}`\n\n")
                    f.write(f"**Category:** {finding['category'].title()}\n\n")
                    f.write(f"**Problem:** {finding['problem']}\n\n")
                    f.write(f"**Fix:** {finding['fix']}\n\n")

                    if finding.get('code'):
                        f.write("**Code:**\n")
                        f.write(f"```typescript\n{finding['code']}\n```\n\n")

                    f.write("---\n\n")


def main():
    """Main execution"""
    # Capture the original working directory where command was executed
    execution_dir = os.getcwd()
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    print(f"\n{'='*60}")
    print(f"NEXT.JS COMPREHENSIVE SCANNER")
    print(f"{'='*60}")
    print(f"Scanning: {root_dir}")

    # Run all scanners
    scanners = [
        'scan-performance.py',
        'scan-security.py',
        'scan-debug.py',
        'scan-api-status.py'
    ]

    results = {}
    for scanner in scanners:
        result = run_scanner(scanner, root_dir, execution_dir)
        results[scanner.replace('.py', '')] = result

    # Generate combined report
    combined_report = generate_combined_report(results)

    # Print summary
    print_summary(combined_report)

    # Save JSON report in the execution directory
    json_output = os.path.join(execution_dir, 'nextjs-audit-report.json')
    with open(json_output, 'w') as f:
        json.dump(combined_report, f, indent=2)

    print(f"\n{'='*60}")
    print(f"JSON report saved to: {json_output}")

    # Generate markdown report in the execution directory
    md_output = os.path.join(execution_dir, 'nextjs-audit-report.md')
    generate_markdown_report(combined_report, md_output)
    print(f"Markdown report saved to: {md_output}")
    print(f"{'='*60}\n")

    # Exit with error code if critical issues found
    critical_count = combined_report['severity_breakdown']['Critical']
    sys.exit(1 if critical_count > 0 else 0)


if __name__ == '__main__':
    main()
