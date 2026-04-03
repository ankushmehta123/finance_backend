from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, text


def _format_row(row: Any) -> str:
    if row is None:
        return "None"
    # SQLAlchemy usually returns Row objects; str() is fine and keeps it simple.
    return str(row)


def main() -> None:
    project_root = Path(__file__).resolve().parent
    db_path = project_root / "data" / "finance.db"

    print(f"Checking database: {db_path}")
    if not db_path.exists():
        print("DB file does not exist yet.")
        print("Run: python setup_db.py")
        raise SystemExit(1)

    print(f"DB size (bytes): {db_path.stat().st_size}")

    # On Windows, SQLAlchemy expects slashes in the sqlite URL.
    database_url = f"sqlite:///{db_path.as_posix()}"
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
    )

    with engine.connect() as conn:
        print("\nSQLite PRAGMAs")
        for sql in [
            "PRAGMA foreign_keys;",
            "PRAGMA journal_mode;",
            "PRAGMA cache_size;",
            "PRAGMA synchronous;",
            "SELECT sqlite_version() AS sqlite_version;",
        ]:
            result = conn.execute(text(sql))
            row = result.fetchone()
            if row is not None:
                print(f"- {sql.strip()}: {_format_row(row[0] if len(row) == 1 else row)}")

        print("\nTables")
        tables = conn.execute(
            text(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name;
                """
            )
        ).fetchall()
        if not tables:
            print("(no user tables found)")
        else:
            for (name,) in tables:
                print(f"- {name}")

        # --- users ---
        print("\nusers")
        users_count = conn.execute(text("SELECT COUNT(*) FROM users;")).scalar_one()
        print(f"- row_count: {users_count}")

        user_sample = conn.execute(
            text(
                """
                SELECT id, name, email, role, is_active, created_at
                FROM users
                ORDER BY id
                LIMIT 10;
                """
            )
        ).fetchall()
        for r in user_sample:
            print(f"- {_format_row(r)}")

        print("\nfinancial_records")
        records_count = conn.execute(
            text("SELECT COUNT(*) FROM financial_records;")
        ).scalar_one()
        print(f"- row_count: {records_count}")

        # Record distributions
        print("\nRecord distribution")
        for sql in [
            "SELECT record_type, COUNT(*) AS cnt FROM financial_records GROUP BY record_type ORDER BY cnt DESC;",
            "SELECT category, COUNT(*) AS cnt FROM financial_records GROUP BY category ORDER BY cnt DESC LIMIT 10;",
        ]:
            rows = conn.execute(text(sql)).fetchall()
            print(f"- {sql.split(';')[0].strip()}:")
            for r in rows:
                print(f"  - {_format_row(r)}")

        # Per-user totals
        print("\nPer-user totals")
        per_user = conn.execute(
            text(
                """
                SELECT
                    u.email,
                    COUNT(fr.id) AS record_count,
                    COALESCE(SUM(fr.amount), 0) AS net_amount
                FROM users u
                LEFT JOIN financial_records fr ON fr.user_id = u.id
                GROUP BY u.id
                ORDER BY u.id;
                """
            )
        ).fetchall()
        for r in per_user:
            print(f"- {_format_row(r)}")

        # Foreign key sanity check (should return 0 rows).
        print("\nForeign key sanity check (orphan financial_records)")
        orphans = conn.execute(
            text(
                """
                SELECT fr.id
                FROM financial_records fr
                LEFT JOIN users u ON u.id = fr.user_id
                WHERE u.id IS NULL
                LIMIT 5;
                """
            )
        ).fetchall()
        if not orphans:
            print("- OK: no orphan rows found")
        else:
            print("- Found orphans:")
            for r in orphans:
                print(f"  - {_format_row(r)}")

    print("\nDone.")


if __name__ == "__main__":
    main()

