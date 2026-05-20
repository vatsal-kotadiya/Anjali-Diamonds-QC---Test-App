# Diamond QC — Product Requirements Document

**Version:** 1.1 (updated from Figma UI — 2026-05-20)  
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
- Work reliably in a factory environment (low bandwidth tolerance, offline-first submission queue)

### Non-Goals (v1)
- ERP or inventory integration
- Production output tracking ("completed diamonds")
- Multi-factory / cloud deployment (single-factory local server assumed)
- Password hashing / enterprise SSO (deferred to v2)

---

## 3. Design System

### Color Palette
| Token | Value | Usage |
|---|---|---|
| Primary | Orange `#E8491B` (approx) | Mic button, active tabs, CTAs, severity dots, Submit |
| Primary Dark | Near-black navy `#0F1A2E` | Sign In button, primary action buttons |
| Background | Light gray `#F5F5F5` | App background |
| Surface | White `#FFFFFF` | Cards, sheets |
| Login Background | Dark maroon `#3B0A0A` | Login screen only |
| Severe | Red-orange (Primary) | Severity badge |
| Moderate | Amber/Yellow | Severity badge |
| Low | Green | Severity badge |
| Success dot | Green | Active user status |
| Error dot | Red | Inactive user status |

### Typography & Shape
- Clean sans-serif font (e.g. Inter or system default)
- Cards use large rounded corners (~16 dp)
- Input fields: rounded rectangle, outlined on focus with Primary color
- Buttons: fully rounded pill shape

### Bottom Navigation
| Role | Tab 1 | Tab 2 | Tab 3 | Tab 4 |
|---|---|---|---|---|
| Worker | Home (house) | History (clock) | Profile (person) | — |
| Management | Dashboard (house) | Chatbot (bubble) | Profile (person) | — |
| Admin | Dashboard (house) | Users (group) | Chatbot (bubble) | Profile (person) |

---

## 4. Users & Roles

| Role | Description | Primary Device |
|---|---|---|
| **Worker** | Shop-floor employee at a specific workstation | Personal Android phone or shared tablet |
| **Management** | Supervisors who monitor quality KPIs | Tablet or phone |
| **Admin** | Factory manager who configures the system | Phone |

### Role capabilities

**Worker**
- Submit Receive or Problem reports with voice + diamond ID
- View full submission history (searchable, filterable)
- Toggle UI language (English / Gujarati / Hindi)

**Management**
- View real-time defect dashboard with period filter
- Drill into per-process report details
- Access Diamond Assistant chatbot for ad-hoc queries

**Admin**
- All Management capabilities
- CRUD users with auto-generated employee codes
- Configure departments and processes
- View/reveal user passwords

---

## 5. Platform & Tech Stack

### Mobile App
- **Framework:** Flutter (preferred) or Kotlin Multiplatform
  - Flutter rationale: single codebase for Android + iOS, mature plugin ecosystem for audio recording, faster iteration
  - KMP rationale: if native Android feel is critical and iOS is a stretch goal
- **Min SDK:** Android 8.0 (API 26) / iOS 15
- **Offline support:** Report submissions queue locally (SQLite via `drift` or Room) and sync when connectivity is restored

### Backend (separate service)
- **Runtime:** Python (FastAPI) or Node.js (Fastify) — TBD
- **DB:** PostgreSQL
- **Audio storage:** Cloudflare R2 (object storage; no egress fees)
- **Auth:** JWT (access + refresh tokens)
- **Speech-to-text:** Sarvam AI `saarika:v2` (Gujarati audio → Gujarati transcript)
- **Translation:** Google Gemini `gemini-2.0-flash` (Gujarati transcript → English transcript)
- **AI analysis + chat:** Google Gemini `gemini-2.0-flash`

