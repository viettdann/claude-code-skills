# Code Reviewer Skill

Expert code review skill for Claude Code that automatically reviews code for quality, security, and best practices.

## Overview

The Code Reviewer skill provides professional-grade code reviews focusing on:

- **Security Vulnerabilities**: SQL injection, XSS, command injection, hardcoded secrets
- **Code Quality**: Readability, maintainability, error handling, type safety
- **Best Practices**: Framework conventions, architecture patterns, SOLID principles
- **Performance**: Inefficient algorithms, N+1 queries, resource management

## Features

### Automatic Activation

Skill activates automatically when:
- Code changes or commits are made
- User mentions "review", "commit", or "merge"
- After significant code modifications
- Explicit code review request

### Comprehensive Analysis

Reviews include:
- Latest commit analysis (including merge commits)
- File-by-file detailed review
- Severity-classified findings (Critical, High, Medium, Low)
- Actionable fixes with before/after code examples
- Framework-specific best practices

### Multi-Language Support

Supports code review for:
- JavaScript/TypeScript (React, Next.js, Node.js)
- C#/.NET (ABP Framework, Entity Framework)
- Python
- Java
- Go
- And more...

### Automatic Report Generation

**NEW**: Skill automatically generates comprehensive markdown reports for every review.

**Features:**
- **Detailed documentation** - Complete review saved as markdown file
- **Professional format** - Executive summary, severity-classified issues, actionable fixes
- **Persistent reference** - Reports serve as audit trail for tracking progress
- **Shareable** - Easy to share with team or include in PR discussions
- **Comprehensive structure** - Includes Quick Stats, Priority Roadmap, Immediate Actions

**Report Filenames:**
- `CODE-REVIEW-REPORT-2025-01-13.md` (general reviews, no commit)
- `CODE-REVIEW-REPORT-2025-01-13-abc1234.md` (commit-specific reviews)
- `SECURITY-AUDIT-REPORT-2025-01-13.md` (security-focused audits)

See [REPORT-TEMPLATE.md](REPORT-TEMPLATE.md) for complete report structure.

### JSON Output for PR Automation

**NEW**: Skill generates machine-readable JSON output alongside markdown reports.

**Generated Files:**
- `CODE-REVIEW-REPORT-2025-01-13.md` (human-readable markdown)
- `CODE-REVIEW-REPORT-2025-01-13.json` (machine-readable JSON, compact format)

**Use Cases:**
- **Automated PR Comments** - Post inline comments on specific lines of code
- **CI/CD Integration** - Block merges based on severity or production readiness
- **Custom Dashboards** - Track code quality metrics over time
- **AI Review Bots** - Build GitHub/GitLab bots that act like human reviewers

**JSON Includes:**
- Complete issue details with file paths and line numbers
- Severity levels and priorities
- Recommended fixes with code examples
- Production readiness flag for merge gates
- Metrics and grades for tracking trends

**Format:** JSON output uses compact format (no pretty-printing) to minimize file size for CI/CD systems and reduce token usage when parsed.

**Documentation:** See [SCHEMA.md](SCHEMA.md) for complete JSON schema and structure details.

## Usage

### Basic Usage

Ask Claude to review code:

```
Review my latest commit
```

```
Can you review the code I just changed?
```

```
Review this merge commit for issues
```

### Review Specific Commits

```
Review commit abc123
```

```
Review the last 3 commits
```

### Focus on Specific Aspects

```
Review my code for security vulnerabilities
```

```
Check my code for performance issues
```

```
Review this code for React best practices
```

## Review Output

### Report File Generation

Skill automatically creates comprehensive markdown report file for every review.

Report saved in project root with filename format:
- `CODE-REVIEW-REPORT-2025-01-13.md` (general reviews)
- `CODE-REVIEW-REPORT-2025-01-13-abc1234.md` (commit-specific reviews)
- `SECURITY-AUDIT-REPORT-2025-01-13.md` (security audits)

### Report Structure

Each generated report includes:

1. **📊 Executive Summary**: Overall assessment, grade, key highlights
2. **📋 Quick Stats Table**: Security, Performance, Code Quality status
3. **🚨 Critical Issues**: Security vulnerabilities, must-fix blockers
4. **🔴 High Priority Issues**: Bugs, major problems, architectural violations
5. **⚠️ Medium Priority Issues**: Code quality improvements, technical debt
6. **ℹ️ Low Priority Issues**: Style suggestions, minor optimizations
7. **✅ Strengths & Best Practices**: What the code does well (5-10 examples)
8. **📋 Summary & Priority Roadmap**: Issue distribution, fix order prioritization
9. **🎯 Recommended Immediate Actions**: Step-by-step fix guide with code
10. **📚 References & Resources**: Links to documentation, OWASP, framework guides
11. **🎬 Conclusion**: Final verdict, production readiness, next steps
12. **📌 Appendix**: Quick reference links to all issues

### Issue Format

Each issue includes:
- **File and line number**: Exact location
- **Category**: Security, Performance, Correctness, etc.
- **Problem**: Clear description
- **Impact**: What could go wrong
- **Fix**: Before/after code examples
- **References**: Links to documentation

