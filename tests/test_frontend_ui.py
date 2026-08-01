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


if __name__ == "__main__":
    unittest.main()
