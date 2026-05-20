"""Sarvam AI (speech) + Google Gemini (analysis & chat) wrappers."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable

import requests
from dotenv import load_dotenv

load_dotenv(override=True)

def get_sarvam_key():
    return os.getenv("SARVAM_API_KEY", "")

def get_gemini_key():
    return os.getenv("GEMINI_API_KEY", "")

SARVAM_STT_MODEL = os.getenv("SARVAM_STT_MODEL", "saarika:v2.5")
# saaras has no "flash" variant — v2.5 is the latest/fastest available
SARVAM_TRANSLATE_MODEL = os.getenv("SARVAM_TRANSLATE_MODEL", "saaras:v2.5")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
# Lighter, faster Gemini for the translation-refine pass (just a glossary fix)
GEMINI_REFINE_MODEL = os.getenv("GEMINI_REFINE_MODEL", "gemini-2.5-flash-lite")

SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"
SARVAM_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"


# --------- Sarvam ---------

def _sarvam_headers() -> dict:
    return {"api-subscription-key": get_sarvam_key()}


import time
from concurrent.futures import ThreadPoolExecutor

def _sarvam_post(url: str, files: dict, data: dict) -> dict:
    """Helper with retries for Sarvam API calls."""
    last_err = None
    for attempt in range(3):
        try:
            r = requests.post(
                url, 
                headers=_sarvam_headers(), 
                files=files, 
                data=data, 
                timeout=180
            )
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_err = e
            time.sleep(2 ** attempt)  # exponential backoff
    raise last_err

_MIME_BY_EXT = {
    ".wav": "audio/wav",
    ".webm": "audio/webm",
    ".ogg": "audio/ogg",
    ".mp3": "audio/mpeg",
    ".m4a": "audio/mp4",
    ".mp4": "audio/mp4",
}


def _audio_mime(audio_path: Path) -> str:
    return _MIME_BY_EXT.get(audio_path.suffix.lower(), "audio/wav")


def transcribe_gujarati(audio_path: Path) -> str:
    """Get original-language transcript (Gujarati)."""
    if not get_sarvam_key():
        raise RuntimeError("SARVAM_API_KEY missing in .env")
    with open(audio_path, "rb") as f:
        files = {"file": (audio_path.name, f, _audio_mime(audio_path))}
        data = {
            "language_code": "gu-IN",
            "model": SARVAM_STT_MODEL,
            "mode": "verbatim"
        }
        res = _sarvam_post(SARVAM_STT_URL, files=files, data=data)
    return res.get("transcript", "")

def translate_to_english(audio_path: Path) -> str:
    """Use Sarvam's speech-to-text-translate to get English directly from audio."""
    if not get_sarvam_key():
        raise RuntimeError("SARVAM_API_KEY missing in .env")
    with open(audio_path, "rb") as f:
        files = {"file": (audio_path.name, f, _audio_mime(audio_path))}
        data = {"model": SARVAM_TRANSLATE_MODEL}
        res = _sarvam_post(SARVAM_TRANSLATE_URL, files=files, data=data)
    return res.get("transcript", "")

def process_audio_full(audio_path: Path) -> tuple[str, str]:
    """Transcribe (Gujarati) + translate (English) in parallel, then refine
    the English with Gemini to fix diamond-industry-specific mistranslations
    (e.g. Sarvam renders "હીરો" as "hero" instead of "diamond")."""
    with ThreadPoolExecutor(max_workers=2) as executor:
        f_gu = executor.submit(transcribe_gujarati, audio_path)
        f_en = executor.submit(translate_to_english, audio_path)
        gu, en_raw = f_gu.result(), f_en.result()
    en = refine_translation(gujarati=gu, english=en_raw)
    return gu, en


