# Claude / Coding Agent Context

This file carries repo-local instructions for Claude-style coding agents working in the Hermes Agent checkout.

## William real Chrome routing

For any browser-dependent task, first discover, inventory, and reuse William's already-open real Chrome/CDP/browser-harness sessions before opening or navigating anything. This is mandatory every single time, especially for Instagram, Threads, Gmail, Google, Higgsfield, Atlas, media downloads, screenshots, scraping, and any account-specific workflow. The goal is to avoid tab/profile spam and avoid losing logged-in state. Do not rely on one hardcoded port; inventory every available open CDP/browser target first.

Required routing checklist before any browser action:

1. Update the working inventory scratch file before the browser task: `$HERMES_HOME/browser-cdp-inventory.md` for the active profile, currently `/Users/chen/.hermes/profiles/intern/browser-cdp-inventory.md`. Preferred helper: `/Users/chen/.hermes/shared/scripts/update_browser_cdp_inventory.py --note '<before task>'`.
2. Inspect all already-open CDP/browser-harness targets first. Start with env-provided CDP URLs such as `BU_CDP_URL` / `BROWSER_CDP_URL`, scan common local CDP ports, run `browser-harness --doctor`, `browser-harness -c 'print(list_tabs())'`, query `/json/version` and `/json/list` on every responding CDP endpoint, and use AppleScript tab URL enumeration when available.
3. Enumerate existing Chrome tabs and CDP targets before `browser_navigate`, browser-harness `new_tab()`, `goto_url()`, or launching/using any new browser/profile.
4. If a matching logged-in tab or profile is already open, attach to that target and continue there. Do not open a fresh Chrome profile, Browserbase/cloud browser, generic unauthenticated browser session, or a new tab that loses login state.
5. Only open a new tab/profile after confirming no matching logged-in CDP target exists, and only if the user explicitly asks or approves that fallback.
6. If blocked by Google/Chrome/passkey/auth or remote-debugging approval, report the exact blocker and ask William to unlock or approve the existing tab/profile. Do not silently fall back to a logged-out browser.
7. Update `$HERMES_HOME/browser-cdp-inventory.md` again after the browser task with changed URLs, new tabs, closed tabs, selected target, and any blocker.

If William says the page/browser/tab is already open, treat that as authoritative. Attach to the existing tab/context first. Never route around this by opening a fresh logged-out browser.

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
