const messages = {
  zh: {
    iAm: "我是",
    currentMember: "当前家庭成员",
    switchLanguage: "切换语言",
    boardViews: "共享板视图",
    family: "家庭成员",
    eyebrow: "家庭共享板",
    heading: "说出来，家里就安排好了。",
    subheading: "AI 会把中文或英文整理成日程、待办或笔记。",
    inputLabel: "要添加什么？",
    inputPlaceholder: "例如：周六下午三点带孩子看牙医",
    optionalOwner: "负责人（可选）",
    unassigned: "未分配",
    record: "语音",
    stop: "停止",
    add: "添加",
    board: "共享板",
    calendar: "日历",
    notes: "笔记",
    unclaimed: "未认领",
    claimed: "已认领",
    done: "完成",
    familyMembers: "家庭成员",
    memberHelp: "先添加家庭成员。每个人使用前在右上角选择自己。",
    memberName: "成员姓名",
    addMember: "添加成员",
    previousMonth: "上个月",
    nextMonth: "下个月",
    close: "关闭",
    event: "日程",
    task: "待办",
    note: "笔记",
    owner: "负责人",
    status: "状态",
    createdBy: "添加人",
    due: "截止",
    starts: "时间",
    allDay: "全天",
    delete: "删除",
    confirmDelete: "确定删除这项内容吗？",
    empty: "这里还没有内容",
    chooseMember: "请先添加并选择一位家庭成员",
    added: "已添加",
    updated: "已更新",
    deleted: "已删除",
    recording: "正在录音，再按一次停止",
    processing: "AI 正在整理…",
    microphoneError: "无法使用麦克风",
    networkError: "操作失败，请检查服务和 API 配置",
    openrouterMissing: "请在 .env 配置 OPENROUTER_API_KEY",
    groqMissing: "请在 .env 配置 GROQ_API_KEY",
    noSpeech: "没有识别到语音",
    today: "今天",
  },
  en: {
    iAm: "I am",
    currentMember: "Current family member",
    switchLanguage: "Switch language",
    boardViews: "Board views",
    family: "Family",
    eyebrow: "Shared family board",
    heading: "Say it. The household is organized.",
    subheading: "AI turns Chinese or English into an event, task, or note.",
    inputLabel: "What would you like to add?",
    inputPlaceholder: "For example: Dentist for the kids Saturday at 3 PM",
    optionalOwner: "Owner (optional)",
    unassigned: "Unassigned",
    record: "Voice",
    stop: "Stop",
    add: "Add",
    board: "Board",
    calendar: "Calendar",
    notes: "Notes",
    unclaimed: "Unclaimed",
    claimed: "Claimed",
    done: "Done",
    familyMembers: "Family members",
    memberHelp: "Add family members first. Each person selects themselves before use.",
    memberName: "Member name",
    addMember: "Add member",
    previousMonth: "Previous month",
    nextMonth: "Next month",
    close: "Close",
    event: "Event",
    task: "Task",
    note: "Note",
    owner: "Owner",
    status: "Status",
    createdBy: "Added by",
    due: "Due",
    starts: "Time",
    allDay: "All day",
    delete: "Delete",
    confirmDelete: "Delete this item?",
    empty: "Nothing here yet",
    chooseMember: "Add and choose a family member first",
    added: "Added",
    updated: "Updated",
    deleted: "Deleted",
    recording: "Recording — press again to stop",
    processing: "AI is organizing it…",
    microphoneError: "Microphone is unavailable",
    networkError: "Action failed. Check the service and API configuration.",
    openrouterMissing: "Configure OPENROUTER_API_KEY in .env",
    groqMissing: "Configure GROQ_API_KEY in .env",
    noSpeech: "No speech was detected",
    today: "Today",
  },
};

const state = {
  board: { members: [], items: [] },
  language: localStorage.getItem("home-language")
    || (navigator.language.toLowerCase().startsWith("zh") ? "zh" : "en"),
  month: new Date(new Date().getFullYear(), new Date().getMonth(), 1),
  selectedDate: dateKey(new Date()),
  recorder: null,
  recordingTimer: null,
};

const $ = (selector) => document.querySelector(selector);
const actorSelect = $("#actorSelect");
const ownerSelect = $("#newOwnerSelect");
const membersDialog = $("#membersDialog");
const recordButton = $("#recordButton");

