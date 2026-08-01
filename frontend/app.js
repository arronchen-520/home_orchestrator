"use strict";

const copy = {
  zh: {
    currentMember: "当前家庭成员", settings: "设置", homeTitle: "今天有什么想记录的吗？",
    homeSubtitle: "记录、查询，或者聊聊。", voiceTitle: "家庭助手",
    tapToTalk: "按住说话", stopRecording: "说完松开", preferTyping: "想打字？",
    messageLabel: "输入记录、问题或消息", messagePlaceholder: "例如：周六三点看牙，提醒妈妈",
    send: "发送", conversation: "对话", clear: "清空", remindWho: "提醒谁",
    preparation: "准备事项", cancel: "取消", confirm: "确认", todayEyebrow: "今日摘要",
    todayTitle: "今天", refresh: "刷新", plans: "安排", calendar: "日历", chooseMonth: "选择月份",
    unscheduled: "未定时间", familyMemory: "常用信息", notes: "笔记",
    notesHelp: "家里常用的信息，放在这里。", home: "首页",
    close: "关闭", title: "标题", details: "详情", delete: "删除", save: "保存",
    followups: "补充记录", addFollowup: "添加补充记录", followupPlaceholder: "补充最新情况…",
    add: "添加", logout: "退出登录", authTitle: "登录 Hearthbook", email: "邮箱",
    password: "密码", login: "登录", signup: "创建账号", householdSetup: "设置家庭",
    householdName: "家庭名称", yourName: "你的名字", createHousehold: "创建家庭",
    orJoin: "或者加入已有家庭", inviteCode: "家庭邀请码", joinHousehold: "加入家庭",
    event: "日程", task: "待办", note: "笔记", allDay: "全天", due: "截止",
    starts: "开始", reminder: "提醒", remind: "提醒", done: "已完成", markDone: "标记完成", markOpen: "恢复待办",
    emptyToday: "今天没有安排或提醒。", emptyCalendar: "这个月还没有安排。",
    emptyUnscheduled: "还没有定时间的待办。", emptyNotes: "还没有记录。",
    emptyConversation: "还没有对话。", listening: "正在听…", thinking: "正在处理…",
    saved: "已保存", deleted: "已删除", added: "已添加", confirmed: "已确认",
    deleteConfirm: "确定删除这条内容吗？", chooseMember: "请先选择你是谁。",
    microphoneError: "无法使用麦克风，可以改用文字输入。", networkError: "暂时连接不上，过一会儿再试。",
    noSpeech: "没有听到声音，再试一次。", familyMembers: "家庭成员", invite: "邀请码",
    recurrence: "重复", daily: "每天", weekly: "每周", monthly: "每月", overdue: "已过期",
  },
  en: {
    currentMember: "Current family member", settings: "Settings", homeTitle: "Anything you'd like to note today?",
    homeSubtitle: "Add a note, ask a question, or just chat.", voiceTitle: "Family assistant",
    tapToTalk: "Hold to talk", stopRecording: "Release when you're done", preferTyping: "Prefer to type?",
    messageLabel: "Type a plan, question, or message", messagePlaceholder: "Example: Dentist Saturday at 3, remind Mom",
    send: "Send", conversation: "Conversation", clear: "Clear", remindWho: "Who should we remind?",
    preparation: "Preparation", cancel: "Cancel", confirm: "Confirm", todayEyebrow: "Today's summary",
    todayTitle: "Today", refresh: "Refresh", plans: "Plans", calendar: "Calendar", chooseMonth: "Choose month",
    unscheduled: "No date yet", familyMemory: "Household info", notes: "Notes",
    notesHelp: "Keep household details here.", home: "Home",
    close: "Close", title: "Title", details: "Details", delete: "Delete", save: "Save",
    followups: "Notes", addFollowup: "Add a note", followupPlaceholder: "Add a note…",
    add: "Add", logout: "Log out", authTitle: "Sign in to Hearthbook", email: "Email",
    password: "Password", login: "Sign in", signup: "Create account", householdSetup: "Set up your household",
    householdName: "Household name", yourName: "Your name", createHousehold: "Create household",
    orJoin: "Or join an existing household", inviteCode: "Household invite code", joinHousehold: "Join household",
    event: "Event", task: "Task", note: "Note", allDay: "All day", due: "Due",
    starts: "Starts", reminder: "Reminder", remind: "Reminder", done: "Done", markDone: "Mark done", markOpen: "Mark open",
    emptyToday: "Nothing planned or due today.", emptyCalendar: "Nothing planned this month.",
    emptyUnscheduled: "No tasks without a date.", emptyNotes: "No notes yet.",
    emptyConversation: "No messages yet.", listening: "Listening…", thinking: "Working…",
    saved: "Saved", deleted: "Deleted", added: "Added", confirmed: "Confirmed",
    deleteConfirm: "Delete this item?", chooseMember: "Choose who you are first.",
    microphoneError: "The microphone isn't available. You can type instead.", networkError: "Can't connect right now. Try again in a moment.",
    noSpeech: "I didn't hear anything. Try again.", familyMembers: "Family members", invite: "Invite code",
    recurrence: "Repeats", daily: "Daily", weekly: "Weekly", monthly: "Monthly", overdue: "Overdue",
  },
};

