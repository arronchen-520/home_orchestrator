import unittest
from pathlib import Path


class NotificationDeploymentTest(unittest.TestCase):
    def test_cron_targets_the_edge_function_not_railway(self):
        migration = Path("supabase/migrations/202607310005_notifications.sql").read_text(encoding="utf-8")
        function = Path("supabase/functions/daily-notifications/index.ts").read_text(encoding="utf-8")

        self.assertIn("hearthbook_notification_edge_url", migration)
        self.assertNotIn("/internal/notifications/run", migration)
        self.assertIn("NOTIFICATION_CRON_SECRET", function)

    def test_daily_summary_skips_when_no_open_items_exist(self):
        function = Path("supabase/functions/daily-notifications/index.ts").read_text(encoding="utf-8")

        self.assertIn("summaryItems.some((item) => !item.completed_at)", function)


if __name__ == "__main__":
    unittest.main()
