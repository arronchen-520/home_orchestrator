const messages = {
  zh: {
    iAm: "我是",
    currentMember: "当前家庭成员",
    switchLanguage: "切换语言",
    boardViews: "共享板视图",
    itemTypes: "内容类型",
    family: "家庭成员",
    eyebrow: "全家的事，一个地方",
    heading: "把家里的事，放在一起。",
    subheading: "打几个字或说一句，我们会整理成日程、待办或笔记。",
    inputLabel: "要添加什么？",
    inputPlaceholder: "例如：周六下午三点带孩子看牙医",
    sortHint: "有时间的进日历，要做的进待办，信息留在笔记。",
    optionalOwner: "负责人（可选）",
    unassigned: "未分配",
    record: "语音",
    stop: "停止",
    add: "添加",
    board: "共享板",
    calendar: "日历",
    notes: "笔记",
    workEyebrow: "家庭工作台",
    boardTitle: "全家的进行中",
    boardDescription: "日程和待办在这里认领、推进和完成；笔记单独收好。",
    myBoardTitle: "我的工作台",
    myBoardDescription: "这里只显示分配给我的日程和待办。",
    openItems: "未完成",
    mineItems: "我的",
    thisWeek: "本周",
    everyone: "全部",
    justMine: "只看我的",
    scopeFilter: "看板范围",
    search: "搜索",
    searchPlaceholder: "搜索日程或待办",
    type: "类型",
    allTypes: "全部类型",
    tasksOnly: "只看待办",
    eventsOnly: "只看日程",
    allOwners: "全部负责人",
    emptyFiltered: "没有符合当前筛选的内容",
    unclaimed: "未认领",
    claimed: "已认领",
    done: "完成",
    familyMembers: "家庭成员",
    citySetupTitle: "选择家庭城市",
    citySetupHelp: "天气会显示在日历上。输入城市和国家，例如 Toronto, CA。",
    cityLabel: "家庭城市",
    cityPlaceholder: "例如 Toronto, CA",
    saveCity: "保存城市",
    savingCity: "正在确认城市…",
    editCity: "修改家庭城市",
    cityNotFound: "找不到这个城市，请尝试加上国家代码",
    weatherData: "天气数据由 OpenWeather 提供",
    precipitation: "降雨概率",
    weatherUnavailable: "暂时无法加载天气",
    memberHelp: "先添加家庭成员。每个人使用前在右上角选择自己。",
    memberName: "成员姓名",
    addMember: "添加成员",
    previousPeriod: "上一段时间",
    nextPeriod: "下一段时间",
    calendarView: "日历视图",
    month: "月",
    week: "周",
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
    recurs: "重复",
    daily: "每天",
    weekly: "每周",
    monthly: "每月",
    monthlyLastDay: "每月最后一天",
    recurrenceEnds: "重复结束",
    edit: "编辑",
    editItem: "编辑内容",
    title: "标题",
    details: "详情",
    editScope: "修改范围",
    thisOccurrence: "只修改这一次",
    entireSeries: "修改整个系列",
    date: "日期",
    ends: "结束",
    specificTime: "指定时间",
    dueDate: "截止日期",
    seriesEditWarning: "修改系列开始时间会清除已有的单次例外。",
    saveChanges: "保存修改",
    editOccurrence: "修改这一次",
    cancelOccurrence: "取消这一次",
    confirmCancelOccurrence: "确定只取消这一次日程吗？",
    occurrenceTitlePrompt: "修改这一次的标题",
    occurrenceDatePrompt: "修改这一次的日期或时间",
    delete: "删除",
    confirmDelete: "确定删除这项内容吗？",
    confirmDeleteSeries: "确定删除整个重复日程吗？",
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
    openweatherMissing: "请在 .env 配置 OPENWEATHER_API_KEY",
    noSpeech: "没有识别到语音",
    today: "今天",
    notesEyebrow: "家庭资料夹",
    notesTitle: "留给以后用的信息",
    notesDescription: "门锁密码、购物偏好、学校信息——不需要完成，但需要找得到。",
  },
  en: {
    iAm: "I am",
    currentMember: "Current family member",
    switchLanguage: "Switch language",
    boardViews: "Board views",
    itemTypes: "Item types",
    family: "Family",
    eyebrow: "One place for home life",
    heading: "Keep home life together.",
    subheading: "Type it or say it. We’ll sort it into an event, task, or note.",
    inputLabel: "What would you like to add?",
    inputPlaceholder: "For example: Dentist for the kids Saturday at 3 PM",
    sortHint: "Timed plans go to Calendar, actions become Tasks, and information stays in Notes.",
    optionalOwner: "Owner (optional)",
    unassigned: "Unassigned",
    record: "Voice",
    stop: "Stop",
    add: "Add",
    board: "Board",
    calendar: "Calendar",
    notes: "Notes",
    workEyebrow: "Family workspace",
    boardTitle: "What everyone is working on",
    boardDescription: "Claim, move, and finish events and tasks here. Notes stay filed separately.",
    myBoardTitle: "My workspace",
    myBoardDescription: "Only events and tasks assigned to me are shown here.",
    openItems: "Open",
    mineItems: "Mine",
    thisWeek: "This week",
    everyone: "Everyone",
    justMine: "Just mine",
    scopeFilter: "Board scope",
    search: "Search",
    searchPlaceholder: "Search events or tasks",
    type: "Type",
    allTypes: "All types",
    tasksOnly: "Tasks only",
    eventsOnly: "Events only",
    allOwners: "All owners",
    emptyFiltered: "Nothing matches these filters",
    unclaimed: "Unclaimed",
    claimed: "Claimed",
    done: "Done",
    familyMembers: "Family members",
    citySetupTitle: "Choose your household city",
    citySetupHelp: "Weather will appear in Calendar. Enter a city and country, such as Toronto, CA.",
    cityLabel: "Household city",
    cityPlaceholder: "For example, Toronto, CA",
    saveCity: "Save city",
    savingCity: "Checking city…",
    editCity: "Edit household city",
    cityNotFound: "City not found. Try adding the country code.",
    weatherData: "Weather data provided by OpenWeather",
    precipitation: "Chance of rain",
    weatherUnavailable: "Weather is temporarily unavailable",
    memberHelp: "Add family members first. Each person selects themselves before use.",
    memberName: "Member name",
    addMember: "Add member",
    previousPeriod: "Previous period",
    nextPeriod: "Next period",
    calendarView: "Calendar view",
    month: "Month",
    week: "Week",
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
    recurs: "Repeats",
    daily: "Daily",
    weekly: "Weekly",
    monthly: "Monthly",
    monthlyLastDay: "Last day of every month",
    recurrenceEnds: "Recurrence ends",
    edit: "Edit",
    editItem: "Edit item",
    title: "Title",
    details: "Details",
    editScope: "Edit scope",
    thisOccurrence: "Only this occurrence",
    entireSeries: "Entire series",
    date: "Date",
    ends: "Ends",
    specificTime: "Specific time",
    dueDate: "Due date",
    seriesEditWarning: "Changing the series start clears existing occurrence exceptions.",
    saveChanges: "Save changes",
    editOccurrence: "Edit this occurrence",
    cancelOccurrence: "Cancel this occurrence",
    confirmCancelOccurrence: "Cancel only this occurrence?",
    occurrenceTitlePrompt: "Edit this occurrence's title",
    occurrenceDatePrompt: "Edit this occurrence's date or time",
    delete: "Delete",
    confirmDelete: "Delete this item?",
    confirmDeleteSeries: "Delete this entire recurring series?",
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
    openweatherMissing: "Configure OPENWEATHER_API_KEY in .env",
    noSpeech: "No speech was detected",
    today: "Today",
    notesEyebrow: "Family reference",
    notesTitle: "Information worth keeping",
    notesDescription: "Door codes, shopping preferences, school details—nothing to complete, but easy to find.",
  },
};

