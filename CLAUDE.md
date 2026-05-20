# Diamond QC — Project Plan & Context

This file is the durable plan/spec for the Diamond QC app. Future Claude sessions
should read this first to understand goals, decisions, and what's been built.

---

## 1. Product vision

A web app for **defect tracking** across a diamond manufacturing workflow.
Diamonds pass through stages (4P, Sawing, Bruting, Polishing, Faceting, Final QC).
At each stage, defects can occur — cracks, chips, burns, polish issues.

Workers verbally report defects in **Gujarati**. AI transcribes, translates,
classifies severity, and **correlates** related reports (e.g. Worker A reports
"I made a mistake on diamond #123" and Worker B in the next stage reports
"I received #123 defective" — both refer to the same diamond/incident).
When a diamond accumulates 2+ reports, Gemini does a **chain analysis** over
all of them together and attributes responsibility to a specific worker.

---

## 2. Roles

| Role | Sees |
|---|---|
| **Worker** | Home (two big buttons + history), Report submission, Profile (with EN ↔ Gujarati switch) |
| **Management** | Dashboard, AI Chatbot, Profile |
| **Admin** | Dashboard, Users (CRUD), Settings (depts + processes), Chatbot, Profile |

---

## 3. Locked decisions (from clarifying Q&A)

| Decision | Choice |
|---|---|
| AI integration | **Real Sarvam + Gemini APIs** (keys in `.env`) |
| Diamond ID | **Free-text typed by worker** — no separate `diamonds` table |
| Processes & departments | **Admin-configurable** via Settings page |
| Auth | **Username + plaintext password** (admin sees password column) |
| Audio capture | **Browser mic** via `st.audio_input` |
| Deployment | **Local machine** for now (SQLite + local audio folder) |
| Mobile access | **PWA** — installable to home screen on Android & iOS via manifest + service worker injected into Streamlit's parent document |
| Chatbot | **Plain Gemini chat** — no DB tools in MVP |
| Correlation timing | **Immediately after submit** — 72h window on same `diamond_id` |
| Chain attribution | **Immediately after submit** — re-runs whenever a diamond reaches ≥2 reports and writes the same chain result onto every row |
| Employee code | Auto-generated `<factory:3><floor:2><table:2><count:4>` (e.g. `vaw03010001`); admin can edit |

---

## 4. Tech stack

- **Frontend + Backend:** Streamlit (single-process Python app)
- **DB:** SQLite (`diamond_qc.db` at project root)
- **Audio storage:** Local filesystem `./storage/audio/<uuid>.wav` (DB stores path + uuid only)
- **Speech-to-text + translation:** Sarvam AI
  - `https://api.sarvam.ai/speech-to-text` → Gujarati transcript (`saarika:v2`)
  - `https://api.sarvam.ai/speech-to-text-translate` → English transcript (`saaras:v2`)
- **Analysis + chat:** Google Gemini (`gemini-2.0-flash` via `google-generativeai`)
- **Charts:** Altair
- **Env:** `python-dotenv`

Production path (later): move audio to **Cloudflare R2** (cheapest, no egress fees).

---

## 5. Database schema (7 tables)

```
departments(id, name UNIQUE, created_at)
processes(id, name UNIQUE, order_index, created_at)
users(id, emp_code UNIQUE, factory_code, floor, table_no, seq_count,
      username UNIQUE, password, name, role[admin|management|worker],
      department_id→departments, process_id→processes,
      mobile, address, language_pref[en|gu], status[active|inactive], created_at)
      -- process_id is REQUIRED for role='worker'. Each worker is bound to
      -- exactly one process/workstation; reports auto-tag this process and
      -- the report page no longer shows a process dropdown.
reports(id, worker_id→users [role MUST = 'worker'], process_id→processes,
        diamond_id TEXT, report_type[receive|problem], created_at)
        -- DB triggers (trg_reports_worker_only_ins/upd) RAISE ABORT if
        -- worker_id references a user whose role != 'worker'.
audio_files(id, report_id→reports UNIQUE, file_uuid, file_path,
            language, transcript_original, transcript_english,
            duration_seconds, created_at)
ai_analysis(id, report_id→reports UNIQUE,
            severity[Severe|Moderate|Low], root_cause, defect_type,
            linked_report_id→reports, correlation_confidence,
            responsible_user_id→users, responsibility_reason, chain_summary,
            has_matching_problem_report TEXT,    -- 'yes' / 'no'
            stories_consistent TEXT,             -- 'yes' / 'no' / 'unverifiable'
            consistency_reason TEXT,             -- 1-line Gemini explanation
            raw_response, created_at)
```

**Correlation link:** `ai_analysis.linked_report_id` points to the earlier report
Gemini matched against (same diamond, same defect).

