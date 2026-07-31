import os
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import app as app_module
from fastapi.testclient import TestClient

from test_support import FakeClient


class SupabaseAuthTest(unittest.TestCase):
    def test_authenticated_board_uses_supabase_data_api_without_database_url(self):
        store = {
            name: []
            for name in (
                "households",
                "household_memberships",
                "members",
                "submissions",
                "items",
                "recurrence_exceptions",
                "chat_sessions",
                "chat_messages",
            )
        }
        store["households"].append(
            {
                "id": "family",
                "name": "Test home",
                "invite_code": "TESTCODE",
                "timezone": "UTC",
                "city": None,
                "country_code": None,
                "memory": "",
            }
        )
        store["household_memberships"].append(
            {"user_id": "user-1", "household_id": "family"}
        )
        store["members"].append(
            {
                "id": "member-1",
                "household_id": "family",
                "name": "Alice",
                "role": "Owner",
                "deleted_at": None,
                "created_at": "2026-07-30T00:00:00+00:00",
            }
        )
        client = FakeClient(store)

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
            TestClient(app_module.app, base_url="https://testserver") as browser,
        ):
            response = browser.get("/api/board")
            self.assertFalse(hasattr(app_module.app.state, "database_url"))

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["household"]["name"], "Test home")
        self.assertEqual(response.json()["members"][0]["name"], "Alice")
        self.assertEqual(response.headers["x-frame-options"], "DENY")
        self.assertIn("default-src 'self'", response.headers["content-security-policy"])

    def test_data_api_migration_keeps_rls_and_limits_rpc_access(self):
        migrations = Path("supabase/migrations")
        schema = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(migrations.glob("*.sql"))
        ).lower()
        for table in (
            "households",
            "household_memberships",
            "members",
            "submissions",
            "items",
            "recurrence_exceptions",
            "chat_sessions",
            "chat_messages",
        ):
            self.assertIn(f"alter table public.{table} enable row level security", schema)
        self.assertIn(
            "grant execute on function public.create_board_items", schema
        )
        self.assertIn(
            "revoke all on function public.create_board_items", schema
        )


if __name__ == "__main__":
    unittest.main()
