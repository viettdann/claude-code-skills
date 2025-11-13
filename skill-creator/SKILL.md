---
name: skill-creator
description: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities with specialized knowledge, workflows, or tool integrations.
---

# Skill Creator

Guide for creating effective Agent Skills in Claude Code.

## What Are Agent Skills?

Skills are modular packages that extend Claude's capabilities by packaging expertise into discoverable capabilities through organized folders containing instructions, scripts, and resources.

**Key characteristic**: Skills are **model-invoked**—Claude autonomously decides when to activate them based on your request and the skill's description. This distinguishes them from user-invoked slash commands.

### Skill Types

1. **Personal Skills** (`~/.claude/skills/`) - Available across all projects; ideal for individual workflows
2. **Project Skills** (`.claude/skills/`) - Shared with teams via git; used for project-specific expertise
3. **Plugin Skills** - Bundled with Claude Code plugins; automatically available upon installation

### What Skills Provide

1. **Specialized workflows** - Multi-step procedures for specific domains
2. **Tool integrations** - Instructions for working with specific file formats or APIs
3. **Domain expertise** - Company-specific knowledge, schemas, business logic
4. **Bundled resources** - Scripts, references, and assets for complex and repetitive tasks

## Skill Structure

A minimal skill requires:
- A `SKILL.md` file containing YAML frontmatter and Markdown instructions
- Optional supporting files (scripts, templates, reference documents)

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required - lowercase, numbers, hyphens only, max 64 chars)
│   │   ├── description: (required - max 1024 chars)
│   │   └── allowed-tools: (optional - restrict tool access)
│   └── Markdown instructions (required)
└── Supporting Files (optional)
    ├── reference.md       - Documentation loaded as needed
    ├── examples.md        - Example usage patterns
    ├── scripts/           - Executable code (Python/Bash/etc.)
    └── templates/         - Template files
```

### YAML Frontmatter Requirements

**Required fields:**

- `name`: Must use lowercase letters, numbers, and hyphens only (max 64 characters)
- `description`: Brief description of what the skill does and when to use it (max 1024 characters)

**Optional fields:**

- `allowed-tools`: Array of tool names to restrict which tools Claude can access when the skill activates. Useful for read-only operations or security-sensitive workflows.

Example frontmatter:
```yaml
---
name: excel-analyzer
description: Analyze Excel spreadsheets, generate pivot tables, create charts. Use when working with Excel files.
allowed-tools: [Read, Bash, WebFetch]
---
```

### Supporting Files Organization

Claude employs **progressive disclosure**, reading supporting files only when contextually relevant:

- **reference.md** - Detailed documentation, schemas, API specs
- **examples.md** - Usage examples and patterns
- **scripts/** - Utility scripts for deterministic operations
- **templates/** - Template files used in output

### Progressive Disclosure Design Principle

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Supporting files** - As needed by Claude (loaded on demand)

## Creating Effective Skills

### Best Practices

#### Make Descriptions Discoverable

Include both functionality and activation triggers in the description. Claude uses descriptions to determine when to activate skills.

**Good example:**
```yaml
description: Analyze Excel spreadsheets, generate pivot tables, create charts. Use when working with Excel files.
```

**Poor example:**
```yaml
description: Excel tool
```

The good example includes:
- What the skill does (analyze, generate, create)
- When to use it (when working with Excel files)

#### Keep Skills Focused

Address one capability per skill rather than bundling multiple features.

**Good:** Separate "PDF form filling" from broader "document processing"
**Poor:** Single skill handling PDFs, Word docs, spreadsheets, and images

#### Restrict Tool Access (Optional)

Use `allowed-tools` frontmatter field to limit which tools Claude can access when the skill activates.

**Use cases:**
- Read-only operations (allow only `Read`, `Grep`, `Glob`)
- Security-sensitive workflows
- Preventing unintended side effects

Example:
```yaml
---
name: codebase-analyzer
description: Analyze codebase structure and patterns. Use when analyzing code without modifications.
allowed-tools: [Read, Grep, Glob, Bash]
---
```

### Skill Creation Workflow

#### Step 1: Create Skill Directory

For **Personal Skills** (available across all projects):
```bash
mkdir -p ~/.claude/skills/skill-name
```

For **Project Skills** (shared with team via git):
```bash
mkdir -p .claude/skills/skill-name
```

#### Step 2: Create SKILL.md

Create `SKILL.md` with required frontmatter and instructions:

```markdown
---
name: skill-name
description: Brief description of what the skill does and when to use it.
---

