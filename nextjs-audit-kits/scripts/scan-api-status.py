#!/usr/bin/env python3
"""
Fast scanner for API response status code issues.

This script quickly scans Next.js API routes and Server Actions to detect:
1. Incorrect HTTP status codes (200 OK with error messages)
2. Missing status codes in error responses
3. Console.log statements in production code
4. Responses with error indicators without proper HTTP status

Usage:
    python3 scan-api-status.py [directory]

Output:
    JSON with flagged files and line numbers for LLM validation
"""

import os
import re
import json
import sys
from pathlib import Path
from typing import List, Dict, Any


# Patterns for API route files
API_ROUTE_PATTERNS = [
    r"app/.*?/route\.(ts|tsx|js|jsx)$",  # App Router API routes
    r"pages/api/.*?\.(ts|tsx|js|jsx)$",   # Pages Router API routes
    r".*?/api/.*?\.(ts|tsx|js|jsx)$",     # Generic API files
]

# Patterns for Server Actions
SERVER_ACTION_PATTERNS = [
    r"['\"]use server['\"]",
]

# Error field indicators (what developers hide in JSON)
ERROR_FIELDS = [
    "error", "err", "errors",
    "issue", "issues",
    "problem", "problems",
    "failure", "fail", "failed",
    "exception", "fault", "warning",
    "message", "msg", "messages",  # Suspicious
]

# Boolean failure indicators
FAILURE_FLAGS = [
    r"success\s*:\s*false",
    r"ok\s*:\s*false",
    r"valid\s*:\s*false",
    r"failed\s*:\s*true",
    r"isError\s*:\s*true",
    r"hasError\s*:\s*true",
]

# Status string values (not HTTP status)
STATUS_STRINGS = [
    r"status\s*:\s*['\"]error['\"]",
    r"status\s*:\s*['\"]fail(ed)?['\"]",
    r"status\s*:\s*['\"]invalid['\"]",
]

# Console logging patterns
CONSOLE_PATTERNS = [
    r"console\.log\(",
    r"console\.error\(",
    r"console\.warn\(",
    r"console\.info\(",
    r"console\.debug\(",
    r"console\.trace\(",
    r"console\.dir\(",
    r"console\.table\(",
    r"console\.time\(",
    r"console\.timeEnd\(",
    r"debugger;",
]


def is_api_route_file(filepath: str) -> bool:
    """Check if file is an API route."""
    for pattern in API_ROUTE_PATTERNS:
        if re.search(pattern, filepath):
            return True
    return False


def scan_file(filepath: str) -> Dict[str, Any]:
    """Scan a single file for status code issues."""
    findings = {
        "file": filepath,
        "incorrect_status_codes": [],
        "missing_status_codes": [],
        "console_logging": [],
        "has_responses": False,
        "has_server_action": False,
    }

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        return findings

    for line_num, line in enumerate(lines, start=1):
        line_stripped = line.strip()

        # Check if it's a Server Action
        if re.search(r"['\"]use server['\"]", line_stripped):
            findings["has_server_action"] = True

        # Check for NextResponse.json or Response
        if "NextResponse.json" in line or "new Response" in line or ".json(" in line:
            findings["has_responses"] = True

            # Check for explicit 200 with error fields
            if re.search(r"status\s*:\s*200", line):
                for error_field in ERROR_FIELDS:
                    if error_field in line_stripped.lower():
                        findings["incorrect_status_codes"].append({
                            "line": line_num,
                            "code": line_stripped,
                            "reason": f"200 status with '{error_field}' field",
                            "severity": "HIGH"
                        })
                        break

            # Check for error fields without status code
            has_status = re.search(r"status\s*:\s*[45]\d{2}", line)
            if not has_status:
                for error_field in ERROR_FIELDS:
                    # Look for field in JSON-like structure
                    pattern = rf"[{{,]\s*{error_field}\s*:"
                    if re.search(pattern, line_stripped, re.IGNORECASE):
                        findings["missing_status_codes"].append({
                            "line": line_num,
                            "code": line_stripped,
                            "reason": f"Response with '{error_field}' field but no 4xx/5xx status",
                            "severity": "HIGH"
                        })
                        break

                # Check for boolean failure flags
                for flag_pattern in FAILURE_FLAGS:
                    if re.search(flag_pattern, line_stripped):
                        findings["missing_status_codes"].append({
                            "line": line_num,
                            "code": line_stripped,
                            "reason": f"Failure flag without proper HTTP status",
                            "severity": "HIGH"
                        })
                        break

                # Check for status string values
                for status_str in STATUS_STRINGS:
                    if re.search(status_str, line_stripped):
                        findings["missing_status_codes"].append({
                            "line": line_num,
                            "code": line_stripped,
                            "reason": "String status instead of HTTP status code",
                            "severity": "HIGH"
                        })
                        break

        # Check for console logging
        for console_pattern in CONSOLE_PATTERNS:
            if re.search(console_pattern, line_stripped):
                severity = "LOW" if "debugger" in console_pattern else "MEDIUM"
                findings["console_logging"].append({
                    "line": line_num,
                    "code": line_stripped,
                    "reason": f"Console/debug statement in production code",
                    "severity": severity
                })
                break

    return findings


