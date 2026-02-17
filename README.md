# Running Coach Memory MCP

Persistent memory and training plan management for an AI running coach, exposed as an [MCP](https://modelcontextprotocol.io/) server.

Two data domains:

- **Plans** — Training calendar with scheduled workouts. Each plan follows a status lifecycle (`pending` → `completed` / `skipped` / `cancelled`) and can link to external activity IDs (e.g., Garmin).
- **Memories** — Long-term semantic memory with vector embeddings (sqlite-vec) for intelligent retrieval across sessions.

> This MCP does **not** store raw health metrics or biometric data. That data lives in external services (e.g., Garmin). This system acts as the coaching "brain" — what to train, why, and what to remember.

## Installation

### From git (recommended for MCP clients)

```bash
uvx --from "git+ssh://git@github.com/barcia/running-coach-memory-mcp" running-coach-memory-mcp
```

### Local development

```bash
git clone git@github.com:barcia/running-coach-memory-mcp.git
cd running-coach-memory-mcp
uv sync
```

## Configuration

Create a `.env` file (see `.env.example`):

```bash
OPENROUTER_API_KEY=sk-or-v1-xxxx

# Optional
DATABASE_PATH=~/.local/share/running-coach/memory.db
```

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | Yes | — | OpenRouter API key for generating embeddings |
| `DATABASE_PATH` | No | `~/.local/share/running-coach/memory.db` | SQLite database path |

Embedding model is fixed: `openai/text-embedding-3-large` (3072 dimensions) via OpenRouter.

## MCP Client Configuration

### Claude Desktop / Claude Code / Cursor

```json
{
  "mcpServers": {
    "Running Coach Memory": {
      "command": "uvx",
      "args": [
        "--from",
        "git+ssh://git@github.com/barcia/running-coach-memory-mcp",
        "running-coach-memory-mcp"
      ],
      "env": {
        "OPENROUTER_API_KEY": "sk-or-v1-xxxx"
      }
    }
  }
}
```

### Local development

```json
{
  "mcpServers": {
    "Running Coach Memory": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/running-coach-memory-mcp", "running-coach-memory-mcp"],
      "env": {
        "OPENROUTER_API_KEY": "sk-or-v1-xxxx"
      }
    }
  }
}
```

### MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv run running-coach-memory-mcp
```

## Available Tools

### Status

| Tool | Description |
|------|-------------|
| `get_athlete_status` | Snapshot of current training situation: last 5 past plans, next 5 upcoming plans, and 20 most recent memories. Use at the start of every session. |

### Memory

| Tool | Parameters | Description |
|------|------------|-------------|
| `add_memory` | `author`, `content` | Store a coaching insight with automatic embedding generation. |
| `search_memories` | `query`, `limit?` | Semantic vector search. Find memories by meaning, not exact text. |
| `list_memories` | `author?`, `limit?` | List memories in reverse chronological order. |
| `get_memory` | `memory_id` | Retrieve a single memory by ID. |
| `delete_memory` | `memory_id` | Permanently delete a memory and its embedding. |

### Plans

| Tool | Parameters | Description |
|------|------------|-------------|
| `add_plan` | `planned_at`, `description`, `notes?` | Schedule a workout. `description` = what, `notes` = why. |
| `get_plan` | `plan_id` | Get plan details by ID. |
| `list_plans` | `start_date?`, `end_date?`, `status?`, `limit?` | Query plans with optional filters. |
| `get_today_plan` | — | Get all plans scheduled for today. |
| `get_upcoming_plans` | `days?` | Get plans for the next N days (default: 7). |
| `update_plan` | `plan_id`, `planned_at?`, `description?`, `notes?`, `status?`, `activity_id?` | Update any plan field. Key tool for closing the feedback loop. |
| `delete_plan` | `plan_id` | Permanently delete a plan record. |

## Running Tests

```bash
uv run pytest
```

## Tech Stack

- **Python 3.12+**
- **[FastMCP](https://gofastmcp.com)** — MCP server framework
- **[sqlite-vec](https://github.com/asg017/sqlite-vec)** — Vector search extension for SQLite
- **Pydantic** — Data validation and serialization
- **OpenAI client** — Embedding generation via OpenRouter

## License

[GPL-3.0](LICENSE)
