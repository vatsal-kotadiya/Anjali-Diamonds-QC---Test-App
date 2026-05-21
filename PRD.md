# Diamond QC — Product Requirements Document

**Version:** 1.3 (aligned with Figma UI)
**Date:** 2026-05-21
**Status:** Draft

---

## 1. Overview

Diamond QC is a mobile-first defect-tracking application for diamond manufacturing operations. Workers verbally report defects in Gujarati at each stage of the manufacturing pipeline. AI transcribes, translates, and classifies reports, then cross-correlates them across stages to attribute responsibility to specific workers.

The app replaces manual paper-based defect logging and provides management with a real-time dashboard to monitor quality across the production floor.

---

## 2. Goals & Non-Goals

### Goals
- Allow shop-floor workers to submit voice-based defect reports in under 60 seconds
- Give management real-time visibility into defect patterns across all processes
- Use AI to automatically link related reports about the same diamond and attribute responsibility
- Work reliably in a factory environment (offline-first submission queue)
- Single codebase running on Android and iOS

### Non-Goals (v1)
- ERP or inventory integration
- Production output tracking ("completed diamonds")
- Multi-factory / cloud deployment (single-factory local server for v1)
- Password hashing / enterprise SSO (deferred to v2)

---

## 3. Design System (from Figma)

### Color Palette
| Token | Hex | Usage |
|---|---|---|
| Primary | `#E8491B` | Mic button, active tabs, CTAs, Submit, orange accents |
| Primary Dark | `#0F1A2E` | Sign In button |
| Login Background | `#3B0A0A` | Login screen full-screen background |
| App Background | `#F5F5F5` | All screens background |
| Surface | `#FFFFFF` | Cards, sheets, bottom nav |
| Input Fill | `#F0F0F0` | Unfocused input background |
| Severe | `#E8491B` | Severity badge + dot |
| Moderate | `#FFC107` | Severity badge + dot |
| Low | `#4CAF50` | Severity badge + dot |
| Active Green | `#4CAF50` | User status dot, ONLINE indicator |
| Inactive Red | `#E53935` | Inactive status dot, fault rate, Sign Out icon |
| Receive Tag Bg | `#EBF5FF` | Receive Report tag background |
| Receive Tag Fg | `#1D72E8` | Receive Report tag text |
| Problem Tag Bg | `#FFF0EB` | Problem Report tag background |
| Problem Tag Fg | `#E8491B` | Problem Report tag text |

### Shape & Typography
- All cards: `borderRadius: 16dp`
- All buttons: fully pill-shaped (`borderRadius: 100dp`)
- Input fields: `borderRadius: 12dp`, orange `1.5dp` border on focus
- Labels above inputs: ALL CAPS, `11sp`, `letterSpacing: 0.8`
- Font: Inter or system default sans-serif

### Bottom Navigation (per Figma)
| Role | Tab 1 | Tab 2 | Tab 3 | Tab 4 |
|---|---|---|---|---|
| Worker | Home (house) | History (clock) | Profile (person) | — |
| Management | Dashboard (house) | Chatbot (chat bubble) | Profile (person) | — |
| Admin | Dashboard (house) | Users (group) | Chatbot (chat bubble) | Profile (person) |

Active tab icon: Primary orange. Inactive: grey. No labels visible in nav bar.

---

## 4. Users & Roles

| Role | Description | Primary Device |
|---|---|---|
| **Worker** | Shop-floor employee at a specific workstation | Personal Android phone or shared tablet |
| **Management** | Supervisors who monitor quality KPIs | Phone or tablet |
| **Admin** | Factory manager who configures the system | Phone |

### Role Capabilities

**Worker**
- Submit Receive or Problem reports with voice + diamond ID
- View full personal submission history (searchable + filterable)
- Toggle UI language: English / Gujarati / Hindi

**Management**
- Real-time defect dashboard with period filter (Daily/Weekly/Monthly)
- Drill into per-process report details
- Access Diamond Assistant chatbot

**Admin**
- All Management capabilities
- CRUD users with auto-generated employee codes
- Configure departments and processes
- View and reveal user passwords

---

## 5. Platform & Tech Stack

### Mobile App
- **Framework:** Flutter 3.x — single codebase for Android + iOS
- **Language:** Dart
- **Min SDK:** Android 8.0 (API 26) / iOS 15
- **Offline support:** Reports queue locally in SQLite (`drift`) and sync when online
- **iOS builds:** Codemagic CI — no Mac required for development

### Backend
- **Runtime:** Python FastAPI
- **Database:** PostgreSQL
- **Audio storage:** Cloudflare R2
- **Auth:** JWT (access + refresh tokens)
- **Speech-to-text:** Sarvam AI `saarika:v2` (Gujarati audio → Gujarati text)
- **Translation:** Google Gemini `gemini-2.0-flash` (Gujarati text → English text)
- **AI analysis + chat:** Google Gemini `gemini-2.0-flash`

