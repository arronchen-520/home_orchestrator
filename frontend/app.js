"use strict";

const copy = {
  zh: {
    settings: "设置", homeTitle: "今天有什么想记录的吗？",
    homeSubtitle: "记录、查询，或者聊聊。", voiceTitle: "家庭助手",
    tapToTalk: "点一下开始说话", stopRecording: "说完点这里发送", preferTyping: "文字输入", uploadImage: "上传图片",
    messageLabel: "输入记录、问题或消息", messagePlaceholder: "例如：周六三点看牙，提醒妈妈",
    send: "发送", imageNoteLabel: "补充说明（可选）", imageNotePlaceholder: "例如：帮我记到日历", sendImage: "发送图片", imageUploaded: "已上传图片", imageOnly: "请上传 3 MB 以内的 PNG 或 JPEG 图片", conversation: "对话", clear: "清空", remindWho: "提醒谁",
    preparation: "准备事项", cancel: "取消", confirm: "确认", todayEyebrow: "今日摘要",
    todayTitle: "今天", today: "今天", refresh: "刷新", plans: "安排", calendar: "日历",
    previousMonth: "上个月", nextMonth: "下个月", emptyCalendarDay: "这一天还没有安排。",
    calendarFilter: "筛选安排", taskFilter: "筛选待办", filterAll: "全部", filterMine: "我的",
    calendarDensityHelp: "色深表示当天安排数量",
    unscheduled: "未定时间", taskSpace: "待办与笔记", tasks: "待办", dueSoon: "未来 7 天", moreTasks: "展开更多", emptyTasks: "没有待办。", familyMemory: "常用信息", notes: "笔记",
    notesHelp: "家里常用的信息，放在这里。", home: "首页",
    close: "关闭", edit: "编辑", title: "标题", details: "详情", basicInfo: "基本信息", schedule: "时间安排", moreActions: "更多操作", delete: "删除", save: "保存",
    followups: "进展记录", addFollowup: "添加进展", followupPlaceholder: "记录最新进展…",
    add: "添加", logout: "退出登录", authTitle: "登录 Hearthbook", email: "邮箱",
    password: "密码", login: "登录", signup: "创建账号", householdSetup: "设置家庭",
    householdName: "家庭名称", yourName: "你的名字", memberRole: "你的身份（可选）", myRole: "我的身份", saveProfile: "保存资料", createHousehold: "创建家庭",
    orJoin: "或者加入已有家庭", inviteCode: "家庭邀请码", joinHousehold: "加入家庭", households: "家庭组", currentHousehold: "当前家庭", myProfile: "我的资料", otherHouseholds: "其他家庭", joinAnotherHousehold: "加入已有家庭", account: "账户", switchHousehold: "切换家庭", createAnotherHousehold: "创建新家庭", leaveHousehold: "退出这个家庭", leaveHouseholdConfirm: "确定退出这个家庭吗？家庭中的记录会保留。",
    event: "日程", task: "待办", note: "笔记", allDay: "全天", due: "截止",
    starts: "开始", reminder: "提醒", remind: "提醒", done: "已完成", markDone: "标记完成", markOpen: "恢复待办",
    emptyToday: "今天还没有安排。说一句或输入文字来添加。", emptyNotes: "还没有笔记。告诉我需要记住什么。",
    emptyConversation: "还没有对话。", listening: "正在听…", thinking: "正在处理…",
    saved: "已保存", deleted: "已删除", added: "已添加", confirmed: "已确认",
    deleteConfirm: "确定删除这条内容吗？", deleteSeriesConfirm: "确定删除整个重复日程吗？",
    cancelOccurrenceConfirm: "确定只取消这一次日程吗？",
    microphoneError: "无法使用麦克风，可以改用文字输入。", networkError: "暂时连接不上，过一会儿再试。", serverError: "服务暂时不可用，请稍后再试。",
    authRequired: "登录状态已失效，请重新登录。", householdSetupRequired: "请先创建或加入一个家庭。", invalidRequest: "请检查输入内容后再试。",
    voiceUnavailable: "语音服务暂时不可用，可以改用文字输入。", voiceTranscriptionFailed: "没有成功识别语音，可以再试一次或改用文字输入。",
    imageUnderstandingFailed: "暂时无法读懂这张图片，请换一张更清晰的图片或补充说明。",
    emailAlreadyRegistered: "这个邮箱已经注册过了，请直接登录。", signupFailed: "暂时无法创建账号，请稍后再试。", assistantUnavailable: "助手暂时不可用，请稍后再试。",
    noSpeech: "没有听到声音，再试一次。", familyMembers: "家庭成员", invite: "邀请码",
    recurrence: "重复", noRecurrence: "不重复", daily: "每天", weekly: "每周", monthly: "每月",
    monthlyLastDay: "每月最后一天", recurrenceEnds: "重复结束", editScope: "修改范围",
    repeatOn: "重复日期", weekdayMO: "周一", weekdayTU: "周二", weekdayWE: "周三", weekdayTH: "周四", weekdayFR: "周五", weekdaySA: "周六", weekdaySU: "周日",
    thisOccurrence: "只修改这一次", entireSeries: "修改整个系列", occurrenceEditHint: "这次修改只影响当前日期。", restoreOccurrence: "恢复系列默认设置", restoreOccurrenceConfirm: "恢复这个日期的系列默认设置吗？这次单独修改会被移除。", occurrenceRestored: "已恢复系列默认设置", date: "日期", ends: "结束",
    specificTime: "指定时间", dueDate: "截止日期", overdue: "已过期",
    notifications: "通知", notificationHelp: "在提醒时间推送日程和待办，并在每天上午 9 点（本地时间）发送今日摘要。",
    allowNotifications: "允许通知", disableNotifications: "关闭通知", notificationsEnabled: "通知已开启",
    notificationsChecking: "正在检查通知状态…", notificationsUnavailable: "通知暂时不可用，请稍后再试。",
    installForNotifications: "请先将 Hearthbook 添加到主屏幕，再开启通知。",
    notificationsDenied: "通知权限已被拒绝，请在系统设置中开启。",
    notificationOn: "已开启", notificationOff: "未开启", notificationUnavailableShort: "不可用", notificationCheckingShort: "检查中",
  },
  en: {
    settings: "Settings", homeTitle: "Anything you'd like to note today?",
    homeSubtitle: "Add a note, ask a question, or just chat.", voiceTitle: "Family assistant",
    tapToTalk: "Tap to start talking", stopRecording: "Tap to send", preferTyping: "Text input", uploadImage: "Upload image",
    messageLabel: "Type a plan, question, or message", messagePlaceholder: "Example: Dentist Saturday at 3, remind Mom",
    send: "Send", imageNoteLabel: "Optional note", imageNotePlaceholder: "Example: Add this to the calendar", sendImage: "Send image", imageUploaded: "Image uploaded", imageOnly: "Upload a PNG or JPEG image up to 3 MB", conversation: "Conversation", clear: "Clear", remindWho: "Who should we remind?",
    preparation: "Preparation", cancel: "Cancel", confirm: "Confirm", todayEyebrow: "Today's summary",
    todayTitle: "Today", today: "Today", refresh: "Refresh", plans: "Plans", calendar: "Calendar",
    previousMonth: "Previous month", nextMonth: "Next month", emptyCalendarDay: "Nothing planned for this day.",
    calendarFilter: "Filter plans", taskFilter: "Filter tasks", filterAll: "All", filterMine: "Mine",
    calendarDensityHelp: "Darker days have more plans.",
    unscheduled: "No date yet", taskSpace: "Tasks and notes", tasks: "Tasks", dueSoon: "Due in 7 days", moreTasks: "Show more", emptyTasks: "No tasks yet.", familyMemory: "Household info", notes: "Notes",
    notesHelp: "Keep household details here.", home: "Home",
    close: "Close", edit: "Edit", title: "Title", details: "Details", basicInfo: "Basic information", schedule: "Schedule", moreActions: "More actions", delete: "Delete", save: "Save",
    followups: "Updates", addFollowup: "Add an update", followupPlaceholder: "Add the latest update…",
    add: "Add", logout: "Log out", authTitle: "Sign in to Hearthbook", email: "Email",
    password: "Password", login: "Sign in", signup: "Create account", householdSetup: "Set up your household",
    householdName: "Household name", yourName: "Your name", memberRole: "Your role (optional)", myRole: "My role", saveProfile: "Save profile", createHousehold: "Create household",
    orJoin: "Or join an existing household", inviteCode: "Household invite code", joinHousehold: "Join household", households: "Households", currentHousehold: "Current household", myProfile: "My profile", otherHouseholds: "Other households", joinAnotherHousehold: "Join an existing household", account: "Account", switchHousehold: "Switch household", createAnotherHousehold: "Create another household", leaveHousehold: "Leave this household", leaveHouseholdConfirm: "Leave this household? Its records will be kept.",
    event: "Event", task: "Task", note: "Note", allDay: "All day", due: "Due",
    starts: "Starts", reminder: "Reminder", remind: "Reminder", done: "Done", markDone: "Mark done", markOpen: "Mark open",
    emptyToday: "Nothing planned today. Speak or type to add something.", emptyNotes: "No notes yet. Tell me what to remember.",
    emptyConversation: "No messages yet.", listening: "Listening…", thinking: "Working…",
    saved: "Saved", deleted: "Deleted", added: "Added", confirmed: "Confirmed",
    deleteConfirm: "Delete this item?", deleteSeriesConfirm: "Delete this entire recurring event?",
    cancelOccurrenceConfirm: "Cancel only this occurrence?",
    microphoneError: "The microphone isn't available. You can type instead.", networkError: "Can't connect right now. Try again in a moment.", serverError: "The service is temporarily unavailable. Try again later.",
    authRequired: "Your session has expired. Please sign in again.", householdSetupRequired: "Create or join a household first.", invalidRequest: "Check your input and try again.",
    voiceUnavailable: "Voice service is temporarily unavailable. You can type instead.", voiceTranscriptionFailed: "I couldn't transcribe that. Try again or type instead.",
    imageUnderstandingFailed: "I couldn't read that image. Try a clearer image or add a note.",
    emailAlreadyRegistered: "That email is already registered. Try signing in.", signupFailed: "We couldn't create your account. Try again later.", assistantUnavailable: "The assistant is temporarily unavailable. Try again later.",
    noSpeech: "I didn't hear anything. Try again.", familyMembers: "Family members", invite: "Invite code",
    recurrence: "Repeats", noRecurrence: "Does not repeat", daily: "Daily", weekly: "Weekly", monthly: "Monthly",
    monthlyLastDay: "Last day of each month", recurrenceEnds: "Repeat until", editScope: "Edit scope",
    repeatOn: "Repeat on", weekdayMO: "Mon", weekdayTU: "Tue", weekdayWE: "Wed", weekdayTH: "Thu", weekdayFR: "Fri", weekdaySA: "Sat", weekdaySU: "Sun",
    thisOccurrence: "Only this occurrence", entireSeries: "Entire series", occurrenceEditHint: "Changes here affect this date only.", restoreOccurrence: "Restore series defaults", restoreOccurrenceConfirm: "Restore the series defaults for this date? Its one-off changes will be removed.", occurrenceRestored: "Series defaults restored", date: "Date", ends: "Ends",
    specificTime: "Specific time", dueDate: "Due date", overdue: "Overdue",
    notifications: "Notifications", notificationHelp: "Get event and task reminders, plus a daily summary at 9 AM local time.",
    allowNotifications: "Allow notifications", disableNotifications: "Turn off notifications", notificationsEnabled: "Notifications are on",
    notificationsChecking: "Checking notification status…", notificationsUnavailable: "Notifications are temporarily unavailable. Try again later.",
    installForNotifications: "Add Hearthbook to your Home Screen before turning on notifications.",
    notificationsDenied: "Notification permission is blocked. Enable it in system settings.",
    notificationOn: "On", notificationOff: "Off", notificationUnavailableShort: "Unavailable", notificationCheckingShort: "Checking",
  },
};

