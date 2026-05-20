# Diamond QC — Streamlit MVP

Quality-control reporting system for a diamond manufacturing workflow.
Workers record voice reports in Gujarati → Sarvam AI transcribes & translates → Gemini classifies severity and links related reports.

## Roles

- **Worker** — submits Receive Reports (defect received from previous stage) and Problem Reports (own mistake). Records audio in Gujarati.
- **Management** — defect dashboard, AI chatbot, profile.
- **Admin** — dashboard, user management (with auto-generated employee codes), settings (departments + processes), chatbot, profile.

## Employee code format

`<factory:3><floor:2><table:2><count:4>` — e.g. **`vaw03010001`**
The admin form auto-suggests the next code from factory + floor + table inputs and lets you override it manually.

## Quick start (Windows / PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

copy .env.example .env
# Edit .env and paste your SARVAM_API_KEY and GEMINI_API_KEY

python seed.py
streamlit run app.py
```

Default login: **admin / admin123**

## Install on a phone (PWA)

The app is a Progressive Web App, so any worker / manager / admin can install it
to their home screen and use it like a native app.

1. Make the app reachable on your network. By default `streamlit run app.py`
   binds to `0.0.0.0:8501`, so other devices on the same Wi-Fi can hit it at
   `http://<your-PC-IP>:8501` (find your IP with `ipconfig`).
2. On the phone, open that URL:
   - **Android (Chrome):** a banner will appear → tap "Install". Or menu (⋮) → "Install app".
   - **iOS (Safari):** tap Share → "Add to Home Screen".
3. The installed icon launches the app in standalone mode (no browser chrome).

> Note: Streamlit needs an active websocket, so true offline use isn't
> supported. The service worker caches the shell — opening offline shows a
> stale page; new submissions require connectivity.

To replace the placeholder diamond icons with your branding, drop in your own
`icon-192.png`, `icon-512.png`, and `icon-512-maskable.png` in `static/`.

## Project layout

```
app.py                 # Streamlit entry point + role-based sidebar nav
auth.py                # login / logout / require_login
db.py                  # SQLite schema, connect(), query helpers, next_emp_code()
seed.py                # creates admin user, default departments + processes
ai_clients.py          # Sarvam (STT + translate) and Gemini (analyze + chat)
i18n.py                # English/Gujarati strings for worker UI
views/
  worker_home.py       # Two big buttons + report history
  worker_report.py     # Diamond ID + record audio + AI pipeline + save
  dashboard.py         # Defect bar chart + drill-down with KPIs
  chatbot.py           # Gemini chat (no DB tools in MVP)
  admin_users.py       # CRUD users, auto emp_code, filters, search
  admin_settings.py    # Manage departments + processes
  profile.py           # Shared profile + language switch + logout
storage/audio/         # Recorded .wav files (DB only stores path + uuid)
diamond_qc.db          # SQLite database (created on first run)
```

## Database schema (7 tables)

| Table          | Purpose                                                                 |
|----------------|-------------------------------------------------------------------------|
| `departments`  | Admin-managed list (Sorting, Polishing, ...)                            |
| `processes`    | Admin-managed manufacturing stages (4P, Sawing, Polishing, ...)         |
| `users`        | All roles. Carries `emp_code` + factory/floor/table breakdown.          |
| `reports`      | One row per submitted report (receive / problem). FK to user + process. |
| `audio_files`  | Audio path + Sarvam transcripts (Gujarati + English). FK to report.     |
| `ai_analysis`  | Gemini output: severity, defect type, root cause, linked_report_id.     |

`ai_analysis.linked_report_id` is the correlation link — when worker A reports
"I made a mistake on #123" and worker B reports "I received #123 defective",
Gemini detects the match and writes the link on submission.

## Audio storage

Files live in `./storage/audio/<uuid>.wav`. DB only stores `file_uuid` + `file_path`.
For production, swap the path for a Cloudflare R2 or S3 key — only `ai_clients.py`
and `views/worker_report.py` need updating.

## What's stubbed for MVP

- Chatbot has no DB access — it's plain Gemini chat. Wiring text-to-SQL or function-calling is the next iteration.
- Dashboard shows "defective count" but no "completed diamonds" metric yet (we don't track production output).
- No password hashing (per request — admin sees plaintext password column).
