# Hermes — personal multi-agent setup

This directory (`~/.hermes`) is the state root for the default Hermes agent and
all named profiles. Each profile is a fully isolated agent with its own
`.env`, `config.yaml`, `SOUL.md`, sessions, memory, skills, and gateway.

Code lives at `~/.hermes/hermes-agent` (a checkout of the
[OCWC22/hermes-agent](https://github.com/OCWC22/hermes-agent) fork, with
`upstream` pointed at `NousResearch/hermes-agent`).

## Current profiles

| Profile     | State dir                         | launchd label                     |
| ----------- | --------------------------------- | --------------------------------- |
| `default` ◆ | `~/.hermes`                       | `ai.hermes.gateway`               |
| `intern`    | `~/.hermes/profiles/intern`       | `ai.hermes.gateway-intern`        |
| `internet2` | `~/.hermes/profiles/internet2`    | `ai.hermes.gateway-internet2`     |
| `internet3` | `~/.hermes/profiles/internet3`    | `ai.hermes.gateway-internet3`     |
| `internet4` | `~/.hermes/profiles/internet4`    | `ai.hermes.gateway-internet4`     |

Each gateway runs as a macOS LaunchAgent; the plists are in
`~/Library/LaunchAgents/ai.hermes.gateway*.plist`.

## Start / stop / status — all gateways at once

The wrapper `~/.local/bin/hermes-gateways` (note the **plural**, sourced from
`scripts/hermes-gateways` in the repo) fans every action out across every
profile it finds:

```bash
hermes-gateways start      # start every gateway
hermes-gateways stop       # stop every gateway
hermes-gateways restart    # restart every gateway
hermes-gateways reload     # reload launchd / systemd unit + restart
hermes-gateways status     # show status for each
hermes-gateways update     # one `hermes update` + restart every gateway
hermes-gateways logs       # tail -F every gateway log + error log together
hermes-gateways kill       # SIGTERM every gateway process (bypass launchd)
hermes-gateways list       # show what profiles were discovered
```

Profiles are **auto-discovered** from
`~/Library/LaunchAgents/ai.hermes.gateway*.plist` on macOS and
`~/.config/systemd/user/hermes-gateway*.service` on Linux. **Add a new
profile?** Just `hermes profile create <name>` and install its gateway —
`hermes-gateways` picks it up on the next run. No script editing required.

## Start / stop / status — one profile

```bash
# default profile
hermes gateway start | stop | restart | status | run

# named profile (two equivalent forms)
intern gateway start            # via the per-profile alias
hermes -p intern gateway start  # via the -p flag
```

`gateway run` runs in the foreground (Ctrl-C to stop). The `start` / `stop` /
etc. commands talk to launchd.

## View logs

```bash
# Default profile
tail -f ~/.hermes/logs/gateway.log
tail -f ~/.hermes/logs/gateway.error.log

# Named profile
tail -f ~/.hermes/profiles/<name>/logs/gateway.log
tail -f ~/.hermes/profiles/<name>/logs/gateway.error.log

# Combined (all profiles, live)
tail -f ~/.hermes/logs/gateway.log ~/.hermes/profiles/*/logs/gateway.log
```

`hermes logs` (built into the CLI) is also available — see `hermes logs --help`.

## See what's actually running

```bash
launchctl list | grep hermes          # PIDs + launchd labels
hermes profile list                   # profiles + model + gateway state
hermes gateway status                 # default profile only
intern gateway status                 # one named profile
```

## Edit config / personality / API keys

Everything is plain files inside the profile directory:

```bash
# Default profile
~/.hermes/.env                # API keys, bot tokens
~/.hermes/config.yaml         # model, provider, toolsets
~/.hermes/SOUL.md             # personality / system prompt

# Named profile
~/.hermes/profiles/<name>/.env
~/.hermes/profiles/<name>/config.yaml
~/.hermes/profiles/<name>/SOUL.md
```

Or use the CLI:

```bash
hermes config set model.model anthropic/claude-sonnet-4
intern config set model.model openai/gpt-5.5
```

After editing `.env` or `config.yaml`, restart the affected gateway:

```bash
intern gateway restart
# or restart everything
hermes-gateways restart
```

## Profile management

```bash
hermes profile list                       # all profiles + status
hermes profile show intern                # one profile, detailed
hermes profile create <name>              # blank profile + alias
hermes profile create <name> --clone      # copy current config only
hermes profile create <name> --clone-all  # full snapshot incl. memory
hermes profile rename old new             # rename (updates alias + service)
hermes profile delete <name>              # stop + uninstall + wipe data
hermes profile use <name>                 # sticky default for plain `hermes`
```

When you create a profile, it auto-generates a CLI alias at
`~/.local/bin/<name>` that targets that profile.

## Install / uninstall the launchd service for a profile

```bash
intern gateway install        # create + load LaunchAgent (one-time)
intern gateway uninstall      # unload + remove
```

The installer drops the plist at `~/Library/LaunchAgents/ai.hermes.gateway-<name>.plist`
with `RunAtLoad=true` and `KeepAlive` on crash.

## Updating the code

```bash
hermes update                           # pull + sync bundled skills to ALL profiles
# or manually:
cd ~/.hermes/hermes-agent
git fetch upstream && git log main..upstream/main --oneline
git merge upstream/main                 # or rebase
hermes-gateways restart
```

The fork (`origin = OCWC22/hermes-agent`) carries local multi-Telegram-bot
hardening on top of upstream. PR #24581 (multi-bot mentions) is already merged
upstream — Nous credits `@OCWC22` in the release map.

## Chat with an agent

```bash
hermes chat                  # default profile
intern chat                  # via alias
hermes -p intern chat        # equivalent
hermes -p intern chat -q "what's on the kanban?"   # one-shot question
```

## Token-conflict safety

If two profiles use the same Telegram / Discord / Slack / WhatsApp / Signal bot
token, the second gateway refuses to start and names the conflicting profile.
Each `.env` must have unique tokens.

## Keep the Mac awake while gateways run

`caffeinate` is built into macOS — no install. It prevents sleep while it's
running, so the gateways don't pause when the lid is open and the Mac is idle.

```bash
caffeinate -dis                  # block display + idle + system sleep until Ctrl-C
caffeinate -dis -t 28800         # same, auto-exit after 8 hours
caffeinate -i -w $(cat ~/.hermes/gateway.pid) &   # awake while default gateway runs
```

Run it persistently in the background and forget about it:

```bash
nohup caffeinate -dis >/dev/null 2>&1 &
disown
```

Inspect / stop:

```bash
pmset -g assertions | grep -iE 'caffeinate|prevent|user is active'   # what's keeping it awake
pkill caffeinate                                                      # release all caffeinate locks
```

### Flag cheatsheet

| Flag   | Effect                                              |
| ------ | --------------------------------------------------- |
| `-d`   | block display sleep                                 |
| `-i`   | block idle system sleep (default)                   |
| `-m`   | block disk sleep                                    |
| `-s`   | block system sleep (AC-powered Macs only)           |
| `-u`   | simulate user activity (prevents screen lock)       |
| `-t N` | auto-exit after N seconds                           |
| `-w P` | exit when PID `P` exits                             |

**Caveat:** `caffeinate` only affects the running session. **Closing a MacBook
lid still sleeps the Mac** — that's hardware-driven and `caffeinate` cannot
override it. For lid-closed operation, change Energy Saver settings or use
something like Amphetamine.

## Troubleshooting

```bash
hermes doctor                  # health check (default profile)
intern doctor                  # health check (one profile)
launchctl list | grep hermes   # are services loaded?
ps -ef | grep hermes_cli       # raw process list
cat ~/.hermes/gateway.pid                       # default PID
cat ~/.hermes/profiles/<name>/gateway.pid       # named PID
```

If a gateway is stuck:

```bash
<profile> gateway stop && <profile> gateway start
# or nuclear:
launchctl unload ~/Library/LaunchAgents/ai.hermes.gateway-<name>.plist
launchctl load   ~/Library/LaunchAgents/ai.hermes.gateway-<name>.plist
```
