# Claude / Coding Agent Context

This file carries repo-local instructions for Claude-style coding agents working in the Hermes Agent checkout.

## William real Chrome routing

For logged-in browser work, first discover and reuse William's already-open real Chrome/browser-harness sessions before opening or navigating a new tab/profile. Enumerate existing Chrome tabs and CDP targets first (`browser-harness --doctor`, AppleScript tab URLs, `/json/list` on active CDP ports). If William says the page/browser/tab is already open, attach to that existing tab/context and do not create a new Chrome profile, cloud browser, or unauthenticated CDP session. If blocked by Google/Chrome/passkey auth, report the exact blocker and ask William to unlock that existing tab/profile.

## Touchdown / William golden outreach standard

For Touchdown Labs, William-facing outreach, LinkedIn DMs, cold email, investor/customer notes, and inference-infra writing: assume the recipient is highly competent and already handling the obvious model/API-cost questions unless evidence says otherwise. Do not open with generic savings, audit, or token-cost copy unless William explicitly asks for service-first cold email.

Default golden LinkedIn/outreach shape:

```text
Not a pitch, but an inference research question. I’d assume {Company} already has obvious model/API cost handled. Curious where the biggest costs and latency are for you? {workflow loop}: {2-3 mechanisms}.
```

Alternate blunt API/self-host fork:

```text
Not pitching, but a research question for inference. Is inference cost an issue? If you use APIs, have you audited self-hosting? If you self-host, what optimizations are you having the most trouble with: vLLM, kernels, batching, KV cache, routing?
```

Extrapolate this rule across channels: competence assumption first, workflow-specific inference question second, 2-3 concrete mechanisms third, correction permission last. Offer tooling, workload replay, profiling, or a second set of eyes only after the useful question is clear.

## GBrain routing

For Touchdown Labs, William-facing writing, Hermes, OpenClaw, GBrain, inference infrastructure, vLLM, SGLang, LMCache, InferGuard, outreach, people, companies, meetings, investors, customers, technical decisions, and project status: search GBrain before answering. Save durable decisions, facts, technical findings, outreach outcomes, and reusable prompts back to GBrain.