copy.zh.messageTooLong = "文字最多 1,000 个字符。";
copy.zh.recordingLimit = "录音最长 60 秒，已发送前 60 秒。";
copy.zh.audioTooLarge = "录音不能超过 5 MB。";
copy.en.messageTooLong = "Messages can be up to 1,000 characters.";
copy.en.recordingLimit = "Recordings can be up to 60 seconds. Sending the first 60 seconds.";
copy.en.audioTooLarge = "Recordings can be up to 5 MB.";
copy.zh.dailyLimit = "今天的 5 次 AI 请求已用完，请明天再试。";
copy.en.dailyLimit = "Today's 5 AI requests have been used. Try again tomorrow.";

const $ = (selector) => document.querySelector(selector);
const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
const MAX_MESSAGE_CHARS = 1000;
const MAX_AUDIO_BYTES = 5 * 1024 * 1024;
const MAX_RECORDING_MS = 60 * 1000;
const state = {
  language: localStorage.getItem("hearthbook-language") || (navigator.language.startsWith("zh") ? "zh" : "en"),
  board: { household: {}, members: [], items: [] },
  today: [], calendar: [], calendarMonth: dateKey().slice(0, 7), selectedDate: dateKey(), calendarAgendaOpen: false,
  calendarFilter: localStorage.getItem("hearthbook-calendar-filter") === "mine" ? "mine" : "all",
  taskFilter: localStorage.getItem("hearthbook-task-filter") === "mine" ? "mine" : "all",
  messages: [], pending: null, selectedItem: null,
  sessionId: localStorage.getItem("hearthbook-session") || null,
  households: [], activeHouseholdId: null,
  recorder: null, recordingTimer: null,
  notification: { ready: false, configured: false, publicKey: "", registration: null, subscription: null },
};

function t(key) { return copy[state.language][key] || key; }

async function api(path, options = {}) {
  let response;
  try {
    response = await fetch(path, {
      ...options,
      headers: options.body instanceof FormData ? options.headers : { "Content-Type": "application/json", ...options.headers },
    });
  } catch (_) {
    const error = new Error(t("networkError"));
    error.status = 0;
    throw error;
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const codeCopy = {
      daily_ai_limit: "dailyLimit", server_error: "serverError", service_unavailable: "serverError",
      assistant_unavailable: "assistantUnavailable", auth_failed: "authRequired", email_already_registered: "emailAlreadyRegistered",
      signup_failed: "signupFailed", voice_unavailable: "voiceUnavailable", voice_transcription_failed: "voiceTranscriptionFailed",
      image_understanding_failed: "imageUnderstandingFailed", no_speech: "noSpeech", notifications_unavailable: "notificationsUnavailable",
    };
    const code = data.detail?.code;
    const knownDetails = { "Authentication required": "authRequired", "Household setup required": "householdSetupRequired" };
    const rawDetail = typeof data.detail === "string" ? data.detail : data.detail?.[0]?.msg || "";
    const safeDetail = codeCopy[code] ? t(codeCopy[code]) : response.status >= 500 ? t("serverError") : knownDetails[rawDetail] ? t(knownDetails[rawDetail]) : response.status === 422 ? t("invalidRequest") : rawDetail;
    const error = new Error(safeDetail || t("networkError"));
    error.status = response.status;
    throw error;
  }
  return data;
}

function showToast(message, isError = false) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.hidden = false;
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => { toast.hidden = true; }, 3200);
}

