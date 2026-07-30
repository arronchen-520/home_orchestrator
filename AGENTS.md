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
- `app.py`: FastAPI routes, Groq speech-to-text, and static file serving.
- `static/`: dependency-free bilingual browser UI.
- `data/board.sqlite3`: runtime state; never commit it.
- `BOARD_DB_PATH`: optional local database override for isolated tests.

## Working rules

- Route AI-created items through LangGraph; keep ordinary CRUD in
  `BoardDatabase` transactions behind `BoardService`.
- Keep board state in domain tables, not LangGraph checkpoints.
- Keep AI owner assignment impossible; owner is always a user choice.
- Preserve the input language in generated titles and details.
- Keep Chinese and English UI strings in `static/app.js`.
- Store one row per recurring event series and expand occurrences in the
  calendar. Series edits and deletion apply to every occurrence.
- Keep recurrence event-only and limited to daily, weekly, and monthly. Do not
  add end dates or per-occurrence exceptions until a concrete requirement needs
  them. Preserve the distinction between a fixed day-of-month and the last day
  of each month.
- Do not add React, an ORM, authentication, or notifications until a concrete
  requirement needs them.
- Never commit `.env`, API keys, audio, or local board data.
- Add one focused runnable test for non-trivial state behavior.
