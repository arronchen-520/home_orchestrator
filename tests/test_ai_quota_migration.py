from pathlib import Path
import unittest


class AiQuotaMigrationTest(unittest.TestCase):
    def test_default_limits_are_backfilled_and_created_for_new_users(self):
        migration = Path("supabase/migrations/202608020006_default_ai_user_limits.sql").read_text(encoding="utf-8").lower()
        for expected in (
            "alter column daily_limit set default 5",
            "select id, 5 from auth.users",
            "create or replace function public.create_ai_user_limit",
            "drop trigger if exists create_ai_user_limit on auth.users",
            "create trigger create_ai_user_limit",
        ):
            self.assertIn(expected, migration)


if __name__ == "__main__":
    unittest.main()