function dateKey(value = new Date()) {
  const date = value instanceof Date ? value : new Date(value);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function localDate(key) {
  const [year, month, day] = key.split("-").map(Number);
  return new Date(year, month - 1, day);
}

function formatDate(key, options = { weekday: "long", month: "short", day: "numeric" }) {
  return new Intl.DateTimeFormat(state.language === "zh" ? "zh-CN" : "en-CA", options).format(localDate(key));
}

function formatDateTime(value, allDay = false) {
  if (!value) return "";
  if (allDay && /^\d{4}-\d{2}-\d{2}$/.test(value)) return formatDate(value);
  return new Intl.DateTimeFormat(state.language === "zh" ? "zh-CN" : "en-CA", {
    month: "short", day: "numeric", ...(allDay ? {} : { hour: "numeric", minute: "2-digit" }),
  }).format(new Date(value));
}

function supportsPush() {
  return "serviceWorker" in navigator && "PushManager" in window && "Notification" in window;
}

function needsHomeScreenInstall() {
  return "standalone" in navigator && !navigator.standalone;
}

function renderNotificationSettings() {
  const button = $("#notificationButton");
  const status = $("#notificationStatus");
  const summary = $("#notificationSummary");
  button.className = "secondary-button full-width";
  button.setAttribute("aria-busy", String(!state.notification.ready));
  status.dataset.state = "";
  summary.textContent = "";
  let summaryKey = "notificationCheckingShort";
  if (!supportsPush() || needsHomeScreenInstall()) {
    button.disabled = true;
    status.textContent = needsHomeScreenInstall() ? t("installForNotifications") : t("notificationsUnavailable");
    status.dataset.state = "warning";
    summaryKey = "notificationUnavailableShort";
  } else if (!state.notification.ready || !state.notification.configured) {
    button.disabled = true;
    status.textContent = t(state.notification.ready ? "notificationsUnavailable" : "notificationsChecking");
    status.dataset.state = state.notification.ready ? "warning" : "";
    summaryKey = state.notification.ready ? "notificationUnavailableShort" : "notificationCheckingShort";
  } else if (Notification.permission === "denied") {
    button.disabled = true;
    status.textContent = t("notificationsDenied");
    status.dataset.state = "warning";
    summaryKey = "notificationUnavailableShort";
  } else {
    button.disabled = false;
    button.className = `${state.notification.subscription ? "secondary" : "primary"}-button full-width`;
    button.textContent = t(state.notification.subscription ? "disableNotifications" : "allowNotifications");
    status.textContent = state.notification.subscription ? t("notificationsEnabled") : "";
    status.dataset.state = state.notification.subscription ? "success" : "";
    summaryKey = state.notification.subscription ? "notificationOn" : "notificationOff";
  }
  summary.textContent = t(summaryKey);
}

function applicationServerKey(value) {
  const padding = "=".repeat((4 - value.length % 4) % 4);
  const bytes = atob((value + padding).replace(/-/g, "+").replace(/_/g, "/"));
  return Uint8Array.from(bytes, (character) => character.charCodeAt(0));
}

async function savePushSubscription(subscription) {
  const value = subscription.toJSON();
  await api("/api/notifications/subscriptions", {
    method: "POST",
    body: JSON.stringify({ ...value, timezone, language: state.language }),
  });
}

async function syncNotifications() {
  const config = await api("/api/notifications/config");
  state.notification.ready = true;
  state.notification.configured = config.enabled;
  state.notification.publicKey = config.vapid_public_key || "";
  if (config.enabled && supportsPush() && !needsHomeScreenInstall()) {
    try {
      const registration = await navigator.serviceWorker.register("/sw.js");
      state.notification.registration = registration;
      state.notification.subscription = await registration.pushManager.getSubscription();
      if (state.notification.subscription) await savePushSubscription(state.notification.subscription);
    } catch (_) { state.notification.configured = false; }
  }
  renderNotificationSettings();
}

async function removePushSubscription() {
  const subscription = state.notification.subscription;
  if (!subscription) return;
  await api("/api/notifications/subscriptions", {
    method: "DELETE", body: JSON.stringify({ endpoint: subscription.endpoint }),
  });
  await subscription.unsubscribe();
  state.notification.subscription = null;
  renderNotificationSettings();
}

function toLocalDateTime(value) {
  if (!value) return "";
  const date = new Date(value);
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
}

function itemDate(item) {
  const value = item.occurrence_date || item.start_date || item.due_date || item.start_at || item.due_at;
  return value ? (/^\d{4}-\d{2}-\d{2}$/.test(value) ? value : dateKey(value)) : "";
}

function itemTime(item) {
  if (item.kind === "event") {
    if (item.all_day || item.start_date) return t("allDay");
    return item.start_at ? formatDateTime(item.start_at) : "";
  }
  if (item.kind === "task") return item.due_at ? `${t("due")} ${formatDateTime(item.due_at)}` : item.due_date ? t("due") : "";
  return "";
}

function memberName(id) {
  return state.board.members.find((member) => member.id === id)?.name || "";
}

function reminderNames(item) {
  return (item.remind_member_ids || []).map(memberName).filter(Boolean);
}

function draftMeta(draft) {
  const parts = [];
  if (draft.kind === "event") {
    if (draft.start_date) parts.push(`${t("date")}: ${formatDate(draft.start_date)} · ${t("allDay")}`);
    else if (draft.start_at) {
      const end = draft.end_at ? `–${formatDateTime(draft.end_at)}` : "";
      parts.push(`${t("starts")}: ${formatDateTime(draft.start_at)}${end}`);
    }
  } else if (draft.kind === "task") {
    const due = draft.due_at ? formatDateTime(draft.due_at) : draft.due_date ? formatDate(draft.due_date) : "";
    if (due) parts.push(`${t("due")}: ${due}`);
  }
  if (draft.recurrence) {
    const weekdays = draft.recurrence === "weekly" && draft.weekdays?.length
      ? ` · ${draft.weekdays.map((day) => t(`weekday${day}`)).join(", ")}` : "";
    parts.push(`${t("recurrence")}: ${t(draft.monthly_on_last_day ? "monthlyLastDay" : draft.recurrence)}${weekdays}`);
  }
  if (draft.reminder_at) parts.push(`${t("reminder")}: ${formatDateTime(draft.reminder_at)}`);
  return parts.join(" · ");
}

function applyLanguage() {
  document.documentElement.lang = state.language === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-i18n]").forEach((node) => { node.textContent = t(node.dataset.i18n); });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => { node.placeholder = t(node.dataset.i18nPlaceholder); });
  document.querySelectorAll("[data-i18n-aria]").forEach((node) => { node.setAttribute("aria-label", t(node.dataset.i18nAria)); });
  $("#languageButton").textContent = state.language === "zh" ? "EN" : "中";
  $("#todayDate").textContent = formatDate(dateKey(), { weekday: "long", month: "long", day: "numeric" });
  renderAll();
  renderNotificationSettings();
}

function renderMembers() {
  const household = state.board.household || {};
  const householdName = $("#currentHouseholdName");
  const summary = $("#householdSummary");
  householdName.textContent = household.name || "";
  householdName.hidden = !household.name;
  summary.replaceChildren();
  if (household.invite_code) summary.append(textNode("p", `${t("invite")}: ${household.invite_code}`));
  const list = document.createElement("ul");
  state.board.members.forEach((member) => list.append(textNode("li", member.role ? `${member.name} · ${member.role}` : member.name)));
  summary.append(list);
  const currentMember = state.board.members.find((member) => member.id === state.board.current_member_id);
  $("#memberProfileForm").hidden = !currentMember;
  $("#profileSummary").textContent = currentMember
    ? [currentMember.name, currentMember.role].filter(Boolean).join(" · ") : "";
  $("#membersSummary").textContent = state.board.members.length ? String(state.board.members.length) : "";
  if (currentMember) {
    $("#memberName").value = currentMember.name || "";
    $("#memberRole").value = currentMember.role || "";
  }
}

function renderHouseholdControls() {
  const switcher = $("#householdSwitcher");
  const select = $("#householdSelect");
  switcher.hidden = state.households.length < 2;
  select.replaceChildren(...state.households.map((household) => new Option(household.name, household.id)));
  select.value = state.activeHouseholdId || "";
}

function textNode(tag, content, className = "") {
  const node = document.createElement(tag);
  node.className = className;
  node.textContent = content;
  return node;
}

