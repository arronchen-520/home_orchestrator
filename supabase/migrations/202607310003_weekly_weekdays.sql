alter table public.items
    add column weekdays text[] not null default '{}'::text[],
    add constraint items_weekdays_check check (
        cardinality(weekdays) = 0
        or recurrence = 'weekly'
            and weekdays <@ array['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']::text[]
    );
