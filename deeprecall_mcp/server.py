"""Deep Recall MCP Server.

Gives any AI agent biological memory — memories that strengthen, decay,
self-organize, and catch their own contradictions.

Install:
    pip install deeprecall-mcp

Configure in Claude Code (~/.claude/settings.json):
    {
        "mcpServers": {
            "deeprecall": {
                "command": "deeprecall-mcp",
                "env": {"DEEPRECALL_API_KEY": "ec_live_..."}
            }
        }
    }

Configure in Cursor (.cursor/mcp.json):
    {
        "mcpServers": {
            "deeprecall": {
                "command": "deeprecall-mcp",
                "env": {"DEEPRECALL_API_KEY": "ec_live_..."}
            }
        }
    }
"""

import os
import sys
import json
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

API_BASE = os.environ.get("DEEPRECALL_API_URL", "https://api.deeprecall.dev")
API_KEY = os.environ.get("DEEPRECALL_API_KEY", "")

app = Server("deeprecall")
_client: httpx.Client | None = None

# System prompt that teaches the AI how to use Deep Recall
AGENT_INSTRUCTIONS = """You have access to Deep Recall — a biological memory system. Use it actively:

WHEN TO REMEMBER (deeprecall_remember):
- When you learn facts about the user (name, role, preferences, goals)
- When something important happens (decisions, breakthroughs, problems solved)
- When the user shares preferences or opinions
- When you learn relationships between people or concepts
- Add emotional context (valence/arousal) when the user expresses feelings

WHEN TO SEARCH (deeprecall_search):
- At the START of every conversation — search for context about the user/topic
- When the user references something from the past
- When you need background on a person or project
- Before giving advice — check if you've stored relevant knowledge

WHEN TO USE EMOTIONAL SEARCH (deeprecall_emotional_search) — paid plans only:
- When the conversation has emotional weight
- When looking for memories about how someone felt
- For AI companion interactions
- If this tool is not available, the user is on a free plan

WHEN TO REINFORCE (deeprecall_reinforce):
- After using retrieved memories in your response, reinforce the ones you cited
- signal_health > 0.7 if the response was good, < 0.4 if it wasn't helpful

WHEN TO CHECK CONTRADICTIONS (deeprecall_contradictions):
- Periodically, or when you notice conflicting information
- Resolve them when you have enough context

WHEN TO DECAY (deeprecall_decay):
- Run occasionally (not every conversation) to clean stale memories

IMPORTANT: Search for relevant memories BEFORE responding to give personalized, context-aware answers."""


def get_client() -> httpx.Client:
    global _client
    if _client is None:
        if not API_KEY:
            raise RuntimeError(
                "DEEPRECALL_API_KEY not set. Get one at https://deeprecall.dev"
            )
        _client = httpx.Client(
            base_url=API_BASE,
            headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
            timeout=30.0,
        )
    return _client


def api_call(method: str, path: str, **kwargs) -> dict:
    """Make an API call and return the JSON response."""
    client = get_client()
    if method == "GET":
        resp = client.get(path, params=kwargs.get("params"))
    elif method == "POST":
        resp = client.post(path, json=kwargs.get("json"))
    else:
        raise ValueError(f"Unsupported method: {method}")

    if resp.status_code >= 400:
        return {"error": resp.text, "status": resp.status_code}
    return resp.json()


# --- Plan Detection ---

_user_plan: str = "free"


def _detect_plan() -> str:
    """Check the user's plan by hitting the stats endpoint at startup."""
    global _user_plan
    try:
        result = api_call("GET", "/v1/stats")
        _user_plan = result.get("plan", "free")
    except Exception:
        _user_plan = "free"
    return _user_plan


def _is_paid() -> bool:
    return _user_plan in ("starter", "pro", "enterprise")


# --- Tool Definitions ---