function empty(container, key) {
  container.replaceChildren(textNode("p", t(key), "empty"));
}

function itemCard(item) {
  const card = document.createElement("button");
  card.type = "button";
  card.className = `item-card ${item.kind || "event"} ${item.completed_at ? "is-done" : ""}`;
  const top = document.createElement("span");
  top.className = "item-card-top";
  top.append(textNode("span", t(item.kind || "event"), `badge ${item.kind || "event"}`));
  const timing = itemTime(item);
  if (timing) top.append(textNode("span", timing, "item-time"));
  card.append(top, textNode("strong", item.title || ""));
  if (item.details) card.append(textNode("span", item.details, "item-details"));
  const reminded = reminderNames(item);
  if (reminded.length) card.append(textNode("span", `${t("remind")}: ${reminded.join(", ")}`, "remind-line"));
  card.addEventListener("click", () => openItem(item));
  return card;
}

function renderToday() {
  const list = $("#todayItems");
  list.replaceChildren();
  const seen = new Set();
  state.today.forEach((item) => {
    const key = item.id || `${item.kind}:${item.title}:${itemDate(item)}`;
    if (!seen.has(key)) list.append(itemCard(item));
    seen.add(key);
  });
  if (!list.children.length) empty(list, "emptyToday");
}

function filteredCalendarItems() {
  if (state.calendarFilter !== "mine") return state.calendar;
  return state.calendar.filter((item) => item.remind_member_ids?.includes(state.board.current_member_id));
}

function filteredTasks() {
  return state.board.items.filter((item) => item.kind === "task" && !item.completed_at
    && (state.taskFilter !== "mine" || item.remind_member_ids?.includes(state.board.current_member_id)));
}

function calendarSummary(items) {
  return ["event", "task"].map((kind) => {
    const count = items.filter((item) => item.kind === kind).length;
    return count ? `${count}${state.language === "zh" ? " 个" : " "}${t(kind)}${state.language === "en" && count !== 1 ? "s" : ""}` : "";
  }).filter(Boolean).join(state.language === "zh" ? "，" : ", ");
}

