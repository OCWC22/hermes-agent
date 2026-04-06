---
name: prompt-spec-library
description: "Engineer, version, test, and maintain production prompt specs — meta-prompts that automate engineering, marketing, and operations workflows via other AI systems."
version: 1.0.0
metadata:
  hermes:
    tags: [meta-prompts, prompt-engineering, automation, versioning]
    category: domain
    related_skills: [operations-assistant, company-knowledge-graph]
---

# Prompt Spec Library

A prompt spec is a versioned, tested, production-ready prompt designed to run on a target system without human supervision. This skill governs how to create, test, version, and maintain them.

## When to Use

- User says "automate X" or "build a prompt for Y" → create a prompt spec
- User says "this prompt isn't working" → debug and revision workflow
- User says "what automations do we have" → inventory from the knowledge graph
- Cron health check finds a degraded prompt → revision workflow

## Creating a Prompt Spec

### Step 1: Decompose the task

Before writing any prompt, answer:
1. **What's the input?** — What varies per invocation? Define every variable.
2. **What's the output?** — What exact format/structure? Show the schema.
3. **Where does it run?** — Hermes cron, Hermes delegate_task, Zapier, n8n, API, script?
4. **What model?** — Specific model matters. A prompt tuned for Sonnet may fail on Gemma.
5. **What goes wrong?** — List the 3 most likely failure modes before writing anything.

### Step 2: Write the spec

```markdown
# [Task Name] v1.0

## Purpose
[One sentence — what outcome does this produce?]

## Runtime
- Where: [Hermes cron | delegate_task | Zapier | n8n | API | script]
- Model: [exact model identifier]
- Schedule: [cron expression — if recurring]
- Trigger: [event description — if event-driven]

## Inputs
| Variable | Source | Type | Required | Example |
|----------|--------|------|----------|---------|
| `{{var}}` | [where it comes from] | [string/json/file] | [yes/no] | [concrete example] |

## System Prompt
```
[The EXACT system prompt. Production-ready. Not a sketch.]
```

## User Message Template
```
[Template with {{variables}}. This changes per invocation.]
```

## Output Schema
```json
{
  "field": "type — description",
  "field": "type — description"
}
```

## Example
**Input:** [concrete input values]
**Output:**
```
[complete expected output]
```

## Failure Modes
| # | Failure | Detection | Handling |
|---|---------|-----------|----------|
| 1 | [what goes wrong] | [how to detect] | [retry/escalate/fallback] |
| 2 | ... | ... | ... |

## Validation Checklist
- [ ] Test: normal input → correct output
- [ ] Test: edge case → graceful handling
- [ ] Test: garbage input → error, not hallucination
- [ ] Test: empty/null inputs → defined behavior

## Changelog
- v1.0 — [date] — Initial spec
```

### Step 3: Save to file

Every prompt spec goes to a file. Specs that only exist in chat history are dead specs.

Save location: `~/.hermes/skills/company/prompts/references/[task-name]-v[version].md`

Or if the user has a project directory, save there.

### Step 4: Test the spec

Run the spec once with real inputs. Compare output to the expected output in the spec. If it doesn't match:
1. Identify which failure mode triggered
2. Add a guardrail to the system prompt
3. Bump the version
4. Re-test

## Versioning Rules

- **v1.0** — Initial spec, tested with at least 3 inputs
- **v1.1, v1.2, ...** — Minor fixes (wording, guardrails, format tweaks)
- **v2.0** — Major revision (different approach, model change, output schema change)
- Always update the changelog
- Keep previous versions in the file as comments or in a `references/archive/` folder

## Debugging a Failing Prompt

When a prompt spec produces bad output:

1. **Get the trace** — What was the actual input? What was the actual output?
2. **Classify the failure** — Which failure mode from the spec? Or a new one?
3. **Isolate the cause:**
   - Model-level: wrong model, wrong parameters, context overflow
   - Prompt-level: ambiguous instruction, missing guardrail, format drift
   - Input-level: unexpected input format, missing variable, garbage data
4. **Fix and version** — Don't edit in place. Create v[n+1] with the fix documented in changelog.
5. **Add the failure as a test case** — So it doesn't regress.

## Design Principles

1. **System prompt = behavior. User message = data.** Never mix them.
2. **Show the output schema, don't describe it.** JSON schema > prose description.
3. **Negative constraints beat positive hopes.** "Do NOT include disclaimers" > hoping it won't.
4. **Design for the weakest model.** If it might run on a small model, make instructions explicit.
5. **Self-validation.** Ask the model to check its output against the schema before returning.
6. **Handle null.** Every variable needs a "what if missing" behavior.
7. **One prompt, one job.** If a prompt does two things, split it into two prompts.

## Common Automation Patterns

### Content Pipeline (marketing)
- Input: `{{topic}}`, `{{audience}}`, `{{channel}}`, `{{brand_voice_doc}}`
- Output: Draft post/email/ad copy in brand voice
- Key guardrail: Reference brand voice doc explicitly; reject if topic is outside company domain

### Engineering Triage (support/ops)
- Input: `{{ticket_text}}`, `{{error_logs}}`, `{{system_context}}`
- Output: `{severity, category, assignee_suggestion, reproduction_steps}`
- Key guardrail: Severity must cite specific evidence from logs; never guess P0

### Outreach Personalization (sales)
- Input: `{{prospect_name}}`, `{{company}}`, `{{role}}`, `{{recent_activity}}`
- Output: Personalized email draft
- Key guardrail: No fabricated facts; if `{{recent_activity}}` is empty, use generic opener

### Meeting Summary (internal ops)
- Input: `{{transcript}}`
- Output: `{decisions[], action_items[{owner, task, deadline}], open_questions[]}`
- Key guardrail: Only attribute decisions to people explicitly named in transcript

### Code Review (engineering)
- Input: `{{diff}}`, `{{pr_description}}`, `{{repo_conventions}}`
- Output: `{summary, findings[{severity, file, line, issue, suggestion}], verdict}`
- Key guardrail: Findings must reference specific lines; verdict must be approve/request-changes, never "looks good" without findings

## Relationship to Other Skills

- **operations-assistant** — delegates to this skill when user says "automate X"
- **company-knowledge-graph** — prompt specs are stored in the `prompts/` domain of the graph