# Core tools available to ALL plans
CORE_TOOLS = [
    Tool(
        name="deeprecall_remember",
        description=(
            "Store a memory. Memories are automatically embedded for semantic search, "
            "connected to similar memories in the knowledge graph, and checked for "
            "contradictions with existing memories. Supports emotional context (valence/arousal/dominance)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The memory content to store",
                },
                "kind": {
                    "type": "string",
                    "enum": ["fact", "episode", "preference", "skill", "note"],
                    "description": "Memory type. fact=durable knowledge, episode=event, preference=like/dislike, skill=how-to, note=general",
                    "default": "fact",
                },
                "person": {
                    "type": "string",
                    "description": "Person this memory is about (auto-creates entity if new)",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Tags for categorization",
                },
                "salience": {
                    "type": "number",
                    "description": "Importance 0-1. Higher = resists decay longer",
                    "default": 0.5,
                },
                "valence": {
                    "type": "number",
                    "description": "Emotional valence -1 (negative) to +1 (positive)",
                },
                "arousal": {
                    "type": "number",
                    "description": "Emotional arousal 0 (calm) to 1 (excited)",
                },
            },
            "required": ["content"],
        },
    ),
    Tool(
        name="deeprecall_search",
        description=(
            "Search memories using hybrid keyword + semantic search with Reciprocal Rank Fusion. "
            "Finds memories by meaning, not just keywords. 'outdoor activities' finds 'loves hiking in mountains'."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query — natural language works best",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (1-100)",
                    "default": 10,
                },
                "kind": {
                    "type": "string",
                    "description": "Filter by memory kind",
                },
                "person": {
                    "type": "string",
                    "description": "Filter by person name",
                },
                "mode": {
                    "type": "string",
                    "enum": ["hybrid", "keyword", "semantic"],
                    "description": "Search mode",
                    "default": "hybrid",
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="deeprecall_conversation",
        description=(
            "Store a conversation turn. Optionally auto-extracts facts, entities, and "
            "relationships from the conversation using LLM extraction (requires paid plan)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "role": {
                    "type": "string",
                    "enum": ["user", "assistant", "system"],
                },
                "content": {"type": "string", "description": "The conversation content"},
                "person": {"type": "string", "description": "Who is speaking (for user turns)"},
                "session_id": {"type": "string", "description": "Group turns into sessions"},
                "extract_facts": {"type": "boolean", "description": "Auto-extract facts from content", "default": False},
            },
            "required": ["role", "content"],
        },
    ),
    Tool(
        name="deeprecall_entities",
        description=(
            "List or get entities (people, organizations, places) that Deep Recall has learned about. "
            "Shows characteristics, relationships, and how many memories involve each entity."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "Get a specific entity by ID. If omitted, lists all entities.",
                },
                "entity_type": {
                    "type": "string",
                    "description": "Filter by type (person, organization, place)",
                },
                "limit": {"type": "integer", "default": 20},
            },
        },
    ),
    Tool(
        name="deeprecall_contradictions",
        description=(
            "Get detected contradictions — memories that conflict with each other. "
            "Automatically detected when new memories semantically clash with existing ones. "
            "Resolve contradictions to keep your knowledge consistent."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "resolve"],
                    "default": "list",
                },
                "contradiction_id": {
                    "type": "string",
                    "description": "ID of contradiction to resolve (for resolve action)",
                },
                "resolution": {
                    "type": "string",
                    "description": "How was it resolved (for resolve action)",
                },
                "keep_memory_id": {"type": "string", "description": "Memory to keep"},
                "delete_memory_id": {"type": "string", "description": "Memory to delete"},
            },
        },
    ),
    Tool(
        name="deeprecall_decay",
        description=(
            "Run intelligent forgetting. Memories that haven't been accessed decay in salience. "
            "Frequently recalled memories resist decay (ACT-R cognitive architecture). "
            "Call periodically to keep your memory store clean."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "half_life_hours": {
                    "type": "number",
                    "description": "Decay half-life in hours. 168 = 1 week (default)",
                    "default": 168,
                },
                "coherence": {
                    "type": "number",
                    "description": "System coherence 0-1. Higher = faster decay (system is healthy, can forget more)",
                    "default": 0.5,
                },
            },
        },
    ),
    Tool(
        name="deeprecall_reinforce",
        description=(
            "Hebbian reinforcement — strengthen memories that were useful, weaken ones that weren't. "
            "Call after your agent uses retrieved memories. Cited memories get stronger. "
            "Uncited memories in low-signal responses get weaker. Dead band (0.4-0.7) = no change."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "retrieved_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "IDs of memories that were retrieved for context",
                },
                "signal_health": {
                    "type": "number",
                    "description": "How good was the response? 0-1. Above 0.7 = reinforce. Below 0.4 = weaken.",
                },
                "cited_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "IDs of memories actually cited/used in the response. These are NEVER weakened.",
                },
            },
            "required": ["retrieved_ids", "signal_health"],
        },
    ),
    Tool(
        name="deeprecall_stats",
        description="Get memory stats — total memories, entities, usage, plan info, memory pressure.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="deeprecall_account",
        description=(
            "Check account status, plan details, usage limits, and upgrade options. "
            "Use this to see how much capacity is left and what features are available. "
            "If the user is approaching their memory limit, suggest upgrading."
        ),
        inputSchema={"type": "object", "properties": {}},
    ),
]

