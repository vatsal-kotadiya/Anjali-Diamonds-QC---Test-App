"""Persona selector — replaces login/logout with a cascading role/person picker.

Renders directly inside the sidebar where name+role used to be shown.
Returns a user dict (same shape as auth.current_user()) or None.
"""
from __future__ import annotations

import streamlit as st

from db import query_all, query_one

# Titles available under Management role
MANAGEMENT_TITLES = [
    "CEO",
    "CTO",
    "COO",
    "General Manager",
    "Manager",
    "Supervisor",
]


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

@st.cache_data(ttl=60)
def _get_departments() -> list[dict]:
    rows = query_all("SELECT id, name FROM departments ORDER BY name")
    return [dict(r) for r in rows]


@st.cache_data(ttl=60)
def _get_workers_by_dept(dept_id: int) -> list[dict]:
    rows = query_all(
        """SELECT u.id, u.name, u.emp_code
           FROM users u
           WHERE u.role = 'worker' AND u.department_id = ? AND u.status = 'active'
           ORDER BY u.name""",
        (dept_id,),
    )
    return [dict(r) for r in rows]


@st.cache_data(ttl=60)
def _get_management_users() -> list[dict]:
    rows = query_all(
        "SELECT * FROM users WHERE role = 'management' AND status = 'active' ORDER BY name"
    )
    return [dict(r) for r in rows]


@st.cache_data(ttl=60)
def _get_admin_users() -> list[dict]:
    rows = query_all(
        "SELECT * FROM users WHERE role = 'admin' AND status = 'active' ORDER BY name"
    )
    return [dict(r) for r in rows]


def _load_full_user(user_id: int) -> dict | None:
    row = query_one(
        """SELECT u.*, d.name AS department_name, p.name AS process_name
           FROM users u
           LEFT JOIN departments d ON d.id = u.department_id
           LEFT JOIN processes   p ON p.id = u.process_id
           WHERE u.id = ? AND u.status = 'active'""",
        (user_id,),
    )
    return dict(row) if row else None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render_selector() -> dict | None:
    """Render the cascading persona picker in the sidebar (top section).

    Call this INSIDE a ``with st.sidebar:`` block — it draws the 💎 header,
    the role/title/person dropdowns, and the current-user badge.

    Returns the selected user dict (same shape as auth._load_user) or None
    when nothing is selected yet.
    """

    st.markdown("### 💎 Diamond QC")

    # ── Level 1: Role ──────────────────────────────────────────────────────
    role_options = ["— select role —", "Admin", "Management", "Worker"]
    role = st.selectbox(
        "Role",
        role_options,
        key="ps_role",
        label_visibility="collapsed",
    )

    if role == "— select role —":
        st.caption("Select a role to continue ↑")
        st.session_state.pop("user", None)
        return None

    user: dict | None = None

    # ── Admin ──────────────────────────────────────────────────────────────
    if role == "Admin":
        admins = _get_admin_users()
        if not admins:
            st.warning("No admin users found. Run `python seed.py` first.")
            return None
        names = [u["name"] for u in admins]
        idx = st.selectbox(
            "Admin user",
            range(len(names)),
            format_func=lambda i: names[i],
            key="ps_admin_user",
            label_visibility="collapsed",
        )
        user = _load_full_user(admins[idx]["id"])

    # ── Management ─────────────────────────────────────────────────────────
    elif role == "Management":
        # Sub-level: title
        title = st.selectbox(
            "Title",
            MANAGEMENT_TITLES,
            key="ps_mgmt_title",
            label_visibility="collapsed",
        )

        mgmt_users = _get_management_users()
        if mgmt_users:
            names = [u["name"] for u in mgmt_users]
            idx = st.selectbox(
                "Person",
                range(len(names)),
                format_func=lambda i: names[i],
                key="ps_mgmt_user",
                label_visibility="collapsed",
            )
            user = _load_full_user(mgmt_users[idx]["id"])
        else:
            # No management users seeded yet — show a synthetic demo user
            st.caption(f"No management users in DB · showing {title} demo view")
            user = {
                "id": -1,
                "name": f"Demo {title}",
                "role": "management",
                "emp_code": None,
                "department_id": None,
                "department_name": None,
                "process_id": None,
                "process_name": None,
                "mobile": None,
                "address": None,
                "language_pref": "en",
                "status": "active",
            }

    # ── Worker ─────────────────────────────────────────────────────────────
    else:  # Worker
        depts = _get_departments()
        if not depts:
            st.warning("No departments found. Run `python seed.py` first.")
            return None

        dept_names = [d["name"] for d in depts]
        dept_idx = st.selectbox(
            "Department",
            range(len(dept_names)),
            format_func=lambda i: dept_names[i],
            key="ps_dept",
            label_visibility="collapsed",
        )
        selected_dept = depts[dept_idx]

        workers = _get_workers_by_dept(selected_dept["id"])
        if not workers:
            st.warning(f"No workers in **{selected_dept['name']}** dept yet.")
            return None

        w_labels = [
            f"{w['name']}  ({w['emp_code'] or 'no code'})" for w in workers
        ]
        w_idx = st.selectbox(
            "Worker",
            range(len(w_labels)),
            format_func=lambda i: w_labels[i],
            key="ps_worker",
            label_visibility="collapsed",
        )
        user = _load_full_user(workers[w_idx]["id"])

    # ── Persist & badge ────────────────────────────────────────────────────
    if user:
        st.session_state["user"] = user
        st.caption(f"**{user['name']}**  ·  {user['role']}")
        if user.get("emp_code"):
            st.caption(f"`{user['emp_code']}`")

    return user
