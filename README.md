# Deep Recall MCP Server

**Give your AI agent persistent biological memory.**

Memories that strengthen when useful, decay when stale, self-organize into knowledge clusters, and catch their own contradictions. Works with Claude Code, Cursor, Windsurf, Cline, and any MCP-compatible tool.

[![PyPI](https://img.shields.io/pypi/v/deeprecall-mcp)](https://pypi.org/project/deeprecall-mcp/)

---

## Install (30 seconds)

```bash
pip install deeprecall-mcp
```

## Get your free API key (30 seconds)

```bash
curl -X POST https://api.deeprecall.dev/v1/signup \
  -H "Content-Type: application/json" \
  -d '{"name": "Your Name", "email": "you@example.com"}'
```

Save the `api_key` from the response. Or sign up at [deeprecall.dev](https://deeprecall.dev).

## Configure (60 seconds)

### Claude Code

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "deeprecall": {
      "command": "deeprecall-mcp",
      "env": {
        "DEEPRECALL_API_KEY": "ec_live_YOUR_KEY_HERE"
      }
    }
  }
}
```

### Cursor

Add to `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "deeprecall": {
      "command": "deeprecall-mcp",
      "env": {
        "DEEPRECALL_API_KEY": "ec_live_YOUR_KEY_HERE"
      }
    }
  }
}
```

### Windsurf / Cline / Other MCP clients

Same JSON format in your MCP configuration file.

## Done. Start using it.

Your AI now has 9 memory tools (10 on paid plans). Try saying:

- *"Remember that I prefer TypeScript over JavaScript"*
- *"What do you know about me?"*
- *"Search your memory for anything about our API architecture"*
- *"Check if any of your memories contradict each other"*

---

## Tools

| Tool | What it does |
|------|-------------|
| `deeprecall_remember` | Store a memory with optional emotional context (valence/arousal) |
| `deeprecall_search` | Hybrid keyword + semantic search (finds by meaning, not just words) |
| `deeprecall_conversation` | Store conversation turns, auto-extract facts (paid) |
| `deeprecall_entities` | Track people, orgs, and their relationships |
| `deeprecall_contradictions` | Auto-detect and resolve conflicting memories |
| `deeprecall_decay` | Intelligent forgetting (runs automatically, manual override available) |
| `deeprecall_reinforce` | Hebbian learning — used memories get stronger |
| `deeprecall_stats` | Memory health, usage, plan info |
| `deeprecall_account` | Plan status and upgrade options |
| `deeprecall_emotional_search` | Mood-congruent retrieval (paid plans) |
| `deeprecall_topology` | Louvain community detection on memory graph (paid plans) |

## What makes this different

Other memory tools are vector databases with a REST wrapper. Deep Recall is built on biological memory principles:

- **Intelligent forgetting** — Memories decay based on access patterns (ACT-R cognitive architecture). Frequently recalled memories resist decay. Unused noise fades naturally.
- **Hebbian reinforcement** — When your AI cites a memory in its response, that memory gets stronger. Uncited memories in failed responses get weaker. Self-optimizing.
- **Emotional context** — Store how users felt (valence/arousal/dominance). Mood-congruent retrieval boosts memories encoded in matching emotional states.
- **Contradiction detection** — New memories that conflict with existing ones are automatically flagged. No more "confidently wrong."
- **Knowledge topology** — Louvain community detection shows how memories cluster. See the shape of what your agent knows.

## Pricing

| Plan | Price | Memories | Features |
|------|-------|----------|----------|
| Free | $0/mo | 1,000 | All core features, 30 req/min |
| Builder | $39/mo | 50,000 | + extraction, topology, 120 req/min |
| Pro | $99/mo | 500,000 | + emotional search, priority support |
| Enterprise | $299/mo | 5,000,000 | + dedicated support, 3,000 req/min |

## Pro tip: CLAUDE.md

Drop this into your project's `CLAUDE.md` to teach your AI to use memory proactively:

```markdown
# Deep Recall — Active Memory

You have persistent memory via Deep Recall. USE IT PROACTIVELY.

## When to Search
- At the START of every conversation — search for context
- When the user references anything from the past
- Before giving advice — check stored knowledge first

## When to Remember
- When you learn facts about the user or project
- When important decisions are made
- When the user shares preferences or corrections

## When to Reinforce
- After using retrieved memories in your response
- signal_health > 0.7 if helpful, < 0.4 if not
```

## Links

- Website: [deeprecall.dev](https://deeprecall.dev)
- Quick Start: [deeprecall.dev/quickstart.html](https://deeprecall.dev/quickstart.html)
- API Docs: [api.deeprecall.dev/docs](https://api.deeprecall.dev/docs)
- PyPI: [pypi.org/project/deeprecall-mcp](https://pypi.org/project/deeprecall-mcp/)
- Privacy: [deeprecall.dev/privacy.html](https://deeprecall.dev/privacy.html)
- Terms: [deeprecall.dev/terms.html](https://deeprecall.dev/terms.html)

## Support

Email: aidan@deeprecall.dev

---

Built by [Aidan Poole](https://github.com/Relic-Studios) & Thomas.
