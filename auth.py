"""Authentication helpers. Plaintext passwords per MVP spec.

Sessions persist across page refreshes via a server-side `sessions` table
keyed by a UUID token stored in the URL query parameter `sid`.
"""
from __future__ import annotations

import uuid

import streamlit as st

from db import connect, query_one


def _load_user(user_id: int) -> dict | None:
    row = query_one(
        """SELECT u.*, d.name AS department_name, p.name AS process_name
           FROM users u
           LEFT JOIN departments d ON d.id = u.department_id
           LEFT JOIN processes   p ON p.id = u.process_id
           WHERE u.id = ? AND u.status = 'active'""",
        (user_id,),
    )
    return dict(row) if row else None


def login(username: str, password: str) -> dict | None:
    row = query_one(
        """SELECT u.id FROM users u
           WHERE u.username = ? AND u.password = ? AND u.status = 'active'""",
        (username, password),
    )
    if row is None:
        return None
    user = _load_user(row["id"])
    if not user:
        return None

    # Persist session in DB and surface the token in the URL so a refresh
    # re-attaches to the same session.
    token = uuid.uuid4().hex
    with connect() as c:
        c.execute(
            "INSERT INTO sessions (token, user_id) VALUES (?, ?)",
            (token, user["id"]),
        )
    st.session_state["user"] = user
    st.session_state["sid"] = token
    st.query_params["sid"] = token
    return user


def current_user() -> dict | None:
    return st.session_state.get("user")


def logout() -> None:
    token = st.session_state.get("sid") or st.query_params.get("sid")
    if token:
        with connect() as c:
            c.execute("DELETE FROM sessions WHERE token = ?", (token,))
    for k in ("user", "sid"):
        st.session_state.pop(k, None)
    try:
        st.query_params.clear()
    except Exception:
        # Fallback for older Streamlit query_params API
        st.experimental_set_query_params()


def _restore_from_token() -> dict | None:
    """If the URL carries a valid sid token, hydrate session_state from it."""
    token = st.query_params.get("sid")
    if not token:
        return None
    row = query_one("SELECT user_id FROM sessions WHERE token = ?", (token,))
    if not row:
        # Stale token (e.g. server restarted, sessions table empty). Clean it up.
        try:
            st.query_params.clear()
        except Exception:
            pass
        return None
    user = _load_user(row["user_id"])
    if not user:
        return None
    st.session_state["user"] = user
    st.session_state["sid"] = token
    return user


def require_login() -> dict | None:
    """Returns user dict if logged in, else renders login form and returns None."""
    user = current_user() or _restore_from_token()
    if user:
        return user

    st.title("Diamond QC — Sign in")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in")
    if submitted:
        u = login(username.strip(), password)
        if u:
            st.rerun()
        else:
            st.error("Invalid credentials or inactive account.")
    st.caption("Default admin: **admin / admin123**")
    return None
