# Code Review Report Template

This template provides the structure for auto-generated code review reports. The Code Reviewer skill uses this format to create comprehensive, actionable code review documentation.

## Template Structure

```markdown
# 🔍 [Project Name] Code Review Report

**Project:** [Project Name]
**Framework:** [Framework/Stack]
**Language:** [Primary Language]
**Analysis Date:** YYYY-MM-DD
**Analyzed By:** Code Reviewer Skill
**Commit/Branch:** [Commit SHA or branch name]

---

## 📊 Executive Summary

### Overall Assessment: **[Grade]**

[2-3 paragraph summary]

**Key Highlights:**
- ✅ [Strength]
- ⚠️ [Concern]

### Quick Stats

| Category | Status |
|----------|--------|
| Security | [Status] |
| Code Quality | [Status] |
| Performance | [Status] |
| Best Practices | [Status] |
| Test Coverage | [Status] |

---

## Table of Contents

1. [Critical Issues](#critical-issues) (X)
2. [High Priority Issues](#high-priority-issues) (X)
3. [Medium Priority Issues](#medium-priority-issues) (X)
4. [Low Priority Issues](#low-priority-issues) (X)
5. [Strengths & Best Practices](#strengths--best-practices) (X+)
6. [Summary & Priority Roadmap](#summary--priority-roadmap)
7. [Recommended Immediate Actions](#recommended-immediate-actions)
8. [References & Resources](#references--resources)

---

## 🚨 CRITICAL ISSUES (X)

### 🚨 CRITICAL #1: [Issue Title]

**Location:** `path/to/file.ext:line`
**Severity:** CRITICAL
**Category:** [Category]

#### Problem
[Description]

#### Impact
- 🔴 **[Impact]**

#### Current Code (Problematic)
```language
// ❌ Current
[code]
```

#### Recommended Fix
```language
// ✅ Recommended
[code]
```

#### Testing
```bash
[test commands]
```

#### References
- [Links]

---

## 🔴 HIGH PRIORITY ISSUES (X)
[Same format]

---

## ⚠️ MEDIUM PRIORITY ISSUES (X)
[Same format]

---

## ℹ️ LOW PRIORITY ISSUES (X)
[Same format]

---

## ✅ STRENGTHS & BEST PRACTICES

### ✅ #1: [Strength Title]

**Finding:** [Description]

**Evidence:**
```
✅ [Evidence]
```

**Example from Codebase:**
```language
// ✅ Example
[code]
```

**Why This is Excellent:**
- ✅ **[Benefit]**

---

## 📋 Summary & Priority Roadmap

### Issue Distribution by Severity

| Severity | Count | Must Fix Before Production? |
|----------|-------|----------------------------|
| 🚨 **CRITICAL** | X | [Status] |
| 🔴 **HIGH** | X | [Status] |
| ⚠️ **MEDIUM** | X | [Status] |
| ℹ️ **LOW** | X | [Status] |
| ✅ **STRENGTHS** | X+ | [Status] |

### Overall Code Quality Score

**Security:** [Grade] - [Assessment]
**Performance:** [Grade] - [Assessment]
**Maintainability:** [Grade] - [Assessment]
**Best Practices:** [Grade] - [Assessment]
**Architecture:** [Grade] - [Assessment]

**Overall:** **[Grade]** - [Verdict]

### Priority Fix Order

#### 🚨 IMMEDIATE
| # | Issue | File | Priority |
|---|-------|------|----------|
| 1 | [Issue] | `file:line` | **P0** |

---

## 🎯 RECOMMENDED IMMEDIATE ACTIONS

### Phase 1: [Phase Name]

**Objective:** [Objective]

#### Step 1.1: [Task]

```language
[code/commands]
```

### Verification Checklist

#### Security
- [ ] [Checklist item]

#### Reliability
- [ ] [Checklist item]

---

## 📚 REFERENCES & RESOURCES

### Framework Documentation
- [Links]

### Security
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

### Performance
- [Links]

---

## 🎬 CONCLUSION

### Final Verdict

**Code Quality Grade: [Grade]** - [Summary]

### What's Exceptional ✅
[Paragraphs]

### Critical Gaps ❌
[If any]

### Bottom Line
[Assessment]

**Recommendation:** [Recommendation]

### Next Steps
1. ✅ **[Task]**

---

**Report Generated:** YYYY-MM-DD HH:MM
**Analyzer:** Code Reviewer Skill
**Total Files Analyzed:** X
**Total Lines Analyzed:** X

---

## 📌 APPENDIX: Issue Quick Reference

### Quick Links to Issues

**CRITICAL:**
- [Link]

**HIGH:**
- [Link]

### File Locations Quick Reference

```
CRITICAL/HIGH FILES:
├── file1:line
└── file2:line
```

---

**End of Report**
```

