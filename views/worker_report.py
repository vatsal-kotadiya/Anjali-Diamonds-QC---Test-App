"""Report submission page — recording + transcript + AI analysis."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from pathlib import Path

import streamlit as st

import ai_clients
from auth import current_user
from db import AUDIO_DIR, connect, query_all
from i18n import t


CORRELATION_WINDOW_HOURS = 72


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


def render() -> None:
    user = current_user()
    report_type = st.session_state.get("report_type", "receive")

    title = t("receive_report") if report_type == "receive" else t("problem_report")
    st.title(title)

    if st.button("← " + t("back")):
        st.session_state["nav_to"] = "home"
        st.rerun()

    if not user.get("process_id"):
        st.error(
            "Your profile is not linked to a process. Ask the admin to assign one."
        )
        return
    proc_id = user["process_id"]
    proc_name = user.get("process_name") or "—"

    st.info(f"{t('process')}: **{proc_name}**  (from your profile)")
    diamond_id = st.text_input(t("diamond_id"), max_chars=64).strip()
    audio = st.audio_input(t("record_audio"))

    submit = st.button(t("submit_report"), type="primary", disabled=not (diamond_id and audio))
    if not submit:
        return

    # Save audio file
    file_uuid = uuid.uuid4().hex
    audio_path: Path = AUDIO_DIR / f"{file_uuid}.wav"
    audio_bytes = audio.getvalue()
    audio_path.write_bytes(audio_bytes)

    # Sarvam: original transcript + English translation
    transcript_gu = ""
    transcript_en = ""
    try:
        with st.spinner(t("transcribing")):
            transcript_gu = ai_clients.transcribe_gujarati(audio_path)
            transcript_en = ai_clients.translate_to_english(audio_path)
    except Exception as e:
        st.warning(f"Sarvam error: {e}. Saving without transcript.")

    # Insert report + audio
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

    # Backend flag: does ANY 'problem' report exist for this diamond?
    # (Pure DB lookup — never displayed in UI; used only by Gemini + future logic.)
    pr_row = query_all(
        "SELECT 1 FROM reports WHERE diamond_id = ? AND report_type='problem' LIMIT 1",
        (diamond_id,),
    )
    has_matching_problem = "yes" if pr_row else "no"

    # Gemini analysis + correlation
    try:
        with st.spinner(t("analyzing")):
            candidates = _candidate_links(diamond_id, exclude_report_id=report_id)
            analysis = ai_clients.analyze_report(
                report_type=report_type,
                diamond_id=diamond_id,
                process_name=proc_name,
                worker_name=user["name"],
                transcript_english=transcript_en or transcript_gu,
                candidate_links=candidates,
                has_matching_problem_report=(has_matching_problem == "yes"),
            )
        with connect() as c:
            c.execute(
                """INSERT INTO ai_analysis
                   (report_id, severity, root_cause, defect_type,
                    linked_report_id, correlation_confidence, raw_response,
                    has_matching_problem_report)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    report_id,
                    analysis.get("severity"),
                    analysis.get("root_cause"),
                    analysis.get("defect_type"),
                    analysis.get("linked_report_id"),
                    float(analysis.get("correlation_confidence") or 0.0),
                    analysis.get("raw"),
                    has_matching_problem,  # 'yes' / 'no'
                ),
            )
        # Keep the flag in sync across all earlier rows for the same diamond.
        # (If this submission IS the problem report, every prior 'receive'
        #  analysis row for the diamond should flip to 1.)
        with connect() as c:
            c.execute(
                """UPDATE ai_analysis SET has_matching_problem_report = ?
                   WHERE report_id IN (SELECT id FROM reports WHERE diamond_id = ?)""",
                (has_matching_problem, diamond_id),
            )
    except Exception as e:
        st.warning(f"Gemini error: {e}. Report saved without analysis.")

    # Backend-only story-consistency check: if BOTH a receive and a problem
    # report exist for this diamond, ask Gemini whether they describe the same
    # defect. Result is written to every ai_analysis row for the diamond.
    try:
        pairs = query_all(
            """SELECT r.report_type, a.transcript_english
               FROM reports r
               LEFT JOIN audio_files a ON a.report_id = r.id
               WHERE r.diamond_id = ?""",
            (diamond_id,),
        )
        receive_t = [p["transcript_english"] for p in pairs if p["report_type"] == "receive" and p["transcript_english"]]
        problem_t = [p["transcript_english"] for p in pairs if p["report_type"] == "problem" and p["transcript_english"]]
        if receive_t and problem_t:
            verdict = ai_clients.verify_story_consistency(
                diamond_id=diamond_id,
                receive_transcripts=receive_t,
                problem_transcripts=problem_t,
            )
        else:
            verdict = {
                "stories_consistent": "unverifiable",
                "consistency_reason": "Need both a Receive and a Problem report to compare.",
            }
        with connect() as c:
            c.execute(
                """UPDATE ai_analysis
                   SET stories_consistent = ?, consistency_reason = ?
                   WHERE report_id IN (SELECT id FROM reports WHERE diamond_id = ?)""",
                (
                    verdict.get("stories_consistent"),
                    verdict.get("consistency_reason"),
                    diamond_id,
                ),
            )
    except Exception as e:
        st.warning(f"Story-consistency check skipped: {e}")

    # Chain analysis: if this diamond has 2+ reports, ask Gemini to attribute blame
    # across ALL of them and write the same chain result onto every related row.
    try:
        chain_rows = query_all(
            """SELECT r.id, r.worker_id AS user_id, r.report_type, r.created_at,
                      u.name AS worker_name,
                      p.name AS process,
                      a.transcript_english
               FROM reports r
               JOIN users u ON u.id = r.worker_id
               JOIN processes p ON p.id = r.process_id
               LEFT JOIN audio_files a ON a.report_id = r.id
               WHERE r.diamond_id = ?
               ORDER BY r.created_at""",
            (diamond_id,),
        )
        if len(chain_rows) >= 2:
            # Pull the latest consistency verdict for this diamond (if any) so
            # the chain prompt can factor it in.
            consistency_row = query_all(
                """SELECT stories_consistent, consistency_reason
                   FROM ai_analysis ai
                   JOIN reports r ON r.id = ai.report_id
                   WHERE r.diamond_id = ? AND ai.stories_consistent IS NOT NULL
                   LIMIT 1""",
                (diamond_id,),
            )
            cons_verdict = consistency_row[0]["stories_consistent"] if consistency_row else None
            cons_reason = consistency_row[0]["consistency_reason"] if consistency_row else None

            with st.spinner("Analyzing the full diamond chain..."):
                chain = ai_clients.analyze_diamond_chain(
                    diamond_id=diamond_id,
                    reports=[dict(r) for r in chain_rows],
                    stories_consistent=cons_verdict,
                    consistency_reason=cons_reason,
                )
            ids = [r["id"] for r in chain_rows]
            placeholders = ",".join("?" * len(ids))
            with connect() as c:
                c.execute(
                    f"""UPDATE ai_analysis
                        SET responsible_user_id = ?,
                            responsibility_reason = ?,
                            chain_summary = ?
                        WHERE report_id IN ({placeholders})""",
                    (
                        chain.get("responsible_user_id"),
                        chain.get("responsibility_reason"),
                        chain.get("chain_summary"),
                        *ids,
                    ),
                )
            resp_name = None
            if chain.get("responsible_user_id"):
                row = query_all(
                    "SELECT name FROM users WHERE id = ?", (chain["responsible_user_id"],)
                )
                if row:
                    resp_name = row[0]["name"]
            st.info(
                f"🔗 This diamond has {len(chain_rows)} reports. "
                f"**Responsible:** {resp_name or '—'}. "
                f"_{chain.get('responsibility_reason') or ''}_"
            )
    except Exception as e:
        st.warning(f"Chain analysis skipped: {e}")

    st.success(t("report_saved"))
    st.markdown(f"**{t('transcript_original')}:** {transcript_gu or '—'}")
    st.markdown(f"**{t('transcript_english')}:** {transcript_en or '—'}")
    st.audio(audio_bytes)