def scan_directory(directory: str) -> List[Dict[str, Any]]:
    """Scan directory for API files and status code issues."""
    all_findings = []

    # Find all TypeScript/JavaScript files
    for root, dirs, files in os.walk(directory):
        # Skip node_modules, .next, etc.
        dirs[:] = [d for d in dirs if d not in [
            'node_modules', '.next', '.git', 'dist', 'build', 'out'
        ]]

        for file in files:
            if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                filepath = os.path.join(root, file)
                relative_path = os.path.relpath(filepath, directory)

                # Prioritize API routes
                if is_api_route_file(relative_path):
                    findings = scan_file(filepath)
                    if (findings["incorrect_status_codes"] or
                        findings["missing_status_codes"] or
                        findings["console_logging"]):
                        findings["is_api_route"] = True
                        all_findings.append(findings)
                # Also scan files with responses or server actions
                elif "use server" in open(filepath, 'r', encoding='utf-8', errors='ignore').read(1000):
                    findings = scan_file(filepath)
                    if (findings["incorrect_status_codes"] or
                        findings["missing_status_codes"] or
                        findings["console_logging"]):
                        findings["is_api_route"] = False
                        all_findings.append(findings)

    return all_findings


def generate_summary(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary statistics."""
    total_files = len(findings)
    total_status_issues = sum(
        len(f["incorrect_status_codes"]) + len(f["missing_status_codes"])
        for f in findings
    )
    total_console = sum(len(f["console_logging"]) for f in findings)

    severity_count = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for finding in findings:
        for issue in finding["incorrect_status_codes"] + finding["missing_status_codes"]:
            severity_count[issue["severity"]] += 1
        for console in finding["console_logging"]:
            severity_count[console["severity"]] += 1

    return {
        "total_files_flagged": total_files,
        "total_status_code_issues": total_status_issues,
        "total_console_logging": total_console,
        "severity_breakdown": severity_count,
        "total_issues": total_status_issues + total_console,
    }


def main():
    """Main execution."""
    directory = sys.argv[1] if len(sys.argv) > 1 else "."

    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning {directory} for API status code issues...", file=sys.stderr)

    findings = scan_directory(directory)
    summary = generate_summary(findings)

    output = {
        "summary": summary,
        "findings": findings,
    }

    # Output JSON
    print(json.dumps(output, indent=2))

    # Print summary to stderr
    print(f"\n📊 Scan Summary:", file=sys.stderr)
    print(f"  Files flagged: {summary['total_files_flagged']}", file=sys.stderr)
    print(f"  Status code issues: {summary['total_status_code_issues']}", file=sys.stderr)
    print(f"  Console logging: {summary['total_console_logging']}", file=sys.stderr)
    print(f"  Severity: HIGH={summary['severity_breakdown']['HIGH']}, "
          f"MEDIUM={summary['severity_breakdown']['MEDIUM']}, "
          f"LOW={summary['severity_breakdown']['LOW']}", file=sys.stderr)

    if summary['total_issues'] > 0:
        print(f"\n⚠️  Found {summary['total_issues']} issues requiring LLM validation", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"\n✅ No issues found", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
