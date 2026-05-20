# Diamond QC — Technical Requirements Document

**Version:** 1.0  
**Date:** 2026-05-20  
**Companion doc:** PRD v1.1  
**Platform:** Flutter (Android primary, iOS stretch)

---

## 1. Project Structure

```
lib/
├── main.dart
├── app.dart                    # MaterialApp + router + theme
├── core/
│   ├── theme/
│   │   ├── app_colors.dart
│   │   ├── app_text_styles.dart
│   │   ├── app_theme.dart
│   │   └── app_dimensions.dart
│   ├── router/
│   │   └── app_router.dart     # GoRouter route definitions
│   ├── network/
│   │   ├── api_client.dart     # Dio instance + interceptors
│   │   ├── auth_interceptor.dart
│   │   └── endpoints.dart
│   ├── storage/
│   │   ├── secure_storage.dart # JWT tokens (flutter_secure_storage)
│   │   └── local_db.dart       # Drift SQLite (offline queue)
│   └── utils/
│       ├── audio_utils.dart
│       └── date_utils.dart
├── features/
│   ├── auth/
│   │   ├── data/
│   │   ├── domain/
│   │   └── presentation/
│   │       └── login_screen.dart
│   ├── worker/
│   │   ├── report/
│   │   │   └── presentation/
│   │   │       ├── report_screen.dart
│   │   │       └── widgets/
│   │   │           ├── report_type_tab_bar.dart
│   │   │           ├── hint_banner.dart
│   │   │           ├── diamond_id_field.dart
│   │   │           ├── mic_button.dart
│   │   │           ├── waveform_display.dart
│   │   │           └── transcript_box.dart
│   │   └── history/
│   │       └── presentation/
│   │           ├── history_screen.dart
│   │           └── widgets/
│   │               └── report_history_card.dart
│   ├── dashboard/
│   │   └── presentation/
│   │       ├── dashboard_screen.dart
│   │       └── widgets/
│   │           ├── kpi_summary_row.dart
│   │           ├── period_tab_bar.dart
│   │           ├── defect_rate_chart.dart
│   │           └── report_details_sheet.dart
│   ├── chatbot/
│   │   └── presentation/
│   │       ├── chatbot_screen.dart
│   │       └── widgets/
│   │           ├── suggested_prompt_chip.dart
│   │           ├── chat_bubble.dart
│   │           └── chat_input_bar.dart
│   ├── admin/
│   │   ├── users/
│   │   │   └── presentation/
│   │   │       ├── users_list_screen.dart
│   │   │       ├── user_detail_screen.dart
│   │   │       ├── create_user_screen.dart
│   │   │       └── widgets/
│   │   │           ├── user_list_tile.dart
│   │   │           ├── user_stats_row.dart
│   │   │           └── report_card.dart
│   │   └── settings/
│   │       └── presentation/
│   │           └── settings_screen.dart
│   └── profile/
│       └── presentation/
│           ├── profile_screen.dart
│           └── widgets/
│               └── language_selector.dart
└── shared/
    └── widgets/
        ├── app_scaffold.dart       # scaffold + bottom nav
        ├── filter_chip_row.dart
        ├── search_bar.dart
        ├── severity_badge.dart
        ├── report_type_tag.dart
        ├── audio_player_tile.dart
        └── loading_overlay.dart
```

---

## 2. Design Tokens

### 2.1 Colors — `app_colors.dart`

```dart
class AppColors {
  // Brand
  static const primary        = Color(0xFFE8491B); // orange — buttons, active tabs, mic
  static const primaryDark    = Color(0xFF0F1A2E); // near-black navy — Sign In button
  static const loginBg        = Color(0xFF3B0A0A); // dark maroon — login screen only

  // Backgrounds
  static const background     = Color(0xFFF5F5F5); // app background
  static const surface        = Color(0xFFFFFFFF); // cards, sheets
  static const inputFill      = Color(0xFFF0F0F0); // unfocused input bg

  // Severity
  static const severe         = Color(0xFFE8491B); // same as primary
  static const moderate       = Color(0xFFFFC107); // amber
  static const low            = Color(0xFF4CAF50); // green

  // Status
  static const activeGreen    = Color(0xFF4CAF50);
  static const inactiveRed    = Color(0xFFE53935);

  // Text
  static const textPrimary    = Color(0xFF1A1A1A);
  static const textSecondary  = Color(0xFF6B7280);
  static const textHint       = Color(0xFF9CA3AF);

  // Report type tags
  static const receiveTagBg   = Color(0xFFEBF5FF);
  static const receiveTagFg   = Color(0xFF1D72E8);
  static const problemTagBg   = Color(0xFFFFF0EB);
  static const problemTagFg   = Color(0xFFE8491B);
}
```

### 2.2 Dimensions — `app_dimensions.dart`

