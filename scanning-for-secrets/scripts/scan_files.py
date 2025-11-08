#!/usr/bin/env python3
"""
Secret Scanner - File Scanner
Scans current files for hardcoded secrets, API keys, and credentials.
Optimized for Next.js/Vite and .NET/ABP projects.
"""

import re
import os
import json
import sys
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from multiprocessing import Pool, cpu_count

# Pattern definitions (compiled for performance)
PATTERNS = [
    # Cloud Provider Credentials
    {
        "name": "AWS Access Key ID",
        "pattern": re.compile(r"AKIA[0-9A-Z]{16}"),
        "severity": "CRITICAL",
        "context": [".env", "appsettings.json"],
    },
    {
        "name": "AWS Secret Access Key",
        "pattern": re.compile(r"aws[_-]?secret[_-]?access[_-]?key['\"\s:=]+[A-Za-z0-9/+=]{40}", re.IGNORECASE),
        "severity": "CRITICAL",
        "context": [".env", "appsettings.json"],
    },
    {
        "name": "Azure Storage Connection String",
        "pattern": re.compile(r"DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[A-Za-z0-9+/=]{88};"),
        "severity": "CRITICAL",
        "context": ["appsettings.json", ".env", "Web.config"],
    },
    {
        "name": "Google Cloud API Key",
        "pattern": re.compile(r"AIza[0-9A-Za-z_-]{35}"),
        "severity": "CRITICAL",
        "context": [".env", "next.config.js"],
    },

    # Azure Specific Patterns
    {
        "name": "Azure SQL Database Connection String",
        "pattern": re.compile(r"Server=tcp:[^;]+\.database\.windows\.net[^;]*;.*Password=([^;\"']+)", re.IGNORECASE),
        "severity": "CRITICAL",
        "context": ["appsettings.json", ".env", "azure-pipelines.yml"],
    },
    {
        "name": "Azure Service Principal Client Secret",
        "pattern": re.compile(r"(?:AZURE_CLIENT_SECRET|ClientSecret)['\"\s:=]+[A-Za-z0-9~._-]{34,40}", re.IGNORECASE),
        "severity": "CRITICAL",
        "context": [".env", "appsettings.json", "azure-pipelines.yml"],
    },
    {
        "name": "Azure DevOps Personal Access Token",
        "pattern": re.compile(r"(?:AZURE_DEVOPS_PAT|ADO_PAT|SYSTEM_ACCESSTOKEN)['\"\s:=]+[A-Za-z0-9]{52}", re.IGNORECASE),
        "severity": "CRITICAL",
        "context": [".env", "azure-pipelines.yml"],
    },
    {
        "name": "Azure Storage Account Key",
        "pattern": re.compile(r"(?:AccountKey|AZURE_STORAGE_KEY)['\"\s:=]+[A-Za-z0-9+/=]{88}", re.IGNORECASE),
        "severity": "CRITICAL",
        "context": ["appsettings.json", ".env"],
    },
    {
        "name": "Azure Cosmos DB Key",
        "pattern": re.compile(r"AccountEndpoint=https://[^;]+;AccountKey=([A-Za-z0-9+/=]{88})", re.IGNORECASE),
        "severity": "CRITICAL",
        "context": ["appsettings.json", ".env"],
    },
    {
        "name": "Azure Service Bus Connection String",
        "pattern": re.compile(r"Endpoint=sb://[^;]+;SharedAccessKeyName=[^;]+;SharedAccessKey=([A-Za-z0-9+/=]{43,})", re.IGNORECASE),
        "severity": "CRITICAL",
        "context": ["appsettings.json", ".env"],
    },
    {
        "name": "Azure Event Hub Connection String",
        "pattern": re.compile(r"Endpoint=sb://[^;]+\.servicebus\.windows\.net/;.*SharedAccessKey=([A-Za-z0-9+/=]{43,})", re.IGNORECASE),
        "severity": "CRITICAL",
        "context": ["appsettings.json", ".env"],
    },
    {
        "name": "Azure Redis Cache Connection String",
        "pattern": re.compile(r"[a-z0-9-]+\.redis\.cache\.windows\.net[^,]*,password=([^,\"']+)", re.IGNORECASE),
        "severity": "HIGH",
        "context": ["appsettings.json", ".env"],
    },
    {
        "name": "Azure Application Insights Key",
        "pattern": re.compile(r"(?:InstrumentationKey|APPINSIGHTS_INSTRUMENTATIONKEY)['\"\s:=]+[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", re.IGNORECASE),
        "severity": "MEDIUM",
        "context": ["appsettings.json", ".env"],
    },
    {
        "name": "Azure Container Registry Password",
        "pattern": re.compile(r"(?:ACR_PASSWORD|acrPassword)['\"\s:=]+[A-Za-z0-9+/=]{43,}", re.IGNORECASE),
        "severity": "CRITICAL",
        "context": [".env", "docker-compose.yml", "azure-pipelines.yml"],
    },
    {
        "name": "Azure Functions Host Key",
        "pattern": re.compile(r"x-functions-key['\"\s:=]+[A-Za-z0-9_-]{52,}", re.IGNORECASE),
        "severity": "HIGH",
        "context": ["local.settings.json", ".env"],
    },
    {
        "name": "Azure App Services Publishing Password",
        "pattern": re.compile(r"<publishProfile.*userName=\"([^\"]+)\".*userPWD=\"([^\"]+)\"", re.IGNORECASE),
        "severity": "CRITICAL",
        "context": [".pubxml", "publish profile"],
    },
    {
        "name": "Azure Key Vault Secret (in code)",
        "pattern": re.compile(r"https://[a-z0-9-]+\.vault\.azure\.net/secrets/[^/]+/([a-f0-9]{32})", re.IGNORECASE),
        "severity": "HIGH",
        "context": ["Any file"],
        "warning": "Secret version should not be hardcoded",
    },

    # Docker Specific Patterns
    {
        "name": "Docker Hub Access Token",
        "pattern": re.compile(r"(?:DOCKER_HUB_TOKEN|DOCKERHUB_TOKEN)['\"\s:=]+[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", re.IGNORECASE),
        "severity": "CRITICAL",
        "context": [".env", "docker-compose.yml", ".github/workflows"],
    },
    {
        "name": "Docker Registry Password",
        "pattern": re.compile(r"(?:DOCKER_PASSWORD|REGISTRY_PASSWORD)['\"\s:=]+[^\s\"']{8,}", re.IGNORECASE),
        "severity": "CRITICAL",
        "context": [".env", "docker-compose.yml", "Dockerfile"],
    },
    {
        "name": "Docker Compose Environment Secret",
        "pattern": re.compile(r"environment:\s*(?:\n\s+)?(?:.*\n\s+)*?[A-Z_]+(?:PASSWORD|SECRET|KEY|TOKEN):\s*['\"]?([^'\"\s]{8,})['\"]?", re.MULTILINE),
        "severity": "HIGH",
        "context": ["docker-compose.yml"],
        "warning": "Use docker secrets or .env file instead",
    },
    {
        "name": "Dockerfile ARG with Secret",
        "pattern": re.compile(r"ARG\s+(?:PASSWORD|SECRET|TOKEN|KEY|API_KEY)=([^\s]+)", re.IGNORECASE),
        "severity": "HIGH",
        "context": ["Dockerfile"],
        "warning": "ARG values are visible in image history",
    },
    {
        "name": "Dockerfile ENV with Secret",
        "pattern": re.compile(r"ENV\s+(?:PASSWORD|SECRET|TOKEN|KEY|API_KEY)\s*=?\s*([^\s]+)", re.IGNORECASE),
        "severity": "HIGH",
        "context": ["Dockerfile"],
        "warning": "ENV values are visible in image inspection",
    },
    {
        "name": "Harbor Registry Password",
        "pattern": re.compile(r"harbor[_-]?password['\"\s:=]+[^\s\"']{8,}", re.IGNORECASE),
        "severity": "CRITICAL",
        "context": [".env", "docker-compose.yml"],
    },

    # Next.js / Vite Specific
    {
        "name": "NEXT_PUBLIC with Sensitive Data",
        "pattern": re.compile(r"NEXT_PUBLIC_[A-Z_]*(?:API|SECRET|KEY|TOKEN)['\"\s:=]+[A-Za-z0-9+/=-]{20,}", re.IGNORECASE),
        "severity": "HIGH",
        "context": [".env"],
        "warning": "NEXT_PUBLIC_ vars are exposed to browser",
    },
    {
        "name": "VITE with Sensitive Data",
        "pattern": re.compile(r"VITE_[A-Z_]*(?:API|SECRET|KEY|TOKEN)['\"\s:=]+[A-Za-z0-9+/=-]{20,}", re.IGNORECASE),
        "severity": "HIGH",
        "context": [".env"],
        "warning": "VITE_ vars are exposed to browser",
    },
    {
        "name": "Vercel Token",
        "pattern": re.compile(r"vercel[_-]?token['\"\s:=]+[A-Za-z0-9]{24}", re.IGNORECASE),
        "severity": "CRITICAL",
        "context": [".vercel/", ".env"],
    },
    {
        "name": "Next.js API Secret",
        "pattern": re.compile(r"(?:NEXTAUTH_SECRET|API_SECRET|APP_SECRET)['\"\s:=]+[A-Za-z0-9+/=-]{32,}", re.IGNORECASE),
        "severity": "CRITICAL",
        "context": [".env.local"],
    },

    # .NET / ABP Specific
    {
        "name": "SQL Server Connection String",
        "pattern": re.compile(r"(?:Server|Data Source)=[^;]+;(?:Database|Initial Catalog)=[^;]+;(?:User ID|UID)=([^;]+);(?:Password|PWD)=([^;\"']+)", re.IGNORECASE),
        "severity": "CRITICAL",
        "context": ["appsettings.json", "Web.config"],
    },
    {
        "name": "Entity Framework Connection String with Password",
        "pattern": re.compile(r'ConnectionStrings["\s:]*\{[^}]*Password=([^;"\']+)', re.IGNORECASE),
        "severity": "CRITICAL",
        "context": ["appsettings.json"],
    },
    {
        "name": "ABP License Code",
        "pattern": re.compile(r"AbpLicenseCode['\"\s:=]+[A-Za-z0-9+/=-]{50,}", re.IGNORECASE),
        "severity": "MEDIUM",
        "context": ["appsettings.json"],
    },
    {
        "name": "IdentityServer Client Secret",
        "pattern": re.compile(r'ClientSecrets["\s:]*\[[^\]]*Value["\s:]*["\']([A-Za-z0-9+/=-]{16,})["\']', re.IGNORECASE),
        "severity": "CRITICAL",
        "context": ["appsettings.json"],
    },
    {
        "name": "JWT Signing Key (.NET)",
        "pattern": re.compile(r'(?:JwtBearer|Jwt).*["\'](?:Secret|SigningKey|IssuerSigningKey)["\']:\s*["\']([A-Za-z0-9+/=-]{32,})["\']', re.IGNORECASE),
        "severity": "CRITICAL",
        "context": ["appsettings.json"],
    },
    {
        "name": "Redis Connection with Password",
        "pattern": re.compile(r"(?:localhost|[0-9.]+|[a-z0-9.-]+):\d+,password=([^,\s\"']+)", re.IGNORECASE),
        "severity": "HIGH",
        "context": ["appsettings.json"],
    },
    {
        "name": "SMTP Password",
        "pattern": re.compile(r'Smtp["\s:]*\{[^}]*["\'](?:Password|UserName)["\']:\s*["\']([^"\']{8,})["\']', re.IGNORECASE),
        "severity": "HIGH",
        "context": ["appsettings.json"],
    },

    # Generic Patterns
    {
        "name": "Private Key",
        "pattern": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        "severity": "CRITICAL",
        "context": ["Any file"],
    },
    {
        "name": "JWT Token",
        "pattern": re.compile(r"eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+"),
        "severity": "HIGH",
        "context": [".env", "config files"],
    },
    {
        "name": "Generic API Key",
        "pattern": re.compile(r"(?:api[_-]?key|apikey|api[_-]?secret)['\"\s:=]+([A-Za-z0-9_-]{20,})", re.IGNORECASE),
        "severity": "HIGH",
        "context": [".env", "config files"],
    },
    {
        "name": "Password Variable",
        "pattern": re.compile(r'(?:password|passwd|pwd)["\s:=]+["\']?([^"\'\s]{8,})["\']?', re.IGNORECASE),
        "severity": "HIGH",
        "context": ["Any config file"],
    },
    {
        "name": "Database URL with Credentials",
        "pattern": re.compile(r"(?:postgres|mysql|mongodb(?:\+srv)?)://[a-zA-Z0-9_-]+:([^@\s]+)@"),
        "severity": "CRITICAL",
        "context": [".env", "DATABASE_URL"],
    },
    {
        "name": "Bearer Token",
        "pattern": re.compile(r"Bearer\s+[A-Za-z0-9_-]{20,}"),
        "severity": "HIGH",
        "context": ["HTTP headers in code"],
    },
    {
        "name": "Slack Webhook",
        "pattern": re.compile(r"https://hooks\.slack\.com/services/T[A-Z0-9]{8,}/B[A-Z0-9]{8,}/[A-Za-z0-9]{24}"),
        "severity": "MEDIUM",
        "context": [".env"],
    },
    {
        "name": "GitHub Token",
        "pattern": re.compile(r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}"),
        "severity": "CRITICAL",
        "context": [".env", "CI/CD configs"],
    },
    {
        "name": "Stripe API Key",
        "pattern": re.compile(r"(?:sk|pk)_(?:live|test)_[0-9a-zA-Z]{24,}"),
        "severity": "CRITICAL",
        "context": [".env"],
    },
    {
        "name": "SendGrid API Key",
        "pattern": re.compile(r"SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}"),
        "severity": "HIGH",
        "context": [".env", "appsettings.json"],
    },
    {
        "name": "NPM Auth Token",
        "pattern": re.compile(r"//registry\.npmjs\.org/:_authToken=([A-Za-z0-9-_]+)"),
        "severity": "CRITICAL",
        "context": [".npmrc"],
    },
]

