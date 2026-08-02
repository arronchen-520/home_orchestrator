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

        self.assertIn('id="imageInput" type="file" accept="image/png"', index)
        self.assertIn('id="imageText" rows="2" maxlength="2000"', index)
        self.assertNotIn('id="imageText" rows="2" maxlength="2000" required', index)
        self.assertIn('async function sendImage(file, text)', app)
        self.assertIn('api("/api/image", { method: "POST", body: form })', app)

    def test_settings_dialog_has_an_explicit_close_action(self):
        index = Path("frontend/index.html").read_text(encoding="utf-8")
        app = Path("frontend/app.js").read_text(encoding="utf-8")

        self.assertIn('id="settingsCloseButton"', index)
        self.assertIn('$("#settingsCloseButton").addEventListener("click", () => $("#settingsDialog").close());', app)

    def test_notification_states_are_visually_distinct(self):
        app = Path("frontend/app.js").read_text(encoding="utf-8")
        styles = Path("frontend/styles.css").read_text(encoding="utf-8")

        self.assertIn('notificationsChecking: "正在检查通知状态…"', app)
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
        self.assertIn('item.remind_member_id === state.board.current_member_id', app)
        self.assertIn('localStorage.setItem("hearthbook-task-filter", state.taskFilter)', app)

    def test_calendar_filter_uses_the_current_members_reminders(self):
        index = Path("frontend/index.html").read_text(encoding="utf-8")
        app = Path("frontend/app.js").read_text(encoding="utf-8")
        styles = Path("frontend/styles.css").read_text(encoding="utf-8")

        self.assertIn('data-calendar-filter="all"', index)
        self.assertIn('data-calendar-filter="mine"', index)
        self.assertIn('filterMine: "我的"', app)
        self.assertIn('function filteredCalendarItems()', app)
        self.assertIn('item.remind_member_id === state.board.current_member_id', app)
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


if __name__ == "__main__":
    unittest.main()
