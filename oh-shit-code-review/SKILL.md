---
name: oh-shit-code-review
description: Reviews git diffs for critical security vulnerabilities, data leaks, and breaking changes in Next.js and .NET C# (ABP Framework) code. Use when reviewing commits, diffs, or before merging code. Only reports severe "oh-shit" level issues that warrant immediate attention.
allowed-tools: [Read, Grep, Glob, Bash, Write]
---

# Oh-Shit Code Review

Critical issue detector for git commits targeting Next.js and .NET C# (ABP Framework) codebases.

## Purpose

Catch severe security vulnerabilities, data leaks, and breaking changes before they reach production. This skill focuses exclusively on "oh-shit" level issues—problems that warrant immediate attention and could cause production incidents, security breaches, or data loss.

## Activation Triggers

Use this skill when:
- Reviewing git commits before merge
- Analyzing git diffs for security issues
- Pre-merge code review for critical changes
- User mentions: "review commit", "check diff", "scan changes", "review code"

## Model Selection

IMPORTANT: Always use the **Haiku model** for this skill to ensure:
- Fast execution
- Cost-effective scanning
- Consistent results with temperature: 0

## Core Principles

1. **High Precision, Low Recall**: Miss an issue rather than create false positives
2. **Critical Issues Only**: Never report style, tests, minor bugs, or subjective quality
3. **Confidence-Based Filtering**: Only report findings with ≥75 confidence score
4. **Context-Aware**: Use git history to understand intent and avoid false positives
5. **Fast Detection**: Identify issues quickly - let developers handle the fixes

## Execution Workflow

### Step 1: Get Git Diff

Use Bash to retrieve git diff:

```bash
# Get diff for staged changes
git diff --cached

# Or get diff for specific commit
git diff <commit-hash>^..<commit-hash>

# Or get diff between branches
git diff main..feature-branch
```

If user doesn't specify, default to `git diff --cached` (staged changes).

**Edge case**: If diff is >10,000 lines, output:
```markdown
# Code Review Report

## Summary
- **Result**: DIFF_TOO_LARGE
- **Recommendation**: Break into smaller commits or review manually
```

### Step 2: Identify Changed Files

