---
name: touchdown-outreach-tone
description: "Use when writing or revising Touchdown Labs cold emails and LinkedIn posts/DMs for William. Voice: technical founder to technical founder, useful-first, open-source tooling, diagnostics, benchmarks, no salesy consulting tone."
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [touchdown-labs, outbound, cold-email, linkedin, sales, tone]
    related_skills: [outbound-campaign]
---

# Touchdown Labs Voice MVP — Cold Emails + LinkedIn

## Core voice

Write like a technical founder talking to another technical founder.

Direct. Useful. Specific.

No fluff. No corporate tone. No fake hype. No over-explaining. No “would love to hop on a call” energy. No broad “AI transformation” language. No hard-sell consulting posture.

The copy should feel like:

```text
I’m building useful open-source tooling around real AI workloads. I want to understand what actually matters, then help teams cut cost, latency, and complexity.
```

## Main positioning

Touchdown Labs builds open-source CLI tools, diagnostics, benchmarks, and research to help teams understand and improve AI workloads.

We care about:

- AI inference cost
- workflow complexity
- latency
- retries
- routing
- API vs self-hosted decisions
- GPU infrastructure
- KV cache / LMCache / prefix caching
- workload-specific kernel optimization
- cost per completed workflow, not just cost per model call

Simple version:

```text
We help teams find where AI workflows get expensive and hard to run.
```

More technical version:

```text
We build open-source diagnostics and benchmarks for AI inference workloads, from APIs to self-hosted GPUs and kernels.
```

Helpful-first version:

```text
We’re building tooling that helps teams diagnose and reduce AI workflow cost themselves. If deeper help is useful later, we can help there too.
```

## What not to sound like

Do not sound like:

```text
We are an AI transformation consultancy helping enterprises unlock value through AI infrastructure optimization.
```

Do not sound like:

```text
I’d love to connect and explore synergies.
```

Do not sound like:

```text
You probably have hidden inefficiencies in your stack.
```

Do not sound like:

```text
We can reduce your inference spend by 40%.
```

That feels fake, salesy, or condescending.

## Email goal

First-touch emails should not hard sell.

They should:

1. Identify the company’s real AI workload.
2. Show we understand the workflow.
3. Explain we are building open-source tooling around that workload.
4. Ask what would actually help their team benchmark or diagnose it.
5. Softly mention deeper help only at the end.

The goal is customer discovery + useful tooling.

Not:

```text
Can I sell you consulting?
```

Better:

```text
What would actually make this easier for your team to benchmark or diagnose?
```

## Best cold email template

```text
Hi {first_name},

We’re building open-source CLI tools, diagnostics, and benchmarks to help teams cut AI inference cost and complexity themselves.

For {niche}, I want the tooling to reflect real production workflows, not generic AI tests.

{company} looks like the right pattern: {specific_workflows}.

What would actually make this easier for your team to benchmark or diagnose: {diagnostic_options}, or something else?

If deeper help is useful later, we can help there too — but the first goal is making the tooling useful.

William
```

Subject pattern:

```text
{workload} workloads
```

## Example — Paratus

Subject:

```text
Healthcare voice workloads
```

Email:

```text
Hi Pablo,

We’re building open-source CLI tools, diagnostics, and benchmarks to help teams cut AI inference cost and complexity themselves.

For healthcare voice, I want the tooling to reflect real production workflows, not generic AI tests.

Paratus looks like the right pattern: patient calls, intake, scheduling, insurance checks, no-shows, documentation, and EHR workflows.

What would actually make this easier for your team to benchmark or diagnose: cost per completed call, latency, retries, fallback routing, EHR/tool delays, or something else?

If deeper help is useful later, we can help there too — but the first goal is making the tooling useful.

William
```

## Email principles

### Assume competence

Do not write like the team is broken.

Bad:

```text
You are probably wasting money on AI inference.
```

Better:

```text
What would actually make this easier for your team to benchmark or diagnose?
```

### Be workload-specific

Bad:

```text
Are AI costs a problem?
```

Better:

```text
What would actually help benchmark cost per completed patient call, retries, fallback routing, or EHR/tool delays?
```

### Ask for useful input

Bad:

```text
Do you have 15 minutes?
```

Better:

```text
What would actually make this useful for your team?
```

### Frame assumptions clearly

Use:

- “{Company} looks like the right pattern…”
- “For {niche}, I want the tooling to reflect…”
- “What would actually make this easier…”

Avoid:

- “You probably…”
- “I noticed inefficiencies…”
- “You need…”
- “We can save you X%…”

## LinkedIn voice

LinkedIn should use the same useful-first posture.

Connection notes / DMs should be short, technical, and not needy. No “explore synergies.” No “would love to connect.” No fake compliment.

### LinkedIn connection note pattern

```text
Hey {first_name}, I’m building open-source diagnostics and benchmarks for {workload} inference workflows. {Company} looks like a useful production pattern. Curious what would actually help your team benchmark cost, latency, retries, or routing.
```

### Short LinkedIn DM pattern

```text
Hey {first_name}, quick context: we’re building open-source CLI tools and benchmarks for AI inference workloads.

For {niche}, I want the tests to reflect real production workflows, not generic model calls. {Company} looks close to that: {specific_workflows}.

What would actually help your team diagnose this: {diagnostic_options}, or something else?
```

### LinkedIn post pattern

