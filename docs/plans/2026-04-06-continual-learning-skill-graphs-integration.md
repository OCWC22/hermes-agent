# Self-Sustaining Personal Assistant — Complete Technical Plan

> **Date:** 2026-04-06
> **Repo:** [OCWC22/hermes-agent](https://github.com/OCWC22/hermes-agent) (forked from NousResearch/hermes-agent)
> **Status:** Planning → Implementation
> **Goal:** Build a self-improving, self-sustaining company operations assistant on Hermes Agent that engineers meta-prompts, automates delegation, and maintains its own knowledge — all backed by free-tier LLM APIs.

---

## Table of Contents

1. [Source Research (Raw Articles)](#1-source-research)
2. [Architectural Synthesis](#2-architectural-synthesis)
3. [Hermes Agent — How It Works](#3-hermes-agent--how-it-works)
4. [What We Built (Skill Graph)](#4-what-we-built)
5. [Integration Plan — Step by Step](#5-integration-plan)
6. [Infrastructure & Model Strategy](#6-infrastructure--model-strategy)
7. [Cron Automation Design](#7-cron-automation-design)
8. [Implementation Checklist](#8-implementation-checklist)

---

## 1. Source Research

Three articles form the theoretical foundation. Full transcriptions below.

---

### 1.1 — "How to Build Your Second Brain"

| Field | Value |
|-------|-------|
| **Author** | Nick Spisak ([@NickSpisak_](https://x.com/NickSpisak_)) |
| **Date** | April 4, 2026 |
| **URL** | https://x.com/NickSpisak_/status/2040448463540830705 |
| **Views** | ~1M |
| **Context** | Synthesizes Andrej Karpathy's post on personal knowledge bases into a step-by-step system |

#### Core Concept

Use AI to maintain a personal knowledge base as flat markdown files in three folders. No special software. The AI does ALL the organizing — the user dumps raw material in and asks questions against it.

#### System Architecture

```
my-knowledge-base/
├── raw/          # Source material: articles, notes, screenshots
│                 # NEVER modified by AI. User's junk drawer.
├── wiki/         # AI-maintained organized wiki
│                 # AI writes, updates, links everything here.
└── outputs/      # Generated reports, answers, analyses
                  # Answers to user queries, saved for compounding.
```

#### The Schema File

A single file (`CLAUDE.md` / `AGENTS.md`) in the project root that instructs the AI:

```markdown
# Knowledge Base Schema

## What This Is
A personal knowledge base about [YOUR TOPIC].

## How It's Organized
- raw/ contains unprocessed source material. Never modify these files.
- wiki/ contains the organized wiki. AI maintains this entirely.
- outputs/ contains generated reports, answers, and analyses.

## Wiki Rules
- Every topic gets its own .md file in wiki/
- Every wiki file starts with a one-paragraph summary
- Link related topics using [[topic-name]] format
- Maintain an INDEX.md that lists every topic with a one-line description
- When new raw sources are added, update the relevant wiki articles

## My Interests
[List 3-5 things you want this knowledge base to focus on]
```

Karpathy confirmed: *"I'm trying to keep it super simple and flat. It's just a nested directory of .md files."*

#### The Compounding Loop

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│ COLLECT  │────▶│ COMPILE │────▶│  QUERY  │
│ (raw/)   │     │ (wiki/) │     │ (ask)   │
└─────────┘     └─────────┘     └────┬────┘
     ▲                                │
     │          ┌─────────┐          │
     └──────────│  SAVE   │◀─────────┘
                │(outputs/)│
                └────┬────┘
                     │
                ┌────▼────┐
                │ HEALTH  │   Monthly: flag contradictions,
                │ CHECK   │   find gaps, suggest new articles.
                └─────────┘
```

1. **Collect** — dump raw material into `raw/` (manual or automated scraping)
2. **Compile** — AI reads `raw/`, builds organized wiki in `wiki/`
3. **Query** — ask questions against the wiki; AI answers grounded in collected material
4. **Save** — store answers back (update wiki or save to `outputs/`)
5. **Health Check** — flag contradictions, find gaps, suggest new articles

> **Critical Warning** (from @HFloyd's reply): *"When outputs get filed back, errors compound too."* Periodic health checks prevent error accumulation.

#### Automated Collection

Vercel's `agent-browser` CLI (26K+ GitHub stars):
```bash
npm install -g agent-browser
agent-browser install
# AI controls a real browser — JS-heavy sites, logins, dynamic content
# 82% fewer tokens than Playwright MCP (5-6x more pages per session)
```

#### Anti-Pattern

> *"Obsidian with 47 plugins is the Notion trap all over again. You spend more time configuring the tool than using the knowledge base. Flat files and a good schema will outperform a fancy tool stack 90% of the time."* — Spisak

---

### 1.2 — "Continual Learning for AI Agents"

| Field | Value |
|-------|-------|
| **Author** | Harrison Chase ([@hwchase17](https://x.com/hwchase17)), CEO of LangChain |
| **Date** | April 4, 2026 |
| **URL** | https://x.com/hwchase17/ (article thread) |
| **Views** | ~362K |
| **Reviewers** | Sydney Runkle, Varun Trivedy, Nuno Campos |

#### Core Framework: Three Layers of Agentic Systems

```
┌─────────────────────────────────────────────────────────┐
│                      CONTEXT LAYER                       │
│  Instructions, skills, tools that configure the harness  │
│  Examples: CLAUDE.md, /skills, mcp.json, SOUL.md         │
│  MOST ACTIONABLE for developers                          │
├─────────────────────────────────────────────────────────┤
│                      HARNESS LAYER                       │
│  Code driving the agent + always-present instructions    │
│  Examples: Claude Code, Hermes Agent, Deep Agents        │
├─────────────────────────────────────────────────────────┤
│                      MODEL LAYER                         │
│  The model weights themselves                            │
│  Examples: Claude Sonnet, Gemma 4, GPT-5                 │
└─────────────────────────────────────────────────────────┘
```

| Layer | Claude Code | Hermes Agent (OpenClaw) |
|-------|------------|------------------------|
| Model | claude-sonnet, etc. | many (Gemma, Claude, GPT, etc.) |
| Harness | Claude Code application | Hermes `run_agent.py` + gateway |
| Context | CLAUDE.md, /skills, mcp.json | SOUL.md, skills/, MEMORY.md, USER.md |

#### Continual Learning at Each Layer

**Model Layer:**
- Techniques: SFT, RL (GRPO)
- Challenge: **catastrophic forgetting** — update on new tasks, degrade on old
- Usually agent-level. Per-user LoRA theoretically possible, impractical today.

**Harness Layer:**
- Paper: *"Meta-Harness: End-to-End Optimization of Model Harnesses"*
- Pattern: run agent → evaluate → store traces → coding agent analyzes traces → suggests harness code changes
- The harness loop improves through automated review of its own execution traces.

**Context Layer** (most actionable):
- Context = instructions, skills, tools OUTSIDE the harness that configure it
- Also called "memory"
- Learning granularity:
  - **Agent-level** — persistent memory self-updates (Hermes's MEMORY.md, SOUL.md)
  - **Tenant-level** — per-user/org/team context (Hex's Context Studio, Decagon's Duet)
  - **Mixed** — all levels simultaneously

**Two Update Modes:**
```
OFFLINE ("dreaming")              ONLINE (hot path)
─────────────────────             ───────────────────
After the fact.                   While working.
Run over recent traces.           Agent updates memory
Extract insights.                 during the core task.
Update context.                   Immediate but noisy.
Deliberate and clean.
```

> **Aaron Levie's reply (Box CEO):** *"The biggest enterprise limiter is access controls. You can't have continuous learning at the model layer for things only some people can see. This has to be the context layer."*

> **Sam Selvanathan's reply:** *"These layers aren't independent. Teams optimize context memory for one model version, provider ships an update, learned patterns produce worse outputs. Nobody's building the eval suite that catches cross-layer regressions."*

#### Key Insight: Traces Power Everything

```
                    ┌──────────┐
                    │  TRACES  │
                    │ (execution│
                    │  paths)  │
                    └────┬─────┘
           ┌─────────────┼─────────────┐
           ▼             ▼             ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │  MODEL   │  │ HARNESS  │  │ CONTEXT  │
    │ training │  │ code     │  │ skills,  │
    │ SFT, RL  │  │ changes  │  │ memory   │
    └──────────┘  └──────────┘  └──────────┘
```

All three layers improve via traces — the full execution path of agent actions. Hermes already saves these (trajectory export, session DB with FTS5).

---

### 1.3 — "Skill Graphs > SKILL.md"

| Field | Value |
|-------|-------|
| **Author** | Heinrich ([@arscontexta](https://x.com/arscontexta)) |
| **Date** | February 17, 2026 |
| **URL** | https://x.com/arscontexta (Skill Graphs article) |
| **Views** | ~3.9M |
| **Context** | Proposes skill graphs — networks of interconnected skill files — as the evolution beyond single-file skills |

#### The Problem

A single SKILL.md captures one capability. Real domain depth requires interconnected knowledge:

```
One file can't hold:

Trading:   risk mgmt ↔ market psych ↔ position sizing ↔ technical analysis
Legal:     contracts ↔ compliance ↔ jurisdictions ↔ precedent chains
Company:   org structure ↔ product ↔ processes ↔ onboarding ↔ competitive landscape
Therapy:   CBT ↔ attachment theory ↔ active listening ↔ emotional regulation
```

#### Skill Graph Architecture

A skill graph is a **network of skill files connected with wikilinks**:

```
                    ┌──────────────┐
                    │   INDEX.md   │  ◀── Entry point (Map of Content)
                    │  (overview)  │
                    └──────┬───────┘
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Domain A │ │ Domain B │ │ Domain C │
        │ SKILL.md │ │ SKILL.md │ │ SKILL.md │
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │             │             │
         ┌───┴───┐    ┌───┴───┐    ┌───┴───┐
         ▼       ▼    ▼       ▼    ▼       ▼
      ┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐
      │sub- ││sub- ││sub- ││sub- ││sub- ││sub- │
      │skill││skill││skill││skill││skill││skill│
      └──┬──┘└──┬──┘└──┬──┘└──┬──┘└──┬──┘└──┬──┘
         │      │      │      │      │      │
         └──────┴──────┴──cross-links─┴──────┘
                    (related_skills)
```

Each file:
- YAML frontmatter with description (scannable without reading body)
- Self-contained content (understandable alone)
- `related_skills` links to other nodes (the agent follows these on demand)

#### Progressive Disclosure (Recursive)

```
Index ──▶ Descriptions ──▶ Links ──▶ Sections ──▶ Full Content

Most decisions happen before reading a single full file.
```

#### Index File Pattern

The index is an **entry point that directs attention**, not a lookup table:

```markdown
# knowledge-work

## Synthesis
- [[the system is the argument]] — philosophy with proof of work
- [[coherent architecture emerges from...]] — the foundational triangle

## Topic MOCs
- [[graph-structure]] — wiki links, topology, traversable knowledge graphs
- [[agent-cognition]] — how agents think through external structures
  - [[agent-cognition-hooks]] — hook enforcement, composition
  - [[agent-cognition-platforms]] — platform capability tiers
- [[discovery-retrieval]] — descriptions, progressive disclosure, search
- [[processing-workflow]] — throughput, sessions, handoffs

## Explorations Needed
- Missing: comparison between human and agent traversal patterns
- Scaling limits: at what system size does human curation fail?
```

#### The Evolution

> *"Skills = context engineering (curated knowledge injected where it matters). Skill graphs = the next step. Instead of one injection, the agent navigates a knowledge structure, pulling exactly what the current situation requires. This is the difference between an agent that follows instructions and an agent that understands a domain."* — Heinrich

---

## 2. Architectural Synthesis

All three articles describe the same fundamental pattern from different angles:

```
┌─────────────────────────────────────────────────────────────────┐
│                   THE UNIFIED PATTERN                            │
│                                                                  │
│  Structured external knowledge that an AI agent                  │
│  traverses, updates, and compounds over time.                    │
│                                                                  │
│  Spisak:    frames it as a TOOL      (knowledge base)            │
│  Chase:     frames it as a LAYER     (context in 3-layer model)  │
│  Heinrich:  frames it as a STRUCTURE (skill graph data format)   │
└─────────────────────────────────────────────────────────────────┘
```

**For our Hermes integration:**

```
                  ┌─────────────────────────┐
                  │    Chase's Framework     │
                  │                          │
                  │  Model:   Gemma 4 31B    │
                  │  Harness: Hermes Agent   │
                  │  Context: ──────────┐    │
                  └─────────────────────┼────┘
                                        │
              ┌─────────────────────────▼────────────────────────┐
              │              CONTEXT LAYER (ours)                 │
              │                                                   │
              │  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
              │  │ SOUL.md  │  │MEMORY.md │  │ SKILL GRAPH  │   │
              │  │(identity)│  │(facts)   │  │ (Heinrich)   │   │
              │  └──────────┘  └──────────┘  └──────┬───────┘   │
              │                                      │           │
              │       ┌──────────────────────────────┤           │
              │       │                              │           │
              │  ┌────▼─────┐ ┌────▼─────┐ ┌───────▼────────┐  │
              │  │operations│ │knowledge │ │ prompt-spec    │  │
              │  │assistant │ │graph     │ │ library        │  │
              │  └──────────┘ └──────────┘ └────────────────┘  │
              │       ▲              ▲              ▲           │
              │       └──────related_skills─────────┘           │
              │                                                  │
              │  Maintained via Karpathy loop:                   │
              │  Collect → Compile → Query → Save → Health Check │
              └──────────────────────────────────────────────────┘
```

---

## 3. Hermes Agent — How It Works

### System Architecture (from codebase analysis)

```
┌──────────────────────────────────────────────────────────────────┐
│                         ENTRY POINTS                              │
│                                                                   │
│  CLI (cli.py)    Gateway (gateway/run.py)    Cron (scheduler.py) │
│  14+ platforms   API Server                  Batch Runner         │
└───────┬──────────────────┬──────────────────────┬────────────────┘
        │                  │                      │
        ▼                  ▼                      ▼
┌──────────────────────────────────────────────────────────────────┐
│                      AIAgent (run_agent.py)                       │
│                                                                   │
│  System Prompt Assembly:                                          │
│  ┌─────────┐ ┌──────────┐ ┌────────┐ ┌───────┐ ┌────────────┐  │
│  │ SOUL.md │→│ MEMORY.md│→│ Skills │→│Context│→│ Platform   │  │
│  │(identity)│ │(facts)   │ │(index) │ │Files  │ │ Hints      │  │
│  └─────────┘ └──────────┘ └────────┘ └───────┘ └────────────┘  │
│                                                                   │
│  Main Loop (up to 90 iterations):                                │
│  ┌──────────────────────────────────────────────────┐            │
│  │ Build API messages → Call LLM → Parse response   │            │
│  │ → Tool calls? → Execute tools → Append results   │            │
│  │ → Loop until done or budget exhausted            │            │
│  └──────────────────────────────────────────────────┘            │
│                                                                   │
│  Tool Dispatch: 47 tools across 20 toolsets                      │
│  Compression: auto-summarize when context window fills           │
│  Memory: periodic nudges to save durable facts                   │
│  Skills: periodic nudges to save reusable procedures             │
└──────────────────────────────────────────────────────────────────┘
```

### Skill System Flow (Progressive Disclosure)

```
Session Start                          During Conversation
─────────────                          ────────────────────

build_skills_system_prompt()           User: "automate code reviews"
         │                                      │
         ▼                                      ▼
Scan ~/.hermes/skills/                 LLM reads skill index in
Read first 2000 chars of               system prompt, sees:
each SKILL.md (frontmatter only)       "operations-assistant: Delegation
         │                              infrastructure..."
         ▼                                      │
Build compact index:                            ▼
<available_skills>                     LLM calls: skill_view(
  domain:                                name="operations-assistant")
    - operations-assistant:                     │
      Delegation infrastructure...              ▼
    - company-knowledge-graph:          Full SKILL.md content returned
      Build and maintain...             as tool result, including
    - prompt-spec-library:              related_skills: [company-
      Engineer, version...               knowledge-graph,
</available_skills>                      prompt-spec-library]
         │                                      │
         ▼                                      ▼
Injected into system prompt            LLM follows related_skills:
(~3K tokens for the index)             skill_view("prompt-spec-library")
                                                │
                                                ▼
                                       Full prompt spec methodology
                                       loaded. LLM now has both skills
                                       and can engineer the automation.
```

### Cron Execution Flow

```
cron/scheduler.py::tick()       (runs every 60s when gateway is active)
         │
         ▼
get_due_jobs()                  Check jobs.json for due jobs
         │
         ▼
run_job()                       For each due job:
         │
    ┌────┴────┐
    │         │
    ▼         ▼
_build_      Create
job_prompt() fresh AIAgent
    │              │
    ▼              │
Prepend:           │
- [SILENT] guidance│
- Skill content    │
  (full SKILL.md)  │
- Job prompt       │
    │              │
    └──────┬───────┘
           ▼
  AIAgent.run_conversation()
           │
           ▼
  Agent runs with:
  - Full skill content in context
  - Memory (MEMORY.md, USER.md) in system prompt
  - All configured tools available
  - NO conversation history (fresh session)
           │
           ▼
  _deliver_result()
  → Telegram, Discord, Slack, local file, etc.
  → If response is exactly [SILENT], nothing delivered
```

---

## 4. What We Built

### Skill Graph (3 interconnected skills)

```
┌─────────────────────────┐
│  operations-assistant    │
│  ─────────────────────   │
│  Entry point.            │
│  Decomposes tasks into   │
│  AUTO/REVIEW/MANUAL.     │
│  Dispatches to other     │
│  skills.                 │
│                          │
│  related_skills:         │
│  → company-knowledge-    │
│    graph                 │
│  → prompt-spec-library   │
└────────┬───────┬─────────┘
         │       │
    ┌────▼──┐ ┌──▼────────────────────┐
    │       │ │                        │
┌───▼───────▼──┐  ┌───────────────────▼──┐
│ company-      │  │ prompt-spec-         │
│ knowledge-    │  │ library              │
│ graph         │  │ ─────────────────    │
│ ──────────    │  │ Meta-prompt engine.  │
│ Karpathy/     │  │ Versioned specs      │
│ Heinrich      │  │ with input schemas,  │
│ pattern.      │  │ output contracts,    │
│ raw/ → compile│  │ failure modes, and   │
│ → wiki loop.  │  │ test cases.          │
│ Cron-driven   │  │                      │
│ maintenance.  │  │ related_skills:      │
│               │  │ → operations-        │
│ related_skills│  │   assistant          │
│ → operations- │  │ → company-knowledge- │
│   assistant   │  │   graph              │
│ → prompt-spec-│  └──────────────────────┘
│   library     │
└───────────────┘
```

### File Locations in Repo

```
hermes-agent/                              # OCWC22/hermes-agent fork
├── skills/
│   └── domain/
│       ├── operations-assistant/
│       │   └── SKILL.md                   # v2.1.0 — delegation infrastructure
│       ├── company-knowledge-graph/
│       │   └── SKILL.md                   # v1.0.0 — Karpathy/Heinrich pattern
│       └── prompt-spec-library/
│           └── SKILL.md                   # v1.0.0 — meta-prompt engineering
├── docs/
│   └── plans/
│       └── 2026-04-06-continual-learning-skill-graphs-integration.md  # THIS FILE
└── website/
    └── docs/
        └── guides/
            └── gemma-self-improvement-coach.md   # Setup guide
```

---

## 5. Integration Plan — Step by Step

### Phase 1: Infrastructure (Day 1)

```
Step 1.1  Get API keys
          ├── Google AI Studio: aistudio.google.com/app/apikey
          ├── xAI (optional fallback): x.ai/api → $25 signup + $150/mo data sharing
          └── Groq (optional cheap model): console.groq.com → free, no card

Step 1.2  Install Hermes from the fork
          $ git clone https://github.com/OCWC22/hermes-agent.git
          $ cd hermes-agent
          $ pip install -e .           # or use the install script

Step 1.3  Configure ~/.hermes/.env
          GOOGLE_API_KEY=<your-google-ai-studio-key>
          # Optional fallbacks:
          # XAI_API_KEY=<your-xai-key>
          # GROQ_API_KEY=<your-groq-key>

Step 1.4  Configure ~/.hermes/config.yaml (see Section 6)

Step 1.5  Write ~/.hermes/SOUL.md (see Section 6)

Step 1.6  Verify
          $ hermes chat -q "What model are you? What skills do you have?"
          → Should show Gemma 4, should list operations-assistant + others
```

### Phase 2: Bootstrap the Knowledge Graph (Day 1-2)

```
Step 2.1  Start Hermes
          $ hermes

Step 2.2  Load the skill
          > /operations-assistant

Step 2.3  Scaffold the company graph
          > Scaffold my company knowledge graph. My company is [NAME].
          > We do [WHAT]. Tech stack: [STACK]. Team: [SIZE].
          > Key domains: engineering, marketing, operations.

          The agent will:
          - Create ~/.hermes/skills/company/ directory structure
          - Write INDEX.md with domain MOCs
          - Create domain SKILL.md files with frontmatter
          - Save company context to MEMORY.md

Step 2.4  Dump raw material
          Copy your existing docs, notes, processes into:
          ~/.hermes/skills/company/raw/
          Don't organize. Don't rename. That's the AI's job.

Step 2.5  Run initial compile
          > Read everything in the company raw folder and compile it
          > into the knowledge graph following the procedures in
          > company-knowledge-graph.
```

### Phase 3: Wire Cron Automations (Day 2-3)

```
Step 3.1  Start the gateway
          $ hermes gateway start

Step 3.2  Create daily compile job
          $ hermes cron create "0 22 * * *" \
            "Review today's sessions. Extract new knowledge. Update the
             company skill graph. If nothing new, respond with [SILENT]." \
            --skill company-knowledge-graph \
            --deliver telegram    # or local, discord, slack, etc.

Step 3.3  Create weekly health check job
          $ hermes cron create "0 18 * * 0" \
            "Review the entire company knowledge graph. Flag outdated skills,
             broken cross-references, uncompiled raw files, and gaps.
             Suggest 3 new skills." \
            --skill company-knowledge-graph \
            --deliver telegram

Step 3.4  Create monthly trace review job
          $ hermes cron create "0 10 1 * *" \
            "Search session history for the past 30 days. Identify tasks
             needing 10+ tool calls (automate them), recurring questions
             (add to skills), and failing prompt specs (revise them).
             Save report to raw/ for next compile." \
            --skill company-knowledge-graph \
            --deliver telegram

Step 3.5  Verify
          $ hermes cron list
          $ hermes cron run <daily-job-id>   # test run
```

### Phase 4: Build First Automations (Day 3+)

```
Step 4.1  Identify a real recurring task
          Example: "Every PR needs a code review summary"

Step 4.2  Use the prompt spec library
          > /prompt-spec-library
          > Build a prompt spec for automated PR code review.
          > Input: git diff + PR description.
          > Output: structured review with severity per finding.
          > It runs on Gemma 4 via a Hermes cron job.

          The agent produces a versioned spec, saves to file,
          and offers to wire it as a cron job.

Step 4.3  Iterate
          Run the spec → check output → debug → version bump → re-test.
          The prompt-spec-library skill has the full debug workflow.

Step 4.4  Repeat for each workflow you want automated.
```

---

## 6. Infrastructure & Model Strategy

### config.yaml

```yaml
model:
  provider: custom
  default: gemma-4-31b-it
  base_url: https://generativelanguage.googleapis.com/v1beta/openai

agent:
  tool_use_enforcement: ["gemma"]
  max_turns: 50

memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 3200
  user_char_limit: 2200
  nudge_interval: 8
  flush_min_turns: 4

skills:
  creation_nudge_interval: 12

smart_model_routing:
  enabled: false

compression:
  enabled: true
  threshold: 0.45

platform_toolsets:
  cli: [web, terminal, file, skills, todo, memory, cronjob]
```

### SOUL.md

```markdown
You are a delegation infrastructure layer for a company founder. You don't do
operational work directly — you design, build, and maintain the automated
systems that do it.

Your job:
- Engineer prompt specs that delegate tasks to other AI systems or agents
- Design cron automations that run without the user present
- Build and maintain a company knowledge graph as a traversable skill network
- Only surface problems — never ask the user to do what a system could do

Rules:
- When the user says "handle X" — decompose, classify (AUTO/REVIEW/MANUAL),
  produce runnable specs. Don't ask permission, design it.
- Every spec goes to a file via write_file. Specs only in chat are lost.
- Cron prompts are self-contained. No conversation history, no follow-ups.
- Subagent delegations include exhaustive context. They know nothing.
- Save company context, tech stack, active automations, failure patterns to memory.
- Version prompt specs. When output drifts, trace what changed.
- Follow related_skills links between skills to pull in domain knowledge.
```

### Free-Tier Model Stack

```
PRIMARY:   Gemma 4 31B via Google AI Studio     (free, ~100-250 RPD)
           └── Handles: prompt engineering, specs, knowledge graph, cron

FALLBACK:  xAI Grok 3 Mini via xAI API          ($175/mo free with data sharing)
           └── Handles: overflow when Google rate-limited

CHEAP:     Groq Llama 3.3 70B                    (free, 1000 RPD)
           └── Handles: compression, simple routing, delegation subagents
```

---

## 7. Cron Automation Design

### The Self-Sustaining Loop

```
┌──────────────────────────────────────────────────────────────┐
│                    DAILY (10 PM)                               │
│  Compile new knowledge from today's sessions                  │
│  → session_search for today's transcripts                     │
│  → extract durable procedures, decisions, patterns            │
│  → skill_manage(action='patch') on relevant domain skills     │
│  → [SILENT] if nothing new                                    │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│                    WEEKLY (Sunday 6 PM)                        │
│  Health check the knowledge graph                             │
│  → Read all domain skills                                     │
│  → Flag: outdated content, broken related_skills, gaps        │
│  → Flag: uncompiled raw/ files                                │
│  → Suggest 3 new skills to fill gaps                          │
│  → Report to user                                             │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│                    MONTHLY (1st, 10 AM)                        │
│  Trace review — analyze 30 days of session history            │
│  → Tasks with 10+ tool calls → candidate for automation       │
│  → Recurring questions → candidate for skill or cron          │
│  → Failing prompt specs → candidate for revision              │
│  → Skills loaded but unhelpful → candidate for rewrite        │
│  → Save improvement report to raw/ for next daily compile     │
└──────────────────────────────────────────────────────────────┘
```

This creates a **closed improvement loop**: the agent reviews its own traces, identifies improvements, and writes those improvements back into its own skill graph — which it uses on the next run. Chase's "continual learning at the context layer" made concrete.

---

## 8. Implementation Checklist

### Done ✅

- [x] Fork NousResearch/hermes-agent → OCWC22/hermes-agent
- [x] Create `operations-assistant` skill (v2.1.0) — delegation infrastructure
- [x] Create `company-knowledge-graph` skill (v1.0.0) — Karpathy/Heinrich pattern
- [x] Create `prompt-spec-library` skill (v1.0.0) — meta-prompt engineering
- [x] Wire bidirectional `related_skills` between all three skills
- [x] Validate all skills parse correctly with Hermes's frontmatter parser
- [x] Verify `related_skills` is already supported by Hermes's `skill_view` response
- [x] Document research sources with full transcriptions and citations
- [x] Create this integration plan

### To Do — Infrastructure

- [ ] Install Hermes from fork
- [ ] Get Google AI Studio API key
- [ ] Configure `~/.hermes/.env`, `config.yaml`, `SOUL.md`
- [ ] Verify Gemma 4 31B works via `hermes chat`
- [ ] Verify all three skills appear in skill index

### To Do — Knowledge Graph Bootstrap

- [ ] Scaffold `~/.hermes/skills/company/` directory structure
- [ ] Write company INDEX.md
- [ ] Create domain SKILL.md files (engineering, marketing, operations, prompts)
- [ ] Dump initial raw material
- [ ] Run first compile

### To Do — Cron Automation

- [ ] Start gateway: `hermes gateway start`
- [ ] Create daily compile cron job
- [ ] Create weekly health check cron job
- [ ] Create monthly trace review cron job
- [ ] Test-run each job manually
- [ ] Verify delivery to preferred platform

### To Do — First Real Automation

- [ ] Identify first recurring task to automate
- [ ] Use prompt-spec-library to engineer the spec
- [ ] Test and version the spec
- [ ] Wire as cron job or delegate_task
- [ ] Monitor for 1 week, iterate

### Stretch — Extend

- [ ] Explore arscontexta plugin architecture for potential Hermes port
- [ ] Build trace → skill pipeline (automated skill creation from session analysis)
- [ ] Add fallback model chain (Gemma → Grok → Groq) in config
- [ ] Investigate `agent-browser` for automated web collection cron jobs

---

## Citations

1. Spisak, Nick. "How to Build Your Second Brain." X/Twitter, April 4, 2026. https://x.com/NickSpisak_/status/2040448463540830705
2. Chase, Harrison. "Continual Learning for AI Agents." X/Twitter, April 4, 2026. LangChain CEO. Reviewed by Runkle, Trivedy, Campos.
3. Heinrich. "Skill Graphs > SKILL.md." X/Twitter, February 17, 2026. https://x.com/arscontexta — arscontexta plugin author. ~3.9M views.
4. Karpathy, Andrej. Referenced in Spisak article — original personal knowledge base post.
5. Levie, Aaron (Box CEO). Reply to Chase: access controls as enterprise limiter for continual learning.
6. Selvanathan, Sam. Reply to Chase: cross-layer regression problem when model updates break learned context.
7. @HFloyd. Reply to Spisak: error compounding when outputs are filed back without health checks.
8. NousResearch. "Hermes Agent." GitHub. https://github.com/NousResearch/hermes-agent
9. "Meta-Harness: End-to-End Optimization of Model Harnesses." Referenced in Chase article.