def refine_translation(*, gujarati: str, english: str) -> str:
    """Ask Gemini to fix diamond-manufacturing-context errors in Sarvam's
    English translation. Falls back to the original Sarvam output on error
    so a Gemini failure never hides the user's transcript."""
    if not english or not english.strip():
        return english
    try:
        genai = _gemini()
    except Exception:
        return english

    prompt = f"""You are a translation editor for a diamond-manufacturing factory in Gujarat, India.
A worker spoke in Gujarati. Sarvam AI auto-translated it to English but uses CONTEXT-FREE translation,
so it makes domain mistakes. Your job: produce a clean, accurate English version.

DIAMOND-INDUSTRY DOMAIN GLOSSARY (apply only when context warrants):

# Core noun corrections
- "હીરો" (heero) = DIAMOND (NOT "hero" the person). This is the #1 mistake.
- "મશીન" = the polishing / cutting / sawing machine.
- "સાહેબ" / "સાહબ" / "સાહબજી" = sir / boss / supervisor.
- "ભાઈ" = informal "brother" — usually just a polite address, often skip in English.
- "કારીગર" = artisan / skilled worker.
- "મિસ્તરી" = workshop master / senior technician.
- "પાર્ટી" = customer / client (NOT a "party event").
- "માલ" = goods / stock (the diamond rough or batch), NOT "wealth".

# Tools, parts, consumables (Gujarati or Gujlish)
- "ડિસ્ક" / "ડિસ્કુ" / "લેપ" = the polishing wheel / lap.
- "ડોપ" / "બોપ" = dop (the stick that holds the diamond against the wheel).
- "તાંગ" = tang / holder.
- "પાવડર" = diamond polishing powder / paste.
- "બાથ" = chemical bath.
- "તાવડી" = pan / sieve / tray.

# Processes (worker may name them in Gujlish)
- "૪P" / "ફોર પી" / "પ્લાનિંગ" = 4P (planning stage).
- "સોઇંગ" / "સોઈંગ" = sawing.
- "બ્રુટિંગ" / "બ્રુટ" = bruting (rounding stage).
- "પોલિશ" / "પોલિશિંગ" = polishing.
- "ફેસેટિંગ" / "ફેસેટ" = faceting.
- "QC" / "ક્યુસી" = quality control / final inspection.

# Defect & condition terms
- "ક્રેક" / "તિરાડ" / "ક્રેક પડી ગયો" = crack (developed a crack — NOT "fell" or "dropped").
- "ચીપ" / "ચીપીંગ" / "ચીપાઈ ગયો" = chip / chipped on edge.
- "તૂટી ગયો" = broken / chipped (in diamond context — NOT "fully shattered").
- "કાળો પડી ગયો" / "બળી ગયો" = turned black / burned (carbon spot or polish burn).
- "ધાર બગડી" / "ધાર તૂટી" = edge damaged / edge broken.
- "ફેસ ખરાબ" / "ફેસ ગયો" = facet damaged / mis-cut facet.
- "ધૂળ" / "ધૂળિયો" = dust / dusty (foreign particles).
- "ઇન્ક્લુઝન" / "દાગ" / "ડાઘ" = inclusion / spot / blemish inside the stone.
- "ધુમ્મસ" / "મિલ્કી" = milky / cloudy appearance.

# Action verbs that get mistranslated
- "ઘસવું" / "ઘસતા" / "ઘસતા ઘસતા" = polishing / while polishing (NOT just "rubbing").
- "હલવાઈ ગયો" (in machine context) = got STUCK / WEDGED (NEVER "halwa" / "yogurt").
- "નીકળી ગયો" = popped out / came loose (NOT "went out").
- "પડી ગયો" (about a defect) = developed / appeared (NOT "fell").
- "દઈ નાખી" / "બગાડી નાખી" / "ખોટું કરી નાખ્યું" = ruined / spoiled / damaged.
- "ઊડી ગયો" / "ઊડ્યો" = flew off / chipped off (a fragment broke away).
- "મારી નાખ્યો" (about a diamond) = ruined / destroyed (literal "killed" is wrong).
- "બેસાડ્યો" / "બેસાડી દીધો" = mounted / set (the diamond into the dop).
- "ગોઠવ્યો" = positioned / aligned.

# Quality grading
- "કેરેટ" = carat. "પોઇન્ટ" = point (1/100 of a carat).
- "ગ્રેડ" = grade. "ક્લેરિટી" = clarity. "કટ" = cut.
- "VVS / VS / SI" — leave as is.

# Quantities & filler
- "એક નંગ" / "નંગ" = one piece / piece.
- "બે-ત્રણ" = two-three. "થોડું" = a bit / slightly.
- Filler words like "આ", "પેલું", "પેલો" — usually drop in English.

RULES:
1. Only apply a correction when the Gujarati clearly supports it.
2. Keep names, IDs, numbers, and English loanwords as-is.
3. Do NOT add information that isn't in the Gujarati.
4. Return one clean, natural English sentence (or 2-3 if needed). Lowercase first letter ok; punctuation natural.

GUJARATI ORIGINAL:
"{gujarati}"

SARVAM'S RAW ENGLISH (may contain domain errors):
"{english}"

Return ONLY the corrected English sentence. No quotes, no markdown, no explanation."""

    try:
        # Use the lighter Gemini flash-lite for the refine pass — it's just a
        # glossary substitution, not deep reasoning, so the smaller model is
        # plenty accurate and noticeably faster.
        model = genai.GenerativeModel(GEMINI_REFINE_MODEL)
        resp = model.generate_content(prompt)
        cleaned = (resp.text or "").strip().strip('"').strip("'")
        return cleaned or english
    except Exception:
        return english


# --------- Gemini ---------

