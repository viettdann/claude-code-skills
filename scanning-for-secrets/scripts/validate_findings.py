#!/usr/bin/env python3
"""
Secret Scanner - Findings Validator
Validates scanner findings to reduce false positives.
Uses entropy analysis, placeholder detection, and context awareness.
"""

import re
import sys
import json
import math
from pathlib import Path
from typing import List, Dict, Optional
import base64

# Placeholder terms that indicate example/fake values
PLACEHOLDER_TERMS = [
    "example", "sample", "test", "demo", "placeholder", "changeme",
    "your_", "my_", "xxx", "todo", "replace", "insert", "enter",
    "fake", "dummy", "mock", "default", "temp", "temporary",
    "12345", "abcde", "secret", "password", "token", "key",
    "asdf", "qwerty", "admin", "root",
]

# Format placeholder patterns
FORMAT_PLACEHOLDERS = [
    r"<[A-Z_]+>",                    # <YOUR_API_KEY>
    r"\{[A-Z_]+\}",                  # {API_KEY}
    r"\$\{[A-Z_]+\}",                # ${API_KEY}
    r"\[[A-Z_]+\]",                  # [API_KEY]
    r"\.\.\.+",                      # ...
    r"\*\*\*+",                      # ***
    r"xxx+",                         # xxx
    r"000+",                         # 000
    r"123456+",                      # 123456
    r"abc+def+",                     # abcdef
]

# Known example values from official documentation
KNOWN_EXAMPLES = [
    "AKIAIOSFODNN7EXAMPLE",                      # AWS docs
    "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",  # AWS secret key
    "sk_test_4eC39HqLyjWDarjtT1zdp7dc",         # Stripe test
    "AIzaSyDaGmWKa4JsXZ-HjGw7ISLn_3namBGewQe",  # Google (docs)
    "your-secret-key-here",
    "your-api-key-here",
    "change-this-to-your-secret",
]

# File patterns that typically contain examples
EXAMPLE_FILE_PATTERNS = [
    r"\.example$",
    r"\.sample$",
    r"\.template$",
    r"\.dist$",
    r"README",
    r"EXAMPLE",
    r"SAMPLE",
    r"TEMPLATE",
    r"__mocks__",
    r"fixtures",
    r"\.test\.",
    r"\.spec\.",
]


def calculate_entropy(data: str) -> float:
    """Calculate Shannon entropy of a string."""
    if not data:
        return 0

    entropy = 0
    for x in range(256):
        p_x = data.count(chr(x)) / len(data)
        if p_x > 0:
            entropy += - p_x * math.log2(p_x)

    return entropy


def contains_placeholder_term(value: str) -> bool:
    """Check if value contains placeholder terms."""
    value_lower = value.lower()
    for term in PLACEHOLDER_TERMS:
        if term in value_lower:
            return True
    return False


def matches_placeholder_format(value: str) -> bool:
    """Check if value matches placeholder format patterns."""
    for pattern_str in FORMAT_PLACEHOLDERS:
        if re.search(pattern_str, value, re.IGNORECASE):
            return True
    return False


def is_known_example(value: str) -> bool:
    """Check if value is a known example from documentation."""
    return value in KNOWN_EXAMPLES


def is_example_file(file_path: str) -> bool:
    """Check if file is an example/template file."""
    for pattern_str in EXAMPLE_FILE_PATTERNS:
        if re.search(pattern_str, file_path, re.IGNORECASE):
            return True
    return False


def is_test_file(file_path: str) -> bool:
    """Check if file is a test file."""
    test_patterns = [r"\.test\.", r"\.spec\.", r"/tests?/", r"/__tests__/", r"\.test$"]
    for pattern_str in test_patterns:
        if re.search(pattern_str, file_path, re.IGNORECASE):
            return True
    return False


def is_commented_out(line_content: str) -> bool:
    """Check if finding is in a comment."""
    stripped = line_content.strip()
    comment_patterns = [
        r"^\s*//",      # JavaScript/C# single-line
        r"^\s*/\*",     # Multi-line comment start
        r"^\s*\*",      # Multi-line comment continuation
        r"^\s*#",       # Python/Shell/YAML
        r"^\s*<!--",    # HTML/XML
    ]
    for pattern in comment_patterns:
        if re.match(pattern, stripped):
            return True
    return False


