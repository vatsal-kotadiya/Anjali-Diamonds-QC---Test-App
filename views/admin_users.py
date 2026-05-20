"""Admin user management: list, create, edit, delete, toggle active."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from db import connect, next_emp_code, query_all, query_one


def _all_departments():
    return query_all("SELECT id, name FROM departments ORDER BY name")


def _all_processes():
    return query_all("SELECT id, name FROM processes ORDER BY order_index, name")


def _user_table() -> pd.DataFrame:
    rows = query_all(
        """SELECT u.id, u.emp_code, u.username, u.password, u.name, u.role,
                  d.name AS department, p.name AS process,
                  u.factory_code, u.floor, u.table_no,
                  u.mobile, u.address, u.status
           FROM users u
           LEFT JOIN departments d ON d.id = u.department_id
           LEFT JOIN processes p ON p.id = u.process_id
           ORDER BY u.created_at DESC"""
    )
    return pd.DataFrame([dict(r) for r in rows])


def _create_user_form():
    st.subheader("➕ Create user")
    depts = _all_departments()
    dept_opts = {"—": None, **{d["name"]: d["id"] for d in depts}}
    procs = _all_processes()
    proc_opts = {"—": None, **{p["name"]: p["id"] for p in procs}}

    # Identity inputs first (used to suggest emp_code)
    # Bumping this counter after a successful create gives the widgets a fresh
    # key so Streamlit treats them as new (clearing their stored value).
    n = st.session_state.get("cu_reset", 0)
    col_a, col_b, col_c = st.columns(3)
    factory = col_a.text_input(
        "Factory code (3 letters)", max_chars=3, key=f"cu_factory_{n}"
    ).lower()
    floor = col_b.text_input("Floor (2 digits)", max_chars=2, key=f"cu_floor_{n}")
    table_no = col_c.text_input("Table (2 digits)", max_chars=2, key=f"cu_table_{n}")

    suggested = ""
    if factory and floor and table_no:
        try:
            suggested, _ = next_emp_code(factory, floor, table_no)
        except Exception:
            suggested = ""

    with st.form("create_user", clear_on_submit=True):
        emp_code = st.text_input(
            "Employee Code (auto-generated — editable)",
            value=suggested,
            help="Format: <factory><floor><table><count>, e.g. vaw03010001",
        )
        c1, c2 = st.columns(2)
        name = c1.text_input("Full name")
        role = c2.selectbox("Role", ["worker", "management", "admin"])
        c3, c4 = st.columns(2)
        username = c3.text_input("Username")
        password = c4.text_input("Password")
        c5, c6, c7 = st.columns(3)
        dept_name = c5.selectbox("Department", list(dept_opts.keys()))
        proc_name = c6.selectbox(
            "Process (workers only)",
            list(proc_opts.keys()),
            help="Bind a worker to one process/workstation. Their reports auto-tag this.",
        )
        mobile = c7.text_input("Mobile")
        address = st.text_area("Address", height=70)
        submitted = st.form_submit_button("Create user", type="primary")

    if not submitted:
        return

    if not all([name, username, password, factory, floor, table_no, emp_code]):
        st.error("Please fill in name, username, password, factory, floor, table, emp code.")
        return
    if role == "worker" and not proc_opts[proc_name]:
        st.error("Workers must be assigned a Process.")
        return

    # Re-derive seq from emp_code if possible (last 4 digits)
    seq = None
    if len(emp_code) >= 4 and emp_code[-4:].isdigit():
        seq = int(emp_code[-4:])

    try:
        with connect() as c:
            c.execute(
                """INSERT INTO users
                   (emp_code, factory_code, floor, table_no, seq_count,
                    username, password, name, role, department_id, process_id,
                    mobile, address)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    emp_code,
                    factory[:3].ljust(3, "x"),
                    str(floor).zfill(2),
                    str(table_no).zfill(2),
                    seq,
                    username,
                    password,
                    name,
                    role,
                    dept_opts[dept_name],
                    proc_opts[proc_name] if role == "worker" else None,
                    mobile or None,
                    address or None,
                ),
            )
        # Bump the counter so factory/floor/table widgets get fresh keys and reset
        st.session_state["cu_reset"] = n + 1
        st.toast(f"Created {name} ({emp_code})", icon="✅")
        st.rerun()
    except Exception as e:
        st.error(f"Could not create user: {e}")


