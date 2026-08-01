# Hearthbook

Hearthbook is a mobile-first bilingual family assistant. Speak or type once to
record a plan, ask about the household, or continue a conversation. The Home
screen shows a deterministic summary of what happens, is due, is overdue, or
needs a reminder today.

Hearthbook 是一个移动端优先的双语家庭助手。用户可以通过文字或语音记录安排、查询家庭事项，或继续一段对话；Home 页面用确定性的 Today 视图展示今天发生、到期、逾期和需要提醒的内容。

## Product model

- Events, tasks, and standalone notes share one household database.
- Dated tasks appear in Calendar; undated tasks stay in `Unscheduled`.
- Events may recur daily, weekly, or monthly, including fixed-day and month-end rules.
- Events and tasks have append-only follow-up notes.
- `remind_member_id` identifies who should be reminded. It is not ownership,
  assignment, claiming, or a kanban workflow.
- Tasks use `completed_at`; events and tasks can be edited manually afterward.
- Every message is routed through LangGraph to capture, query, or chat.
- Capture creates drafts for explicit review. Query uses a household-scoped,
  read-only in-memory SQLite projection and may propose one item update; the
  browser applies that update only after explicit confirmation.

## Repository structure

```text
backend/hearthbook/
  api/          FastAPI auth, household, board, conversation, and notification routes
  domain/       item models, recurrence, calendar, and Today calculations
  llm/          OpenRouter/LangGraph routing, capture, chat, and safe SQL queries
  services/     application operations used by the API routes
  storage/      Supabase board and conversation persistence
  main.py       FastAPI app, middleware, static files, and /health
frontend/       dependency-free bilingual browser/PWA UI
design-system/  visual reference material
supabase/
  migrations/   Postgres schema, RPC transactions, membership, and RLS
  functions/    Edge Functions, including daily-notifications
tests/          focused API, graph, domain, frontend, and deployment-boundary checks
```

Supabase Postgres is the source of truth. The SQLite database used by the query
assistant is an in-memory, household-scoped projection and is never the write
connection. The ignored `data/` directory is local runtime data, not product
storage.

## Run locally

```powershell
Copy-Item .env.example .env
# Fill the required values locally. Never commit .env.
uv sync
uv run python -m backend.hearthbook.main
```

Open <http://127.0.0.1:8000>.

Required for the app: `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, and
`OPENROUTER_API_KEY`. Voice input additionally needs `DEEPGRAM_API_KEY`.
`OPENROUTER_MODEL` defaults to `openrouter/free`; `DEEPGRAM_MODEL` defaults to
`nova-3`.

Apply every file in `supabase/migrations/` in filename order before using the
app.

## Web Push notifications

The `daily-notifications` Supabase Edge Function sends reminders and the daily
summary. Supabase Cron invokes it; Railway is not contacted by the Cron job and
can sleep when nobody uses the app.

For the notification path, Railway needs:

- `SUPABASE_SECRET_KEY`: a backend-only `sb_secret_...` key.
- `VAPID_PUBLIC_KEY`: the public half of one permanent VAPID key pair.

Generate the VAPID pair once:

```powershell
npx --yes web-push@3.6.7 generate-vapid-keys
```

Copy `publicKey` to Railway and Supabase; keep `privateKey` in Supabase only.
Generate the Cron secret once without sharing it:

```powershell
node -e "console.log(require('crypto').randomBytes(32).toString('base64url'))"
```

Set these Supabase Edge Function secrets and deploy the function:

```powershell
npx supabase@latest login
npx supabase@latest secrets set --project-ref YOUR_PROJECT_REF VAPID_PUBLIC_KEY=YOUR_PUBLIC_KEY VAPID_PRIVATE_KEY=YOUR_PRIVATE_KEY VAPID_SUBJECT=https://YOUR-RAILWAY-DOMAIN NOTIFICATION_CRON_SECRET=YOUR_RANDOM_SECRET
npx supabase@latest functions deploy daily-notifications --project-ref YOUR_PROJECT_REF --no-verify-jwt
```

Then run `202607310005_notifications.sql`, followed by this once in the
Supabase SQL editor:

```sql
select vault.create_secret(
  'https://YOUR-PROJECT-REF.supabase.co/functions/v1/daily-notifications',
  'hearthbook_notification_edge_url'
);
select vault.create_secret(
  'YOUR_RANDOM_SECRET',
  'hearthbook_notification_cron_secret'
);
```

The migration creates the one-minute `hearthbook-notifications` Cron job. It
does nothing until both Vault secrets exist. Railway must not contain
`VAPID_PRIVATE_KEY`, `VAPID_SUBJECT`, or `NOTIFICATION_CRON_SECRET`.

Verify the job with:

```sql
select jobid, jobname, schedule, active
from cron.job
where jobname = 'hearthbook-notifications';
```

On iOS 16.4 or later, add Hearthbook to the Home Screen before enabling
notifications. The saved device timezone is refreshed when the app opens and
controls the local 9 AM daily summary.

## Test

```powershell
uv run python -m unittest -v
```

Tests use small contract stubs and do not call AI, transcription, or Supabase
providers.