function t(key) {
  return messages[state.language][key] || key;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: options.body instanceof FormData
      ? options.headers
      : { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data.detail || "";
    if (detail.includes("OPENROUTER_API_KEY")) throw new Error(t("openrouterMissing"));
    if (detail.includes("GROQ_API_KEY")) throw new Error(t("groqMissing"));
    throw new Error(detail || t("networkError"));
  }
  return data;
}

function showToast(text, error = false) {
  const toast = $("#toast");
  toast.textContent = text;
  toast.classList.toggle("error", error);
  toast.hidden = false;
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => { toast.hidden = true; }, 3500);
}

function applyLanguage() {
  document.documentElement.lang = state.language === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    element.placeholder = t(element.dataset.i18nPlaceholder);
  });
  document.querySelectorAll("[data-i18n-aria]").forEach((element) => {
    element.setAttribute("aria-label", t(element.dataset.i18nAria));
  });
  $("#languageButton").textContent = state.language === "zh" ? "EN" : "中";
  render();
}

function selectedActor() {
  return actorSelect.value || "";
}

function requireActor() {
  if (selectedActor()) return true;
  showToast(t("chooseMember"), true);
  membersDialog.showModal();
  return false;
}

function fillMemberSelect(select, includeUnassigned, selectedValue = "") {
  select.replaceChildren();
  if (includeUnassigned) {
    select.add(new Option(t("unassigned"), ""));
  }
  state.board.members.forEach((member) => {
    select.add(new Option(member.name, member.id));
  });
  if ([...select.options].some((option) => option.value === selectedValue)) {
    select.value = selectedValue;
  }
}

function renderMembers() {
  const savedActor = localStorage.getItem("home-actor") || selectedActor();
  fillMemberSelect(actorSelect, false, savedActor);
  if (!actorSelect.value && state.board.members.length) {
    actorSelect.value = state.board.members[0].id;
    localStorage.setItem("home-actor", actorSelect.value);
  }
  fillMemberSelect(ownerSelect, true, ownerSelect.value);

  const list = $("#memberList");
  list.replaceChildren();
  state.board.members.forEach((member) => {
    const item = document.createElement("li");
    item.textContent = member.name;
    list.append(item);
  });
}

function memberName(id) {
  return state.board.members.find((member) => member.id === id)?.name || t("unassigned");
}

function formatDateTime(value, allDay = false) {
  if (!value) return "";
  const date = new Date(value);
  return new Intl.DateTimeFormat(state.language === "zh" ? "zh-CN" : "en-CA", {
    dateStyle: "medium",
    ...(allDay ? {} : { timeStyle: "short" }),
  }).format(date);
}

function createText(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  element.textContent = text;
  return element;
}

function itemCard(item, compact = false) {
  const card = document.createElement("article");
  card.className = `item-card ${item.status === "done" ? "done-card" : ""} ${item.kind === "note" ? "note-card" : ""}`;

  const top = document.createElement("div");
  top.className = "item-topline";
  const badge = createText("span", `badge ${item.kind}`, t(item.kind));
  const remove = createText("button", "delete-button", t("delete"));
  remove.type = "button";
  remove.addEventListener("click", () => removeItem(item.id));
  top.append(badge, remove);
  card.append(top, createText("h3", "", item.title));

  if (item.details) card.append(createText("p", "", item.details));

  const meta = document.createElement("div");
  meta.className = "item-meta";
  if (item.kind === "event") {
    meta.append(createText(
      "p",
      "",
      `${t("starts")}: ${formatDateTime(item.start_at, item.all_day)}${item.all_day ? ` · ${t("allDay")}` : ""}`,
    ));
  } else if (item.kind === "task" && item.due_at) {
    meta.append(createText("p", "", `${t("due")}: ${formatDateTime(item.due_at)}`));
  }
  meta.append(createText("p", "", `${t("createdBy")}: ${memberName(item.created_by)}`));
  card.append(meta);

  if (!compact && item.kind !== "note") {
    const controls = document.createElement("div");
    controls.className = "item-controls";

    const ownerLabel = createText("label", "", t("owner"));
    const itemOwner = document.createElement("select");
    fillMemberSelect(itemOwner, true, item.owner_id || "");
    itemOwner.addEventListener("change", () => {
      updateItem(item.id, { owner_id: itemOwner.value || null });
    });
    ownerLabel.append(itemOwner);

    const statusLabel = createText("label", "", t("status"));
    const statusSelect = document.createElement("select");
    ["unclaimed", "claimed", "done"].forEach((status) => {
      statusSelect.add(new Option(t(status), status));
    });
    statusSelect.value = item.status;
    statusSelect.addEventListener("change", () => {
      updateItem(item.id, { status: statusSelect.value });
    });
    statusLabel.append(statusSelect);
    controls.append(ownerLabel, statusLabel);
    card.append(controls);
  } else if (compact && item.kind !== "note") {
    card.append(createText("p", "", `${t("owner")}: ${memberName(item.owner_id)}`));
  }
  return card;
}

