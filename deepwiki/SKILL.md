---
name: deepwiki
description: Access GitHub repository documentation and search capabilities through DeepWiki. Use when user asks about repository structure, documentation, or has questions about any public GitHub repo. Supports exploring repo topics, reading docs, and AI-powered Q&A grounded in repo context.
---

# DeepWiki Skill

Access comprehensive documentation and AI-powered search for any public GitHub repository.

## What is DeepWiki?

DeepWiki is a knowledge management system that provides structured access to GitHub repository documentation. The DeepWiki MCP server offers programmatic access to repository docs and context-grounded AI search capabilities.

## Available Tools

### 1. `read_wiki_structure`
**Purpose**: Get list of documentation topics for a GitHub repo

**Parameters**:
- `repoName` (required): Format `owner/repo` (e.g., `facebook/react`)

**Use when**:
- User wants to know what documentation is available
- Exploring repo structure before diving into specific topics
- Getting overview of repo's documentation organization

**Example**:
```
User: "What documentation is available for the React repository?"
→ Use read_wiki_structure with repoName="facebook/react"
```

### 2. `read_wiki_contents`
**Purpose**: View full documentation about a GitHub repo

**Parameters**:
- `repoName` (required): Format `owner/repo` (e.g., `vercel/next.js`)

**Use when**:
- User wants comprehensive documentation content
- Need detailed information about repo's features, architecture, or usage
- Following up after viewing structure to read actual content

**Example**:
```
User: "Show me the documentation for Next.js"
→ Use read_wiki_contents with repoName="vercel/next.js"
```

### 3. `ask_question`
**Purpose**: Ask any question about a GitHub repo with AI-powered, context-grounded answers

**Parameters**:
- `repoName` (required): Format `owner/repo` (e.g., `microsoft/vscode`)
- `question` (required): The question to ask about the repository

**Use when**:
- User has specific question about repo functionality, architecture, or usage
- Need targeted answer rather than browsing full documentation
- Looking for specific implementation details or best practices

**Example**:
```
User: "How does VS Code handle extensions?"
→ Use ask_question with repoName="microsoft/vscode" and question="How does VS Code handle extensions?"
```

## Workflow Patterns

### Pattern 1: Discovery → Documentation
1. Use `read_wiki_structure` to see available topics
2. Use `read_wiki_contents` to read full documentation
3. Use `ask_question` for specific clarifications

### Pattern 2: Direct Question
1. Use `ask_question` directly when user has specific question
2. Optionally use `read_wiki_contents` for broader context if needed

### Pattern 3: Repository Exploration
1. Start with `read_wiki_structure` to understand scope
2. Use `ask_question` to drill into specific areas of interest

## Best Practices

1. **Repo Name Format**: Always use `owner/repo` format (e.g., `facebook/react`, not just `react`)

2. **Tool Selection**:
   - Specific question → `ask_question`
   - Broad exploration → `read_wiki_structure` then `read_wiki_contents`
   - Topic discovery → `read_wiki_structure`

3. **Question Formulation**: Make questions specific and focused for best results from `ask_question`

4. **Public Repos Only**: DeepWiki MCP server only works with public/open-source repositories

5. **Parallel Exploration**: When user mentions multiple repos, can query them in parallel

## Limitations

- Only works with **public GitHub repositories**
- No write capabilities (read-only access)
- Results depend on available documentation quality in repo

## Examples

**Example 1: Repository Overview**
```
User: "What can you tell me about the shadcn/ui repository?"
Assistant: Let me explore this repository for you.
→ Uses read_wiki_structure with repoName="shadcn/ui"
→ Uses read_wiki_contents with repoName="shadcn/ui"
→ Provides overview based on documentation
```

**Example 2: Specific Question**
```
User: "How does React's reconciliation algorithm work?"
Assistant: I'll search the React repository for information about reconciliation.
→ Uses ask_question with repoName="facebook/react"
   and question="How does the reconciliation algorithm work?"
→ Returns context-grounded answer
```

**Example 3: Comparing Multiple Repos**
```
User: "Compare Vue and React's state management approaches"
Assistant: Let me query both repositories.
→ Uses ask_question with repoName="vuejs/core" and question="How does state management work?"
→ Uses ask_question with repoName="facebook/react" and question="How does state management work?"
→ Compares and contrasts the approaches
```

**Example 4: Documentation Discovery**
```
User: "What topics are covered in the TypeScript documentation?"
Assistant: Let me check the available documentation topics.
→ Uses read_wiki_structure with repoName="microsoft/TypeScript"
→ Lists all available documentation topics
```

## Tips for Users

- Be specific with repo names (use full `owner/repo` format)
- For broad exploration, ask to "explore" or "show documentation"
- For specific questions, ask directly and tool will use `ask_question`
- Can query multiple repos in parallel for comparisons