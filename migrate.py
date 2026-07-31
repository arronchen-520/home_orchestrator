import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


load_dotenv()


def main() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")
    migrations = sorted(
        (Path(__file__).parent / "supabase" / "migrations").glob("*.sql")
    )
    with psycopg.connect(database_url, autocommit=True) as connection:
        for migration in migrations:
            connection.execute(migration.read_text(encoding="utf-8"))
            print(f"Applied {migration.name}")


if __name__ == "__main__":
    main()
