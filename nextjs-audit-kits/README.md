# Next.js Kits

Comprehensive Next.js toolkit for performance optimization, security auditing, debugging, and code optimization. Works with both App Router (Next.js 13+) and Pages Router applications.

## Features

- 🚀 **Performance Optimization** - Bundle analysis, rendering optimization, caching, image/font optimization
- 🔒 **Security Auditing** - XSS prevention, CSRF protection, Server Actions security, API route security
- 🐛 **Debugging Assistance** - Hydration errors, TypeScript issues, build/runtime errors
- ⚡ **Code Optimization** - Component optimization, data fetching, SEO, accessibility, TypeScript best practices

## Installation

### For Project Skills (Team Sharing)

```bash
# Copy to project .claude/skills directory
mkdir -p .claude/skills
cp -r nextjs-kits .claude/skills/

# Commit to share with team
git add .claude/skills/nextjs-kits
git commit -m "skills: add nextjs-kits"
git push
```

### For Personal Skills

```bash
# Copy to personal skills directory
mkdir -p ~/.claude/skills
cp -r nextjs-kits ~/.claude/skills/
```

### Verify Installation

Ask Claude Code:
```
What skills are available?
```

You should see `nextjs-kits` listed.

## Usage

The skill activates automatically when you ask questions related to Next.js performance, security, debugging, or optimization.

### Trigger Examples

**Performance:**
- "Analyze my Next.js app for performance issues"
- "Why is my bundle size so large?"
- "How can I improve my Core Web Vitals?"
- "Check my caching strategy"

**Security:**
- "Audit my Next.js app for security vulnerabilities"
- "Check my Server Actions for security issues"
- "Scan for XSS vulnerabilities"
- "Review my API routes for security"

**Debugging:**
- "Help me fix this hydration error"
- "Debug this TypeScript error in my Next.js app"
- "Why is my page not rendering?"
- "Find issues causing runtime errors"

**Optimization:**
- "Optimize my Next.js components"
- "Improve SEO for my Next.js site"
- "Check data fetching patterns"
- "Review accessibility in my app"

## Quick Start

### 1. Full Analysis

```
Analyze my Next.js app for performance, security, and optimization issues
```

Claude will:
1. Explore your codebase structure
2. Run comprehensive scans for all issue types
3. Validate findings with context
4. Generate prioritized report with fixes

### 2. Specific Category

```
Scan my Next.js app for security vulnerabilities
```

Claude will focus on security-specific patterns and provide detailed remediation.

### 3. Standalone Scripts (Optional)

Quick pattern-based scans without AI:

```bash
# Run all scans
python3 .claude/skills/nextjs-kits/scripts/scan-all.py

# Individual scans
python3 .claude/skills/nextjs-kits/scripts/scan-performance.py
python3 .claude/skills/nextjs-kits/scripts/scan-security.py
python3 .claude/skills/nextjs-kits/scripts/scan-debug.py
```

See [scripts/README.md](scripts/README.md) for detailed script documentation.

## What Gets Analyzed

### Performance
- **Bundle Size**: Large dependencies, unnecessary imports, missing tree-shaking
- **Rendering**: Blocking renders, inefficient hydration, missing Suspense
- **Caching**: Fetch configuration, React cache usage, revalidation strategies
- **Images**: Unoptimized images, missing dimensions, wrong formats
- **Fonts**: Unoptimized font loading
- **Code Splitting**: Missing dynamic imports for heavy components

### Security
- **XSS Prevention**: dangerouslySetInnerHTML, unsanitized input, template literals
- **Server Actions**: Missing validation, missing authorization
- **API Routes**: CSRF protection, rate limiting, input validation
- **Environment Variables**: Exposed secrets, improper NEXT_PUBLIC_ usage
- **SQL Injection**: Template literal SQL queries
- **Authentication**: Missing auth checks, insecure session handling

### Debugging
- **Hydration Errors**: Date/time mismatches, window/document access, client/server state
- **TypeScript Issues**: Any types, @ts-ignore, missing types
- **Server Components**: Client hooks in server components, browser API usage
- **Runtime Errors**: Missing error handling, null references
- **Build Errors**: Configuration issues, module resolution

### Optimization
- **Components**: Missing memo, useMemo, useCallback
- **Data Fetching**: Waterfall requests, missing streaming, parallel fetching
- **SEO**: Missing metadata, sitemap, robots.txt, structured data
- **Accessibility**: Missing alt text, ARIA labels, semantic HTML
- **TypeScript**: Type safety, generic types, proper typing

## Report Format

### Executive Summary
```markdown
## Executive Summary
- **Files Scanned**: 42 files
- **Issues Found**: 15 total (Critical: 2, High: 5, Medium: 6, Low: 2)
- **Categories**: Performance (8), Security (4), Bugs (2), Optimization (1)
```

### Detailed Findings
```markdown
### [SEVERITY] Issue Title

**Location**: `app/components/Header.tsx:42`

**Problem**: Importing moment.js increases bundle size significantly

**Impact**: Adds 200KB+ to bundle, slowing initial page load

**Fix**:
\`\`\`typescript
// ❌ Before (problematic)
import moment from 'moment'

// ✅ After (recommended)
import { format } from 'date-fns'
\`\`\`

**References**:
- [Next.js Optimization](https://nextjs.org/docs/app/building-your-application/optimizing)
```

## Supported Versions

