"""Shared profile page (worker / management / admin)."""
from __future__ import annotations

import streamlit as st

from auth import current_user, logout
from db import connect
from i18n import t


def render() -> None:
    user = current_user()
    st.title(t("profile"))

    st.markdown(f"**Name:** {user['name']}")
    if user.get("emp_code"):
        st.markdown(f"**Employee Code:** `{user['emp_code']}`")
    st.markdown(f"**Username:** {user['username']}")
    st.markdown(f"**Role:** {user['role'].title()}")
    st.markdown(f"**Department:** {user.get('department_name') or '—'}")
    if user["role"] == "worker":
        st.markdown(f"**Process:** {user.get('process_name') or '—'}")
    st.markdown(f"**Mobile:** {user.get('mobile') or '—'}")
    st.markdown(f"**Address:** {user.get('address') or '—'}")

    st.divider()
    st.subheader(t("language"))
    new_lang = st.radio(
        " ",
        options=["en", "gu"],
        index=0 if (user.get("language_pref") or "en") == "en" else 1,
        format_func=lambda c: "English" if c == "en" else "ગુજરાતી",
        horizontal=True,
        label_visibility="collapsed",
    )
    if new_lang != user.get("language_pref"):
        with connect() as c:
            c.execute("UPDATE users SET language_pref = ? WHERE id = ?", (new_lang, user["id"]))
        st.session_state["user"]["language_pref"] = new_lang
        st.rerun()

    st.divider()
    if st.button(t("logout"), type="primary"):
        logout()
        st.rerun()