def _edit_user_form(user_id: int):
    u = query_one("SELECT * FROM users WHERE id = ?", (user_id,))
    if not u:
        st.error("User not found.")
        return
    depts = _all_departments()
    dept_opts = {"—": None, **{d["name"]: d["id"] for d in depts}}
    current_dept_name = next(
        (n for n, did in dept_opts.items() if did == u["department_id"]), "—"
    )
    procs = _all_processes()
    proc_opts = {"—": None, **{p["name"]: p["id"] for p in procs}}
    current_proc_name = next(
        (n for n, pid in proc_opts.items() if pid == u["process_id"]), "—"
    )

    st.subheader(f"✏️ Edit user #{u['id']}")
    with st.form(f"edit_user_{user_id}"):
        emp_code = st.text_input("Employee Code", value=u["emp_code"] or "")
        c1, c2 = st.columns(2)
        name = c1.text_input("Full name", value=u["name"])
        role = c2.selectbox(
            "Role",
            ["worker", "management", "admin"],
            index=["worker", "management", "admin"].index(u["role"]),
        )
        c3, c4 = st.columns(2)
        username = c3.text_input("Username", value=u["username"])
        password = c4.text_input("Password", value=u["password"])
        c5, c6, c7 = st.columns(3)
        factory = c5.text_input("Factory", value=u["factory_code"] or "", max_chars=3)
        floor = c6.text_input("Floor", value=u["floor"] or "", max_chars=2)
        table_no = c7.text_input("Table", value=u["table_no"] or "", max_chars=2)
        c8, c8b, c9 = st.columns(3)
        dept_name = c8.selectbox(
            "Department",
            list(dept_opts.keys()),
            index=list(dept_opts.keys()).index(current_dept_name),
        )
        proc_name = c8b.selectbox(
            "Process (workers only)",
            list(proc_opts.keys()),
            index=list(proc_opts.keys()).index(current_proc_name),
        )
        mobile = c9.text_input("Mobile", value=u["mobile"] or "")
        address = st.text_area("Address", value=u["address"] or "", height=70)
        status = st.selectbox(
            "Status", ["active", "inactive"], index=0 if u["status"] == "active" else 1
        )
        c10, c11 = st.columns(2)
        save = c10.form_submit_button("Save changes", type="primary")
        cancel = c11.form_submit_button("Cancel")

    if cancel:
        st.session_state.pop("edit_user_id", None)
        st.rerun()
    if not save:
        return

    seq = int(emp_code[-4:]) if len(emp_code) >= 4 and emp_code[-4:].isdigit() else None
    try:
        with connect() as c:
            c.execute(
                """UPDATE users SET
                     emp_code=?, factory_code=?, floor=?, table_no=?, seq_count=?,
                     username=?, password=?, name=?, role=?, department_id=?,
                     process_id=?, mobile=?, address=?, status=?
                   WHERE id = ?""",
                (
                    emp_code,
                    (factory or "")[:3].ljust(3, "x") if factory else None,
                    str(floor).zfill(2) if floor else None,
                    str(table_no).zfill(2) if table_no else None,
                    seq,
                    username,
                    password,
                    name,
                    role,
                    dept_opts[dept_name],
                    proc_opts[proc_name] if role == "worker" else None,
                    mobile or None,
                    address or None,
                    status,
                    user_id,
                ),
            )
        st.success("User updated.")
        st.session_state.pop("edit_user_id", None)
        st.rerun()
    except Exception as e:
        st.error(f"Update failed: {e}")


def render() -> None:
    st.title("👥 User Management")

    if "edit_user_id" in st.session_state:
        _edit_user_form(st.session_state["edit_user_id"])
        st.divider()

    df = _user_table()

    # Filters
    f1, f2, f3, f4 = st.columns([2, 2, 2, 3])
    role_f = f1.selectbox("Role", ["All", "admin", "management", "worker"])
    status_f = f2.selectbox("Status", ["All", "active", "inactive"])
    dept_f = f3.selectbox("Department", ["All"] + sorted({d for d in df["department"].dropna()}))
    q = f4.text_input("Search (name / username / emp code)")

    view = df.copy()
    if role_f != "All":
        view = view[view["role"] == role_f]
    if status_f != "All":
        view = view[view["status"] == status_f]
    if dept_f != "All":
        view = view[view["department"] == dept_f]
    if q:
        ql = q.lower()
        view = view[
            view.apply(
                lambda r: ql in str(r["name"]).lower()
                or ql in str(r["username"]).lower()
                or ql in str(r["emp_code"] or "").lower(),
                axis=1,
            )
        ]

    st.dataframe(
        view.drop(columns=["id"], errors="ignore"),
        use_container_width=True,
        hide_index=True,
    )

    # Inline per-row actions — one compact strip per user under the table
    st.markdown("### Row actions")
    if view.empty:
        st.caption("No users match filters.")
    else:
        for _, r in view.iterrows():
            uid = int(r["id"])
            c1, c2, c3, c4 = st.columns([6, 2, 1, 1])
            c1.markdown(
                f"`{r['emp_code'] or '—'}` &nbsp; **{r['name']}** "
                f"<span style='color:#888'>({r['username']} · {r['role']})</span>",
                unsafe_allow_html=True,
            )
            is_active = r["status"] == "active"
            if c2.button(
                "🟢 Active" if is_active else "🔴 Inactive",
                key=f"toggle_{uid}",
                help="Click to flip status",
                use_container_width=True,
            ):
                with connect() as c:
                    c.execute(
                        "UPDATE users SET status = CASE status "
                        "WHEN 'active' THEN 'inactive' ELSE 'active' END WHERE id = ?",
                        (uid,),
                    )
                st.rerun()
            if c3.button("✏️", key=f"edit_{uid}", help="Edit user", use_container_width=True):
                st.session_state["edit_user_id"] = uid
                st.rerun()
            if c4.button(
                "🗑️", key=f"del_{uid}", help="Delete user", use_container_width=True
            ):
                with connect() as c:
                    c.execute("DELETE FROM users WHERE id = ?", (uid,))
                st.toast(f"Deleted {r['name']}")
                st.rerun()

    st.divider()
    _create_user_form()
