---
name: code-reviewer
description: Expert code reviewer for code quality, security, and best practices. Use proactively after code changes, commits, merges, or when user requests code review. Analyzes latest commits including merge commits. Automatically generates comprehensive markdown reports.
allowed-tools: Bash, Read, Grep, Glob, Task, Write
---

# Code Reviewer

This skill provides expert code review for code quality, security, and best practices.

## When to Activate

Automatically activate when:
- User has just made code changes or commits
- User mentions "review", "commit", "merge", or "code quality"
- After significant code modifications
- User explicitly requests a code review

## Review Execution Steps

### 1. Identify Latest Changes

**For latest commit review:**
```bash
# Get the latest commit SHA and message
git log -1 --oneline

# Show files changed in latest commit
git show --stat HEAD

# Get detailed diff for latest commit
git show HEAD
```

**For merge commit review:**
```bash
# Check if latest commit is a merge
git log -1 --merges

# For merge commits, compare against first parent
git diff HEAD^1 HEAD

# Show all files in merge
git diff --name-status HEAD^1 HEAD
```

**For uncommitted changes:**
```bash
# Show uncommitted changes
git diff
git diff --staged
```

### 2. Analyze Changed Files

For each file:

1. **Read the full file** to understand context
2. **Identify the specific changes** using git diff
3. **Analyze for issues** across multiple dimensions

### 3. Review Dimensions

Review code across critical areas:

#### Security Vulnerabilities

Check for:
- SQL injection vulnerabilities (unsanitized queries)
- XSS vulnerabilities (unescaped user input)
- Command injection (shell execution with user input)
- Path traversal vulnerabilities
- Hardcoded secrets/credentials
- Insecure cryptography
- Authentication/authorization bypasses
- CSRF vulnerabilities
- Insecure deserialization
- Use of dangerous functions (`eval`, `exec`, `innerHTML`)

Reference [PATTERNS.md](PATTERNS.md) for specific grep patterns.

#### Code Quality

