import { createClient } from "npm:@supabase/supabase-js@2.57.0";
import { DateTime } from "npm:luxon@3.5.0";
import webpush from "npm:web-push@3.6.7";

type Row = Record<string, any>;
const encoder = new TextEncoder();
const weekdayCodes = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"];

function sameSecret(left: string, right: string) {
  const a = encoder.encode(left); const b = encoder.encode(right);
  let difference = a.length ^ b.length;
  for (let i = 0; i < Math.max(a.length, b.length); i += 1) difference |= (a[i] || 0) ^ (b[i] || 0);
  return difference === 0;
}
function zoned(value: string, zone: string) { return DateTime.fromISO(value, { setZone: true }).setZone(zone); }
function localDate(value: string, zone: string) { return DateTime.fromISO(`${value}T00:00:00`, { zone }); }
function itemDate(item: Row, zone: string) {
  const value = item.kind === "event" ? item.start_date || item.start_at : item.due_date || item.due_at;
  return value ? (value.length === 10 ? value : zoned(value, zone).toISODate()) : null;
}
function occurrenceStart(item: Row, occurrenceDate: string, zone: string) {
  if (item.all_day) return localDate(occurrenceDate, zone);
  const original = zoned(item.start_at, zone);
  return DateTime.fromObject({ year: +occurrenceDate.slice(0, 4), month: +occurrenceDate.slice(5, 7), day: +occurrenceDate.slice(8, 10), hour: original.hour, minute: original.minute, second: original.second, millisecond: original.millisecond }, { zone });
}
function isOccurrence(item: Row, day: DateTime, zone: string) {
  const firstDate = itemDate(item, zone);
  if (!firstDate || item.kind !== "event" || !item.recurrence) return false;
  const first = localDate(firstDate, zone).startOf("day"); const current = day.startOf("day");
  const until = item.recurrence_until ? localDate(item.recurrence_until, zone).endOf("day") : null;
  if (current < first || (until && current > until)) return false;
  if (item.recurrence === "daily") return true;
  if (item.recurrence === "weekly") {
    const weekdays = item.weekdays?.length ? item.weekdays : [weekdayCodes[first.weekday - 1]];
    return weekdays.includes(weekdayCodes[current.weekday - 1]);
  }
  return item.monthly_on_last_day ? current.day === current.endOf("month").day : current.day === first.day;
}
function effectiveOccurrence(item: Row, occurrenceDate: string, zone: string, exceptions: Map<string, Row>) {
  const exception = exceptions.get(`${item.id}:${occurrenceDate}`); if (exception?.cancelled) return null;
  const base = occurrenceStart(item, occurrenceDate, zone);
  const start = exception?.start_date ? localDate(exception.start_date, zone) : exception?.start_at ? zoned(exception.start_at, zone) : base;
  return { ...item, ...exception, series_id: item.id, occurrence_date: occurrenceDate, start };
}
function reminderTime(item: Row, occurrence: Row, zone: string) {
  const original = occurrenceStart(item, itemDate(item, zone)!, zone);
  return occurrence.start.plus({ milliseconds: zoned(item.reminder_at, zone).toMillis() - original.toMillis() });
}
function candidates(item: Row, now: DateTime, zone: string, exceptions: Map<string, Row>) {
  if (!item.recurrence || !item.reminder_at) return [];
  const original = occurrenceStart(item, itemDate(item, zone)!, zone);
  const offset = zoned(item.reminder_at, zone).toMillis() - original.toMillis();
  const expected = now.minus({ milliseconds: offset }).setZone(zone).startOf("day");
  return [-1, 0, 1].flatMap((delta) => {
    const day = expected.plus({ days: delta });
    if (!isOccurrence(item, day, zone)) return [];
    const occurrence = effectiveOccurrence(item, day.toISODate()!, zone, exceptions);
    return occurrence ? [occurrence] : [];
  });
}
function reminderKey(item: Row) { return `reminder:${item.series_id || item.id}:${item.occurrence_date || "single"}:${item.reminder_at}`; }
function reminderPayload(item: Row, language: string) {
  const title = language === "zh" ? (item.kind === "event" ? "日程提醒" : "待办提醒") : (item.kind === "event" ? "Event reminder" : "Task reminder");
  return { title, body: item.title, url: "/#calendar", tag: reminderKey(item) };
}
function summaryPayload(items: Row[], language: string, localDay: string) {
  const open = items.filter((item) => !item.completed_at); const titles = open.slice(0, 3).map((item) => item.title).join(language === "zh" ? "、" : ", ");
  const body = language === "zh" ? (open.length ? `${open.length} 项：${titles}` : "今天没有安排或待办。") : (open.length ? `${open.length} items: ${titles}` : "Nothing planned or due today.");
  return { title: language === "zh" ? "今日摘要" : "Today's summary", body: open.length > 3 ? `${body}…` : body, url: "/#home", tag: `summary:${localDay}` };
}
function todayItems(items: Row[], now: DateTime, zone: string, exceptions: Map<string, Row>) {
  const target = now.toISODate()!; const result = new Map<string, Row>();
  const add = (item: Row) => result.set(`${item.series_id || item.id}:${item.occurrence_date || ""}`, item);
  for (const item of items) {
    if (item.kind === "note") continue;
    if (!item.recurrence) {
      const scheduled = itemDate(item, zone); const reminder = item.reminder_at && zoned(item.reminder_at, zone).toISODate();
      if (scheduled === target || reminder === target || (item.kind === "task" && scheduled && scheduled < target)) add(item);
      continue;
    }
    if (isOccurrence(item, now, zone)) { const occurrence = effectiveOccurrence(item, target, zone, exceptions); if (occurrence) add(occurrence); }
    for (const occurrence of candidates(item, now, zone, exceptions)) if (reminderTime(item, occurrence, zone).toISODate() === target) add(occurrence);
  }
  return [...result.values()];
}