function appendEmpty(container) {
  container.append(createText("p", "empty", t("empty")));
}

function renderBoard() {
  ["unclaimed", "claimed", "done"].forEach((status) => {
    const items = state.board.items.filter(
      (item) => item.kind !== "note" && item.status === status,
    );
    const container = $(`#${status}Items`);
    container.replaceChildren();
    items.forEach((item) => container.append(itemCard(item)));
    if (!items.length) appendEmpty(container);
    $(`#${status}Count`).textContent = items.length;
  });
}

function dateKey(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function itemDate(item) {
  const value = item.kind === "event" ? item.start_at : item.kind === "task" ? item.due_at : null;
  return value ? dateKey(new Date(value)) : null;
}

function renderCalendar() {
  const locale = state.language === "zh" ? "zh-CN" : "en-CA";
  $("#monthTitle").textContent = new Intl.DateTimeFormat(locale, {
    month: "long",
    year: "numeric",
  }).format(state.month);

  const grid = $("#calendarGrid");
  grid.replaceChildren();
  const weekBase = new Date(2026, 0, 4);
  for (let day = 0; day < 7; day += 1) {
    const date = new Date(weekBase);
    date.setDate(weekBase.getDate() + day);
    grid.append(createText(
      "div",
      "weekday",
      new Intl.DateTimeFormat(locale, { weekday: "short" }).format(date),
    ));
  }

  const first = new Date(state.month.getFullYear(), state.month.getMonth(), 1);
  const start = new Date(first);
  start.setDate(1 - first.getDay());
  const today = dateKey(new Date());

  for (let index = 0; index < 42; index += 1) {
    const date = new Date(start);
    date.setDate(start.getDate() + index);
    const key = dateKey(date);
    const button = createText("button", "day", date.getDate());
    button.type = "button";
    button.classList.toggle("outside", date.getMonth() !== state.month.getMonth());
    button.classList.toggle("today", key === today);
    button.classList.toggle("selected", key === state.selectedDate);
    button.setAttribute("aria-label", new Intl.DateTimeFormat(locale, {
      dateStyle: "full",
    }).format(date));
    button.addEventListener("click", () => {
      state.selectedDate = key;
      state.month = new Date(date.getFullYear(), date.getMonth(), 1);
      renderCalendar();
    });

    const count = state.board.items.filter((item) => itemDate(item) === key).length;
    if (count) {
      const dots = document.createElement("span");
      dots.className = "day-dots";
      for (let dot = 0; dot < Math.min(count, 3); dot += 1) {
        dots.append(createText("span", "day-dot", ""));
      }
      button.append(dots);
    }
    grid.append(button);
  }

  const selected = new Date(`${state.selectedDate}T12:00:00`);
  $("#agendaTitle").textContent = new Intl.DateTimeFormat(locale, {
    dateStyle: "full",
  }).format(selected);
  const agenda = $("#agendaItems");
  agenda.replaceChildren();
  const dayItems = state.board.items.filter((item) => itemDate(item) === state.selectedDate);
  dayItems.forEach((item) => agenda.append(itemCard(item, true)));
  if (!dayItems.length) appendEmpty(agenda);
}

function renderNotes() {
  const container = $("#notesItems");
  container.replaceChildren();
  const notes = state.board.items.filter((item) => item.kind === "note");
  notes.forEach((item) => container.append(itemCard(item)));
  if (!notes.length) appendEmpty(container);
}

function render() {
  renderMembers();
  renderBoard();
  renderCalendar();
  renderNotes();
}

async function loadBoard() {
  try {
    state.board = await api("/api/board");
    render();
    if (!state.board.members.length && !membersDialog.open) membersDialog.showModal();
  } catch (error) {
    showToast(error.message || t("networkError"), true);
  }
}

async function updateItem(itemId, fields) {
  if (!requireActor()) return;
  try {
    state.board = await api(`/api/items/${itemId}`, {
      method: "PATCH",
      body: JSON.stringify({ actor_id: selectedActor(), ...fields }),
    });
    render();
    showToast(t("updated"));
  } catch (error) {
    showToast(error.message || t("networkError"), true);
    await loadBoard();
  }
}

async function removeItem(itemId) {
  if (!requireActor() || !window.confirm(t("confirmDelete"))) return;
  try {
    state.board = await api(
      `/api/items/${itemId}?actor_id=${encodeURIComponent(selectedActor())}`,
      { method: "DELETE" },
    );
    render();
    showToast(t("deleted"));
  } catch (error) {
    showToast(error.message || t("networkError"), true);
  }
}

function setProcessing(processing) {
  $("#submitButton").disabled = processing;
  recordButton.disabled = processing;
  $("#submitButton").textContent = processing ? t("processing") : t("add");
}

$("#inputForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!requireActor()) return;
  const input = $("#textInput");
  setProcessing(true);
  try {
    state.board = await api("/api/input", {
      method: "POST",
      body: JSON.stringify({
        text: input.value,
        actor_id: selectedActor(),
        owner_id: ownerSelect.value || null,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC",
      }),
    });
    input.value = "";
    ownerSelect.value = "";
    render();
    showToast(t("added"));
  } catch (error) {
    showToast(error.message || t("networkError"), true);
  } finally {
    setProcessing(false);
  }
});

