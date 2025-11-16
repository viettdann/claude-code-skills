# Oh-Shit Code Review

Critical issue detector for git commits targeting Next.js and .NET C# (ABP Framework) codebases.

## What is This?

An Agent Skill that automatically reviews your git diffs for severe "oh-shit" level issues:
- 🔒 **Security vulnerabilities** (SQL injection, XSS, exposed secrets)
- 💥 **Breaking changes** (deleted APIs, changed routes, removed DTOs)
- 🔓 **Data leaks** (secrets in client code, multi-tenant violations)

**Philosophy**: Fast detection, not comprehensive fixes. We identify "oh-shit" problems and let developers handle the solutions.

**What it doesn't do**:
- Provide fixed code or detailed remediation
- Report style issues, missing tests, or minor bugs
- Act as code quality advisor

## Quick Start

### Prerequisites

- Claude Code (v1.0+)
- Git repository with commits to review
- Next.js and/or .NET C# (ABP Framework) codebase

### Installation

**Option 1: Project Skill (Shared with Team)**
```bash
# Clone or copy this skill to your project
mkdir -p .claude/skills
cp -r oh-shit-code-review .claude/skills/

# Commit to share with team
git add .claude/skills/oh-shit-code-review
git commit -m "Add oh-shit-code-review skill"
```

**Option 2: Personal Skill (Just for You)**
```bash
# Copy to personal skills directory
mkdir -p ~/.claude/skills
cp -r oh-shit-code-review ~/.claude/skills/
```

### Usage

Simply ask Claude to review your code changes:

```
"Review my staged changes for critical issues"
"Check this commit for security problems"
"Scan the diff for oh-shit level bugs"
"Review PR #123 for breaking changes"
```

Claude will automatically activate this skill and generate a report.

**Report Output**:
- Displays findings in Claude Code interface
- **Auto-saves** to markdown file: `oh-shit-{branch-name}-{YYYY-MM-DD}-{commit-hash}.md`
- Saved in current working directory
- **Prefixes** all filenames with `oh-shit-` for easy identification
- **Ensures** dashed branch names are properly formatted (e.g., `deploy/dev` -> `deploy-dev`)

**Example filenames**:
- `oh-shit-main-2025-11-17-a1b2c3d.md`
- `oh-shit-deploy-dev-2025-11-17-abc1234.md`
- `oh-shit-feat-payment-2025-11-17-def5678.md`

### Example Workflow

```bash
# Stage your changes
git add .

# Ask Claude to review
# In Claude Code: "Review my staged changes"

# Claude generates report with critical findings
# Report auto-saved to: oh-shit-feat-payment-2025-11-17-def5678.md

# Fix issues
# Commit when clean
git commit -m "fix: address security issues"
```

## What Gets Flagged

### Next.js Critical Issues

**Security Vulnerabilities**:
- ✅ `dangerouslySetInnerHTML` without sanitization
- ✅ Hardcoded API keys/tokens in client code
- ✅ `.env` files with real secrets in commits
- ✅ Admin routes without authentication
- ✅ `eval()` or `Function()` constructor usage
- ✅ Disabled security headers in `next.config.js`

**Breaking Changes**:
- ✅ Deleted/renamed public API routes (`/api/*`)
- ✅ Changed route parameters in `app/` or `pages/`
- ✅ Removed environment variables

**Data Leaks**:
- ✅ Server secrets in client components (`'use client'`)
- ✅ Database queries in client components
- ✅ API keys exposed in `getStaticProps`/`getServerSideProps`

### .NET C# (ABP Framework) Critical Issues

**Security Vulnerabilities**:
- ✅ SQL concatenation without parameterization
- ✅ `[AllowAnonymous]` on sensitive endpoints
- ✅ Hardcoded connection strings/passwords
- ✅ Disabled HTTPS enforcement
- ✅ Raw password storage
- ✅ File uploads without validation

**ABP-Specific Issues**:
- ✅ Bypassed permission system (missing `[Authorize]`)
- ✅ Disabled audit logging on sensitive operations
- ✅ Direct `DbContext` usage breaking multi-tenancy
- ✅ Missing `[UnitOfWork]` on transactions

**Breaking Changes**:
- ✅ Deleted/renamed DTOs in `*.Application.Contracts`
- ✅ Breaking database migrations
- ✅ Removed required config keys
- ✅ Changed API endpoints

**Data Exposure**:
- ✅ Removed multi-tenant filtering (`IMultiTenant`)
- ✅ Exposed internal DTOs without mapping
- ✅ Disabled soft-delete filtering

## Report Format

The skill generates a **concise** markdown report that is both displayed in Claude Code and **automatically saved to a file**.

**Report filename**: `oh-shit-{branch-name}-{YYYY-MM-DD}-{commit-hash}.md`
- Saved in current working directory
- Branch name sanitized for filesystem (slashes → dashes)
- Short commit hash (7 characters)
- Date in ISO format (YYYY-MM-DD)

**Example report content**:

```markdown
# Code Review Report

## Summary
- **Result**: CRITICAL_ISSUES_FOUND | NO_CRITICAL_ISSUES
- **Files Scanned**: 15
- **Critical Issues**: 2

## Critical Issues

### Hardcoded API Key in Client Component
- **File**: `app/components/Analytics.tsx:23`
- **Severity**: CRITICAL
- **Confidence**: 100
- **Problem**: API key hardcoded in client component
- **Code Snippet**: [relevant code]
- **Why Critical**: Secret exposed in browser, attackers can extract and abuse
- **Git Context**: Added by john@example.com on 2025-01-15

---

[Additional issues...]

## Scan Coverage
- **Next.js files reviewed**: 8
- **.NET C# files reviewed**: 7
- **Total changed lines**: 342
```

