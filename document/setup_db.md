# Database Setup (SQLite)

This project uses SQLite for persistence and SQLAlchemy for ORM access.

## Where the SQLite database is stored

The database file is stored in the repository at:

```text
./data/finance.db
```

This is configured in `app/database.py` via:

```python
DATABASE_URL = "sqlite:///./data/finance.db"
```

## How the database schema is created

There are two related behaviors:

1. **Backend startup (FastAPI)**: `main.py` calls `Base.metadata.create_all(bind=engine)` so tables are created if they don’t exist yet.
2. **Seed/setup script**: `setup_db.py` also calls `Base.metadata.create_all(bind=engine)` and then inserts sample users and financial records.

If you only start the backend, you’ll likely have an empty database (no seed data).

## How sample/seed data is inserted

`setup_db.py` defines two seed lists:

- `users_seed`: creates demo users with the roles `admin`, `analyst`, and `viewer`
- `records_seed`: inserts sample `financial_records` rows for those users

### Demo users (seeded)

On first run, `setup_db.py` inserts the following users (passwords are hashed before storage):

| Name | Email | Role | Password |
|---|---|---|---|
| admin | `admin@example.com` | `admin` | `Admin@123` |
| analyst | `analyst@example.com` | `analyst` | `Analyst@123` |
| viewer | `viewer@example.com` | `viewer` | `Viewer@123` |

### Demo financial records (seeded)

`setup_db.py` inserts rows into the `financial_records` table using:

- `user_id` resolved from the seeded users (matched by email)
- `amount` as a decimal
- `record_type` as `"income"` or `"expense"`
- `category` as a free-text category
- `record_date` as an ISO timestamp string
- optional `notes`

## How to recreate / reset the database

`setup_db.py` is designed to **create missing tables** and **add seed data**, but it does not perform a full “drop and rebuild” reset.

Important detail:

- Users are only created if they don’t already exist (`email` is checked).
- Financial records are inserted **unconditionally** from `records_seed`.

That means: **rerunning `setup_db.py` without resetting the DB can duplicate financial records.**

### Full reset procedure

1. Stop the backend/UI (if running).
2. Delete the SQLite file:
   - `data/finance.db`
3. Re-run the seed script:

```bash
uv run python setup_db.py
```

## Verifying the database contents (optional)

The repository includes `check_db.py`, which prints:

- database file path and size
- SQLite PRAGMA information
- table names
- counts and sample rows for `users` and `financial_records`

Run it to confirm the seed data is present:

```bash
uv run python check_db.py
```