const $ = (selector) => document.querySelector(selector);
const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
const state = {
  language: localStorage.getItem("hearthbook-language") || (navigator.language.startsWith("zh") ? "zh" : "en"),
  board: { household: {}, members: [], items: [] },
  today: [], calendar: [], messages: [], pending: null, selectedItem: null,
  sessionId: localStorage.getItem("hearthbook-session") || null,
  recorder: null, recordingTimer: null,
};

function t(key) { return copy[state.language][key] || key; }

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: options.body instanceof FormData ? options.headers : { "Content-Type": "application/json", ...options.headers },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const safeDetail = response.status < 500 && typeof data.detail === "string" ? data.detail : "";
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
  return item.remind_member_id ? [memberName(item.remind_member_id)].filter(Boolean) : [];
}

function applyLanguage() {
  document.documentElement.lang = state.language === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-i18n]").forEach((node) => { node.textContent = t(node.dataset.i18n); });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => { node.placeholder = t(node.dataset.i18nPlaceholder); });
  document.querySelectorAll("[data-i18n-aria]").forEach((node) => { node.setAttribute("aria-label", t(node.dataset.i18nAria)); });
  $("#languageButton").textContent = state.language === "zh" ? "EN" : "中";
  $("#todayDate").textContent = formatDate(dateKey(), { weekday: "long", month: "long", day: "numeric" });
  renderAll();
}

function selectedActor() { return $("#actorSelect").value; }

function requireActor() {
  if (selectedActor()) return true;
  showToast(t("chooseMember"), true);
  return false;
}

