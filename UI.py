import streamlit as st
import requests
import base64
import json
from datetime import date


API_BASE_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Finance Dashboard",
    page_icon="💰",
    layout="wide",
)


def init_session_state() -> None:
    defaults = {
        "access_token": None,
        "logged_in": False,
        "role": None,
        "email": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def decode_jwt_payload(token: str) -> dict | None:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        payload_b64 = parts[1]
        padding = "=" * ((4 - len(payload_b64) % 4) % 4)
        payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
        return json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        return None


def get_auth_headers() -> dict[str, str]:
    token = st.session_state.get("access_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def api_request(method: str, endpoint: str, **kwargs):
    url = f"{API_BASE_URL}{endpoint}"
    headers = kwargs.pop("headers", {})
    headers.update(get_auth_headers())
    try:
        response = requests.request(method, url, headers=headers, timeout=20, **kwargs)
        return response
    except requests.RequestException as exc:
        st.error(f"API request failed: {exc}")
        return None


def login_page() -> None:
    st.title("Finance Dashboard Login")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        payload = {"email": email, "password": password}
        response = api_request("POST", "/auth/login", json=payload)

        if response is None:
            return

        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]

            st.session_state["access_token"] = token
            st.session_state["logged_in"] = True
            st.session_state["email"] = email

            claims = decode_jwt_payload(token)
            if claims:
                st.session_state["role"] = claims.get("role")

            st.success("Login successful")
            st.rerun()
        else:
            try:
                detail = response.json().get("detail", "Login failed")
            except Exception:
                detail = "Login failed"
            st.error(detail)


def logout() -> None:
    st.session_state["access_token"] = None
    st.session_state["logged_in"] = False
    st.session_state["role"] = None
    st.session_state["email"] = None
    st.rerun()


def dashboard_page() -> None:
    st.header("Dashboard")

    summary_response = api_request("GET", "/dashboard/summary")
    category_response = api_request("GET", "/dashboard/category-totals")
    trends_response = api_request("GET", "/dashboard/monthly-trends")
    recent_response = api_request("GET", "/dashboard/recent-activity")

    if summary_response and summary_response.status_code == 200:
        summary = summary_response.json()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Income", summary["total_income"])
        col2.metric("Total Expenses", summary["total_expenses"])
        col3.metric("Net Balance", summary["net_balance"])
    else:
        st.warning("Could not load dashboard summary.")

    st.subheader("Category Totals")
    if category_response and category_response.status_code == 200:
        category_data = category_response.json()
        if category_data:
            st.dataframe(category_data, use_container_width=True)
        else:
            st.info("No category totals found.")
    else:
        st.warning("Could not load category totals.")

    st.subheader("Monthly Trends")
    if trends_response and trends_response.status_code == 200:
        trend_data = trends_response.json()
        if trend_data:
            st.dataframe(trend_data, use_container_width=True)
        else:
            st.info("No monthly trend data found.")
    else:
        st.warning("Could not load monthly trends.")

    st.subheader("Recent Activity")
    if recent_response and recent_response.status_code == 200:
        recent_data = recent_response.json()
        if recent_data:
            st.dataframe(recent_data, use_container_width=True)
        else:
            st.info("No recent activity found.")
    else:
        st.warning("Could not load recent activity.")


def records_page() -> None:
    st.header("Financial Records")

    with st.expander("Filter Records", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            record_type = st.selectbox("Record Type", ["", "income", "expense"])
        with col2:
            category = st.text_input("Category")
        with col3:
            start_date = st.date_input("Start Date", value=None)
        with col4:
            end_date = st.date_input("End Date", value=None)

    params = {}
    if record_type:
        params["record_type"] = record_type
    if category:
        params["category"] = category
    if start_date:
        params["start_date"] = start_date.isoformat()
    if end_date:
        params["end_date"] = end_date.isoformat()

    response = api_request("GET", "/records", params=params)

    if response is None:
        return

    if response.status_code == 200:
        records = response.json()
        st.dataframe(records, use_container_width=True)
    else:
        try:
            detail = response.json().get("detail", "Failed to load records")
        except Exception:
            detail = "Failed to load records"
        st.error(detail)


def create_record_page() -> None:
    st.header("Create Record")

    with st.form("create_record_form"):
        user_id = st.number_input("User ID", min_value=1, step=1)
        amount = st.number_input("Amount", min_value=0.01, step=0.01, format="%.2f")
        record_type = st.selectbox("Record Type", ["income", "expense"])
        category = st.text_input("Category")
        record_date = st.date_input("Record Date", value=date.today())
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Create Record")

    if submitted:
        payload = {
            "user_id": int(user_id),
            "amount": str(amount),
            "record_type": record_type,
            "category": category,
            "record_date": record_date.isoformat(),
            "notes": notes or None,
        }
        response = api_request("POST", "/records", json=payload)

        if response is None:
            return

        if response.status_code in (200, 201):
            st.success("Record created successfully")
            st.json(response.json())
        else:
            try:
                detail = response.json().get("detail", "Failed to create record")
            except Exception:
                detail = "Failed to create record"
            st.error(detail)


def users_page() -> None:
    st.header("Users")

    response = api_request("GET", "/users")
    if response is None:
        return

    if response.status_code == 200:
        users = response.json()
        st.dataframe(users, use_container_width=True)
    else:
        try:
            detail = response.json().get("detail", "Failed to load users")
        except Exception:
            detail = "Failed to load users"
        st.error(detail)
        return

    st.subheader("Create User")
    with st.form("create_user_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["viewer", "analyst", "admin"])
        is_active = st.checkbox("Is Active", value=True)
        submitted = st.form_submit_button("Create User")

    if submitted:
        payload = {
            "name": name,
            "email": email,
            "password": password,
            "role": role,
            "is_active": is_active,
        }
        response = api_request("POST", "/users", json=payload)

        if response is None:
            return

        if response.status_code in (200, 201):
            st.success("User created successfully")
            st.json(response.json())
        else:
            try:
                detail = response.json().get("detail", "Failed to create user")
            except Exception:
                detail = "Failed to create user"
            st.error(detail)


def main() -> None:
    init_session_state()

    if not st.session_state["logged_in"]:
        login_page()
        return

    role = st.session_state.get("role")

    st.sidebar.title("Navigation")
    st.sidebar.markdown(f"**Logged in as:** {st.session_state.get('email', '')}")
    st.sidebar.markdown(f"**Role:** {role or 'unknown'}")

    if role == "admin":
        pages = ["Dashboard", "Records", "Create Record", "Users"]
    elif role == "analyst":
        pages = ["Dashboard", "Records"]
    elif role == "viewer":
        pages = ["Dashboard"]
    else:
        pages = ["Dashboard"]

    page = st.sidebar.radio("Go to", pages)

    if st.sidebar.button("Logout"):
        logout()

    if page == "Dashboard":
        dashboard_page()
    elif page == "Records":
        records_page()
    elif page == "Create Record":
        create_record_page()
    elif page == "Users":
        users_page()


if __name__ == "__main__":
    main()