- ✅ **Next.js 13+ (App Router)** - Full support for Server Components, Server Actions, streaming
- ✅ **Next.js 12 (Pages Router)** - Full support for getServerSideProps, getStaticProps patterns
- ✅ **Hybrid Apps** - Supports projects using both App Router and Pages Router

## Configuration

### Allowed Tools

The skill uses these tools:
- **Task**: Codebase exploration and analysis
- **Grep**: Pattern-based detection
- **Glob**: File finding by extension/pattern
- **Read**: Context validation
- **Bash**: Running standalone scripts
- **Write**: Generating detailed reports (when requested)

### Pattern Detection

All detection patterns are defined in [PATTERNS.md](PATTERNS.md). Includes 50+ patterns across:
- Performance anti-patterns
- Security vulnerabilities
- Common bugs
- Missing optimizations

### Best Practices Reference

See [REFERENCE.md](REFERENCE.md) for comprehensive Next.js best practices covering:
- Server Components vs Client Components
- Data fetching strategies
- Caching and revalidation
- Security guidelines
- Performance optimization techniques

## Examples

See [EXAMPLES.md](EXAMPLES.md) for real-world scenarios:
- Optimizing slow page loads
- Debugging hydration errors
- Securing Server Actions
- Improving Core Web Vitals
- Fixing bundle size issues

## Integration with CI/CD

### GitHub Actions

```yaml
name: Next.js Quality Scan

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Run Next.js scan
        run: |
          chmod +x .claude/skills/nextjs-kits/scripts/*.py
          python3 .claude/skills/nextjs-kits/scripts/scan-all.py .

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: scan-results
          path: nextjs-audit-report.*
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

python3 .claude/skills/nextjs-kits/scripts/scan-security.py .

if [ $? -eq 1 ]; then
  echo "❌ Critical security issues found!"
  exit 1
fi
```

## Customization

### Adding Custom Patterns

Edit [PATTERNS.md](PATTERNS.md) to add your own detection patterns:

```markdown
## Custom Patterns

**Your Custom Check**
\`\`\`
Grep patterns:
- "your-pattern-here"  # Description
\`\`\`
```

### Modifying Severity Levels

Adjust severity in SKILL.md or script files:
- **Critical**: Security vulnerabilities, broken functionality
- **High**: Significant issues, missing best practices
- **Medium**: Suboptimal patterns, performance issues
- **Low**: Style issues, minor optimizations

## Troubleshooting

### Skill Not Activating

1. **Verify installation:**
   ```bash
   ls .claude/skills/nextjs-kits/SKILL.md
   # or
   ls ~/.claude/skills/nextjs-kits/SKILL.md
   ```

2. **Check skill description matches your query:**
   - Use terms like "Next.js", "performance", "security", "debug"
   - Ask about specific issues: "hydration error", "bundle size", "XSS"

3. **Restart Claude Code** to reload skills

### False Positives

The skill validates findings by reading context, but some false positives may occur:
- Review each finding's context
- Cross-reference with Next.js documentation
- Adjust patterns in PATTERNS.md if needed

### Scripts Not Running

```bash
# Make executable
chmod +x .claude/skills/nextjs-kits/scripts/*.py

# Use explicit python
python3 .claude/skills/nextjs-kits/scripts/scan-all.py .
```

## Comparison: AI Analysis vs Standalone Scripts

| Feature | AI Analysis (Skill) | Standalone Scripts |
|---------|---------------------|-------------------|
| **Context awareness** | ✅ Full context | ❌ Pattern matching only |
| **False positives** | ✅ Low (validates context) | ⚠️ Higher |
| **Framework versions** | ✅ Version-aware | ⚠️ Generic patterns |
| **Remediation** | ✅ Detailed, contextual | ⚠️ Generic fixes |
| **Speed** | ⚠️ Slower (thorough) | ✅ Fast |
| **Use case** | Deep analysis | Quick scans, CI/CD |

**Recommendation**: Use AI analysis for comprehensive audits, standalone scripts for quick checks.

## Resources

**Official Documentation:**
- [Next.js Docs](https://nextjs.org/docs)
- [React Docs](https://react.dev)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Web.dev Performance](https://web.dev/performance)

**Skill Documentation:**
- [SKILL.md](SKILL.md) - Full skill implementation
- [PATTERNS.md](PATTERNS.md) - Detection patterns
- [REFERENCE.md](REFERENCE.md) - Best practices reference
- [EXAMPLES.md](EXAMPLES.md) - Usage examples
- [scripts/README.md](scripts/README.md) - Script documentation

## Version History

- **v1.0.0** (2025-11-09): Initial release
  - Performance optimization
  - Security auditing
  - Debugging assistance
  - Code optimization
  - Standalone scanning scripts
  - App Router and Pages Router support

## Contributing

To improve this skill:

1. **Add detection patterns**: Edit [PATTERNS.md](PATTERNS.md)
2. **Update best practices**: Edit [REFERENCE.md](REFERENCE.md)
3. **Add examples**: Edit [EXAMPLES.md](EXAMPLES.md)
4. **Improve scripts**: Edit files in `scripts/`

## License

This skill follows the same license as the claude-code-skills repository.

## Support

For issues or questions:
1. Review [SKILL.md](SKILL.md) for implementation details
2. Check [EXAMPLES.md](EXAMPLES.md) for usage scenarios
3. Consult [REFERENCE.md](REFERENCE.md) for Next.js best practices
4. Review [scripts/README.md](scripts/README.md) for script usage

---

**Made for Claude Code** | [Official Skills Documentation](https://code.claude.com/docs/en/skills.md)