function renderCalendar() {
  const firstDay = state.language === "zh" ? 1 : 0;
  const [start] = calendarRange();
  const month = localDate(`${state.calendarMonth}-01`);
  const byDate = filteredCalendarItems().reduce((result, item) => {
    const key = itemDate(item);
    if (key) (result.get(key) || result.set(key, []).get(key)).push(item);
    return result;
  }, new Map());
  const locale = state.language === "zh" ? "zh-CN" : "en-CA";
  const weekdays = $("#calendarWeekdays");
  const grid = $("#calendarGrid");
  const startDate = localDate(start);

  $("#calendarMonthTitle").textContent = new Intl.DateTimeFormat(locale, {
    year: "numeric", month: "long",
  }).format(month);
  document.querySelectorAll("[data-calendar-filter]").forEach((button) => {
    const active = button.dataset.calendarFilter === state.calendarFilter;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  weekdays.replaceChildren();
  grid.replaceChildren();
  for (let index = 0; index < 7; index += 1) {
    const date = new Date(2026, 0, 4 + ((index + firstDay) % 7));
    weekdays.append(textNode("span", new Intl.DateTimeFormat(locale, { weekday: "short" }).format(date)));
  }
  for (let index = 0; index < 42; index += 1) {
    const date = new Date(startDate);
    date.setDate(startDate.getDate() + index);
    const key = dateKey(date);
    const items = byDate.get(key) || [];
    const button = document.createElement("button");
    button.type = "button";
    button.className = "calendar-day";
    button.classList.toggle("is-outside", date.getMonth() !== month.getMonth());
    button.classList.toggle("is-today", key === dateKey());
    button.classList.toggle("is-selected", key === state.selectedDate);
    if (items.length) button.classList.add(`has-density-${items.length === 1 ? "low" : items.length < 4 ? "medium" : "high"}`);
    button.setAttribute("aria-pressed", String(key === state.selectedDate));
    button.setAttribute("aria-label", `${formatDate(key)}${items.length ? `, ${calendarSummary(items)}` : ""}`);
    button.append(textNode("span", String(date.getDate()), "calendar-day-number"));
    if (items.length) {
      const markers = document.createElement("span");
      markers.className = "calendar-markers";
      items.slice(0, 3).forEach((item) => markers.append(textNode("span", "", `calendar-marker ${item.kind}`)));
      if (items.length > 3) markers.append(textNode("span", `+${items.length - 3}`, "calendar-more"));
      button.append(markers);
    }
    button.addEventListener("click", () => selectCalendarDate(key));
    grid.append(button);
  }

  const agenda = $("#calendarAgenda");
  agenda.hidden = !state.calendarAgendaOpen;
  if (!state.calendarAgendaOpen) return;

  const container = $("#calendarItems");
  container.replaceChildren();
  const selectedItems = byDate.get(state.selectedDate) || [];
  $("#agendaTitle").textContent = formatDate(state.selectedDate);
  const count = $("#agendaCount");
  count.hidden = !selectedItems.length;
  count.textContent = String(selectedItems.length);
  selectedItems.forEach((item) => container.append(itemCard(item)));
  if (!container.children.length) empty(container, "emptyCalendarDay");

}

function taskGroups() {
  const today = dateKey();
  const weekEnd = dateKey(new Date(localDate(today).setDate(localDate(today).getDate() + 6)));
  const groups = { overdue: [], upcoming: [], unscheduled: [], later: [] };
  filteredTasks().forEach((item) => {
    const due = itemDate(item);
    if (!due) groups.unscheduled.push(item);
    else if (due < today) groups.overdue.push(item);
    else if (due <= weekEnd) groups.upcoming.push(item);
    else groups.later.push(item);
  });
  [groups.overdue, groups.upcoming, groups.later].forEach((items) => items.sort((left, right) => itemDate(left).localeCompare(itemDate(right))));
  return groups;
}

function renderTaskGroup(section, container, items) {
  $(section).hidden = !items.length;
  const list = $(container);
  list.replaceChildren();
  items.forEach((item) => list.append(itemCard(item)));
}

function renderNotes() {
  document.querySelectorAll("[data-task-filter]").forEach((button) => {
    const active = button.dataset.taskFilter === state.taskFilter;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  const groups = taskGroups();
  renderTaskGroup("#overdueSection", "#overdueItems", groups.overdue);
  renderTaskGroup("#upcomingSection", "#upcomingItems", groups.upcoming);
  renderTaskGroup("#unscheduledSection", "#unscheduledItems", groups.unscheduled);
  const moreTasks = $("#moreTasks");
  moreTasks.hidden = !groups.later.length;
  $("#moreTasksCount").textContent = groups.later.length ? String(groups.later.length) : "";
  const later = $("#laterItems");
  later.replaceChildren();
  groups.later.forEach((item) => later.append(itemCard(item)));
  $("#emptyTasks").hidden = Boolean(groups.overdue.length || groups.upcoming.length || groups.unscheduled.length || groups.later.length);

  const container = $("#notesItems");
  container.replaceChildren();
  state.board.items.filter((item) => item.kind === "note").forEach((item) => container.append(itemCard(item)));
  if (!container.children.length) empty(container, "emptyNotes");
}

function renderMessages() {
  const panel = $("#conversation");
  panel.hidden = !state.messages.length && !state.pending;
  const list = $("#messageList");
  list.replaceChildren();
  state.messages.forEach((message) => list.append(textNode("p", message.text, `message ${message.role}`)));
  renderConfirmation();
  requestAnimationFrame(() => { list.scrollTop = list.scrollHeight; });
}

function renderConfirmation() {
  const box = $("#confirmation");
  box.hidden = !state.pending;
  if (!state.pending) return;
  if (state.pending.action) {
    $("#confirmationSummary").replaceChildren(textNode("p", state.pending.action.confirmation, "draft-summary"));
    $("#remindChoices").hidden = true;
    $("#preparationChoices").hidden = true;
    return;
  }
  $("#remindChoices").hidden = false;
  $("#preparationChoices").hidden = false;
  const drafts = state.pending.drafts || [];
  const summary = $("#confirmationSummary");
  summary.replaceChildren();
  drafts.forEach((draft) => {
    const row = document.createElement("div");
    row.append(textNode("p", `${t(draft.kind || "event")}: ${draft.title || draft.details || ""}`, "draft-summary"));
    const meta = draftMeta(draft);
    if (meta) row.append(textNode("p", meta, "draft-meta"));
    summary.append(row);
  });

  const reminders = $("#remindChoices");
  reminders.replaceChildren();
  drafts.forEach((draft, index) => {
    if (draft.kind === "note") return;
    const group = document.createElement("div");
    group.className = "reminder-choice-group";
    group.append(textNode("p", draft.title, "reminder-choice-title"));
    const selected = new Set(draft.remind_member_ids || []);
    state.board.members.forEach((member) => {
      const label = document.createElement("label");
      label.className = "checkbox-row";
      const input = document.createElement("input");
      input.type = "checkbox";
      input.value = member.id;
      input.dataset.draftIndex = index;
      input.checked = selected.has(member.id);
      label.append(input, document.createTextNode(member.name));
      group.append(label);
    });
    reminders.append(group);
  });

  const preparations = $("#preparationChoices");
  preparations.replaceChildren();
  drafts.forEach((draft, index) => {
    const content = draft.preparation;
    if (!content) return;
    const label = document.createElement("label");
    const input = document.createElement("input");
    input.type = "checkbox";
    input.dataset.draftIndex = index;
    input.checked = true;
    label.append(input, document.createTextNode(`${t("preparation")}: ${content}`));
    preparations.append(label);
  });
}

function renderAll() {
  renderMembers();
  renderToday();
  renderCalendar();
  renderNotes();
  renderMessages();
}

function consumeResponse(data) {
  if (data.session_id) {
    state.sessionId = data.session_id;
    localStorage.setItem("hearthbook-session", data.session_id);
  }
  const messages = Array.isArray(data.messages) ? data.messages : [];
  const latest = [...messages].reverse().find((message) => message.role === "assistant");
  if (latest?.content && state.messages.at(-1)?.text !== latest.content) {
    state.messages.push({ role: "assistant", text: latest.content });
  }
  state.pending = data.action ? { action: data.action } : data.status === "review" ? data : null;
  renderMessages();
}

function startNewConversation() {
  state.messages = [];
  state.pending = null;
  state.sessionId = null;
  localStorage.removeItem("hearthbook-session");
  renderMessages();
}

async function sendText(text) {
  if (!text.trim()) return;
  state.messages.push({ role: "user", text: text.trim() }, { role: "assistant", text: t("thinking"), pending: true });
  renderMessages();
  try {
    const data = await api("/api/messages", {
      method: "POST",
      body: JSON.stringify({ text: text.trim(), timezone, session_id: state.sessionId || null }),
    });
    state.messages = state.messages.filter((message) => !message.pending);
    consumeResponse(data);
    await refreshData();
  } catch (error) {
    state.messages = state.messages.filter((message) => !message.pending);
    showToast(error.message, true);
    renderMessages();
  }
}

async function sendImage(file, text) {
  state.messages.push({ role: "user", text: text.trim() || t("imageUploaded") }, { role: "assistant", text: t("thinking"), pending: true });
  renderMessages();
  const form = new FormData();
  form.append("file", file, file.name);
  form.append("text", text.trim());
  form.append("timezone", timezone);
  form.append("language", state.language);
  if (state.sessionId) form.append("session_id", state.sessionId);
  try {
    const data = await api("/api/image", { method: "POST", body: form });
    state.messages = state.messages.filter((message) => !message.pending);
    state.messages.at(-1).text = data.image_summary || state.messages.at(-1).text;
    consumeResponse(data);
    await refreshData();
  } catch (error) {
    state.messages = state.messages.filter((message) => !message.pending);
    showToast(error.message, true);
    renderMessages();
  }
}

async function loadBoard() {
  state.board = await api("/api/board");
  renderMembers();
  renderNotes();
  renderCalendar();
}

async function loadToday() {
  state.today = (await api(`/api/today?date=${dateKey()}&timezone=${encodeURIComponent(timezone)}`)).items;
  renderToday();
}

async function loadCalendar() {
  const [start, end] = calendarRange();
  state.calendar = (await api(`/api/calendar?start=${start}&end=${end}&timezone=${encodeURIComponent(timezone)}`)).items;
  renderCalendar();
}

function calendarRange() {
  const first = localDate(`${state.calendarMonth}-01`);
  const offset = (first.getDay() - (state.language === "zh" ? 1 : 0) + 7) % 7;
  const start = new Date(first);
  start.setDate(first.getDate() - offset);
  const end = new Date(start);
  end.setDate(start.getDate() + 41);
  return [dateKey(start), dateKey(end)];
}

function selectCalendarDate(key) {
  state.selectedDate = key;
  state.calendarAgendaOpen = true;
  if (key.slice(0, 7) !== state.calendarMonth) {
    state.calendarMonth = key.slice(0, 7);
    loadCalendar().catch((error) => showToast(error.message, true));
  } else renderCalendar();
}

function moveCalendar(direction) {
  const month = localDate(`${state.calendarMonth}-01`);
  month.setMonth(month.getMonth() + direction);
  state.calendarMonth = dateKey(month).slice(0, 7);
  state.selectedDate = `${state.calendarMonth}-01`;
  state.calendarAgendaOpen = false;
  loadCalendar().catch((error) => showToast(error.message, true));
}

function setCalendarFilter(value) {
  state.calendarFilter = value === "mine" ? "mine" : "all";
  localStorage.setItem("hearthbook-calendar-filter", state.calendarFilter);
  renderCalendar();
}

function setTaskFilter(value) {
  state.taskFilter = value === "mine" ? "mine" : "all";
  localStorage.setItem("hearthbook-task-filter", state.taskFilter);
  renderNotes();
}

async function refreshData() {
  await Promise.all([loadBoard(), loadToday(), loadCalendar()]);
}

function editorItem(scope) {
  if (scope === "occurrence" || !state.selectedItem?.series_id) return state.selectedItem;
  return state.board.items.find((item) => item.id === state.selectedItem.series_id) || state.selectedItem;
}

function itemWeekdays(item) {
  if (item.weekdays?.length) return item.weekdays;
  const value = item.start_date ? `${item.start_date}T12:00:00` : item.start_at;
  return value ? [["SU", "MO", "TU", "WE", "TH", "FR", "SA"][new Date(value).getDay()]] : [];
}

function toggleEditorFields() {
  const item = editorItem($("#editScope").value);
  if (!item) return;
  const allDay = item.kind === "event" && $("#editAllDay").checked;
  $("#editStartDateField").hidden = !allDay;
  $("#editStartAtField").hidden = allDay;
  $("#editEndAtField").hidden = allDay;
  $("#editStartDate").required = allDay;
  $("#editStartAt").required = item.kind === "event" && !allDay;
  const dueTimed = item.kind === "task" && $("#editDueTimed").checked;
  $("#editDueDateField").hidden = dueTimed;
  $("#editDueAtField").hidden = !dueTimed;
  const editingOccurrence = $("#editScope").value === "occurrence";
  $("#editRecurrenceField").hidden = editingOccurrence;
  $("#editWeekdaysField").hidden = editingOccurrence || $("#editRecurrence").value !== "weekly";
  $("#editRecurrenceUntilField").hidden = editingOccurrence || !$("#editRecurrence").value;
  $("#occurrenceEditHint").hidden = !editingOccurrence;
  $("#restoreOccurrence").hidden = !editingOccurrence;
}

function fillEditor(item, scope) {
  if (!item) return;
  $("#editTitle").value = item.title || "";
  $("#editDetails").value = item.details || "";
  $("#editPreparation").value = item.preparation || "";
  $("#editPreparationField").hidden = item.kind === "note";
  const reminderEditable = item.kind !== "note" && scope !== "occurrence";
  $("#editReminderSettings").hidden = !reminderEditable;
  $("#editReminderAtField").hidden = !reminderEditable;
  $("#editReminderAt").value = reminderEditable ? toLocalDateTime(item.reminder_at) : "";
  $("#editRemindMemberField").hidden = item.kind === "note" || scope === "occurrence";
  $("#editEventFields").hidden = item.kind !== "event";
  $("#editTaskFields").hidden = item.kind !== "task";
  $("#editScheduleSection").hidden = item.kind === "note";
  if (item.kind === "event") {
    $("#editAllDay").checked = Boolean(item.all_day);
    $("#editStartDate").value = item.start_date || "";
    $("#editStartAt").value = toLocalDateTime(item.start_at);
    $("#editEndAt").value = toLocalDateTime(item.end_at);
    $("#editRecurrence").value = item.monthly_on_last_day ? "monthly_last_day" : item.recurrence || "";
    const weekdays = item.recurrence === "weekly" ? itemWeekdays(item) : [];
    $("#editWeekdaysField").querySelectorAll("input").forEach((input) => { input.checked = weekdays.includes(input.value); });
    $("#editRecurrenceUntil").value = item.recurrence_until || "";
  } else if (item.kind === "task") {
    $("#editDueTimed").checked = Boolean(item.due_at);
    $("#editDueDate").value = item.due_date || "";
    $("#editDueAt").value = toLocalDateTime(item.due_at);
  }
  toggleEditorFields();
  updateEditReminderSummary();
}

function updateEditReminderSummary() {
  const names = [...$("#editRemindMembers").querySelectorAll("input:checked")]
    .map((input) => memberName(input.value)).filter(Boolean);
  $("#editRemindMemberSummary").textContent = names.join(", ") || "—";
  const when = $("#editReminderAt").value
    ? formatDateTime(new Date($("#editReminderAt").value).toISOString()) : "";
  $("#editReminderSummary").textContent = [when, names.join(", ")].filter(Boolean).join(" · ") || "—";
}

function setItemEditing(editing) {
  $("#itemOverview").hidden = editing;
  $("#itemForm").hidden = !editing;
  $("#editItemButton").hidden = editing;
  $("#followupsSection").hidden = editing || state.selectedItem?.kind === "note";
}

function openItem(item) {
  state.selectedItem = item;
  $("#itemKind").textContent = t(item.kind || "event");
  $("#itemKind").className = `badge ${item.kind || "event"}`;
  $("#itemTitle").textContent = item.title || "";
  const reminderChoices = $("#editRemindMembers");
  reminderChoices.replaceChildren();
  const selected = new Set(item.remind_member_ids || []);
  state.board.members.forEach((member) => {
    const label = document.createElement("label");
    label.className = "checkbox-row";
    const input = document.createElement("input");
    input.type = "checkbox";
    input.value = member.id;
    input.checked = selected.has(member.id);
    label.append(input, document.createTextNode(member.name));
    reminderChoices.append(label);
  });
  $("#editRemindMemberField").open = false;
  $("#editReminderSettings").open = false;
  $("#editScopeField").hidden = !item.is_occurrence;
  $("#editScope").value = item.is_occurrence ? "occurrence" : "series";
  $("#itemFormError").hidden = true;
  fillEditor(editorItem($("#editScope").value), $("#editScope").value);

  const meta = $("#itemMeta");
  meta.replaceChildren();
  const timing = itemTime(item);
  if (timing) meta.append(textNode("p", timing));
  if (item.reminder_at) meta.append(textNode("p", `${t("reminder")}: ${formatDateTime(item.reminder_at)}`));
  if (item.recurrence) {
    const weekdays = item.recurrence === "weekly" && itemWeekdays(item).length
      ? ` · ${itemWeekdays(item).map((day) => t(`weekday${day}`)).join(", ")}` : "";
    meta.append(textNode("p", `${t("recurrence")}: ${t(item.monthly_on_last_day ? "monthlyLastDay" : item.recurrence)}${weekdays}`));
  }
  if (item.completed_at) meta.append(textNode("p", t("done")));
  const toggleDone = $("#toggleDone");
  $("#itemViewActions").hidden = item.kind !== "task";
  toggleDone.hidden = item.kind !== "task";
  toggleDone.className = item.completed_at ? "secondary-button" : "primary-button";
  toggleDone.textContent = t(item.completed_at ? "markOpen" : "markDone");

  const reminded = reminderNames(item);
  const details = item.details?.trim();
  $("#itemDetails").hidden = !details;
  $("#itemDetails").textContent = details || "";
  $("#itemReminders").textContent = reminded.length ? `${t("remind")}: ${reminded.join(", ")}` : "";
  const preparation = item.preparation?.trim();
  $("#preparationSection").hidden = !preparation;
  $("#itemPreparation").textContent = preparation || "";
  $("#followupsSection").open = false;
  renderFollowups(item);
  setItemEditing(false);
  $("#itemDialog").showModal();
}

function renderFollowups(item) {
  const list = $("#followupList");
  list.replaceChildren();
  (item.notes || []).forEach((note) => {
    const content = note.content;
    const author = memberName(note.member_id);
    const row = document.createElement("article");
    row.append(textNode("p", content));
    if (author || note.created_at) row.append(textNode("small", [author, note.created_at ? formatDateTime(note.created_at) : ""].filter(Boolean).join(" · ")));
    list.append(row);
  });
  $("#followupsCount").textContent = item.notes?.length ? String(item.notes.length) : "";
  $("#followupsSection").hidden = item.kind === "note";
}

async function updateSelected(fields) {
  if (!state.selectedItem) return;
  await api(`/api/items/${state.selectedItem.id}`, {
    method: "PATCH", body: JSON.stringify(fields),
  });
  await refreshData();
}

function switchTab(name) {
  document.querySelectorAll(".view").forEach((view) => {
    const active = view.dataset.view === name;
    view.hidden = !active;
    view.classList.toggle("active", active);
  });
  document.querySelectorAll(".bottom-tab").forEach((tab) => {
    const active = tab.dataset.tab === name;
    tab.classList.toggle("active", active);
    active ? tab.setAttribute("aria-current", "page") : tab.removeAttribute("aria-current");
  });
  if (name === "calendar") loadCalendar().catch((error) => showToast(error.message, true));
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function loadSession() {
  try {
    const session = await api("/api/auth/session");
    if (!session.authenticated) return $("#authDialog").showModal();
    if (!session.household_ready) return $("#onboardingDialog").showModal();
    state.households = Array.isArray(session.households) ? session.households : [];
    state.activeHouseholdId = session.active_household_id || null;
    renderHouseholdControls();
    await refreshData();
    await syncNotifications();
  } catch (error) {
    showToast(error.message, true);
  }
}

$("#languageButton").addEventListener("click", () => {
  state.language = state.language === "zh" ? "en" : "zh";
  localStorage.setItem("hearthbook-language", state.language);
  applyLanguage();
  loadCalendar().catch((error) => showToast(error.message, true));
  if (state.notification.subscription) savePushSubscription(state.notification.subscription).catch(() => {});
});

$("#settingsButton").addEventListener("click", () => {
  renderNotificationSettings();
  document.querySelectorAll("#settingsDialog .settings-details").forEach((section) => { section.open = false; });
  $("#settingsDialog").showModal();
});
document.querySelectorAll("#settingsDialog .settings-details").forEach((section) => {
  section.addEventListener("toggle", () => {
    if (section.open) document.querySelectorAll("#settingsDialog .settings-details").forEach((other) => {
      if (other !== section) other.open = false;
    });
  });
});
$("#householdSelect").addEventListener("change", async (event) => {
  const householdId = event.target.value;
  if (!householdId || householdId === state.activeHouseholdId) return;
  try {
    await api("/api/households/select", { method: "POST", body: JSON.stringify({ household_id: householdId }) });
    state.activeHouseholdId = householdId;
    startNewConversation();
    await refreshData();
    renderHouseholdControls();
  } catch (error) {
    event.target.value = state.activeHouseholdId || "";
    showToast(error.message, true);
  }
});
$("#settingsCloseButton").addEventListener("click", () => $("#settingsDialog").close());
$("#memberProfileForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    state.board = await api("/api/members/me", {
      method: "PATCH",
      body: JSON.stringify({ name: $("#memberName").value, role: $("#memberRole").value }),
    });
    renderAll();
    showToast(t("saved"));
  } catch (error) { showToast(error.message, true); }
});
$("#notificationButton").addEventListener("click", async () => {
  try {
    if (state.notification.subscription) return await removePushSubscription();
    if (await Notification.requestPermission() !== "granted") return renderNotificationSettings();
    const subscription = await state.notification.registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: applicationServerKey(state.notification.publicKey),
    });
    await savePushSubscription(subscription);
    state.notification.subscription = subscription;
    renderNotificationSettings();
  } catch (error) { showToast(error.message, true); }
});
$("#textToggle").addEventListener("click", () => {
  const form = $("#messageForm");
  form.hidden = !form.hidden;
  $("#textToggle").setAttribute("aria-expanded", String(!form.hidden));
  if (!form.hidden) $("#messageInput").focus();
});
$("#messageForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = $("#messageInput");
  const value = input.value;
  if (value.length > MAX_MESSAGE_CHARS) return showToast(t("messageTooLong"), true);
  input.value = "";
  await sendText(value);
});
$("#imageInput").addEventListener("change", () => {
  const file = $("#imageInput").files[0];
  if (!file) return;
  if (!["image/png", "image/jpeg"].includes(file.type) || file.size > 3 * 1024 * 1024) {
    $("#imageInput").value = "";
    return showToast(t("imageOnly"), true);
  }
  $("#imageFileName").textContent = file.name;
  $("#imageForm").hidden = false;
  $("#imageText").focus();
});
$("#cancelImage").addEventListener("click", () => {
  $("#imageInput").value = "";
  $("#imageText").value = "";
  $("#imageForm").hidden = true;
});
$("#imageForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = $("#imageInput").files[0];
  if (!file) return;
  const text = $("#imageText").value;
  $("#imageText").value = "";
  $("#imageForm").hidden = true;
  $("#imageInput").value = "";
  await sendImage(file, text);
});
$("#clearConversation").addEventListener("click", () => {
  startNewConversation();
});
$("#refreshToday").addEventListener("click", () => loadToday().catch((error) => showToast(error.message, true)));
$("#previousMonth").addEventListener("click", () => moveCalendar(-1));
$("#nextMonth").addEventListener("click", () => moveCalendar(1));
$("#calendarTodayButton").addEventListener("click", () => {
  state.calendarMonth = dateKey().slice(0, 7);
  state.selectedDate = dateKey();
  state.calendarAgendaOpen = false;
  loadCalendar().catch((error) => showToast(error.message, true));
});
document.querySelectorAll("[data-calendar-filter]").forEach((button) => {
  button.addEventListener("click", () => setCalendarFilter(button.dataset.calendarFilter));
});
document.querySelectorAll("[data-task-filter]").forEach((button) => {
  button.addEventListener("click", () => setTaskFilter(button.dataset.taskFilter));
});
document.querySelectorAll(".bottom-tab").forEach((tab) => tab.addEventListener("click", () => {
  const hash = `#${tab.dataset.tab}`;
  if (location.hash === hash) switchTab(tab.dataset.tab);
  else location.hash = hash;
}));
window.addEventListener("hashchange", () => {
  const tab = location.hash.slice(1);
  if (["home", "calendar", "notes"].includes(tab)) switchTab(tab);
});