# NOTE: This list is for DOCUMENTATION ONLY - the scanner actually scans ALL files recursively.
# The scanner uses os.walk() to find all files, then filters by binary detection and SKIP_DIRS.
# This means it automatically handles ALL variations:
#   - azure-pipelines.yml, azure-pipeline.yaml, azure_pipelines.yml
#   - docker-compose.yml, docker-compose.yaml, docker_compose.yml
#   - .gitlab-ci.yml, .gitlab-ci.yaml
# Common target files (for reference):
TARGET_FILES_REFERENCE = [
    # Next.js / Vite
    ".env", ".env.local", ".env.production", ".env.development", ".env.staging",
    "next.config.js", "next.config.mjs", "next.config.ts",
    "vite.config.js", "vite.config.ts",

    # .NET / ABP
    "appsettings.json", "appsettings.*.json",
    "Web.config", "App.config",
    "*.csproj", "*.pubxml",

    # Azure
    "azure-pipelines.yml", "azure-pipelines.yaml", "local.settings.json",

    # Docker
    "docker-compose.yml", "docker-compose.yaml", "Dockerfile",

    # CI/CD & Common
    ".gitlab-ci.yml", ".gitlab-ci.yaml",
    "package.json", ".npmrc",
]

# Directories to skip
SKIP_DIRS = {
    "node_modules", ".git", "bin", "obj", "dist", "build", ".next",
    "__pycache__", ".venv", "venv", "vendor", "packages",
    ".vercel", ".nuxt", ".cache", "coverage",
}