```dart
class AppDimensions {
  // Border radius
  static const radiusCard     = 16.0;
  static const radiusInput    = 12.0;
  static const radiusPill     = 100.0; // fully rounded buttons/tabs
  static const radiusChip     = 8.0;

  // Spacing
  static const pagePadding    = 16.0;
  static const cardPadding    = 16.0;
  static const sectionGap     = 16.0;
  static const itemGap        = 12.0;

  // Component heights
  static const inputHeight    = 52.0;
  static const buttonHeight   = 52.0;
  static const bottomNavHeight = 64.0;
  static const micButtonSize  = 80.0;
}
```

### 2.3 Text Styles — `app_text_styles.dart`

```dart
class AppTextStyles {
  static const appBarTitle    = TextStyle(fontSize: 18, fontWeight: FontWeight.w700);
  static const sectionLabel   = TextStyle(fontSize: 11, fontWeight: FontWeight.w700,
                                  letterSpacing: 0.8, color: AppColors.textSecondary);
  static const cardTitle      = TextStyle(fontSize: 15, fontWeight: FontWeight.w600);
  static const body           = TextStyle(fontSize: 14, fontWeight: FontWeight.w400);
  static const caption        = TextStyle(fontSize: 12, fontWeight: FontWeight.w400,
                                  color: AppColors.textSecondary);
  static const kpiValue       = TextStyle(fontSize: 22, fontWeight: FontWeight.w700);
  static const kpiLabel       = TextStyle(fontSize: 12, fontWeight: FontWeight.w500,
                                  color: AppColors.textSecondary);
  static const buttonLabel    = TextStyle(fontSize: 15, fontWeight: FontWeight.w600,
                                  color: Colors.white);
}
```

---

## 3. Navigation

### Router — GoRouter

```
/login                          → LoginScreen
/worker
  /report                       → ReportScreen (default tab: receive)
  /history                      → HistoryScreen
  /profile                      → ProfileScreen
/management
  /dashboard                    → DashboardScreen
  /dashboard/:processId         → ReportDetailsScreen
  /chatbot                      → ChatbotScreen
  /profile                      → ProfileScreen
/admin
  /dashboard                    → DashboardScreen
  /dashboard/:processId         → ReportDetailsScreen
  /users                        → UsersListScreen
  /users/create                 → CreateUserScreen
  /users/:userId                → UserDetailScreen
  /users/:userId/edit           → EditUserScreen
  /chatbot                      → ChatbotScreen
  /settings                     → SettingsScreen
  /profile                      → ProfileScreen
```

### Shell routes & bottom navigation

Each role has a `ShellRoute` wrapping its tabs with a shared `AppScaffold` that renders the role-specific `BottomNavigationBar`.

```dart
// Worker shell tabs
enum WorkerTab { report, history, profile }

// Management shell tabs
enum ManagementTab { dashboard, chatbot, profile }

// Admin shell tabs
enum AdminTab { dashboard, users, chatbot, profile }
```

**Transitions:**
- Tab switches: no animation (instant swap)
- Push to sub-screen (e.g. ReportDetails, UserDetail): slide-from-right (`CupertinoPageRoute` or `CustomTransitionPage` with `SlideTransition`)
- Modal sheets (filters, dropdowns): slide-from-bottom with `showModalBottomSheet`

---

## 4. Screen-by-Screen Technical Specification

### 4.1 Login Screen

**Widget tree (simplified):**
```
Scaffold(backgroundColor: AppColors.loginBg)
└── Center
    └── Column
        ├── Text("Anjali Diamonds")          // white, bold, 28sp
        ├── Text("Sign in to your account")  // textSecondary, 14sp
        └── Card(borderRadius: 20)
            └── Column
                ├── _LabeledInput("USERNAME")
                ├── _LabeledInput("PASSWORD", obscureText: true)
                ├── Row [ Checkbox, Text("Stay logged in") ]
                └── ElevatedButton("Sign In")  // primaryDark bg, pill shape
```

**State:**
- `usernameController`, `passwordController` (`TextEditingController`)
- `stayLoggedIn` bool — if true, persist refresh token on successful login
- `isLoading` bool — shows `CircularProgressIndicator` inside button during API call

**Input field spec:**
- Background: `AppColors.inputFill`
- Focused border: 1.5 dp `AppColors.primary`
- Unfocused border: 1 dp `Color(0xFFE5E7EB)`
- Label: ALL CAPS, `AppTextStyles.sectionLabel`, sits above the field (not floating)

**Sign In button:**
- Full width, height 52 dp, `borderRadius: AppDimensions.radiusPill`
- Color: `AppColors.primaryDark`
- On tap: validate → `POST /auth/login` → store JWT → navigate to role home

**Error handling:**
- Invalid credentials: red text below password field
- Account inactive: same red text
- Network error: `SnackBar` at bottom

---

### 4.2 Worker Report Screen

**State management:** `ReportNotifier` (Riverpod `AsyncNotifier` or BLoC)

