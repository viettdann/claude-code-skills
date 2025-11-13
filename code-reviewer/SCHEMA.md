# Code Review JSON/YAML Schema

This document defines the structured output schema for code reviews, enabling programmatic consumption for PR automation, CI/CD integration, and automated code review bots.

## Overview

The skill generates both human-readable markdown reports AND machine-readable JSON/YAML files for each review. The JSON/YAML output enables:

- **Automated PR comments** - Post inline comments on specific lines
- **CI/CD integration** - Block merges based on severity
- **Review aggregation** - Track code quality over time
- **Custom tooling** - Build dashboards, metrics, alerts

## File Outputs

For each review, the skill generates:

1. **Markdown Report**: `CODE-REVIEW-REPORT-{date}.md` (human-readable)
2. **JSON Output**: `CODE-REVIEW-REPORT-{date}.json` (machine-readable)
3. **YAML Output** (optional): `CODE-REVIEW-REPORT-{date}.yaml`

## JSON Schema

### Root Object

```json
{
  "review": {
    "metadata": {...},
    "summary": {...},
    "issues": [...],
    "strengths": [...],
    "files": [...],
    "metrics": {...}
  }
}
```

### Complete Schema

```typescript
interface CodeReview {
  review: {
    metadata: ReviewMetadata;
    summary: ReviewSummary;
    issues: Issue[];
    strengths: Strength[];
    files: FileAnalysis[];
    metrics: ReviewMetrics;
  }
}

interface ReviewMetadata {
  project: string;
  framework: string;
  language: string;
  reviewDate: string;          // ISO 8601: "2025-01-13T14:30:00Z"
  analyzedBy: string;           // "Code Reviewer Skill v1.0"
  reviewType: string;           // "commit" | "branch" | "security-audit" | "full"
  commit?: {
    sha: string;
    message: string;
    author: string;
    date: string;
  };
  branch?: string;
  reportVersion: string;        // "1.0.0"
}

interface ReviewSummary {
  grade: string;                // "A+", "A", "A-", "B+", "B", "C", "F"
  verdict: string;              // "LGTM" | "Needs Changes" | "Blocked"
  overallAssessment: string;    // Plain text summary
  filesReviewed: number;
  linesAdded: number;
  linesRemoved: number;
  totalIssues: number;
  issueCounts: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  strengthsCount: number;
  estimatedFixTime: number;     // Total minutes
  productionReady: boolean;
}

interface Issue {
  id: string;                   // "CRITICAL-1", "HIGH-2", etc.
  severity: "critical" | "high" | "medium" | "low";
  title: string;
  category: string;             // "Security", "Performance", "Code Quality", etc.
  file: string;                 // "src/api/auth.ts"
  line: number;                 // Start line number
  lineEnd?: number;             // End line (for ranges)
  column?: number;              // Optional column number
  description: string;          // Plain text description
  impact: string[];             // Array of impact points
  currentCode?: string;         // Problematic code snippet
  recommendedFix?: string;      // Fixed code snippet
  fixOptions?: FixOption[];     // Multiple fix approaches
  estimatedFixTime: number;     // Minutes
  references: string[];         // URLs to docs
  tags: string[];               // ["sql-injection", "security", "owasp"]
  autoFixable: boolean;         // Can be auto-fixed?
  priority: number;             // 0=highest (P0), 1=P1, 2=P2, 3=P3
}

interface FixOption {
  name: string;                 // "Option 1: Parameterized Queries (Recommended)"
  description: string;
  code: string;                 // Code example
  steps?: string[];             // Step-by-step instructions
}

interface Strength {
  id: string;                   // "STRENGTH-1"
  title: string;
  category: string;             // "Architecture", "Security", "Performance"
  description: string;
  evidence: string[];           // Evidence points
  exampleCode?: string;         // Code showing best practice
  file?: string;                // Optional: file where found
  line?: number;                // Optional: line number
  benefits: string[];           // Why this is excellent
}

interface FileAnalysis {
  path: string;                 // "src/api/auth.ts"
  linesAdded: number;
  linesRemoved: number;
  language: string;             // "TypeScript", "C#", etc.
  issues: string[];             // Issue IDs found in this file
  strengths: string[];          // Strength IDs found in this file
  complexity?: string;          // "low", "medium", "high"
  status: string;               // "clean", "needs-review", "blocked"
}

interface ReviewMetrics {
  security: MetricScore;
  performance: MetricScore;
  codeQuality: MetricScore;
  bestPractices: MetricScore;
  testCoverage?: MetricScore;
  overallScore: number;         // 0-100
}

interface MetricScore {
  score: number;                // 0-100
  grade: string;                // "A+", "A", etc.
  status: "excellent" | "good" | "needs-attention" | "critical";
  description: string;
}
```

## Example JSON Output

