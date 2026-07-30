# Home Orchestrator agent guide

## Goal

Build the smallest useful bilingual family board. SQLite domain tables are the
source of truth; LangGraph orchestrates AI ingestion. The board has three item
types: events, tasks, and notes. Events can recur daily, weekly, or monthly.

## Commands

- Install/sync: `uv sync`
- Run: `uv run home-orchestrator`
- Test: `uv run python -m unittest -v`

## Architecture

- `board_db.py`: SQLite schema, transactions, board queries, and mutations.
- `board_graph.py`: OpenRouter extraction and the multi-item ingestion graph.
- `weather.py`: OpenWeather city lookup, five-day aggregation, and short cache.
- `app.py`: FastAPI routes, Groq speech-to-text, and static file serving.
- `python-dateutil`: server-side recurrence expansion for calendar date ranges.
- `static/`: dependency-free bilingual browser UI.
- `data/board.sqlite3`: runtime state; never commit it.
- `BOARD_DB_PATH`: optional local database override for isolated tests.

## Working rules

- Route AI-created items through LangGraph; keep ordinary CRUD in
  `BoardDatabase` transactions behind `BoardService`.
- Keep board state in domain tables, not LangGraph checkpoints.
- AI may suggest an owner from household context, but the user must be able to
  change or clear every suggestion before confirmation. Notes never have owners.
- Preserve the input language in generated titles and details.
- Keep Chinese and English UI strings in `static/app.js`.
- Keep weather optional: provider failures must not block board data.
- Store one row per recurring event series and expand requested calendar ranges
  on the server. Series edits and deletion apply to every occurrence.
- Keep recurrence event-only and limited to daily, weekly, and monthly. Preserve
  fixed day-of-month versus month-end rules and inclusive recurrence end dates.
- Store cancelled or moved occurrences in `recurrence_exceptions`, keyed by the
  original local occurrence date. Never materialize every future occurrence.
- Do not add React, an ORM, authentication, or notifications until a concrete
  requirement needs them.
- Never commit `.env`, API keys, audio, or local board data.
- Add one focused runnable test for non-trivial state behavior.