# File extensions to skip (binary files)
SKIP_EXTENSIONS = {
    ".exe", ".dll", ".so", ".dylib", ".bin", ".dat",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico",
    ".pdf", ".zip", ".tar", ".gz", ".rar", ".7z",
    ".mp3", ".mp4", ".avi", ".mov", ".woff", ".woff2", ".ttf", ".eot",
}


def is_binary_file(file_path: Path) -> bool:
    """Check if file is binary by reading first 8192 bytes."""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)
            if b'\0' in chunk:
                return True
        return False
    except Exception:
        return True


def should_scan_file(file_path: Path) -> bool:
    """Determine if file should be scanned."""
    # Check if any parent directory is in skip list
    for parent in file_path.parents:
        if parent.name in SKIP_DIRS:
            return False

    # Skip binary extensions
    if file_path.suffix in SKIP_EXTENSIONS:
        return False

    # Skip if binary
    if is_binary_file(file_path):
        return False

    # Skip files larger than 10MB (likely binary or generated)
    try:
        if file_path.stat().st_size > 10 * 1024 * 1024:
            return False
    except Exception:
        return False

    return True


def scan_file(file_path: Path) -> List[Dict]:
    """Scan a single file for secrets."""
    findings = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, start=1):
            for pattern_def in PATTERNS:
                matches = pattern_def["pattern"].finditer(line)
                for match in matches:
                    # Extract matched value
                    matched_value = match.group(0)
                    if match.groups():
                        matched_value = match.group(1) if len(match.groups()) >= 1 else matched_value

                    finding = {
                        "file": str(file_path),
                        "line": line_num,
                        "pattern_name": pattern_def["name"],
                        "severity": pattern_def["severity"],
                        "matched_value": matched_value[:100],  # Limit to 100 chars
                        "line_content": line.strip()[:200],  # Context
                        "warning": pattern_def.get("warning", ""),
                    }
                    findings.append(finding)

    except Exception as e:
        # Silently skip files that can't be read
        pass

    return findings


