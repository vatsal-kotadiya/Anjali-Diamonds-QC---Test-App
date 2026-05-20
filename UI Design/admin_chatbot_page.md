# Admin / Management — AI Chatbot Page — Figma Design Spec

**Type:** Pure Figma mockup. NO code is written or edited anywhere. Output is one new Figma frame.

**File:** Add a new frame to the existing Figma file `gM9sCiUJzoh8Pv4EOMORNX`.

**Style reference:** Same Jaimin Craft light theme + orange accents already locked in for Worker Report / History / Profile and Admin Users / Profile pages. Background `#F3F4F6`, white cards with soft shadows, orange `#FF6B35` accent, 3-icon bottom nav with active circle.

---

## Context

The Diamond QC app has an admin / management **AI Chatbot** that runs on Google Gemini and lets them ask questions about defects, workers, processes etc. Currently it's the default Streamlit chat UI.

This spec is a **mobile-style chatbot page** in Jaimin Craft style — chat bubbles, suggested-prompt chips, an input bar with mic + send, and the standard 3-icon bottom nav with **Chat icon ACTIVE**.

---

## Frame metadata

- **Name:** `Admin — AI Chatbot`
- **Size:** 390 × 844 px (iPhone 14 Pro)
- **Position:** x = 3420, y = 0 in file `gM9sCiUJzoh8Pv4EOMORNX`
- **Background:** `#F3F4F6`
- **Corner radius:** 40 px
- **Clip contents:** true

---

## Top bar (y ≈ 40, height 56)

Three-zone, gutters 18 px:

- **Left:** back-arrow SVG inside 32 × 32 transparent area (dark icon `#1F2937`)
- **Center (stacked):**
  - Title **"Diamond Assistant"** — Inter Bold 16 px, `#1F2937`
  - Sub-line — Inter Regular 11 px, `#10B981` with a tiny green dot 6 × 6 px on the left:
    - **"● Online · Gemini 2.5"**
- **Right:** "Clear" pill — 56 × 28 px, soft orange tint `#FFEFE8`, orange text `#FF6B35` Inter Semi-Bold 11 px, 14 px radius. Tapping clears the chat history (visual only).

---

## Welcome card (y ≈ 110, shown only at the top of an empty / fresh chat)

White card, 342 × auto, 16 px radius, 1 px border `#E5E7EB`, soft drop shadow, 18 px padding, 12 px gap.

- **Bot avatar row** — 40 × 40 px orange circle `#FF6B35` with a white robot/sparkle SVG icon centered inside
- **Title** "Hi Admin 👋" — Inter Bold 16 px, dark
- **Sub** "I can answer questions about reports, workers, and defects. Try one of the prompts below or type your own." — Inter Regular 13 px, gray

---

## Suggested-prompt chips (y ≈ 240, two rows, 10 px gap between rows, 8 px gap between chips)

Horizontal-wrap auto-layout (or two HORIZONTAL rows since Figma auto-layout supports wrap).

Each chip:
- Pill, white card, 1 px light border `#E5E7EB`, soft shadow, 10 px radius
- Padding 10 × 14 px, label Inter Medium 12 px, dark `#1F2937`
- Small SVG icon on left (16 × 16, gray `#6B7280`)

### Chip set

1. 📊 **"Top defective workers this month"**
2. 🔥 **"Severe defects today"**
3. 💎 **"Reports for diamond D-89898"**
4. 👥 **"Who is responsible for diamond chains?"**
5. 🛠 **"Which process has the most defects?"**
6. 🕒 **"Show me yesterday's activity"**

(Only the first 4 fit cleanly in 2 rows on a 390-wide screen; the rest scroll horizontally.)

---

## Chat messages area (y ≈ 320 onward, scrollable)

Vertical stack of messages, 12 px gap, 24 px gutter, 16 px padding at the top.

### Bot message bubble (left-aligned)
- 40 × 40 px orange-circle avatar on the left
- Bubble: white card, 14 px radius (corners 4 px on bottom-left to "point" at avatar), 1 px light border, soft shadow, 14 × 14 padding, max-width 260 px
- Body text Inter Regular 13 px dark
- Timestamp below bubble: Inter Regular 10 px gray "14:32"

### User message bubble (right-aligned)
- No avatar (or small "You" avatar — optional)
- Bubble: orange `#FF6B35` filled, 14 px radius (corner 4 px on bottom-right), 14 × 14 padding, max-width 260 px
- Body text Inter Regular 13 px **white**
- Timestamp below bubble: Inter Regular 10 px gray, right-aligned

### Sample conversation to render in the mockup

1. **Bot:** "Hi Admin 👋 I can answer questions about reports, workers, and defects. Try one of the prompts below or type your own." (14:30)
2. **User:** "Top defective workers this month" (14:31)
3. **Bot:** "In the last 30 days, the top 3 workers by Severe report count are:\n\n1. Anita Yadav — 5 reports\n2. Bharat Jain — 3 reports\n3. Mohan Das — 2 reports\n\nWant me to break these down by process?" (14:31)
4. **User:** "Yes, by process" (14:32)
5. **Bot:** "Sure — here's the breakdown… *(typing indicator)*" (14:32, in-progress)

### Typing indicator (last bubble)
- White bubble with 3 small gray dots animated (in design: just draw 3 circles 6 × 6 px gray `#9CA3AF` with one slightly darker to imply animation)
- No timestamp on a typing bubble

