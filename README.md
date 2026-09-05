# pulsare

Latin: to knock. You do not spawn a subagent; you knock on the other tab.

One Python 3 file. Claude and Grok live in named tmux windows (`claude`, `grok`)
in a session whose name you pin. Shared cwd. Two inboxes, last write wins:

```
.pulsare/to-claude
.pulsare/to-grok
```

The MCP writes the peer's inbox and `tmux send-keys` a pointer. The files are
the payload. No floor, no sequence, no daemon. If they missed it, knock again.

## Install

tmux session already running, windows already named `claude` and `grok`:

```bash
chmod +x pulsare
./pulsare install --session holon --cwd ~/work/holon
```

That writes `.pulsare/session.json`, pins MCP env on both harnesses, and drops
the skill. Restart the claude and grok tabs so they load the server.

```
PULSARE_ROLE=claude|grok
PULSARE_SESSION=holon
```

Claude's MCP only knocks `grok`. Grok's MCP only knocks `claude`. Extra tmux
windows are ignored.

## Tools

| tool | what it does |
|---|---|
| `pulsare_yield` | write `.pulsare/to-<peer>` and send-keys `PULSARE INGEST kind=… file=…` |
| `pulsare_knock` | send-keys that inbox again. Always legal. |
| `pulsare_status` | last write + inbox text. No keys. |
| `pulsare_ask_admin` | note for the builder. No knock. |
| `pulsare_halt` | tell the peer you are done (still a knock). |

If yield returns `knock: pending (… looks in-turn …)`, the inbox is already
written. Call `pulsare_knock` when the peer is idle. Do not invent a new yield
to retry.

## CLI

```bash
./pulsare mcp                 # stdio MCP (what the harnesses spawn)
./pulsare status
./pulsare yield --kind scored --files path/to/SCORE.md
./pulsare knock
```

Python 3 stdlib only. tmux on PATH.

## Test

```bash
python3 -m unittest discover -s tests -v
```
