# Home Orchestrator agent guide

## Goal

Build the smallest useful mobile-first bilingual family assistant. Supabase
Postgres is the source of truth; LangGraph routes every message to capture,
query, or conversation specialists. The assistant has events, tasks, and
standalone notes. Events can recur daily, weekly, or monthly.

## Commands

- Install/sync: `uv sync`
- Run: `uv run python app.py`
- Test: `uv run python -m unittest -v`

## Architecture

- `board_db.py`: Supabase Data API queries, deterministic Today, and mutations.
- `board_graph.py`: OpenRouter router plus capture/query/chat graph nodes.
- `auth.py`, `board_api.py`, `conversation_api.py`: focused FastAPI routes.
- `recurrence.py`: server-side recurrence expansion and exceptions.
- The family assistant is read-only: AI-generated SQL runs only against a
  household-scoped in-memory SQLite projection, never the writable board connection.
- `weather.py`: OpenWeather city lookup, five-day aggregation, and short cache.
- `app.py`: FastAPI setup, middleware, and static file serving.
- `conversation_api.py`: Deepgram speech-to-text and unified messages.
- `static/`: dependency-free bilingual browser UI.
- `supabase/migrations/`: Postgres schema, household membership, and RLS.
- `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY`: required.

## Working rules

- Route every message through LangGraph; keep ordinary CRUD in `BoardDatabase`
  behind `BoardService`.
- Keep board state in Supabase domain tables, not LangGraph checkpoints.
- AI may infer who should be reminded from household context. This is never
  ownership or assignment, and it must remain visible and correctable.
- AI may propose one preparation for an event or task; save it only when the
  user accepts it, and keep it manually editable afterward.
- Keep conversations continuous. Queries remain read-only; proposed item changes
  require explicit confirmation. Never expose generated SQL.
- Preserve the input language in generated titles and details.
- Keep Chinese and English UI strings in `static/app.js`.
- Keep Home limited to unified voice/text conversation and deterministic Today.
- Keep primary mobile navigation to Home, Calendar, and Notes.
- Dated tasks belong in Calendar; undated tasks stay in a small Unscheduled list.
- Events and tasks support append-only follow-up notes.
- Keep weather optional: provider failures must not block board data.
- Store one row per recurring event series and expand requested calendar ranges
  on the server. Series edits and deletion apply to every occurrence.
- Keep recurrence event-only and limited to daily, weekly, and monthly. Preserve
  fixed day-of-month versus month-end rules and inclusive recurrence end dates.
- Store cancelled or moved occurrences in `recurrence_exceptions`, keyed by the
  original local occurrence date. Never materialize every future occurrence.
- Do not add React, an ORM, social login, or notification delivery until a concrete
  requirement needs them.
- Never commit `.env`, database credentials, API keys, or audio.
- Add one focused runnable test for non-trivial state behavior.