**Key principles**:
- No fixed code examples
- No detailed remediation steps
- Fast detection only - developers handle the fixes
- Reports archived for team reference and audit trail

## Configuration

### Confidence Threshold

The skill only reports findings with confidence ≥ 75:
- **100**: Definitely real and critical (e.g., hardcoded production password)
- **90**: Very high confidence (e.g., missing auth on sensitive endpoint)
- **75**: High confidence - threshold for reporting
- **50**: Medium - not reported
- **25**: Low - not reported
- **0**: False positive - not reported

### Severity Levels

Only **CRITICAL** and **HIGH** severity issues are reported:
- **CRITICAL**: Security vulnerabilities, data leaks, production risks
- **HIGH**: Breaking changes, significant impact

Not reported:
- **MEDIUM**: Code duplication, minor inefficiencies
- **LOW**: Style issues, minor optimizations

## Advanced Usage

### Review Specific Commit

```
"Review commit abc123 for critical issues"
```

Claude will run: `git diff abc123^..abc123`

### Review Branch vs Main

```
"Review feature-branch against main for security issues"
```

Claude will run: `git diff main..feature-branch`

### Review Specific Files

```
"Check app/api/payment/route.ts for security vulnerabilities"
```

Claude will focus on that specific file in the diff.

### Custom Scope

```
"Review my changes but only check for SQL injection and secrets"
```

Claude will filter patterns to match your request.

## Troubleshooting

### Skill Not Activating

**Symptoms**: Claude doesn't use the skill when reviewing code.

**Solutions**:
1. Check skill is installed:
   ```bash
   ls .claude/skills/oh-shit-code-review/SKILL.md
   # or
   ls ~/.claude/skills/oh-shit-code-review/SKILL.md
   ```

2. Restart Claude Code to reload skills

3. Use activation keywords: "review commit", "check diff", "scan changes"

4. Verify YAML frontmatter is valid:
   ```bash
   head -n 6 .claude/skills/oh-shit-code-review/SKILL.md
   ```

### Too Many False Positives

**Symptoms**: Skill reports issues that aren't real problems.

**Solutions**:
1. Check git history is being used (should show in report under "Git Context")
2. Review confidence scores - should all be ≥ 75
3. Update PATTERNS.md to exclude false positive patterns
4. File an issue with example false positive

### Missing Real Issues

**Symptoms**: Skill doesn't catch a critical issue you know exists.

**Solutions**:
1. Check if issue is in supported categories (see "What Gets Flagged")
2. Review PATTERNS.md to see if detection pattern exists
3. Add new pattern to PATTERNS.md if missing
4. File an issue with example missed issue

### Diff Too Large Error

**Symptoms**: Report shows "DIFF_TOO_LARGE".

**Solutions**:
- Break commit into smaller logical chunks
- Review files individually
- Use `git add -p` for partial staging

## Performance

- **Fast**: Uses Haiku model for quick analysis
- **Cost-effective**: Only loads context when needed
- **Scalable**: Handles diffs up to 10,000 lines

Typical scan times:
- Small commit (1-5 files): ~5 seconds
- Medium commit (5-20 files): ~15 seconds
- Large commit (20-50 files): ~30 seconds

## Contributing

### Adding New Detection Patterns

1. Edit `PATTERNS.md` with new grep pattern
2. Document validation steps
3. Set confidence threshold
4. Test on real examples
5. Commit changes

### Improving Accuracy

1. Review false positives in your commits
2. Update validation logic in `SKILL.md`
3. Add exclusion patterns to `PATTERNS.md`
4. Share improvements with team

### Framework Updates

When Next.js or ABP Framework updates:
- Review changelog for new security features
- Update patterns for deprecated APIs
- Add patterns for new vulnerability types

## Examples

See `examples/` directory for sample reports:
- `example-nextjs-critical.md` - Next.js security findings
- `example-dotnet-critical.md` - .NET C# security findings
- `example-no-issues.md` - Clean diff report

## Resources

**Official Documentation**:
- ABP Framework Security: https://docs.abp.io/en/abp/latest/Authorization
- Next.js Security: https://nextjs.org/docs/app/building-your-application/configuring/content-security-policy
- OWASP Top 10: https://owasp.org/www-project-top-ten/

**Skill Documentation**:
- Detection Patterns: [PATTERNS.md](PATTERNS.md)
- Skill Instructions: [SKILL.md](SKILL.md)
- Example Reports: [examples/](examples/)

## Version History

- **v1.1.0** (2025-11-17): Auto-save reports
  - **NEW**: Automatic markdown report file generation
  - Filename format: `oh-shit-{branch-name}-{YYYY-MM-DD}-{commit-hash}.md`
  - Reports saved to current working directory
  - Edge case handling (detached HEAD, long branch names, file conflicts)

- **v1.0.0** (2025-11-17): Initial release
  - Next.js security scanning
  - .NET C# (ABP Framework) security scanning
  - Confidence-based filtering
  - Git history context
  - Breaking change detection

## License

This skill follows the same license as your project.

## Support

- Report issues in project repository
- Review PATTERNS.md for detection logic
- Check examples/ for expected output format
- Consult official framework security docs