def scan_directory_worker(file_path: Path) -> List[Dict]:
    """Worker function for parallel scanning."""
    if should_scan_file(file_path):
        return scan_file(file_path)
    return []


def scan_directory(directory: Path, use_multiprocessing: bool = True) -> List[Dict]:
    """Scan directory recursively for secrets."""
    all_findings = []

    # Collect all files to scan
    files_to_scan = []
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for file_name in files:
            file_path = Path(root) / file_name
            files_to_scan.append(file_path)

    print(f"📁 Found {len(files_to_scan)} files to check...", file=sys.stderr)

    if use_multiprocessing and len(files_to_scan) > 10:
        # Use multiprocessing for large scans
        num_processes = max(1, cpu_count() - 1)
        with Pool(num_processes) as pool:
            results = pool.map(scan_directory_worker, files_to_scan)

        for findings in results:
            all_findings.extend(findings)
    else:
        # Single-threaded for small scans
        for file_path in files_to_scan:
            findings = scan_directory_worker(file_path)
            all_findings.extend(findings)

    return all_findings


def generate_summary(findings: List[Dict]) -> Dict:
    """Generate summary statistics."""
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    pattern_counts = {}

    for finding in findings:
        severity = finding["severity"]
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

        pattern = finding["pattern_name"]
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

    return {
        "total_findings": len(findings),
        "severity_counts": severity_counts,
        "pattern_counts": pattern_counts,
    }