---

## Input bar (y ≈ 740, sticky at bottom above nav)

Horizontal auto-layout pill, 342 × 52 px, white card, 26 px radius, 1 px light border, soft shadow, 6 px padding (left/right and vertical), 10 px gap.

Contents (left → right):

1. **Attach button** — 36 × 36 px transparent button, gray paperclip SVG (18 px, `#6B7280`)
2. **Input field** — flex-grow, transparent, placeholder **"Ask anything…"** Inter Regular 14 px, `#9CA3AF`
3. **Mic button** — 36 × 36 px light gray fill `#F3F4F6`, 18 px radius, gray mic SVG (16 px, `#6B7280`)
4. **Send button** — 40 × 40 px orange circle `#FF6B35`, white paper-plane SVG (18 px), soft orange drop shadow

---

## Bottom nav (y ≈ 760, but below input bar — sits at y ≈ 800 or replaces the sticky bar based on state)

Pill 200 × 56 px, white, 28 px corner radius, soft drop shadow. Centered horizontally.

Three SVG icons evenly spaced (no emoji):
- Home (gray `#6B7280`, 24 px) — inactive
- **Chat — ACTIVE** — 44 × 44 px orange `#FF6B35` filled circle, white chat-bubble glyph centered
- Person (gray, 24 px) — inactive

*Note: place the bottom nav below the input bar with 8 px gap, or merge them visually so the nav floats just under the keyboard area on mobile.*

---

## Variant frames (optional)

### Variant A — Empty state (x = 3840)
Identical layout but **no message bubbles below the welcome card** — just the welcome card + suggested chips + input bar. Use to show the fresh-launch state.

### Variant B — Streaming response (x = 4260)
Show a bot bubble mid-stream with a small "Stop generating" outline pill button below it (right-aligned, gray border, dark text, 11 px Medium).

---

## Color tokens (Jaimin Craft palette)

| Use | Hex |
|---|---|
| Background | `#F3F4F6` |
| Card / bot bubble | `#FFFFFF` |
| Primary orange / user bubble / send btn | `#FF6B35` |
| Soft orange tint | `#FFEFE8` |
| Text dark | `#1F2937` |
| Text gray | `#6B7280` |
| Subtle / placeholder | `#9CA3AF` |
| Light border | `#E5E7EB` |
| Soft fill (mic btn bg) | `#F3F4F6` |
| Online green | `#10B981` |

## Typography (Inter)

| Element | Style |
|---|---|
| Page title | Bold 16 |
| Status sub-line | Regular 11 |
| Welcome title | Bold 16 |
| Chip label | Medium 12 |
| Bubble body | Regular 13 |
| Timestamp | Regular 10 |
| Input placeholder | Regular 14 |
| Clear pill | Semi-Bold 11 |

---

## Layout summary

```
┌─────────────────────────────────┐
│ ←  Diamond Assistant   [Clear]  │  Top bar
│    ● Online · Gemini 2.5        │
├─────────────────────────────────┤
│ ┌────────────────────────────┐  │
│ │ (🤖)                        │  │
│ │ Hi Admin 👋                 │  │  Welcome card
│ │ I can answer questions...  │  │
│ └────────────────────────────┘  │
│                                 │
│ [📊 Top workers] [🔥 Severe]    │  Suggested chips
│ [💎 D-89898]    [👥 Chains]     │
│                                 │
│ (🤖) Bot reply here...          │  Chat messages
│        14:32                    │
│                ╔═══════════════╗ │
│                ║  User msg…     ║ │
│                ╚═══════════════╝ │
│                            14:33 │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ 📎  Ask anything…   🎤  [➤] │ │  Input bar
│ └─────────────────────────────┘ │
│                                 │
│     [ 🏠   (💬)   👤 ]           │  Bottom nav
└─────────────────────────────────┘
```

---

## What Claude will do (Figma only)

1. Create the **`Admin — AI Chatbot`** frame at (3420, 0) in the existing Figma file.
2. Build: top bar (back · title + Online · Clear pill), Welcome card (bot avatar + heading + sub), 4 suggested-prompt chips (2 × 2 grid), conversation area with sample bubbles (bot + user + bot + user + typing indicator), bottom input bar (paperclip + input + mic + send), bottom nav with **Chat active** in orange circle.
3. All icons SVG — back, robot/sparkle, paperclip, mic, paper-plane (send), home, chat-bubble, person, and small chip icons.
4. Use real Diamond QC data in sample messages (workers Anita / Bharat / Mohan, diamond D-89898, etc.).
5. (Optional) Build Variant A (empty state) at x = 3840 and Variant B (streaming) at x = 4260.
6. Take a screenshot for visual review.

**ZERO code edits. ZERO webapp changes. Only Figma frames.**

---

## Verification

- Confirm new frame visible: `Admin — AI Chatbot`
- Visual checks:
  - Top bar matches Worker Profile style (back arrow + centered title + small status sub-line + right pill)
  - Welcome card has orange bot avatar + warm greeting copy
  - Suggested chips render in 2 rows, each white pill with small icon + label
  - At least 4 chat bubbles (2 bot, 2 user) + typing indicator
  - Bot bubble = white with bottom-left "tail"; user bubble = orange filled with white text and bottom-right "tail"
  - Input bar with paperclip + flex input + mic + orange send button
  - Bottom nav: 3 icons, chat-bubble icon highlighted in orange circle
