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


class JoinClient(MembershipClient):
    def rpc(self, name, payload):
        self.rpc_call = (name, payload)
        return self

    def execute(self):
        return SimpleNamespace(data="family") if hasattr(self, "rpc_call") else super().execute()


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
    def test_join_passes_member_role_to_supabase(self):
        client = JoinClient()
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
            patch.object(app_module, "data_client", return_value=client),
            patch("backend.hearthbook.api.auth.data_client", return_value=client),
            TestClient(app_module.app, base_url="https://testserver") as browser,
        ):
            response = browser.post(
                "/api/households/join",
                json={"invite_code": "ABC", "member_name": "Sam", "member_role": "Driver"},
            )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(
            client.rpc_call,
            (
                "join_household",
                {
                    "household_invite_code": "ABC",
                    "member_name": "Sam",
                    "member_role": "Driver",
                },
            ),
        )

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
            "conversation_messages", "push_subscriptions", "notification_deliveries",
        ):
            self.assertIn(f"alter table public.{table} enable row level security", schema)
        storage = (migrations / "202607310002_simplify_storage.sql").read_text(encoding="utf-8").lower()
        for removed in ("owner_id", "assignment_state"):
            self.assertNotIn(removed, storage)
        for current in ("jsonb", "timestamptz", "conversation_id", "create_board_items"):
            self.assertIn(current, storage)
        self.assertIn("drop table public.submissions", storage)
        self.assertIn("conversation_sessions.household_id = items.household_id", storage)
        identity = (migrations / "202607310003_account_member_identity.sql").read_text(encoding="utf-8").lower()
        self.assertIn("members_household_user_unique", identity)
        self.assertIn("members_household_read", identity)
        join_role = (migrations / "202607310004_join_member_role.sql").read_text(encoding="utf-8").lower()
        self.assertIn("member_role text", join_role)
        self.assertIn("member_role, now_text", join_role)
        notifications = (migrations / "202607310005_notifications.sql").read_text(encoding="utf-8").lower()
        self.assertIn("'* * * * *'", notifications)
        self.assertIn("claim_notification_delivery", notifications)
        self.assertIn("x-notification-cron-secret", notifications)
        self.assertIn("timeout_milliseconds := 30000", notifications)


if __name__ == "__main__":
    unittest.main()
