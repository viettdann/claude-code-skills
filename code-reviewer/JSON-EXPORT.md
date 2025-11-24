# JSON Export (Advanced Feature)

**⚠️ IMPORTANT**: This feature is STRICTLY OPTIONAL and should only be used when explicitly requested by users for CI/CD integration or automation purposes.

## 🚫 Strict Enforcement Rules

**DO NOT generate JSON unless ALL conditions are met:**

1. ✅ User explicitly typed one of these phrases:
   - "generate JSON"
   - "create JSON report" 
   - "export as JSON"
   - "I need JSON output"
   - "output JSON"
2. ✅ User mentioned CI/CD integration or automation needs

**❌ DO NOT generate JSON if:**
- User only requested "code review" (default = markdown only)
- User said "review my code" without mentioning JSON
- You think JSON would be "helpful" (it's not - markdown is default)
- Previous conversation mentioned JSON (each review is independent)

**DEFAULT BEHAVIOR (99% of cases):**
- ✅ Generate markdown report ONLY
- ✅ NO JSON file creation
- ✅ NO JSON output in terminal

**Violation = Task Failure:** If you generate JSON without explicit user request, you have VIOLATED these instructions and FAILED the task.

---

## Pre-Flight Validation (Required Before JSON Generation)

Before creating ANY JSON file, you MUST check:

```bash
# CHECKPOINT: Did user explicitly request JSON?
# Review the user's message for keywords:
# - "JSON" mentioned? YES/NO
# - "export" mentioned? YES/NO  
# - "CI/CD" mentioned? YES/NO
#
# If ALL answers are NO → STOP. Generate markdown only.
# If ANY answer is YES → Confirm intent with user before proceeding
```

**Confirmation required:**
- Ask user: "Confirm: Generate JSON report alongside markdown? (yes/no)"
- Wait for explicit confirmation
- Only proceed if user confirms

---

## JSON Structure

Follow the complete schema defined in [SCHEMA.md](SCHEMA.md).

**Key sections:**
- `metadata` - Project, commit, timestamps
- `summary` - Grade, verdict, issue counts, productionReady flag
- `issues[]` - File, line, severity, description, fix
- `strengths[]` - Best practices identified
- `files[]` - Per-file status
- `metrics` - Quality scores

**Important:** Generate **compact JSON** (no pretty-printing) to minimize file size for CI/CD systems and reduce token usage when parsed.

---

## Generation Workflow (After User Confirmation)

```bash
# ONLY execute after user explicitly requested AND confirmed JSON

# Generate JSON filename
JSON_FILE="${REPORT_FILE%.md}.json"

# Example: CODE-REVIEW-REPORT-2025-01-13.json (general)
# Example: CODE-REVIEW-REPORT-2025-01-13-abc1234.json (commit)

# 1. Collect metadata
REPORT_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
COMMIT_SHA=$(git log -1 --format=%h)
PROJECT_NAME=$(basename $(git rev-parse --show-toplevel))

# 2. Use Write tool to create COMPACT JSON (no pretty-printing)
# Populate with all findings organized according to schema

# 3. VALIDATE JSON with jq (quick check)
if command -v jq &> /dev/null; then
  if jq empty "$JSON_FILE" 2>/dev/null; then
    echo "✓ JSON validation passed"
  else
    echo "✗ JSON validation FAILED - file may be invalid"
  fi
fi

# 4. Inform user
echo "✅ Code review complete!"
echo "📄 Markdown report: ${REPORT_FILE}"
echo "📊 JSON output: ${JSON_FILE}"
```

---

## Notes

- Generate **compact JSON** (single-line, no indentation) to minimize file size for CI/CD systems and reduce token usage when parsed
- Validate with `jq` if available (optional but recommended) - fails fast if JSON is malformed
- JSON can be used for PR automation, CI/CD integration, or custom tooling

---

## Terminal Output (When JSON Requested)

**🚫 CRITICAL**: DO NOT add JSON output to terminal unless:
1. User explicitly requested JSON using keywords above
2. User confirmed JSON generation when asked

**Only if both conditions met, add:**
```
📊 JSON output: CODE-REVIEW-REPORT-2025-11-14-[commit-hash].json
✓ JSON validation passed
```

**Default (no JSON request):** Omit JSON lines entirely from terminal output.
