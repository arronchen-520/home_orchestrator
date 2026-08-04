# Hearthbook agent guide

## Goal

Build the smallest useful mobile-first bilingual family assistant. Supabase
Postgres is the source of truth. LangGraph routes text, audio, and image input
to capture, query, or chat. The board contains events, tasks, and standalone
notes.

## Commands

- Install/sync: `uv sync`
- Run: `uv run python -m backend.hearthbook.main`
- Test: `uv run python -m unittest -v`

## Current structure

- `backend/hearthbook/main.py`: FastAPI app, session/household middleware,
  security headers, static serving, and `/health`.
- `backend/hearthbook/api/`: auth and household setup, board CRUD, unified
  text/audio messages, and push-subscription routes.
- `backend/hearthbook/domain/`: Pydantic item models, recurrence expansion,
  Calendar, and deterministic Today logic.
- `backend/hearthbook/llm/`: OpenRouter model/graph plus capture, board-context
  query, and chat nodes. Image understanding is in the conversation API and
  feeds the same graph.
- `backend/hearthbook/services/`: `BoardService`, the API boundary for board
  reads, writes, conversation handling, and confirmation.
- `backend/hearthbook/storage/`: Supabase board and conversation persistence.
- `frontend/`: dependency-free bilingual browser/PWA UI for Home, Calendar,
  Notes, review/confirmation, editing, and notifications.
- `supabase/migrations/`: Postgres tables, RPC transactions, household
  membership, RLS, and notification delivery bookkeeping.
- `supabase/functions/daily-notifications/`: Supabase Cron/Web Push delivery.
- `design-system/`: visual reference material; runtime UI remains in `frontend/`.
- `tests/`: focused runnable contract and behavior checks.

## Architecture rules

- Keep board state in Supabase domain tables, not LangGraph checkpoints.
- Route every message through LangGraph. Keep ordinary CRUD in
  `BoardDatabase` behind `BoardService`.
- Capture produces drafts and requires explicit confirmation before creating
  items. Confirmation also accepts or rejects preparations and selects reminder
  recipients.
- Query first receives a compact household-scoped index plus the auth-bound
  member, then receives full details only for item ids it selects. Never restore
  generated SQL or a writable query connection.
- Query replies may propose one supported item update. The browser must show
  it and require confirmation before calling the normal item `PATCH` route.
- LLM recurrence changes must provide a complete rule and affect the entire
  event series only, never one occurrence.
- Validate returned query references against the supplied board context.
- Current minimal UI intentionally shows an LLM update's `confirmation` text,
  not a field-by-field `action.fields` diff, and does not render query
  `references`. Revisit either only when the product needs inspectable update
  diffs or links to supporting board items.
- Keep conversations continuous and preserve the input language in generated
  titles, details, and replies.
- AI may infer who should be reminded from household context. This is visible
  and correctable, and is never ownership or assignment. Preserve
  `remind_member_ids` semantics, cap it at five members, and use it for
  Calendar/Tasks “Mine” filters.
- AI may suggest one preparation for an event or task. Save it only after the
  user accepts it; keep it manually editable.
- Keep Home limited to unified text/audio/image conversation and deterministic
  Today.
  Primary mobile navigation is Home, Calendar, and Notes.
- Dated tasks belong in Calendar; undated tasks stay in `Unscheduled`.
- Events and tasks support append-only follow-up notes. Notes themselves do not
  have reminders or follow-up notes.
- Store timed schedules with an item-level IANA `schedule_timezone`. Preserve
  all-day and inclusive multi-day event dates when expanding Calendar/Today.
- Store one row per recurring event series. Expand requested ranges on the
  server; series edits/deletion affect all occurrences.
- Recurrence is event-only and limited to daily, weekly, and monthly. Preserve
  weekly weekday sets, fixed day-of-month versus month-end rules, and inclusive
  recurrence end dates.
- Store cancelled or moved occurrences in `recurrence_exceptions`, keyed by the
  original local occurrence date. Never materialize every future occurrence.
- Keep Web Push delivery in the Supabase Edge Function. The app only manages
  subscriptions; never move VAPID private keys or Cron secrets into the client.
- Consume the authenticated user's daily AI quota before OpenRouter or
  Deepgram calls. The default is five requests per UTC day.

## Boundaries

- Required app configuration: `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, and
  `OPENROUTER_API_KEY`. Voice additionally needs `DEEPGRAM_API_KEY`.
- `OPENROUTER_MODEL` defaults to `openrouter/free`; `DEEPGRAM_MODEL` defaults
  to `nova-3`.
- `SUPABASE_SECRET_KEY` and `VAPID_PUBLIC_KEY` are backend notification
  configuration. VAPID private material and `NOTIFICATION_CRON_SECRET` stay in
  Supabase only.
- Trust-boundary limits are 1,000 text characters, 5 MB audio, 3 MB PNG/JPEG
  images, and five reminder recipients. The browser limits recordings to 60
  seconds.
- Never commit `.env`, credentials, API keys, private keys, or audio.
- A Git commit does not apply Supabase migrations or deploy Edge Functions;
  verify those separately before claiming production behavior.
- Do not add React, an ORM, social login, or another service until a concrete
  requirement needs it.
- Add one focused runnable test for non-trivial state behavior. Keep tests
  provider-free unless a live integration is explicitly requested.