```dart
enum ReportType { receive, problem }
enum RecordingState { idle, recording, recorded }
enum SubmissionState { idle, uploading, transcribing, translating, analysing, success, error }
```

**Widget tree:**
```
AppScaffold(title: "Anjali Diamonds", tab: WorkerTab.report)
└── Column
    ├── ReportTypeTabBar           // orange pill toggle
    ├── HintBanner                 // dismissible, updates per tab
    ├── DiamondIdField             // dropdown + QR icon
    ├── Expanded
    │   └── Column(mainAxisAlignment: center)
    │       ├── MicButton          // 80dp circle, orange
    │       ├── WaveformDisplay    // shown after recording
    │       └── TranscriptBox      // auto-filled after STT
    └── SubmitButton               // orange pill, pinned bottom
```

#### ReportTypeTabBar
```dart
// Two pills in a Row, inside a rounded container
// Active: filled orange pill with white text
// Inactive: transparent with border, textPrimary text
// Switching tab: updates ReportType in state, swaps hint text
```

#### HintBanner
```dart
Container(
  color: Colors.white,
  child: Row(
    children: [
      Icon(Icons.info_outline, size: 16, color: textSecondary),
      Expanded(child: Text(hintText)),
      IconButton(Icons.close, onPressed: dismiss),
    ],
  ),
)
// dismissed state stored in local bool, not persisted
```

#### DiamondIdField
```dart
// Styled dropdown (DropdownButtonFormField or custom overlay)
// Right trailing: IconButton with QR scanner icon (camera_alt or qr_code)
// QR tap: launch mobile_scanner package, on scan fill the field value
// Height: AppDimensions.inputHeight
// Border: same as login inputs, focus = orange
```

**Open question #7 resolution options:**
- Option A (dropdown): pre-load known diamond IDs from `/diamonds` endpoint
- Option B (free-text + QR): `TextFormField` with `keyboardType: TextInputType.text`, QR button launches scanner overlay

#### MicButton
```dart
GestureDetector(
  onTap: toggleRecording,
  child: AnimatedContainer(
    width: 80, height: 80,
    decoration: BoxDecoration(
      shape: BoxShape.circle,
      color: isRecording ? AppColors.primary.withOpacity(0.8) : AppColors.primary,
      boxShadow: isRecording ? [pulseShadow] : [],
    ),
    child: Icon(Icons.mic, color: Colors.white, size: 36),
  ),
)
// While recording: animate a pulsing ring around the circle using AnimationController
```

**Audio recording:** `record` package (`AudioRecorder`)
- Format: AAC (`.m4a`) or WAV — WAV preferred for Sarvam compatibility
- Sample rate: 16 kHz mono (Sarvam requirement)
- File saved to app's temp directory; path passed to upload on submit

#### WaveformDisplay
```dart
// Use audio_waveforms package
// PlayerController for playback scrubbing
// Orange bars on white/light background
// Shown only when RecordingState == recorded
```

#### TranscriptBox
```dart
Container(
  decoration: BoxDecoration(
    color: Colors.white,
    borderRadius: BorderRadius.circular(AppDimensions.radiusInput),
    border: Border.all(color: Color(0xFFE5E7EB)),
  ),
  child: TextField(
    controller: transcriptController,
    maxLines: 4,
    readOnly: true,               // auto-filled from STT; not user-editable in v1
    decoration: InputDecoration(labelText: "Transcript"),
  ),
)
```

#### SubmitButton
```dart
// Disabled: grey, until diamondId != null && recordingState == recorded
// Loading: replace label with CircularProgressIndicator (white, size 20)
// Progress label: "Uploading…" / "Transcribing…" / "Translating…" / "Analysing…"
// Changes text every ~2s based on SubmissionState enum
```

**Submission flow (async):**
```
1. Set state → uploading
   PUT /audio/upload  (multipart, returns file_uuid)
2. Set state → transcribing
   POST /sarvam/stt   (server calls Sarvam saarika:v2)
3. Set state → translating
   POST /sarvam/translate  (server calls Sarvam saaras:v2)
4. Set state → analysing
   POST /reports      (saves report + triggers Gemini async)
5. Set state → success
   Show transcript + severity badge
   If chain result: show attribution banner
```

**Offline path:** if no network detected before step 1, serialize `{reportType, diamondId, audioPath, workerId}` to local SQLite `pending_reports` table, show "Queued" toast.

---

### 4.3 Worker History Screen

**Data:** `GET /reports?worker_id=me&limit=50&offset=0`

**Widget tree:**
```
Scaffold(appBar: BackAppBar("History"))
└── Column
    ├── SearchBar(hint: "Search by Diamond ID…")
    ├── FilterChipRow(options: ["All Types", "Receive Report", "Problem Report"])
    └── ListView.builder
        └── ReportHistoryCard (per item)
```

