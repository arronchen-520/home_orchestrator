import json
import os
import unittest
from uuid import uuid4

import psycopg
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from app import app
from board_db import BoardDatabase


load_dotenv()


class SupabaseAuthTest(unittest.TestCase):
    def setUp(self):
        self.database_url = os.environ["DATABASE_URL"]
        self.password = f"Test-{uuid4().hex}!"
        self.users = [
            (uuid4(), f"hearthbook-{uuid4().hex}@local.invalid"),
            (uuid4(), f"hearthbook-{uuid4().hex}@local.invalid"),
        ]
        with psycopg.connect(self.database_url, autocommit=True) as connection:
            for user_id, email in self.users:
                connection.execute(
                    """
                    insert into auth.users (
                        instance_id, id, aud, role, email, encrypted_password,
                        email_confirmed_at, raw_app_meta_data, raw_user_meta_data,
                        created_at, updated_at, confirmation_token, recovery_token,
                        email_change_token_new, email_change
                    ) values (
                        '00000000-0000-0000-0000-000000000000',
                        %s, 'authenticated', 'authenticated', %s,
                        crypt(%s, gen_salt('bf')), now(),
                        '{"provider":"email","providers":["email"]}', '{}',
                        now(), now(), '', '', '', ''
                    )
                    """,
                    (user_id, email, self.password),
                )
                connection.execute(
                    """
                    insert into auth.identities (
                        provider_id, user_id, identity_data, provider,
                        created_at, updated_at
                    ) values (%s, %s, %s::jsonb, 'email', now(), now())
                    """,
                    (
                        str(user_id),
                        user_id,
                        json.dumps({"sub": str(user_id), "email": email}),
                    ),
                )

    def tearDown(self):
        with psycopg.connect(self.database_url, autocommit=True) as connection:
            connection.execute(
                """
                delete from public.households
                where id in (
                    select household_id from public.household_memberships
                    where user_id = any(%s)
                )
                """,
                ([user_id for user_id, _ in self.users],),
            )
            connection.execute(
                "delete from auth.users where id = any(%s)",
                ([user_id for user_id, _ in self.users],),
            )

    def test_login_join_and_rls_household_isolation(self):
        with (
            TestClient(app, base_url="https://testserver") as first,
            TestClient(app, base_url="https://testserver") as second,
        ):
            health = first.get("/health")
            self.assertEqual(health.status_code, 200)
            self.assertEqual(health.headers["x-frame-options"], "DENY")
            self.assertIn(
                "default-src 'self'",
                health.headers["content-security-policy"],
            )
            self.assertIn(
                "max-age=31536000",
                health.headers["strict-transport-security"],
            )
            for client, (_, email) in zip((first, second), self.users):
                response = client.post(
                    "/api/auth/login",
                    json={"email": email, "password": self.password},
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn("Secure", response.headers["set-cookie"])

            invalid_join = second.post(
                "/api/households/join",
                json={"invite_code": "NOT-A-CODE", "member_name": "Bob"},
            )
            self.assertEqual(invalid_join.status_code, 400)
            self.assertEqual(
                invalid_join.json()["detail"], "Invalid household invite"
            )

            self.assertEqual(
                first.post(
                    "/api/households",
                    json={
                        "household_name": "First home",
                        "member_name": "Alice",
                    },
                ).status_code,
                201,
            )
            first_board = first.get("/api/board").json()
            first_household_id = first_board["household"]["id"]
            invite_code = first_board["household"]["invite_code"]
            self.assertEqual(
                second.post(
                    "/api/households/join",
                    json={"invite_code": invite_code, "member_name": "Bob"},
                ).status_code,
                200,
            )
            self.assertEqual(
                {member["name"] for member in first.get("/api/board").json()["members"]},
                {"Alice", "Bob"},
            )

            second_create = first.post(
                "/api/households",
                json={
                    "household_name": "Second home",
                    "member_name": "Alice",
                },
            )
            self.assertEqual(second_create.status_code, 201, second_create.text)
            second_board = first.get("/api/board").json()
            self.assertEqual(second_board["household"]["name"], "Second home")
            session = first.get("/api/auth/session").json()
            self.assertEqual(len(session["households"]), 2)
            self.assertEqual(
                session["active_household_id"],
                second_board["household"]["id"],
            )
            self.assertEqual(
                first.post(
                    "/api/households/select",
                    json={"household_id": first_household_id},
                ).status_code,
                200,
            )
            self.assertEqual(
                first.get("/api/board").json()["household"]["id"],
                first_household_id,
            )

            hidden_household = f"test-{uuid4()}"
            with psycopg.connect(self.database_url, autocommit=True) as connection:
                connection.execute(
                    """
                    insert into public.households (
                        id, name, invite_code, created_at
                    ) values (%s, 'Hidden', %s, now()::text)
                    """,
                    (hidden_household, uuid4().hex[:12]),
                )
            try:
                self.assertEqual(
                    first.post(
                        "/api/households/select",
                        json={"household_id": hidden_household},
                    ).status_code,
                    404,
                )
                database = BoardDatabase(
                    self.database_url, str(self.users[0][0])
                )
                visible = {
                    row["id"]
                    for row in database.connection.execute(
                        "select id from households"
                    )
                }
                database.close()
                self.assertEqual(
                    visible,
                    {first_household_id, second_board["household"]["id"]},
                )
            finally:
                with psycopg.connect(
                    self.database_url, autocommit=True
                ) as connection:
                    connection.execute(
                        "delete from public.households where id = %s",
                        (hidden_household,),
                    )


if __name__ == "__main__":
    unittest.main()
