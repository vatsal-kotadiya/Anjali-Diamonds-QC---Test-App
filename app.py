"""Diamond QC — Streamlit entry point.

Run:
    pip install -r requirements.txt
    python seed.py            # one-time
    streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

from persona_selector import render_selector
from db import init_db
from pwa import inject_pwa
from views import (
    admin_settings,
    admin_users,
    chatbot,
    dashboard,
    profile,
    worker_home,
)

st.set_page_config(
    page_title="Diamond QC",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="auto",
)
inject_pwa()

# Mobile-friendly CSS — bigger touch targets, hidden header on small screens.
st.markdown(
    """
    <style>
      .stButton > button { min-height: 3rem; font-size: 1rem; }
      @media (max-width: 640px) {
        .block-container { padding: 0.75rem 0.75rem 4rem; }
        header[data-testid="stHeader"] { background: transparent; }
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.25rem !important; }
      }
      /* Hide WebKit 3-dot overflow menu on audio (contains "Download"). */
      audio::-webkit-media-controls-overflow-button,
      audio::-webkit-media-controls-overflow-menu-button {
          display: none !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# Suppress the audio "Download" option globally. Streamlit's st.audio renders
# a native <audio controls>; we set controlsList="nodownload noplaybackrate"
# on every audio element, including ones added later by reruns, via a
# MutationObserver running in the parent (Streamlit main) document.
import streamlit.components.v1 as components

components.html(
    """
    <script>
      (function () {
        const doc = window.parent.document;
        const harden = (el) => {
          try {
            el.setAttribute('controlsList', 'nodownload noplaybackrate');
            el.setAttribute('disablePictureInPicture', '');
            el.setAttribute('oncontextmenu', 'return false');
          } catch (e) {}
        };
        const scan = () => doc.querySelectorAll('audio').forEach(harden);
        scan();
        const obs = new MutationObserver(scan);
        obs.observe(doc.body, { childList: true, subtree: true });
      })();
    </script>
    """,
    height=0,
)

@st.cache_resource
def cached_init_db():
    init_db()

cached_init_db()

# ----- Persona selector (replaces login) -----
with st.sidebar:
    user = render_selector()
    st.divider()
if user is None:
    st.stop()

role = user["role"]

# ----- Sidebar nav -----
with st.sidebar:

    if role == "worker":
        pages = {
            "🏠 Home": "home",
            "👤 Profile": "profile",
        }
    elif role == "management":
        pages = {
            "🏠 Home": "dashboard",
            "🤖 AI Chatbot": "chatbot",
            "👤 Profile": "profile",
        }
    else:  # admin
        pages = {
            "🏠 Home": "dashboard",
            "👥 Users": "users",
            "🛠️ Settings": "settings",
            "🤖 AI Chatbot": "chatbot",
            "👤 Profile": "profile",
        }

    labels = list(pages.keys())
    nav_label = st.radio("Navigate", labels, index=0, label_visibility="collapsed")
    nav = pages[nav_label]


# ----- Page dispatch -----
if role == "worker":
    if nav == "home":
        worker_home.render()
    elif nav == "profile":
        profile.render()
elif role == "management":
    if nav == "dashboard":
        dashboard.render()
    elif nav == "chatbot":
        chatbot.render()
    elif nav == "profile":
        profile.render()
else:  # admin
    if nav == "dashboard":
        dashboard.render()
    elif nav == "users":
        admin_users.render()
    elif nav == "settings":
        admin_settings.render()
    elif nav == "chatbot":
        chatbot.render()
    elif nav == "profile":
        profile.render()