### Architecture
```
Flutter App (Android + iOS)
    │
    ├── REST API ──► FastAPI ──► PostgreSQL
    │                  │
    │                  ├──► Sarvam AI    (STT)
    │                  ├──► Gemini       (translation + analysis + chat)
    │                  └──► Cloudflare R2 (audio files)
    │
    └── Local SQLite / drift (offline queue)
```

---

## 6. Database Schema

```sql
departments(id, name UNIQUE, created_at)

processes(id, name UNIQUE, order_index, created_at)

users(
  id, emp_code UNIQUE,
  factory_code, floor, table_no, seq_count,
  username UNIQUE, password,
  name, role [admin | management | worker],
  department_id → departments,
  process_id → processes,        -- REQUIRED for workers
  mobile, address,
  language_pref [en | gu | hi],
  status [active | inactive],
  joining_date DATE,
  created_at
)

reports(
  id, worker_id → users,
  process_id → processes,
  diamond_id TEXT,
  report_type [receive | problem],
  created_at
)

audio_files(
  id, report_id → reports UNIQUE,
  file_uuid, file_url,
  language, transcript_original, transcript_english,
  duration_seconds, created_at
)

ai_analysis(
  id, report_id → reports UNIQUE,
  severity [Severe | Moderate | Low],
  root_cause, defect_type,
  linked_report_id → reports,
  correlation_confidence,
  responsible_user_id → users,
  responsibility_reason, chain_summary,
  has_matching_problem_report TEXT,   -- 'yes' / 'no'
  stories_consistent TEXT,            -- 'yes' / 'no' / 'unverifiable'
  consistency_reason TEXT,
  raw_response, created_at
)
```

**Fault Rate** — derived metric: `(problem_reports / total_reports) × 100` per user. Computed at query time, not stored.

**Employee code format:** `<factory:3><floor:2><table:2><count:4>` — e.g. `vaw03010001`

---

## 7. Screens & User Flows

### 7.1 Authentication

**Login Screen** *(from Figma)*
- Full-screen dark maroon (`#3B0A0A`) background
- Centered white card (borderRadius: 20dp) containing:
  - App name **"Anjali Diamonds"** (white, bold, 28sp) above card
  - Subtitle **"Sign in to your account"** (grey, 14sp) above card
  - ALL-CAPS label **USERNAME** + text input field
  - ALL-CAPS label **PASSWORD** + password input field
  - **Stay logged in** checkbox row
  - **Sign In** pill button (dark navy, full width)
- Error states: wrong credentials, account inactive, network error

---

### 7.2 Worker Flow

**Bottom nav:** Home · History · Profile

#### Home / Report Screen *(from Figma)*
Single screen — report type selected via tab toggle at top (not two separate screens).

- **Tab toggle row** (top):
  - `Receive Report` — orange filled pill when active
  - `Problem Report` — outlined pill when active
  - Switching tab swaps hint text below
- **Hint banner** (dismissible `×`):
  - Receive: *"Record a report if you receive a defective diamond."*
  - Problem: *"Record if you make a mistake while making the diamond."*
- **Diamond ID field** — dropdown with QR scanner icon on right trailing edge
  - ⚠️ Open question: dropdown of known IDs vs free-text + QR scan
- **Mic button** — 80dp orange circle, centered on screen
  - Pulsing ring animation while recording
  - Tap to start / tap again to stop
- **Waveform bar** — shown after recording, orange amplitude bars on white background
- **Transcript box** — Gujarati text auto-filled after STT; read-only in v1
- **Submit button** — orange pill, bottom of screen; disabled until Diamond ID + audio ready
- **Inline submission progress** text replaces button label:
  - Uploading… → Transcribing… → Translating… → Analysing… → ✅ Done
- On chain result: banner *"Responsibility attributed to [Name]"*
- On no network: save to queue, show "Pending" badge in History

#### History Screen *(from Figma)*
- AppBar: **History** title, back arrow
- Search bar: `"Search by Diamond ID…"`
- Filter chip: **All Types ▾** (Receive Report / Problem Report)
- Report list — each card (white, rounded-16):
  - Row: colored dot (severity) · **Diamond ID** bold · timestamp right (`12:52, 16 May`)
  - Blue pill **Receive Report** tag OR orange pill **Problem Report** tag
  - Gujarati transcript snippet (2 lines, ellipsis)

#### Profile Screen *(from Figma — "Employee Profile")*
- AppBar: **Employee Profile**, back arrow
- **Profile header card**: orange circle avatar (initial letter) + edit pencil overlay + name + emp code
- **ACCOUNT card** + **Edit** button:
  - Rows: USERNAME · DEPARTMENT · PROCESS · Mobile · ADDRESS