def has_high_entropy(value: str, threshold: float = 4.5) -> bool:
    """Check if value has high entropy (likely random)."""
    entropy = calculate_entropy(value)
    return entropy >= threshold


def is_likely_base64(value: str) -> bool:
    """Check if value is likely base64 encoded."""
    # Base64 pattern: alphanumeric + / + = padding
    if re.match(r'^[A-Za-z0-9+/]+=*$', value) and len(value) >= 16:
        try:
            base64.b64decode(value)
            return True
        except Exception:
            pass
    return False


def is_uuid_format(value: str) -> bool:
    """Check if value is in UUID format."""
    uuid_pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    return bool(re.match(uuid_pattern, value))


def validate_finding(finding: Dict) -> Dict:
    """Validate a single finding and assign confidence/updated severity."""
    value = finding["matched_value"]
    file_path = finding["file"]
    line_content = finding.get("line_content", "")
    original_severity = finding["severity"]

    # Validation flags
    is_placeholder = False
    is_example = False
    is_in_comment = False
    is_test = False
    high_entropy = False
    confidence = "HIGH"  # Default confidence
    updated_severity = original_severity

    # Check various indicators
    if contains_placeholder_term(value):
        is_placeholder = True
        confidence = "LOW"
        updated_severity = "INFO"

    if matches_placeholder_format(value):
        is_placeholder = True
        confidence = "LOW"
        updated_severity = "INFO"

    if is_known_example(value):
        is_example = True
        confidence = "LOW"
        updated_severity = "INFO"

    if is_example_file(file_path):
        is_example = True
        confidence = "LOW"
        updated_severity = "INFO"

    if is_test_file(file_path):
        is_test = True
        # Don't automatically downgrade test files, but note it
        if confidence == "HIGH":
            confidence = "MEDIUM"

    if is_commented_out(line_content):
        is_in_comment = True
        # Comments are medium risk (might indicate real secret nearby)
        if updated_severity in ["CRITICAL", "HIGH"]:
            updated_severity = "MEDIUM"
        confidence = "MEDIUM"

    # Entropy check (high entropy = likely real secret)
    if has_high_entropy(value):
        high_entropy = True
        # If high entropy and not obviously placeholder, likely real
        if not (is_placeholder or is_example):
            confidence = "HIGH"
    else:
        # Low entropy = likely placeholder
        if not (is_placeholder or is_example):
            confidence = "MEDIUM"

    # Special checks for specific patterns
    if is_likely_base64(value) or is_uuid_format(value):
        # These formats often indicate real secrets
        if not (is_placeholder or is_example):
            confidence = "HIGH"

    # Very short values (< 8 chars) are likely placeholders
    if len(value) < 8:
        confidence = "LOW"
        updated_severity = "INFO"

    # Create validation result
    validation = {
        "original_severity": original_severity,
        "updated_severity": updated_severity,
        "confidence": confidence,
        "is_placeholder": is_placeholder,
        "is_example": is_example,
        "is_test": is_test,
        "is_in_comment": is_in_comment,
        "high_entropy": high_entropy,
        "entropy": round(calculate_entropy(value), 2),
        "value_length": len(value),
    }

    # Add validation to finding
    finding["validation"] = validation
    finding["severity"] = updated_severity  # Update severity
    finding["confidence"] = confidence

    return finding


def validate_findings(findings: List[Dict]) -> List[Dict]:
    """Validate all findings."""
    validated = []

    for finding in findings:
        validated_finding = validate_finding(finding)
        validated.append(validated_finding)

    return validated


def categorize_findings(findings: List[Dict]) -> Dict:
    """Categorize findings by severity and confidence."""
    categorized = {
        "critical": [],
        "high": [],
        "medium": [],
        "low": [],
        "info": [],
    }

    for finding in findings:
        severity = finding["severity"].lower()
        if severity in categorized:
            categorized[severity].append(finding)

    return categorized


