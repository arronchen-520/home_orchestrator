alter table public.recurrence_exceptions
    add column reminder_at timestamptz,
    add column reminder_overridden boolean not null default false;