#### ReportHistoryCard
```dart
Container(
  margin: EdgeInsets.symmetric(vertical: 6, horizontal: 16),
  padding: EdgeInsets.all(14),
  decoration: BoxDecoration(
    color: Colors.white,
    borderRadius: BorderRadius.circular(AppDimensions.radiusCard),
  ),
  child: Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Row(
        children: [
          StatusDot(color: severityColor),      // 8dp filled circle
          Text(diamondId, fontWeight: bold),
          Spacer(),
          Text(formattedTime, style: caption),
        ],
      ),
      SizedBox(height: 6),
      ReportTypeTag(type: reportType),           // blue/orange pill
      SizedBox(height: 6),
      Text(transcriptSnippet, maxLines: 2, overflow: ellipsis),
    ],
  ),
)
// Tap → navigate to /worker/report/:id detail (not in scope for v1 — open question)
```

**Search:** client-side filter on loaded list (no separate API call for v1)

**Filter:** chip toggles `All Types` / `Receive Report` / `Problem Report` — filters `ListView` items

---

### 4.4 Dashboard Screen (Management + Admin)

**Data:** `GET /dashboard?period=daily|weekly|monthly`  
**Auto-refresh:** `Timer.periodic(Duration(seconds: 10), _refresh)` — cancelled in `dispose()`

**Widget tree:**
```
AppScaffold(title: "Anjali Diamonds")
└── Column
    ├── KpiSummaryRow
    ├── PeriodTabBar            // Daily · Weekly · Monthly
    └── Expanded
        └── SingleChildScrollView
            └── Column
                ├── Text("Defect Rate by Process")
                └── DefectRateChart
```

#### KpiSummaryRow
```dart
Row(
  children: [
    KpiCard(value: "10", label: "TOTAL REPORTS"),
    KpiCard(value: "6", label: "EMPLOYEES INVOLVED", valueColor: Colors.blue),
    SeverityKpiCard(severe: 5, moderate: 2, low: 1),
  ],
)
// Each card: white rounded container, value in kpiValue style, label in kpiLabel style
// SeverityKpiCard: stacked colored Text rows
```

#### PeriodTabBar
```dart
// Underline-style tab bar (not pills)
// Active tab: orange bottom border 2dp + orange text
// Inactive: textSecondary text, no border
// Switching period: re-fetches dashboard data
```

#### DefectRateChart
```dart
// Custom painter OR fl_chart HorizontalBarChart
// Y-axis: process names (left-aligned text)
// X-axis: hidden (no labels)
// Bars: orange filled rectangles, height ~12dp, rounded right end
// Value label: Text at bar tip, right-aligned
// Row height: 48dp per process
// Chart height = processCount * 48dp

// Tap interaction:
// GestureDetector on each bar row → push ReportDetailsScreen(processId, period)
```

**Implementation note:** use `fl_chart` `BarChart` rotated, or build a custom `ListView` where each row has a `FractionallySizedBox` for the bar width (simpler, no chart lib complexity for this design).

---

### 4.5 Report Details Screen

**Route:** `/dashboard/:processId` with `period` query param  
**Data:** `GET /reports?process_id=:id&period=daily|weekly|monthly`

**Widget tree:**
```
Scaffold
├── AppBar(title: "Report Details", subtitle: "$processName · $period")
│   └── IconButton(Icons.close)
└── Column
    ├── StatsRow(totalReports, workers, defectPercent)
    ├── SeverityChipsBar(severe, moderate, low)
    ├── SearchBar("Search reports…")
    ├── Row [ FilterDropdown("All Types"), FilterDropdown("All Severity"), SortButton ]
    └── Expanded → ListView.builder → ReportCard
```

#### SeverityChipsBar
```dart
Column(
  children: [
    Row(children: [
      SeverityChip(AppColors.severe, "5 Severe"),
      SeverityChip(AppColors.moderate, "2 Moderate"),
      SeverityChip(AppColors.low, "1 Low"),
    ]),
    SizedBox(height: 8),
    SeverityGradientBar(),   // LinearGradient red→amber→green, borderRadius pill
  ],
)
```

#### ReportCard
```dart
Container(
  decoration: BoxDecoration(color: Colors.white, borderRadius: 12),
  child: Column(
    children: [
      Row([StatusDot, DiamondIdBadge, ReportTypeTag, SeverityBadge]),
      Text("$workerName · Dept: $dept", style: caption),
      SizedBox(height: 8),
      Text(gujaratiTranscript, maxLines: 3),
      SizedBox(height: 8),
      AudioPlayerTile(url: audioUrl, duration: durationSeconds),
      Row([Text(formattedDateTime), Spacer(), DefectTypeTag(defectType)]),
    ],
  ),
)
```

#### AudioPlayerTile
```dart
// Uses just_audio package
// UI: orange circular play/pause button + WaveformBar (static, not interactive — use
//     audio_waveforms PlayerController for interactive scrubbing if needed)
//     + elapsed/total time Text ("0:08/0:08")
// State: playing / paused
// Only one player active at a time — use a shared AudioPlayerManager singleton
```

