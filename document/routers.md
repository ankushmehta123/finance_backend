# API Routers

The backend endpoints are split across routers in `app/routers/`, and each router is registered in `main.py`.

Authentication uses a Bearer token:

- UI sends: `Authorization: Bearer <access_token>`

Protected endpoints enforce RBAC using `require_roles([...])`.

## Auth Router (`app/routers/auth.py`)

- Prefix: `/auth`
- Tags: `auth`

### `POST /auth/login`

- Purpose: authenticate a user using email/password
- Request body: `LoginRequest` (`email`, `password`)
- Response: `TokenResponse` (`access_token`, `token_type="bearer"`)
- RBAC: not protected (login must be accessible without a token)

On success, the token payload includes the user id (`sub`) and the user role (`role`).

## Users Router (`app/routers/users.py`)

- Prefix: `/users`
- Tags: `users`
- RBAC: **admin only** for all endpoints in this router

### `POST /users`

- Purpose: create a new user
- Request body: `UserCreate` (`name`, `email`, `password`, `role`, `is_active`)
- Response: `UserOut`
- Responsibilities: validates unique email, stores password hash, sets role/status

### `GET /users`

- Purpose: list all users
- Response: `list[UserOut]`

### `GET /users/{user_id}`

- Purpose: fetch a single user by id
- Response: `UserOut`
- Errors: `404 User not found`

### `PATCH /users/{user_id}/role`

- Purpose: update a user’s role
- Request body: `UserRoleUpdate` (`role`)
- Response: `UserOut`
- Errors: `404 User not found`

### `PATCH /users/{user_id}/status`

- Purpose: activate/deactivate a user
- Request body: `UserStatusUpdate` (`is_active`)
- Response: `UserOut`
- Errors: `404 User not found`

## Records Router (`app/routers/records.py`)

- Prefix: `/records`
- Tags: `records`
- RBAC summary:
  - `POST`, `PATCH`, `DELETE`: **admin only**
  - `GET` endpoints: **analyst or admin**

### `POST /records`

- Purpose: create a financial record
- RBAC: admin only
- Request body: `RecordCreate`:
  - `user_id`, `amount`, `record_type` (`income`/`expense`), `category`, `record_date`, optional `notes`
- Response: `RecordOut`

### `GET /records`

- Purpose: list records with optional filters
- RBAC: analyst/admin
- Query parameters:
  - `record_type` (`income` or `expense`)
  - `category` (substring match, via `ilike`)
  - `start_date`, `end_date` (ISO dates)
- Response: `list[RecordOut]`

### `GET /records/{record_id}`

- Purpose: get a single record by id
- RBAC: analyst/admin
- Response: `RecordOut`
- Errors: `404 Record not found`

### `PATCH /records/{record_id}`

- Purpose: update an existing record
- RBAC: admin only
- Request body: `RecordUpdate` (all fields optional)
- Response: `RecordOut`
- Errors: `404 Record not found`

### `DELETE /records/{record_id}`

- Purpose: delete a record
- RBAC: admin only
- Response: `204 No Content`
- Errors: `404 Record not found`

## Dashboard Router (`app/routers/dashboard.py`)

- Prefix: `/dashboard`
- Tags: `dashboard`
- RBAC: viewer/analyst/admin can access all endpoints in this router

### `GET /dashboard/summary`

- Purpose: return total income, total expenses, and net balance
- Response: `DashboardSummaryOut`

### `GET /dashboard/category-totals`

- Purpose: return aggregated totals by `category` and `record_type`
- Response: `list[CategoryTotalOut]`

### `GET /dashboard/recent-activity`

- Purpose: return a recent list of financial records (default limit: 10)
- Query parameters:
  - `limit` (validated as `1..50`)
- Response: `list[RecentActivityOut]`

### `GET /dashboard/monthly-trends`

- Purpose: return aggregated totals grouped by month (`YYYY-MM`) and `record_type`
- Response: `list[MonthlyTrendOut]`

