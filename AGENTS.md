# Home Orchestrator agent guide

## Goal

Build the smallest useful bilingual family board. LangGraph owns every board
mutation. Phase 1 has three item types: events, tasks, and notes.

## Commands

- Install/sync: `uv sync`
- Run: `uv run home-orchestrator`
- Test: `uv run python -m unittest -v`

## Architecture

- `board_graph.py`: state schema, OpenRouter classification, mutations, and
  SQLite-backed LangGraph graph.
- `app.py`: FastAPI routes, Groq speech-to-text, and static file serving.
- `static/`: dependency-free bilingual browser UI.
- `data/board.sqlite3`: runtime state; never commit it.

## Working rules

- Route every create, owner, status, and delete operation through LangGraph.
- Keep AI owner assignment impossible; owner is always a user choice.
- Preserve the input language in generated titles and details.
- Keep Chinese and English UI strings in `static/app.js`.
- Do not add React, an ORM, authentication, notifications, or recurrence until
  a concrete Phase 2 requirement needs them.
- Never commit `.env`, API keys, audio, or local board data.
- Add one focused runnable test for non-trivial state behavior.