---

### 4.6 Diamond Assistant (Chatbot) Screen

**Data:** stateful conversation; `POST /chat` with `{messages: [...], role: "admin|management"}`

**Widget tree:**
```
Scaffold
├── AppBar
│   ├── leading: BackButton
│   ├── title: Column [ "Diamond Assistant", OnlineIndicator ]
│   └── actions: [ TextButton("Clear") ]
└── Column
    ├── Expanded
    │   └── ListView.builder(reverse: true)
    │       ├── WelcomeCard          // shown when messages.isEmpty
    │       ├── SuggestedPromptChips // shown when messages.isEmpty
    │       └── ChatBubble (per msg)
    └── ChatInputBar
```

#### OnlineIndicator
```dart
Row(children: [
  Container(width: 8, height: 8, decoration: BoxDecoration(
    color: AppColors.activeGreen, shape: BoxShape.circle)),
  SizedBox(width: 4),
  Text("ONLINE", style: TextStyle(fontSize: 10, color: AppColors.activeGreen)),
])
```

#### WelcomeCard
```dart
// Centered card with orange robot avatar circle (80dp), greeting text, description
// Shown only when conversation is empty
```

#### SuggestedPromptChips
```dart
// Wrap widget with 3 chips
// Chip style: white background, rounded border, leading icon, body text
// Tap: inserts text into input and sends immediately
const suggestions = [
  (Icons.trending_up, "Top defective workers this month"),
  (Icons.warning_amber, "Severe defects today"),
  (Icons.history,       "Last night's shift summary"),
];
```

#### ChatBubble
```dart
// User message: right-aligned, orange background, white text, rounded corners (all + bottom-right flat)
// AI message: left-aligned, white card, leading orange robot avatar icon, textPrimary
// AI messages support basic markdown: bold via **text**, numbered lists
```

#### ChatInputBar
```dart
Container(
  decoration: BoxDecoration(color: Colors.white, boxShadow: [...]),
  child: Row(
    children: [
      IconButton(Icons.attach_file, color: textSecondary),   // v1: noop or hidden
      Expanded(child: TextField(hint: "Ask anything…")),
      IconButton(Icons.mic, color: textSecondary),            // voice-to-text for query
      CircleAvatar(
        backgroundColor: AppColors.primary,
        child: IconButton(Icons.send, color: Colors.white),
      ),
    ],
  ),
)
// Mic: record short query, run STT, fill text field (same Sarvam STT pipeline)
// Send: disabled while AI is responding (show typing indicator)
```

**Typing indicator:** three animated dots (`...`) shown as an AI bubble while awaiting response.

**Clear:** resets conversation state; no server call needed (v1 chat is stateless).

---

### 4.7 Profile Screen (All Roles)

**Shared widget, renders differently by role (Worker / Management / Admin)**

**Widget tree:**
```
Scaffold(appBar: BackAppBar(roleTitle))
└── SingleChildScrollView
    └── Column
        ├── ProfileHeaderCard
        ├── AccountCard
        ├── LanguageCard
        └── SignOutCard
```

#### ProfileHeaderCard
```dart
Container(
  color: Colors.white, borderRadius: 16,
  child: Row(
    children: [
      CircleAvatar(
        radius: 28,
        backgroundColor: AppColors.primary,
        child: Text(initial, style: TextStyle(color: Colors.white, fontSize: 22)),
      ),
      // Edit pencil overlay at bottom-right of avatar: small orange circle with edit icon
      Column(children: [
        Text(name, style: cardTitle),
        Text(empCode, style: caption),
      ]),
    ],
  ),
)
```

#### AccountCard
```dart
Container(
  color: Colors.white, borderRadius: 16,
  child: Column(
    children: [
      Row([ Text("ACCOUNT", style: sectionLabel), TextButton("Edit") ]),
      Divider(),
      _InfoRow("USERNAME", username),
      _InfoRow("DEPARTMENT", department),
      _InfoRow("PROCESS", process),     // hidden for management/admin
      _InfoRow("Mobile", mobile),
      _InfoRow("ADDRESS", address ?? "—"),
    ],
  ),
)
// Edit tap → opens EditProfileSheet (bottom sheet with editable fields)
```

#### LanguageCard
```dart
Container(
  color: Colors.white, borderRadius: 16,
  child: Column(
    children: [
      Text("Language", style: cardTitle),
      SizedBox(height: 12),
      Row(children: [
        LanguagePill(label: "English", sublabel: "English",  selected: lang == 'en'),
        LanguagePill(label: "ગુજરાતી", sublabel: "Gujarati", selected: lang == 'gu'),
        LanguagePill(label: "हिंदी",   sublabel: "Hindi",    selected: lang == 'hi'),
      ]),
    ],
  ),
)

// LanguagePill:
// Selected: orange outlined circle + orange text
// Unselected: plain text
// Tap: update language_pref via PATCH /users/me, re-load ARB locale
```