def _gemini():
    import google.generativeai as genai

    key = get_gemini_key()
    if not key:
        raise RuntimeError("GEMINI_API_KEY missing in .env")
    genai.configure(api_key=key)
    return genai


def analyze_report(
    *,
    report_type: str,
    diamond_id: str,
    process_name: str,
    worker_name: str,
    transcript_english: str,
    candidate_links: Iterable[dict] = (),
    has_matching_problem_report: bool = False,
) -> dict:
    """Ask Gemini to classify severity + extract root cause + optionally link a prior report.

    candidate_links: list of dicts {id, report_type, worker, transcript} for the same diamond_id
                     within a recent window. Gemini decides if any of them are the same incident.
    Returns: {severity, root_cause, defect_type, linked_report_id, correlation_confidence, raw}
    """
    genai = _gemini()

    candidates_str = (
        "\n".join(
            f"- id={c['id']}, type={c['report_type']}, worker={c['worker']}, transcript=\"{c['transcript']}\""
            for c in candidate_links
        )
        or "(none)"
    )

    prompt = f"""You are a quality-control analyst at a diamond manufacturing facility.
Analyze the worker's defect report and respond with STRICT JSON only — no markdown.

NEW REPORT:
  diamond_id: {diamond_id}
  process: {process_name}
  worker: {worker_name}
  report_type: {report_type}   # 'receive' = received defective from previous stage; 'problem' = worker admits own mistake
  transcript (English): "{transcript_english}"

CANDIDATE EARLIER REPORTS FOR THE SAME DIAMOND:
{candidates_str}

CONTEXT FLAG:
  problem_report_filed_for_this_diamond: {"yes" if has_matching_problem_report else "no"}
  # "yes" means some worker has admitted fault (anywhere in time) for this diamond.
  # "no" means no Problem report exists — if the current report is 'receive',
  # the upstream worker has not yet owned up. Treat this as a stronger signal
  # that the upstream worker may be evading responsibility.

Return JSON with keys:
  severity        : "Severe" | "Moderate" | "Low"
  defect_type     : short label (e.g. "Edge crack", "Polish burn", "Chipping")
  root_cause      : 1-2 sentence plain-English root cause
  linked_report_id: integer id of the matching earlier report if BOTH describe the same diamond AND same defect; otherwise null
  correlation_confidence: float 0..1 (0 if no link)
"""

    model = genai.GenerativeModel(GEMINI_MODEL)
    resp = model.generate_content(prompt)
    text = resp.text.strip()
    # Strip markdown fences if present
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = {
            "severity": "Moderate",
            "defect_type": "Unclassified",
            "root_cause": "Could not parse AI response.",
            "linked_report_id": None,
            "correlation_confidence": 0.0,
        }
    data["raw"] = resp.text
    return data


def verify_story_consistency(
    *,
    diamond_id: str,
    receive_transcripts: list[str],
    problem_transcripts: list[str],
) -> dict:
    """Compare 'receive' vs 'problem' report transcripts for the same diamond
    and decide whether they describe the same defect.

    Returns: {stories_consistent: 'yes'|'no'|'unverifiable', consistency_reason, raw}
    """
    if not receive_transcripts or not problem_transcripts:
        return {
            "stories_consistent": "unverifiable",
            "consistency_reason": "Need at least one Receive and one Problem report to compare.",
            "raw": "",
        }

    genai = _gemini()
    recv = "\n".join(f"  - \"{t}\"" for t in receive_transcripts if t)
    prob = "\n".join(f"  - \"{t}\"" for t in problem_transcripts if t)

    prompt = f"""You are a quality-control auditor at a diamond manufacturing facility.
For diamond_id={diamond_id}, compare what downstream workers reported RECEIVING
vs what the upstream worker reported as THEIR OWN PROBLEM. Decide whether both
sides describe the SAME defect.

RECEIVE reports (English transcripts):
{recv}

PROBLEM reports (English transcripts):
{prob}

Respond with STRICT JSON only — no markdown:
{{
  "stories_consistent": "yes" | "no" | "unverifiable",
  "consistency_reason": "1-line plain-English justification (e.g. 'both describe an edge crack', 'problem report mentions polish burn but receive says chip on table — different defects')"
}}

Rules:
- "yes" if the defect type / location / cause described in BOTH match (paraphrasing is fine).
- "no" if the two sides describe clearly different defects (different defect type or different location).
- "unverifiable" if transcripts are too vague to compare.
"""
    model = genai.GenerativeModel(GEMINI_MODEL)
    resp = model.generate_content(prompt)
    text = resp.text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = {
            "stories_consistent": "unverifiable",
            "consistency_reason": "Could not parse AI response.",
        }
    data["raw"] = resp.text
    return data