### Architecture
```
Mobile App (Flutter)
    │
    ├── REST API  ──► FastAPI backend  ──► PostgreSQL
    │                       │
    │                       ├──► Sarvam AI (STT — Gujarati transcript)
    │                       ├──► Gemini (translation + analysis + chat)
    │                       └──► Cloudflare R2 (audio files)
    │
    └── Local SQLite (offline queue)
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
  language_pref [en | gu | hi],  -- Hindi added
  status [active | inactive],
  joining_date DATE,             -- shown in user detail
  created_at
)

reports(
  id, worker_id → users,         -- must be role=worker (enforced by DB trigger)
  process_id → processes,
  diamond_id TEXT,
  report_type [receive | problem],
  created_at
)

audio_files(
  id, report_id → reports UNIQUE,
  file_uuid, file_url,           -- R2 URL
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

**Derived metric — Fault Rate:** computed on the fly as `problem_reports / total_reports * 100` per user. Not stored; calculated at query time.

**Employee code format:** `<factory:3><floor:2><table:2><count:4>` e.g. `vaw03010001`

---

## 7. Screens & User Flows

### 7.1 Authentication

**Login screen** *(dark maroon full-screen background, centered white card)*
- App name "Anjali Diamonds" + subtitle "Sign in to your account" above the card
- USERNAME and PASSWORD labeled text fields with placeholder text
- "Stay logged in" checkbox — persists JWT refresh token in secure storage
- "Sign In" pill button (dark navy, full width)
- Error states: wrong credentials, account inactive, network error

---

### 7.2 Worker Flow

**Bottom navigation:** Home · History · Profile

#### Home / Report screen
This is a single combined screen — the two report types are tab toggles at the top, not separate screens.

- **Tab bar at top:** `Receive Report` (orange pill when active) | `Problem Report` (outlined when inactive)
  - Switching tab updates the contextual hint banner below
  - Hint banner: dismissible `×` button
    - Receive: *"Record a report if you receive a defective diamond."*
    - Problem: *"Record if you make a mistake while making the diamond.."*
- **Diamond ID field** — dropdown with a QR scanner icon on the right
  - ⚠️ **Open question #7:** Design shows a dropdown; original spec was free-text. Resolve before sprint 1 — if diamond IDs are known in advance they can populate the dropdown; otherwise revert to free-text with optional QR scan.
- **Mic button** — large orange circle, center of screen
  - Tap to start recording; shows live audio waveform animation
  - Tap again to stop; waveform thumbnail stays visible for playback
  - Re-record clears previous audio
- **Transcript area** — text box below waveform; auto-filled with Gujarati transcript after recording + STT
- **Submit button** — orange pill, bottom-right; disabled until Diamond ID selected + audio recorded
- **Process** — not shown on this screen; auto-tagged from worker's profile

**Submission states (inline, replaces waveform area):**
1. Uploading audio…
2. Transcribing…
3. Translating…
4. Analysing…
5. ✅ Submitted — Gujarati transcript + severity badge visible
6. Chain ran → banner: "Responsibility attributed to [Name]"

**Offline:** save to local queue, show "Pending" badge on the report row in History

---

#### History screen *(clock tab)*
- Page title: **History**
- Search bar: "Search by Diamond ID…"
- Filter chip: **All Types ▾** (Receive Report / Problem Report)
- Report list — each card:
  - Colored dot (severity color) + Diamond ID (e.g. `D-34232`) + timestamp (`12:52, 16 May`)
  - Report type tag: blue pill for **Receive Report**, orange pill for **Problem Report**
  - Gujarati transcript snippet (1–2 lines)
- Tap card → full detail (transcript, audio playback, severity, AI analysis)

---

#### Profile screen *(person tab)*
- Back arrow + title: **Employee Profile**
- Avatar circle (orange, initial letter) + name + emp code + edit pencil icon
- **ACCOUNT** section with **Edit** button (top-right of section)
  - USERNAME / DEPARTMENT / PROCESS / Mobile / ADDRESS rows
- **Language** section — 3-option pill selector: `English` · `ગુજરાતી` · `हिंदी`
  - Selected option: orange outlined pill; others: plain text
- **Sign Out** row — red icon, light red background card

---

### 7.3 Management Flow

**Bottom navigation:** Dashboard · Chatbot · Profile

#### Dashboard screen
- App bar: **Anjali Diamonds**
- **Summary KPI row** (always visible, 3 cards):
  - Total Reports (count)
  - Employees Involved (count, blue)
  - Severity breakdown: `5 Severe` (orange) · `2 Moderate` (amber) · `1 Low` (green)
- **Period tabs:** `Daily` · `Weekly` · `Monthly` (active = orange underline)
- **Defect Rate by Process** — horizontal bar chart
  - Process names on left (4P, Sawing, Bruting, Polishing, Faceting, Final QC)
  - Orange bars extending right; defect count label at far right
  - Tap a bar row → navigate to **Report Details screen**

#### Report Details screen *(drill-down, separate screen)*
- App bar: **Report Details** · subtitle: `Process · Period` (e.g. *Bruting · Monthly*)
- Close (×) button top-right
- **KPI row:** Total Reports · Workers (unique count) · Defect % 
- **Severity chips + gradient bar:** `● 5 Severe` · `● 2 Moderate` · `● 1 Low` + red→yellow→green gradient bar
- Search bar: "Search reports…"
- Filters row: **All Types ▾** · **All Severity ▾** · Sort: **Newest ↕**
- **Reports list** — each card:
  - Colored dot + Diamond ID badge + Report Type tag (PROBLEM / RECEIVE) + Severity badge (● Severe)
  - Worker name + Dept (e.g. *Harshil Patel · Dept: Bruting-A*)
  - Gujarati transcript (2–3 lines)
  - Audio player: orange play button + waveform + elapsed/total time (e.g. `0:08/0:08`)
  - Timestamp (e.g. *15 May 2026, 11:08*) + **Defect type tag** bottom-right (e.g. `Burn/Crack` in orange)

#### Diamond Assistant (Chatbot) screen
- App bar: **Diamond Assistant** · green `● ONLINE` indicator · **Clear** button (top-right)
- Welcome card: robot avatar + "Hi [Role] 👋" greeting + description text
- **Suggested prompt chips** (3, shown before first message):
  - `↗ Top defective workers this month`
  - `⚠ Severe defects today`
  - `🕐 Last night's shift summary`
