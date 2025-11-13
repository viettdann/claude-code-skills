# Code Review JSON Output

## Overview

The Code Reviewer skill generates JSON output alongside markdown reports. The JSON file contains structured data useful for PR automation and CI/CD integration.

## Generated Files

For each review:
1. **Markdown Report**: `CODE-REVIEW-REPORT-{date}.md` (human-readable)
2. **JSON Output**: `CODE-REVIEW-REPORT-{date}.json` (machine-readable)
3. **YAML Output** (optional): `CODE-REVIEW-REPORT-{date}.yaml`

## JSON Structure

The JSON contains:
- **metadata** - Project info, commit details, timestamps
- **summary** - Overall grade, verdict, issue counts, production readiness flag
- **issues[]** - Array of all issues with file paths and line numbers
- **strengths[]** - Array of best practices identified
- **files[]** - Per-file analysis and status
- **metrics** - Quality scores (security, performance, code quality)

## Key Fields

**For PR automation, the most useful fields are:**

```json
{
  "review": {
    "summary": {
      "productionReady": false,
      "grade": "B+",
      "issueCounts": {
        "critical": 1,
        "high": 2,
        "medium": 3,
        "low": 0
      }
    },
    "issues": [
      {
        "file": "src/api/auth.ts",
        "line": 23,
        "severity": "critical",
        "title": "SQL Injection Vulnerability",
        "description": "...",
        "recommendedFix": "..."
      }
    ]
  }
}
```

## Usage

The JSON can be consumed by your custom tooling for:
- PR comment bots
- CI/CD merge gates
- Code quality dashboards
- Automated reporting

See [SCHEMA.md](../SCHEMA.md) for complete schema documentation.