def main():
    """Main scanner function."""
    # Determine scan directory
    scan_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

    if not scan_dir.exists():
        print(f"❌ Error: Directory {scan_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 Scanning {scan_dir} for secrets...", file=sys.stderr)
    print(f"📊 Using {len(PATTERNS)} detection patterns", file=sys.stderr)

    # Scan directory
    findings = scan_directory(scan_dir)

    # Generate summary
    summary = generate_summary(findings)

    # Output results as JSON
    output = {
        "scan_directory": str(scan_dir),
        "summary": summary,
        "findings": findings,
    }

    # Write to file
    output_file = scan_dir / "secret-scan-results.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    # Print summary to stderr
    print(f"\n✅ Scan complete!", file=sys.stderr)
    print(f"📄 Results written to: {output_file}", file=sys.stderr)
    print(f"\n📊 Summary:", file=sys.stderr)
    print(f"   Total findings: {summary['total_findings']}", file=sys.stderr)
    print(f"   Critical: {summary['severity_counts']['CRITICAL']}", file=sys.stderr)
    print(f"   High: {summary['severity_counts']['HIGH']}", file=sys.stderr)
    print(f"   Medium: {summary['severity_counts']['MEDIUM']}", file=sys.stderr)
    print(f"   Low: {summary['severity_counts']['LOW']}", file=sys.stderr)

    # Exit with error code if critical findings
    if summary['severity_counts']['CRITICAL'] > 0:
        print(f"\n⚠️  {summary['severity_counts']['CRITICAL']} CRITICAL findings detected!", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
