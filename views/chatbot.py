"""Simple Gemini-powered chatbot for Management / Admin."""
from __future__ import annotations

import streamlit as st

import ai_clients


def render() -> None:
    st.title("🤖 AI Assistant")
    st.caption("Powered by Gemini. (MVP: no DB access — coming in next iteration.)")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask anything…")
    if not prompt:
        return

    st.session_state["chat_history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        try:
            reply = ai_clients.chat(st.session_state["chat_history"])
        except Exception as e:
            reply = f"⚠️ Gemini error: {e}"
        st.markdown(reply)
    st.session_state["chat_history"].append({"role": "assistant", "content": reply})
