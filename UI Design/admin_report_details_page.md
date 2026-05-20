# Admin / Management — Process Drill-down (Report Details) Page — Figma Design Spec

**Type:** Pure Figma mockup. NO code is written or edited anywhere. Output is one new Figma frame.

**File:** Add a new frame to the existing Figma file `gM9sCiUJzoh8Pv4EOMORNX`.

**Style references:**
- [../screenshots/home.png](../screenshots/home.png) — Jaimin Craft palette
- [../screenshots/userdetails.png](../screenshots/userdetails.png) — Performance card pattern
- [../screenshots/history page.png](../screenshots/history page.png) — list-card pattern

---

## Context

When admin or management taps a process bar on the Dashboard, this page opens — showing the per-process drill-down (KPIs + every report for that process).

**Latest design change (per user request):** the three severity levels (Severe / Moderate / Low) are no longer shown as separate columns. They are **merged into a single "Bug Levels" cell** that shows all three breakdowns inline using colored dot-pills + numbers. This saves vertical space and lets the Performance card stay one row (3 columns) instead of two rows.

---

## Frame metadata

- **Name:** `Admin — Report Details (Bruting)`
- **Size:** 390 × 900 px
- **Position:** x = 2580, y = 0 in file `gM9sCiUJzoh8Pv4EOMORNX`
- **Background:** `#F3F4F6`
- **Corner radius:** 40 px

---

## Top bar (y ≈ 40, height 56)

Three-zone, gutters 18 px:

- **Left:** back-arrow SVG inside 32 × 32 transparent area, dark icon `#1F2937`
- **Center (stacked):**
  - Title **"Report Details"** — Inter Bold 16 px, `#1F2937`
  - Sub-line **"Bruting · Monthly"** — Inter Regular 11 px, `#6B7280`
- **Right:** `✕` close SVG inside 32 × 32 light-gray pill `#F3F4F6`, gray icon

---

## Period filter row (y ≈ 110)

Three small pills horizontally, 10 px gap, 24 px gutter:

- **Daily** — 70 × 32 px, white card, 1 px light border
- **Weekly** — same style
- **Monthly** — **ACTIVE** → orange fill `#FF6B35`, white text, Inter Semi-Bold 12 px, soft orange shadow

---

## Performance card (y ≈ 160) — **UPDATED LAYOUT**

White card, 342 × auto, 16 px corner radius, 1 px border `#E5E7EB`, soft drop shadow, 20 px padding.

- Section label **"PERFORMANCE — BRUTING"** — Inter Semi-Bold 11 px CAPS, `#6B7280` (top-left, 16 px below it the stats)

### Stats row (HORIZONTAL, 3 cells, equal width, 1 px `#F3F4F6` vertical dividers between them)

Each cell is a vertical stack, centered, 6 px gap:

| Cell 1 | Cell 2 | Cell 3 |
|---|---|---|
| **TOTAL REPORTS** label (10 px CAPS gray) | **WORKERS** label | **DEFECT %** label |
| `8` (Bold 28 px, orange `#FF6B35`) | `4` (Bold 28 px, dark `#1F2937`) | `8%` (Bold 28 px, orange `#FF6B35`) |

### Bug Levels row (NEW — replaces the second row of 3 separate cells)

Below a thin `#F3F4F6` horizontal divider with 16 px margin:

- Section sub-label **"BUG LEVELS"** — Inter Semi-Bold 10 px CAPS, `#6B7280`, 8 px below divider
- 12 px below the label, **single horizontal row** with 3 colored stat pills, 10 px gap, left-aligned:

#### Pill design (each is a horizontal auto-layout chip)

- Padding 6 px / 12 px, 14 px corner radius
- Background = soft tint of that severity color (`#FFE5E5` / `#FFF6E2` / `#E5F8EF`)
- Contents (left → right, 8 px gap):
  - 8 × 8 px solid dot in severity color
  - **Number** — Inter Bold 14 px, severity color
  - **Label** — Inter Medium 11 px, severity color (slightly muted)

