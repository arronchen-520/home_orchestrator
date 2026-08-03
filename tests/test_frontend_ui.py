import unittest
from pathlib import Path


class FrontendUIContractTest(unittest.TestCase):
    def test_text_and_screenshot_controls_share_one_row(self):
        index = Path("frontend/index.html").read_text(encoding="utf-8")
        app = Path("frontend/app.js").read_text(encoding="utf-8")
        styles = Path("frontend/styles.css").read_text(encoding="utf-8")

        self.assertIn('<div class="input-options">', index)
        self.assertLess(index.index('id="textToggle"'), index.index('class="image-toggle"'))
        self.assertIn('preferTyping: "文字输入"', app)
        self.assertIn('preferTyping: "Text input"', app)
        self.assertIn('.input-options { display: flex;', styles)

    def test_screenshot_can_send_without_an_optional_note(self):
        index = Path("frontend/index.html").read_text(encoding="utf-8")
        app = Path("frontend/app.js").read_text(encoding="utf-8")

        self.assertIn('id="imageInput" type="file" accept="image/png,.png,image/jpeg,.jpg,.jpeg"', index)
        self.assertIn('id="imageText" rows="2" maxlength="2000"', index)
        self.assertNotIn('id="imageText" rows="2" maxlength="2000" required', index)
        self.assertIn('async function sendImage(file, text)', app)
        self.assertIn('["image/png", "image/jpeg"].includes(file.type)', app)
        self.assertIn('api("/api/image", { method: "POST", body: form })', app)

    def test_conversation_input_limits_have_clear_feedback(self):
        index = Path("frontend/index.html").read_text(encoding="utf-8")
        app = Path("frontend/app.js").read_text(encoding="utf-8")

        self.assertIn('id="messageInput" rows="2" maxlength="1000"', index)
        self.assertIn('const MAX_AUDIO_BYTES = 5 * 1024 * 1024;', app)
        self.assertIn('const MAX_RECORDING_MS = 60 * 1000;', app)
        self.assertIn('messageTooLong', app)
        self.assertIn('recordingLimit', app)
        self.assertIn('audioTooLarge', app)
        self.assertIn('daily_ai_limit', app)
        self.assertIn('dailyLimit', app)

    def test_settings_dialog_has_an_explicit_close_action(self):
        index = Path("frontend/index.html").read_text(encoding="utf-8")
        app = Path("frontend/app.js").read_text(encoding="utf-8")

        self.assertIn('id="settingsCloseButton"', index)
        self.assertIn('$("#settingsCloseButton").addEventListener("click", () => $("#settingsDialog").close());', app)

    def test_settings_uses_single_open_sections_after_current_household(self):
        index = Path("frontend/index.html").read_text(encoding="utf-8")
        app = Path("frontend/app.js").read_text(encoding="utf-8")
        styles = Path("frontend/styles.css").read_text(encoding="utf-8")

        self.assertIn('class="settings-current"', index)
        self.assertLess(index.index('id="currentHouseholdTitle"'), index.index('id="profileTitle"'))
        self.assertLess(index.index('id="profileTitle"'), index.index('id="notificationTitle"'))
        self.assertLess(index.index('id="notificationTitle"'), index.index('id="membersTitle"'))
        self.assertIn('<details class="settings-details" name="settings">', index)
        self.assertIn('id="profileSummary" class="settings-summary"', index)
        self.assertIn('id="notificationSummary" class="settings-summary"', index)
        self.assertIn('id="membersSummary" class="settings-summary"', index)
        self.assertIn('id="joinAdditionalHouseholdForm"', index)
        self.assertIn('$("#joinAdditionalHouseholdForm").addEventListener("submit", async (event) => {', app)
        self.assertIn('section.addEventListener("toggle", () => {', app)
        self.assertIn('section.open = false;', app)
        self.assertIn('householdName.hidden = !household.name;', app)
        self.assertIn('.settings-details summary { min-height: 56px;', styles)

    def test_notification_states_are_visually_distinct(self):
        app = Path("frontend/app.js").read_text(encoding="utf-8")
        styles = Path("frontend/styles.css").read_text(encoding="utf-8")

        self.assertIn('notificationsChecking: "正在检查通知状态…"', app)
        self.assertIn('notificationUnavailableShort: "Unavailable"', app)
        self.assertIn('summary.textContent = t(summaryKey);', app)
        self.assertIn('status.dataset.state = "warning"', app)
        self.assertIn('status.dataset.state = state.notification.subscription ? "success" : ""', app)
        self.assertIn('button:disabled { cursor: not-allowed; opacity: .5; }', styles)

    def test_calendar_keeps_month_grid_and_only_shows_date_details_after_a_tap(self):
        index = Path("frontend/index.html").read_text(encoding="utf-8")
        app = Path("frontend/app.js").read_text(encoding="utf-8")
        styles = Path("frontend/styles.css").read_text(encoding="utf-8")

        self.assertIn('id="calendarGrid"', index)
        self.assertIn('id="calendarAgenda"', index)
        self.assertIn('calendarAgendaOpen: false', app)
        self.assertIn('agenda.hidden = !state.calendarAgendaOpen;', app)
        self.assertIn("function calendarRange()", app)
        self.assertIn("function selectCalendarDate(key)", app)
        self.assertIn('state.calendarAgendaOpen = true;', app)
        self.assertIn('.calendar-weekdays, .calendar-grid { display: grid;', styles)

    def test_tasks_precede_notes_and_are_grouped_by_due_date(self):
        index = Path("frontend/index.html").read_text(encoding="utf-8")
        app = Path("frontend/app.js").read_text(encoding="utf-8")

        self.assertIn('id="notesTitle" data-i18n="taskSpace"', index)
        self.assertLess(index.index('id="tasksTitle"'), index.index('id="notesSectionTitle"'))
        self.assertIn('id="overdueSection"', index)
        self.assertIn('id="upcomingSection"', index)
        self.assertIn('id="unscheduledSection"', index)
        self.assertIn('id="moreTasks"', index)
        self.assertIn("function taskGroups()", app)
        self.assertIn('item.kind === "task" && !item.completed_at', app)
        self.assertIn("groups.upcoming", app)
        self.assertIn("groups.unscheduled", app)

    def test_task_filter_uses_the_current_members_reminders_independently(self):
        index = Path("frontend/index.html").read_text(encoding="utf-8")
        app = Path("frontend/app.js").read_text(encoding="utf-8")

        self.assertIn('data-task-filter="all"', index)
        self.assertIn('data-task-filter="mine"', index)
        self.assertIn('taskFilter: localStorage.getItem("hearthbook-task-filter")', app)
        self.assertIn("function filteredTasks()", app)
        self.assertIn('item.remind_member_ids?.includes(state.board.current_member_id)', app)
        self.assertIn('localStorage.setItem("hearthbook-task-filter", state.taskFilter)', app)

    def test_calendar_filter_uses_the_current_members_reminders(self):
        index = Path("frontend/index.html").read_text(encoding="utf-8")
        app = Path("frontend/app.js").read_text(encoding="utf-8")
        styles = Path("frontend/styles.css").read_text(encoding="utf-8")

        self.assertIn('data-calendar-filter="all"', index)
        self.assertIn('data-calendar-filter="mine"', index)
        self.assertIn('filterMine: "我的"', app)
        self.assertIn('function filteredCalendarItems()', app)
        self.assertIn('item.remind_member_ids?.includes(state.board.current_member_id)', app)
        self.assertIn('localStorage.setItem("hearthbook-calendar-filter", state.calendarFilter)', app)
        self.assertIn('.calendar-filter-button { min-height: 44px;', styles)

    def test_calendar_uses_density_as_a_secondary_busy_signal(self):
        index = Path("frontend/index.html").read_text(encoding="utf-8")
        app = Path("frontend/app.js").read_text(encoding="utf-8")
        styles = Path("frontend/styles.css").read_text(encoding="utf-8")

        self.assertIn('data-i18n="calendarDensityHelp"', index)
        self.assertIn("function calendarSummary(items)", app)
        self.assertIn('has-density-${items.length === 1 ? "low" : items.length < 4 ? "medium" : "high"}', app)
        self.assertIn('.calendar-day.has-density-low:not(.is-selected)', styles)
        self.assertIn('.calendar-day.has-density-medium:not(.is-selected)', styles)
        self.assertIn('.calendar-day.has-density-high:not(.is-selected)', styles)

    def test_item_dialog_shows_saved_preparation_only_when_present(self):
        index = Path("frontend/index.html").read_text(encoding="utf-8")
        app = Path("frontend/app.js").read_text(encoding="utf-8")
        styles = Path("frontend/styles.css").read_text(encoding="utf-8")

        self.assertIn('id="preparationSection"', index)
        self.assertIn('id="itemPreparation"', index)
        self.assertIn('const preparation = item.preparation?.trim();', app)
        self.assertIn('$("#preparationSection").hidden = !preparation;', app)
        self.assertIn('$("#itemPreparation").textContent = preparation || "";', app)

    def test_item_dialog_shows_details_before_editing(self):
        index = Path("frontend/index.html").read_text(encoding="utf-8")
        app = Path("frontend/app.js").read_text(encoding="utf-8")
        styles = Path("frontend/styles.css").read_text(encoding="utf-8")

        self.assertIn('id="itemOverview" class="item-overview"', index)
        self.assertIn('id="itemDetails" class="item-details" hidden', index)
        self.assertIn('id="itemForm" class="item-form" hidden', index)
        self.assertIn('id="editItemButton"', index)
        self.assertIn('id="cancelItemEditButton"', index)
        self.assertIn('id="editReminderSettings" class="reminder-picker"', index)
        self.assertIn('function setItemEditing(editing)', app)
        self.assertIn('$("#itemOverview").hidden = editing;', app)
        self.assertIn('$("#itemDetails").hidden = !details;', app)
        self.assertIn('$("#itemForm").hidden = !editing;', app)
        self.assertIn('$("#editItemButton").addEventListener("click", () => {', app)
        self.assertIn('$("#cancelItemEditButton").addEventListener("click", () => {', app)
        self.assertIn('<div class="item-form-actions">', index)
        self.assertNotIn('id="itemDangerActions"', index)
        self.assertIn('id="deleteItem" class="danger-button"', index)
        self.assertIn('.item-form-actions {\n  position: sticky;', styles)
        self.assertIn('z-index: 1;', styles)
        self.assertIn('padding: 12px 20px max(20px, env(safe-area-inset-bottom));', styles)
        self.assertIn('.item-dialog-actions .quiet-button { white-space: nowrap; }', styles)
        self.assertIn('.item-form > *, .editor-section, .editor-fields, .reminder-picker, .reminder-settings-body, .reminder-settings-body > * { min-width: 0; }', styles)
        self.assertIn('.reminder-settings-body input { max-width: 100%; }', styles)

    def test_capture_confirmation_shows_schedule_and_reminder_metadata(self):
        app = Path("frontend/app.js").read_text(encoding="utf-8")

        self.assertIn("function draftMeta(draft)", app)
        self.assertIn('t("recurrence")', app)
        self.assertIn('t("reminder")', app)
        self.assertIn('const meta = draftMeta(draft);', app)
        self.assertIn('textNode("p", meta, "draft-meta")', app)

    def test_reminder_picker_is_collapsed_until_the_user_edits_it(self):
        index = Path("frontend/index.html").read_text(encoding="utf-8")
        app = Path("frontend/app.js").read_text(encoding="utf-8")
        styles = Path("frontend/styles.css").read_text(encoding="utf-8")

        self.assertIn('<details id="editRemindMemberField" class="reminder-picker">', index)
        self.assertIn('$("#editRemindMemberField").open = false;', app)
        self.assertIn('$("#editRemindMembers").addEventListener("change", updateEditReminderSummary);', app)
        self.assertIn('.reminder-picker summary { display: flex;', styles)
        self.assertIn('.item-preparation { display: grid;', styles)

    def test_item_editor_supports_preparation_and_restoring_one_occurrence(self):
        index = Path("frontend/index.html").read_text(encoding="utf-8")
        app = Path("frontend/app.js").read_text(encoding="utf-8")

        self.assertIn('id="editPreparation"', index)
        self.assertIn('id="restoreOccurrence"', index)
        self.assertIn('$("#editPreparation").value = item.preparation || "";', app)
        self.assertIn('fields.preparation = $("#editPreparation").value.trim() || null;', app)
        self.assertIn('/occurrences/${state.selectedItem.occurrence_date}/override', app)

    def test_item_dialog_can_edit_a_series_reminder_time(self):
        index = Path("frontend/index.html").read_text(encoding="utf-8")
        app = Path("frontend/app.js").read_text(encoding="utf-8")

        self.assertIn('id="editReminderAt" type="datetime-local"', index)
        self.assertIn('const reminderEditable = item.kind !== "note" && scope !== "occurrence";', app)
        self.assertIn('$("#editReminderAt").value = reminderEditable ? toLocalDateTime(item.reminder_at) : "";', app)
        self.assertIn('fields.reminder_at = $("#editReminderAt").value', app)


if __name__ == "__main__":
    unittest.main()