# Skill Name

## Purpose

Clear explanation of what this skill does.

## When to Use

Specific scenarios that should trigger this skill.

## Instructions

Detailed instructions for how Claude should use this skill.
```

**Writing style guidelines:**
- Use imperative/infinitive form (verb-first instructions)
- Use objective, instructional language
- Example: "To accomplish X, do Y" (not "You should do X")
- Keep SKILL.md focused on procedural instructions
- Move detailed reference material to supporting files

#### Step 3: Add Supporting Files (Optional)

Add supporting files as needed:

- **reference.md** - Schemas, API docs, detailed documentation
- **examples.md** - Usage examples and patterns
- **scripts/** - Executable code for deterministic operations
- **templates/** - Template files used in output

Example structure:
```
skill-name/
├── SKILL.md
├── reference.md
├── examples.md
├── scripts/
│   └── helper.py
└── templates/
    └── template.html
```

#### Step 4: Test the Skill

After creating the skill:

1. Restart Claude Code to load the skill
2. Ask questions matching the skill's description
3. Verify Claude activates the skill appropriately
4. Check that instructions are clear and effective

**Verification:**
- Ask Claude "What skills are available?" to confirm skill is loaded
- Try queries that should trigger the skill
- Try queries that shouldn't trigger it (to verify specificity)

#### Step 5: Iterate

Refine based on usage:

1. Use the skill on real tasks
2. Notice when Claude struggles or misunderstands
3. Update SKILL.md or supporting files
4. Restart Claude Code and test again

## Managing Skills

### Viewing Skills

Ask Claude: "What skills are available?"

Or check filesystem:
- Personal: `~/.claude/skills/`
- Project: `.claude/skills/`

### Updating Skills

1. Edit SKILL.md or supporting files
2. Restart Claude Code for changes to take effect

### Removing Skills

Delete the skill directory:

For Personal Skills:
```bash
rm -rf ~/.claude/skills/skill-name
```

For Project Skills:
```bash
rm -rf .claude/skills/skill-name
git commit -m "Remove skill-name skill"
```

### Sharing Skills

**Via Git (Project Skills):**
Commit Project Skills to repository. Team members get access upon pull.

**Via Plugins (Recommended):**
Bundle skills with Claude Code plugins for automatic distribution and updates.

## Troubleshooting

### Skill Not Activating

**Common issues:**

1. **Vague description** - Add specific trigger terms
   - ❌ "Document tool"
   - ✅ "Convert PDF to Word. Use when converting PDF documents."

2. **Invalid YAML** - Check frontmatter syntax
   ```yaml
   ---
   name: valid-name
   description: Valid description here.
   ---
   ```

3. **Incorrect file path** - Verify location
   - Personal: `~/.claude/skills/skill-name/SKILL.md`
   - Project: `.claude/skills/skill-name/SKILL.md`

4. **Didn't restart** - Restart Claude Code after creating/editing skill

**Debug mode:**
Run `claude --debug` to view skill loading errors.

### Multiple Skills Conflicting

Use distinct terminology in descriptions to help Claude select appropriately.

**Example - Distinguishing similar skills:**
```yaml
# pdf-converter skill
description: Convert PDF to other formats (Word, Excel, images). Use for PDF conversion tasks.

# pdf-editor skill
description: Edit PDF content, rotate pages, merge PDFs, split PDFs. Use for PDF editing operations.
```