| Pill | Dot + text color | Tint background | Sample |
|---|---|---|---|
| Severe | `#FF4D4D` | `#FFE5E5` | ● `5` Severe |
| Moderate | `#F59E0B` | `#FFF6E2` | ● `2` Moderate |
| Low | `#10B981` | `#E5F8EF` | ● `1` Low |

### OPTIONAL stacked-bar variant (visual alternative below the pills)

If the user wants the distribution to be even more visual, add a 6 px-tall stacked horizontal bar below the 3 pills, full-width inside the card, 3 px radius:

- Left 62.5% red `#FF4D4D` (5 / 8)
- Middle 25% amber `#F59E0B` (2 / 8)
- Right 12.5% green `#10B981` (1 / 8)

This is a single horizontal bar that visually shows the severity mix at a glance.

---

## Search & filter (y ≈ 360)

- **Search bar** — 342 × 44 px, white pill, 22 px radius, 1 px border, magnifier SVG + placeholder **"Search by Diamond ID or worker…"** (Inter Regular 13 px, `#9CA3AF`)
- 12 px below: filter pills row (2 pills, 10 px gap, gutter 24 px)
  - **All Types** (Receive / Problem / All) — 110 × 32 px white pill + caret
  - **All Severity** (Severe / Moderate / Low / All) — 120 × 32 px white pill + caret

---

## Reports section (y ≈ 460)

Section header row (24 px gutter):
- Left: **"Reports (8)"** — Inter Bold 14 px, dark
- Right: tiny **"Sort: Newest"** caret link — Inter Medium 11 px, `#6B7280`

### Report card (342 × ~210 px, 12 px gap)

White, 14 px corner radius, 1 px light border, soft shadow, 16 px padding, 12 px gap between sections.

```
┌─────────────────────────────────────────────┐
│ ●  D-67676              [● Severe] [Problem]│  ← header row
│    Anita Yadav · Bruting                    │  ← sub-line
│ ─────────────────────────────────────────── │
│ "ઘસતા ઘસતા હીરો કાળો પડી ગયો છે"             │  ← Gujarati transcript
│ ─────────────────────────────────────────── │
│ [▶ ━━━━━━━━━━ 0:08 / 0:08 🔊]                │  ← audio player
│                                             │
│ 15 May 2026, 11:08          DEFECT: Burn    │  ← footer
└─────────────────────────────────────────────┘
```

#### Row 1 — Header
- 8 × 8 px orange dot `#FF6B35`
- **Diamond ID** Inter Bold 14 px dark
- Spacer (grow)
- **Severity chip** (matches the new bug-level pill style — soft tint background + colored dot + label)
- **Type chip** (Receive blue tint / Problem orange tint)

#### Row 2 — Sub-line
- `{worker_name} · {dept}` Inter Regular 11 px gray

#### Row 3 — Gujarati transcript chip
- Background `#F3F4F6`, 12 px padding, 10 px radius
- Inter Regular 13 px dark, up to 2 lines

#### Row 4 — Audio player
- 310 × 40 px, light gray track + orange progress fill
- Orange play/pause circle (32 × 32) on left
- Timestamp on right Inter Regular 11 px gray
- Tiny volume SVG

#### Row 5 — Footer
- Date Inter Regular 11 px gray
- Right: `DEFECT: Burn` Inter Medium 11 px gray

### Sample cards (real data)

| # | Diamond | Worker | Type | Severity | Defect | Transcript | Time |
|---|---|---|---|---|---|---|---|
| 1 | D-67676 | Anita Yadav | Problem | Severe | Burn | ઘસતા ઘસતા હીરો કાળો પડી ગયો છે | 15 May, 11:08 |
| 2 | D-89898 | Bharat Jain | Problem | Severe | Crack | હું ઘસતો હતો ત્યારે હીરો બે ટુકડામાં તૂટી ગયો | 15 May, 15:24 |
| 3 | D-34232 | Mohan Das | Receive | Severe | Polishing crack | આજે ઘસતા ઘસતા ક્રેક પડી ગયો છે હીરામાં | 16 May, 12:52 |

