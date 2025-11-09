# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Official Documentation

This repository contains Claude Code skills following the official Agent Skills specification. For comprehensive documentation:

- **Official Skills Guide**: https://code.claude.com/docs/en/skills.md
- **Skills Best Practices**: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices
- **Skills Overview**: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview
- **Engineering Blog**: [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- **Full Docs Map**: See `knowledge/claude_code_docs_map.md` for complete documentation structure

### Knowledge Directory

The `knowledge/` directory contains official Claude Code documentation for reference:

- `claude_code_docs_skills.md` - Complete official skills documentation
- `claude_code_docs_map.md` - Hierarchical map of all Claude Code docs with links

These files provide the authoritative source for skill specifications, best practices, and troubleshooting. When in doubt, refer to these official docs.

## Repository Overview

This is a collection of **Claude Code Skills** - specialized AI agents for security auditing, code quality analysis, and documentation access. Each skill is a self-contained module with its own SKILL.md definition, documentation, and standalone scripts.

**What are Agent Skills?** Skills package expertise into discoverable capabilities. They are **model-invoked** (Claude autonomously decides when to use them) rather than user-invoked like slash commands.

## Skill Architecture

### Core Skill Components

Each skill follows a consistent structure:

```
skill-name/
├── SKILL.md           # Skill definition with frontmatter metadata
├── README.md          # User-facing documentation
├── PATTERNS.md        # Detection patterns and grep rules (if applicable)
├── REFERENCE.md       # Technical reference materials (if applicable)
├── EXAMPLES.md        # Usage examples (if applicable)
└── scripts/           # Standalone scanning scripts (optional)
    ├── README.md      # Script documentation
    └── *.py, *.sh     # Executable scan scripts
```

### SKILL.md Frontmatter

Every skill must have a SKILL.md file with YAML frontmatter following official specifications:

```yaml
---
name: skill-name
description: Brief description of what the skill does and when to use it
allowed-tools: Task, Grep, Glob, Read, Bash, Write
---
```

**Field requirements (official specs):**
- `name` (required): Must use lowercase letters, numbers, and hyphens only. Maximum 64 characters. Must match directory name.
- `description` (required): Brief description of what the skill does and **when to use it**. Maximum 1024 characters. This field is **critical for discovery** - Claude uses it to determine when to activate the skill.
- `allowed-tools` (optional): Restricts which tools Claude can use when this skill is active. When specified, Claude can only use the listed tools without asking for permission. Useful for read-only skills or security-sensitive workflows. If not specified, Claude follows the standard permission model.

**Description best practices:**
- Include both **what** the skill does and **when** to use it
- Use specific trigger terms users would mention
- List supported frameworks/technologies
- Example: "Analyze Excel spreadsheets, create pivot tables, generate charts. Use when working with Excel files, spreadsheets, or .xlsx format."

### Skill Types and Locations

Claude Code discovers skills from three sources:

1. **Personal Skills** (`~/.claude/skills/`)
   - Available across all your projects
   - For individual workflows and preferences
   - Not shared with team

2. **Project Skills** (`.claude/skills/` in project root)
   - Shared with team via git
   - For team workflows and conventions
   - Automatically available when team members clone/pull

3. **Plugin Skills** (bundled with plugins)
   - Distributed via plugin marketplaces
   - Installed through plugin system
   - Work same as personal/project skills

**This repository** contains project skills that can be distributed as a plugin or used directly in `.claude/skills/`.

### Skill Activation

**Model-invoked behavior**: Skills are **automatically activated** by Claude based on the user's request and the skill's description. Users don't need to explicitly invoke skills (unlike slash commands which require `/command` syntax).

**How activation works:**
1. User asks a question or makes a request
2. Claude analyzes the request against all available skill descriptions
3. If a skill's description matches the context, Claude automatically loads and uses it
4. The skill's SKILL.md instructions guide Claude's behavior

**Activation triggers:**
- Primary use cases mentioned in description
- Keywords and technology names (e.g., "Next.js", "ABP", "secrets")
- Action verbs (e.g., "audit", "scan", "analyze", "check")
- File types or patterns (e.g., "PDF files", ".xlsx format")

**Example**: If a skill's description mentions "scan for secrets in Next.js apps", asking "Check my code for secrets" will activate that skill.

### Progressive Disclosure

Claude uses **progressive disclosure** to manage context efficiently:

- **SKILL.md is loaded first** when the skill activates
- **Supporting files** (README.md, PATTERNS.md, REFERENCE.md, scripts/) are loaded **only when needed**
- Reference supporting files from SKILL.md using relative paths: `[advanced usage](REFERENCE.md)`
- Claude will read referenced files automatically when following those links

This approach:
- Reduces initial token usage
- Allows comprehensive documentation without overwhelming context
- Enables deep-dive when Claude needs specific details

### Two-Tier Execution Model

Skills support both AI-guided analysis and standalone script execution:

1. **AI-Guided Analysis** (Primary)
   - Claude Code reads SKILL.md and executes analysis using allowed tools
   - Uses Task tool for exploration, Grep for pattern matching, Read for context
   - Provides contextual findings with explanations and remediation

2. **Standalone Scripts** (Optional, Secondary)
   - Quick pattern-based scans without AI overhead
   - Located in `scripts/` directory
   - Written in Python or Bash for portability
   - Generate structured output (JSON, markdown reports)
   - Can be run independently or as pre-scan before AI analysis

## Common Patterns Across Skills

### Security Audit Skills (abp-framework-analyzer, nextjs-security-audit, scanning-for-secrets)

**Execution strategy:**
1. **Initial Reconnaissance**: Use Task tool with Explore agent ("very thorough") to map codebase
2. **Systematic Analysis**: Use Grep with predefined patterns from PATTERNS.md
3. **Validation**: Read flagged files to confirm issues in context
4. **Reporting**: Generate severity-classified findings with fixes

**Severity classification:**
- **Critical**: Security vulnerabilities, data corruption risks, architectural violations
- **High**: Performance issues, missing validation, DDD violations
- **Medium**: Code duplication, inefficiencies, missing patterns
- **Low**: Style issues, minor optimizations

**Report format:**
```markdown
### [SEVERITY] Issue Title
**Location:** `path/to/file.ext:line`
**Problem:** [Description]
**Impact:** [Consequences]
**Fix:**
```typescript
// ❌ Before (problematic)
// ✅ After (recommended)
```
**References:** [Links to docs]
```

### Pattern Detection Approach

All auditing skills use grep patterns defined in PATTERNS.md:

**Example pattern structure:**
```
Grep patterns:
- "pattern1"  # Description of what it catches
- "pattern2"  # Description
```

**Best practices:**
- Always read context around matches to avoid false positives
- Cross-reference with framework documentation
- Consider framework-specific conventions (ABP, Next.js)
- Validate placeholders vs real secrets

### Standalone Script Integration

Skills with `scripts/` directories provide quick scans:

**Typical script workflow:**
```bash
# Run standalone script first (optional quick scan)
python3 scripts/scan_files.py

# Then use AI analysis for context and validation
# Claude reads script output and provides deeper analysis
```

**Script characteristics:**
- Executable permissions (`chmod +x`)
- Output to stdout or JSON files
- README.md documents usage and output format
- No external dependencies beyond Python stdlib (or document requirements)

## Development Guidelines

### Creating New Skills

**Official validation checklist:**

1. **Directory Setup**
   ```bash
   # For project skills
   mkdir -p .claude/skills/skill-name
   cd .claude/skills/skill-name

   # Or for personal skills
   mkdir -p ~/.claude/skills/skill-name
   cd ~/.claude/skills/skill-name
   ```

2. **Create SKILL.md** with valid frontmatter
   - `name`: lowercase, hyphens only, max 64 chars, matches directory name
   - `description`: max 1024 chars, includes **both what and when**
   - `allowed-tools`: (optional) list of permitted tools

   ```yaml
   ---
   name: my-skill-name
   description: What the skill does and when to use it. Include key terms users would mention.
   allowed-tools: Read, Grep, Glob
   ---

   # Skill Name

   ## Instructions
   Clear, step-by-step guidance for Claude.

   ## Examples
   Concrete examples of using this skill.
   ```

3. **Add supporting files** (loaded via progressive disclosure)
   - README.md for user documentation
   - PATTERNS.md for detection patterns (if applicable)
   - REFERENCE.md for technical details
   - scripts/ for standalone tools (optional)

4. **Validate YAML syntax**
   ```bash
   cat SKILL.md | head -n 15
   # Check: opening --- on line 1, closing --- before content, no tabs
   ```

5. **Test activation**
   - Ask Claude questions matching your description
   - Use: "What skills are available?" to verify it's loaded
   - Debug with: `claude --debug` to see loading errors

6. **Verify skill doesn't activate incorrectly**
   - Ask unrelated questions to ensure description is specific enough
   - Adjust description if skill activates too broadly or too narrowly

### Modifying Existing Skills

**Update workflow:**

1. **Edit SKILL.md**
   ```bash
   # For project skills
   code .claude/skills/my-skill/SKILL.md

   # For personal skills
   code ~/.claude/skills/my-skill/SKILL.md
   ```

2. **Changes take effect on restart**
   - If Claude Code is running, restart it to load updates
   - New sessions will automatically use updated version

3. **Commit changes (project skills)**
   ```bash
   git add .claude/skills/my-skill/
   git commit -m "skills (my-skill): describe changes"
   git push
   ```

**When updating patterns:**
1. Update PATTERNS.md with new grep patterns
2. Update SKILL.md execution steps if workflow changes
3. Update scripts/ if standalone scanners need new patterns
4. Add examples to EXAMPLES.md

**When fixing false positives:**
1. Add validation logic to SKILL.md
2. Update scripts/validate_findings.py (if exists)
3. Document exclusion patterns

**When adding features:**
1. Update skill description in SKILL.md frontmatter (if activation triggers change)
2. Add new grep patterns to PATTERNS.md
3. Update report format if needed
4. Add examples to documentation

**Document skill versions** (optional but recommended):

```markdown
# My Skill

## Version History
- v2.0.0 (2025-10-01): Breaking changes to API
- v1.1.0 (2025-09-15): Added new features
- v1.0.0 (2025-09-01): Initial release
```

This helps team members understand what changed between versions.

### Skill Documentation Best Practices

- **SKILL.md**: Detailed execution instructions for Claude Code
- **README.md**: User-facing documentation with quick start
- **PATTERNS.md**: Technical reference for detection patterns
- **EXAMPLES.md**: Real-world usage scenarios
- **scripts/README.md**: Script usage and output format

## Working with This Repository

### Running Standalone Scripts

**Secret Scanner:**
```bash
cd scanning-for-secrets
python3 scripts/scan_files.py          # Scan current files
python3 scripts/validate_findings.py   # Validate findings
python3 scripts/scan_git_history.py    # Check git history
```

**ABP Framework Analyzer:**
```bash
cd abp-framework-analyzer
bash scripts/scan-async-issues.sh        # Find async/sync violations
bash scripts/scan-repository-issues.sh   # Find repository anti-patterns
```

**Next.js Security Audit:**
```bash
cd nextjs-security-audit
bash scripts/scan-secrets.sh             # Find hardcoded secrets
bash scripts/scan-server-actions.sh      # Audit Server Actions
python3 scripts/scan-type-safety.py      # Type safety issues
python3 scripts/scan-all.py              # Run all scans
```

### Git Workflow

**Standard workflow:**
```bash
git status                    # Check current state
git add <skill-name>/         # Stage skill changes
git commit -m "skills (<skill-name>): description"
git push origin main
```

**Commit message format:**
```
skills (<skill-name>): brief description

Longer explanation if needed
```

**Examples:**
- `skills (abp-framework-analyzer): Add DDD tactical pattern validation`
- `skills (scanning-for-secrets): Add Azure DevOps PAT detection`
- `skills: add new TypeScript API analyzer skill`

### Testing Skills

**Manual testing:**
1. Ask Claude Code a question that should trigger the skill
2. Verify skill activates correctly
3. Check that output matches expected format
4. Validate findings for false positives

**Example test queries:**
- "Scan my code for secrets" → activates scanning-for-secrets
- "Audit my ABP project for DDD violations" → activates abp-framework-analyzer
- "Check my Next.js app for security issues" → activates nextjs-security-audit
- "What docs are available for react?" → activates deepwiki

### Adding Dependencies

**Python scripts:**
- Prefer standard library when possible
- Document required packages in skill README.md
- Example: scanning-for-secrets requires `gitpython`

**Installation instructions format:**
```bash
# Required dependencies
pip install gitpython

# or
pip install -r requirements.txt  # if using requirements.txt
```

## Architecture Principles

### Skill Design Philosophy

1. **Self-Contained**: Each skill is independent with complete documentation
2. **Discoverable**: Description field clearly states use cases
3. **Actionable**: Findings include remediation steps and code examples
4. **Validated**: Reduce false positives through context reading
5. **Tiered**: Support both AI analysis and standalone scripts

### Tool Usage Guidelines

**When to use each tool:**
- **Task (Explore)**: Initial codebase reconnaissance, understanding structure
- **Grep**: Pattern-based detection, finding specific code patterns
- **Glob**: Finding files by name/extension
- **Read**: Validating findings, understanding context
- **Bash**: Running standalone scripts, git operations
- **Write**: Generating reports (when report output requested)

**Tool usage patterns:**
```
Discovery:     Task (Explore) → Glob/Grep → Read → Report
Validation:    Grep → Read → Validate → Report
Quick Scan:    Bash (scripts) → Read output → Summarize
```

### Report Writing Standards

**All reports should include:**
1. Executive summary (files scanned, issues found, severity breakdown)
2. Prioritized findings (Critical → High → Medium → Low)
3. File paths with line numbers (`path/to/file.ext:123`)
4. Code examples (❌ Before / ✅ After format)
5. Remediation steps specific to the issue
6. References to official documentation

**Avoid:**
- Generic recommendations without context
- Reporting without validating in actual code
- Missing file/line references
- Recommendations without code examples

## Troubleshooting

### Skill Not Activating

**Official debugging steps:**

1. **Check description specificity**
   ```yaml
   # ❌ Too vague
   description: Helps with documents

   # ✅ Specific
   description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when user mentions PDFs, forms, or document extraction.
   ```

2. **Verify file path and structure**
   ```bash
   # Personal skills
   ls ~/.claude/skills/my-skill/SKILL.md

   # Project skills
   ls .claude/skills/my-skill/SKILL.md
   ```

3. **Check YAML syntax**
   ```bash
   cat SKILL.md | head -n 15
   # Verify: opening --- on line 1, closing --- before content, no tabs, proper indentation
   ```

4. **View loading errors**
   ```bash
   claude --debug
   # Shows skill loading errors and validation issues
   ```

5. **Verify skill is discovered**
   Ask Claude: "What skills are available?" or "List all available skills"

### Multiple Skills Conflicting

**Problem**: Claude uses the wrong skill or seems confused between similar skills.

**Solution**: Use distinct trigger terms in descriptions

```yaml
# ❌ Similar descriptions
# Skill 1
description: For data analysis
# Skill 2
description: For analyzing data

# ✅ Distinct triggers
# Skill 1
description: Analyze sales data in Excel files and CRM exports. Use for sales reports, pipeline analysis, revenue tracking.
# Skill 2
description: Analyze log files and system metrics data. Use for performance monitoring, debugging, system diagnostics.
```

### Skill Has Errors

1. **Check dependencies availability**
   - Claude will automatically install required dependencies or ask for permission
   - List requirements in skill description: "Requires pypdf and pdfplumber packages"

2. **Verify script permissions**
   ```bash
   chmod +x .claude/skills/my-skill/scripts/*.py
   ```

3. **Check file paths in SKILL.md**
   - Use forward slashes (Unix style): `scripts/helper.py` ✅
   - Not Windows style: `scripts\helper.py` ❌

### False Positives in Security Scans
- Add validation logic to skill instructions
- Update PATTERNS.md with exclusion patterns
- Improve context reading in analysis steps
- Update scripts/validate_findings.py

### Script Execution Issues
- Verify executable permissions (`chmod +x script.sh`)
- Check Python version (requires 3.7+)
- Install missing dependencies
- Run from correct directory

### Report Quality Issues
- Include more context from Read tool
- Add specific remediation for each issue type
- Reference framework-specific documentation
- Validate findings before reporting

## Skills vs Slash Commands

Understanding the distinction between Skills and Slash Commands is crucial:

| Feature | Skills | Slash Commands |
|---------|--------|----------------|
| **Invocation** | Model-invoked (automatic) | User-invoked (explicit `/command`) |
| **Activation** | Claude decides based on context | User explicitly types command |
| **Use case** | Complex analysis, multi-step workflows | Quick templated prompts, shortcuts |
| **Scope** | Can use multiple tools, full capabilities | Simple prompt expansion |
| **Discovery** | Via description matching | Must be known/discovered by user |

**Use Skills for:**
- Security audits and code analysis
- Complex multi-step workflows
- Context-aware assistance
- When Claude should proactively help
- Capabilities requiring tool usage (Read, Grep, Bash)

**Use Slash Commands for:**
- Quick prompt templates
- User-initiated shortcuts
- Simple repetitive prompts
- When user wants explicit control

**Example comparison:**

```yaml
# Skill (automatic)
---
name: code-reviewer
description: Review code for best practices. Use when reviewing code or analyzing code quality.
---
# Activates when user says: "Review this code"

# Slash Command (explicit)
/review - "Please review this code for best practices"
# Only runs when user types: /review
```

## Distributing Skills

### As Project Skills (Git)
```bash
# Add to project
mkdir -p .claude/skills/
cp -r skill-name .claude/skills/
git add .claude/skills/
git commit -m "skills: add skill-name"
git push

# Team members get automatically on pull
git pull  # Skills now available
```

### As Plugin (Recommended for Distribution)

For wider distribution, package skills as a plugin:

1. Create plugin structure with `skills/` directory
2. Add to plugin marketplace
3. Users install via plugin system

See: https://code.claude.com/docs/en/plugins.md

## Resources

**Official Claude Code Documentation:**
- **Skills Guide**: https://code.claude.com/docs/en/skills.md
- **Skills Best Practices**: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices
- **Skills Overview**: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview
- **Plugins Guide**: https://code.claude.com/docs/en/plugins.md
- **Plugin Marketplaces**: https://code.claude.com/docs/en/plugin-marketplaces.md
- **Slash Commands**: https://code.claude.com/docs/en/slash-commands.md
- **Complete Docs Map**: See `knowledge/claude_code_docs_map.md`

**Framework-Specific Documentation:**
- ABP Framework: https://docs.abp.io/
- Next.js: https://nextjs.org/docs
- OWASP: https://owasp.org/

**Pattern References (in this repository):**
- Each skill's PATTERNS.md contains detection patterns
- REFERENCE.md provides technical background
- EXAMPLES.md shows real-world usage

## Version Information

**Repository format**: Claude Code Skills v1.0
**Skill format version**: 2025-01 (following official specification)
**Compatible with**: Claude Code 1.0+
**Official spec**: https://code.claude.com/docs/en/skills.md