# Paid-only tools — only registered if the user has a paid plan
PAID_TOOLS = [
    Tool(
        name="deeprecall_emotional_search",
        description=(
            "Search with emotional context boost. Memories encoded in similar emotional states "
            "are ranked higher (mood-congruent retrieval). Essential for AI companions. "
            "Requires Builder plan or higher."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "valence": {"type": "number", "description": "Current emotional valence -1 to +1"},
                "arousal": {"type": "number", "description": "Current arousal 0 to 1"},
                "dominance": {"type": "number", "description": "Current dominance 0 to 1", "default": 0.5},
                "boost_weight": {"type": "number", "description": "How much emotion influences ranking 0-1", "default": 0.2},
                "limit": {"type": "integer", "default": 10},
            },
            "required": ["query", "valence", "arousal"],
        },
    ),
    Tool(
        name="deeprecall_topology",
        description=(
            "Analyze the memory knowledge graph. Shows how memories cluster into communities "
            "(Louvain algorithm), graph density, modularity score, and fragmentation risk. "
            "See the shape of what you know. Requires Builder plan or higher."
        ),
        inputSchema={"type": "object", "properties": {}},
    ),
]


def get_available_tools() -> list[Tool]:
    """Return tools based on user's plan. Paid features only show for paid users."""
    _detect_plan()
    tools = list(CORE_TOOLS)
    if _is_paid():
        tools.extend(PAID_TOOLS)
    return tools


# --- Handlers ---

@app.list_prompts()
async def list_prompts():
    from mcp.types import Prompt, PromptArgument
    return [
        Prompt(
            name="deeprecall_instructions",
            description="Instructions for the AI on how to use Deep Recall memory tools proactively",
            arguments=[],
        ),
    ]


@app.get_prompt()
async def get_prompt(name: str, arguments: dict | None = None):
    from mcp.types import PromptMessage, TextContent as PromptTextContent
    if name == "deeprecall_instructions":
        return {
            "description": "Deep Recall memory system instructions",
            "messages": [
                PromptMessage(
                    role="user",
                    content=PromptTextContent(type="text", text=AGENT_INSTRUCTIONS),
                )
            ],
        }
    raise ValueError(f"Unknown prompt: {name}")


@app.list_tools()
async def list_tools():
    return get_available_tools()


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        result = _dispatch(name, arguments)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