const state = {
  board: { household: {}, members: [], items: [] },
  calendarItems: [],
  weekItems: [],
  weather: null,
  language: localStorage.getItem("home-language")
    || (navigator.language.toLowerCase().startsWith("zh") ? "zh" : "en"),
  month: new Date(new Date().getFullYear(), new Date().getMonth(), 1),
  selectedDate: dateKey(new Date()),
  calendarMode: localStorage.getItem("home-calendar-mode") === "week" ? "week" : "month",
  boardScope: "all",
  typeFilter: "all",
  ownerFilter: "all",
  search: "",
  recorder: null,
  recordingTimer: null,
  editingItem: null,
  editingOccurrence: null,
};

const $ = (selector) => document.querySelector(selector);
const actorSelect = $("#actorSelect");
const ownerSelect = $("#newOwnerSelect");
const householdDialog = $("#householdDialog");
const membersDialog = $("#membersDialog");
const itemEditor = $("#itemEditor");
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
    if (detail.includes("OPENWEATHER_API_KEY")) throw new Error(t("openweatherMissing"));
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
  const ownerFilter = $("#ownerFilter");
  const savedFilter = state.ownerFilter;
  ownerFilter.replaceChildren(
    new Option(t("allOwners"), "all"),
    new Option(t("unassigned"), "unassigned"),
  );
  state.board.members.forEach((member) => {
    ownerFilter.add(new Option(member.name, member.id));
  });
  if ([...ownerFilter.options].some((option) => option.value === savedFilter)) {
    ownerFilter.value = savedFilter;
  } else {
    state.ownerFilter = "all";
  }

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
  const date = allDay && /^\d{4}-\d{2}-\d{2}$/.test(value)
    ? localDateFromKey(value)
    : new Date(value);
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