def generate_report(findings: List[Dict], output_format: str = "markdown") -> str:
    """Generate human-readable report."""
    categorized = categorize_findings(findings)

    if output_format == "markdown":
        lines = []
        lines.append("# Secret Scanner Validation Report\n")

        # Summary
        total = len(findings)
        critical = len(categorized["critical"])
        high = len(categorized["high"])
        medium = len(categorized["medium"])
        low = len(categorized["low"])
        info = len(categorized["info"])

        lines.append("## Summary\n")
        lines.append(f"- **Total findings:** {total}")
        lines.append(f"- **Critical:** {critical} (require immediate action)")
        lines.append(f"- **High:** {high} (require action)")
        lines.append(f"- **Medium:** {medium} (review recommended)")
        lines.append(f"- **Low:** {low} (low priority)")
        lines.append(f"- **Info:** {info} (likely false positives)\n")

        # Critical findings
        if categorized["critical"]:
            lines.append("## 🚨 Critical Findings\n")
            for finding in categorized["critical"]:
                lines.append(f"### {finding['file']}:{finding['line']}")
                lines.append(f"- **Pattern:** {finding['pattern_name']}")
                lines.append(f"- **Confidence:** {finding['confidence']}")
                lines.append(f"- **Value:** `{finding['matched_value'][:50]}...`")
                lines.append(f"- **Context:** `{finding['line_content'][:100]}`")
                val = finding['validation']
                lines.append(f"- **Entropy:** {val['entropy']} (High entropy: {val['high_entropy']})")
                lines.append("")

        # High findings
        if categorized["high"]:
            lines.append("## ⚠️  High Severity Findings\n")
            for finding in categorized["high"]:
                lines.append(f"### {finding['file']}:{finding['line']}")
                lines.append(f"- **Pattern:** {finding['pattern_name']}")
                lines.append(f"- **Confidence:** {finding['confidence']}")
                lines.append(f"- **Value:** `{finding['matched_value'][:50]}...`")
                lines.append("")

        # Recommendations
        lines.append("## Recommendations\n")
        if critical > 0:
            lines.append("### Immediate Actions Required")
            lines.append("1. Rotate all critical credentials immediately")
            lines.append("2. Remove secrets from codebase")
            lines.append("3. Add files to `.gitignore`")
            lines.append("4. Check git history for exposure")
            lines.append("")

        return "\n".join(lines)

    return ""


def main():
    """Main validation function."""
    # Read input file
    if len(sys.argv) < 2:
        print("Usage: python3 validate_findings.py <scan-results.json>", file=sys.stderr)
        sys.exit(1)

    input_file = Path(sys.argv[1])

    if not input_file.exists():
        print(f"❌ Error: File {input_file} does not exist", file=sys.stderr)
        print("Run scan_files.py first to generate findings", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 Validating findings from {input_file}...", file=sys.stderr)

    # Load findings
    with open(input_file, 'r') as f:
        scan_data = json.load(f)

    findings = scan_data.get("findings", [])

    if not findings:
        print("✅ No findings to validate", file=sys.stderr)
        sys.exit(0)

    print(f"📊 Validating {len(findings)} findings...", file=sys.stderr)

    # Validate
    validated_findings = validate_findings(findings)

    # Categorize
    categorized = categorize_findings(validated_findings)

    # Update scan data
    scan_data["findings"] = validated_findings
    scan_data["categorized"] = categorized

    # Summary
    summary = {
        "total": len(validated_findings),
        "critical": len(categorized["critical"]),
        "high": len(categorized["high"]),
        "medium": len(categorized["medium"]),
        "low": len(categorized["low"]),
        "info": len(categorized["info"]),
    }
    scan_data["validation_summary"] = summary

    # Write validated results
    output_file = input_file.parent / "validated-findings.json"
    with open(output_file, 'w') as f:
        json.dump(scan_data, f, indent=2)

    # Generate markdown report
    report = generate_report(validated_findings)
    report_file = input_file.parent / "secret-scan-report.md"
    with open(report_file, 'w') as f:
        f.write(report)

    # Print summary
    print(f"\n✅ Validation complete!", file=sys.stderr)
    print(f"📄 Validated results: {output_file}", file=sys.stderr)
    print(f"📄 Report: {report_file}", file=sys.stderr)
    print(f"\n📊 Summary:", file=sys.stderr)
    print(f"   Total findings: {summary['total']}", file=sys.stderr)
    print(f"   Critical: {summary['critical']}", file=sys.stderr)
    print(f"   High: {summary['high']}", file=sys.stderr)
    print(f"   Medium: {summary['medium']}", file=sys.stderr)
    print(f"   Low: {summary['low']}", file=sys.stderr)
    print(f"   Info (likely false positives): {summary['info']}", file=sys.stderr)

    # Exit with error if critical findings
    if summary['critical'] > 0:
        print(f"\n⚠️  {summary['critical']} CRITICAL findings require immediate action!", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
