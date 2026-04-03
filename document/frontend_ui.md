# Frontend UI (`UI.py`) - Streamlit

The frontend is a Streamlit app defined in `UI.py`. It provides:

- Login page (email/password -> access token)
- Role-based navigation (Dashboard / Records / Users)
- Views that call the backend APIs over HTTP

## How Streamlit interacts with FastAPI

`UI.py` communicates with the backend using Python’s `requests` library:

- Backend base URL:
  - `API_BASE_URL = "http://127.0.0.1:8000"`
- Helper function:
  - `api_request(method, endpoint, **kwargs)` builds:
    - `url = f"{API_BASE_URL}{endpoint}"`
    - sends `Authorization: Bearer <token>` when `st.session_state["access_token"]` exists

Protected endpoints will return `401`/`403` if the token is missing/invalid or the user role is not allowed.

## Authentication flow (token handling)

1. `init_session_state()` initializes session values:
   - `access_token`, `logged_in`, `role`, `email`
2. `login_page()` shows an HTML form and calls:
   - `POST /auth/login` with JSON: `{"email": ..., "password": ...}`
3. On success:
   - saves `access_token` into `st.session_state["access_token"]`
   - sets `logged_in = True`
   - decodes the JWT payload locally to extract `role` for UI navigation
4. Subsequent API calls include:
   - `Authorization: Bearer <access_token>`

Note: the UI decodes the token payload for navigation, but the backend still enforces RBAC on every protected endpoint.

## UI workflow (what each page does)

### 1. Login gate

- If `st.session_state["logged_in"]` is `False`, the UI only shows the login form.

### 2. Sidebar navigation based on role

After login, `main()` builds a page list based on `st.session_state["role"]`:

- `admin`: `Dashboard`, `Records`, `Create Record`, `Users`
- `analyst`: `Dashboard`, `Records`
- `viewer`: `Dashboard`

### 3. Dashboard page

`dashboard_page()` calls these backend endpoints:

- `GET /dashboard/summary`
- `GET /dashboard/category-totals`
- `GET /dashboard/monthly-trends`
- `GET /dashboard/recent-activity`

It renders:

- metrics for totals
- dataframes for the aggregated lists

### 4. Records page (filter + list)

`records_page()`:

- collects optional filters (record type, category, start date, end date)
- calls:
  - `GET /records` with those query parameters
- displays the result as a dataframe

### 5. Create Record page

`create_record_page()`:

- collects record fields (including `user_id`)
- calls:
  - `POST /records` with JSON payload
- on success shows returned record details

### 6. Users page (admin only)

`users_page()`:

- calls:
  - `GET /users` to show the users list
- provides a “Create User” form that calls:
  - `POST /users` with `name`, `email`, `password`, `role`, `is_active`

## How to run the UI

Backend must be running first.

```bash
uv run streamlit run UI.py
```

Streamlit will start a local web server (commonly on `http://127.0.0.1:8501`).

## Quick start with seeded demo accounts

If you ran `setup_db.py`, you can log in with the demo users seeded by `setup_db.py`:

- `admin@example.com` / `Admin@123`
- `analyst@example.com` / `Analyst@123`
- `viewer@example.com` / `Viewer@123`

