# Admin — Users List & User Detail Pages — Figma Design Spec

**Type:** Pure Figma mockup. NO code is written or edited anywhere. Output is two new Figma frames only.

**File:** Add two new frames to the existing Figma file `gM9sCiUJzoh8Pv4EOMORNX`, beside the existing Worker pages.

**Style references:**
- [../screenshots/userhome.png](../screenshots/userhome.png) — the **list page** layout
- [../screenshots/userdetails.png](../screenshots/userdetails.png) — the **detail page** layout
- [../screenshots/home.png](../screenshots/home.png) — overall Jaimin Craft palette / typography

---

## Context

The Diamond QC app has an admin-only **Users Management** view — currently a flat dataframe table. The admin needs a **mobile-style redesign** in two screens that mirror the reference screenshots:

1. **Users List page** — every user on one scrolling page with quick stats per row
2. **User Detail page** — full profile + performance metrics + recent reports, opened when admin taps a row

Both screens use the same Jaimin Craft light theme + orange accents already locked in for the worker pages.

---

# PAGE 1 — Users List

## Frame metadata
- **Name:** `Admin — Users List`
- **Size:** 390 × 844 px (iPhone 14 Pro)
- **Background:** `#FAFAFB`
- **Corner radius:** 40 px
- **Clip contents:** true

## Top bar (y ≈ 58)
Three-zone row, gutters 24 px:
- **Left zone (~80 px):** empty / spacer
- **Centered:**
  - Title **"Users"** — Inter Bold 22 px, `#1F2937`
  - Sub-line **"24 Users"** — Inter Regular 11 px, `#9CA3AF` (centered, 4 px below title)
- **Right zone:** `+ Add` pill button — 88 × 38 px, orange `#FF6B35`, white plus SVG icon (16 px) + text Inter Semi-Bold 13 px white, soft orange shadow

## Search bar (y ≈ 130)
- 342 × 44 px, white pill, 22 px radius, 1 px border `#E5E7EB`
- Magnifier SVG (16 px gray) on left
- Placeholder **"Search by name, username or emp code…"** Inter Regular 13 px, `#9CA3AF`

## Filter row (y ≈ 188)
Three filter pills (10 px gap, 24 px gutter):
- **Role** dropdown — 120 × 36 px (Worker / Management / Admin / All)
- **Department** dropdown — 142 × 36 px
- **Status** dropdown — 110 × 36 px (Active / Inactive / All)

Each pill: white card, 18 px radius, light border `#E5E7EB`, label Inter Medium 12 px + caret-down SVG (12 px, gray).

## User cards list (y ≈ 280 onward)
Each row card: 342 × ~112 px, white, 14 px corner radius, 1 px border `#E5E7EB`, soft drop shadow.
Cards stacked vertically with 10 px gap, gutter 24 px.

### Card internal layout
```
●  1   Ramesh Patel                              Polishing
       vaw03010001 · Worker
       REPORTS         SEVERE        FAULT %
       12              3             25%
```

**Row 1 — Header (≈ 22 px, HORIZONTAL):**
- 8 × 8 px **status dot** — green `#10B981` for active, red `#FF4D4D` for inactive
- **Index number** `1`, `2`, `3` — Inter Regular 12 px, `#9CA3AF`
- **Full name** — Inter Bold 14 px, `#1F2937`
- Spacer (grow)
- Right-aligned **Department** or **Process** — Inter Regular 11 px, `#9CA3AF`

**Row 2 — Sub-line (≈ 16 px):**
- `{emp_code} · {Role}` — Inter Regular 11 px, `#6B7280`

**Row 3 — Stats (≈ 36 px, 3 columns):**

| Column | Label (CAPS 10 px gray) | Value (Semi-Bold 14 px) |
|---|---|---|
| Reports | REPORTS | total reports filed (dark) — `—` for admin/management |
| Severe | SEVERE | count of Severe reports (green `#10B981` if 0, dark if >0) |
| Fault rate | FAULT % | (severe ÷ total)% — orange `#FF6B35` if >10%, gray otherwise |

### Sample data (real users from DB)

| # | Status | Name | emp_code | Role | Dept | Reports | Severe | Fault % |
|---|---|---|---|---|---|---|---|---|
| 1 | ● green | Ramesh Patel | vaw03010001 | Worker | Polishing | 12 | 3 | 25% |
| 2 | ● green | Anita Yadav | vaw01040004 | Worker | Bruting | 8 | 5 | 62% |
| 3 | ● green | Mohan Das | vaw02020003 | Worker | Polishing | 6 | 2 | 33% |
| 4 | ● green | Suresh Patel | — | Management | — | — | — | — |
| 5 | ● red | Geeta Nair | vaw03010005 | Worker | Faceting | 3 | 0 | 0% |
| 6 | ● green | Bharat Jain | vaw01030007 | Worker | Polishing | 5 | 3 | 60% |
| 7 | ● green | Vijay Sharma | vaw02010002 | Worker | Faceting | 4 | 1 | 25% |

## Bottom nav (y ≈ 760)
Pill 240 × 60 px, white, 30 px radius, soft shadow. Four SVG icons evenly spaced:
- Grid (gray) — inactive
- Clipboard (gray) — inactive
- **Person — ACTIVE** — orange `#FF6B35` filled 46 × 46 circle behind white person glyph
- More-dots (gray) — inactive

