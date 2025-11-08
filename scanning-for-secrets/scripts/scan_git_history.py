#!/usr/bin/env python3
"""
Secret Scanner - Git History Scanner
Scans git commit history for accidentally committed secrets.
Checks environment files and configuration files across all commits.
"""

import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

try:
    import git
except ImportError:
    print("❌ Error: gitpython not installed", file=sys.stderr)
    print("Install with: pip install gitpython", file=sys.stderr)
    sys.exit(1)

# Sensitive file patterns to check in history
SENSITIVE_FILE_PATTERNS = [
    # Environment files
    r"\.env$",
    r"\.env\.local$",
    r"\.env\.production$",
    r"\.env\.development$",
    r"\.env\.staging$",
    r"\.env\..*$",

    # .NET config files
    r"appsettings\.Production\.json$",
    r"appsettings\.Staging\.json$",
    r"appsettings\..*\.json$",
    r"appsettings\.secrets\.json$",
    r"Web\.config$",
    r".*\.pubxml$",

    # Azure specific (handle both .yml and .yaml, various naming)
    r"azure[-_]?pipelines?\.(yml|yaml)$",  # azure-pipelines, azure_pipelines, azure-pipeline
    r"local\.settings\.json$",  # Azure Functions
    r"\.azure/.*\.json$",
    r"azuredeploy\.parameters\.(json|yml|yaml)$",
    r".*\.publishsettings$",

    # Docker specific (handle both .yml and .yaml, all naming variations)
    # Matches: compose.yml, docker-compose.yml, api-compose.yml, etc.
    r"[-_]?compose\.(yml|yaml)$",  # Any file ending in compose.yml/yaml
    r"[-_]?compose\..*\.(yml|yaml)$",  # compose.prod.yml, docker-compose.dev.yaml, api-compose.test.yml
    r"Dockerfile(\..*)?$",  # Dockerfile, Dockerfile.prod, etc.
    r"\.dockerconfigjson$",
    r"\.docker/config\.json$",

    # CI/CD configs (handle both .yml and .yaml)
    r"\.gitlab-ci\.(yml|yaml)$",
    r"\.github/workflows/.*\.(yml|yaml)$",
    r"\.circleci/config\.(yml|yaml)$",
    r"bitbucket-pipelines\.(yml|yaml)$",

    # Credential files
    r"credentials\.json$",
    r"secrets\.json$",
    r"\.npmrc$",
    r"\.pypirc$",

    # Keys
    r".*\.pem$",
    r".*\.key$",
    r".*\.pfx$",
    r".*\.p12$",
    r".*\.cer$",

    # Vercel/Netlify
    r"\.vercel/.*\.json$",
    r"\.netlify/.*\.json$",
]

