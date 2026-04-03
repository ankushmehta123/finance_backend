# Backend Overview

This backend is a small FastAPI application that exposes JSON APIs for:

- Authentication (login -> access token)
- User management (admin only)
- Financial records CRUD and filtering
- Dashboard analytics (summary, category totals, monthly trends, recent activity)

## High-level architecture

The main pieces live in `main.py` and the `app/` package:

- `main.py`: creates the FastAPI app, configures middleware/CORS, and includes routers
- `app/database.py`: SQLAlchemy engine/session + SQLite configuration
- `app/models.py`: ORM models (tables)
- `app/schemas.py`: Pydantic request/response models
- `app/crud.py`: database operations and dashboard aggregation queries
- `app/auth.py`: password hashing and token creation/validation
- `app/dependencies.py`: authentication (`get_current_user`) and RBAC enforcement (`require_roles`)
- `app/routers/*`: endpoint definitions (auth/users/records/dashboard)

## What `main.py` does

`main.py` is the entrypoint that builds the FastAPI server:

1. Configures logging.
2. Creates database tables on startup:
   - `Base.metadata.create_all(bind=engine)`
3. Creates the FastAPI app:
   - title/description/version
4. Adds CORS middleware for local development UI origins.
5. Registers routers:
   - `app.include_router(auth.router)`
   - `app.include_router(users.router)`
   - `app.include_router(records.router)`
   - `app.include_router(dashboard.router)`
6. Adds a middleware that logs request method/path and response status.
7. Adds a simple root endpoint:
   - `GET /` returns `{"message": "Finance backend is running"}`
8. If run directly, starts Uvicorn on `127.0.0.1:8000` with `reload=True`.

## FastAPI request flow (end-to-end)

For a typical API call, the flow is:

1. **FastAPI matches a route** in one of the routers under `app/routers/`.
2. **Dependencies execute** (when declared on the endpoint):
   - `get_db` provides a SQLAlchemy `Session`
   - `oauth2_scheme` extracts the `Authorization: Bearer ...` token
   - `get_current_user` decodes the token, loads the user, and checks `is_active`
   - `require_roles([...])` verifies the user’s role is allowed for that endpoint
3. **Route handler runs**:
   - calls functions in `app/crud.py` for DB reads/writes and analytics queries
   - or calls `app/auth.py` for login / token creation
4. **Response model validation/serialization**:
   - endpoint `response_model=...` ensures the output matches the expected schema
5. **Middleware logs** the request outcome.

## Authentication and role-based access control (RBAC)

### How authentication works

- The client logs in using `POST /auth/login` with:
  - `email`
  - `password`
- `app/auth.py` verifies the user:
  - fetches by email (`crud.get_user_by_email`)
  - checks the password hash
  - checks `user.is_active`
- If valid, the backend issues an access token that includes:
  - `sub`: user id (as a string)
  - `role`: one of `admin`, `analyst`, `viewer`
  - `exp`: expiration timestamp

The UI sends this token on subsequent requests as:

- `Authorization: Bearer <access_token>`

### How RBAC is enforced

`app/dependencies.py` provides:

- `get_current_user(...)`: decodes token and loads the active user
- `require_roles(allowed_roles)`: ensures `current_user.role` is in `allowed_roles`

RBAC is applied per endpoint via:

- `dependencies=[Depends(require_roles([...]))]`

In practice:

- `admin` can create/update users and manage records
- `analyst` can view records and access dashboard endpoints
- `viewer` can access dashboard endpoints but cannot manage records/users

## Notes about dev security

`app/auth.py` uses a hard-coded dev token secret (`SECRET_KEY = "local-dev-secret-change-me"`).
For production, this should be moved to environment configuration and rotated.

