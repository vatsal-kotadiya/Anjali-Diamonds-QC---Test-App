# Overview KPIs — Small Card Set — Figma Design Spec

**Type:** Single component spec. NO code, no full page — just the **KPI card row** for the top of any analytics page.

---

## Purpose

Show the key analytics numbers as a **row of small individual cards** — each KPI gets its own card. The **Bug Levels card is a single combined KPI** that shows all 3 severity counts inside one card (instead of 3 separate Severe/Moderate/Low cards).

So the row has **4 small cards total**, not 6 — and not one merged super-card.

---

## Component metadata

- **Name:** `KPI Card Row`
- **Width:** 342 px (parent gutter 24 px on 390 frame)
- **Height:** ~108 px
- **Layout:** HORIZONTAL auto-layout, 4 cards, 10 px gap between

Each individual card is small (compact) — designed to fit 4 across on a mobile screen.

---

## Individual KPI card (small, repeating element)

- **Width:** ~78 px (auto — flex-grow to share the row)
- **Height:** 108 px
- **Background:** white, 14 px corner radius, 1 px border `#E5E7EB`, soft drop shadow
- **Padding:** 12 px all around
- **Inner layout:** VERTICAL auto-layout, 6 px gap, items left-aligned

### Card contents (top → bottom)

1. **Big number** — Inter Bold 24 px, color per stat
2. **CAPS label** — Inter Medium 10 px, `#6B7280`, can wrap to 2 lines

---

## The 4 cards in the row

### Card 1 — Total Reports
- Number: `10` — color `#1F2937` (dark)
- Label: `TOTAL REPORTS`

### Card 2 — Problem Reports
- Number: `2` — color `#FF6B35` (orange — admits-fault signal)
- Label: `PROBLEM REPORTS`

### Card 3 — Workers Involved
- Number: `6` — color `#3B82F6` (blue — informational)
- Label: `WORKERS INVOLVED`

### Card 4 — **Bug Levels (combined — 1 single card with 3 inline numbers)**

Same card frame and size as the others (78 × 108 px), but the interior shows the 3 severity counts stacked compactly:

```
┌──────────────┐
│  ● 5         │   ← Severe row (red dot + bold red number)
│  ● 2         │   ← Moderate row (amber dot + bold amber number)
│  ● 1         │   ← Low row (green dot + bold green number)
│              │
│  BUG LEVELS  │   ← single CAPS label at the bottom
└──────────────┘
```

#### Inner structure of the Bug Levels card

- VERTICAL auto-layout, 6 px gap, 12 px padding
- Top section: 3 mini rows, each a HORIZONTAL line of `[dot 6×6 px]` + `[number Bold 14 px in severity color]`, 6 px gap, 3 px row spacing
- Bottom: CAPS label "BUG LEVELS" Inter Medium 10 px gray

Severity tokens:

| Level | Dot color | Number color |
|---|---|---|
| Severe | `#FF4D4D` | `#FF4D4D` |
| Moderate | `#F59E0B` | `#F59E0B` |
| Low | `#10B981` | `#10B981` |

---

## Visual mock — full row

```
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│          │ │          │ │          │ │ ●5       │
│   10     │ │    2     │ │    6     │ │ ●2       │
│          │ │          │ │          │ │ ●1       │
│ TOTAL    │ │ PROBLEM  │ │ WORKERS  │ │          │
│ REPORTS  │ │ REPORTS  │ │ INVOLVED │ │ BUG      │
│          │ │          │ │          │ │ LEVELS   │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
   ↑ dark      ↑ orange      ↑ blue     ↑ multi-color
```

---

## Variants

### Variant A — default (shown above, 4 cards in 1 row)

### Variant B — 5-card row (when Defect % is shown)

Adds a 5th small card (cards shrink to ~64 px wide):
- Number: `8%` — color `#FF6B35` (orange)
- Label: `DEFECT %`

### Variant C — 2 × 2 grid (very narrow screens, < 360 px)

Wrap 4 cards into a 2 × 2 grid instead of 1 × 4. Cards become wider (~155 px each).

---

## Empty state

If all the regular KPIs are 0:
- Number stays `0` but in gray `#9CA3AF`
- Cell background subtle gray `#FAFAFA` instead of pure white

For Bug Levels with zero of everything:
- Show a single subtle gray pill inside the card: `—` Inter Bold 14 px gray
- Label still reads `BUG LEVELS`

---

## Color tokens

| Use | Hex |
|---|---|
| Card surface | `#FFFFFF` |
| Card border | `#E5E7EB` |
| Label gray | `#6B7280` |
| Total (neutral) | `#1F2937` |
| Problem (orange) | `#FF6B35` |
| Workers (blue) | `#3B82F6` |
| Severe red | `#FF4D4D` |
| Moderate amber | `#F59E0B` |
| Low green | `#10B981` |
| Empty / subtle | `#9CA3AF` |

## Typography (Inter)

| Element | Style |
|---|---|
| Big number (regular KPI) | Bold 24 |
| Bug-level number | Bold 14 |
| CAPS label | Medium 10 |

---

## Layout summary

```
Row width: 342 px
Row height: 108 px
Cards: 4 × ~78 px each, 10 px gap
Each card: 14 px radius, 1 px border, soft shadow, 12 px padding
```

---

## Verification

- 4 separate small cards in one horizontal row (not 1 merged super-card)
- First 3 cards show a big number (Bold 24 px) in their meaningful color + CAPS label
- 4th card is the **Bug Levels** card — single card with **3 stacked severity counts** (●5 / ●2 / ●1) and ONE label "BUG LEVELS"
- All cards share the same width and height
- Row fits within 342 px on a 390 px mobile screen
- No horizontal scrolling