$("#confirmButton").addEventListener("click", async () => {
  if (!state.pending) return;
  if (state.pending.action) {
    try {
      await api(`/api/items/${state.pending.action.item_id}`, {
        method: "PATCH",
        body: JSON.stringify(state.pending.action.fields),
      });
      state.pending = null;
      await refreshData();
      renderMessages();
      showToast(t("confirmed"));
    } catch (error) { showToast(error.message, true); }
    return;
  }
  const drafts = state.pending.drafts || [];
  const remind_member_ids = drafts.map((_, index) => [
    ...$("#remindChoices").querySelectorAll(`[data-draft-index="${index}"]:checked`),
  ].map((input) => input.value));
  const accepted_preparations = drafts.map((_, index) => Boolean($("#preparationChoices").querySelector(`[data-draft-index="${index}"]`)?.checked));
  try {
    await api(`/api/conversations/${state.sessionId}/confirm`, {
      method: "POST", body: JSON.stringify({ remind_member_ids, accepted_preparations }),
    });
    startNewConversation();
    await refreshData();
    showToast(t("confirmed"));
  } catch (error) { showToast(error.message, true); }
});
$("#cancelConfirmation").addEventListener("click", () => { state.pending = null; renderMessages(); });

$("#editAllDay").addEventListener("change", toggleEditorFields);
$("#editDueTimed").addEventListener("change", toggleEditorFields);
$("#editRecurrence").addEventListener("change", () => {
  const inputs = [...$("#editWeekdaysField").querySelectorAll("input")];
  if ($("#editRecurrence").value === "weekly" && !inputs.some((input) => input.checked)) {
    const value = $("#editAllDay").checked ? `${$("#editStartDate").value}T12:00:00` : $("#editStartAt").value;
    const weekday = value && ["SU", "MO", "TU", "WE", "TH", "FR", "SA"][new Date(value).getDay()];
    inputs.forEach((input) => { input.checked = input.value === weekday; });
  }
  toggleEditorFields();
});
$("#editScope").addEventListener("change", (event) => fillEditor(editorItem(event.target.value), event.target.value));
$("#editRemindMembers").addEventListener("change", updateEditReminderSummary);
$("#editReminderAt").addEventListener("change", updateEditReminderSummary);
$("#editItemButton").addEventListener("click", () => {
  if (!state.selectedItem) return;
  const scope = state.selectedItem.is_occurrence ? $("#editScope").value : "series";
  fillEditor(editorItem(scope), scope);
  setItemEditing(true);
});
$("#itemForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const scope = state.selectedItem?.is_occurrence ? $("#editScope").value : "series";
  const item = editorItem(scope);
  if (!item) return;
  $("#itemFormError").hidden = true;
  try {
    const fields = { title: $("#editTitle").value.trim(), details: $("#editDetails").value.trim() };
    if (item.kind !== "note") fields.preparation = $("#editPreparation").value.trim() || null;
    if (item.kind !== "note" && scope === "series") {
      fields.remind_member_ids = [...$("#editRemindMembers").querySelectorAll("input:checked")]
        .map((input) => input.value);
      fields.reminder_at = $("#editReminderAt").value
        ? new Date($("#editReminderAt").value).toISOString() : null;
    }
    if (item.kind === "event") {
      if ($("#editAllDay").checked) {
        fields.start_date = $("#editStartDate").value;
        fields.start_at = null;
        fields.end_at = null;
      } else {
        fields.start_at = new Date($("#editStartAt").value).toISOString();
        fields.end_at = $("#editEndAt").value ? new Date($("#editEndAt").value).toISOString() : null;
        fields.start_date = null;
      }
      if (scope === "series") {
        const recurrence = $("#editRecurrence").value;
        fields.all_day = $("#editAllDay").checked;
        fields.recurrence = recurrence === "monthly_last_day" ? "monthly" : recurrence || null;
        fields.weekdays = recurrence === "weekly"
          ? [...$("#editWeekdaysField").querySelectorAll("input:checked")].map((input) => input.value) : [];
        fields.monthly_on_last_day = recurrence === "monthly_last_day";
        fields.recurrence_until = recurrence ? $("#editRecurrenceUntil").value || null : null;
      }
      fields.schedule_timezone = timezone;
    } else if (item.kind === "task") {
      fields.due_at = $("#editDueTimed").checked && $("#editDueAt").value
        ? new Date($("#editDueAt").value).toISOString() : null;
      fields.due_date = $("#editDueTimed").checked ? null : $("#editDueDate").value || null;
      fields.schedule_timezone = timezone;
    }
    const path = state.selectedItem.is_occurrence && scope === "occurrence"
      ? `/api/items/${state.selectedItem.series_id}/occurrences/${state.selectedItem.occurrence_date}`
      : `/api/items/${item.id}`;
    await api(path, { method: "PATCH", body: JSON.stringify(fields) });
    await refreshData();
    $("#itemDialog").close();
    showToast(t("saved"));
  } catch (error) {
    $("#itemFormError").textContent = error.message;
    $("#itemFormError").hidden = false;
  }
});
$("#restoreOccurrence").addEventListener("click", async () => {
  if (!state.selectedItem?.is_occurrence || !confirm(t("restoreOccurrenceConfirm"))) return;
  try {
    await api(`/api/items/${state.selectedItem.series_id}/occurrences/${state.selectedItem.occurrence_date}/override`, { method: "DELETE" });
    $("#itemDialog").close();
    await refreshData();
    showToast(t("occurrenceRestored"));
  } catch (error) { showToast(error.message, true); }
});
$("#deleteItem").addEventListener("click", async () => {
  if (!state.selectedItem) return;
  const occurrence = state.selectedItem.is_occurrence && $("#editScope").value === "occurrence";
  const confirmation = occurrence ? "cancelOccurrenceConfirm"
    : state.selectedItem.recurrence ? "deleteSeriesConfirm" : "deleteConfirm";
  if (!confirm(t(confirmation))) return;
  try {
    const path = occurrence
      ? `/api/items/${state.selectedItem.series_id}/occurrences/${state.selectedItem.occurrence_date}`
      : `/api/items/${state.selectedItem.id}`;
    await api(path, { method: "DELETE" });
    $("#itemDialog").close();
    await refreshData();
    showToast(t("deleted"));
  } catch (error) { showToast(error.message, true); }
});
$("#toggleDone").addEventListener("click", async () => {
  if (!state.selectedItem) return;
  try {
    await updateSelected({ completed: !state.selectedItem.completed_at });
    $("#itemDialog").close();
    showToast(t("saved"));
  } catch (error) { showToast(error.message, true); }
});
$("#followupForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.selectedItem) return;
  const input = $("#followupInput");
  try {
    await api(`/api/items/${state.selectedItem.id}/notes`, {
      method: "POST", body: JSON.stringify({ content: input.value.trim() }),
    });
    input.value = "";
    await refreshData();
    const fresh = state.board.items.find((item) => item.id === state.selectedItem.id) || state.selectedItem;
    state.selectedItem = fresh;
    renderFollowups(fresh);
    showToast(t("added"));
  } catch (error) { showToast(error.message, true); }
});

