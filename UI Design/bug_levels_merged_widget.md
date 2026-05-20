# Bug Levels — Single KPI Card — Figma Design Spec

**Type:** Single component spec. NO code, no full page — just the **Bug Levels** card that fits inside the KPI row alongside the other 3 small KPIs.

This replaces both:
- The old 3-column row (Severe / Moderate / Low as 3 separate cells)
- The old wide pill row variant

…with **one small KPI card** that holds all 3 severity counts compactly inside it.

---

## Component metadata

- **Name:** `Bug Levels KPI Card`
- **Width:** ~78 px (matches the other small KPI cards in the row)
- **Height:** 108 px
- **Background:** white card, 14 px corner radius, 1 px border `#E5E7EB`, soft drop shadow
- **Padding:** 12 px all around
- **Inner layout:** VERTICAL auto-layout, 6 px gap, items left-aligned

---

## Card contents (top → bottom)

### Section 1 — 3 severity rows (stacked, 3 px gap)

Each row is a tiny HORIZONTAL flex line: `[dot]` + `[number]`

| Row | Dot (6 × 6 px solid) | Number (Inter Bold 14 px) |
|---|---|---|
| Severe | `#FF4D4D` | `5` in `#FF4D4D` |
| Moderate | `#F59E0B` | `2` in `#F59E0B` |
| Low | `#10B981` | `1` in `#10B981` |

Row spacing 3 px between, 6 px gap between dot and number.

### Section 2 — Card label (at the bottom)

- **CAPS label** — Inter Medium 10 px, color `#6B7280`
- Text: `BUG LEVELS`
- Left-aligned, 8 px above the bottom edge of the card

---

## Visual mock

```
┌────────────┐
│            │
│  ● 5       │  ← Severe (red)
│  ● 2       │  ← Moderate (amber)
│  ● 1       │  ← Low (green)
│            │
│ BUG LEVELS │  ← single CAPS label
│            │
└────────────┘
   ↑ 78 × 108 px
```

---

## Where it sits

This card is the 4th card in the [Overview KPIs row](overview_kpis_merged_widget.md). The full row has 4 cards:

```
[ Total Reports ]  [ Problem Reports ]  [ Workers Involved ]  [ Bug Levels (this card) ]
       10                  2                     6                ● 5 / ● 2 / ● 1
```

All 4 cards share the same dimensions (78 × 108 px) for a clean grid look.

---

## Empty state

If all three counts are 0:
- Show a single subtle pill inside the card:
  - `—` Inter Bold 14 px, color `#9CA3AF`
  - Centered horizontally
- Label still reads `BUG LEVELS` at the bottom

---

## Color tokens

| Use | Hex |
|---|---|
| Card surface | `#FFFFFF` |
| Card border | `#E5E7EB` |
| Label gray | `#6B7280` |
| Severe | `#FF4D4D` |
| Moderate | `#F59E0B` |
| Low | `#10B981` |
| Empty / subtle | `#9CA3AF` |

## Typography (Inter)

| Element | Style |
|---|---|
| Severity number | Bold 14 |
| CAPS label | Medium 10 |

---

## Verification

- Card dimensions: 78 × 108 px (same as the other 3 small KPI cards)
- Three severity rows stacked vertically inside: ● 5 (red), ● 2 (amber), ● 1 (green)
- Each row has a 6 × 6 solid dot in its severity color + Bold 14 px number in matching color
- ONE single CAPS label `BUG LEVELS` at the bottom of the card
- Card uses the same border / radius / shadow / padding as the sibling KPI cards in the row
