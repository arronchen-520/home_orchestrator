import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import SESSION_COOKIE, app


class HouseholdAccessTest(unittest.TestCase):
    def test_access_codes_isolate_households(self):
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict(
            os.environ,
            {
                "BOARD_DB_PATH": str(Path(temp_dir) / "test.sqlite3"),
                "HOUSEHOLD_CODES_JSON": json.dumps(
                    {"family-a": "family-a-code", "family-b": "family-b-code"}
                ),
                "SESSION_SECRET": "test-secret-that-is-at-least-32-characters",
            },
        ):
            with TestClient(app) as client:
                self.assertEqual(client.get("/api/board").status_code, 401)
                client.cookies.set(SESSION_COOKIE, "tampered")
                self.assertEqual(client.get("/api/board").status_code, 401)
                client.cookies.clear()

                self.assertEqual(
                    client.post(
                        "/api/session", json={"code": "family-a-code"}
                    ).status_code,
                    200,
                )
                self.assertEqual(
                    client.post(
                        "/api/members", json={"name": "Alice", "role": ""}
                    ).status_code,
                    201,
                )

                client.delete("/api/session")
                client.post("/api/session", json={"code": "family-b-code"})
                self.assertEqual(client.get("/api/board").json()["members"], [])
                client.post("/api/members", json={"name": "Bob", "role": ""})

                client.delete("/api/session")
                client.post("/api/session", json={"code": "family-a-code"})
                self.assertEqual(
                    [member["name"] for member in client.get("/api/board").json()["members"]],
                    ["Alice"],
                )


if __name__ == "__main__":
    unittest.main()
