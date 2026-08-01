import os
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from backend.hearthbook import main as app_module
from fastapi.testclient import TestClient


class MembershipClient:
    def table(self, _name):
        return self

    def select(self, _columns):
        return self

    def eq(self, _key, _value):
        return self

    def execute(self):
        return SimpleNamespace(data=[{"household_id": "family"}])


class BoardStub:
    def get_board(self):
        return {
            "household": {"id": "family", "name": "Test home", "timezone": "UTC"},
            "members": [{"id": "member-1", "name": "Alice", "role": "Owner"}],
            "items": [],
            "result": None,
        }

    def get_today(self, target, _timezone):
        return {"date": target.isoformat(), "items": []}


class SupabaseAuthTest(unittest.TestCase):
    def test_authenticated_board_route_and_security_headers(self):
        with (
            patch.dict(
                os.environ,
                {
                    "SUPABASE_URL": "https://example.supabase.co",
                    "SUPABASE_PUBLISHABLE_KEY": "test-key",
                },
                clear=True,
            ),
            patch.object(
                app_module,
                "authenticate",
                return_value=(SimpleNamespace(id="user-1"), "token", None),
            ),
            patch.object(app_module, "data_client", return_value=MembershipClient()),
            patch("backend.hearthbook.api.board.board_service", return_value=BoardStub()),
            TestClient(app_module.app, base_url="https://testserver") as browser,
        ):
            response = browser.get("/api/board")
            today = browser.get("/api/today?date=2026-08-01&timezone=UTC")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["members"][0]["name"], "Alice")
        self.assertEqual(today.json()["items"], [])
        self.assertEqual(response.headers["x-frame-options"], "DENY")
        self.assertIn("default-src 'self'", response.headers["content-security-policy"])

    def test_latest_migration_keeps_rls_and_native_storage(self):
        migrations = Path("supabase/migrations")
        schema = "\n".join(
            path.read_text(encoding="utf-8") for path in sorted(migrations.glob("*.sql"))
        ).lower()
        for table in (
            "households", "household_memberships", "members", "items",
            "recurrence_exceptions", "item_notes", "conversation_sessions",
            "conversation_messages",
        ):
            self.assertIn(f"alter table public.{table} enable row level security", schema)
        latest = sorted(migrations.glob("*.sql"))[-1].read_text(encoding="utf-8").lower()
        for removed in ("owner_id", "assignment_state"):
            self.assertNotIn(removed, latest)
        for current in ("jsonb", "timestamptz", "conversation_id", "create_board_items"):
            self.assertIn(current, latest)
        self.assertIn("drop table public.submissions", latest)
        self.assertIn("conversation_sessions.household_id = items.household_id", latest)


if __name__ == "__main__":
    unittest.main()
