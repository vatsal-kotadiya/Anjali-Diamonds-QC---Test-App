"""Worker home page: two toggle buttons + inline report form + history."""
from __future__ import annotations

import uuid
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

import streamlit as st

import ai_clients
from auth import current_user
from db import AUDIO_DIR, connect, query_all
import streamlit.components.v1 as components
import base64
import threading
from i18n import t

import os
# Declare the custom component using an absolute path to avoid loading issues
COMPONENT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "components", "live_recorder")
_live_recorder = components.declare_component(
    "live_recorder",
    path=COMPONENT_DIR
)

def live_recorder(key=None, **kwargs):
    return _live_recorder(key=key, default=None, **kwargs)


CORRELATION_WINDOW_HOURS = 72


# ---------------------------------------------------------------------------
# Helpers (adapted from worker_report.py)
# ---------------------------------------------------------------------------

def _candidate_links(diamond_id: str, exclude_report_id: int | None = None) -> list[dict]:
    cutoff = (datetime.utcnow() - timedelta(hours=CORRELATION_WINDOW_HOURS)).isoformat(" ")
    rows = query_all(
        """SELECT r.id, r.report_type, u.name AS worker, a.transcript_english AS transcript
           FROM reports r
           JOIN users u ON u.id = r.worker_id
           LEFT JOIN audio_files a ON a.report_id = r.id
           WHERE r.diamond_id = ? AND r.created_at >= ?
             AND (? IS NULL OR r.id != ?)
           ORDER BY r.created_at DESC
           LIMIT 10""",
        (diamond_id, cutoff, exclude_report_id, exclude_report_id),
    )
    return [dict(r) for r in rows]