#### SignOutCard
```dart
Container(
  color: Colors.white, borderRadius: 16,
  child: ListTile(
    leading: Container(
      padding: 8,
      decoration: BoxDecoration(color: Color(0xFFFFEBEB), borderRadius: 10),
      child: Icon(Icons.logout, color: AppColors.inactiveRed),
    ),
    title: Text("Sign Out", style: TextStyle(color: AppColors.inactiveRed, fontWeight: w600)),
    onTap: _confirmSignOut,
  ),
)
// Tap: show ConfirmDialog ("Are you sure?") → on confirm: clear tokens, navigate /login
```

---

### 4.8 Admin — Users List Screen

**Data:** `GET /users?role=&department=&status=&search=&page=1`  
**Pagination:** infinite scroll (load next page when user scrolls within 200dp of end)

**Widget tree:**
```
Scaffold
├── AppBar(title: "Users", subtitle: "24 Users", actions: [AddButton])
└── Column
    ├── SearchBar("Search by name, username or emp code…")
    ├── FilterChipRow(["Role ▾", "Department ▾", "Status ▾"])
    └── Expanded → ListView.builder → UserListTile
```

#### UserListTile
```dart
ListTile(
  leading: Row(children: [
    StatusDot(isActive),             // 10dp circle, green/red
    SizedBox(width: 8),
    Text(index.toString(), style: caption),
  ]),
  title: Text(name, style: cardTitle),
  subtitle: Text("$empCode · $roleTitle", style: caption),
  trailing: Text(factoryName, style: caption),
)
// Divider between tiles
// Tap → push UserDetailScreen
```

**Filter bottom sheets:** tapping each chip opens a `showModalBottomSheet` with a list of options (radio-style); selected option shown in chip label.

---

### 4.9 Admin — User Detail Screen

**Data:** `GET /users/:id` + `GET /users/:id/reports`

**Widget tree:**
```
Scaffold
├── AppBar(title: name, subtitle: "$factory · $status", actions: [DeleteButton])
└── SingleChildScrollView
    └── Column
        ├── UserStatsGrid
        ├── UserDetailsCard
        └── RecentReportsSection
```

#### UserStatsGrid
```dart
// 3-column × 2-row grid
GridView.count(
  crossAxisCount: 3, shrinkWrap: true,
  children: [
    StatCell("TOTAL REPORTS", totalReports, Colors.black),
    StatCell("SEVERE",         severe,       AppColors.severe),
    StatCell("MODERATE",       moderate,     AppColors.moderate),
    StatCell("LOW",            low,          AppColors.low),
    StatCell("FAULT RATE",     "$faultRate%", AppColors.inactiveRed),
    StatCell("STATUS",         status,        statusColor),
  ],
)
// Fault Rate = (problem reports / total reports * 100).toStringAsFixed(0) + "%"
```

#### UserDetailsCard
```dart
// White card with "DETAILS" label + Edit button
// _DetailRow widgets for each field:
//   Emp Code, Username, Password (masked + eye toggle), Role, Department,
//   Factory, Floor, Table, Process, Joining Date, Mobile, Address
// Password row: Row [ masked text, Spacer, IconButton(eye) ]
//   eye tap: toggles _showPassword bool, rebuilds with cleartext vs "●●●●●●●●"
```

#### RecentReportsSection
```dart
Column(
  children: [
    Text("Recent Reports ($count)", style: cardTitle),
    Row([ FilterDropdown("All Types"), FilterDropdown("All Severity") ]),
    ...reportCards,
  ],
)
// Uses same ReportCard widget as Report Details screen
```

**Delete button:** red outlined button top-right of AppBar  
On tap → `ConfirmDialog` ("Delete [name]? This cannot be undone.") → `DELETE /users/:id` → pop + refresh list

---

### 4.10 Admin — Create / Edit User Screen

**Widget tree:**
```
Scaffold(appBar: BackAppBar("Create User"))
└── SingleChildScrollView
    └── Column
        ├── EmpCodeSection
        ├── IdentitySection
        ├── AssignmentSection
        ├── ContactSection
        └── Padding → CreateUserButton
```

#### EmpCodeSection
```dart
// White card
Row(children: [
  Expanded(child: _LabeledInput("Factory")),    // 3-char, e.g. "vaw"
  SizedBox(width: 8),
  Expanded(child: _LabeledInput("Floor")),      // 2-digit
  SizedBox(width: 8),
  Expanded(child: _LabeledInput("Table")),      // 2-digit
])
SizedBox(height: 12)
// Auto-generated emp code: reacts to factory/floor/table onChange
//   → debounced GET /emp-code/next?factory=&floor=&table= → updates read-only field
Container(
  color: AppColors.inputFill,
  child: Text(empCode),                        // e.g. "vaw03010001"
)
Text("Auto-generated from Factory + Floor + Table", style: caption)
```