- Chat bubbles — AI responses left-aligned (orange robot avatar), user messages right-aligned (orange bubble)
- **Input bar** (pinned bottom): paperclip icon · "Ask anything…" placeholder · mic icon · orange send button

#### Profile screen
- Title: **Management Profile**
- Same layout as Worker Profile (avatar, account section, language selector, Sign Out)
- Account section shows: USERNAME / DEPARTMENT / PROCESS / Mobile / ADDRESS

---

### 7.4 Admin Flow

**Bottom navigation:** Dashboard · Users · Chatbot · Profile

All Management screens, plus:

#### Users screen
- App bar: **Users** · subtitle: `24 Users` · orange **`+ Add`** button (top-right)
- Search bar: "Search by name, username or emp code…"
- Filter chips: **Role ▾** · **Department ▾** · **Status ▾**
- User list — each row (numbered):
  - Status dot (green = active, red = inactive) + numbered index
  - Name (bold) + factory name (right-aligned, e.g. *Chikuwadi*)
  - EMP code · Role title (e.g. `EMP001 · Quality Inspector`)
- Tap row → **User Detail screen**

#### User Detail screen
- App bar: User name · subtitle: `Factory · Status` (e.g. *Silay · Active*) · red **Delete** button
  - ⚠️ **Note:** Design shows a Delete button; PRD originally specified Deactivate only. Resolve — recommend keeping Delete for admin, Deactivate for management.
- **Stats row** (6 cells): Total Reports · Severe · Moderate · Low · Fault Rate % · Status
  - Fault Rate = problem reports / total reports × 100, shown in red
  - Status shown in green (Active) or red (Inactive)