Parse git diff output to extract:
- File paths
- Change type (added, modified, deleted)
- Language/framework (Next.js vs .NET C#)

**Next.js indicators**:
- Extensions: `.tsx`, `.ts`, `.jsx`, `.js`
- Directories: `app/`, `pages/`, `components/`, `lib/`, `src/`
- Config files: `next.config.js`, `next.config.ts`
- Environment: `.env`, `.env.local`, `.env.production`

**.NET C# (ABP Framework) indicators**:
- Extensions: `.cs`
- Directories: `*.Application/`, `*.Domain/`, `*.EntityFrameworkCore/`, `*.HttpApi/`, `*.Web/`
- Config files: `appsettings.json`, `appsettings.*.json`
- Project files: `*.csproj`

### Step 3: Scan for Critical Issues

For each changed file, scan ONLY for critical issues defined in [PATTERNS.md](PATTERNS.md).

**Never skip security-critical files** regardless of name:
- `auth*`, `security*`, `payment*`, `credential*`
- Files with passwords, tokens, keys

#### Next.js Critical Issues

**Security vulnerabilities**:
- `dangerouslySetInnerHTML` without DOMPurify/sanitization
- Hardcoded API keys/tokens/secrets in client code
- `.env*` files with actual secrets (not `.env.example`)
- Exposed admin routes without auth check
- `eval()` or `new Function()` usage
- Disabled security headers: `contentSecurityPolicy: false`, `X-Frame-Options` removed

**Breaking changes**:
- Deleted/renamed public API routes (`/api/*` in `pages/` or `app/`)
- Changed route parameters in `app/` or `pages/`
- Removed required environment variables other services depend on
- Breaking changes in shared component props

**Data leaks**:
- Server-side secrets in client components (`'use client'` with `process.env`)
- Database queries in client components
- API keys exposed in `getStaticProps`/`getServerSideProps` return values

#### .NET C# (ABP Framework) Critical Issues

**Security vulnerabilities**:
- SQL concatenation: `$"SELECT * FROM {table}"` without parameterization
- `[AllowAnonymous]` on sensitive endpoints (payment, admin, user data)
- Hardcoded connection strings with real passwords
- Disabled HTTPS enforcement: `UseHttpsRedirection()` removed
- Raw password storage without hashing
- Exposed internal APIs without `[Authorize]`
- Disabled CSRF: `ValidateAntiForgeryToken = false`
- File upload without validation/size limits

**ABP Framework-specific**:
- Bypassing permission system: Removed `[Authorize(PermissionName)]`
- Disabled audit logging: `[DisableAuditing]` on sensitive operations
- Direct `DbContext` usage breaking multi-tenancy
- Removed `[UnitOfWork]` where transactions required

**Breaking changes**:
- Deleted/renamed DTOs in `*.Application.Contracts`
- Breaking database migrations (column deletion without data migration)
- Removed required config keys from `appsettings.json`
- Changed API endpoint routes or HTTP methods

**Data exposure**:
- Removed multi-tenant filtering: Removed `IMultiTenant` interface
- Exposed internal DTOs directly without mapping
- Disabled soft-delete filtering: `IgnoreQueryFilters()`

### Step 4: Confidence Scoring

For each potential finding, assign confidence score (0-100):

**Confidence Score Guidelines**:
- **0 (False positive)**: Pattern match but context shows it's safe
  - Example: `dangerouslySetInnerHTML` but DOMPurify is imported and used
- **25 (Uncertain)**: Might be real but can't verify without more context
  - Example: Environment variable might be secret or might be public URL
- **50 (Real but minor)**: Real issue but low impact
  - Example: `console.log` with user data in dev-only code
- **75 (Real and important)**: Confirmed issue with significant impact
  - Example: API key hardcoded in client code
- **100 (Critical)**: Definitely real, immediate security/production risk
  - Example: Hardcoded production database password in commit

**Scoring factors**:
- Pattern match strength
- Context from surrounding code
- Git history (new code vs pre-existing)
- Framework-specific conventions
- File location (client vs server)

### Step 5: Git History Context

IMPORTANT: Check git history to avoid false positives and understand intent.

For each finding, use Bash to check:

```bash
# Who wrote this code and when
git blame <file> -L <line_start>,<line_end>

# Change history for this file
git log --oneline -n 5 -- <file>

# Full context of this change
git diff HEAD~1..HEAD -- <file>
```

**Use history to**:
- Identify if this is new code or pre-existing (only flag new issues)
- Understand developer intent from commit messages
- Detect patterns (repeated issues by same author)
- Avoid flagging framework boilerplate or generated code

### Step 6: Filter and Deduplicate

**Filtering rules**:
1. Remove findings with confidence < 75
2. Remove findings in files marked as generated (`// Auto-generated`)
3. Remove findings in dependencies (`node_modules/`, `bin/`, `obj/`)
4. Remove findings in test files UNLESS they test security (auth, encryption)

**Deduplication**:
- Same issue flagged multiple times? Keep highest confidence version
- Merge evidence from multiple detections
- Group related findings (e.g., multiple secrets in same file)

### Step 7: Re-sort by Priority

Sort findings by: `(confidence × severity_weight)`

**Severity weights**:
- CRITICAL: 10
- HIGH: 5

Example: 75 confidence × 10 (CRITICAL) = 750 priority score

### Step 8: Generate Report

Use the strict markdown template below. **Do not deviate from this format**.

**Keep it concise** - this is a fast review for issue detection, not comprehensive remediation guidance.

```markdown
# Code Review Report

## Summary
- **Result**: CRITICAL_ISSUES_FOUND | NO_CRITICAL_ISSUES
- **Files Scanned**: [count]
- **Critical Issues**: [count]

## Critical Issues

### [ISSUE_TYPE]
- **File**: `path/to/file.ext:line_number`
- **Severity**: CRITICAL | HIGH
- **Confidence**: [0-100]
- **Problem**: [1-2 sentence - what's wrong]
- **Why Critical**: [1-3 sentence - immediate risk]
- **Code Snippet**:

```[language]
[relevant code snippet - 8 lines max]
```
- **Git Context**: [who/when/why from git blame/log]

---

[Repeat for each issue]

## Scan Coverage
- **Next.js files reviewed**: [count]
- **.NET C# files reviewed**: [count]
- **Total changed lines**: [count]
- **False positives filtered**: [count]
```

**If NO_CRITICAL_ISSUES:**
```markdown
# Code Review Report

## Summary
- **Result**: NO_CRITICAL_ISSUES
- **Files Scanned**: [count]

No critical security vulnerabilities, data leaks, or breaking changes detected.

## Scan Coverage
- **Next.js files reviewed**: [count]
- **.NET C# files reviewed**: [count]
- **Total changed lines**: [count]
- **False positives filtered**: [count]
```

### Step 9: Save Report to File

IMPORTANT: After generating the report, automatically save it to a markdown file using the Write tool.

**Filename format**: `oh-shit-{branch-name}-{YYYY-MM-DD}-{short-hash}.md`

**Steps to create filename:**

1. Get git information using Bash:
   ```bash
   # Get current branch name
   git rev-parse --abbrev-ref HEAD

   # Get current date
   date +%Y-%m-%d

   # Get short commit hash (7 chars)
   git rev-parse --short=7 HEAD
   ```

2. Sanitize branch name for filesystem:
   - Replace `/` with `-` (e.g., `deploy/dev` → `deploy-dev`)
   - Replace spaces with `-`
   - Remove special characters: `*`, `?`, `<`, `>`, `|`, `:`, `\`, `"`
   - Convert to lowercase

3. Construct filename:
   ```
   {sanitized-branch}-{YYYY-MM-DD}-{hash}.md
   ```

   **Examples**:
   - `oh-shit-main-2025-11-17-a1b2c3d.md`
   - `oh-shit-deploy-dev-2025-11-17-abc1234.md`
   - `oh-shit-feat-payment-2025-11-17-def5678.md`

4. Write report to file using Write tool:
   - Use absolute path: `{current-working-directory}/{filename}`
   - Content: The markdown report generated in Step 8

5. Output confirmation:
   ```
   Report saved to: {filename}
   ```

**Edge cases**:

- **Detached HEAD state**: Use commit hash as branch name (e.g., `oh-shit-detached-a1b2c3d-2025-11-17-a1b2c3d.md`)
- **Long branch names**: Truncate to 50 chars max before adding date/hash
- **File already exists**: Append timestamp in seconds to ensure uniqueness (e.g., `oh-shit-main-2025-11-17-a1b2c3d-1737123456.md`)

## Output Requirements

**Always include**:
1. Exact file paths with line numbers
2. Confidence score for each finding
3. Brief problem statement (1-2 sentence)
4. Why it's critical (1-3 sentence)
5. Minimal code snippet (8 lines max)

**Never include**:
- Fixed code examples or detailed remediation steps
- Long explanations or advisory content
- Style issues (formatting, naming conventions)
- Missing tests or documentation
- TODOs or console.logs (unless security-related)
- Minor type issues
- Subjective code quality opinions
- Anything below 75 confidence

**Remember**: Fast detection - let developers handle the fixes.

## Edge Cases

**Large diffs (>10,000 lines)**:
- Return "DIFF_TOO_LARGE" result
- Recommend breaking into smaller commits

**Unrecognized file types**:
- Skip silently
- Don't report "unknown file type"

**Uncertain severity**:
- DO NOT report
- Better to miss than false alert

**Generated code**:
- Skip files with `// Auto-generated` or similar markers
- Skip migration files generated by ABP CLI
- Skip Next.js build output

**Test files**:
- Skip test files UNLESS testing security (auth, encryption, permissions)
- Security test changes ARE critical

## Examples

See [examples/](examples/) directory for sample reports:
- `example-nextjs-critical.md` - Next.js security findings
- `example-dotnet-critical.md` - .NET C# security findings
- `example-no-issues.md` - Clean diff report

## Anti-Patterns to Avoid

❌ **Don't do this**:
- Provide fixed code examples
- Give detailed remediation steps
- Act as advisor with "you should..." guidance
- Report style issues or minor problems
- Write long explanations

✅ **Do this**:
- Identify the critical issue quickly
- State the problem in 1-2 sentence
- State why it's critical in 1-3 sentence
- Show minimal code snippet (8 lines max)
- Let developers handle the fix

## Validation Checklist

Before completing the review, verify:
- [ ] All findings have confidence ≥ 75
- [ ] All findings are CRITICAL or HIGH severity only
- [ ] Each finding has file:line reference
- [ ] No fixed code examples included
- [ ] No detailed remediation steps
- [ ] Report is concise and fast to read
- [ ] Template format followed exactly
- [ ] Deduplication performed
- [ ] Report saved to file with correct naming format
- [ ] File path confirmation output to user

## References

- Detection patterns: [PATTERNS.md](PATTERNS.md)
- Example reports: [examples/](examples/)
- ABP Framework Security: https://docs.abp.io/en/abp/latest/Authorization
- Next.js Security: https://nextjs.org/docs/app/building-your-application/configuring/content-security-policy
- OWASP Top 10: https://owasp.org/www-project-top-ten/
