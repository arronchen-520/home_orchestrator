# Hearthbook

Hearthbook is a mobile-first bilingual family assistant. Speak or type once to
record a plan, ask about the household, or continue a conversation. The home
screen shows a deterministic summary of what happens, is due, is overdue, or
needs a reminder today.

Hearthbook 是一个移动端优先的双语家庭助手。用户通过同一个语音或文字入口记录
安排、查询家庭事项或继续对话；首页可靠展示今天发生、今天到期、已经过期，以及
今天需要提醒的内容。

## Product model

- Events, tasks, and standalone notes share one household database.
- Dated tasks appear in Calendar; undated tasks stay in “Unscheduled”.
- Events may recur daily, weekly, or monthly, including month-end rules.
- Events and tasks have append-only follow-up notes.
- `remind_member_id` means who should be reminded. There is no ownership,
  assignment, claim, or kanban workflow.
- Tasks use `completed_at` instead of workflow columns.
- Every message is routed to a capture, query, or conversation node.
- Capture writes require review. Queries use a household-scoped, read-only
  in-memory SQLite projection that can scale independently from capture.

## Architecture

- `backend/hearthbook/api/`: FastAPI auth, board, conversation, and dependencies.
- `backend/hearthbook/llm/`: LangGraph router/specialists and read-only SQL projection.
- `backend/hearthbook/domain/`: item models, recurrence, calendar, and Today logic.
- `backend/hearthbook/services/`: application operations used by HTTP routes.
- `backend/hearthbook/storage/`: Supabase board and conversation persistence.
- `frontend/`: dependency-free mobile bilingual UI.
- `tests/`: focused API, graph, Today, recurrence, and SQL-boundary checks.
- `supabase/migrations/`: Postgres schema, RPC transactions, and RLS.

## Run

```powershell
Copy-Item .env.example .env
# Fill the required values locally. Never commit .env.
uv sync
uv run python -m backend.hearthbook.main
```

Open <http://127.0.0.1:8000>.

Required: `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, and
`OPENROUTER_API_KEY`. Voice needs `DEEPGRAM_API_KEY`.

Apply `supabase/migrations/` in filename order. The mobile refactor intentionally
replaces the previous application tables; later migrations move forward normally.

## Test

```powershell
uv run python -m unittest -v
```

Tests use small contract stubs and do not call AI, transcription, or Supabase providers.