function weatherForDate(key) {
  return state.weather?.days.find((day) => day.date === key) || null;
}

function weatherIcon(weather, size = 32) {
  const image = document.createElement("img");
  image.src = `https://openweathermap.org/img/wn/${weather.icon}@2x.png`;
  image.alt = weather.description;
  image.width = size;
  image.height = size;
  image.loading = "lazy";
  return image;
}

function weatherBrief(weather) {
  const brief = document.createElement("span");
  brief.className = "weather-brief";
  brief.append(
    weatherIcon(weather),
    createText("span", "", `${weather.temp_min}° / ${weather.temp_max}°`),
  );
  return brief;
}

function renderSelectedWeather() {
  const container = $("#selectedWeather");
  const weather = weatherForDate(state.selectedDate);
  container.replaceChildren();
  container.hidden = !weather;
  if (!weather) return;

  const copy = document.createElement("div");
  copy.append(
    createText("strong", "", weather.description),
    createText("p", "", `${weather.temp_min}° / ${weather.temp_max}°`),
    createText(
      "p",
      "",
      `${t("precipitation")}: ${weather.precipitation_probability}%`,
    ),
  );
  container.className = "weather-detail";
  container.append(weatherIcon(weather, 52), copy);
}

function itemCard(item, compact = false, index = 0) {
  const card = document.createElement("article");
  card.className = `item-card ${item.status === "done" ? "done-card" : ""} ${item.kind === "note" ? "note-card" : ""}`;
  card.style.setProperty("--item-index", index);

  const top = document.createElement("div");
  top.className = "item-topline";
  const badge = createText("span", `badge ${item.kind}`, t(item.kind));
  const actions = document.createElement("div");
  actions.className = "item-actions";
  if (compact && item.is_occurrence) {
    const edit = createText("button", "delete-button", t("editOccurrence"));
    edit.type = "button";
    edit.addEventListener("click", () => editOccurrence(item));
    const cancel = createText("button", "delete-button", t("cancelOccurrence"));
    cancel.type = "button";
    cancel.addEventListener("click", () => cancelOccurrence(item));
    actions.append(edit, cancel);
  } else {
    const edit = createText("button", "delete-button", t("edit"));
    edit.type = "button";
    edit.addEventListener("click", () => openItemEditor(item));
    const remove = createText("button", "delete-button", t("delete"));
    remove.type = "button";
    remove.addEventListener("click", () => removeItem(item));
    actions.append(edit, remove);
  }
  top.append(badge, actions);
  card.append(top, createText("h3", "", item.title));

  if (item.details) card.append(createText("p", "", item.details));

  const meta = document.createElement("div");
  meta.className = "item-meta";
  if (item.kind === "event") {
    const starts = item.start_at || item.start_date;
    meta.append(createText(
      "p",
      "",
      `${t("starts")}: ${formatDateTime(starts, item.all_day)}${item.all_day ? ` · ${t("allDay")}` : ""}`,
    ));
    if (item.recurrence) {
      const recurrence = item.monthly_on_last_day ? "monthlyLastDay" : item.recurrence;
      meta.append(createText("p", "", `${t("recurs")}: ${t(recurrence)}`));
      if (item.recurrence_until) {
        meta.append(createText(
          "p",
          "",
          `${t("recurrenceEnds")}: ${formatDateTime(item.recurrence_until, true)}`,
        ));
      }
    }
  } else if (item.kind === "task" && (item.due_at || item.due_date)) {
    const due = item.due_at || item.due_date;
    meta.append(createText("p", "", `${t("due")}: ${formatDateTime(due, Boolean(item.due_date))}`));
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
    if (item.recurrence) {
      const endLabel = createText("label", "", t("recurrenceEnds"));
      const endInput = document.createElement("input");
      endInput.type = "date";
      endInput.value = item.recurrence_until || "";
      endInput.addEventListener("change", () => {
        updateItem(item.id, { recurrence_until: endInput.value || null });
      });
      endLabel.append(endInput);
      controls.append(endLabel);
    }
    card.append(controls);
  } else if (compact && item.kind !== "note") {
    card.append(createText("p", "", `${t("owner")}: ${memberName(item.owner_id)}`));
  }
  card.addEventListener("click", (event) => {
    if (!event.target.closest("button, input, select, textarea, label")) {
      openItemEditor(item);
    }
  });
  return card;
}

