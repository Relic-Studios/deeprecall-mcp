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

**The pattern: Context, Remember, Process**

1. **Before** — `deeprecall_context`: Pull relevant memories, person profile, contradictions
2. **During** — `deeprecall_remember`: Your agent stores what it thinks matters
3. **After** — `deeprecall_learn`: Biology takes over — reinforcement, decay, contradiction detection, graph building, memory consolidation

Your agent decides what's worth keeping. Deep Recall handles what happens to those memories over time.

## What happens behind the scenes

Every time your agent stores a memory, Deep Recall automatically:

- **Builds graph edges** to semantically similar memories
- **Detects contradictions** with existing knowledge
- **Resolves temporal changes** ("moved from SF to NYC" → auto-supersedes, not contradiction)
- **Infers relationships** from entity co-occurrence ("Alice" + "Google" in 3 memories → `works_at`)
- **Consolidates clusters** of related episodic memories into durable facts
- **Weights search by salience** — faded memories rank lower, like real recall

No LLM calls. Pure biology running in milliseconds.

## Tools

| Tool | What it does |
|------|-------------|
| `deeprecall_context` | Pull all relevant context before responding (memories, profile, contradictions) |
| `deeprecall_remember` | Store a memory with optional emotional context (valence/arousal) |
| `deeprecall_learn` | Post-conversation biology: reinforcement, decay, contradiction scan |
| `deeprecall_search` | Hybrid keyword + semantic search (41ms median) |
| `deeprecall_entities` | Track people, orgs, and their auto-inferred relationships |
| `deeprecall_contradictions` | View and resolve conflicting memories |
| `deeprecall_decay` | Manual intelligent forgetting (also runs automatically) |
| `deeprecall_reinforce` | Hebbian learning — cited memories get stronger |
| `deeprecall_stats` | Memory health, usage, plan info |
| `deeprecall_account` | Plan status and upgrade options |
| `deeprecall_emotional_search` | Mood-congruent retrieval (paid) |
| `deeprecall_topology` | Louvain community detection on memory graph (paid) |

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
| Free | $0/mo | 1,000 | All core features, 30 req/min |
| Builder | $39/mo | 50,000 | + topology, 120 req/min |
| Pro | $99/mo | 500,000 | + emotional search, priority support |
| Enterprise | $299/mo | 5,000,000 | + dedicated support, 3,000 req/min |

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
