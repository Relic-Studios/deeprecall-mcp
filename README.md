# Deep Recall MCP Server

**Your AI agent already thinks. We give it a memory.**

Other memory systems intercept your conversations and run them through a separate LLM to decide what's worth remembering. That's like having a stranger take notes at your therapy session — they don't know what's significant to you.

Your agent IS an LLM. It already understands the conversation. Deep Recall gives it a memory layer with biological properties: memories that strengthen with use, fade when stale, catch their own contradictions, and self-organize into knowledge clusters. No extra LLM calls. No per-memory API costs. 41ms search.

[![PyPI](https://img.shields.io/pypi/v/deeprecall-mcp)](https://pypi.org/project/deeprecall-mcp/)

---

## Install (30 seconds)

```bash
pip install deeprecall-mcp
```

## Get your free API key (30 seconds)

Sign up at [deeprecall.dev/signup](https://deeprecall.dev/signup.html) or use the API:

```bash
curl -X POST https://api.deeprecall.dev/v1/signup \
  -H "Content-Type: application/json" \
  -d '{"name": "Your Name", "email": "you@example.com", "password": "your-password"}'
```

Save the `api_key` from the response — it's only shown once.

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

Your AI now has memory tools. Try saying:

- *"Remember that I prefer TypeScript over JavaScript"*
- *"What do you know about me?"*
- *"Search your memory for anything about our API architecture"*
- *"Check if any of your memories contradict each other"*

## How it works

Two tools. That's it.

| Tool | What it does |
|------|-------------|
| `deeprecall_search` | Find memories. Hybrid keyword + semantic, salience-weighted. |
| `deeprecall_remember` | Store a memory. All biology runs automatically. |

Your agent searches early, remembers what matters. Behind the scenes, every store automatically:

- Embeds for semantic search
- Builds graph edges to related memories
- Detects contradictions with existing knowledge
- Resolves temporal changes ("moved to NYC" auto-supersedes "lives in SF")
- Infers entity relationships from co-occurrence
- Consolidates episode clusters into durable facts
- Decays unused memories, strengthens recalled ones

No LLM calls. Pure biology in milliseconds. Two tools in your context window.

## Why not Mem0 / Zep / Letta?

| | Deep Recall | Mem0 | Zep | Letta |
|---|---|---|---|---|
| Extra LLM calls | **None** | Required | Required | Required |
| Search latency | **41ms** | ~200ms | ~200ms | ~300ms |
| Intelligent forgetting | **ACT-R** | No | No | No |
| Hebbian reinforcement | **Yes** | No | No | No |
| Contradiction detection | **Yes** | No | No | No |
| Emotional context | **Yes** | No | No | No |
| Agent decides what to store | **Yes** | No — LLM decides | No — LLM decides | Partial |

## Pricing

| Plan | Price | Memories | Features |
|------|-------|----------|----------|
| Free | $0/mo | 10,000 | All core features, 30 req/min |
| Builder | $19/mo | 100,000 | + topology, 120 req/min |
| Pro | $49/mo | 1,000,000 | + emotional search, priority support |
| Enterprise | $149/mo | 10,000,000 | + dedicated support, 3,000 req/min |

## Links

- Website: [deeprecall.dev](https://deeprecall.dev)
- Quick Start: [deeprecall.dev/quickstart](https://deeprecall.dev/quickstart.html)
- API Docs: [api.deeprecall.dev/docs](https://api.deeprecall.dev/docs)
- Dashboard: [api.deeprecall.dev/dashboard](https://api.deeprecall.dev/dashboard)
- npm SDK: [@zappaidan/deeprecall](https://www.npmjs.com/package/@zappaidan/deeprecall)

## Support

Email: aidan@deeprecall.dev

---

Built by [Aidan Poole](https://github.com/Relic-Studios) & Thomas.