@st.fragment
def _render_report_form(user: dict, report_type: str) -> None:
    """Render the inline report submission form."""
    title = t("receive_report") if report_type == "receive" else t("problem_report")
    icon = "📥" if report_type == "receive" else "⚠️"

    st.markdown(f"#### {icon} {title}")

    if not user.get("process_id"):
        st.error("Your profile is not linked to a process. Ask the admin to assign one.")
        return

    proc_id = user["process_id"]
    proc_name = user.get("process_name") or "—"

    st.info(f"{t('process')}: **{proc_name}**  (from your profile)")

    # ---- Custom CSS: compact diamond ID + square-card audio recorder button ----
    st.markdown(
        """
        <style>
        /* Compact diamond-ID input */
        div[data-testid="stTextInput"] input {
            font-size: 0.9rem;
            padding: 0.35rem 0.6rem;
            border-radius: 8px;
        }


        /* Submit button full-width */
        div[data-testid="stButton"] > button[kind="primary"] {
            width: 100%;
            min-height: 3rem;
            font-size: 1rem;
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---- Diamond ID — compact single-line input ----
    col_id, _ = st.columns([2, 3])
    with col_id:
        diamond_id = st.text_input(
            t("diamond_id"),
            max_chars=64,
            placeholder="e.g. D-00123",
            label_visibility="visible",
            key=f"diamond_id_{report_type}",
        ).strip()

    st.markdown("---")

    # ---- Audio recorder (custom component with pre-warmed mic for instant start) ----
    st.markdown(
        "<p style='text-align:center; color:gray; font-size:0.85rem; margin: 0.5rem 0'>"
        + t("record_audio") + "</p>",
        unsafe_allow_html=True,
    )
    _, col_mic, _ = st.columns([1, 1.5, 1])
    with col_mic:
        recorder_data = live_recorder(key=f"live_recorder_{report_type}")

    audio = None
    if recorder_data and isinstance(recorder_data, dict):
        audio_b64 = recorder_data.get("audio", "")
        if audio_b64:
            audio_bytes = base64.b64decode(audio_b64)
            class _MockAudio:
                def __init__(self, b): self.b = b
                def getvalue(self): return self.b
            audio = _MockAudio(audio_bytes)

    gu_key = f"trans_gu_{report_type}"
    en_key = f"trans_en_{report_type}"
    hash_key = f"audio_hash_{report_type}"
    if not audio:
        for k in [gu_key, en_key, hash_key]:
            if k in st.session_state:
                del st.session_state[k]
    else:
        # Detect a NEW recording (audio bytes changed since last run) and
        # transcribe once — show the transcript so the worker can verify
        # before submitting.
        current_hash = hashlib.md5(audio.getvalue()).hexdigest()
        if st.session_state.get(hash_key) != current_hash:
            st.session_state[hash_key] = current_hash
            temp_path = AUDIO_DIR / f"temp_{uuid.uuid4().hex}.webm"
            temp_path.write_bytes(audio.getvalue())
            try:
                with st.spinner(t("transcribing")):
                    gu, en = ai_clients.process_audio_full(temp_path)
                st.session_state[gu_key] = gu
                st.session_state[en_key] = en
            except Exception as e:
                st.warning(f"Sarvam error: {e}")
            finally:
                if temp_path.exists():
                    temp_path.unlink()

        if st.session_state.get(gu_key):
            st.info(
                f"**{t('transcript_original')}:**\n\n"
                f"{st.session_state[gu_key]}"
            )
            if st.session_state.get(en_key):
                st.caption(
                    f"**English:** {st.session_state[en_key]}"
                )

    st.markdown("")

    # ---- Submit button ----
    submitted = st.button(
        t("submit_report"),
        type="primary",
        key=f"submit_{report_type}",
        use_container_width=True,
    )

    if not submitted:
        return

    if not diamond_id or not audio:
        st.warning("Please enter a Diamond ID and record audio before submitting.")
        return

    # ---- Save audio file ----
    # Custom recorder uses MediaRecorder → emits WebM/Opus, so save as .webm
    # for Sarvam to pick the right MIME via _audio_mime().
    file_uuid = uuid.uuid4().hex
    audio_path: Path = AUDIO_DIR / f"{file_uuid}.webm"
    audio_bytes = audio.getvalue()
    audio_path.write_bytes(audio_bytes)

    # ---- Use pre-generated transcripts ----
    transcript_gu = st.session_state.get(f"trans_gu_{report_type}", "")
    transcript_en = st.session_state.get(f"trans_en_{report_type}", "")

    # If for some reason they aren't there, try one last time
    if not transcript_gu and audio:
        try:
            with st.spinner(t("transcribing")):
                transcript_gu, transcript_en = ai_clients.process_audio_full(audio_path)
        except Exception as e:
            st.warning(f"Sarvam error: {e}. Saving without transcript.")

    # ---- Insert report + audio ----
    with connect() as c:
        cur = c.execute(
            """INSERT INTO reports (worker_id, process_id, diamond_id, report_type)
               VALUES (?, ?, ?, ?)""",
            (user["id"], proc_id, diamond_id, report_type),
        )
        report_id = cur.lastrowid
        c.execute(
            """INSERT INTO audio_files
               (report_id, file_uuid, file_path, language, transcript_original, transcript_english)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (report_id, file_uuid, str(audio_path), "gu-IN", transcript_gu, transcript_en),
        )

    # ---- Background Tasks (AI Analysis & Chain of Responsibility) ----
    def _run_background_tasks(r_id, d_id, p_name, u_name, t_en, t_gu, r_type):
        try:
            # 1. Individual Report Analysis
            candidates = _candidate_links(d_id, exclude_report_id=r_id)
            analysis = ai_clients.analyze_report(
                report_type=r_type,
                diamond_id=d_id,
                process_name=p_name,
                worker_name=u_name,
                transcript_english=t_en or t_gu,
                candidate_links=candidates,
            )
            
            with connect() as c_bg:
                c_bg.execute(
                    """INSERT INTO ai_analysis
                       (report_id, severity, root_cause, defect_type,
                        linked_report_id, correlation_confidence, raw_response)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        r_id,
                        analysis.get("severity"),
                        analysis.get("root_cause"),
                        analysis.get("defect_type"),
                        analysis.get("linked_report_id"),
                        float(analysis.get("correlation_confidence") or 0.0),
                        analysis.get("raw"),
                    ),
                )
                
                # 2. Chain of Responsibility Analysis
                chain_rows = query_all(
                    """SELECT r.id, r.worker_id AS user_id, r.report_type, r.created_at,
                              u.name AS worker_name, p.name AS process, a.transcript_english
                       FROM reports r
                       JOIN users u ON u.id = r.worker_id
                       JOIN processes p ON p.id = r.process_id
                       LEFT JOIN audio_files a ON a.report_id = r.id
                       WHERE r.diamond_id = ?
                       ORDER BY r.created_at""",
                    (d_id,),
                )
                if len(chain_rows) >= 2:
                    chain = ai_clients.analyze_diamond_chain(
                        diamond_id=d_id,
                        reports=[dict(r) for r in chain_rows],
                    )
                    ids = [r["id"] for r in chain_rows]
                    placeholders = ",".join("?" * len(ids))
                    c_bg.execute(
                        f"""UPDATE ai_analysis
                            SET responsible_user_id = ?, responsibility_reason = ?, chain_summary = ?
                            WHERE report_id IN ({placeholders})""",
                        (
                            chain.get("responsible_user_id"),
                            chain.get("responsibility_reason"),
                            chain.get("chain_summary"),
                            *ids,
                        ),
                    )
        except Exception as bg_e:
            import logging
            logging.error(f"[BACKGROUND AI ERROR] Report {r_id}: {bg_e}")

    # Kick off background tasks
    threading.Thread(
        target=_run_background_tasks,
        args=(report_id, diamond_id, proc_name, user["name"], transcript_en, transcript_gu, report_type),
        daemon=True
    ).start()

    # ---- Success ----
    st.success(t("report_saved"))
    st.markdown(f"**{t('transcript_original')}:** {transcript_gu or '—'}")
    st.audio(audio_bytes)

    # Collapse form after successful submit
    st.session_state["active_report_type"] = None
    # Clear temp transcripts
    for k in [f"trans_gu_{report_type}", f"trans_en_{report_type}", f"audio_hash_{report_type}"]:
        if k in st.session_state:
            del st.session_state[k]


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render() -> None:
    user = current_user()
    st.title(t("worker_home_title"))
    st.write(t("welcome_user", name=user["name"]))

    # Track which report form is open (None = none open)
    active = st.session_state.get("active_report_type")  # "receive" | "problem" | None

    c1, c2 = st.columns(2)

    # --- Receive Report button ---
    receive_label = (
        "✖ Close Receive Report" if active == "receive" else "📥  " + t("receive_report")
    )
    if c1.button(receive_label, use_container_width=True, type="primary", key="btn_receive"):
        st.session_state["active_report_type"] = None if active == "receive" else "receive"
        st.rerun()

    # --- Problem Report button ---
    problem_label = (
        "✖ Close Problem Report" if active == "problem" else "⚠️  " + t("problem_report")
    )
    if c2.button(problem_label, use_container_width=True, type="primary", key="btn_problem"):
        st.session_state["active_report_type"] = None if active == "problem" else "problem"
        st.rerun()

    # --- Inline report form (toggled) ---
    if active in ("receive", "problem"):
        st.divider()
        _render_report_form(user, active)

    # --- Recent history ---
    st.divider()
    st.subheader(t("my_history"))
    rows = query_all(
        """SELECT r.id, r.diamond_id, r.report_type, r.created_at,
                  p.name AS process_name,
                  a.transcript_original, a.transcript_english,
                  ai.severity, ai.defect_type
           FROM reports r
           JOIN processes p ON p.id = r.process_id
           LEFT JOIN audio_files a ON a.report_id = r.id
           LEFT JOIN ai_analysis ai ON ai.report_id = r.id
           WHERE r.worker_id = ?
           ORDER BY r.created_at DESC
           LIMIT 25""",
        (user["id"],),
    )
    if not rows:
        st.info(t("no_reports_yet"))
        return
    for r in rows:
        with st.expander(
            f"#{r['id']}  •  {r['diamond_id']}  •  {r['process_name']}  •  {r['report_type']}  •  {r['created_at']}"
        ):
            if r["severity"]:
                st.markdown(
                    f"**Severity:** {r['severity']}  |  **Defect:** {r['defect_type'] or '—'}"
                )
            st.markdown(f"**Transcript:** {r['transcript_original'] or '—'}")