function appendEmpty(container, key = "empty") {
  container.append(createText("p", "empty", t(key)));
}

function actionItems() {
  return state.board.items.filter((item) => item.kind !== "note");
}

function filteredBoardItems() {
  const query = state.search.trim().toLocaleLowerCase();
  return actionItems().filter((item) => {
    if (state.boardScope === "mine" && item.owner_id !== selectedActor()) return false;
    if (state.typeFilter !== "all" && item.kind !== state.typeFilter) return false;
    if (state.boardScope === "all" && state.ownerFilter !== "all") {
      if (state.ownerFilter === "unassigned" && item.owner_id) return false;
      if (state.ownerFilter !== "unassigned" && item.owner_id !== state.ownerFilter) return false;
    }
    return !query || `${item.title} ${item.details || ""}`.toLocaleLowerCase().includes(query);
  });
}

function happensThisWeek(item) {
  return state.weekItems.some(
    (occurrence) => (occurrence.series_id || occurrence.id) === item.id,
  );
}

function renderBoard() {
  const allItems = actionItems();
  const visibleItems = filteredBoardItems();
  const openItems = allItems.filter((item) => item.status !== "done");
  $("#openStat").textContent = openItems.length;
  $("#mineStat").textContent = openItems.filter((item) => item.owner_id === selectedActor()).length;
  $("#weekStat").textContent = openItems.filter(happensThisWeek).length;
  $("#boardTabCount").textContent = openItems.length;
  $("#notesTabCount").textContent = state.board.items.filter((item) => item.kind === "note").length;
  $("#boardTitle").textContent = t(state.boardScope === "mine" ? "myBoardTitle" : "boardTitle");
  const boardDescription = $("#boardTitle").nextElementSibling;
  boardDescription.textContent = t(
    state.boardScope === "mine" ? "myBoardDescription" : "boardDescription",
  );
  $("#ownerFilter").disabled = state.boardScope === "mine";
  document.querySelectorAll("[data-scope]").forEach((button) => {
    const active = button.dataset.scope === state.boardScope;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  const defaultFilters = state.boardScope === "all"
    && state.typeFilter === "all"
    && state.ownerFilter === "all"
    && !state.search.trim();

  ["unclaimed", "claimed", "done"].forEach((status) => {
    const items = visibleItems.filter((item) => item.status === status);
    const container = $(`#${status}Items`);
    container.replaceChildren();
    items.forEach((item, index) => container.append(itemCard(item, false, index)));
    if (!items.length) appendEmpty(container, defaultFilters ? "empty" : "emptyFiltered");
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
  const value = item.kind === "event"
    ? item.start_at || item.start_date
    : item.kind === "task"
      ? item.due_at || item.due_date
      : null;
  if (/^\d{4}-\d{2}-\d{2}$/.test(value || "")) return value;
  return value ? dateKey(new Date(value)) : null;
}

function localDateFromKey(key) {
  return new Date(`${key}T12:00:00`);
}

function startOfWeek(date) {
  const start = new Date(date);
  start.setDate(date.getDate() - date.getDay());
  return start;
}

function itemsForDate(key) {
  return state.calendarItems.filter((item) => itemDate(item) === key);
}

function renderCalendarDay(grid, date, locale, outside = false) {
  const key = dateKey(date);
  const today = dateKey(new Date());
  const dayItems = itemsForDate(key);
  const weather = weatherForDate(key);
  const weekMode = state.calendarMode === "week";
  const button = document.createElement("button");
  button.type = "button";
  button.className = `day${weekMode ? " week-day" : ""}`;
  button.classList.toggle("outside", outside);
  button.classList.toggle("today", key === today);
  button.classList.toggle("selected", key === state.selectedDate);
  const dateLabel = new Intl.DateTimeFormat(locale, {
    dateStyle: "full",
  }).format(date);
  button.setAttribute(
    "aria-label",
    weather
      ? `${dateLabel}, ${weather.description}, ${weather.temp_min}°–${weather.temp_max}°`
      : dateLabel,
  );

  if (weekMode) {
    button.append(
      createText("span", "week-day-name", new Intl.DateTimeFormat(locale, {
        weekday: "short",
      }).format(date)),
      createText("strong", "week-day-number", date.getDate()),
    );
    if (weather) button.append(weatherBrief(weather));
    const preview = document.createElement("span");
    preview.className = "week-preview";
    dayItems.slice(0, 3).forEach((item) => {
      preview.append(createText("span", `calendar-label ${item.kind}`, item.title));
    });
    if (dayItems.length > 3) preview.append(createText("span", "more-label", `+${dayItems.length - 3}`));
    button.append(preview);
  } else {
    button.append(createText("span", "day-number", date.getDate()));
    if (weather) button.append(weatherBrief(weather));
    if (dayItems.length) {
      const dots = document.createElement("span");
      dots.className = "day-dots";
      dayItems.slice(0, 3).forEach((item) => {
        dots.append(createText("span", `day-dot ${item.kind}`, ""));
      });
      button.append(dots);
    }
  }

  button.addEventListener("click", () => {
    state.selectedDate = key;
    state.month = new Date(date.getFullYear(), date.getMonth(), 1);
    renderCalendar();
  });
  grid.append(button);
}

function renderCalendar() {
  const locale = state.language === "zh" ? "zh-CN" : "en-CA";
  const selected = localDateFromKey(state.selectedDate);
  const grid = $("#calendarGrid");
  const household = state.board.household || {};
  const locationButton = $("#householdLocationButton");
  locationButton.hidden = !household.city;
  locationButton.textContent = household.city
    ? `${household.city}, ${household.country_code}`
    : "";
  $("#weatherAttribution").hidden = !state.weather?.days.length;
  grid.replaceChildren();
  grid.classList.toggle("week-mode", state.calendarMode === "week");

  document.querySelectorAll("[data-calendar-mode]").forEach((button) => {
    const active = button.dataset.calendarMode === state.calendarMode;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });

  if (state.calendarMode === "month") {
    $("#monthTitle").textContent = new Intl.DateTimeFormat(locale, {
      month: "long",
      year: "numeric",
    }).format(state.month);

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
    for (let index = 0; index < 42; index += 1) {
      const date = new Date(start);
      date.setDate(start.getDate() + index);
      renderCalendarDay(grid, date, locale, date.getMonth() !== state.month.getMonth());
    }
  } else {
    const start = startOfWeek(selected);
    const end = new Date(start);
    end.setDate(start.getDate() + 6);
    const shortDate = new Intl.DateTimeFormat(locale, { month: "short", day: "numeric" });
    $("#monthTitle").textContent = `${shortDate.format(start)} – ${shortDate.format(end)}`;
    for (let index = 0; index < 7; index += 1) {
      const date = new Date(start);
      date.setDate(start.getDate() + index);
      renderCalendarDay(grid, date, locale);
    }
  }

  $("#agendaTitle").textContent = new Intl.DateTimeFormat(locale, {
    dateStyle: "full",
  }).format(selected);
  const agenda = $("#agendaItems");
  agenda.replaceChildren();
  const dayItems = itemsForDate(state.selectedDate);
  renderSelectedWeather();
  dayItems.forEach((item, index) => agenda.append(itemCard(item, true, index)));
  if (!dayItems.length) appendEmpty(agenda);
}

function renderNotes() {
  const container = $("#notesItems");
  container.replaceChildren();
  const notes = state.board.items.filter((item) => item.kind === "note");
  notes.forEach((item, index) => container.append(itemCard(item, false, index)));
  if (!notes.length) appendEmpty(container);
}

function render() {
  renderMembers();
  renderBoard();
  renderCalendar();
  renderNotes();
}

function calendarRange() {
  if (state.calendarMode === "week") {
    const start = startOfWeek(localDateFromKey(state.selectedDate));
    const end = new Date(start);
    end.setDate(start.getDate() + 6);
    return [dateKey(start), dateKey(end)];
  }
  const first = new Date(state.month.getFullYear(), state.month.getMonth(), 1);
  const start = new Date(first);
  start.setDate(1 - first.getDay());
  const end = new Date(start);
  end.setDate(start.getDate() + 41);
  return [dateKey(start), dateKey(end)];
}

async function loadCalendar() {
  try {
    const [start, end] = calendarRange();
    const currentWeek = startOfWeek(new Date());
    const currentWeekEnd = new Date(currentWeek);
    currentWeekEnd.setDate(currentWeek.getDate() + 6);
    const [calendar, week] = await Promise.all([
      api(`/api/calendar?start=${start}&end=${end}`),
      api(`/api/calendar?start=${dateKey(currentWeek)}&end=${dateKey(currentWeekEnd)}`),
    ]);
    state.calendarItems = calendar.items;
    state.weekItems = week.items;
  } catch (error) {
    state.calendarItems = [];
    state.weekItems = [];
    showToast(error.message || t("networkError"), true);
  }
  render();
}

async function loadBoard() {
  try {
    state.board = await api("/api/board");
    await loadCalendar();
    if (!state.board.household?.city) {
      $("#closeHouseholdDialog").hidden = true;
      householdDialog.showModal();
      return;
    }
    await loadWeather();
    if (!state.board.members.length && !membersDialog.open) membersDialog.showModal();
  } catch (error) {
    showToast(error.message || t("networkError"), true);
  }
}

async function loadWeather() {
  if (!state.board.household?.city) return;
  try {
    const language = state.language === "zh" ? "zh_cn" : "en";
    state.weather = await api(`/api/weather?lang=${language}`);
    renderCalendar();
  } catch (error) {
    state.weather = null;
    renderCalendar();
    showToast(t("weatherUnavailable"), true);
  }
}

async function updateItem(itemId, fields) {
  if (!requireActor()) return;
  try {
    state.board = await api(`/api/items/${itemId}`, {
      method: "PATCH",
      body: JSON.stringify({ actor_id: selectedActor(), ...fields }),
    });
    await loadCalendar();
    showToast(t("updated"));
  } catch (error) {
    showToast(error.message || t("networkError"), true);
    await loadBoard();
  }
}

function toLocalDateTime(value) {
  if (!value) return "";
  const date = new Date(value);
  const local = new Date(date.valueOf() - (date.getTimezoneOffset() * 60000));
  return local.toISOString().slice(0, 16);
}

function toggleEditorFields() {
  const allDay = $("#editAllDay").checked;
  $("#editStartDateField").hidden = !allDay;
  $("#editStartAtField").hidden = allDay;
  $("#editEndAtField").hidden = allDay;
  $("#editStartDate").required = allDay;
  $("#editStartAt").required = !allDay;
  const dueTimed = $("#editDueTimed").checked;
  $("#editDueDateField").hidden = dueTimed;
  $("#editDueAtField").hidden = !dueTimed;
}

function editorItemForScope(scope) {
  if (scope === "occurrence") return state.editingOccurrence;
  if (!state.editingOccurrence) return state.editingItem;
  return state.board.items.find(
    (item) => item.id === state.editingOccurrence.series_id,
  );
}

function fillItemEditor(item, scope) {
  if (!item) return;
  state.editingItem = item;
  $("#editTitle").value = item.title;
  $("#editDetails").value = item.details || "";
  $("#editEventFields").hidden = item.kind !== "event";
  $("#editTaskFields").hidden = item.kind !== "task";

  if (item.kind === "event") {
    $("#editAllDay").checked = Boolean(item.all_day);
    $("#editStartDate").value = item.start_date || "";
    $("#editStartAt").value = toLocalDateTime(item.start_at);
    $("#editEndAt").value = toLocalDateTime(item.end_at);
    $("#editRecurrenceUntil").value = item.recurrence_until || "";
  } else if (item.kind === "task") {
    $("#editDueTimed").checked = Boolean(item.due_at);
    $("#editDueDate").value = item.due_date || "";
    $("#editDueAt").value = toLocalDateTime(item.due_at);
  }

  const editingSeries = scope === "series" && Boolean(item.recurrence);
  $("#editRecurrenceUntilField").hidden = !editingSeries;
  $("#editSeriesWarning").hidden = !(
    editingSeries && Boolean(state.editingOccurrence)
  );
  toggleEditorFields();
}

function openItemEditor(item) {
  state.editingItem = item;
  state.editingOccurrence = item.is_occurrence ? item : null;
  const scope = state.editingOccurrence ? "occurrence" : "series";
  $("#editScopeField").hidden = !state.editingOccurrence;
  $("#editScope").value = scope;
  $("#itemEditorError").hidden = true;
  fillItemEditor(editorItemForScope(scope) || item, scope);
  itemEditor.showModal();
}

function editOccurrence(item) {
  openItemEditor(item);
}

async function saveItemEditor(event) {
  event.preventDefault();
  if (!requireActor()) return;
  const error = $("#itemEditorError");
  error.hidden = true;
  const scope = $("#editScope").value;
  const item = editorItemForScope(scope);
  const fields = {
    title: $("#editTitle").value,
    details: $("#editDetails").value,
  };

  if (item.kind === "event") {
    if ($("#editAllDay").checked) {
      fields.start_date = $("#editStartDate").value;
      fields.start_at = null;
      fields.end_at = null;
    } else {
      fields.start_at = new Date($("#editStartAt").value).toISOString();
      fields.end_at = $("#editEndAt").value
        ? new Date($("#editEndAt").value).toISOString()
        : null;
      fields.start_date = null;
    }
    if (scope === "series") {
      fields.all_day = $("#editAllDay").checked;
      if (item.recurrence) {
        fields.recurrence_until = $("#editRecurrenceUntil").value || null;
      }
    }
  } else if (item.kind === "task") {
    if ($("#editDueTimed").checked) {
      fields.due_at = $("#editDueAt").value
        ? new Date($("#editDueAt").value).toISOString()
        : null;
      fields.due_date = null;
    } else {
      fields.due_date = $("#editDueDate").value || null;
      fields.due_at = null;
    }
  }

  const path = state.editingOccurrence && scope === "occurrence"
    ? `/api/items/${state.editingOccurrence.series_id}/occurrences/${state.editingOccurrence.occurrence_date}`
    : `/api/items/${item.id}`;
  try {
    state.board = await api(path, {
      method: "PATCH",
      body: JSON.stringify({ actor_id: selectedActor(), ...fields }),
    });
    await loadCalendar();
    itemEditor.close();
    showToast(t("updated"));
  } catch (problem) {
    error.textContent = problem.message || t("networkError");
    error.hidden = false;
  }
}

async function cancelOccurrence(item) {
  if (
    !requireActor()
    || !window.confirm(t("confirmCancelOccurrence"))
  ) return;
  try {
    state.board = await api(
      `/api/items/${item.series_id}/occurrences/${item.occurrence_date}`
        + `?actor_id=${encodeURIComponent(selectedActor())}`,
      { method: "DELETE" },
    );
    await loadCalendar();
    showToast(t("deleted"));
  } catch (error) {
    showToast(error.message || t("networkError"), true);
  }
}

async function removeItem(item) {
  const message = item.recurrence ? "confirmDeleteSeries" : "confirmDelete";
  if (!requireActor() || !window.confirm(t(message))) return;
  try {
    state.board = await api(
      `/api/items/${item.id}?actor_id=${encodeURIComponent(selectedActor())}`,
      { method: "DELETE" },
    );
    await loadCalendar();
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

$("#editAllDay").addEventListener("change", toggleEditorFields);
$("#editDueTimed").addEventListener("change", toggleEditorFields);
$("#editScope").addEventListener("change", (event) => {
  fillItemEditor(editorItemForScope(event.target.value), event.target.value);
});
$("#itemEditorForm").addEventListener("submit", saveItemEditor);
$("#closeItemEditor").addEventListener("click", () => itemEditor.close());
$("#cancelItemEditor").addEventListener("click", () => itemEditor.close());

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
    await loadCalendar();
    showToast(t("added"));
  } catch (error) {
    showToast(error.message || t("networkError"), true);
  } finally {
    setProcessing(false);
  }
});

$("#householdForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = $("#householdCity");
  const error = $("#householdError");
  const button = $("#saveHouseholdButton");
  button.disabled = true;
  button.textContent = t("savingCity");
  error.hidden = true;
  try {
    state.board = await api("/api/household", {
      method: "PUT",
      body: JSON.stringify({ city: input.value }),
    });
    state.weather = null;
    householdDialog.close();
    render();
    await loadWeather();
    if (!state.board.members.length && !membersDialog.open) membersDialog.showModal();
  } catch (problem) {
    error.textContent = problem.message.includes("City not found")
      ? t("cityNotFound")
      : problem.message;
    error.hidden = false;
  } finally {
    button.disabled = false;
    button.textContent = t("saveCity");
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
  renderBoard();
});

$("#membersButton").addEventListener("click", () => membersDialog.showModal());
$("#householdLocationButton").addEventListener("click", () => {
  const household = state.board.household || {};
  $("#householdCity").value = household.city
    ? `${household.city}, ${household.country_code}`
    : "";
  $("#closeHouseholdDialog").hidden = false;
  $("#householdError").hidden = true;
  householdDialog.showModal();
});
householdDialog.addEventListener("cancel", (event) => {
  if (!state.board.household?.city) event.preventDefault();
});
$("#languageButton").addEventListener("click", () => {
  state.language = state.language === "zh" ? "en" : "zh";
  localStorage.setItem("home-language", state.language);
  applyLanguage();
  loadWeather();
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

document.querySelectorAll("[data-scope]").forEach((button) => {
  button.addEventListener("click", () => {
    state.boardScope = button.dataset.scope;
    renderBoard();
  });
});

$("#boardSearch").addEventListener("input", (event) => {
  state.search = event.target.value;
  renderBoard();
});

$("#typeFilter").addEventListener("change", (event) => {
  state.typeFilter = event.target.value;
  renderBoard();
});

$("#ownerFilter").addEventListener("change", (event) => {
  state.ownerFilter = event.target.value;
  renderBoard();
});

document.querySelectorAll("[data-calendar-mode]").forEach((button) => {
  button.addEventListener("click", async () => {
    state.calendarMode = button.dataset.calendarMode;
    localStorage.setItem("home-calendar-mode", state.calendarMode);
    await loadCalendar();
  });
});

async function moveCalendar(direction) {
  if (state.calendarMode === "month") {
    state.month = new Date(state.month.getFullYear(), state.month.getMonth() + direction, 1);
    state.selectedDate = dateKey(state.month);
  } else {
    const selected = localDateFromKey(state.selectedDate);
    selected.setDate(selected.getDate() + (direction * 7));
    state.selectedDate = dateKey(selected);
    state.month = new Date(selected.getFullYear(), selected.getMonth(), 1);
  }
  await loadCalendar();
}

$("#previousPeriod").addEventListener("click", () => moveCalendar(-1));
$("#nextPeriod").addEventListener("click", () => moveCalendar(1));
$("#todayButton").addEventListener("click", async () => {
  const today = new Date();
  state.selectedDate = dateKey(today);
  state.month = new Date(today.getFullYear(), today.getMonth(), 1);
  await loadCalendar();
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