Write like a build log / research note, not a launch announcement.

Structure:

1. Specific workload problem.
2. Why generic benchmarks miss it.
3. What Touchdown is building/measuring.
4. Ask builders/operators what would be useful.

Example skeleton:

```text
Most AI inference benchmarks still measure model calls.

But real workflows are messier: {workflow_specifics}.

For {niche}, we’re building open-source diagnostics around {metrics}: cost per completed workflow, latency, retries, fallback routing, cache behavior, and API vs self-hosted tradeoffs.

If you run this in production, what would actually be useful to benchmark?
```

## Workload adaptation bank

Pick the relevant workload and make the diagnostic options concrete.

### Voice / calls

Use nouns like:

- patient call
- intake
- scheduling
- insurance check
- no-show
- documentation
- EHR workflow
- STT/LLM/TTS handoff
- cost per completed call
- fallback routing
- interruption handling

Diagnostic options:

```text
cost per completed call, latency, retries, fallback routing, EHR/tool delays
```

### RAG / document AI

Use nouns like:

- document answer
- retrieval depth
- reranking
- repeated context
- long-context prefill
- source grounding
- cost per successful answer

Diagnostic options:

```text
retrieval depth, rerank latency, context size, repeated chunks missing cache, cost per successful answer
```

### Agent workflows

Use nouns like:

- completed task
- tool calls
- retry loops
- routing
- fallback policy
- context growth
- failed attempts

Diagnostic options:

```text
cost per completed task, tool-call retries, fallback routing, context growth, latency per workflow step
```

### Coding agents

Use nouns like:

- repo context
- patch attempts
- failed edits
- test loops
- tool-call retries
- long-context prefill

Diagnostic options:

```text
cost per accepted patch, repeated repo context, failed edits, test-loop retries, long-context latency
```

### Creative generation

Use nouns like:

- generation
- edit
- retry
- failed output
- queueing
- fallback model policy
- cost per accepted result

Diagnostic options:

```text
cost per accepted generation, retry rate, queue latency, fallback policy, API vs self-hosted routing
```

### Infra / GPU / self-hosted

Use nouns like:

- GPU utilization
- KV cache
- LMCache
- prefix cache
- batching
- queueing
- prefill/decode split
- kernel bottleneck
- cost per useful task

Diagnostic options:

```text
KV/cache behavior, batching, queue depth, prefill/decode bottlenecks, GPU timelines, cost per useful task
```

## Technical detail rules

Use technical terms only when they help the recipient recognize the workload.

Good:

```text
cost per completed call, latency, retries, fallback routing, EHR/tool delays
```

Good:

```text
KV/cache behavior, queue depth, prefill/decode bottlenecks, and cost per useful task
```

Bad:

```text
We optimize speculative decoding, KV cache, LMCache, prefix caching, offload, routing, kernels, batching, GPUs, and observability.
```

Do not dump buzzwords. Pick 3-5 diagnostic options tied to the workload.

## Common pitfalls

1. Hard-selling consulting too early. The first goal is useful tooling and customer discovery.
2. Sounding like a consultancy. Never use “AI transformation,” “unlock value,” or “explore synergies.”
3. Talking down to the recipient. Assume they are competent.
4. Making fake certainty claims. Avoid “you probably have hidden inefficiencies.”
5. Making fake ROI claims. No “40% savings” unless user provides verified proof.
6. Writing generic AI cost copy. Always name the workload.
7. Asking for a call as the main CTA. Ask what would actually help them benchmark or diagnose.
8. Over-explaining inference. The recipient is technical.
9. Overloading the email with mechanisms. Pick the relevant diagnostic options.
10. Forgetting the open-source tooling frame.

## Verification gate for outbound

Before writing or drafting outreach for real recipients, verify provenance for factual claims. Do not rely on model memory for names, titles, emails, stack details, or workload claims.

Required before Gmail draft creation:

- Person + title has a source URL or is user-supplied.
- Email is verified from a source, CRM, user-supplied list, or email verification tool. Pattern guesses are not verified unless William explicitly approves.
- Company/workload claim has a source URL/excerpt, user-supplied evidence, or the copy explicitly frames it as an assumption.
- Keep a skimmable source ledger separating verified, inferred, not found, and user-supplied facts.
- If a source has no link or durable artifact, mark it inferred or not found.
- Draft safety and send safety should be explicit.

Skimmable display format:

```text
## Company — Contact
- Indexed: YYYY-MM-DDTHH:MM:SSZ
- Verified: source-backed or user-supplied facts with links
- Inferred: assumptions/predictions, clearly labeled
- Not found: missing email/contact/stack evidence
- Draft/send: safe_to_draft={true|false}; safe_to_send={true|false}; reason
```

## Final checklist

- [ ] Technical founder to technical founder
- [ ] Useful-first, open-source tooling frame
- [ ] Workload-specific
- [ ] Assumes competence
- [ ] Asks what would help benchmark or diagnose
- [ ] Mentions deeper help only softly at the end, if at all
- [ ] No corporate tone
- [ ] No fake hype
- [ ] No fake ROI claims
- [ ] No “would love to hop on a call” energy
- [ ] No “explore synergies”
- [ ] No “you probably have hidden inefficiencies”
- [ ] No generic AI transformation language
- [ ] LinkedIn is short and direct
- [ ] Email goal is customer discovery + useful tooling