#### IdentitySection
```dart
// White card
_LabeledInput("Full Name")
_LabeledDropdown("Role", options: ["Admin", "Management", "Worker"])
Row([
  Expanded(child: _LabeledInput("Username")),
  SizedBox(width: 8),
  Expanded(child: _LabeledPasswordInput("Password")),  // eye toggle
])
```

#### AssignmentSection
```dart
// White card
_LabeledDropdown("Department", options: departmentList)
_LabeledDropdown("Process", options: processList)
Text("Process is required only for workers", style: caption)
// Process dropdown disabled when role != Worker
```

#### CreateUserButton
```dart
SizedBox(
  width: double.infinity, height: AppDimensions.buttonHeight,
  child: ElevatedButton.icon(
    icon: Icon(Icons.add),
    label: Text("Create User"),
    style: ElevatedButton.styleFrom(
      backgroundColor: AppColors.primary,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppDimensions.radiusPill)),
    ),
    onPressed: _submitForm,
  ),
)
```

**Validation:**
- All fields required except Address
- Username: no spaces, min 3 chars
- Password: min 4 chars (plaintext per spec)
- Process: required only when role == Worker
- Show inline error text below field on submit

---

## 5. Shared Widgets

### SeverityBadge
```dart
// Small pill
Container(
  padding: EdgeInsets.symmetric(horizontal: 8, vertical: 3),
  decoration: BoxDecoration(
    color: severityColor.withOpacity(0.12),
    borderRadius: BorderRadius.circular(AppDimensions.radiusPill),
    border: Border.all(color: severityColor, width: 0.5),
  ),
  child: Row(children: [
    Container(width: 6, height: 6, decoration: BoxDecoration(
      color: severityColor, shape: BoxShape.circle)),
    SizedBox(width: 4),
    Text(label, style: TextStyle(color: severityColor, fontSize: 11, fontWeight: w600)),
  ]),
)
```

### ReportTypeTag
```dart
// "RECEIVE" → blue pill   "PROBLEM" → orange pill
Container(
  padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
  decoration: BoxDecoration(
    color: isReceive ? AppColors.receiveTagBg : AppColors.problemTagBg,
    borderRadius: BorderRadius.circular(6),
  ),
  child: Text(label, style: TextStyle(
    color: isReceive ? AppColors.receiveTagFg : AppColors.problemTagFg,
    fontSize: 11, fontWeight: w600)),
)
```

### FilterDropdown
```dart
// Outlined pill with chevron icon
// Tap: showModalBottomSheet with radio list
OutlinedButton.icon(
  icon: Text(selectedLabel),
  label: Icon(Icons.keyboard_arrow_down),
  style: OutlinedButton.styleFrom(
    side: BorderSide(color: Color(0xFFE5E7EB)),
    shape: StadiumBorder(),
    padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
  ),
)
```

### AppScaffold
```dart
// Wraps every role screen
// Renders the correct BottomNavigationBar for the current role
// Active tab icon: AppColors.primary filled
// Inactive tab icon: AppColors.textSecondary
// Background: white, no elevation, top border 1dp Color(0xFFE5E7EB)
// BottomNavigationBar type: fixed (no shifting animation)
```

---

## 6. State Management

**Chosen approach:** Riverpod (`flutter_riverpod`)

| Provider | Type | Purpose |
|---|---|---|
| `authProvider` | `AsyncNotifierProvider` | Login, token refresh, role |
| `reportProvider` | `AsyncNotifierProvider` | Report screen state + submission |
| `historyProvider` | `FutureProvider.family` | Worker's report list |
| `dashboardProvider` | `AsyncNotifierProvider` | Dashboard data + auto-refresh |
| `reportDetailsProvider` | `FutureProvider.family` | Per-process drill-down |
| `usersProvider` | `AsyncNotifierProvider` | Paginated user list + filters |
| `userDetailProvider` | `FutureProvider.family` | Single user + their reports |
| `chatProvider` | `NotifierProvider` | Conversation messages |
| `audioPlayerProvider` | `NotifierProvider` | Singleton AudioPlayer manager |
| `localeProvider` | `NotifierProvider` | Current app locale |

---

## 7. API Client

**Package:** `dio` + `dio_cache_interceptor` (optional)

```dart
// auth_interceptor.dart
// onRequest: attach "Authorization: Bearer <access_token>"
// onError (401): attempt token refresh via /auth/refresh
//   success → retry original request with new token
//   failure → clear tokens, redirect to /login
```

**Base response wrapper:**
```dart
class ApiResponse<T> {
  final T? data;
  final String? error;
  final int statusCode;
}
```