---

# PAGE 2 — User Detail

## Frame metadata
- **Name:** `Admin — User Detail`
- **Size:** 390 × 900 px
- **Background:** `#FAFAFB`
- **Corner radius:** 40 px

## Top bar (y ≈ 58)
- **Left:** back-arrow SVG inside 40 × 40 transparent button (gray icon `#6B7280`)
- **Center (stacked):**
  - **Name** — Inter Bold 22 px, `#1F2937` (e.g. "Anita Yadav")
  - Sub-line — Inter Regular 12 px, `#9CA3AF` — `"Bruting · Active"` (Process · Status)
- **Right:** `🗑 Delete` outline pill — 92 × 36 px, white, red border `#FF4D4D`, red text + trash SVG (`#FF4D4D`), Inter Semi-Bold 12 px

## Performance card (y ≈ 144)
342 × auto, white, 16 px radius, 1 px border, soft shadow, 18 px padding, 16 px gap.
- Section label **"PERFORMANCE"** — Inter Semi-Bold 10 px CAPS, `#6B7280`
- **Row 1 (3 columns):**
  - **TOTAL REPORTS** label + value `12` (Bold 22 px, dark)
  - **SEVERE** label + value `5` (Bold 22 px, red `#FF4D4D` if > 0, otherwise dark)
  - **MODERATE** label + value `4` (Bold 22 px, amber `#F59E0B`)
- **Row 2 (3 columns):**
  - **LOW** label + value `3` (Bold 22 px, green `#10B981`)
  - **FAULT RATE** label + value `41%` (Bold 22 px, orange `#FF6B35`)
  - **STATUS** label + value `Active` (Bold 22 px, green) or `Inactive` (red)

## Info card (y ≈ 320)
342 × auto, white, 16 px radius, 1 px border, soft shadow, 18 px padding, 14 px gap.
- Section label **"DETAILS"** — Inter Semi-Bold 10 px CAPS, gray (top-left)
- Right: `✏ Edit` outline pill (76 × 32 px, white, light border, dark text + pencil SVG)
- **Rows (key on left, value on right, both 13 px):**
  - `Emp Code` → `vaw01040004`
  - `Username` → `anita_y`
  - `Role` → `Worker`
  - `Department` → `Bruting`
  - `Process` → `Bruting`
  - `Factory` → `vaw` · `Floor` → `01` · `Table` → `04` (compact row)
  - `Mobile` → `+91 98xx xx xxxx`
  - `Address` → `123, Polishing Lane, Surat`

## Assignment History card (y ≈ 520)
342 × auto, white, 16 px radius, 1 px border, soft shadow, 18 px padding, 12 px gap.
- Title row: **"Recent Reports (12)"** — Inter Bold 14 px, dark
- Filter row (2 pills, 10 px gap, smaller pills 110 × 32):
  - **All Types** (Receive / Problem / All)
  - **All Severity** (Severe / Moderate / Low / All)

### Report row item (~88 px each, soft divider below)
```
D-67676            ● Severe         INPUT      OUTPUT     FAULT
Bruting · May 15                    1          —          ✓
```

- **Diamond ID** (Inter Semi-Bold 13 px, orange `#FF6B35` — link style)
- Severity chip on right: small pill 10 × 4 padding, label "● Severe" / "● Moderate" / "● Low" colored accordingly
- Sub-line: `{process_name} · {date}` — Inter Regular 11 px, gray
- 3-column stat row (smaller, Medium 12 px):
  - **TYPE** — `Receive` or `Problem`
  - **DEFECT** — short label or `—`
  - **STATUS** — `✓ Done` (green) or `Pending` (amber)

Show 2–3 sample rows in the mockup.

## Bottom nav (y ≈ 820)
Same shared 4-icon pill as the list page, **Person icon ACTIVE** (orange circle behind white glyph).

---

## Color tokens (Jaimin Craft palette)

| Use | Hex |
|---|---|
| Background | `#FAFAFB` |
| Card surface | `#FFFFFF` |
| Primary orange | `#FF6B35` |
| Soft orange tint | `#FFEFE8` |
| Text dark | `#1F2937` |
| Text gray | `#6B7280` |
| Subtle / placeholder | `#9CA3AF` |
| Light border | `#E5E7EB` |
| Soft fill | `#F3F4F6` |
| Severe red | `#FF4D4D` |
| Moderate amber | `#F59E0B` |
| Low / Active green | `#10B981` |

## Typography (Inter)

| Element | Style |
|---|---|
| Page title | Bold 22 |
| Sub-title | Regular 12 |
| Section CAPS label | Semi-Bold 10 |
| Card title | Bold 14 |
| Stat big number | Bold 22 |
| Stat regular value | Semi-Bold 14 |
| Stat label CAPS | Medium 10 |
| Sub-text | Regular 11 |
| Body | Regular 13 |

---

## Verification

- Confirm two new frames in Figma: `Admin — Users List` and `Admin — User Detail`
- Visual checks against userhome.png and userdetails.png:
  - List page: title + count, search, filter pills, list cards with 3-stat row, bottom nav Person active
  - Detail page: back/name/Delete header, Performance card with stat cells, Info card with Edit button, Recent Reports with sub-filters and rows
  - Bottom nav: Person icon highlighted in orange circle on both screens