Deno.serve(async (request) => {
  const secret = Deno.env.get("NOTIFICATION_CRON_SECRET") || "";
  if (!secret || !sameSecret(request.headers.get("x-notification-cron-secret") || "", secret)) return new Response("Unauthorized", { status: 401 });
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const vapidPublic = Deno.env.get("VAPID_PUBLIC_KEY")!;
  const vapidPrivate = Deno.env.get("VAPID_PRIVATE_KEY")!;
  const vapidSubject = Deno.env.get("VAPID_SUBJECT")!;
  if (!serviceKey || !vapidPublic || !vapidPrivate || !vapidSubject) return new Response("Notifications are not configured", { status: 503 });
  webpush.setVapidDetails(vapidSubject, vapidPublic, vapidPrivate);
  const client = createClient(Deno.env.get("SUPABASE_URL")!, serviceKey);
  const now = DateTime.utc();
  const { data: subscriptions, error } = await client.from("push_subscriptions").select("id,user_id,endpoint,p256dh,auth,timezone,language").is("disabled_at", null);
  if (error) throw error;
  const userIds = [...new Set((subscriptions || []).map((item) => item.user_id))];
  const { data: members, error: membersError } = userIds.length ? await client.from("members").select("id,user_id,household_id").in("user_id", userIds).is("deleted_at", null) : { data: [], error: null };
  if (membersError) throw membersError;
  const byUser = new Map<string, Map<string, Set<string>>>();
  for (const member of members || []) {
    const homes = byUser.get(member.user_id) || new Map<string, Set<string>>(); const ids = homes.get(member.household_id) || new Set<string>();
    ids.add(member.id); homes.set(member.household_id, ids); byUser.set(member.user_id, homes);
  }
  const cache = new Map<string, Promise<{ items: Row[]; exceptions: Map<string, Row> }>>();
  const load = (householdId: string) => {
    if (!cache.has(householdId)) cache.set(householdId, (async () => {
      const { data: items, error } = await client.from("items").select("*").eq("household_id", householdId); if (error) throw error;
      const series = (items || []).filter((item) => item.recurrence).map((item) => item.id);
      const { data: exceptions, error: exceptionError } = series.length ? await client.from("recurrence_exceptions").select("*").in("series_id", series) : { data: [], error: null };
      if (exceptionError) throw exceptionError;
      return { items: items || [], exceptions: new Map((exceptions || []).map((item) => [`${item.series_id}:${item.occurrence_date}`, item])) };
    })());
    return cache.get(householdId)!;
  };
  let sent = 0;
  for (const subscription of subscriptions || []) {
    const localNow = now.setZone(subscription.timezone); if (!localNow.isValid) continue;
    const homes = byUser.get(subscription.user_id) || new Map<string, Set<string>>();
    const send = async (key: string, payload: Row) => {
      const { data: claimed, error: claimError } = await client.rpc("claim_notification_delivery", { target_subscription_id: subscription.id, target_notification_key: key });
      if (claimError || !claimed) return;
      try {
        await webpush.sendNotification({ endpoint: subscription.endpoint, keys: { p256dh: subscription.p256dh, auth: subscription.auth } }, JSON.stringify(payload), { TTL: 3600 });
        await client.from("notification_deliveries").update({ sent_at: now.toISO() }).eq("subscription_id", subscription.id).eq("notification_key", key); sent += 1;
      } catch (error: any) {
        if ([404, 410].includes(error?.statusCode)) await client.from("push_subscriptions").update({ disabled_at: now.toISO() }).eq("id", subscription.id);
        await client.from("notification_deliveries").delete().eq("subscription_id", subscription.id).eq("notification_key", key);
        console.error("Web Push failed", error?.statusCode || error);
      }
    };
    const summaryItems: Row[] = [];
    for (const [householdId, memberIds] of homes) {
      const { items, exceptions } = await load(householdId);
      for (const item of items) {
        if (!item.reminder_at || item.completed_at || !memberIds.has(item.remind_member_id)) continue;
        const occurrences = item.recurrence ? candidates(item, now, subscription.timezone, exceptions) : [{ ...item, series_id: null, occurrence_date: null }];
        for (const occurrence of occurrences) {
          const due = item.recurrence ? reminderTime(item, occurrence, subscription.timezone) : zoned(item.reminder_at, subscription.timezone);
          if (due >= now.minus({ minutes: 15 }) && due <= now) {
            const scheduled = { ...occurrence, reminder_at: due.toISO() };
            await send(reminderKey(scheduled), reminderPayload(scheduled, subscription.language));
          }
        }
      }
      if (localNow.hour === 9) summaryItems.push(...todayItems(items, localNow, subscription.timezone, exceptions));
    }
    if (localNow.hour === 9 && homes.size) await send(`summary:${localNow.toISODate()}`, summaryPayload(summaryItems, subscription.language, localNow.toISODate()!));
  }
  return Response.json({ subscriptions: subscriptions?.length || 0, sent });
});
