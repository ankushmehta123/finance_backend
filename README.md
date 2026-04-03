# Finance Dashboard Backend

FastAPI backend APIs for a finance dashboard application, including authentication, role-based access control (RBAC), financial records CRUD, and dashboard analytics (summary, trends, and recent activity).

The Streamlit UI (`UI.py`) consumes these APIs to provide an interactive web interface.

## Features

- Authentication via `POST /auth/login` returning an access token
- Role-based access control (RBAC) for API endpoints (viewer, analyst, admin)
- User management APIs (admin-only)
- Financial records APIs with filtering (admin for write operations; analyst for read access)
- Dashboard analytics endpoints:
  - Total summary (income, expenses, net balance)
  - Category totals
  - Monthly trends
  - Recent activity feed
- SQLite database with SQLAlchemy and a seed/setup script

## Tech Stack

- Backend: FastAPI, SQLAlchemy, Pydantic, Uvicorn
- Database: SQLite (`data/finance.db`)
- Frontend UI: Streamlit (`UI.py`) + HTTP requests to the backend
- Dev tooling: `uv` for dependency syncing/running

## Prerequisites

- Python 3.12+ (see `.python-version`)
- `uv` installed
- A running backend on `http://127.0.0.1:8000` for the UI to call
- For the Streamlit UI: `streamlit` and `requests` are imported/used by `UI.py` (ensure they are available in your environment)

## Installation and setup steps

- Pull/clone the repo
- Make sure uv is installed
- Run: uv sync
- Run backend: uv run main.py
- Run frontend UI: uv run streamlit run UI.py

For first-time demo data, you should also seed the SQLite database:

```bash
uv run python setup_db.py
```

## How to run backend

```bash
uv run main.py
```

Once running, you can open:

- API root: `http://127.0.0.1:8000/`
- Swagger UI: `http://127.0.0.1:8000/docs`

## How to run frontend UI

Backend must be running first.

```bash
uv run streamlit run UI.py
```

Then open the Streamlit app in your browser (default is typically `http://127.0.0.1:8501`).

## Project structure

```text
.
├─ main.py
├─ UI.py
├─ setup_db.py
├─ check_db.py
├─ pyproject.toml
├─ uv.lock
├─ app/
│  ├─ auth.py
│  ├─ crud.py
│  ├─ database.py
│  ├─ dependencies.py
│  ├─ models.py
│  ├─ schemas.py
│  └─ routers/
│     ├─ auth.py
│     ├─ users.py
│     ├─ records.py
│     └─ dashboard.py
├─ data/
│  └─ finance.db
└─ document/
   ├─ setup_db.md
   ├─ backend_overview.md
   ├─ app_structure.md
   ├─ routers.md
   └─ frontend_ui.md
```

## Detailed documentation

Detailed backend and project documentation is available inside the `/document` folder.

- [document/](./document/)

## Troubleshooting / Notes

- Empty dashboard / no data:
  - Run the seed script: `uv run python setup_db.py`
  - If you need to fully reset data, delete `data/finance.db` and rerun the seed script.
- UI can’t load protected endpoints (401/403):
  - Log in via the Streamlit login form (the UI calls `POST /auth/login`)
  - Ensure your account role matches the API (viewer/analyst/admin).
- Streamlit dependencies missing:
  - `UI.py` imports `streamlit` and `requests`. If `uv run streamlit run UI.py` fails, add the missing dependencies to your environment (or update `pyproject.toml`) and rerun `uv sync`.
- Token security (dev note):
  - The dev token secret is hard-coded in `app/auth.py` as `local-dev-secret-change-me`. For production, replace this with a real secret (env var / configuration).