- **Language card**:
  - 3-pill toggle: `English` · `ગુજરાતી` · `हिंदी`
  - Selected: orange outlined pill; unselected: plain text
- **Sign Out card**: red logout icon on light-red background + "Sign Out" text

---

### 7.3 Management Flow

**Bottom nav:** Dashboard · Chatbot · Profile

#### Dashboard Screen *(from Figma)*
- AppBar: **Anjali Diamonds**
- **KPI summary row** (3 cards, always visible):
  - Total Reports (count, black)
  - Employees Involved (count, blue)
  - Severity split: `5 Severe` (orange) · `2 Moderate` (amber) · `1 Low` (green)
- **Period tabs**: `Daily` · `Weekly` · `Monthly` — active tab has orange underline
- **"Defect Rate by Process"** section label
- **Horizontal bar chart**:
  - Processes on Y-axis (4P, Sawing, Bruting, Polishing, Faceting, Final QC)
  - Orange bars extending right, defect count label at tip
  - Tap a bar row → navigate to Report Details screen

#### Report Details Screen *(from Figma)*
- AppBar: **Report Details** · subtitle `Process · Period` (e.g. *Bruting · Monthly*) · `×` close button
- **Stats row**: Total Reports · Workers (unique) · Defect %
- **Severity chips + gradient bar**:
  - `● 5 Severe` · `● 2 Moderate` · `● 1 Low`
  - Red → amber → green `LinearGradient` pill bar below
- Search bar: `"Search reports…"`
- Filter row: **All Types ▾** · **All Severity ▾** · **Sort: Newest ↕**
- **Report cards** (each):
  - Row: colored dot · Diamond ID (e.g. `D-67676`) · PROBLEM/RECEIVE tag · Severe/Moderate/Low badge
  - Worker name + Dept (e.g. `Harshil Patel · Dept: Bruting-A`)
  - Gujarati transcript (3 lines)
  - Audio player: orange play button + waveform bars + `0:08/0:08` time
  - Footer row: timestamp left · **Defect type tag** right (e.g. `Burn/Crack` orange text)

#### Diamond Assistant Screen *(from Figma)*
- AppBar: **Diamond Assistant** · `● ONLINE` green indicator · **Clear** button
- **Welcome card** (shown when chat is empty):
  - Orange robot avatar circle (80dp)
  - `"Hi Admin 👋"` greeting
  - Description text
- **Suggested prompt chips** (3, hidden after first message):
  - `↗ Top defective workers this month`
  - `⚠ Severe defects today`
  - `🕐 Last night's shift summary`
- Chat list (reverse): AI bubbles left (robot avatar), user bubbles right (orange)
- **Input bar** (pinned bottom): paperclip · text field `"Ask anything…"` · mic · orange send button

#### Profile Screen *(from Figma — "Management Profile")*
- Same layout as Worker Profile
- AppBar title: **Management Profile**
- No Process row in account section

---

### 7.4 Admin Flow

**Bottom nav:** Dashboard · Users · Chatbot · Profile

All Management screens, plus:

#### Users Screen *(from Figma)*
- AppBar: **Users** · `24 Users` subtitle · orange `+ Add` button
- Search: `"Search by name, username or emp code…"`
- Filter chips: **Role ▾** · **Department ▾** · **Status ▾**
- User list — each row (numbered):
  - Green dot (active) or red dot (inactive) + index number
  - **Name** bold + factory name right-aligned (e.g. `Chikuwadi`)
  - `EMP001 · Quality Inspector` subtitle
  - Tap → User Detail screen

#### User Detail Screen *(from Figma)*
- AppBar: user name · `Factory · Status` subtitle · red **Delete** button
- **Stats grid** (3×2):
  - TOTAL REPORTS · SEVERE (red) · MODERATE (amber)
  - LOW (green) · FAULT RATE % (red) · STATUS (green/red)
- **DETAILS section** + **Edit** button:
  - Emp Code · Username · Password (`●●●●●●●●` + eye reveal toggle)
  - Role · Department · Factory · Floor · Table · Process
  - Joining Date · Mobile · Address
- **Recent Reports section**:
  - Filter row: **All Types ▾** · **All Severity ▾**
  - Same report cards as Report Details screen (with audio player)

#### Create / Edit User Screen *(from Figma)*
- AppBar: **Create User**
- **Section 1 — Emp Code**:
  - 3-column inline row: `Factory` · `Floor` · `Table`
  - Auto-generated read-only code below (e.g. `vaw03010001`)
  - Helper text: *"Auto-generated from Factory + Floor + Table"*
- **Section 2 — Identity**:
  - Full Name · Role dropdown (Admin / Management / Worker)
  - Username + Password side-by-side (password has eye toggle)
- **Section 3 — Assignment**:
  - Department dropdown · Process dropdown
  - Helper: *"Process is required only for workers"*
