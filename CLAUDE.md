# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Note**: For comprehensive documentation on working with this repository, see [AGENTS.md](AGENTS.md), which provides multi-agent compatible guidance following the [agents.md specification](https://agents.md/).

## Claude Code Specifics

This section contains Claude Code-specific information. For general repository information, skill architecture, development guidelines, and troubleshooting, see [AGENTS.md](AGENTS.md).

### Official Documentation

- **Official Skills Guide**: https://code.claude.com/docs/en/skills.md
- **Skills Best Practices**: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices
- **Skills Overview**: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview
- **Engineering Blog**: [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- **Full Docs Map**: See `knowledge/claude_code_docs_map.md` for complete documentation structure

### Knowledge Directory

The `knowledge/` directory contains official Claude Code documentation for reference:

- `claude_code_docs_skills.md` - Complete official skills documentation
- `claude_code_docs_map.md` - Hierarchical map of all Claude Code docs with links

These files provide the authoritative source for skill specifications, best practices, and troubleshooting.

## Quick Start for Claude Code

### Skill Locations

Claude Code discovers skills from:

1. **Personal Skills** (`~/.claude/skills/`) - Available across all your projects
2. **Project Skills** (`.claude/skills/` in project root) - Shared with team via git
3. **Plugin Skills** - Distributed via plugin marketplaces

This repository contains project skills that can be:

- Copied to `.claude/skills/` for project-level use
- Copied to `~/.claude/skills/` for personal use
- Packaged as a plugin for wider distribution

### Debugging Skills in Claude Code

If a skill isn't activating:

```bash
# View loading errors
claude --debug

# Check skill is discovered
# Ask Claude: "What skills are available?"
```

**Validate YAML syntax:**

```bash
cat .claude/skills/my-skill/SKILL.md | head -n 15
# Verify: opening --- on line 1, closing --- before content, no tabs
```

### Claude Code Tool Permissions

Use `allowed-tools` in SKILL.md frontmatter to restrict tools:

```yaml
---
name: my-skill
description: Read-only analysis skill
allowed-tools: Read, Grep, Glob # Claude won't ask for permission to use these
---
```

Available tools: `Task`, `Grep`, `Glob`, `Read`, `Bash`, `Write`

### Skills vs Slash Commands

| Feature        | Skills                                 | Slash Commands                     |
| -------------- | -------------------------------------- | ---------------------------------- |
| **Invocation** | Model-invoked (automatic)              | User-invoked (explicit `/command`) |
| **Activation** | Claude decides based on context        | User explicitly types command      |
| **Use case**   | Complex analysis, multi-step workflows | Quick templated prompts, shortcuts |

See [AGENTS.md](AGENTS.md) for detailed comparison and examples.

## Additional Resources

**For general repository information**, see [AGENTS.md](AGENTS.md):

- Repository overview and skill architecture
- Build and test commands
- Code style guidelines
- Development workflow (creating/modifying skills)
- Pattern detection approaches
- Report writing standards
- Troubleshooting guide
- Git workflow

**Official Claude Code Documentation:**

- **Skills Guide**: https://code.claude.com/docs/en/skills.md
- **Plugins Guide**: https://code.claude.com/docs/en/plugins.md
- **Plugin Marketplaces**: https://code.claude.com/docs/en/plugin-marketplaces.md
- **Slash Commands**: https://code.claude.com/docs/en/slash-commands.md
- **Complete Docs Map**: See `knowledge/claude_code_docs_map.md`

## Version Information

**Repository format**: Claude Code Skills v1.0
**Skill format version**: 2025-01 (following official specification)
**Compatible with**: Claude Code 1.0+
**Official spec**: https://code.claude.com/docs/en/skills.md
