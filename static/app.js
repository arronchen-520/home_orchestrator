const messages = {
  zh: {
    iAm: "我是",
    currentMember: "当前家庭成员",
    switchLanguage: "切换语言",
    boardViews: "共享板视图",
    itemTypes: "内容类型",
    family: "家庭成员",
    eyebrow: "家里的安排",
    heading: "今天家里有什么事？",
    subheading: "输入文字或说一句话，就能添加日程、待办或笔记。",
    inputLabel: "要添加什么？",
    inputPlaceholder: "例如：周六下午三点带孩子看牙医",
    sortHint: "有时间的放进日历，要做的放进待办，其他信息存为笔记。",
    optionalOwner: "负责人（可选）",
    unassigned: "未分配",
    record: "语音",
    stop: "停止",
    add: "添加",
    board: "共享板",
    calendar: "日历",
    notes: "笔记",
    workEyebrow: "家庭看板",
    boardTitle: "大家要做的事",
    boardDescription: "日程和待办都在这里。认领后可以更新进度，笔记在单独页面。",
    myBoardTitle: "我要做的事",
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
    pendingAssignment: "等待接受",
    accept: "接受",
    reject: "拒绝",
    familyMembers: "家庭成员",
    familyManage: "家庭管理",
    accessTitle: "打开家庭看板",
    accessHelp: "输入家人分享给你的访问码。",
    accessCode: "家庭访问码",
    unlock: "打开看板",
    unlocking: "正在打开…",
    invalidAccess: "访问码不正确",
    switchHousehold: "切换家庭",
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
    memberHelp: "添加家庭成员后，每个人使用前在右上角选择自己。",
    memberName: "成员姓名",
    memberRole: "身份（例如：爸爸）",
    removeMember: "删除",
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
    reminder: "提醒时间",
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
    cancel: "取消",
    confirmCancelOccurrence: "确定只取消这一次日程吗？",
    occurrenceTitlePrompt: "修改这一次的标题",
    occurrenceDatePrompt: "修改这一次的日期或时间",
    delete: "删除",
    confirmDelete: "确定删除这项内容吗？",
    confirmDeleteSeries: "确定删除整个重复日程吗？",
    empty: "这里还没有内容",
    chooseMember: "请先添加并选择一位家庭成员",
    added: "已添加",
    reply: "回复",
    analyzing: "正在整理…",
    preparation: "准备工作",
    acceptPreparation: "接受这项准备工作",
    assumptions: "采用的理解",
    conflicts: "需要注意",
    confirmCreate: "确认创建",
    startOver: "重新开始",
    suggestedOwner: "负责人（可修改）",
    timeConflict: "与“{title}”在 {date} 时间冲突",
    duplicateConflict: "可能与“{title}”重复",
    updated: "已更新",
    deleted: "已删除",
    recording: "正在录音，再按一次停止",
    processing: "正在整理…",
    microphoneError: "无法使用麦克风",
    networkError: "操作失败，请检查服务和 API 配置",
    openrouterMissing: "请在 .env 配置 OPENROUTER_API_KEY",
    groqMissing: "请在 .env 配置 GROQ_API_KEY",
    openweatherMissing: "请在 .env 配置 OPENWEATHER_API_KEY",
    noSpeech: "没有识别到语音",
    assistantEyebrow: "家庭助手",
    assistantTitle: "问问家庭安排",
    assistantInputLabel: "询问日程、待办或笔记",
    assistantPlaceholder: "例如：这周末有什么安排？",
    openAssistant: "打开家庭助手",
    closeAssistant: "关闭家庭助手",
    newChat: "新对话",
    send: "发送",
    assistantWelcome: "你可以问家庭日程、待办、提醒、准备工作或笔记。",
    assistantThinking: "正在查找…",
    assistantConfirmAction: "确认修改",
    assistantCancelAction: "取消",
    assistantActionDone: "看板已更新。",
    assistantActionCancelled: "已取消这次修改。",
    today: "今天",
    notesEyebrow: "家庭信息",
    notesTitle: "常用信息",
    notesDescription: "门锁密码、购物偏好、学校信息等，都可以记在这里。",
  },
  en: {
    iAm: "I am",
    currentMember: "Current family member",
    switchLanguage: "Switch language",
    boardViews: "Board views",
    itemTypes: "Item types",
    family: "Family",
    eyebrow: "Family plans",
    heading: "What's happening at home?",
    subheading: "Type or say something to add an event, task, or note.",
    inputLabel: "What would you like to add?",
    inputPlaceholder: "For example: Dentist for the kids Saturday at 3 PM",
    sortHint: "Timed plans go on the calendar. Actions become tasks. Other information goes in notes.",
    optionalOwner: "Owner (optional)",
    unassigned: "Unassigned",
    record: "Voice",
    stop: "Stop",
    add: "Add",
    board: "Board",
    calendar: "Calendar",
    notes: "Notes",
    workEyebrow: "Family board",
    boardTitle: "Plans and tasks",
    boardDescription: "Events and tasks are here. Claim one or update its status. Notes stay separate.",
    myBoardTitle: "My items",
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
    pendingAssignment: "Awaiting acceptance",
    accept: "Accept",
    reject: "Decline",
    familyMembers: "Family members",
    familyManage: "Manage family",
    accessTitle: "Open your family board",
    accessHelp: "Enter the access code shared by your family.",
    accessCode: "Household access code",
    unlock: "Open board",
    unlocking: "Opening…",
    invalidAccess: "That access code is not valid",
    switchHousehold: "Switch household",
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
    memberHelp: "Add family members, then choose your name in the top-right before using the board.",
    memberName: "Member name",
    memberRole: "Role (for example, Dad)",
    removeMember: "Remove",
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
    reminder: "Reminder",
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
    cancel: "Cancel",
    confirmCancelOccurrence: "Cancel only this occurrence?",
    occurrenceTitlePrompt: "Edit this occurrence's title",
    occurrenceDatePrompt: "Edit this occurrence's date or time",
    delete: "Delete",
    confirmDelete: "Delete this item?",
    confirmDeleteSeries: "Delete this entire recurring series?",
    empty: "Nothing here yet",
    chooseMember: "Add and choose a family member first",
    added: "Added",
    reply: "Reply",
    analyzing: "Working on it…",
    preparation: "Preparation",
    acceptPreparation: "Accept this preparation",
    assumptions: "Assumptions",
    conflicts: "Needs attention",
    confirmCreate: "Confirm and create",
    startOver: "Start over",
    suggestedOwner: "Owner (editable)",
    timeConflict: "Overlaps \"{title}\" on {date}",
    duplicateConflict: "May duplicate \"{title}\"",
    updated: "Updated",
    deleted: "Deleted",
    recording: "Recording. Press again to stop.",
    processing: "Organizing…",
    microphoneError: "Microphone is unavailable",
    networkError: "Action failed. Check the service and API configuration.",
    openrouterMissing: "Configure OPENROUTER_API_KEY in .env",
    groqMissing: "Configure GROQ_API_KEY in .env",
    openweatherMissing: "Configure OPENWEATHER_API_KEY in .env",
    noSpeech: "No speech was detected",
    assistantEyebrow: "Family assistant",
    assistantTitle: "Ask about home plans",
    assistantInputLabel: "Ask about schedules, tasks, or notes",
    assistantPlaceholder: "For example: What is happening this weekend?",
    openAssistant: "Open family assistant",
    closeAssistant: "Close family assistant",
    newChat: "New chat",
    send: "Send",
    assistantWelcome: "Ask about family events, tasks, reminders, preparations, or notes.",
    assistantThinking: "Checking the board…",
    assistantConfirmAction: "Confirm change",
    assistantCancelAction: "Cancel",
    assistantActionDone: "I updated the board.",
    assistantActionCancelled: "That change was cancelled.",
    today: "Today",
    notesEyebrow: "Family notes",
    notesTitle: "Useful information",
    notesDescription: "Keep door codes, shopping preferences, school details, and other household information here.",
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
  intake: null,
  assistant: null,
  assistantPending: "",
  assistantError: "",
  editingItem: null,
  editingOccurrence: null,
};

const $ = (selector) => document.querySelector(selector);
const actorSelect = $("#actorSelect");
const ownerSelect = $("#newOwnerSelect");
const accessDialog = $("#accessDialog");
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
    let message = detail || t("networkError");
    if (detail.includes("OPENROUTER_API_KEY")) message = t("openrouterMissing");
    if (detail.includes("GROQ_API_KEY")) message = t("groqMissing");
    if (detail.includes("OPENWEATHER_API_KEY")) message = t("openweatherMissing");
    const error = new Error(message);
    error.status = response.status;
    throw error;
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
  renderIntake();
  renderAssistant();
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
    select.add(new Option(member.role ? `${member.name} (${member.role})` : member.name, member.id));
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
    item.append(createText("span", "", member.role ? `${member.name} · ${member.role}` : member.name));
    const remove = document.createElement("button");
    remove.className = "button ghost compact";
    remove.type = "button";
    remove.textContent = t("removeMember");
    remove.addEventListener("click", async () => {
      if (!confirm(`${t("removeMember")} ${member.name}?`)) return;
      state.board = await api(`/api/members/${member.id}`, { method: "DELETE" });
      if (localStorage.getItem("home-actor") === member.id) localStorage.removeItem("home-actor");
      render();
    });
    item.append(remove);
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

function reviewList(container, title, items, itemClass = "") {
  container.replaceChildren();
  if (!items?.length) return;
  container.className = "intake-review-section";
  container.append(createText("h3", "", title));
  const list = document.createElement("ul");
  items.forEach((text) => list.append(createText("li", itemClass, text)));
  container.append(list);
}

function draftSchedule(draft) {
  if (draft.kind === "event") {
    const value = draft.start_date || draft.start_at;
    return value ? `${t("starts")}: ${formatDateTime(value, Boolean(draft.start_date))}` : "";
  }
  if (draft.kind === "task") {
    const value = draft.due_date || draft.due_at;
    return value ? `${t("due")}: ${formatDateTime(value, Boolean(draft.due_date))}` : "";
  }
  return "";
}

function renderIntake(response = state.intake) {
  const panel = $("#intakeConversation");
  if (!response) {
    panel.hidden = true;
    return;
  }
  panel.hidden = false;
  const messages = $("#intakeMessages");
  messages.replaceChildren(...response.messages.map((message) =>
    createText("p", `intake-message ${message.role}`, message.content)
  ));

  const reviewing = response.status === "review";
  $("#intakeReview").hidden = !reviewing;
  $("#intakeConfirmButton").hidden = !reviewing;
  $("#submitButton").hidden = reviewing;
  $("#textInput").disabled = reviewing;
  ownerSelect.disabled = true;
  if (!reviewing) {
    $("#textInput").placeholder = t("reply");
    return;
  }

  reviewList($("#intakeAssumptions"), t("assumptions"), response.assumptions);
  const conflicts = response.conflicts.map((conflict) => (
    conflict.kind === "duplicate"
      ? t("duplicateConflict").replace("{title}", conflict.existing_title)
      : t("timeConflict")
        .replace("{title}", conflict.existing_title)
        .replace("{date}", conflict.date)
  ));
  reviewList($("#intakeConflicts"), t("conflicts"), conflicts, "intake-conflict");

  const drafts = $("#intakeDrafts");
  drafts.replaceChildren();
  response.drafts.forEach((draft) => {
    const card = document.createElement("article");
    card.className = "intake-draft";
    card.append(
      createText("strong", "", `${t(draft.kind)} · ${draft.title}`),
    );
    if (draft.details) card.append(createText("p", "", draft.details));
    const schedule = draftSchedule(draft);
    if (schedule) card.append(createText("p", "", schedule));
    if (draft.preparation) {
      if (draft.preparation_accepted === undefined) {
        draft.preparation_accepted = true;
      }
      const preparationLabel = document.createElement("label");
      preparationLabel.className = "preparation-choice";
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.checked = draft.preparation_accepted;
      checkbox.addEventListener("change", () => {
        draft.preparation_accepted = checkbox.checked;
      });
      preparationLabel.append(
        checkbox,
        createText(
          "span",
          "",
          `${t("acceptPreparation")}: ${draft.preparation}`,
        ),
      );
      card.append(preparationLabel);
    }
    if (draft.kind !== "note") {
      const label = document.createElement("label");
      label.append(createText("span", "", t("suggestedOwner")));
      const select = document.createElement("select");
      select.className = "draft-owner";
      select.append(new Option(t("unassigned"), ""));
      state.board.members.forEach((member) => {
        select.append(new Option(
          member.role ? `${member.name} · ${member.role}` : member.name,
          member.id,
        ));
      });
      select.value = draft.owner_id || "";
      select.addEventListener("change", () => {
        draft.owner_id = select.value || null;
      });
      label.append(select);
      card.append(label);
    }
    drafts.append(card);
  });
}

function resetIntake() {
  state.intake = null;
  $("#intakeConversation").hidden = true;
  $("#intakeReview").hidden = true;
  $("#intakeConfirmButton").hidden = true;
  $("#submitButton").hidden = false;
  $("#textInput").disabled = false;
  $("#textInput").value = "";
  $("#textInput").placeholder = t("inputPlaceholder");
  ownerSelect.disabled = false;
  ownerSelect.value = "";
}

function handleIntakeResponse(response) {
  state.intake = response;
  $("#textInput").value = "";
  renderIntake();
}

function renderAssistant() {
  const container = $("#assistantMessages");
  const messages = state.assistant?.messages?.length
    ? [...state.assistant.messages]
    : [{ role: "assistant", content: t("assistantWelcome") }];
  if (state.assistantPending) {
    messages.push(
      { role: "user", content: state.assistantPending },
      { role: "assistant", content: t("assistantThinking") },
    );
  } else if (state.assistantError) {
    messages.push({ role: "assistant", content: state.assistantError });
  }
  container.replaceChildren(...messages.map((message) =>
    createText("p", `assistant-message ${message.role}`, message.content)
  ));
  if (state.assistant?.action && !state.assistantPending && !state.assistantError) {
    const action = document.createElement("div");
    action.className = "assistant-action";
    action.append(createText("p", "", state.assistant.action.confirmation));
    const controls = document.createElement("div");
    controls.className = "assistant-action-controls";
    const confirmButton = createText("button", "button primary compact", t("assistantConfirmAction"));
    confirmButton.type = "button";
    confirmButton.addEventListener("click", confirmAssistantAction);
    const cancelButton = createText("button", "button secondary compact", t("assistantCancelAction"));
    cancelButton.type = "button";
    cancelButton.addEventListener("click", () => {
      state.assistant.action = null;
      state.assistant.messages.push({ role: "assistant", content: t("assistantActionCancelled") });
      renderAssistant();
    });
    controls.append(confirmButton, cancelButton);
    action.append(controls);
    container.append(action);
  }
  container.scrollTop = container.scrollHeight;
}

async function confirmAssistantAction(event) {
  if (!requireActor() || !state.assistant?.action) return;
  const action = state.assistant.action;
  event.currentTarget.disabled = true;
  try {
    state.board = await api(`/api/items/${action.item_id}`, {
      method: "PATCH",
      body: JSON.stringify({ actor_id: selectedActor(), ...action.fields }),
    });
    state.assistant.action = null;
    state.assistant.messages.push({ role: "assistant", content: t("assistantActionDone") });
    await loadCalendar();
    showToast(t("updated"));
  } catch (error) {
    event.currentTarget.disabled = false;
    showToast(error.message || t("networkError"), true);
  }
  renderAssistant();
}

function resetAssistant() {
  state.assistant = null;
  state.assistantPending = "";
  state.assistantError = "";
  $("#assistantInput").value = "";
  renderAssistant();
}

function toggleAssistant(open) {
  const panel = $("#assistantPanel");
  panel.hidden = !open;
  $("#assistantButton").setAttribute("aria-expanded", String(open));
  if (open) {
    renderAssistant();
    $("#assistantInput").focus();
  } else if (document.activeElement?.closest("#assistantPanel")) {
    $("#assistantButton").focus();
  }
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
  if (
    !compact && item.kind === "task" && item.assignment_state === "pending"
    && item.owner_id === selectedActor()
  ) {
    const accept = createText("button", "button primary", t("accept"));
    accept.type = "button";
    accept.addEventListener("click", () => respondToAssignment(item.id, true));
    const reject = createText("button", "delete-button", t("reject"));
    reject.type = "button";
    reject.addEventListener("click", () => respondToAssignment(item.id, false));
    actions.append(accept, reject);
  }
  if (compact && item.is_occurrence) {
    const edit = createText("button", "delete-button", t("edit"));
    edit.type = "button";
    edit.addEventListener("click", () => editOccurrence(item));
    const cancel = createText("button", "delete-button", t("cancel"));
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
  if (item.preparation) {
    card.append(createText("p", "item-preparation", `${t("preparation")}: ${item.preparation}`));
  }
  if (item.kind === "task" && item.assignment_state === "pending") {
    card.append(createText("p", "", t("pendingAssignment")));
  }

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
  if (item.reminder_at) {
    meta.append(createText("p", "", `${t("reminder")}: ${formatDateTime(item.reminder_at)}`));
  }
  meta.append(createText("p", "", `${t("createdBy")}: ${memberName(item.created_by)}`));
  card.append(meta);

  if (!compact && item.kind !== "note") {
    const controls = document.createElement("div");
    controls.className = "item-controls";

    const ownerLabel = createText("label", "", t("owner"));
    const itemOwner = document.createElement("select");
    fillMemberSelect(itemOwner, true, item.owner_id || "");
    const assignmentPending = item.kind === "task" && item.assignment_state === "pending";
    itemOwner.disabled = assignmentPending && item.owner_id === selectedActor();
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
    statusSelect.disabled = assignmentPending;
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
      ? `${dateLabel}, ${weather.description}, ${weather.temp_min}°-${weather.temp_max}°`
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
    $("#monthTitle").textContent = `${shortDate.format(start)} - ${shortDate.format(end)}`;
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
    if (error.status === 401) {
      state.board = { household: {}, members: [], items: [] };
      state.calendarItems = [];
      state.weekItems = [];
      document.querySelectorAll("dialog[open]").forEach((dialog) => dialog.close());
      accessDialog.showModal();
      return;
    }
    showToast(error.message || t("networkError"), true);
  }
}

async function loadSession() {
  try {
    const session = await api("/api/session");
    $("#logoutButton").hidden = !session.required;
    if (session.required && !session.authenticated) {
      accessDialog.showModal();
      return;
    }
    await loadBoard();
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

async function respondToAssignment(itemId, accept) {
  if (!requireActor()) return;
  try {
    state.board = await api(`/api/items/${itemId}/assignment`, {
      method: "POST",
      body: JSON.stringify({ actor_id: selectedActor(), accept }),
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
  $("#editPreparation").value = item.preparation || "";
  $("#editPreparationField").hidden = item.kind === "note";
  $("#editEventFields").hidden = item.kind !== "event";
  $("#editTaskFields").hidden = item.kind !== "task";

  if (item.kind === "event") {
    $("#editAllDay").checked = Boolean(item.all_day);
    $("#editStartDate").value = item.start_date || "";
    $("#editStartAt").value = toLocalDateTime(item.start_at);
    $("#editEndAt").value = toLocalDateTime(item.end_at);
    $("#editRecurrenceUntil").value = item.recurrence_until || "";
    $("#editEventReminderAt").value = toLocalDateTime(item.reminder_at);
  } else if (item.kind === "task") {
    $("#editDueTimed").checked = Boolean(item.due_at);
    $("#editDueDate").value = item.due_date || "";
    $("#editDueAt").value = toLocalDateTime(item.due_at);
    $("#editTaskReminderAt").value = toLocalDateTime(item.reminder_at);
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
  if (item.kind !== "note") {
    fields.preparation = scope === "occurrence"
      ? $("#editPreparation").value
      : $("#editPreparation").value || null;
  }

  if (item.kind === "event") {
    fields.reminder_at = $("#editEventReminderAt").value
      ? new Date($("#editEventReminderAt").value).toISOString() : null;
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
    fields.reminder_at = $("#editTaskReminderAt").value
      ? new Date($("#editTaskReminderAt").value).toISOString() : null;
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
  $("#intakeConfirmButton").disabled = processing;
  recordButton.disabled = processing;
  $("#submitButton").textContent = processing
    ? t("analyzing")
    : state.intake ? t("reply") : t("add");
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
    const response = await api("/api/input", {
      method: "POST",
      body: JSON.stringify({
        text: input.value,
        actor_id: selectedActor(),
        owner_id: state.intake ? null : ownerSelect.value || null,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC",
        session_id: state.intake?.session_id || null,
      }),
    });
    handleIntakeResponse(response);
  } catch (error) {
    showToast(error.message || t("networkError"), true);
  } finally {
    setProcessing(false);
  }
});

$("#intakeResetButton").addEventListener("click", resetIntake);

$("#intakeConfirmButton").addEventListener("click", async () => {
  if (!state.intake || !requireActor()) return;
  setProcessing(true);
  try {
    const ownerIds = state.intake.drafts.map((draft) =>
      draft.kind === "note" ? null : draft.owner_id || null
    );
    const acceptedPreparations = state.intake.drafts.map((draft) =>
      Boolean(draft.preparation && draft.preparation_accepted)
    );
    state.board = await api(`/api/intake/${state.intake.session_id}/confirm`, {
      method: "POST",
      body: JSON.stringify({
        actor_id: selectedActor(),
        owner_ids: ownerIds,
        accepted_preparations: acceptedPreparations,
      }),
    });
    resetIntake();
    render();
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
      body: JSON.stringify({ name: input.value, role: $("#memberRole").value }),
    });
    input.value = "";
    $("#memberRole").value = "";
    render();
    showToast(t("added"));
  } catch (error) {
    showToast(error.message || t("networkError"), true);
  }
});

$("#accessForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = $("#accessButton");
  const error = $("#accessError");
  button.disabled = true;
  button.textContent = t("unlocking");
  error.hidden = true;
  try {
    await api("/api/session", {
      method: "POST",
      body: JSON.stringify({ code: $("#accessCode").value }),
    });
    $("#accessCode").value = "";
    accessDialog.close();
    await loadSession();
  } catch (problem) {
    error.textContent = problem.status === 401 ? t("invalidAccess") : problem.message;
    error.hidden = false;
  } finally {
    button.disabled = false;
    button.textContent = t("unlock");
  }
});
accessDialog.addEventListener("cancel", (event) => event.preventDefault());
$("#logoutButton").addEventListener("click", async () => {
  await api("/api/session", { method: "DELETE" });
  localStorage.removeItem("home-actor");
  window.location.reload();
});

actorSelect.addEventListener("change", () => {
  localStorage.setItem("home-actor", actorSelect.value);
  resetIntake();
  resetAssistant();
  renderBoard();
});

$("#membersButton").addEventListener("click", () => {
  const household = state.board.household || {};
  $("#manageCity").value = household.city ? `${household.city}, ${household.country_code}` : "";
  membersDialog.showModal();
});
$("#manageCityForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    state.board = await api("/api/household", { method: "PUT", body: JSON.stringify({ city: $("#manageCity").value }) });
    state.weather = null;
    render();
    await loadWeather();
    showToast(t("updated"));
  } catch (error) {
    showToast(error.message || t("networkError"), true);
  }
});
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

$("#assistantButton").addEventListener("click", () => {
  toggleAssistant($("#assistantPanel").hidden);
});
$("#assistantCloseButton").addEventListener("click", () => toggleAssistant(false));
$("#assistantNewButton").addEventListener("click", resetAssistant);
$("#assistantPanel").addEventListener("keydown", (event) => {
  if (event.key === "Escape") toggleAssistant(false);
});
$("#assistantForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!requireActor()) return;
  const input = $("#assistantInput");
  const button = $("#assistantSendButton");
  const text = input.value.trim();
  if (!text) return;
  state.assistantPending = text;
  state.assistantError = "";
  input.disabled = true;
  button.disabled = true;
  renderAssistant();
  try {
    state.assistant = await api("/api/assistant", {
      method: "POST",
      body: JSON.stringify({
        text,
        actor_id: selectedActor(),
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC",
        session_id: state.assistant?.session_id || null,
      }),
    });
    input.value = "";
  } catch (error) {
    state.assistantError = error.message || t("networkError");
  } finally {
    state.assistantPending = "";
    input.disabled = false;
    button.disabled = false;
    renderAssistant();
    input.focus();
  }
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
      if (state.intake?.session_id) form.append("session_id", state.intake.session_id);
      setProcessing(true);
      try {
        handleIntakeResponse(
          await api("/api/audio", { method: "POST", body: form })
        );
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
loadSession();