## Field Descriptions

### Header Section

- **Project**: Name of the project being reviewed
- **Framework**: Technology stack (e.g., "Next.js 14 with TypeScript", "ABP 9.3 with .NET 9")
- **Language**: Primary programming language
- **Analysis Date**: Date review was conducted (YYYY-MM-DD format)
- **Commit/Branch**: Git commit SHA or branch name if applicable

### Executive Summary

- **Overall Assessment**: Letter grade (A+, A, A-, B+, B, C, F)
- **Key Highlights**: 3-5 bullet points of major findings (both positive and negative)
- **Quick Stats**: High-level status for each major category using ✅/⚠️/🔴 indicators

### Issues Sections

Each issue should include:
- **Location**: File path with line number
- **Severity**: CRITICAL, HIGH, MEDIUM, or LOW
- **Category**: Type of issue (Security, Performance, Code Quality, etc.)
- **Problem**: 2-3 sentences explaining the issue
- **Impact**: Bulleted list of consequences
- **Current Code**: Code showing the problem with ❌ marker
- **Recommended Fix**: Fixed code with ✅ marker and explanation
- **Testing**: Commands or scenarios to verify the fix
- **References**: Links to relevant documentation

### Severity Criteria

**CRITICAL (🚨):**
- Security vulnerabilities (SQL injection, XSS, auth bypass)
- Data corruption risks
- System crashes or stability issues
- **Action**: Must fix immediately before any deployment

**HIGH (🔴):**
- Bugs affecting functionality
- Major performance issues
- Architectural violations
- Security gaps (missing authorization, weak validation)
- **Action**: Should fix before production deployment

**MEDIUM (⚠️):**
- Code quality issues
- Minor performance problems
- Missing best practices
- Technical debt
- **Action**: Address in next sprint or iteration

**LOW (ℹ️):**
- Style inconsistencies
- Minor optimizations
- Documentation improvements
- Refactoring opportunities
- **Action**: Nice to have, backlog items

### Strengths Section

- Identify 5-10 positive patterns in the codebase
- Provide evidence with code examples
- Explain why each practice is excellent
- Use ✅ markers to highlight good practices

### Grading Scale

**A+ (95-100%):** Exceptional code quality, production-ready, exemplary practices
**A (90-94%):** Excellent quality, minor improvements possible
**A- (85-89%):** Very good, some improvements needed
**B+ (80-84%):** Good, several improvements recommended
**B (75-79%):** Acceptable, needs work before production
**C (70-74%):** Below standard, significant issues
**F (<70%):** Poor quality, major refactoring needed

### Report Filename Conventions

Use consistent naming:

- **General review**: `CODE-REVIEW-REPORT-{YYYY-MM-DD}.md`
- **Commit review**: `CODE-REVIEW-REPORT-{YYYY-MM-DD}-{commit-sha}.md`
- **Security audit**: `SECURITY-AUDIT-REPORT-{YYYY-MM-DD}.md`
- **Performance review**: `PERFORMANCE-REVIEW-REPORT-{YYYY-MM-DD}.md`

### Best Practices for Report Generation

1. **Be specific**: Include exact file paths and line numbers
2. **Be actionable**: Provide concrete fixes, not just problems
3. **Be balanced**: Highlight both issues and strengths
4. **Be thorough**: Cover all changed files, not just problematic ones
5. **Be educational**: Explain why issues matter
6. **Be constructive**: Focus on improvement, not criticism

### Example Report Locations

Reports should be saved at project root:

```
project/
├── CODE-REVIEW-REPORT-2025-01-13.md
├── SECURITY-AUDIT-REPORT-2025-01-10.md
├── src/
├── tests/
└── README.md
```

## Usage

This template is automatically used by the Code Reviewer skill when generating reports. The skill:

1. Analyzes code using patterns from PATTERNS.md
2. Collects findings organized by severity
3. Identifies strengths and best practices
4. Populates this template with actual data
5. Writes the report file to disk
6. Informs the user of the report location

See SKILL.md for the complete implementation details and EXAMPLES.md for sample reports.

## Version

- **Template Version**: 1.0.0
- **Last Updated**: 2025-01-13
- **Compatible With**: Code Reviewer Skill v1.0+

## References

- Based on ABP Framework Analysis Report structure
- Follows industry-standard code review practices
- Incorporates OWASP security review guidelines
- Aligned with Clean Architecture principles