function renderMembers() {
  const select = $("#actorSelect");
  const saved = localStorage.getItem("hearthbook-actor");
  select.replaceChildren(...state.board.members.map((member) => new Option(member.name, member.id)));
  if (state.board.members.some((member) => member.id === saved)) select.value = saved;
  if (!select.value && state.board.members[0]) select.value = state.board.members[0].id;
  if (select.value) localStorage.setItem("hearthbook-actor", select.value);

  const household = state.board.household || {};
  const summary = $("#householdSummary");
  summary.replaceChildren();
  if (household.name) summary.append(textNode("h3", household.name));
  if (household.invite_code) summary.append(textNode("p", `${t("invite")}: ${household.invite_code}`));
  summary.append(textNode("h3", t("familyMembers")));
  const list = document.createElement("ul");
  state.board.members.forEach((member) => list.append(textNode("li", member.role ? `${member.name} · ${member.role}` : member.name)));
  summary.append(list);
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

function renderCalendar() {
  const container = $("#calendarItems");
  container.replaceChildren();
  const groups = state.calendar.filter((item) => itemDate(item)).reduce((result, item) => {
    const key = itemDate(item);
    if (!result.has(key)) result.set(key, []);
    result.get(key).push(item);
    return result;
  }, new Map());
  [...groups.entries()].sort(([a], [b]) => a.localeCompare(b)).forEach(([key, items]) => {
    const section = document.createElement("section");
    section.className = "date-group";
    section.append(textNode("h2", formatDate(key)));
    const list = document.createElement("div");
    list.className = "item-list";
    items.forEach((item) => list.append(itemCard(item)));
    section.append(list);
    container.append(section);
  });
  if (!container.children.length) empty(container, "emptyCalendar");

  const unscheduled = $("#unscheduledItems");
  unscheduled.replaceChildren();
  state.board.items.filter((item) => item.kind === "task" && !itemDate(item) && !item.completed_at)
    .forEach((item) => unscheduled.append(itemCard(item)));
  if (!unscheduled.children.length) empty(unscheduled, "emptyUnscheduled");
}

function renderNotes() {
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
  drafts.forEach((draft) => summary.append(textNode("p", `${t(draft.kind || "event")}: ${draft.title || draft.details || ""}`, "draft-summary")));

  const reminders = $("#remindChoices");
  reminders.querySelectorAll("label").forEach((label) => label.remove());
  drafts.forEach((draft, index) => {
    const label = document.createElement("label");
    const select = document.createElement("select");
    select.dataset.draftIndex = index;
    select.append(new Option("—", ""));
    state.board.members.forEach((member) => select.append(new Option(member.name, member.id)));
    select.value = draft.remind_member_id || "";
    label.append(document.createTextNode(`${draft.title}: `), select);
    reminders.append(label);
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

async function sendText(text) {
  if (!text.trim() || !requireActor()) return;
  state.messages.push({ role: "user", text: text.trim() }, { role: "assistant", text: t("thinking"), pending: true });
  renderMessages();
  try {
    const data = await api("/api/messages", {
      method: "POST",
      body: JSON.stringify({ text: text.trim(), actor_id: selectedActor(), timezone, session_id: state.sessionId || null }),
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
  const month = $("#calendarMonth").value || dateKey().slice(0, 7);
  const [year, monthNumber] = month.split("-").map(Number);
  const start = `${month}-01`;
  const end = dateKey(new Date(year, monthNumber, 0));
  state.calendar = (await api(`/api/calendar?start=${start}&end=${end}`)).items;
  renderCalendar();
}

async function refreshData() {
  await Promise.all([loadBoard(), loadToday(), loadCalendar()]);
}

function openItem(item) {
  state.selectedItem = item;
  $("#itemKind").textContent = t(item.kind || "event");
  $("#itemKind").className = `badge ${item.kind || "event"}`;
  $("#itemTitle").textContent = item.title || "";
  $("#editTitle").value = item.title || "";
  $("#editDetails").value = item.details || "";
  $("#editRemindMemberField").hidden = item.kind === "note";
  const remindSelect = $("#editRemindMember");
  remindSelect.replaceChildren(new Option("—", ""), ...state.board.members.map((member) => new Option(member.name, member.id)));
  remindSelect.value = item.remind_member_id || "";

  const meta = $("#itemMeta");
  meta.replaceChildren();
  const timing = itemTime(item);
  if (timing) meta.append(textNode("p", timing));
  if (item.reminder_at) meta.append(textNode("p", `${t("reminder")}: ${formatDateTime(item.reminder_at)}`));
  if (item.recurrence) meta.append(textNode("p", `${t("recurrence")}: ${t(item.recurrence)}`));
  if (item.completed_at) meta.append(textNode("p", t("done")));
  $("#toggleDone").hidden = item.kind !== "task";
  $("#toggleDone").textContent = t(item.completed_at ? "markOpen" : "markDone");

  const reminded = reminderNames(item);
  $("#itemReminders").textContent = reminded.length ? `${t("remind")}: ${reminded.join(", ")}` : "";
  renderFollowups(item);
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
  $("#followupsSection").hidden = item.kind === "note";
}

async function updateSelected(fields) {
  if (!state.selectedItem || !requireActor()) return;
  await api(`/api/items/${state.selectedItem.id}`, {
    method: "PATCH", body: JSON.stringify({ actor_id: selectedActor(), ...fields }),
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
    await refreshData();
  } catch (error) {
    showToast(error.message, true);
  }
}

$("#languageButton").addEventListener("click", () => {
  state.language = state.language === "zh" ? "en" : "zh";
  localStorage.setItem("hearthbook-language", state.language);
  applyLanguage();
});

$("#actorSelect").addEventListener("change", (event) => localStorage.setItem("hearthbook-actor", event.target.value));
$("#settingsButton").addEventListener("click", () => $("#settingsDialog").showModal());
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
  input.value = "";
  await sendText(value);
});
$("#clearConversation").addEventListener("click", () => {
  state.messages = [];
  state.pending = null;
  state.sessionId = null;
  localStorage.removeItem("hearthbook-session");
  renderMessages();
});
$("#refreshToday").addEventListener("click", () => loadToday().catch((error) => showToast(error.message, true)));
$("#calendarMonth").addEventListener("change", () => loadCalendar().catch((error) => showToast(error.message, true)));
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
  if (!state.pending || !requireActor()) return;
  if (state.pending.action) {
    try {
      await api(`/api/items/${state.pending.action.item_id}`, {
        method: "PATCH",
        body: JSON.stringify({ actor_id: selectedActor(), ...state.pending.action.fields }),
      });
      state.pending = null;
      await refreshData();
      renderMessages();
      showToast(t("confirmed"));
    } catch (error) { showToast(error.message, true); }
    return;
  }
  const drafts = state.pending.drafts || [];
  const remind_member_ids = drafts.map((_, index) => $("#remindChoices").querySelector(`[data-draft-index="${index}"]`)?.value || null);
  const accepted_preparations = drafts.map((_, index) => Boolean($("#preparationChoices").querySelector(`[data-draft-index="${index}"]`)?.checked));
  try {
    const data = await api(`/api/conversations/${state.sessionId}/confirm`, {
      method: "POST", body: JSON.stringify({ actor_id: selectedActor(), remind_member_ids, accepted_preparations }),
    });
    state.pending = null;
    consumeResponse(data);
    await refreshData();
    showToast(t("confirmed"));
  } catch (error) { showToast(error.message, true); }
});
$("#cancelConfirmation").addEventListener("click", () => { state.pending = null; renderMessages(); });

$("#itemForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const fields = { title: $("#editTitle").value.trim(), details: $("#editDetails").value.trim() };
    if (state.selectedItem.kind !== "note") fields.remind_member_id = $("#editRemindMember").value || null;
    await updateSelected(fields);
    $("#itemDialog").close();
    showToast(t("saved"));
  } catch (error) { showToast(error.message, true); }
});
$("#deleteItem").addEventListener("click", async () => {
  if (!state.selectedItem || !requireActor() || !confirm(t("deleteConfirm"))) return;
  try {
    await api(`/api/items/${state.selectedItem.id}?actor_id=${encodeURIComponent(selectedActor())}`, { method: "DELETE" });
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
  if (!state.selectedItem || !requireActor()) return;
  const input = $("#followupInput");
  try {
    await api(`/api/items/${state.selectedItem.id}/notes`, {
      method: "POST", body: JSON.stringify({ actor_id: selectedActor(), content: input.value.trim() }),
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
  if (!requireActor()) return;
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const chunks = [];
    const recorder = new MediaRecorder(stream);
    state.recorder = recorder;
    recorder.addEventListener("dataavailable", (event) => { if (event.data.size) chunks.push(event.data); });
    recorder.addEventListener("stop", async () => {
      clearTimeout(state.recordingTimer);
      stream.getTracks().forEach((track) => track.stop());
      $("#recordButton").classList.remove("recording");
      $("#recordButton").setAttribute("aria-pressed", "false");
      $("#recordButton span").textContent = t("tapToTalk");
      const audio = new Blob(chunks, { type: recorder.mimeType || "audio/webm" });
      if (!audio.size) return showToast(t("noSpeech"), true);
      const form = new FormData();
      form.append("file", audio, "recording.webm");
      form.append("actor_id", selectedActor());
      form.append("timezone", timezone);
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
    state.recordingTimer = setTimeout(() => recorder.state === "recording" && recorder.stop(), 60000);
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
    await api("/api/households", { method: "POST", body: JSON.stringify({ household_name: $("#newHouseholdName").value, member_name: $("#creatorName").value }) });
    $("#onboardingDialog").close();
    await refreshData();
  } catch (error) { $("#onboardingError").textContent = error.message; $("#onboardingError").hidden = false; }
});
$("#joinHouseholdForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await api("/api/households/join", { method: "POST", body: JSON.stringify({ invite_code: $("#inviteCode").value, member_name: $("#joinerName").value }) });
    $("#onboardingDialog").close();
    await refreshData();
  } catch (error) { $("#onboardingError").textContent = error.message; $("#onboardingError").hidden = false; }
});
$("#logoutButton").addEventListener("click", async () => {
  await api("/api/auth/session", { method: "DELETE" });
  location.reload();
});

$("#calendarMonth").value = dateKey().slice(0, 7);
applyLanguage();
switchTab(["home", "calendar", "notes"].includes(location.hash.slice(1)) ? location.hash.slice(1) : "home");
loadSession();
