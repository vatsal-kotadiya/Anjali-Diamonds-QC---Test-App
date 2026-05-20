"""Admin settings: manage Departments and Processes (admin-configurable)."""
from __future__ import annotations

from datetime import date as _date

import streamlit as st

from db import connect, query_all


def _section_departments():
    st.subheader("🏢 Departments")
    rows = query_all("SELECT id, name FROM departments ORDER BY name")
    for r in rows:
        c1, c2, c3 = st.columns([4, 2, 1])
        c1.write(r["name"])
        new_name = c2.text_input("Rename", value=r["name"], key=f"dn_{r['id']}", label_visibility="collapsed")
        if c2.button("Save", key=f"ds_{r['id']}") and new_name and new_name != r["name"]:
            with connect() as c:
                c.execute("UPDATE departments SET name = ? WHERE id = ?", (new_name, r["id"]))
            st.rerun()
        if c3.button("🗑️", key=f"dd_{r['id']}"):
            with connect() as c:
                c.execute("DELETE FROM departments WHERE id = ?", (r["id"],))
            st.rerun()

    with st.form("add_dept"):
        new = st.text_input("New department")
        if st.form_submit_button("Add department") and new:
            try:
                with connect() as c:
                    c.execute("INSERT INTO departments (name) VALUES (?)", (new,))
                st.rerun()
            except Exception as e:
                st.error(str(e))


def _section_processes():
    st.subheader("⚙️ Processes")
    rows = query_all("SELECT id, name, order_index FROM processes ORDER BY order_index, name")
    for r in rows:
        c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
        new_name = c1.text_input("Name", value=r["name"], key=f"pn_{r['id']}", label_visibility="collapsed")
        new_order = c2.number_input("Order", value=r["order_index"] or 0, key=f"po_{r['id']}", label_visibility="collapsed")
        if c3.button("Save", key=f"ps_{r['id']}"):
            with connect() as c:
                c.execute(
                    "UPDATE processes SET name = ?, order_index = ? WHERE id = ?",
                    (new_name, int(new_order), r["id"]),
                )
            st.rerun()
        if c4.button("🗑️", key=f"pd_{r['id']}"):
            with connect() as c:
                c.execute("DELETE FROM processes WHERE id = ?", (r["id"],))
            st.rerun()

    with st.form("add_proc"):
        c1, c2 = st.columns([3, 1])
        new = c1.text_input("New process name")
        order = c2.number_input("Order", value=0)
        if st.form_submit_button("Add process") and new:
            try:
                with connect() as c:
                    c.execute(
                        "INSERT INTO processes (name, order_index) VALUES (?, ?)",
                        (new, int(order)),
                    )
                st.rerun()
            except Exception as e:
                st.error(str(e))


def _section_daily_totals():
    st.subheader("💎 Daily Targets (diamonds processed per process)")
    st.caption(
        "Enter how many diamonds each process FINISHED for a given date. "
        "Used as the denominator for the dashboard's defect-rate bars."
    )

    sel_date = st.date_input("Date", value=_date.today(), key="pdt_date")
    date_iso = sel_date.isoformat()

    processes = query_all(
        "SELECT id, name FROM processes ORDER BY order_index, name"
    )
    existing = {
        r["process_id"]: r["total_diamonds"]
        for r in query_all(
            "SELECT process_id, total_diamonds FROM process_daily_totals WHERE date = ?",
            (date_iso,),
        )
    }

    with st.form(f"pdt_form_{date_iso}"):
        st.markdown(f"**Editing totals for {date_iso}**")
        new_values = {}
        for p in processes:
            current = existing.get(p["id"], 0)
            new_values[p["id"]] = st.number_input(
                p["name"], min_value=0, step=1, value=int(current), key=f"pdt_{p['id']}_{date_iso}"
            )
        if st.form_submit_button("Save totals", type="primary"):
            with connect() as c:
                for pid, total in new_values.items():
                    c.execute(
                        """INSERT INTO process_daily_totals (process_id, date, total_diamonds)
                           VALUES (?, ?, ?)
                           ON CONFLICT(process_id, date) DO UPDATE SET
                               total_diamonds = excluded.total_diamonds""",
                        (pid, date_iso, int(total)),
                    )
            st.success(f"Saved totals for {date_iso}.")
            st.rerun()


def render() -> None:
    st.title("🛠️ Settings")
    tab1, tab2, tab3 = st.tabs(["Departments", "Processes", "Daily Targets"])
    with tab1:
        _section_departments()
    with tab2:
        _section_processes()
    with tab3:
        _section_daily_totals()