```json
{
  "review": {
    "metadata": {
      "project": "MyApp",
      "framework": "Node.js with Express",
      "language": "TypeScript",
      "reviewDate": "2025-01-13T14:30:00Z",
      "analyzedBy": "Code Reviewer Skill v1.0",
      "reviewType": "commit",
      "commit": {
        "sha": "abc1234",
        "message": "Add user authentication endpoint",
        "author": "John Doe",
        "date": "2025-01-13T10:15:00Z"
      },
      "reportVersion": "1.0.0"
    },
    "summary": {
      "grade": "B+",
      "verdict": "Needs Changes",
      "overallAssessment": "Good implementation with 1 critical security issue requiring immediate fix",
      "filesReviewed": 2,
      "linesAdded": 57,
      "linesRemoved": 0,
      "totalIssues": 3,
      "issueCounts": {
        "critical": 1,
        "high": 1,
        "medium": 1,
        "low": 0
      },
      "strengthsCount": 3,
      "estimatedFixTime": 20,
      "productionReady": false
    },
    "issues": [
      {
        "id": "CRITICAL-1",
        "severity": "critical",
        "title": "SQL Injection Vulnerability",
        "category": "Security",
        "file": "src/api/auth.ts",
        "line": 23,
        "lineEnd": 23,
        "column": 15,
        "description": "User input (email) is directly concatenated into SQL query without sanitization or parameterization, allowing attackers to execute arbitrary SQL commands.",
        "impact": [
          "Complete database compromise - Attackers can read, modify, or delete all data",
          "Authentication bypass - Attackers can login as any user",
          "Data breach - User credentials and sensitive data exposed"
        ],
        "currentCode": "const query = `SELECT * FROM users WHERE email = '${email}'`;",
        "recommendedFix": "const query = 'SELECT * FROM users WHERE email = ?';\ndb.execute(query, [email]);",
        "fixOptions": [
          {
            "name": "Option 1: Parameterized Queries (Recommended)",
            "description": "Use parameterized queries to prevent SQL injection",
            "code": "const query = 'SELECT * FROM users WHERE email = ?';\nconst user = await db.execute(query, [email]);",
            "steps": [
              "Replace template literal with parameterized query",
              "Pass user input as parameters array",
              "Test with malicious input to verify fix"
            ]
          },
          {
            "name": "Option 2: ORM with Query Builder",
            "description": "Use an ORM like Prisma or TypeORM for type-safe queries",
            "code": "const user = await prisma.user.findUnique({\n  where: { email: email }\n});",
            "steps": [
              "Install Prisma: npm install @prisma/client",
              "Define schema and generate client",
              "Use type-safe query methods"
            ]
          }
        ],
        "estimatedFixTime": 5,
        "references": [
          "https://owasp.org/www-community/attacks/SQL_Injection",
          "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html"
        ],
        "tags": ["sql-injection", "security", "owasp-a03", "cwe-89"],
        "autoFixable": false,
        "priority": 0
      },
      {
        "id": "HIGH-1",
        "severity": "high",
        "title": "Password Stored in Plain Text",
        "category": "Security",
        "file": "src/api/auth.ts",
        "line": 34,
        "description": "User password is stored in database without hashing, exposing all passwords if database is breached.",
        "impact": [
          "Mass credential exposure if database compromised",
          "Users with same password on other sites at risk",
          "Compliance violations (GDPR, PCI-DSS)"
        ],
        "currentCode": "await db.execute('INSERT INTO users (email, password) VALUES (?, ?)', [email, password]);",
        "recommendedFix": "import bcrypt from 'bcrypt';\nconst hashedPassword = await bcrypt.hash(password, 10);\nawait db.execute('INSERT INTO users (email, password) VALUES (?, ?)', [email, hashedPassword]);",
        "estimatedFixTime": 10,
        "references": [
          "https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html"
        ],
        "tags": ["password-security", "hashing", "owasp-a02"],
        "autoFixable": false,
        "priority": 0
      },
      {
        "id": "MEDIUM-1",
        "severity": "medium",
        "title": "Missing Input Validation",
        "category": "Code Quality",
        "file": "src/api/auth.ts",
        "line": 15,
        "description": "Email input not validated before use, could lead to invalid data in database.",
        "impact": [
          "Invalid email addresses stored in database",
          "Poor user experience with confusing errors"
        ],
        "recommendedFix": "import { z } from 'zod';\nconst emailSchema = z.string().email();\nconst validatedEmail = emailSchema.parse(email);",
        "estimatedFixTime": 5,
        "references": [
          "https://github.com/colinhacks/zod"
        ],
        "tags": ["validation", "data-quality"],
        "autoFixable": true,
        "priority": 1
      }
    ],
    "strengths": [
      {
        "id": "STRENGTH-1",
        "title": "Proper Async/Await Usage",
        "category": "Best Practices",
        "description": "Consistent use of async/await throughout the codebase with no blocking operations",
        "evidence": [
          "All database operations use await",
          "No .then() chaining (consistent async style)",
          "No blocking sync operations found"
        ],
        "exampleCode": "public async loginUser(email: string, password: string) {\n  const user = await db.execute(query, [email]);\n  return user;\n}",
        "file": "src/api/auth.ts",
        "line": 15,
        "benefits": [
          "Better performance - non-blocking I/O",
          "Improved scalability - efficient thread usage",
          "Cleaner code - more readable than callbacks"
        ]
      },
      {
        "id": "STRENGTH-2",
        "title": "Strong TypeScript Typing",
        "category": "Code Quality",
        "description": "Proper TypeScript types used throughout with no 'any' types",
        "evidence": [
          "Explicit return types on all functions",
          "Properly typed function parameters",
          "No use of 'any' type"
        ],
        "benefits": [
          "Type safety catches errors at compile time",
          "Better IDE autocomplete and refactoring",
          "Self-documenting code"
        ]
      },
      {
        "id": "STRENGTH-3",
        "title": "Comprehensive Error Handling",
        "category": "Code Quality",
        "description": "All async operations wrapped in try-catch blocks",
        "evidence": [
          "Try-catch blocks for all database operations",
          "Proper error logging",
          "User-friendly error messages"
        ],
        "benefits": [
          "Graceful error recovery",
          "Better debugging with error logs",
          "Improved user experience"
        ]
      }
    ],
    "files": [
      {
        "path": "src/api/auth.ts",
        "linesAdded": 45,
        "linesRemoved": 0,
        "language": "TypeScript",
        "issues": ["CRITICAL-1", "HIGH-1", "MEDIUM-1"],
        "strengths": ["STRENGTH-1", "STRENGTH-2", "STRENGTH-3"],
        "complexity": "medium",
        "status": "blocked"
      },
      {
        "path": "src/types/user.ts",
        "linesAdded": 12,
        "linesRemoved": 0,
        "language": "TypeScript",
        "issues": [],
        "strengths": ["STRENGTH-2"],
        "complexity": "low",
        "status": "clean"
      }
    ],
    "metrics": {
      "security": {
        "score": 45,
        "grade": "C",
        "status": "critical",
        "description": "Critical security vulnerabilities found - SQL injection and password storage issues"
      },
      "performance": {
        "score": 90,
        "grade": "A-",
        "status": "excellent",
        "description": "Excellent async patterns, no obvious performance issues"
      },
      "codeQuality": {
        "score": 85,
        "grade": "B+",
        "status": "good",
        "description": "Good code quality with strong typing and error handling"
      },
      "bestPractices": {
        "score": 75,
        "grade": "B",
        "status": "needs-attention",
        "description": "Following most best practices, missing input validation"
      },
      "overallScore": 74
    }
  }
}
```