$("#recordButton").addEventListener("click", async () => {
  if (state.recorder?.state === "recording") return state.recorder.stop();
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const chunks = [];
    const recorder = new MediaRecorder(stream);
    state.recorder = recorder;
    state.recordingLimitReached = false;
    recorder.addEventListener("dataavailable", (event) => { if (event.data.size) chunks.push(event.data); });
    recorder.addEventListener("stop", async () => {
      clearTimeout(state.recordingTimer);
      stream.getTracks().forEach((track) => track.stop());
      $("#recordButton").classList.remove("recording");
      $("#recordButton").setAttribute("aria-pressed", "false");
      $("#recordButton span").textContent = t("tapToTalk");
      const audio = new Blob(chunks, { type: recorder.mimeType || "audio/webm" });
      if (!audio.size) return showToast(t("noSpeech"), true);
      if (audio.size > MAX_AUDIO_BYTES) return showToast(t("audioTooLarge"), true);
      if (state.recordingLimitReached) showToast(t("recordingLimit"), true);
      const form = new FormData();
      form.append("file", audio, "recording.webm");
      form.append("timezone", timezone);
      form.append("language", state.language);
      if (state.sessionId) form.append("session_id", state.sessionId);
      state.messages.push({ role: "assistant", text: t("thinking"), pending: true });
      renderMessages();
      try {
        const data = await api("/api/audio", { method: "POST", body: form });
        state.messages = state.messages.filter((message) => !message.pending);
        if (data.transcript) state.messages.push({ role: "user", text: data.transcript });
        consumeResponse(data);
        await refreshData();
      } catch (error) {
        state.messages = state.messages.filter((message) => !message.pending);
        showToast(error.message, true);
        renderMessages();
      }
    });
    recorder.start();
    $("#recordButton").classList.add("recording");
    $("#recordButton").setAttribute("aria-pressed", "true");
    $("#recordButton span").textContent = t("stopRecording");
    showToast(t("listening"));
    state.recordingTimer = setTimeout(() => {
      if (recorder.state !== "recording") return;
      state.recordingLimitReached = true;
      recorder.stop();
    }, MAX_RECORDING_MS);
  } catch (_) { showToast(t("microphoneError"), true); }
});