**Chain attribution:** when a diamond has 2+ reports, after the per-report analysis
we run `analyze_diamond_chain()` over ALL reports for that diamond and write the
same `responsible_user_id` / `responsibility_reason` / `chain_summary` onto every
row in the chain. The dashboard's "Diamond chains" section surfaces these.

**`has_matching_problem_report` flag:** on every report submission we check
whether ANY 'problem' report exists for that diamond_id and store `'yes'` /
`'no'` on the `ai_analysis` row.

**`stories_consistent` verdict (story verification):** when both a Receive
report and a Problem report exist for the same diamond, Gemini compares their
English transcripts via `verify_story_consistency()` and stores `'yes'` /
`'no'` / `'unverifiable'` plus a 1-line `consistency_reason` on every
`ai_analysis` row for that diamond. Re-evaluated on every new submission. Like
the other flags it's **backend-only** — surfaced into the chain-attribution
prompt so Gemini can blame the worker whose story doesn't match. The flag is also kept in sync across all earlier rows for
the same diamond (so when a Problem report comes in later, every prior Receive
row's flag flips to 1). The flag is **not displayed in the UI** — it exists
only to feed Gemini's `analyze_report()` and `analyze_diamond_chain()` prompts
as an extra context signal ("nobody has admitted fault → weight blame toward
the earliest upstream worker").

**No separate diamonds table** because diamond_id is free-text. Indexed for fast
lookup during correlation: `idx_reports_diamond`, `idx_reports_created`.

---

## 6. Employee code format

`<factory:3 lowercase letters><floor:2 digits><table:2 digits><count:4 digits>`
Example: **`vaw03010001`** = factory `vaw`, floor `03`, table `01`, sequence `0001`.

- `db.next_emp_code(factory, floor, table)` computes the next sequence number for
  that (factory, floor, table) bucket from `MAX(seq_count) + 1`.
- Admin form auto-suggests the next code as soon as factory/floor/table are filled.
- Admin can override the field manually before saving.
- The Edit form also exposes all four parts + the code for full control.

---

## 7. File layout

```
app.py                     # Streamlit entry + role-based sidebar nav + PWA + mobile CSS
pwa.py                     # Injects manifest + meta tags + SW registration
.streamlit/config.toml     # enableStaticServing = true so /app/static/* is served
static/manifest.json       # PWA manifest (name, icons, theme)
static/icon-192.png        # PWA install icon
static/icon-512.png        # PWA splash / install icon
static/icon-512-maskable.png  # Android adaptive icon
static/favicon.png         # Browser tab icon
auth.py                    # login(), logout(), require_login()
db.py                      # schema, connect(), query helpers, next_emp_code()
seed.py                    # admin/admin123 + default depts/processes
ai_clients.py              # Sarvam STT/translate + Gemini analyze_report / analyze_diamond_chain / chat
i18n.py                    # English + Gujarati strings for worker UI
requirements.txt
.env.example               # SARVAM_API_KEY + GEMINI_API_KEY
README.md                  # Setup + run instructions for end user
CLAUDE.md                  # ← this file (durable plan)
storage/audio/             # .wav files (gitignored eventually)
diamond_qc.db              # SQLite (created on first run)
views/
  __init__.py
  worker_home.py           # Two big buttons + report history
  worker_report.py         # Diamond ID + audio + Sarvam + Gemini + save
  dashboard.py             # Defect bar chart + drill-down KPIs + audio playback
  chatbot.py               # Gemini chat (no DB access in MVP)
  admin_users.py           # CRUD users, auto emp_code, filters, search
  admin_settings.py        # Manage departments + processes
  profile.py               # Shared profile + EN/GU switch + logout
```

---

## 8. Report submission flow (the critical path)

1. Worker clicks **Receive Report** or **Problem Report** on home → sets
   `session_state.report_type` and navigates to report page.
2. Worker types Diamond ID + records audio in Gujarati (browser mic via
   `st.audio_input`). **The process is NOT selected** — it comes from
   `users.process_id` which the admin sets on the worker's profile. The
   report page just displays "Process: <name> (from your profile)".
3. On submit:
   - Save audio bytes to `storage/audio/<uuid>.wav`.
   - Call Sarvam STT (Gujarati) → `transcript_original`.
   - Call Sarvam translate → `transcript_english`.
   - INSERT into `reports` + `audio_files`.
   - Look up candidate prior reports for the same `diamond_id` within last 72h.
   - Call Gemini `analyze_report()` with the new report transcript + candidate
     list → `severity`, `defect_type`, `root_cause`, `linked_report_id`,
     `correlation_confidence`. INSERT into `ai_analysis`.
   - **Chain step:** if this `diamond_id` now has ≥2 total reports, call
     `analyze_diamond_chain()` with ALL of them. Gemini returns
     `responsible_user_id`, `responsibility_reason`, `chain_summary`. UPDATE
     every `ai_analysis` row for that diamond with the same chain result so
     the dashboard can read it from any row.
4. Show transcripts + audio playback + success message. If a chain ran, also
   show a banner naming the responsible worker.

All AI errors are non-fatal — the report is saved regardless. Chain step
specifically catches its own errors so a failed chain pass never blocks the
report save.

---

## 9. Dashboard (Management + Admin)

- Period filter: **Daily / Weekly / Monthly** (1d / 7d / 30d windows).
- **Auto-refresh** hardcoded to 10 seconds (constant `AUTO_REFRESH_SECONDS` in
  `views/dashboard.py`). Implemented with `streamlit-autorefresh`; the
  dashboard re-queries the DB on each tick so management can leave it open on
  a TV/monitor.
- **Horizontal bar chart** — processes listed vertically, defect count extending
  right with the number labeled at each bar tip. Chart height auto-scales with
  number of processes.
- Select a process → KPIs (total errors, unique employees, severity breakdown)
  + detailed report list. Each row expands to show transcripts, root cause,
  defect type, **linked report id**, and audio playback.
- **🔗 Diamond chains section:** lists every diamond with ≥2 reports in the
  selected period, sorted by report count. Each row expands to show:
  - The responsible worker (name + emp_code), as attributed by Gemini
  - `chain_summary` — narrative of what happened across stages
  - `responsibility_reason` — why this worker was blamed
  - The full per-report breakdown (time, worker, process, type, severity, transcript)

**Not yet tracked:** "Completed diamonds" — no production-output ingestion.
Decide later how to capture this (manual entry per process per day? barcode scan?).

---

## 10. Mobile / PWA

The app is installable on Android and iOS as a Progressive Web App:

- `static/manifest.json` declares name, icons, theme color, `display: standalone`.
- **No service worker.** Streamlit's static handler only serves under
  `/app/static/`, and a SW registered from there cannot legally take scope `/`
  without a `Service-Worker-Allowed` response header — which Streamlit doesn't
  expose. Chrome 2021+ makes the app installable from the manifest alone, so
  the SW was removed. Add one later only if we put Caddy/Nginx in front to set
  that header, or serve the SW from the root path.
- `pwa.py` (`inject_pwa()`) runs once per session and uses
  `streamlit.components.v1.html` to walk `window.parent.document` and append:
    - `<link rel="manifest">`
    - `<meta name="theme-color">` + iOS web-app meta tags
    - `<link rel="apple-touch-icon">`
  This parent-document injection is required because Streamlit content runs in
  an iframe; the manifest must live on the top-level page for browsers to
  recognize the app as installable.
- Static files are served by Streamlit itself (`enableStaticServing = true`
  in `.streamlit/config.toml`) at `/app/static/<file>`.
- `app.py` also injects mobile-friendly CSS (bigger touch targets, condensed
  spacing on screens ≤640 px).

**Install flow:**
1. Phone visits the app's URL in Chrome (Android) or Safari (iOS).
2. Chrome shows an install prompt automatically; Safari users tap Share → "Add to Home Screen".
3. The installed app launches in standalone mode (no browser chrome).

**Caveats:** Streamlit needs a live websocket — true offline reporting isn't
supported. Without a service worker the app also won't open offline at all; you
get a connection error from the browser. Re-add a SW once we're behind a
reverse proxy that can set `Service-Worker-Allowed: /`.

---

## 11. What's stubbed for the MVP

- Chatbot has no DB access. Next iteration: give Gemini function-calling tools
  (`query_reports`, `top_offenders`, etc.) or a text-to-SQL pass.
- "Completed diamonds" metric isn't ingested.
- No password hashing (admin sees plaintext per spec — revisit before production).
- Audio is local only — swap to R2/S3 when deploying beyond a single machine.

---

## 12. How to run

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env       # paste SARVAM_API_KEY + GEMINI_API_KEY
python seed.py
streamlit run app.py
```

Login: **admin / admin123**

---

## 13. Future iterations (parking lot)

- Chatbot with DB tool access (text-to-SQL or function calling against `reports`,
  `users`, `ai_analysis`).
- Production-output ingestion → "completed diamonds" metric on dashboard.
- Repeat-offender report (Gemini already classifies; just needs a dedicated view
  — group by `ai_analysis.responsible_user_id` and count).
- Password hashing (bcrypt) + role-based row-level checks.
- Move audio to Cloudflare R2; only `ai_clients.py` and `worker_report.py` change.
- Replace placeholder PWA icons in `static/` with branded artwork (192/512/maskable).
- Further mobile-first CSS polish (current build only does base touch-target sizing).
- Audit log (who edited which user, when).
- Bulk user import via CSV.
