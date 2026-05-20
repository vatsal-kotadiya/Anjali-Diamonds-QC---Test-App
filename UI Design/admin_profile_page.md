# Admin — Profile Page — Figma Design Spec

**Type:** Pure Figma mockup. NO code is written or edited anywhere. Output is one new Figma frame.

**File:** Add a new frame to the existing Figma file `gM9sCiUJzoh8Pv4EOMORNX`.

**Style reference:** The user-approved **Worker Profile** design (see screenshot uploaded 2026-05-19). The Admin Profile must visually mirror that exact layout — same cards, same spacing, same colors. The only differences are:
- Title says **"Admin Profile"**
- Avatar initial reflects admin name (e.g. **"S"** for System Administrator)
- Account card has admin-relevant fields (no Department/Process, since admin isn't tied to manufacturing stages)
- Sample data uses real admin user (`admin`, emp_code `adm00000001`)

---

## Frame metadata

- **Name:** `Admin — Profile`
- **Size:** 390 × 844 px (iPhone 14 Pro)
- **Position:** x = 3000, y = 0 in file `gM9sCiUJzoh8Pv4EOMORNX`
- **Background:** `#F3F4F6` (soft light gray, like the worker profile screenshot)
- **Corner radius:** 40 px

---

## Top bar (y ≈ 40, height 56)

Three-zone, gutters 18 px:

- **Left:** back-arrow SVG inside 32 × 32 transparent area (dark icon `#1F2937`)
- **Center:** title **"Admin Profile"** — Inter Bold 16 px, `#1F2937`
- **Right:** spacer (empty 32 × 32 area for balance)

---

## Identity card (y ≈ 110)

White card, 342 × 90 px, 16 px corner radius, 1 px border `#E5E7EB`, soft drop shadow, 16 px padding.
Horizontal auto-layout with 16 px gap, items vertically centered.

**Contents (left → right):**

1. **Avatar** — 56 × 56 px orange circle `#FF6B35`, drop shadow
   - White uppercase initial **"S"** (or first letter of admin's full name) — Inter Bold 22 px white, centered
   - Small orange pencil-edit badge (16 × 16) at bottom-right corner of the avatar, white border 2 px

2. **Identity column** (vertical, 4 px gap)
   - **Full name** "System Administrator" — Inter Bold 16 px, `#1F2937`
   - **Emp code** `adm00000001` — Inter Regular 12 px, `#6B7280`

---

## Account card (y ≈ 220)

White card, 342 × auto, 16 px radius, 1 px border, soft shadow, 18 px padding, 14 px gap between rows.

### Header row
- Left: **"ACCOUNT"** — Inter Semi-Bold 11 px CAPS, `#6B7280`
- Right: **"Edit"** pill — 60 × 28 px, soft orange tint `#FFEFE8`, orange text `#FF6B35` Inter Semi-Bold 12 px, 14 px radius

### Detail rows (each ~38 px tall, divided by a 1 px `#F3F4F6` separator below)

Each row uses HORIZONTAL layout — label on left, value on right, both vertically centered:

| Label (Medium 11 px CAPS, `#6B7280`) | Value (Regular 13 px, `#1F2937`, right-aligned) |
|---|---|
| USERNAME | `admin` |
| ROLE | `Administrator` |
| MOBILE | `+91 98xx xx xxxx` |
| ADDRESS | `—` |

(No Department, no Process — admin isn't bound to manufacturing stages. Drop those rows entirely.)

---

## Language card (y ≈ 470)

White card, 342 × auto, 16 px radius, 1 px border, soft shadow, 18 px padding.

- **Title** "Language" — Inter Bold 14 px, `#1F2937` (top-left)
- 14 px below, 3-pill segmented control (horizontal auto-layout, 14 px gap, centered):

Each pill is 80 × 70 px, centered text, vertical stack:
- **Top line:** English label (Inter Semi-Bold 14 px)
- **Bottom line:** Native script (Inter Regular 11 px gray)

| Pill | State | Top text | Bottom text | Style |
|---|---|---|---|---|
| 1 | **Selected** | English | English | 2 px orange border `#FF6B35`, top text orange, soft glow |
| 2 | Inactive | ગુજરાતી | Gujarati | no border, gray text |
| 3 | Inactive | हिंदी | Hindi | no border, gray text |

(Same three-language toggle as the Worker Profile.)

---

## Sign Out button (y ≈ 620)

White full-width card 342 × 56 px, 14 px radius, 1 px light border, soft shadow.

- Horizontal auto-layout, 14 px gap, vertically centered, 18 px padding
- Left: **icon container** — 36 × 36 px, light red tint `#FEE6E6`, 10 px radius, contains a sign-out-arrow SVG (18 px, red `#FF4D4D`)
- **"Sign Out"** label — Inter Semi-Bold 14 px, red `#FF4D4D`

---

## Bottom nav (y ≈ 740)

Pill 200 × 56 px, white, 28 px corner radius, soft drop shadow. Centered horizontally.

Three SVG icons evenly spaced (no emoji):
- Home (gray `#6B7280`, 24 px) — inactive
- Clock (gray, 24 px) — inactive
- **Person — ACTIVE** — 44 × 44 px orange `#FF6B35` filled circle, white person glyph centered

---

## Color tokens (Jaimin Craft palette, matches Worker Profile exactly)

| Use | Hex |
|---|---|
| Background | `#F3F4F6` |
| Card surface | `#FFFFFF` |
| Primary orange | `#FF6B35` |
| Soft orange tint | `#FFEFE8` |
| Text dark | `#1F2937` |
| Text gray | `#6B7280` |
| Light border | `#E5E7EB` |
| Soft fill | `#F3F4F6` |
| Error / sign-out red | `#FF4D4D` |
| Soft red tint | `#FEE6E6` |

## Typography (Inter)

| Element | Style |
|---|---|
| Page title | Bold 16 |
| Full name | Bold 16 |
| Card title (Language) | Bold 14 |
| Section CAPS label (ACCOUNT) | Semi-Bold 11 |
| Detail label CAPS | Medium 11 |
| Detail value | Regular 13 |
| Avatar initial | Bold 22 white |
| Language pill top | Semi-Bold 14 |
| Language pill bottom | Regular 11 |
| Edit pill | Semi-Bold 12 |
| Sign Out label | Semi-Bold 14 |

---

## Layout summary

```
┌─────────────────────────────────┐
│ ← Admin Profile                 │  Top bar
├─────────────────────────────────┤
│ ┌────────────────────────────┐  │
│ │ (S)  System Administrator  │  │  Identity card
│ │      adm00000001        ✎  │  │
│ └────────────────────────────┘  │
│                                 │
│ ┌────────────────────────────┐  │
│ │ ACCOUNT             [Edit] │  │
│ │ USERNAME            admin  │  │  Account card
│ │ ROLE        Administrator  │  │
│ │ MOBILE   +91 98xx xx xxxx  │  │
│ │ ADDRESS                  — │  │
│ └────────────────────────────┘  │
│                                 │
│ ┌────────────────────────────┐  │
│ │ Language                   │  │  Language card
│ │  ( English )  ગુજરાતી  हिंदी │  │
│ └────────────────────────────┘  │
│                                 │
│ ┌────────────────────────────┐  │
│ │ [↩]  Sign Out              │  │  Sign Out card
│ └────────────────────────────┘  │
│                                 │
│       [ 🏠   🕒   (👤) ]         │  Bottom nav
└─────────────────────────────────┘
```

---

## What Claude will do (Figma only)

1. Create the **`Admin — Profile`** frame at (3000, 0) in the existing Figma file, matching the Worker Profile layout 1:1.
2. Build: top bar (back · "Admin Profile"), identity card (avatar with initial "S" + edit pencil badge + name + emp_code), account card (4 detail rows + Edit pill), language card (3 pill segmented control, English selected), Sign Out card (red icon + label), bottom nav with **Person active** in orange circle.
3. All icons SVG — back arrow, edit pencil, sign-out arrow, home, clock, person.
4. Use real admin data: name `System Administrator`, emp_code `adm00000001`, username `admin`, role `Administrator`.
5. Take a screenshot for visual review.

**ZERO code edits. ZERO webapp changes. Only one Figma frame.**

---

## Verification

- Confirm new frame visible: `Admin — Profile`
- Visual checks side-by-side with the Worker Profile reference screenshot:
  - Top bar matches (back arrow + centered bold title)
  - Identity card: orange circle initial + edit pencil badge + name + code
  - Account card: dark "ACCOUNT" label top-left, orange "Edit" pill top-right, 4 rows with CAPS labels left + values right
  - Language card: 3-pill segmented control, English selected with orange border
  - Sign Out card: light-red square icon + red "Sign Out" text
  - Bottom nav: small white pill, 3 icons, Person highlighted in orange circle
