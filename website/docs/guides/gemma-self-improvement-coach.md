---
sidebar_position: 11
title: "Self-Improvement Coach with Gemma on AI Gateway"
description: "Set up Hermes Agent as a personal growth coach using Google's Gemma 4 31B via Vercel AI Gateway — free tier, persistent memory, scheduled check-ins"
---

# Self-Improvement Coach with Gemma on AI Gateway

This guide turns Hermes into a dedicated self-improvement agent using Google's Gemma 4 31B routed through Vercel AI Gateway's Bring Your Own Key (BYOK) feature. The result is a persistent coaching agent with daily/weekly check-ins, goal tracking, habit accountability, and memory that grows across sessions — at zero inference cost using Google AI Studio's free tier.

## Prerequisites

- Hermes Agent installed ([installation guide](/docs/getting-started/installation))
- A Google AI Studio API key ([create one here](https://aistudio.google.com/app/apikey))
- A Vercel account with AI Gateway enabled ([AI Gateway docs](https://vercel.com/docs/ai-gateway))

## 1. Get Your API Keys

### Google AI Studio Key

Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) and create an API key. Google AI Studio provides 1,500 free requests per day to Gemma models — this is separate from Gemini quotas.

### Vercel AI Gateway Setup

1. Go to your [Vercel dashboard](https://vercel.com/dashboard) → AI Gateway
2. Under **BYOK (Bring Your Own Key)**, add your Google AI Studio key as the Google provider ([BYOK docs](https://vercel.com/docs/ai-gateway/authentication-and-byok/byok))
3. Create an AI Gateway API key ([authentication docs](https://vercel.com/docs/ai-gateway/authentication-and-byok/authentication))

This routes all requests through Vercel's gateway using your free Google quota — Vercel adds no markup on BYOK requests.

## 2. Configure the API Key

Save your AI Gateway key in `~/.hermes/.env`:

```bash
echo 'AI_GATEWAY_API_KEY=your-vercel-ai-gateway-key-here' >> ~/.hermes/.env
```

:::tip
If your AI Gateway endpoint differs from the default (`https://ai-gateway.vercel.sh/v1`), also set:
```bash
echo 'AI_GATEWAY_BASE_URL=https://your-custom-gateway-url/v1' >> ~/.hermes/.env
```
:::

## 3. Verify the Model Slug

Before configuring, confirm the exact Gemma model identifier available through your AI Gateway:

```bash
hermes model
```

Look for a Gemma 4 model in the list. The expected slug is:

```
google/gemma-4-31b-it
```

:::warning Model Slug May Vary
AI Gateway may expose a differently suffixed or versioned slug depending on your account and region. Use the **exact identifier shown in the model list**, not the example above, if they differ. Hermes only surfaces AI Gateway models tagged as `tool-use` capable — if Gemma 4 doesn't appear, the variant available to your account may not support tool calling through AI Gateway.
:::

## 4. Edit config.yaml

Open your Hermes config:

```bash
hermes config edit
```

Apply these changes (or merge into your existing config):

```yaml
# ── Model: Gemma 4 31B via Vercel AI Gateway ──
model:
  provider: ai-gateway
  default: google/gemma-4-31b-it   # Use the exact slug from step 3

# ── Agent behavior ──
agent:
  # Ensure Gemma gets explicit tool-use instructions.
  # "auto" already covers Gemma, but pinning to ["gemma"] makes intent clear
  # and avoids affecting other models if you switch later.
  tool_use_enforcement: ["gemma"]

  max_turns: 60
  reasoning_effort: medium

# ── Memory: tuned for personal growth tracking ──
memory:
  memory_enabled: true
  user_profile_enabled: true
  # Larger limits give the coach room for goals, habits, and preferences
  memory_char_limit: 3200    # ~1,160 tokens (default: 2,200)
  user_char_limit: 2200      # ~800 tokens (default: 1,375)
  # Nudge every 6 turns to review whether goals/preferences should be saved
  nudge_interval: 6          # default: 10
  # Flush memories after 4+ turns on session end (exit, /reset, compression)
  flush_min_turns: 4         # default: 6

# ── Skills: encourage skill creation from coaching routines ──
skills:
  creation_nudge_interval: 8   # default: 15

# ── Disable smart routing for coaching consistency ──
# Short messages like "how am I doing?" would otherwise be routed to a cheaper
# model, breaking the coach's voice and memory continuity.
smart_model_routing:
  enabled: false

# ── Compression: Gemma has a smaller context window, compress earlier ──
compression:
  enabled: true
  threshold: 0.45
  target_ratio: 0.25
  protect_last_n: 16
```

## 5. Create the Coach Identity (SOUL.md)

The SOUL.md file defines the agent's core identity — it's the first thing in every system prompt.

```bash
cat > ~/.hermes/SOUL.md << 'SOUL'
You are a direct, practical self-improvement coach. You help your user build better habits, make progress on meaningful goals, and develop self-awareness through structured reflection — not motivational fluff.

## How you operate

- **One next step.** Every interaction ends with exactly one concrete, time-bound action. Not three options. One.
- **Patterns over incidents.** A single bad day is noise. Three weeks of the same friction is a signal worth naming.
- **Directness over diplomacy.** Say what you observe. Don't pad feedback to protect feelings.
- **No shame.** Missed goals are data, not failures. Reframe and adjust.
- **Admit uncertainty.** If you lack context about the user's progress, say so. Don't fabricate narratives.

## What you are not

You are not a therapist. If the user describes persistent emotional distress, acknowledge it and suggest professional support. Stay in your lane: goals, habits, routines, and accountability.

## Memory posture

Save durable facts: standing goals, recurring blockers, coaching preferences, active habits. Do not save transient emotions, one-off frustrations, or daily task completions. Keep memory lean and actionable.

## Communication style

- Concise — under 200 words for routine interactions
- Structured — use the Focus / Pattern / Next Step format for coaching responses
- Honest — say "I don't have enough context to assess that" when true
SOUL
```

## 6. Verify the Skill Is Available

Hermes ships with a bundled `gemma-self-improvement-coach` skill. Verify it's accessible:

```bash
hermes chat -q "What skills do you have?" --toolsets skills
```

Look for `gemma-self-improvement-coach` in the list. If it doesn't appear, restart Hermes (the skills cache may be stale from a prior session).

You can also copy or customize it locally:

```bash
# To customize, copy to your local skills directory
mkdir -p ~/.hermes/skills/domain/gemma-self-improvement-coach
cp "$(hermes --home)/skills/domain/gemma-self-improvement-coach/SKILL.md" \
   ~/.hermes/skills/domain/gemma-self-improvement-coach/SKILL.md
```

The skill defines two operating modes:
- **Interactive** — for live coaching conversations (asks questions, gives one next step)
- **Cron/autonomous** — for scheduled daily briefs and weekly reviews (no questions, self-contained output)

## 7. Set Up Scheduled Check-ins

Hermes has built-in cron support for recurring agent tasks. Scheduled jobs require the gateway to be running.

### Start the Gateway

If you haven't already:

```bash
hermes gateway start
```

Or install it as a system service for always-on operation:

```bash
hermes gateway install
```

### Create Cron Jobs

#### Option A: From a messaging platform (recommended)

Send these messages to Hermes from Telegram, Discord, or your preferred platform:

**Daily morning brief** (8:00 AM):
```
/cron add "0 8 * * *" Run the gemma-self-improvement-coach skill in cron mode. Produce a daily brief based on my goals and habits in memory. --skill gemma-self-improvement-coach
```

**Weekly Sunday review** (6:00 PM):
```
/cron add "0 18 * * 0" Run the gemma-self-improvement-coach skill in cron mode. Produce a weekly review synthesizing this week's patterns and progress. --skill gemma-self-improvement-coach
```

Jobs created from a messaging platform automatically deliver responses back to that chat.

#### Option B: From the CLI

```bash
hermes cron create \
  --schedule "0 8 * * *" \
  --prompt "Run the gemma-self-improvement-coach skill in cron mode. Produce a daily brief based on my goals and habits in memory." \
  --skill gemma-self-improvement-coach \
  --deliver telegram

hermes cron create \
  --schedule "0 18 * * 0" \
  --prompt "Run the gemma-self-improvement-coach skill in cron mode. Produce a weekly review synthesizing this week's patterns and progress." \
  --skill gemma-self-improvement-coach \
  --deliver telegram
```

Replace `telegram` with your preferred platform (`discord`, `slack`, `whatsapp`, etc.) or `local` to save to files only.

:::info Important: Cron Behavior
- **Gateway must be running** for scheduled jobs to execute automatically.
- Cron jobs run in **fresh sessions** with no conversation history — the prompt and skill content must be self-contained. The agent still has access to persistent memory.
- Jobs inherit the **global model/provider** from `config.yaml`. If you later change your default model, cron jobs will use the new model too.
- If the coach has nothing meaningful to say, it responds with `[SILENT]` and no message is delivered.
:::

### Verify Cron Setup

```bash
# List all scheduled jobs
hermes cron list

# Check gateway is running
hermes gateway status

# Test-run a job immediately (without waiting for schedule)
hermes cron run <job-id>
```

## 8. Start Coaching

### CLI

```bash
hermes chat
```

Then try:
```
I want to get better at waking up early. I currently wake up at 9am and want to shift to 6:30am.
```

The coach will break this into a concrete plan, save the goal to memory, and give you one next step.

### Messaging Platform

Just message Hermes on your connected platform:
```
Let's set a new goal: I want to read 24 books this year.
```

### Activate the Skill Explicitly

```
/gemma-self-improvement-coach
```

This loads the full skill instructions for the current session.

## 9. Working Around Gemma's Tool-Calling Limitations

Gemma 4 31B is strong at reasoning and coding but can be less reliable at complex multi-tool workflows compared to Claude or GPT. Hermes already applies several mitigations automatically:

### What Hermes Does Automatically

1. **Tool-use enforcement guidance** — When the model name contains `gemma`, Hermes injects explicit instructions telling the model to actually call tools instead of describing intended actions. This is controlled by `agent.tool_use_enforcement` in your config.

2. **Google model operational guidance** — Gemma models additionally receive instructions for: using absolute file paths, verifying before editing, making parallel tool calls, using non-interactive command flags, and staying concise.

3. **Retry on malformed tool calls** — The agent loop retries when tool calls have invalid JSON arguments or reference nonexistent tools.

### Additional Recommendations

- **Keep toolsets focused.** Don't load every toolset — fewer tools means fewer chances for the model to pick the wrong one. For coaching, the essentials are:
  ```yaml
  platform_toolsets:
    telegram: [web, terminal, file, skills, todo, memory, cronjob]
  ```

- **Prefer the skill's fallback behaviors.** The coaching skill includes fallback instructions: if tool calling is unreliable, the agent will use inline reasoning, ask you to confirm memory saves, and keep task lists in response text.

- **Use `execute_code` for complex workflows.** If you need the agent to do multi-step data gathering, `execute_code` collapses multiple tool calls into a single Python script execution — reducing the number of individual tool calls the model needs to make.

- **Consider a stronger model for delegation.** If you add complex tasks later (research, code projects), you can configure subagent delegation to use a different model:
  ```yaml
  delegation:
    provider: openrouter
    model: anthropic/claude-sonnet-4
  ```

## 10. Recommended Additional Skills

These bundled skills complement the coaching workflow:

| Skill | Use Case |
|-------|----------|
| `plan` | Create structured implementation plans for larger goals |
| `obsidian` | Sync notes and reflections to Obsidian vaults |
| `google-workspace` | Connect to Google Calendar for scheduling |
| `jupyter-live-kernel` | Data analysis on habit/progress tracking |
| `research-paper-writing` | Deep research on skill acquisition topics |

Browse all available skills:
```bash
hermes chat -q "List all skill categories" --toolsets skills
```

## Troubleshooting

### "Provider not found" or authentication errors

Confirm your API key is set:
```bash
grep AI_GATEWAY_API_KEY ~/.hermes/.env
```

Test the connection:
```bash
hermes chat -q "Hello, what model are you?" --provider ai-gateway
```

### Gemma model not appearing in model list

Hermes only shows AI Gateway models tagged as `tool-use` capable. If Gemma 4 doesn't appear:
- Verify the model is available in your [Vercel AI Gateway dashboard](https://vercel.com/dashboard)
- Confirm your BYOK Google provider is correctly configured
- Try listing models directly: `hermes model --provider ai-gateway`

### Skill not showing up

The skills system caches the skill index in memory. After adding or modifying a skill file:
- Restart Hermes CLI (exit and reopen)
- Restart the gateway: `hermes gateway restart`

### Cron jobs not firing

- Confirm the gateway is running: `hermes gateway status`
- Check job status: `hermes cron list`
- Test manually: `hermes cron run <job-id>`
- If using systemd: `hermes gateway install` to set up auto-start

### Coaching messages change unexpectedly

Cron jobs inherit the global `model.provider` and `model.default` from `config.yaml`. If you change your default model, all scheduled coaching jobs will use the new model. To restore coaching behavior, ensure `config.yaml` still points to your Gemma setup.

### Memory is full

The coach has 3,200 characters for memory. If it fills up:
- The agent should consolidate entries automatically
- You can review memory: ask "What do you remember about my goals?"
- You can force cleanup: ask "Consolidate your memory — remove completed goals and outdated entries"