def _get_process_sequence() -> list[tuple[str, int]]:
    """Return [(process_name, order_index)] in manufacturing order.

    Used to give Gemini the actual stage order so it doesn't have to guess
    from world knowledge (which can be wrong when admin renames stages).
    Imported lazily to avoid circular imports.
    """
    try:
        from db import query_all
        rows = query_all(
            "SELECT name, COALESCE(order_index, 0) AS order_index "
            "FROM processes ORDER BY order_index, name"
        )
        return [(r["name"], int(r["order_index"])) for r in rows]
    except Exception:
        return []


def analyze_diamond_chain(
    *,
    diamond_id: str,
    reports: list[dict],
    stories_consistent: str | None = None,
    consistency_reason: str | None = None,
) -> dict:
    """Analyze ALL reports for one diamond together and attribute responsibility.

    Each report dict should have: id, user_id, worker_name, process, report_type,
    transcript_english, created_at.

    Returns: {responsible_user_id, responsibility_reason, chain_summary, raw}
    """
    genai = _gemini()
    lines = []
    for r in reports:
        lines.append(
            f"- report_id={r['id']} | user_id={r['user_id']} | worker={r['worker_name']} "
            f"| process={r['process']} | type={r['report_type']} | time={r['created_at']}\n"
            f"  transcript: \"{r.get('transcript_english') or ''}\""
        )
    chain_text = "\n".join(lines)
    any_problem = any(r.get("report_type") == "problem" for r in reports)

    # Manufacturing process order (admin-configurable). Pass this in so Gemini
    # uses the FACTORY's defined stage order, not its own world knowledge.
    seq = _get_process_sequence()
    if seq:
        seq_text = " → ".join(name for name, _ in seq)
        seq_ranks = "\n".join(f"  {idx+1}. {name}" for idx, (name, _) in enumerate(seq))
    else:
        seq_text = "(unknown — fall back to chronological order)"
        seq_ranks = ""

    prompt = f"""You are a senior quality-control analyst at a diamond manufacturing facility.
A single diamond (id={diamond_id}) has multiple defect reports from different workers across stages.
Read ALL of them together, reason about which worker actually caused the defect,
and respond with STRICT JSON only — no markdown.

MANUFACTURING PROCESS ORDER (earliest → latest):
{seq_text}
{seq_ranks}

REPORTS (chronological by timestamp — but NOTE the report timestamp may not match
the manufacturing order above. Always use the MANUFACTURING ORDER to decide which
stage is "upstream / earlier"):
{chain_text}

CONTEXT FLAG:
  problem_report_filed_for_this_diamond: {"yes" if any_problem else "no"}
  # "no" means nobody has admitted fault for this diamond. Every report is a
  # 'receive' (defect-passed-downstream). Treat this as evidence the upstream
  # worker is evading responsibility — weight blame toward the earliest stage.

  stories_consistent: {stories_consistent or "unverifiable"}
  consistency_reason: {consistency_reason or "n/a"}
  # If "no", the upstream Problem and downstream Receive reports describe
  # DIFFERENT defects — one of the workers is misreporting. Flag this in
  # responsibility_reason and lean toward the worker whose story is contradicted
  # by physical chain-of-custody (usually the Problem reporter if they're
  # downplaying the defect).

Rules for attribution (apply in this priority):
1. Workers report two types: 'problem' (admit own mistake) and 'receive' (got defective from prior stage).
2. If ONE worker explicitly admits the mistake with a 'problem' report, **prefer them** — they own up to it. Use them as `responsible_user_id` unless there's strong evidence they're lying.
3. Otherwise, the responsible worker is the one at the EARLIEST stage (per MANUFACTURING PROCESS ORDER above, NOT the timestamp).
4. Ties → earliest stage wins. Stage order is authoritative; timestamps are a weaker signal.
5. NEVER blame a 'receive' reporter unless every 'problem' reporter is clearly contradicted.

Return JSON with keys:
  responsible_user_id   : integer user_id from the list above (the worker you blame). Required.
  responsibility_reason : 1-2 sentence plain-English justification. Mention which stage they were at and why.
  chain_summary         : 2-4 sentence narrative of what happened to this diamond across stages.
"""
    model = genai.GenerativeModel(GEMINI_MODEL)
    resp = model.generate_content(prompt)
    text = resp.text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = {
            "responsible_user_id": None,
            "responsibility_reason": "Could not parse AI response.",
            "chain_summary": "",
        }
    data["raw"] = resp.text
    return data


def chat(messages: list[dict]) -> str:
    """Simple chatbot. messages: [{role:'user'|'assistant', content:str}, ...]"""
    genai = _gemini()
    model = genai.GenerativeModel(GEMINI_MODEL)
    history = [
        {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
        for m in messages[:-1]
    ]
    chat_session = model.start_chat(history=history)
    resp = chat_session.send_message(messages[-1]["content"])
    return resp.text