- **DETAILS section** + **Edit** button:
  - Emp Code / Username / Password (masked `●●●●●●●●` with eye-toggle reveal) / Role / Department / Factory / Floor / Table / Process / Joining Date / Mobile / Address
- **Recent Reports section** — filterable sub-list:
  - Filters: **All Types ▾** · **All Severity ▾**
  - Report cards (same format as Report Details screen)
  - Diamond ID shown as `D-XXXXX` format

#### Create / Edit User screen
- Title: **Create User** (or **Edit User**)
- **Section 1 — Employee Code:**
  - Inline row: `Factory` · `Floor` · `Table` (3 short fields)
  - Auto-generated Employee Code field (read-only, e.g. `vaw03010001`) with helper: *"Auto-generated from Factory + Floor + Table"*
- **Section 2 — Identity:**
  - Full Name
  - Role dropdown (Admin / Management / Worker)
  - Username · Password (side by side, password has eye-toggle)
- **Section 3 — Assignment:**
  - Department dropdown
  - Process dropdown — helper text: *"Process is required only for workers"*
- **Section 4 — Contact:**
  - Mobile (with `+91` prefix)
  - Address (multiline)
- **`+ Create User`** orange pill button (full width, pinned bottom)

#### Settings screen
- **Departments** tab: list with inline add/edit/delete
- **Processes** tab: list with inline add/edit/delete + drag-to-reorder (sets `order_index`)

---

## 8. AI Integration Details

### Per-report analysis (`analyze_report`)
Triggered immediately after a report is saved.

**Input to Gemini:**
- English transcript of new report
- Candidate prior reports for same `diamond_id` within last 72 hours (id, worker name, process, type, transcript)

**Output (JSON):**
```json
{
  "severity": "Severe | Moderate | Low",
  "defect_type": "string",
  "root_cause": "string",
  "linked_report_id": "int | null",
  "correlation_confidence": "float 0–1"
}
```

### Chain attribution (`analyze_diamond_chain`)
Triggered when a `diamond_id` reaches ≥ 2 total reports. Re-runs on every new submission for that diamond.

**Input:** All reports for the diamond (worker, process, type, transcript, severity, `stories_consistent`)

**Output (JSON):**
```json
{
  "responsible_user_id": "int",
  "responsibility_reason": "string",
  "chain_summary": "string"
}
```

Result written to every `ai_analysis` row for that diamond (fan-out update).

### Story consistency check (`verify_story_consistency`)
Run when both a Receive and a Problem report exist for the same diamond. Compares English transcripts → `stories_consistent` (`yes` / `no` / `unverifiable`) + `consistency_reason`. Backend-only — feeds chain attribution prompt, not shown in UI.

### Diamond Assistant chat
- Backed by Gemini
- System prompt includes role context (Admin / Management)
- v1: no live DB tool access — Gemini responds from conversation context only
- v2: give Gemini function-calling tools (`query_reports`, `top_offenders`, etc.)

### AI error policy
All AI calls are non-fatal. Report is saved regardless. Mobile app shows: *"AI analysis unavailable — report saved"*.

---

## 9. Offline & Sync

| Scenario | Behaviour |
|---|---|
| No connectivity on submit | Report data + audio saved to local SQLite queue; shown as "Pending" in History |
| Connectivity restored | Background sync uploads in order; History badge updates |
| Partial upload failure | Retry with exponential backoff (3 attempts); then "Sync failed" + manual retry |
| Duplicate (same diamond_id + type within 5 min) | Server deduplication: return existing report ID |

Audio uploads to R2 before the report row is inserted. If audio upload fails, whole submission retries.

---

## 10. Notifications (v1: local only)

| Trigger | Notification |
|---|---|
| Queued report synced | "Report for diamond #[id] submitted" |
| Chain attribution available | "Responsibility attributed: [Name] — diamond #[id]" (management + admin only) |
| Sync failed after retries | "Report sync failed — tap to retry" |