# Secret patterns (same as scan_files.py but simplified)
SECRET_PATTERNS = [
    # Cloud Providers
    {
        "name": "AWS Access Key",
        "pattern": re.compile(r"AKIA[0-9A-Z]{16}"),
        "severity": "CRITICAL",
    },
    {
        "name": "Azure Storage Connection String",
        "pattern": re.compile(r"DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[A-Za-z0-9+/=]{88};"),
        "severity": "CRITICAL",
    },
    {
        "name": "Azure SQL Connection String",
        "pattern": re.compile(r"Server=tcp:[^;]+\.database\.windows\.net[^;]*;.*Password=([^;\"']+)", re.IGNORECASE),
        "severity": "CRITICAL",
    },
    {
        "name": "Azure Service Principal Secret",
        "pattern": re.compile(r"(?:AZURE_CLIENT_SECRET|ClientSecret)['\"\s:=]+[A-Za-z0-9~._-]{34,40}", re.IGNORECASE),
        "severity": "CRITICAL",
    },
    {
        "name": "Azure DevOps PAT",
        "pattern": re.compile(r"(?:AZURE_DEVOPS_PAT|ADO_PAT)['\"\s:=]+[A-Za-z0-9]{52}", re.IGNORECASE),
        "severity": "CRITICAL",
    },
    {
        "name": "Azure Container Registry Password",
        "pattern": re.compile(r"(?:ACR_PASSWORD|acrPassword)['\"\s:=]+[A-Za-z0-9+/=]{43,}", re.IGNORECASE),
        "severity": "CRITICAL",
    },

    # Docker
    {
        "name": "Docker Hub Token",
        "pattern": re.compile(r"(?:DOCKER_HUB_TOKEN|DOCKERHUB_TOKEN)['\"\s:=]+[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", re.IGNORECASE),
        "severity": "CRITICAL",
    },
    {
        "name": "Docker Registry Password",
        "pattern": re.compile(r"(?:DOCKER_PASSWORD|REGISTRY_PASSWORD)['\"\s:=]+[^\s\"']{8,}", re.IGNORECASE),
        "severity": "CRITICAL",
    },

    # Generic
    {
        "name": "Private Key",
        "pattern": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        "severity": "CRITICAL",
    },
    {
        "name": "Generic API Key",
        "pattern": re.compile(r"(?:api[_-]?key|apikey)['\"\s:=]+([A-Za-z0-9_-]{20,})", re.IGNORECASE),
        "severity": "HIGH",
    },
    {
        "name": "Database URL with Password",
        "pattern": re.compile(r"(?:postgres|mysql|mongodb)://[a-zA-Z0-9_-]+:([^@\s]+)@"),
        "severity": "CRITICAL",
    },
    {
        "name": "JWT Token",
        "pattern": re.compile(r"eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+"),
        "severity": "HIGH",
    },
    {
        "name": "GitHub Token",
        "pattern": re.compile(r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}"),
        "severity": "CRITICAL",
    },
    {
        "name": "Stripe API Key",
        "pattern": re.compile(r"(?:sk|pk)_(?:live|test)_[0-9a-zA-Z]{24,}"),
        "severity": "CRITICAL",
    },
    {
        "name": "SQL Server Connection String",
        "pattern": re.compile(r"(?:Server|Data Source)=[^;]+;.*Password=([^;\"']+)", re.IGNORECASE),
        "severity": "CRITICAL",
    },
    {
        "name": "Password Variable",
        "pattern": re.compile(r'(?:password|passwd|pwd)["\s:=]+["\']?([^"\'\s]{8,})["\']?', re.IGNORECASE),
        "severity": "HIGH",
    },
]


def is_sensitive_file(file_path: str) -> bool:
    """Check if file path matches sensitive file patterns."""
    for pattern_str in SENSITIVE_FILE_PATTERNS:
        if re.search(pattern_str, file_path, re.IGNORECASE):
            return True
    return False


def scan_content_for_secrets(content: str, file_path: str) -> List[Dict]:
    """Scan file content for secret patterns."""
    findings = []
    lines = content.split('\n')

    for line_num, line in enumerate(lines, start=1):
        for pattern_def in SECRET_PATTERNS:
            matches = pattern_def["pattern"].finditer(line)
            for match in matches:
                matched_value = match.group(0)
                if match.groups():
                    matched_value = match.group(1) if len(match.groups()) >= 1 else matched_value

                finding = {
                    "pattern_name": pattern_def["name"],
                    "severity": pattern_def["severity"],
                    "matched_value": matched_value[:100],
                    "line": line_num,
                    "line_content": line.strip()[:200],
                }
                findings.append(finding)

    return findings


def scan_commit(repo: git.Repo, commit: git.Commit, file_path: str) -> Optional[Dict]:
    """Scan a specific file in a commit for secrets."""
    try:
        # Get file content at this commit
        file_content = (commit.tree / file_path).data_stream.read().decode('utf-8', errors='ignore')

        # Scan for secrets
        secrets = scan_content_for_secrets(file_content, file_path)

        if secrets:
            return {
                "commit_hash": commit.hexsha[:8],
                "commit_hash_full": commit.hexsha,
                "author": str(commit.author),
                "date": datetime.fromtimestamp(commit.committed_date).isoformat(),
                "message": commit.message.strip(),
                "file": file_path,
                "secrets": secrets,
            }

    except Exception as e:
        # File might not exist in this commit or other errors
        pass

    return None


def get_sensitive_files_from_history(repo: git.Repo) -> List[str]:
    """Get list of all sensitive files ever committed."""
    sensitive_files = set()

    try:
        # Get all files from all commits
        for commit in repo.iter_commits('--all'):
            for item in commit.tree.traverse():
                if item.type == 'blob':  # It's a file
                    if is_sensitive_file(item.path):
                        sensitive_files.add(item.path)

    except Exception as e:
        print(f"⚠️  Warning: Error traversing commits: {e}", file=sys.stderr)

    return list(sensitive_files)