- **Section 4 — Contact**: Mobile (`+91` prefix) · Address (multiline)
- **`+ Create User`** orange pill button, full width, pinned bottom

#### Settings Screen
- **Departments** tab: list + add/edit/delete inline
- **Processes** tab: list + add/edit/delete + drag to reorder

#### Profile Screen *(from Figma — "Admin Profile")*
- Same layout as Management Profile
- AppBar title: **Admin Profile**

---

## 8. AI Integration

### Per-report analysis
- Triggered immediately after report saved
- Input: English transcript + candidate reports for same `diamond_id` within 72h
- Output: `severity`, `defect_type`, `root_cause`, `linked_report_id`, `correlation_confidence`

### Chain attribution
- Triggered when `diamond_id` reaches ≥ 2 reports
- Result written to ALL `ai_analysis` rows for that diamond
- Output: `responsible_user_id`, `responsibility_reason`, `chain_summary`

### Story consistency check
- Backend-only: compares Receive + Problem transcripts for same diamond
- Writes `stories_consistent` + `consistency_reason` to all rows for that diamond
- Feeds into chain attribution prompt as context signal

### AI error policy
All AI calls non-fatal. Report saved regardless. App shows: *"AI analysis unavailable — report saved"*.

---

## 9. Offline & Sync

| Scenario | Behaviour |
|---|---|
| No network on submit | Queue in local SQLite, show "Pending" in History |
| Network restored | Background sync in order via WorkManager |
| Failure | Retry 3× with exponential backoff, then "Sync failed" + manual retry |
| Duplicate | Server deduplication within 5 min |

---

## 10. Notifications (v1 — local only)

| Trigger | Message |
|---|---|
| Queued report synced | "Report for diamond #[id] submitted" |
| Chain attribution done | "Responsibility attributed: [Name]" (management + admin) |
| Sync failed | "Report sync failed — tap to retry" |

FCM server-push deferred to v2.

---

## 11. Localisation

- **Languages:** English (default) · Gujarati · Hindi
- Worker-facing strings translated in all 3 languages
- Management / Admin UI: English only (v1)
- Language preference stored per user (`language_pref [en | gu | hi]`)
- ARB files: `app_en.arb` · `app_gu.arb` · `app_hi.arb`

---

## 12. Security & Auth

| Area | v1 | v2 |
|---|---|---|
| Passwords | Plaintext (admin sees + reveals via eye toggle) | bcrypt |
| Auth tokens | JWT — access 15 min / refresh 30 days, stored in secure storage | Keep |
| Transport | HTTPS | Valid cert |
| Role enforcement | Server-side on every endpoint | Keep |
| Audio | R2 private ACL + short-lived signed URLs | Keep |

---

## 13. Performance Requirements

| Metric | Target |
|---|---|
| Cold start | < 2 s on mid-range Android |
| Report submission (online) | Full pipeline < 15 s |
| Dashboard load | < 1 s cached · < 3 s fresh |
| Dashboard auto-refresh | Every 10 s, no visible jank |
| Max audio recording | 120 s |

---

## 14. Open Questions

| # | Question | Owner | By |
|---|---|---|---|
| 1 | Diamond ID: dropdown of known IDs vs free-text + QR scan? | Anjali + Tech | Sprint 1 |
| 2 | Hard Delete vs soft Deactivate on User Detail? | Anjali | Sprint 2 |
| 3 | Local server vs cloud for v1? | Anjali | Sprint 2 |
| 4 | Personal phones vs shared tablets? | Factory ops | Sprint 1 |
| 5 | iOS in v1 or Android-first? | Anjali | Sprint 1 |
| 6 | Sarvam STT rate limits under concurrent submissions? | Tech | Sprint 2 |

---

## 15. Out-of-Scope (Parking Lot)

- Completed-diamond / production-output ingestion
- Chatbot with live DB query access (text-to-SQL)
- Repeat-offender leaderboard
- Bulk user import via CSV
- Audit log
- Multi-language management UI
- Enterprise SSO / LDAP

---

## 16. Milestones

| Sprint | Deliverables |
|---|---|
| Sprint 1 (2 weeks) | Login screen, worker report screen (tab toggle + mic + waveform + transcript), history screen |
| Sprint 2 (2 weeks) | Backend API + Sarvam STT + Gemini translation, submission E2E, offline queue |
| Sprint 3 (2 weeks) | Gemini analysis + chain attribution, submission result banner |
| Sprint 4 (2 weeks) | Dashboard (KPI cards + bar chart + Report Details drill-down) |
| Sprint 5 (2 weeks) | Admin Users list + User Detail + Create/Edit User, Settings screen |
| Sprint 6 (2 weeks) | Diamond Assistant chatbot, all Profile screens |
| Sprint 7 (1 week) | Gujarati + Hindi localisation, polish, QA, UAT |
