import atexit
import os
from pathlib import Path
from uuid import uuid4

import psycopg
from dotenv import load_dotenv
from psycopg import sql
from psycopg.rows import dict_row

from board_db import BoardDatabase, QmarkCursor


load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]
SCHEMAS: dict[str, str] = {}


class TestBoardDatabase(BoardDatabase):
    __test__ = False

    def __init__(self, path: str | Path):
        key = str(Path(path).resolve())
        self.schema = SCHEMAS.setdefault(key, f"test_{uuid4().hex}")
        self.connection = psycopg.connect(
            DATABASE_URL,
            autocommit=True,
            row_factory=dict_row,
            cursor_factory=QmarkCursor,
            prepare_threshold=None,
        )
        self.connection.execute(
            sql.SQL("create schema if not exists {}").format(
                sql.Identifier(self.schema)
            )
        )
        self.connection.execute(
            sql.SQL("set search_path to {}").format(sql.Identifier(self.schema))
        )

    def setup(self) -> None:
        migration = next(
            (Path(__file__).parent / "supabase" / "migrations").glob("*.sql")
        ).read_text(encoding="utf-8")
        tables = migration[
            migration.index("create table if not exists public.households"):
            migration.index(
                "create or replace function private.is_household_member"
            )
        ].replace("public.", f'"{self.schema}".')
        self.connection.execute(tables)

    def ensure_household(
        self, household_id: str, timezone_name: str = "UTC"
    ) -> None:
        self.connection.execute(
            """
            insert into households (
                id, name, invite_code, timezone, created_at
            ) values (?, ?, ?, ?, now()::text)
            on conflict(id) do nothing
            """,
            (household_id, household_id, uuid4().hex[:12], timezone_name),
        )


@atexit.register
def cleanup_test_schemas() -> None:
    if not SCHEMAS:
        return
    with psycopg.connect(DATABASE_URL, autocommit=True) as connection:
        for schema in set(SCHEMAS.values()):
            connection.execute(
                sql.SQL("drop schema if exists {} cascade").format(
                    sql.Identifier(schema)
                )
            )