FCM server-push deferred to v2.

---

## 11. Localisation

- **Languages:** English (default), Gujarati (`gu`), Hindi (`hi`)
- Worker-facing strings fully translated in all three languages
- Management / Admin UI: English only (v1)
- Language preference stored per user (`language_pref [en | gu | hi]`), synced to backend
- All translated strings in ARB files (Flutter) or XML string resources (KMP)

---

## 12. Security & Auth

| Area | v1 approach | v2 path |
|---|---|---|
| Passwords | Plaintext stored; admin can reveal via eye toggle | bcrypt hashing |
| Auth tokens | JWT (access 15 min / refresh 30 days) in secure storage | Keep |
| Transport | HTTPS (self-signed cert for local deployment) | Valid cert via Let's Encrypt |
| Role enforcement | Server-side on every endpoint | Keep |
| Audio | R2 private ACL; short-lived signed URLs | Keep |

---

## 13. Performance Requirements

| Metric | Target |
|---|---|
| App cold start | < 2 s on mid-range Android |
| Report submission (online) | Full pipeline (upload + STT + translate + Gemini) < 15 s |
| Dashboard load | < 1 s cached, < 3 s fresh fetch |
| Dashboard auto-refresh | 10-second interval, no visible jank |
| Audio recording max duration | 120 seconds |

---

## 14. Analytics & Observability (v1 minimal)

- Crash reporting: Firebase Crashlytics
- API error rate logged server-side (structured logs)
- No product analytics (Amplitude / Mixpanel) in v1

---

## 15. Open Questions

| # | Question | Owner | Decision needed by |
|---|---|---|---|
| 1 | Flutter vs Kotlin Multiplatform — final call? | Tech lead | Before sprint 1 |
| 2 | Backend language — FastAPI vs Fastify? | Tech lead | Before sprint 1 |
| 3 | Local server vs cloud for v1 deployment? | Anjali | Before sprint 2 |
| 4 | Personal phones vs shared tablets? (affects auth UX) | Factory ops | Before sprint 1 |
| 5 | iOS support in v1 or Android-only? | Anjali | Before sprint 1 |
| 6 | Sarvam STT rate limits under concurrent floor submissions? | Tech lead | Sprint 2 |
| 7 | Diamond ID: dropdown (known IDs) vs free-text vs QR scan? Design shows dropdown + QR icon. | Anjali + Tech lead | Before sprint 1 |
| 8 | User deletion: Design shows a Delete button on User Detail. Keep Delete (hard) or replace with Deactivate (soft)? | Anjali | Before sprint 2 |

---

## 16. Out-of-Scope (Parking Lot)

- Completed-diamond / production-output ingestion
- Chatbot with live DB query / function-calling access
- Repeat-offender leaderboard view
- Bulk user import via CSV
- Audit log (who edited which user, when)
- Multi-language management UI
- Enterprise SSO / LDAP
- Hindi for Management / Admin UI (v1 English only)

---

## 17. Milestones (indicative)

| Sprint | Deliverables |
|---|---|
| Sprint 1 (2 weeks) | Auth (login screen), worker report screen (tab toggle + mic + transcript), worker history screen |
| Sprint 2 (2 weeks) | Backend API + Sarvam STT + Gemini translation integration, report submission E2E, offline queue |
| Sprint 3 (2 weeks) | Gemini per-report analysis + chain attribution, submission result banner |
| Sprint 4 (2 weeks) | Dashboard (KPI cards + chart + Report Details drill-down) |
| Sprint 5 (2 weeks) | Admin Users list + User Detail + Create/Edit User, Settings screen |
| Sprint 6 (2 weeks) | Diamond Assistant chatbot, Management profile, all Profile screens |
| Sprint 7 (1 week) | Gujarati + Hindi localisation, polish, QA, UAT |