## Example YAML Output

```yaml
review:
  metadata:
    project: MyApp
    framework: Node.js with Express
    language: TypeScript
    reviewDate: '2025-01-13T14:30:00Z'
    analyzedBy: Code Reviewer Skill v1.0
    reviewType: commit
    commit:
      sha: abc1234
      message: Add user authentication endpoint
      author: John Doe
      date: '2025-01-13T10:15:00Z'
    reportVersion: 1.0.0

  summary:
    grade: B+
    verdict: Needs Changes
    overallAssessment: Good implementation with 1 critical security issue requiring immediate fix
    filesReviewed: 2
    linesAdded: 57
    linesRemoved: 0
    totalIssues: 3
    issueCounts:
      critical: 1
      high: 1
      medium: 1
      low: 0
    strengthsCount: 3
    estimatedFixTime: 20
    productionReady: false

  issues:
    - id: CRITICAL-1
      severity: critical
      title: SQL Injection Vulnerability
      category: Security
      file: src/api/auth.ts
      line: 23
      description: User input directly concatenated into SQL query
      impact:
        - Complete database compromise
        - Authentication bypass
      currentCode: "const query = `SELECT * FROM users WHERE email = '${email}'`;"
      recommendedFix: |
        const query = 'SELECT * FROM users WHERE email = ?';
        db.execute(query, [email]);
      estimatedFixTime: 5
      references:
        - https://owasp.org/www-community/attacks/SQL_Injection
      tags: [sql-injection, security, owasp-a03]
      autoFixable: false
      priority: 0

  strengths:
    - id: STRENGTH-1
      title: Proper Async/Await Usage
      category: Best Practices
      description: Consistent use of async/await throughout
      benefits:
        - Better performance
        - Improved scalability

  files:
    - path: src/api/auth.ts
      linesAdded: 45
      linesRemoved: 0
      language: TypeScript
      issues: [CRITICAL-1, HIGH-1, MEDIUM-1]
      strengths: [STRENGTH-1, STRENGTH-2, STRENGTH-3]
      status: blocked

  metrics:
    security:
      score: 45
      grade: C
      status: critical
    overallScore: 74
```

## JSON Output Usage

The JSON output is designed for PR automation and CI/CD integration. It contains structured data with file paths, line numbers, and severity levels that can be consumed by your custom tooling or PR bots.

## Version

- **Schema Version**: 1.0.0
- **Last Updated**: 2025-01-13
- **Compatible With**: Code Reviewer Skill v1.0+