Assess:
- **Readability**: Clear naming, proper structure
- **Maintainability**: DRY principle, single responsibility
- **Error Handling**: Proper try/catch, error messages
- **Type Safety**: Proper typing (TypeScript/C#/etc)
- **Null Safety**: Null checks, optional chaining
- **Resource Management**: Proper cleanup, disposal
- **Async/Await**: Correct async patterns
- **Performance**: Inefficient algorithms, N+1 queries

#### Best Practices

Verify:
- **Framework conventions** (Next.js, React, ABP, etc)
- **Architecture patterns** (DDD, Clean Architecture)
- **SOLID principles**
- **Code organization** and structure
- **Naming conventions**
- **Comment quality** (why, not what)
- **Test coverage** (if test files included)
- **Dependency management**

#### Language/Framework Specific

**JavaScript/TypeScript:**
- React hooks rules
- Next.js best practices (Server Components, Server Actions)
- Proper state management
- Event handler security
- API route security

**C#/.NET:**
- ABP Framework patterns
- Entity Framework best practices
- Async/await patterns
- Dependency injection
- Exception handling

**Python:**
- PEP 8 compliance
- Type hints usage
- Context managers
- List comprehensions vs loops

**Other languages:**
- Apply language-specific idioms and conventions

### 4. Generate Comprehensive Review Report

**IMPORTANT**: Always generate a comprehensive markdown report file that documents all findings.

#### 4.1 Determine Report Filename

Generate report filename based on context:

```bash
# Get project name from git root directory
PROJECT_NAME=$(basename $(git rev-parse --show-toplevel))

# Get commit SHA if reviewing commit
COMMIT_SHA=$(git log -1 --format=%h)

# Get current date
REVIEW_DATE=$(date +%Y-%m-%d)

# Generate filename (one of these patterns):
# 1. For commit reviews: CODE-REVIEW-REPORT-${REVIEW_DATE}-${COMMIT_SHA}.md
# 2. For general reviews: CODE-REVIEW-REPORT-${REVIEW_DATE}.md
# 3. For security audits: SECURITY-AUDIT-REPORT-${REVIEW_DATE}.md
```

**Examples:**
- `CODE-REVIEW-REPORT-2025-11-14.md` (general review)
- `CODE-REVIEW-REPORT-2025-11-14-[commit-hash].md` (commit review)
- `SECURITY-AUDIT-REPORT-2025-11-14.md` (security audit)

#### 4.2 Report Structure

Generate a comprehensive markdown report following the complete structure defined in [REPORT-TEMPLATE.md](REPORT-TEMPLATE.md).

**Report includes:**
- Executive summary with overall grade (A+ to F)
- Severity-classified issues (Critical, High, Medium, Low)
- Strengths and best practices identified
- Priority roadmap
- Recommended immediate actions with phases
- Verification checklist for production readiness
- References and resources
- Complete appendix with quick reference links

**Key principles:**
- **Be specific**: Include file paths with line numbers (`path/to/file.ext:123`)
- **Identify issues clearly**: Point out what's wrong and why it's problematic
- **Minimal fix guidance**: Suggest approach/direction, not full implementations
- **Reference docs**: Link to official framework documentation
- **NO time estimates**: Do not include fix time estimates - this is a review, not a plan
- **Reviewer mindset**: Point out problems, not guide through solutions

See [REPORT-TEMPLATE.md](REPORT-TEMPLATE.md) for the complete template structure.

#### 4.3 Report Generation Workflow

After completing the analysis:

1. **Collect all findings** - Organize by severity
2. **Count statistics** - Files reviewed, lines changed, issues by severity
3. **Generate filename** - Based on review type and date
4. **Write report file** - Use Write tool to create the markdown file
5. **Inform user** - Tell user the report file path and location

**Example:**

```bash
# After analysis is complete, generate report
REPORT_FILE="CODE-REVIEW-REPORT-2025-01-13.md"

# Use Write tool to create the report
# (populate with all findings organized by the structure above)

# Inform user
echo "✅ Code review complete!"
echo "📄 Report saved to: ${REPORT_FILE}"
echo ""
echo "Summary:"
echo "- Critical Issues: X"
echo "- High Priority: X"
echo "- Medium Priority: X"
echo "- Low Priority: X"
echo "- Strengths Identified: X+"
echo ""
echo "Overall Grade: A-"
echo "Recommendation: [Verdict]"
```

### 5. Generate JSON Output (Optional)

**IMPORTANT**: Generate JSON output **ONLY when user explicitly requests it** (e.g., "generate JSON report", "I need JSON output", "export as JSON").

**By default:** Generate markdown report only. JSON is for CI/CD integration, not human consumption.

When user requests JSON, create a JSON file:

```bash
# Generate JSON filename
JSON_FILE="${REPORT_FILE%.md}.json"

# Example: CODE-REVIEW-REPORT-2025-01-13.json (general)
# Example: CODE-REVIEW-REPORT-2025-01-13-abc1234.json (commit)
```

#### 5.1 JSON Structure

Follow the complete schema defined in [SCHEMA.md](SCHEMA.md).

**Key sections:**
- `metadata` - Project, commit, timestamps
- `summary` - Grade, verdict, issue counts, productionReady flag
- `issues[]` - File, line, severity, description, fix
- `strengths[]` - Best practices identified
- `files[]` - Per-file status
- `metrics` - Quality scores

**Important:** Generate **compact JSON** (no pretty-printing) to minimize file size for CI/CD systems and reduce token usage when parsed.

#### 5.2 Generation Workflow (When Requested)

```bash
# Only execute when user explicitly requests JSON

# 1. Collect metadata
REPORT_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
COMMIT_SHA=$(git log -1 --format=%h)
PROJECT_NAME=$(basename $(git rev-parse --show-toplevel))

# 2. Generate JSON filename (must match markdown report filename)
JSON_FILE="CODE-REVIEW-REPORT-$(date +%Y-%m-%d)-${COMMIT_SHA}.json"

# 3. Use Write tool to create COMPACT JSON (no pretty-printing)
# Populate with all findings organized according to schema

# 4. VALIDATE JSON with jq (quick check)
if command -v jq &> /dev/null; then
  if jq empty "$JSON_FILE" 2>/dev/null; then
    echo "✓ JSON validation passed"
  else
    echo "✗ JSON validation FAILED - file may be invalid"
  fi
fi

# 5. Inform user
echo "✅ Code review complete!"
echo "📄 Markdown report: ${REPORT_FILE}"
echo "📊 JSON output: ${JSON_FILE}"
```

**Notes:**
- Generate **compact JSON** (single-line, no indentation) to minimize file size for CI/CD systems and reduce token usage when parsed
- Validate with `jq` if available (optional but recommended) - fails fast if JSON is malformed
- JSON can be used for PR automation, CI/CD integration, or custom tooling

## Review Guidelines

### Be Constructive

- **Focus on the code, not the person**
- **Explain WHY something is an issue**
- **Point to solution direction, not full implementations**
- **Acknowledge good practices**
- **Prioritize by severity**
- **Act as reviewer, not teacher**: Identify problems, link to docs, let developer solve

### Be Specific

- **Always include file paths and line numbers**
- **Show problematic code snippet when needed**
- **Reference official documentation**
- **Explain the impact of issues**
- **Suggest fix approach, not detailed code**: Brief direction, minimal implementation

### Be Thorough

- **Review all changed files**
- **Consider edge cases**
- **Check for related issues**
- **Validate in broader context**

### Be Practical

- **Distinguish between blockers and nice-to-haves**
- **Consider project context and deadlines**
- **Suggest incremental improvements**
- **Balance perfection with pragmatism**

## Severity Classification

**Critical**: Security vulnerabilities, data corruption, system crashes
- Must be fixed before merge
- Examples: SQL injection, XSS, auth bypass

**High**: Bugs, major performance issues, architectural violations
- Should be fixed before merge
- Examples: Memory leaks, incorrect logic, N+1 queries

**Medium**: Code quality issues, minor performance problems
- Should be addressed soon
- Examples: Code duplication, missing error handling

**Low**: Style issues, minor optimizations, suggestions
- Nice to have, consider for future
- Examples: Naming improvements, comment additions

## False Positive Prevention

Before reporting an issue:

1. **Read surrounding context** - Don't just grep, understand the code
2. **Check framework conventions** - What seems wrong might be idiomatic
3. **Verify assumptions** - Ensure your understanding is correct
4. **Consider test code** - Different standards may apply
5. **Check dependencies** - External packages may handle concerns

## Tools Usage

- **Bash**: Git operations, file stats
- **Read**: Read full file contents for context
- **Grep**: Search for specific patterns (use PATTERNS.md)
- **Glob**: Find related files
- **Task**: Complex exploration when needed

## Special Cases

### Merge Commits

For merge commits, focus on:
1. Conflict resolution correctness
2. Integration issues between branches
3. Regression risks
4. Consistency across merged changes

### Large Commits

For commits with 10+ files:
1. Prioritize critical files (security, core logic)
2. Group related changes
3. Provide summary-level feedback
4. Offer to deep-dive specific files

### Generated Code

For auto-generated code (migrations, builds, etc):
1. Verify generator correctness
2. Don't nitpick style in generated files
3. Focus on configuration that drove generation

## Integration with Development Workflow

After completing the review:

1. **Generate comprehensive report file** - Always create a markdown report
2. **Provide user summary** - Show key findings in terminal
3. **Clear verdict** - LGTM | Needs Changes | Blocked
4. **Highlight critical items** - Call out must-fix issues
5. **Report location** - Tell user where report was saved
6. **Offer next steps** - Create issues, follow-up reviews, etc.

**User Communication Template:**

**IMPORTANT**: DO NOT include time estimates, fix time estimates, and so in the terminal output. These are reviews, not plans. Only provide issue counts and severity levels.

```
✅ Code review complete!
📄 Report saved to: CODE-REVIEW-REPORT-2025-11-14-[commit-hash].md

📊 Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Files Reviewed: X files
Lines Changed: +XXX -XXX
Issues Found: X total

🚨 Critical: X (Must fix immediately)
🔴 High: X (Fix before production)
⚠️ Medium: X (Technical debt)
ℹ️ Low: X (Nice to have)
✅ Strengths: X+ best practices identified

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Grade: [A+/A/A-/B+/B/C/F]
Verdict: [LGTM / Needs Changes / Blocked]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[If issues found:]
⚠️ Top Priority Items:
1. [Issue title] - file.ext:line
2. [Issue title] - file.ext:line

📖 Full details in the report file.
```

**Note**: Add JSON output lines only when user explicitly requests JSON generation:
```
📊 JSON output: CODE-REVIEW-REPORT-2025-11-14-[commit-hash].json
✓ JSON validation passed
```

**DO NOT add any of the following to terminal output:**
- ❌ NO "Estimated Fix Time"
- ❌ NO "Critical Fixes Time"
- ❌ NO time/hour estimates

This is a code REVIEW, not a project plan. Focus on identifying issues, not estimating time.

## Progressive Disclosure

For detailed reference:
- **Security Patterns**: See [PATTERNS.md](PATTERNS.md)
- **Usage Examples**: See [EXAMPLES.md](EXAMPLES.md)
- **User Documentation**: See [README.md](README.md)

Claude will automatically load these files when needed for deeper analysis.