$("#memberForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = $("#memberName");
  try {
    state.board = await api("/api/members", {
      method: "POST",
      body: JSON.stringify({ name: input.value }),
    });
    input.value = "";
    render();
    showToast(t("added"));
  } catch (error) {
    showToast(error.message || t("networkError"), true);
  }
});

actorSelect.addEventListener("change", () => {
  localStorage.setItem("home-actor", actorSelect.value);
});

$("#membersButton").addEventListener("click", () => membersDialog.showModal());
$("#languageButton").addEventListener("click", () => {
  state.language = state.language === "zh" ? "en" : "zh";
  localStorage.setItem("home-language", state.language);
  applyLanguage();
});

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((button) => {
      const active = button === tab;
      button.classList.toggle("active", active);
      button.setAttribute("aria-selected", String(active));
    });
    document.querySelectorAll(".view").forEach((view) => {
      view.hidden = view.id !== `${tab.dataset.view}View`;
    });
  });
});

$("#previousMonth").addEventListener("click", () => {
  state.month = new Date(state.month.getFullYear(), state.month.getMonth() - 1, 1);
  state.selectedDate = dateKey(state.month);
  renderCalendar();
});

$("#nextMonth").addEventListener("click", () => {
  state.month = new Date(state.month.getFullYear(), state.month.getMonth() + 1, 1);
  state.selectedDate = dateKey(state.month);
  renderCalendar();
});

recordButton.addEventListener("click", async () => {
  if (state.recorder?.state === "recording") {
    state.recorder.stop();
    return;
  }
  if (!requireActor()) return;
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
      ? "audio/webm;codecs=opus"
      : "";
    const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : {});
    const chunks = [];
    state.recorder = recorder;
    recorder.addEventListener("dataavailable", (event) => {
      if (event.data.size) chunks.push(event.data);
    });
    recorder.addEventListener("stop", async () => {
      clearTimeout(state.recordingTimer);
      stream.getTracks().forEach((track) => track.stop());
      recordButton.classList.remove("recording");
      recordButton.querySelector("span").textContent = t("record");
      const audio = new Blob(chunks, { type: recorder.mimeType || "audio/webm" });
      if (!audio.size) return showToast(t("noSpeech"), true);
      const form = new FormData();
      form.append("file", audio, "recording.webm");
      form.append("actor_id", selectedActor());
      form.append("timezone", Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC");
      if (ownerSelect.value) form.append("owner_id", ownerSelect.value);
      setProcessing(true);
      try {
        state.board = await api("/api/audio", { method: "POST", body: form });
        render();
        showToast(t("added"));
      } catch (error) {
        showToast(error.message || t("networkError"), true);
      } finally {
        setProcessing(false);
      }
    });
    recorder.start();
    recordButton.classList.add("recording");
    recordButton.querySelector("span").textContent = t("stop");
    showToast(t("recording"));
    state.recordingTimer = setTimeout(() => {
      if (recorder.state === "recording") recorder.stop();
    }, 60000);
  } catch {
    showToast(t("microphoneError"), true);
  }
});

applyLanguage();
loadBoard();