**Error states mapped to UI:**
| HTTP | UI behaviour |
|---|---|
| 401 | Auto-refresh; if fails → force logout |
| 403 | SnackBar "You don't have permission" |
| 422 | Inline form validation errors |
| 5xx | SnackBar "Server error — try again" |
| Network | SnackBar "No connection" + queue if on submit |

---

## 8. Offline Queue

**Package:** `drift` (type-safe SQLite ORM for Flutter)

```dart
// pending_reports table
class PendingReports extends Table {
  IntColumn get id        => integer().autoIncrement()();
  TextColumn get workerId => text()();
  TextColumn get reportType => text()();   // receive | problem
  TextColumn get diamondId  => text()();
  TextColumn get audioPath  => text()();   // local file path
  DateTimeColumn get createdAt => dateTime()();
  TextColumn get syncStatus => text().withDefault(Constant('pending'))();
  // pending | uploading | failed
  IntColumn get retryCount => integer().withDefault(Constant(0))();
}
```

**Sync service:** `PendingSyncService` — runs as a `WorkManager` one-time task when network becomes available (listen via `connectivity_plus`)

```
For each pending row (ordered by createdAt ASC):
  1. Mark syncStatus = 'uploading'
  2. Attempt full submission pipeline
  3. On success: delete row from local DB
  4. On failure: increment retryCount
     if retryCount >= 3: mark syncStatus = 'failed', stop retrying
```

---

## 9. Audio Pipeline

```
Record (record pkg)
  └── WAV file, 16kHz mono, saved to getTemporaryDirectory()
      └── Upload to backend (multipart/form-data)
          └── Backend: PUT to Cloudflare R2
              └── Backend: POST to Sarvam saarika:v2 (STT)
                  └── POST to Sarvam saaras:v2 (translate)
                      └── Return { transcript_original, transcript_english } to app
```

**Max recording duration:** 120 seconds — enforced by a `Timer` that auto-stops recording at 120s.

**Playback in lists:** `just_audio` with a global `AudioPlayerManager` — only one track plays at a time. Starting a new track pauses the previous one.

---

## 10. Localisation

**Package:** `flutter_localizations` + `intl`

**ARB files:**
```
lib/l10n/
  app_en.arb   # English (default)
  app_gu.arb   # Gujarati
  app_hi.arb   # Hindi
```

**Locale switching at runtime:**
```dart
// localeProvider (Riverpod)
// On language pill tap:
//   1. PATCH /users/me { language_pref: "gu" }
//   2. ref.read(localeProvider.notifier).setLocale(Locale("gu"))
//   3. MaterialApp.locale updates → all l10n strings re-render
```

**Strings to translate (worker-facing only in v1):**
- Report screen: tab labels, hint banner text, field labels, button labels, submission state messages
- History screen: title, search hint, filter labels
- Profile screen: section labels, language card title, sign out label
- Common: error messages, loading states, empty states

---

## 11. Permissions

| Permission | When requested | Package |
|---|---|---|
| Microphone | First tap of Mic button | `permission_handler` |
| Camera | First tap of QR scanner icon | `permission_handler` |
| Notifications | On first launch (if notifications enabled) | `permission_handler` |

Denied permissions: show a rationale dialog with a "Go to Settings" button (`openAppSettings()`).

---

## 12. Key Packages

| Package | Purpose |
|---|---|
| `go_router` | Navigation |
| `flutter_riverpod` | State management |
| `dio` | HTTP client |
| `flutter_secure_storage` | JWT token storage |
| `drift` | Local SQLite (offline queue) |
| `record` | Audio recording |
| `just_audio` | Audio playback |
| `audio_waveforms` | Waveform visualisation |
| `mobile_scanner` | QR code scanning |
| `connectivity_plus` | Network state monitoring |
| `permission_handler` | Runtime permissions |
| `flutter_localizations` + `intl` | i18n |
| `firebase_crashlytics` | Crash reporting |
| `workmanager` | Background sync |
| `fl_chart` | Dashboard bar chart |
| `cached_network_image` | Avatar / asset caching |

---

## 13. Build & Environment

```
.env.development   → API base URL: http://192.168.x.x:8000
.env.production    → API base URL: https://api.anjalidiamonds.com
```

**Flavors:** `development` and `production` (Flutter `--dart-define` or `flutter_flavorizr`)

**Min Android SDK:** API 26 (Android 8.0)  
**Target Android SDK:** API 35  
**iOS Deployment Target:** 15.0

---

## 14. Testing Strategy

| Layer | Approach |
|---|---|
| Unit | Riverpod notifier logic, API response parsing, emp code generation, fault rate calculation |
| Widget | Key widgets: `ReportTypeTabBar`, `MicButton` state transitions, `SeverityBadge`, `ReportCard` |
| Integration | Submission flow E2E (mock Sarvam + Gemini), offline queue sync cycle |
| Golden tests | Login screen, Dashboard KPI row, ReportCard — snapshot test for design regression |
