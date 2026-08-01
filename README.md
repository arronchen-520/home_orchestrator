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

## Web Push notifications

Notifications are sent by the Supabase `daily-notifications` Edge Function;
Railway is not contacted by the Cron job and can sleep when nobody uses the app.

Railway needs only:

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

Set these Supabase Edge Function secrets. `NOTIFICATION_CRON_SECRET` is a new
random value used only by the Edge Function and Supabase Vault:

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
`VAPID_PRIVATE_KEY`, `VAPID_SUBJECT`, or `NOTIFICATION_CRON_SECRET`. Verify it with:

```sql
select jobid, jobname, schedule, active
from cron.job
where jobname = 'hearthbook-notifications';
```

On iOS 16.4 or later, add Hearthbook to the Home Screen before using the
Settings → Allow notifications button. The saved device timezone is refreshed
whenever the app opens and controls the local 9 AM daily summary.

## Test

```powershell
uv run python -m unittest -v
```

Tests use small contract stubs and do not call AI, transcription, or Supabase providers.
