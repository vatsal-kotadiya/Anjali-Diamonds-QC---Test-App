"""Dashboard shared by Management and Admin — process-wise defect analytics."""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from db import query_all


AUTO_REFRESH_SECONDS = 10


def _period_cutoff(period: str) -> str:
    now = datetime.utcnow()
    if period == "Daily":
        cut = now - timedelta(days=1)
    elif period == "Weekly":
        cut = now - timedelta(days=7)
    else:
        cut = now - timedelta(days=30)
    return cut.isoformat(" ")


def _period_days(period: str) -> int:
    return {"Daily": 1, "Weekly": 7}.get(period, 30)


def render() -> None:
    st.title("🏠 Dashboard")
    st_autorefresh(interval=AUTO_REFRESH_SECONDS * 1000, key="dashboard_autorefresh")

    period = st.radio(
        "Period", ["Daily", "Weekly", "Monthly"], horizontal=True, index=2
    )
    cutoff = _period_cutoff(period)

    # ── Raw data ─────────────────────────────────────────────────────────────
    all_reports = query_all(
        """SELECT r.id, r.diamond_id, r.report_type, r.created_at,
                  p.name AS process_name,
                  u.name AS worker_name, u.emp_code,
                  d.name AS department,
                  a.file_path, a.transcript_english, a.transcript_original,
                  ai.severity, ai.defect_type, ai.root_cause,
                  ai.linked_report_id
           FROM reports r
           JOIN users u    ON u.id = r.worker_id
           JOIN processes p ON p.id = r.process_id
           LEFT JOIN departments d ON d.id = u.department_id
           LEFT JOIN audio_files a ON a.report_id = r.id
           LEFT JOIN ai_analysis ai ON ai.report_id = r.id
           WHERE r.created_at >= ?
           ORDER BY r.created_at DESC""",
        (cutoff,),
    )

    process_rows = query_all(
        """SELECT p.id, p.name,
                  COUNT(r.id) AS report_count,
                  SUM(CASE WHEN r.report_type='problem' THEN 1 ELSE 0 END) AS problems,
                  SUM(CASE WHEN r.report_type='receive' THEN 1 ELSE 0 END) AS received
           FROM processes p
           LEFT JOIN reports r ON r.process_id = p.id AND r.created_at >= ?
           GROUP BY p.id, p.name
           ORDER BY p.order_index, p.name""",
        (cutoff,),
    )

    total_reports = len(all_reports)
    total_problems = sum(1 for r in all_reports if r["report_type"] == "problem")
    total_received = sum(1 for r in all_reports if r["report_type"] == "receive")
    sev_counts = {"Severe": 0, "Moderate": 0, "Low": 0}
    for r in all_reports:
        if r["severity"] in sev_counts:
            sev_counts[r["severity"]] += 1
    unique_workers = len({r["worker_name"] for r in all_reports})
    unique_diamonds = len({r["diamond_id"] for r in all_reports})

    if not process_rows:
        st.info("No processes configured yet.")
        return

    # ── Top-level KPIs ───────────────────────────────────────────────────────
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Total Reports", total_reports)
    k2.metric("Problem Reports", total_problems)
    k3.metric("Workers Involved", unique_workers)
    k4.metric("Severe", sev_counts["Severe"])
    k5.metric("Moderate", sev_counts["Moderate"])
    k6.metric("Low", sev_counts["Low"])

    df = pd.DataFrame([dict(r) for r in process_rows])

    # ── Pull admin-entered "diamonds processed" totals for this period ───────
    days = _period_days(period)
    start_date = (datetime.utcnow() - timedelta(days=days)).date().isoformat()
    totals_rows = query_all(
        """SELECT process_id, COALESCE(SUM(total_diamonds), 0) AS total
           FROM process_daily_totals
           WHERE date >= ?
           GROUP BY process_id""",
        (start_date,),
    )
    totals_by_pid = {r["process_id"]: int(r["total"]) for r in totals_rows}

    st.divider()

    # ── Defect-rate bars ─────────────────────────────────────────────────────
    st.markdown(
        "#### Defect Rate by Process  "
        "<span style='color:#888; font-weight:normal; font-size:0.85rem'>"
        "(red fill = % of diamonds with defects; click a bar for details)</span>",
        unsafe_allow_html=True,
    )

    if "selected_process" not in st.session_state:
        st.session_state.selected_process = None

    # All bars share a 0–100% scale so they're directly comparable.
    domain_max = 100.0

    for _, row in df.iterrows():
        process = row["name"]
        defect_count = int(row["report_count"] or 0)
        total_processed = totals_by_pid.get(int(row["id"]), 0)

        if total_processed > 0:
            pct = min(100.0, (defect_count / total_processed) * 100.0)
        else:
            pct = 0.0

        c_name, c_bar, c_count = st.columns(
            [2, 7, 1.5], vertical_alignment="center"
        )
        c_name.markdown(f"**{process}**")

        single_df = pd.DataFrame([{"Process": process, "Pct": pct, "Max": domain_max}])
        selection = alt.selection_point(fields=["Process"], name="ProcessSelection", empty=False)

        bg_bar = (
            alt.Chart(single_df)
            .mark_bar(color="gray", opacity=0.2, cornerRadius=4, size=28)
            .encode(
                y=alt.Y("Process:N", title=None, axis=None),
                x=alt.X("Max:Q", title=None, scale=alt.Scale(domain=[0, domain_max]), axis=None),
            )
        )
        fg_bar = (
            alt.Chart(single_df)
            .mark_bar(cornerRadius=4, size=28, color="#e45756")
            .encode(
                y=alt.Y("Process:N", title=None, axis=None),
                x=alt.X("Pct:Q", title=None, scale=alt.Scale(domain=[0, domain_max]), axis=None),
                tooltip=[
                    alt.Tooltip("Process:N"),
                    alt.Tooltip("Pct:Q", format=".1f", title="Defect %"),
                ],
            )
            .add_params(selection)
        )
        bar = alt.layer(bg_bar, fg_bar).properties(height=28, padding=0)

        # Bump chart key on each click → fresh Altair state, so re-clicking
        # the same bar always fires a new event (no lingering selection).
        iteration = st.session_state.get(f"chart_iter_{process}", 0)
        chart_key = f"chart_{process}_{iteration}"

        event = c_bar.altair_chart(
            bar, use_container_width=True, on_select="rerun", key=chart_key
        )

        if event and "selection" in event and event.selection.get("ProcessSelection"):
            # Always OPEN the clicked process. Closing is done via ✖ Close
            # button inside the drill-down.
            st.session_state.selected_process = process
            st.session_state[f"chart_iter_{process}"] = iteration + 1
            st.rerun()

        c_count.markdown(
            f"<div style='text-align:right'><b>{defect_count}</b></div>",
            unsafe_allow_html=True,
        )

    selected_process = st.session_state.get("selected_process", None)

    # ── Drill-down ────────────────────────────────────────────────────────────
    st.divider()
    
    if selected_process:
        h_title, h_close = st.columns([6, 1])
        h_title.subheader(f"Detailed Report: {selected_process}")
        if h_close.button("✖ Close", key="close_drilldown", use_container_width=True):
            st.session_state.selected_process = None
            st.rerun()

        detail = [r for r in all_reports if r["process_name"] == selected_process]
        if not detail:
            st.info("No reports for this process in the selected period.")
        else:
            d1, d2, d3, d4, d5 = st.columns(5)
            d1.metric("Total Reports",  len(detail))
            d2.metric("Workers Involved",  len({r["worker_name"] for r in detail}))
            d3.metric("Severe",   sum(1 for r in detail if r["severity"] == "Severe"))
            d4.metric("Moderate", sum(1 for r in detail if r["severity"] == "Moderate"))
            d5.metric("Low",      sum(1 for r in detail if r["severity"] == "Low"))

            st.markdown("### Process Details Table")

            # Make the embedded audio player a bit larger for shop-floor use,
            # and hide the native download / overflow menu so users can't
            # download the audio file.
            st.markdown(
                """
                <style>
                [data-testid="stAudio"] audio {
                    width: 100% !important;
                    min-height: 54px !important;
                    transform: scale(1.15);
                    transform-origin: left center;
                }
                /* Chrome / Edge — hide the 3-dot menu (which has Download) */
                [data-testid="stAudio"] audio::-webkit-media-controls-overflow-button,
                [data-testid="stAudio"] audio::-webkit-media-controls-overflow-menu-button {
                    display: none !important;
                }
                </style>
                <script>
                  // Streamlit renders <audio controls> inside an iframe-less
                  // DOM. Walk it and add controlsList=nodownload so the
                  // browser hides the Download option in the overflow menu.
                  (function disableAudioDownload() {
                    const audios = window.parent.document.querySelectorAll(
                      '[data-testid="stAudio"] audio'
                    );
                    audios.forEach(a => {
                      a.setAttribute('controlsList', 'nodownload noplaybackrate');
                      a.setAttribute('disablePictureInPicture', '');
                    });
                  })();
                </script>
                """,
                unsafe_allow_html=True,
            )

            COL_WEIGHTS = [1.5, 2, 1.8, 1.2, 1.2, 4, 3, 1.8]

            # Table Header
            col_diamond, col1, col2, col_type, col_sev, col3, col4, col5 = st.columns(COL_WEIGHTS)
            col_diamond.markdown("**Diamond ID**")
            col1.markdown("**Worker Name**")
            col2.markdown("**Department**")
            col_type.markdown("**Report Type**")
            col_sev.markdown("**Bug Level**")
            col3.markdown("**Transcript**")
            col4.markdown("**Audio**")
            col5.markdown("**Date**")
            st.markdown(
                "<hr style='margin: 0.25rem 0 0.5rem 0; border-color: #2a2d35;'/>",
                unsafe_allow_html=True,
            )

            SEV_COLOR = {
                "Severe": "#ff4b4b",
                "Moderate": "#f1c40f",
                "Low": "#2ecc71",
            }
            TYPE_LABEL = {"receive": "Receive", "problem": "Problem"}
            TYPE_COLOR = {"receive": "#4a9eff", "problem": "#ff9f43"}

            # Table Rows
            for r in detail:
                c_diamond, c1, c2, c_type, c_sev, c3, c4, c5 = st.columns(COL_WEIGHTS, vertical_alignment="center")
                c_diamond.markdown(f"`{r['diamond_id']}`")
                c1.write(r["worker_name"])
                c2.write(r["department"] or "—")

                rtype = r["report_type"] or "—"
                c_type.markdown(
                    f"<span style='color:{TYPE_COLOR.get(rtype, '#aaa')}; font-weight:600'>"
                    f"{TYPE_LABEL.get(rtype, rtype)}</span>",
                    unsafe_allow_html=True,
                )

                severity = r["severity"] or "—"
                color = SEV_COLOR.get(severity, "#aaaaaa")
                c_sev.markdown(
                    f"<span style='color:{color}; font-weight:600'>{severity}</span>",
                    unsafe_allow_html=True,
                )

                transcript = r["transcript_english"] or r["transcript_original"] or "—"
                c3.caption(transcript)
                
                if r["file_path"] and Path(r["file_path"]).exists():
                    with open(r["file_path"], "rb") as f:
                        raw = f.read()
                    # Detect MIME from magic bytes — extension can lie because
                    # earlier versions saved browser-recorded WebM as ".wav".
                    head = raw[:12]
                    if head.startswith(b"RIFF") and b"WAVE" in head:
                        mime = "audio/wav"
                    elif head.startswith(b"\x1aE\xdf\xa3"):
                        mime = "audio/webm"
                    elif head.startswith(b"OggS"):
                        mime = "audio/ogg"
                    elif head.startswith(b"ID3") or head[:2] == b"\xff\xfb":
                        mime = "audio/mpeg"
                    else:
                        mime = "audio/webm"
                    with c4:
                        st.audio(raw, format=mime)
                else:
                    c4.caption("No audio")
                
                # Time on top, date below
                try:
                    date_obj = (
                        datetime.fromisoformat(r["created_at"])
                        if isinstance(r["created_at"], str)
                        else r["created_at"]
                    )
                    time_str = date_obj.strftime("%H:%M")
                    date_str = date_obj.strftime("%Y-%m-%d")
                except Exception:
                    time_str = ""
                    date_str = str(r["created_at"])
                c5.markdown(
                    f"<div><b>{time_str}</b><br>"
                    f"<span style='color:#888; font-size:0.85rem'>{date_str}</span></div>",
                    unsafe_allow_html=True,
                )

                st.markdown(
                    "<hr style='margin: 0.6rem 0; border: 0; border-top: 1px solid #2a2d35;'/>",
                    unsafe_allow_html=True,
                )