def scan_git_history(repo_path: Path) -> List[Dict]:
    """Scan git history for secrets in sensitive files."""
    try:
        repo = git.Repo(repo_path)
    except git.InvalidGitRepositoryError:
        print(f"❌ Error: {repo_path} is not a git repository", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 Scanning git history for secrets...", file=sys.stderr)

    # Find all sensitive files ever committed
    print(f"📂 Finding sensitive files in history...", file=sys.stderr)
    sensitive_files = get_sensitive_files_from_history(repo)

    if not sensitive_files:
        print(f"✅ No sensitive files found in git history", file=sys.stderr)
        return []

    print(f"📄 Found {len(sensitive_files)} sensitive files in history:", file=sys.stderr)
    for f in sensitive_files[:10]:  # Show first 10
        print(f"   - {f}", file=sys.stderr)
    if len(sensitive_files) > 10:
        print(f"   ... and {len(sensitive_files) - 10} more", file=sys.stderr)

    # Scan each sensitive file across all commits
    all_findings = []
    scanned_commits = 0

    for file_path in sensitive_files:
        print(f"🔎 Scanning history of {file_path}...", file=sys.stderr)

        # Get all commits that modified this file
        try:
            commits = list(repo.iter_commits('--all', paths=file_path))

            for commit in commits:
                scanned_commits += 1
                finding = scan_commit(repo, commit, file_path)
                if finding:
                    all_findings.append(finding)

        except Exception as e:
            print(f"⚠️  Warning: Error scanning {file_path}: {e}", file=sys.stderr)

    print(f"📊 Scanned {scanned_commits} commits", file=sys.stderr)

    return all_findings


def generate_summary(findings: List[Dict]) -> Dict:
    """Generate summary statistics."""
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    files_with_secrets = set()
    commits_with_secrets = set()

    for finding in findings:
        files_with_secrets.add(finding["file"])
        commits_with_secrets.add(finding["commit_hash_full"])

        for secret in finding["secrets"]:
            severity = secret["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

    return {
        "total_findings": len(findings),
        "total_secrets": sum(len(f["secrets"]) for f in findings),
        "files_affected": len(files_with_secrets),
        "commits_affected": len(commits_with_secrets),
        "severity_counts": severity_counts,
    }


def main():
    """Main function."""
    # Determine repository directory
    repo_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

    if not repo_path.exists():
        print(f"❌ Error: Directory {repo_path} does not exist", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 Scanning git history in {repo_path}...", file=sys.stderr)

    # Scan git history
    findings = scan_git_history(repo_path)

    # Generate summary
    summary = generate_summary(findings)

    # Output results
    output = {
        "repository": str(repo_path),
        "scan_type": "git_history",
        "summary": summary,
        "findings": findings,
    }

    # Write to file
    output_file = repo_path / "git-history-scan-results.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    # Print summary
    print(f"\n✅ Git history scan complete!", file=sys.stderr)
    print(f"📄 Results written to: {output_file}", file=sys.stderr)
    print(f"\n📊 Summary:", file=sys.stderr)
    print(f"   Total findings: {summary['total_findings']}", file=sys.stderr)
    print(f"   Total secrets: {summary['total_secrets']}", file=sys.stderr)
    print(f"   Files affected: {summary['files_affected']}", file=sys.stderr)
    print(f"   Commits affected: {summary['commits_affected']}", file=sys.stderr)
    print(f"   Critical: {summary['severity_counts']['CRITICAL']}", file=sys.stderr)
    print(f"   High: {summary['severity_counts']['HIGH']}", file=sys.stderr)

    if summary['total_secrets'] > 0:
        print(f"\n⚠️  Secrets found in git history!", file=sys.stderr)
        print(f"⚠️  These secrets may have been exposed even if removed from current files.", file=sys.stderr)
        print(f"⚠️  Recommended actions:", file=sys.stderr)
        print(f"   1. Rotate all exposed credentials immediately", file=sys.stderr)
        print(f"   2. Use git-filter-repo to remove from history", file=sys.stderr)
        print(f"   3. Force push to remote (coordinate with team)", file=sys.stderr)

    # Exit with error if critical findings
    if summary['severity_counts']['CRITICAL'] > 0:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