def _dispatch(name: str, args: dict) -> dict:
    if name == "deeprecall_remember":
        body = {"content": args["content"]}
        for key in ("kind", "person", "tags", "salience", "valence", "arousal"):
            if key in args and args[key] is not None:
                body[key] = args[key]
        return api_call("POST", "/v1/memories", json=body)

    elif name == "deeprecall_search":
        params = {"q": args["query"]}
        for key in ("limit", "kind", "person", "mode"):
            if key in args and args[key] is not None:
                params[key] = args[key]
        return api_call("GET", "/v1/memories/search", params=params)

    elif name == "deeprecall_emotional_search":
        body = {
            "q": args["query"],
            "valence": args.get("valence", 0.0),
            "arousal": args.get("arousal", 0.5),
            "dominance": args.get("dominance", 0.5),
            "boost_weight": args.get("boost_weight", 0.2),
            "limit": args.get("limit", 10),
        }
        return api_call("POST", "/v1/memory/emotional-search", json=body)

    elif name == "deeprecall_conversation":
        body = {"role": args["role"], "content": args["content"]}
        for key in ("person", "session_id", "extract_facts"):
            if key in args and args[key] is not None:
                body[key] = args[key]
        return api_call("POST", "/v1/conversations", json=body)

    elif name == "deeprecall_entities":
        if "entity_id" in args and args["entity_id"]:
            return api_call("GET", f"/v1/entities/{args['entity_id']}")
        params = {}
        for key in ("entity_type", "limit"):
            if key in args and args[key] is not None:
                params[key] = args[key]
        return api_call("GET", "/v1/entities", params=params)

    elif name == "deeprecall_topology":
        return api_call("GET", "/v1/memory/topology")

    elif name == "deeprecall_contradictions":
        action = args.get("action", "list")
        if action == "resolve":
            body = {"resolution": args.get("resolution", "")}
            if "keep_memory_id" in args:
                body["keep_memory_id"] = args["keep_memory_id"]
            if "delete_memory_id" in args:
                body["delete_memory_id"] = args["delete_memory_id"]
            return api_call(
                "POST",
                f"/v1/memory/contradictions/{args['contradiction_id']}/resolve",
                json=body,
            )
        params = {"status": "active", "limit": args.get("limit", 20)}
        return api_call("GET", "/v1/memory/contradictions", params=params)

    elif name == "deeprecall_decay":
        body = {
            "half_life_hours": args.get("half_life_hours", 168),
            "coherence": args.get("coherence", 0.5),
        }
        return api_call("POST", "/v1/memory/decay", json=body)

    elif name == "deeprecall_reinforce":
        body = {
            "retrieved_ids": args["retrieved_ids"],
            "signal_health": args["signal_health"],
            "cited_ids": args.get("cited_ids", []),
        }
        return api_call("POST", "/v1/memory/reinforce", json=body)

    elif name == "deeprecall_stats":
        return api_call("GET", "/v1/stats")

    elif name == "deeprecall_account":
        stats = api_call("GET", "/v1/stats")
        account = api_call("GET", "/v1/account")

        plan = stats.get("plan", "free")
        limit = stats.get("plan_limit", 1000)
        used = stats.get("total_memories", 0)
        pressure = stats.get("memory_pressure", 0)

        upgrade_info = {
            "free": {
                "next_plan": "Builder",
                "next_price": "$39/mo",
                "next_memories": "50,000",
                "upgrade_url": "https://buy.stripe.com/test_9B600jbbgd7cg1AeUpeQM00",
            },
            "starter": {
                "next_plan": "Pro",
                "next_price": "$99/mo",
                "next_memories": "500,000",
                "upgrade_url": "https://buy.stripe.com/test_5kQeVdcfk5EK9Dc27DeQM01",
            },
            "pro": {
                "next_plan": "Enterprise",
                "next_price": "$299/mo",
                "next_memories": "5,000,000",
                "upgrade_url": "https://buy.stripe.com/test_8x2eVdcfk3wC02C5jPeQM02",
            },
        }

        result = {
            "account": account,
            "plan": plan,
            "memories_used": used,
            "memories_limit": limit,
            "usage_percent": round((used / limit * 100) if limit > 0 else 0, 1),
            "memory_pressure": pressure,
        }

        if plan in upgrade_info:
            result["upgrade"] = upgrade_info[plan]

        if used >= limit:
            result["warning"] = f"Memory limit reached! Upgrade to {upgrade_info.get(plan, {}).get('next_plan', 'a higher plan')} for more."
        elif used >= limit * 0.8:
            result["warning"] = f"Approaching memory limit ({used}/{limit}). Consider upgrading."

        return result

    else:
        return {"error": f"Unknown tool: {name}"}


def main():
    """Run the Deep Recall MCP server."""
    import asyncio

    if not API_KEY:
        print(
            "ERROR: DEEPRECALL_API_KEY not set.\n"
            "Get your free API key at https://deeprecall.dev\n"
            "Then set it: export DEEPRECALL_API_KEY=ec_live_...",
            file=sys.stderr,
        )
        sys.exit(1)

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())

    asyncio.run(run())


if __name__ == "__main__":
    main()