---

## Bottom nav (y ≈ 820)

Pill 200 × 56 px, white, 28 px radius, soft shadow. Centered.
3 SVG icons (matching the Worker Profile pattern):
- **Home — ACTIVE** (Dashboard) → orange `#FF6B35` filled circle 44 × 44, white house glyph
- Chat (gray)
- Person (gray)

(Active = Home because this drill-down is part of the Dashboard flow.)

---

## Color tokens (Jaimin Craft palette)

| Use | Hex |
|---|---|
| Background | `#F3F4F6` |
| Card surface | `#FFFFFF` |
| Primary orange | `#FF6B35` |
| Soft orange tint | `#FFEFE8` |
| Text dark | `#1F2937` |
| Text gray | `#6B7280` |
| Subtle / placeholder | `#9CA3AF` |
| Light border | `#E5E7EB` |
| Soft fill | `#F3F4F6` |
| **Severe** red | `#FF4D4D` / tint `#FFE5E5` |
| **Moderate** amber | `#F59E0B` / tint `#FFF6E2` |
| **Low** green | `#10B981` / tint `#E5F8EF` |
| Receive blue | `#3B82F6` / tint `#EAF2FE` |

## Typography (Inter)

| Element | Style |
|---|---|
| Page title | Bold 16 |
| Sub-title | Regular 11 |
| Section CAPS label | Semi-Bold 10–11 |
| Stat big number | Bold 28 |
| Bug level pill number | Bold 14 |
| Bug level pill label | Medium 11 |
| Diamond ID | Bold 14 |
| Body | Regular 13 |
| Footer / meta | Regular / Medium 11 |

---

## Layout summary

```
┌─────────────────────────────────┐
│ ←  Report Details          ✕    │
│    Bruting · Monthly            │
├─────────────────────────────────┤
│  [Daily] [Weekly] (Monthly)     │
│                                 │
│ ┌────────────────────────────┐  │
│ │ PERFORMANCE — BRUTING      │  │
│ │  TOTAL    WORKERS   DEFECT │  │
│ │    8        4         8%   │  │
│ │ ────────────────────────── │  │
│ │ BUG LEVELS                 │  │
│ │ [●5 Severe] [●2 Mod] [●1 Lo]│ │
│ │ ━━━━━━━━━━━━━━━━━━━━━━━━ ──│  │  (optional stacked bar)
│ └────────────────────────────┘  │
│                                 │
│  [🔍 Search…           ]        │
│  [All Types ▾] [All Severity ▾] │
│                                 │
│  Reports (8)        Sort ▾      │
│ ┌────────────────────────────┐  │
│ │ Report card                │  │
│ └────────────────────────────┘  │
│ ┌────────────────────────────┐  │
│ │ Report card                │  │
│ └────────────────────────────┘  │
│                                 │
│     [ (🏠)   💬   👤 ]           │
└─────────────────────────────────┘
```

---

## Verification

- Confirm new frame visible: `Admin — Report Details (Bruting)`
- Visual checks:
  - Top bar: back · title · sub-line · close
  - Period pills with Monthly active in orange
  - **Performance card has just ONE Stats row** (Total Reports / Workers / Defect %) — not two rows
  - **"BUG LEVELS"** sub-section below the divider with **3 inline colored pills** (Severe red / Moderate amber / Low green)
  - Optional stacked bar below the pills if added
  - Search + 2 filter pills
  - Report cards with chip pair (severity + type), Gujarati transcript chip, audio player, footer
  - Bottom nav: Home icon active in orange circle
