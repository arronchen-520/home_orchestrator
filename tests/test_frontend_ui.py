import unittest
from pathlib import Path


class FrontendUIContractTest(unittest.TestCase):
    def test_notification_states_are_visually_distinct(self):
        app = Path("frontend/app.js").read_text(encoding="utf-8")
        styles = Path("frontend/styles.css").read_text(encoding="utf-8")

        self.assertIn('notificationsChecking: "正在检查通知状态…"', app)
        self.assertIn('status.dataset.state = "warning"', app)
        self.assertIn('status.dataset.state = state.notification.subscription ? "success" : ""', app)
        self.assertIn('button:disabled { cursor: not-allowed; opacity: .5; }', styles)

    def test_calendar_keeps_month_grid_and_unscheduled_tasks_with_notes(self):
        index = Path("frontend/index.html").read_text(encoding="utf-8")
        app = Path("frontend/app.js").read_text(encoding="utf-8")
        styles = Path("frontend/styles.css").read_text(encoding="utf-8")

        self.assertIn('id="calendarGrid"', index)
        self.assertIn('id="agendaTitle"', index)
        self.assertGreater(index.index('id="unscheduledSection"'), index.index('id="notesView"'))
        self.assertIn("function calendarRange()", app)
        self.assertIn("function selectCalendarDate(key)", app)
        self.assertIn('const unscheduledItems = state.board.items.filter', app)
        self.assertIn('.calendar-weekdays, .calendar-grid { display: grid;', styles)


if __name__ == "__main__":
    unittest.main()