$("#authForm").addEventListener("submit", (event) => authenticate(event, "login"));
$("#signupButton").addEventListener("click", (event) => authenticate(event, "signup"));
async function authenticate(event, action) {
  event.preventDefault();
  const errorBox = $("#authError");
  errorBox.hidden = true;
  try {
    await api(`/api/auth/${action}`, { method: "POST", body: JSON.stringify({ email: $("#authEmail").value, password: $("#authPassword").value }) });
    $("#authDialog").close();
    await loadSession();
  } catch (error) { errorBox.textContent = error.message; errorBox.hidden = false; }
}

$("#createHouseholdForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await api("/api/households", { method: "POST", body: JSON.stringify({ household_name: $("#newHouseholdName").value, member_name: $("#creatorName").value, member_role: $("#creatorRole").value }) });
    $("#onboardingDialog").close();
    await refreshData();
  } catch (error) { $("#onboardingError").textContent = error.message; $("#onboardingError").hidden = false; }
});
$("#createAdditionalHouseholdForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await api("/api/households", { method: "POST", body: JSON.stringify({ household_name: $("#additionalHouseholdName").value, member_name: $("#additionalCreatorName").value, member_role: $("#additionalCreatorRole").value }) });
    event.target.reset();
    startNewConversation();
    await loadSession();
  } catch (error) { showToast(error.message, true); }
});
$("#joinAdditionalHouseholdForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await api("/api/households/join", { method: "POST", body: JSON.stringify({ invite_code: $("#additionalInviteCode").value, member_name: $("#additionalJoinerName").value, member_role: $("#additionalJoinerRole").value }) });
    event.target.reset();
    startNewConversation();
    await loadSession();
  } catch (error) { showToast(error.message, true); }
});
$("#joinHouseholdForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await api("/api/households/join", { method: "POST", body: JSON.stringify({ invite_code: $("#inviteCode").value, member_name: $("#joinerName").value, member_role: $("#joinerRole").value }) });
    $("#onboardingDialog").close();
    await refreshData();
  } catch (error) { $("#onboardingError").textContent = error.message; $("#onboardingError").hidden = false; }
});
$("#leaveHouseholdButton").addEventListener("click", async () => {
  if (!window.confirm(t("leaveHouseholdConfirm"))) return;
  try {
    await api("/api/households/leave", { method: "POST" });
    startNewConversation();
    $("#settingsDialog").close();
    await loadSession();
  } catch (error) { showToast(error.message, true); }
});
$("#logoutButton").addEventListener("click", async () => {
  await removePushSubscription().catch(() => {});
  await api("/api/auth/session", { method: "DELETE" });
  location.reload();
});

applyLanguage();
switchTab(["home", "calendar", "notes"].includes(location.hash.slice(1)) ? location.hash.slice(1) : "home");
loadSession();
