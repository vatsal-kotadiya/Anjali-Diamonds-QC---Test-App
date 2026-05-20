"""Minimal English/Gujarati translation map for worker-facing UI."""
from __future__ import annotations

import streamlit as st

STRINGS = {
    "en": {
        "worker_home_title": "Worker Home",
        "welcome_user": "Welcome, {name}",
        "receive_report": "Receive Report",
        "problem_report": "Problem Report",
        "my_history": "My recent reports",
        "no_reports_yet": "You haven't submitted any reports yet.",
        "submit_report": "Submit Report",
        "diamond_id": "Diamond ID",
        "process": "Process",
        "record_audio": "Record audio (Gujarati)",
        "transcribing": "Transcribing & translating...",
        "analyzing": "Analyzing with AI...",
        "report_saved": "Report saved.",
        "transcript_original": "Original transcript",
        "transcript_english": "English translation",
        "profile": "Profile",
        "language": "Language",
        "logout": "Log out",
        "back": "Back",
    },
    "gu": {
        "worker_home_title": "વર્કર હોમ",
        "welcome_user": "સ્વાગત છે, {name}",
        "receive_report": "પ્રાપ્ત રિપોર્ટ",
        "problem_report": "સમસ્યા રિપોર્ટ",
        "my_history": "મારા તાજેતરના રિપોર્ટ્સ",
        "no_reports_yet": "તમે હજુ સુધી કોઈ રિપોર્ટ સબમિટ કર્યો નથી.",
        "submit_report": "રિપોર્ટ સબમિટ કરો",
        "diamond_id": "ડાયમંડ ID",
        "process": "પ્રક્રિયા",
        "record_audio": "ઑડિઓ રેકોર્ડ કરો (ગુજરાતી)",
        "transcribing": "ટ્રાન્સક્રિપ્શન અને અનુવાદ...",
        "analyzing": "AI દ્વારા વિશ્લેષણ...",
        "report_saved": "રિપોર્ટ સાચવાયો.",
        "transcript_original": "મૂળ ટ્રાન્સક્રિપ્ટ",
        "transcript_english": "અંગ્રેજી અનુવાદ",
        "profile": "પ્રોફાઇલ",
        "language": "ભાષા",
        "logout": "લૉગ આઉટ",
        "back": "પાછળ",
    },
}


def lang() -> str:
    user = st.session_state.get("user") or {}
    return st.session_state.get("lang_override") or user.get("language_pref") or "en"


def t(key: str, **fmt) -> str:
    s = STRINGS.get(lang(), STRINGS["en"]).get(key) or STRINGS["en"].get(key, key)
    return s.format(**fmt) if fmt else s
