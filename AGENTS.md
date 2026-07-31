# Home Orchestrator agent guide

## Goal

Build the smallest useful bilingual family board. Supabase Postgres domain
tables are the source of truth; LangGraph orchestrates AI ingestion. The board has three item
types: events, tasks, and notes. Events can recur daily, weekly, or monthly.

## Commands

- Install/sync: `uv sync`
- Run: `uv run python app.py`
- Test: `uv run python -m unittest -v`

## Architecture

- `board_db.py`: Supabase Data API queries, RPC-backed transactions, and mutations.
- `board_graph.py`: OpenRouter extraction and the multi-item ingestion graph.
- The family assistant is read-only: AI-generated SQL runs only against a
  household-scoped in-memory SQLite projection, never the writable board connection.
- `weather.py`: OpenWeather city lookup, five-day aggregation, and short cache.
- `app.py`: FastAPI routes, Groq speech-to-text, and static file serving.
- `python-dateutil`: server-side recurrence expansion for calendar date ranges.
- `static/`: dependency-free bilingual browser UI.
- `supabase/migrations/`: Postgres schema, household membership, and RLS.
- `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY`: required.

## Working rules

- Route AI-created items through LangGraph; keep ordinary CRUD in
  `BoardDatabase` behind `BoardService`.
- Keep board state in Supabase domain tables, not LangGraph checkpoints.
- AI may suggest an owner from household context, but the user must be able to
  change or clear every suggestion before confirmation. Notes never have owners.
- AI may propose one preparation for an event or task; save it only when the
  user accepts it, and keep it manually editable afterward.
- Keep assistant conversations continuous but read-only. Do not expose generated
  SQL in the UI or add chat mutations without a concrete requirement.
- Preserve the input language in generated titles and details.
- Keep Chinese and English UI strings in `static/app.js`.
- Keep weather optional: provider failures must not block board data.
- Store one row per recurring event series and expand requested calendar ranges
  on the server. Series edits and deletion apply to every occurrence.
- Keep recurrence event-only and limited to daily, weekly, and monthly. Preserve
  fixed day-of-month versus month-end rules and inclusive recurrence end dates.
- Store cancelled or moved occurrences in `recurrence_exceptions`, keyed by the
  original local occurrence date. Never materialize every future occurrence.
- Do not add React, an ORM, social login, or notifications until a concrete
  requirement needs them.
- Never commit `.env`, database credentials, API keys, or audio.
- Add one focused runnable test for non-trivial state behavior.
