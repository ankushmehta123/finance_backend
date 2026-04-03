# Application Structure (`app/`)

The `app/` package contains the backend building blocks: database connection/session, ORM models, Pydantic schemas, CRUD helpers, authentication logic, and request dependencies (including RBAC).

## `app/database.py`

Responsible for SQLAlchemy + SQLite configuration:

- Defines `DATABASE_URL = "sqlite:///./data/finance.db"`
- Creates the SQLAlchemy `engine`
- Enables SQLite foreign key support with a connect event:
  - `PRAGMA foreign_keys=ON;`
- Defines:
  - `SessionLocal` (session factory)
  - `Base` (SQLAlchemy declarative base)
- Provides `get_db()` which yields a request-scoped `Session` for FastAPI dependencies.

## `app/models.py`

Defines the database tables using SQLAlchemy ORM:

- `User`
  - `id`, `name`, `email` (unique), `password_hash`, `role`, `is_active`, `created_at`
  - relationship: `records`
- `FinancialRecord`
  - `id`, `user_id` (foreign key to `users.id`), `amount`, `record_type`, `category`, `record_date`, `notes`, `created_at`
  - relationship: `user`

## `app/schemas.py`

Defines Pydantic models used by FastAPI for request validation and response formatting:

- Authentication:
  - `LoginRequest`
  - `TokenResponse`
- Users:
  - `UserCreate`
  - `UserOut`
  - `UserRoleUpdate`
  - `UserStatusUpdate`
- Records:
  - `RecordCreate`
  - `RecordUpdate`
  - `RecordOut`
- Dashboard outputs:
  - `DashboardSummaryOut`
  - `CategoryTotalOut`
  - `MonthlyTrendOut`
  - `RecentActivityOut`

These schemas ensure the API response matches the documented JSON shape.

## `app/crud.py`

Contains database operations (helper functions) used by routers and services:

- Users CRUD:
  - `create_user`, `get_user_by_email`, `get_user_by_id`, `list_users`
  - `update_user_role`, `update_user_status`
- Records CRUD:
  - `create_record`, `get_record_by_id`, `list_records`, `update_record`, `delete_record`
  - `list_records` supports filtering by:
    - `record_type` (`income`/`expense`)
    - `category` (case-insensitive substring match)
    - `start_date` / `end_date` (ISO string comparisons)
- Dashboard analytics:
  - `get_summary`
  - `get_category_totals`
  - `get_monthly_trends`
  - `get_recent_activity`

## `app/auth.py`

Implements authentication and token logic:

- Password hashing:
  - `get_password_hash(password)` (salt + SHA-256)
  - `verify_password(plain_password, stored_hash)`
- Access token creation/validation:
  - `create_access_token(subject, role, expires_delta=None)`
  - `decode_access_token(token)`
  - Token payload includes `sub`, `role`, `iat`, and `exp`
- Login helper:
  - `authenticate_user(db, email, password)`
    - verifies email/password and checks `is_active`

## `app/dependencies.py`

Provides FastAPI dependencies for authentication and RBAC:

- `get_current_user(...)`
  - uses `OAuth2PasswordBearer(tokenUrl="/auth/login")`
  - decodes the token and loads the user from the database
  - denies access if user is missing or `is_active` is false
- `require_roles(allowed_roles)`
  - returns a dependency that checks `current_user.role` is permitted
  - otherwise raises `HTTP_403_FORBIDDEN` with `detail="Insufficient permissions"`

## `app/routers/` (where endpoints are defined)

Endpoint implementations are in:

- `app/routers/auth.py` (login)
- `app/routers/users.py` (user creation/management)
- `app/routers/records.py` (financial records CRUD/filtering)
- `app/routers/dashboard.py` (dashboard analytics endpoints)

`main.py` includes these routers at the application level.

