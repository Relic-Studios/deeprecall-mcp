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
AGENT_INSTRUCTIONS = """You have persistent memory via Deep Recall. Two tools:

1. deeprecall_search — Search your memories. Do this early in conversations to recall what you know.
2. deeprecall_remember — Store what matters. Facts, preferences, decisions, corrections.

That's it. Behind the scenes, every memory you store is automatically:
- Embedded for semantic search
- Connected to related memories in a knowledge graph
- Checked for contradictions with existing knowledge
- Consolidated into durable facts over time
- Decayed if unused, strengthened if recalled

You are the intelligence. You decide what's worth remembering. Deep Recall handles the biology."""


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




# --- Tool Definitions ---

TOOLS = [
    Tool(
        name="deeprecall_remember",
        description=(
            "Store a memory. Behind the scenes: embeds for semantic search, builds graph edges "
            "to related memories, detects contradictions, auto-resolves temporal changes, "
            "infers entity relationships, and periodically consolidates episode clusters into "
            "durable facts. All biology runs automatically — just store what matters."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The memory to store",
                },
                "person": {
                    "type": "string",
                    "description": "Who this memory is about",
                },
                "kind": {
                    "type": "string",
                    "enum": ["fact", "episode", "preference", "skill", "note"],
                    "description": "Memory type",
                    "default": "fact",
                },
                "salience": {
                    "type": "number",
                    "description": "Importance 0-1. Higher resists decay longer.",
                    "default": 0.5,
                },
            },
            "required": ["content"],
        },
    ),
    Tool(
        name="deeprecall_search",
        description=(
            "Search memories. Hybrid keyword + semantic search, ranked by salience. "
            "Faded memories rank lower. 'outdoor activities' finds 'loves hiking'."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language search query",
                },
                "person": {
                    "type": "string",
                    "description": "Filter by person",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    ),
]


def get_available_tools() -> list[Tool]:
    """Return the two core tools."""
    return TOOLS
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
        for key in ("kind", "person", "salience"):
            if key in args and args[key] is not None:
                body[key] = args[key]
        return api_call("POST", "/v1/memories", json=body)

    elif name == "deeprecall_search":
        params = {"q": args["query"]}
        for key in ("limit", "person"):
            if key in args and args[key] is not None:
                params[key] = args[key]
        return api_call("GET", "/v1/memories/search", params=params)

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
