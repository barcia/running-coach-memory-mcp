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

List and search tools return **CSV** format for token efficiency. Single-record tools return JSON.

### Memory

| Tool | Parameters | Returns | Description |
|------|------------|---------|-------------|
| `add_memory` | `author`, `content` | JSON (Memory) | Store a coaching insight with automatic embedding generation. |
| `search_memories` | `query`, `limit?` | CSV (`id,created_at,author,content,distance`) | Semantic vector search. |
| `list_memories` | `author?`, `limit?` | CSV (`id,created_at,author,content`) | List memories in reverse chronological order. |
| `get_memory` | `memory_id` | JSON (Memory) | Retrieve a single memory by ID. |
| `delete_memory` | `memory_id` | JSON (bool) | Permanently delete a memory and its embedding. |

### Plans

| Tool | Parameters | Returns | Description |
|------|------------|---------|-------------|
| `add_plan` | `planned_at`, `description`, `notes?` | JSON (Plan) | Schedule a workout. |
| `get_plan` | `plan_id` | JSON (Plan) | Get plan details by ID. |
| `list_plans` | `start_date?`, `end_date?`, `status?`, `limit?` | CSV (`id,planned_at,description,notes,status,activity_id`) | Query plans with optional filters. |
| `get_today_plan` | — | CSV (same) | Get all plans scheduled for today. |
| `get_upcoming_plans` | `days?` | CSV (same) | Get plans for the next N days (default: 7). |
| `update_plan` | `plan_id`, `planned_at?`, `description?`, `notes?`, `status?`, `activity_id?` | JSON (Plan) | Update any plan field. Key tool for closing the feedback loop. |
| `delete_plan` | `plan_id` | JSON (bool) | Permanently delete a plan record. |

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
