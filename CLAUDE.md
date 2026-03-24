# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Lingua

Rispondi sempre in italiano, indipendentemente dalla lingua usata dall'utente.

## Running the Agent

```bash
# Run directly (uses .env for configuration)
cd agent && python main.py

# Run in Docker (recommended for production)
docker-compose up -d

# Force immediate briefing (bypass scheduler)
RUN_NOW=true python main.py
```

## Configuration

All configuration is via `.env` in the root directory. Key variables:

| Variable | Description |
|---|---|
| `LLM_PROVIDER` | `openai` or `openrouter` |
| `LLM_MODEL` | Model name (e.g. `gpt-4o-mini`) |
| `OPENAI_API_KEY` / `OPENROUTER_API_KEY` | LLM credentials |
| `OPENWEATHER_KEY` | OpenWeatherMap API key |
| `CITY` | Primary city for weather |
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` | Telegram delivery (optional — falls back to stdout) |
| `BRIEFING_HOUR` / `BRIEFING_MINUTE` | Scheduled time (Europe/Rome timezone) |
| `DATA_PATH` | Path to persistent data directory (default: `./data`) |

## Architecture

The agent runs on APScheduler, triggering a `run_briefing()` function once daily. The flow:

1. `main.py` — Entry point and scheduler. Calls `run_briefing()` which orchestrates all tools.
2. `tools/weather.py` — Fetches OpenWeatherMap data. On Wednesdays adds Milan and Turin.
3. `tools/menu.py` — Uses LLM to suggest lunch and dinner. Reads/writes `data/meals.json` to avoid repeating meals within 7 days (resets weekly).
4. `tools/tasks.py` — Reads `data/tasks.json`, returns top 3 active tasks sorted by priority.
5. `llm.py` — LLM abstraction supporting OpenAI and OpenRouter. Use `get_llm_client()` to get the configured client.
6. `notifiers/telegram.py` — Sends the briefing to Telegram, chunking at 4096 chars. Falls back to stdout if credentials are missing.

**Data files** in `data/` are persisted across Docker restarts via volume mount:
- `tasks.json` — Task list with `id`, `title`, `priority`, `status` fields
- `meals.json` — Meal history keyed by week number to track recent suggestions

## Adding New Tools

Follow the pattern in `tools/weather.py` or `tools/tasks.py`: a standalone module with a single function that returns a formatted string or structured data. Import and call it inside `run_briefing()` in `main.py`.

## Adding New Notifiers

Follow `notifiers/telegram.py`: implement a `send(message: str)` function. The briefing message is assembled in `main.py` and passed to the notifier.