### Example Output

```markdown
### [CRITICAL] SQL Injection Vulnerability
**File**: `src/api/users.ts:45`
**Category**: Security
**Problem**: User input directly concatenated into SQL query
**Impact**: Attackers can execute arbitrary SQL commands

**Fix**:
```typescript
// ❌ Current (vulnerable)
const query = `SELECT * FROM users WHERE id = ${userId}`;

// ✅ Recommended (parameterized)
const query = 'SELECT * FROM users WHERE id = ?';
db.execute(query, [userId]);
```

**References**: https://owasp.org/www-community/attacks/SQL_Injection
```

## Configuration

### Installation

**As Project Skill** (shared with team):
```bash
# Copy to your project
cp -r code-reviewer /path/to/your/project/.claude/skills/

# Commit to git
git add .claude/skills/code-reviewer/
git commit -m "skills: add code-reviewer"
git push
```

**As Personal Skill** (just for you):
```bash
# Copy to your personal skills
cp -r code-reviewer ~/.claude/skills/
```

### Allowed Tools

Skill uses these tools:
- `Bash`: Git operations, commit analysis
- `Read`: Read file contents
- `Grep`: Pattern-based detection
- `Glob`: Find related files
- `Task`: Complex codebase exploration
- `Write`: Generate report files

## Best Practices

### When to Use

- **Before Merging**: Review PRs before merging to main
- **After Features**: Review feature branches before integration
- **After Refactoring**: Verify refactoring didn't introduce issues
- **Security Audits**: Regular security-focused reviews
- **Learning**: Understand best practices for your codebase

### Workflow Integration

1. Make code changes
2. Commit code
3. Ask for review: "Review my latest commit"
4. Address critical issues immediately
5. Fix high priority issues before merge
6. Plan medium/low issues for future iterations

### Getting the Most Value

- Review frequently to catch issues early
- Act on critical issues immediately
- Learn from feedback to understand why issues matter
- Ask questions if findings are unclear
- Apply learnings to future code

## Severity Levels

### Critical
Security vulnerabilities, data corruption, crashes. **Must fix before merge**.

Examples:
- SQL injection
- XSS vulnerabilities
- Authentication bypass
- Data corruption risks

### High
Bugs, major performance issues, architectural violations. **Should fix before merge**.

Examples:
- Memory leaks
- Incorrect business logic
- N+1 query problems
- Significant performance issues

### Medium
Code quality issues, minor performance problems. **Address soon**.

Examples:
- Code duplication
- Missing error handling
- Inefficient algorithms
- Architecture deviations

### Low
Style issues, minor optimizations. **Nice to have**.

Examples:
- Naming improvements
- Comment additions
- Minor refactoring opportunities

## Language/Framework Support

### JavaScript/TypeScript
- React hooks rules
- Next.js best practices (App Router, Server Actions)
- Node.js security
- TypeScript type safety
- State management patterns

### C#/.NET
- ABP Framework conventions
- Entity Framework best practices
- Async/await patterns
- Dependency injection
- SOLID principles

### Python
- PEP 8 compliance
- Type hints
- Context managers
- Pythonic idioms

### Other Languages
- Language-specific conventions
- Framework best practices
- Security considerations

## Advanced Usage

### Review Merge Commits

```
Review the merge commit for integration issues
```

Skill will:
- Check conflict resolution
- Verify integration correctness
- Identify regression risks
- Review consistency

### Review Specific Files

```
Review src/components/Auth.tsx for security issues
```

### Comparative Reviews

```
Compare the current code against the previous commit
```

## Troubleshooting

### Skill Not Activating

1. **Check description matches**: Mention "review", "commit", or "code quality"
2. **Verify installation**: Check `.claude/skills/code-reviewer/SKILL.md` exists
3. **Restart Claude Code**: Changes require restart to take effect

### Too Many False Positives

Skill reads full context to minimize false positives. If encountering false positives:
- Mention framework/conventions upfront
- Provide context: "This is test code" or "This is a migration file"
- Request focused review: "Review only security issues"

### Review Too Broad

For large commits:
- Request focused review: "Review only the authentication logic"
- Ask for summary: "Give me a high-level review"
- Review specific files: "Review src/auth/* files only"

## Examples

See [EXAMPLES.md](EXAMPLES.md) for detailed usage examples.

## Technical Reference

See [PATTERNS.md](PATTERNS.md) for security and quality detection patterns used by the skill.

## Contributing

To enhance this skill:

1. **Update SKILL.md**: Add new review dimensions or patterns
2. **Update PATTERNS.md**: Add new grep patterns for detection
3. **Update EXAMPLES.md**: Add new usage examples
4. **Test**: Verify changes with real code reviews

## Support

For issues or questions:
- Check [EXAMPLES.md](EXAMPLES.md) for usage patterns
- Review [PATTERNS.md](PATTERNS.md) for detection logic
- See [SKILL.md](SKILL.md) for technical implementation

## Version

- **Version**: 1.0.0
- **Last Updated**: 2025-01-13
- **Compatible With**: Claude Code 1.0+

## License

This skill follows your project's license terms.
