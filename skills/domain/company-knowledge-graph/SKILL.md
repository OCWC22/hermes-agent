---
name: company-knowledge-graph
description: "Build and maintain a skill graph — a traversable network of interconnected knowledge files that gets smarter every time you use it. Based on Karpathy's second brain + Heinrich's skill graph architecture."
version: 1.0.0
metadata:
  hermes:
    tags: [knowledge-base, skill-graph, wiki, second-brain, continual-learning]
    category: domain
    related_skills: [operations-assistant, prompt-spec-library]
---

# Company Knowledge Graph

A skill graph is a network of interconnected skill files that the agent traverses on demand. Instead of one big document, you have many small composable pieces that reference each other. Each file is one complete thought, procedure, or domain skill.

This skill teaches the agent how to **build, maintain, and traverse** a skill graph for company operations.

## Architecture

```
~/.hermes/skills/company/
  INDEX.md                    # Entry point — map of content with links to all domains
  engineering/
    SKILL.md                  # Engineering domain overview + links to sub-skills
    references/               # Supporting docs, API specs, architecture diagrams
  marketing/
    SKILL.md                  # Marketing domain overview + links to sub-skills
    references/
  operations/
    SKILL.md                  # Ops procedures, vendor info, recurring tasks
    references/
  prompts/
    SKILL.md                  # Prompt spec library — meta-prompts for automation
    references/               # Individual prompt spec files
  raw/
    *.md                      # Unprocessed notes, articles, meeting dumps — AI organizes these
```

Every `SKILL.md` has:
- YAML frontmatter with `name`, `description`, and `related_skills` (cross-references)
- Self-contained content that can be understood alone
- Links to related skills via `related_skills` in frontmatter (the agent follows these)

## How to Build It

### Step 1: Scaffold the graph

Create the folder structure and INDEX.md. Each domain gets a SKILL.md with frontmatter.

Use `write_file` to create each file. The INDEX.md is the entry point:

```markdown
# Company Knowledge Graph

## Domains
- **engineering** — Tech stack, architecture decisions, deployment procedures, code review standards
- **marketing** — Positioning, content pipeline, campaign patterns, audience segments
- **operations** — Vendor management, financial procedures, hiring processes, legal
- **prompts** — Prompt specs for automated workflows (see related: prompt-spec-library)

## How to Use
Load any domain with `skill_view("company/<domain>")`.
Load supporting files with `skill_view("company/<domain>", "references/<file>.md")`.
Drop unprocessed material into `raw/` and run the compile procedure below.
```

### Step 2: Fill the raw folder

Dump everything unorganized into `raw/`:
- Meeting notes
- Articles and research
- Competitor analysis
- Product ideas
- Process docs from other tools
- Pasted Slack/email threads

Don't organize it. That's the AI's job.

### Step 3: Compile raw → skills

Read everything in `raw/`. For each piece of raw material:
1. Identify which domain it belongs to (engineering, marketing, ops, prompts)
2. Extract the durable knowledge (facts, procedures, decisions — not transient context)
3. Either update an existing domain SKILL.md or create a new sub-skill
4. Add `related_skills` cross-references where topics connect across domains
5. Update INDEX.md if new sub-skills were created

### Step 4: Query the graph

The agent reads INDEX.md, follows `related_skills` links, and loads only what the current task requires. This is progressive disclosure:

```
INDEX.md → domain SKILL.md → references/*.md → specific content
```

Most decisions happen before reading a single full reference file.

## Maintenance Procedures

### Daily Compile (Cron)

```
Schedule: 0 22 * * *
Prompt: Review today's sessions via session_search. Extract new procedures,
decisions, or domain knowledge. Update the relevant skill in the company
knowledge graph. If a new topic emerged, create a sub-skill. If nothing
new, respond with [SILENT].
Skill: company-knowledge-graph
```

### Weekly Health Check (Cron)

```
Schedule: 0 18 * * 0
Prompt: Review the company knowledge graph. Flag:
1. Skills with outdated information
2. Cross-references (related_skills) that point to nonexistent skills
3. Topics mentioned in skills but never explained in their own skill
4. Domains with no updates in 2+ weeks
5. Raw files that haven't been compiled yet
Suggest 3 new skills that would fill gaps.
Skill: company-knowledge-graph
```

### Monthly Trace Review (Cron)

```
Schedule: 0 10 1 * *
Prompt: Search session history for the past 30 days. Identify:
1. Tasks requiring 10+ tool calls → candidates for prompt automation
2. Recurring user questions → candidates for skills or cron jobs
3. Prompt specs that produced bad output → candidates for revision
4. Skills loaded but unhelpful → candidates for rewrite
Produce a structured improvement report and save to raw/ for next compile.
Skill: company-knowledge-graph
```

## Graph Traversal Rules

When navigating the skill graph:
- **Start at INDEX.md** for broad queries about the company
- **Go directly to domain SKILL.md** when the domain is known
- **Follow `related_skills`** when the answer spans multiple domains
- **Load `references/`** only when you need specific details (API specs, templates, data)
- **Never load everything** — progressive disclosure means loading only what the current task requires

## Memory Contract

Save to memory:
- The current state of the skill graph (which domains exist, last update dates)
- Known gaps that need filling
- User's priorities for which domains to maintain first

Don't save:
- Actual knowledge graph content (that lives in the skill files)
- Temporary raw material summaries
- Individual compile/health-check results

## Relationship to Other Skills

This skill works with:
- **operations-assistant** — uses the knowledge graph to ground delegation and prompt engineering in company context
- **prompt-spec-library** — prompt specs are a sub-domain of the knowledge graph, stored under `prompts/`
