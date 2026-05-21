# Diamond QC — Technical Requirements Document

**Version:** 1.1 (Flutter + Figma UI aligned)
**Date:** 2026-05-21
**Companion doc:** PRD v1.3
**Framework:** Flutter 3.x — Dart — Android + iOS

---

## 1. Project Structure

```
lib/
├── main.dart
├── app.dart                          # MaterialApp + GoRouter + theme
├── core/
│   ├── theme/
│   │   ├── app_colors.dart
│   │   ├── app_text_styles.dart
│   │   ├── app_theme.dart
│   │   └── app_dimensions.dart
│   ├── router/
│   │   └── app_router.dart           # GoRouter — all routes + ShellRoutes
│   ├── network/
│   │   ├── api_client.dart           # Dio instance
│   │   ├── auth_interceptor.dart     # JWT attach + auto-refresh
│   │   └── endpoints.dart
│   ├── storage/
│   │   ├── secure_storage.dart       # flutter_secure_storage (JWT tokens)
│   │   └── local_db.dart             # drift SQLite (offline queue)
│   └── utils/
│       ├── audio_utils.dart
│       └── date_utils.dart
│
├── features/
│   ├── auth/
│   │   ├── data/
│   │   │   ├── datasource/auth_remote_datasource.dart
│   │   │   ├── model/login_request.dart
│   │   │   ├── model/token_response.dart
│   │   │   └── repository/auth_repository_impl.dart
│   │   ├── domain/
│   │   │   ├── entity/auth_user.dart
│   │   │   ├── repository/auth_repository.dart
│   │   │   └── usecase/login_usecase.dart
│   │   └── presentation/
│   │       ├── notifier/auth_notifier.dart
│   │       └── login_screen.dart
│   │
│   ├── worker/
│   │   ├── report/
│   │   │   ├── data/
│   │   │   │   ├── datasource/report_remote_datasource.dart
│   │   │   │   ├── model/report_request.dart
│   │   │   │   ├── model/report_response.dart
│   │   │   │   └── repository/report_repository_impl.dart
│   │   │   ├── domain/
│   │   │   │   ├── entity/report.dart
│   │   │   │   ├── repository/report_repository.dart
│   │   │   │   └── usecase/submit_report_usecase.dart
│   │   │   └── presentation/
│   │   │       ├── notifier/report_notifier.dart
│   │   │       ├── report_screen.dart
│   │   │       └── widgets/
│   │   │           ├── report_type_tab_bar.dart
│   │   │           ├── hint_banner.dart
│   │   │           ├── diamond_id_field.dart
│   │   │           ├── mic_button.dart
│   │   │           ├── waveform_display.dart
│   │   │           └── transcript_box.dart
│   │   └── history/
│   │       ├── data/
│   │       │   ├── datasource/history_remote_datasource.dart
│   │       │   └── repository/history_repository_impl.dart
│   │       ├── domain/
│   │       │   ├── repository/history_repository.dart
│   │       │   └── usecase/get_history_usecase.dart
│   │       └── presentation/
│   │           ├── notifier/history_notifier.dart
│   │           ├── history_screen.dart
│   │           └── widgets/
│   │               └── report_history_card.dart
│   │
│   ├── dashboard/
│   │   ├── data/
│   │   │   ├── datasource/dashboard_remote_datasource.dart
│   │   │   ├── model/dashboard_response.dart
│   │   │   ├── model/report_details_response.dart
│   │   │   └── repository/dashboard_repository_impl.dart
│   │   ├── domain/
│   │   │   ├── entity/process_defect_count.dart
│   │   │   ├── entity/report_detail.dart
│   │   │   ├── repository/dashboard_repository.dart
│   │   │   ├── usecase/get_dashboard_usecase.dart
│   │   │   └── usecase/get_report_details_usecase.dart
│   │   └── presentation/
│   │       ├── notifier/dashboard_notifier.dart
│   │       ├── notifier/report_details_notifier.dart
│   │       ├── dashboard_screen.dart
│   │       ├── report_details_screen.dart
│   │       └── widgets/
│   │           ├── kpi_summary_row.dart
│   │           ├── period_tab_bar.dart
│   │           ├── defect_rate_chart.dart
│   │           ├── report_card.dart
│   │           └── severity_chips_bar.dart
│   │
│   ├── chatbot/
│   │   ├── data/
│   │   │   ├── datasource/chat_remote_datasource.dart
│   │   │   ├── model/chat_request.dart
│   │   │   ├── model/chat_response.dart
│   │   │   └── repository/chat_repository_impl.dart
│   │   ├── domain/
│   │   │   ├── entity/chat_message.dart
│   │   │   ├── repository/chat_repository.dart
│   │   │   └── usecase/send_message_usecase.dart
│   │   └── presentation/
│   │       ├── notifier/chat_notifier.dart
│   │       ├── chatbot_screen.dart
│   │       └── widgets/
│   │           ├── suggested_prompt_chip.dart
│   │           ├── chat_bubble.dart
│   │           └── chat_input_bar.dart
│   │
│   ├── admin/
│   │   ├── users/
│   │   │   ├── data/
│   │   │   │   ├── datasource/users_remote_datasource.dart
│   │   │   │   ├── model/user_model.dart
│   │   │   │   ├── model/create_user_request.dart
│   │   │   │   └── repository/users_repository_impl.dart
│   │   │   ├── domain/
│   │   │   │   ├── entity/user.dart
│   │   │   │   ├── repository/users_repository.dart
│   │   │   │   ├── usecase/get_users_usecase.dart
│   │   │   │   ├── usecase/create_user_usecase.dart
│   │   │   │   ├── usecase/update_user_usecase.dart
│   │   │   │   └── usecase/delete_user_usecase.dart
│   │   │   └── presentation/
│   │   │       ├── notifier/users_notifier.dart
│   │   │       ├── notifier/user_detail_notifier.dart
│   │   │       ├── users_list_screen.dart
│   │   │       ├── user_detail_screen.dart
│   │   │       ├── create_user_screen.dart
│   │   │       └── widgets/
│   │   │           ├── user_list_tile.dart
│   │   │           └── user_stats_grid.dart
│   │   └── settings/
│   │       ├── data/
│   │       │   └── repository/settings_repository_impl.dart
│   │       ├── domain/
│   │       │   └── usecase/manage_settings_usecase.dart
│   │       └── presentation/
│   │           ├── notifier/settings_notifier.dart
│   │           └── settings_screen.dart
│   │
│   └── profile/
│       ├── data/
│       │   ├── datasource/profile_remote_datasource.dart
│       │   └── repository/profile_repository_impl.dart
│       ├── domain/
│       │   ├── repository/profile_repository.dart
│       │   └── usecase/update_profile_usecase.dart
│       └── presentation/
│           ├── notifier/profile_notifier.dart
│           ├── profile_screen.dart
│           └── widgets/
│               └── language_selector.dart
│
└── shared/
    └── widgets/
        ├── app_scaffold.dart         # Scaffold + role-based BottomNavigationBar
        ├── severity_badge.dart
        ├── report_type_tag.dart
        ├── audio_player_tile.dart
        ├── filter_dropdown.dart
        ├── filter_chip_row.dart
        ├── app_search_bar.dart
        └── loading_overlay.dart
```

---

## 2. Design Tokens

### app_colors.dart
```dart
class AppColors {
  static const primary       = Color(0xFFE8491B); // orange
  static const primaryDark   = Color(0xFF0F1A2E); // near-black navy
  static const loginBg       = Color(0xFF3B0A0A); // dark maroon
  static const background    = Color(0xFFF5F5F5);
  static const surface       = Color(0xFFFFFFFF);
  static const inputFill     = Color(0xFFF0F0F0);

  static const severe        = Color(0xFFE8491B);
  static const moderate      = Color(0xFFFFC107);
  static const low           = Color(0xFF4CAF50);

  static const activeGreen   = Color(0xFF4CAF50);
  static const inactiveRed   = Color(0xFFE53935);

  static const textPrimary   = Color(0xFF1A1A1A);
  static const textSecondary = Color(0xFF6B7280);
  static const textHint      = Color(0xFF9CA3AF);

  static const receiveTagBg  = Color(0xFFEBF5FF);
  static const receiveTagFg  = Color(0xFF1D72E8);
  static const problemTagBg  = Color(0xFFFFF0EB);
  static const problemTagFg  = Color(0xFFE8491B);

  static Color severityColor(String s) => switch (s.toLowerCase()) {
    'severe'   => severe,
    'moderate' => moderate,
    _          => low,
  };
}
```

### app_dimensions.dart
```dart
class AppDimensions {
  static const radiusCard    = 16.0;
  static const radiusInput   = 12.0;
  static const radiusPill    = 100.0;
  static const radiusChip    = 8.0;
  static const pagePadding   = 16.0;
  static const cardPadding   = 16.0;
  static const sectionGap    = 16.0;
  static const itemGap       = 12.0;
  static const inputHeight   = 52.0;
  static const buttonHeight  = 52.0;
  static const micButtonSize = 80.0;
}
```

### app_text_styles.dart
```dart
class AppTextStyles {
  static const appBarTitle  = TextStyle(fontSize: 18, fontWeight: FontWeight.w700);
  static const sectionLabel = TextStyle(fontSize: 11, fontWeight: FontWeight.w700,
                                letterSpacing: 0.8, color: AppColors.textSecondary);
  static const cardTitle    = TextStyle(fontSize: 15, fontWeight: FontWeight.w600);
  static const body         = TextStyle(fontSize: 14, fontWeight: FontWeight.w400);
  static const caption      = TextStyle(fontSize: 12, fontWeight: FontWeight.w400,
                                color: AppColors.textSecondary);
  static const kpiValue     = TextStyle(fontSize: 22, fontWeight: FontWeight.w700);
  static const kpiLabel     = TextStyle(fontSize: 12, fontWeight: FontWeight.w500,
                                color: AppColors.textSecondary);
  static const buttonLabel  = TextStyle(fontSize: 15, fontWeight: FontWeight.w600,
                                color: Colors.white);
}
```

---

## 3. Navigation — GoRouter

```dart
final appRouter = GoRouter(
  initialLocation: '/login',
  redirect: (context, state) => authGuard(context, state),
  routes: [
    GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),

    ShellRoute(
      builder: (_, __, child) => AppScaffold(role: UserRole.worker, child: child),
      routes: [
        GoRoute(path: '/worker/report',  builder: (_, __) => const ReportScreen()),
        GoRoute(path: '/worker/history', builder: (_, __) => const HistoryScreen()),
        GoRoute(path: '/worker/profile', builder: (_, __) => const ProfileScreen()),
      ],
    ),

    ShellRoute(
      builder: (_, __, child) => AppScaffold(role: UserRole.management, child: child),
      routes: [
        GoRoute(path: '/management/dashboard', builder: (_, __) => const DashboardScreen()),
        GoRoute(
          path: '/management/dashboard/:processId',
          builder: (_, state) => ReportDetailsScreen(
            processId: int.parse(state.pathParameters['processId']!),
            period: state.uri.queryParameters['period'] ?? 'daily',
          ),
        ),
        GoRoute(path: '/management/chatbot', builder: (_, __) => const ChatbotScreen()),
        GoRoute(path: '/management/profile', builder: (_, __) => const ProfileScreen()),
      ],
    ),

    ShellRoute(
      builder: (_, __, child) => AppScaffold(role: UserRole.admin, child: child),
      routes: [
        GoRoute(path: '/admin/dashboard', builder: (_, __) => const DashboardScreen()),
        GoRoute(
          path: '/admin/dashboard/:processId',
          builder: (_, state) => ReportDetailsScreen(
            processId: int.parse(state.pathParameters['processId']!),
            period: state.uri.queryParameters['period'] ?? 'daily',
          ),
        ),
        GoRoute(path: '/admin/users',        builder: (_, __) => const UsersListScreen()),
        GoRoute(path: '/admin/users/create', builder: (_, __) => const CreateUserScreen()),
        GoRoute(
          path: '/admin/users/:userId',
          builder: (_, state) => UserDetailScreen(
            userId: int.parse(state.pathParameters['userId']!)),
        ),
        GoRoute(
          path: '/admin/users/:userId/edit',
          builder: (_, state) => CreateUserScreen(
            editUserId: int.parse(state.pathParameters['userId']!)),
        ),
        GoRoute(path: '/admin/chatbot',  builder: (_, __) => const ChatbotScreen()),
        GoRoute(path: '/admin/settings', builder: (_, __) => const SettingsScreen()),
        GoRoute(path: '/admin/profile',  builder: (_, __) => const ProfileScreen()),
      ],
    ),
  ],
);
```

**Transitions:**
- Tab switch: instant (no animation)
- Push (ReportDetails, UserDetail): `SlideTransition` right → left
- Bottom sheets (filters, dropdowns): `showModalBottomSheet`

---

## 4. State Management — Riverpod

```dart
// Auth
final authProvider = AsyncNotifierProvider<AuthNotifier, AuthState>(AuthNotifier.new);

// Report submission
final reportProvider = AsyncNotifierProvider<ReportNotifier, ReportState>(ReportNotifier.new);

// Worker history
final historyProvider = FutureProvider.family<List<Report>, HistoryFilter>(
  (ref, filter) => ref.read(historyRepositoryProvider).getHistory(filter));

// Dashboard
final dashboardProvider = AsyncNotifierProvider<DashboardNotifier, DashboardState>(DashboardNotifier.new);

// Report details drill-down
final reportDetailsProvider = FutureProvider.family<ReportDetailsState, ReportDetailsParams>(
  (ref, params) => ref.read(dashboardRepositoryProvider).getReportDetails(params));

// Users (admin)
final usersProvider = AsyncNotifierProvider<UsersNotifier, UsersState>(UsersNotifier.new);

// User detail
final userDetailProvider = FutureProvider.family<UserDetailState, int>(
  (ref, id) => ref.read(usersRepositoryProvider).getUserDetail(id));

// Chat
final chatProvider = NotifierProvider<ChatNotifier, ChatState>(ChatNotifier.new);

// Global audio player — only one track at a time
final audioPlayerProvider = NotifierProvider<AudioPlayerNotifier, AudioPlayerState>(AudioPlayerNotifier.new);

// App locale
final localeProvider = NotifierProvider<LocaleNotifier, Locale>(LocaleNotifier.new);
```

---

## 5. Key Packages

```yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_localizations:
    sdk: flutter

  go_router: ^13.x.x
  flutter_riverpod: ^2.x.x
  riverpod_annotation: ^2.x.x

  dio: ^5.x.x
  flutter_secure_storage: ^9.x.x

  drift: ^2.x.x
  sqlite3_flutter_libs: ^0.5.x

  record: ^5.x.x
  just_audio: ^0.9.x
  audio_waveforms: ^1.x.x

  mobile_scanner: ^5.x.x
  fl_chart: ^0.68.x

  connectivity_plus: ^6.x.x
  permission_handler: ^11.x.x
  workmanager: ^0.5.x
  intl: ^0.19.x

  firebase_core: ^2.x.x
  firebase_crashlytics: ^3.x.x
  cached_network_image: ^3.x.x

dev_dependencies:
  build_runner: ^2.x.x
  drift_dev: ^2.x.x
  riverpod_generator: ^2.x.x
  json_serializable: ^6.x.x
```

---

## 6. Network Layer — Dio

```dart
// core/network/api_client.dart
Dio createDio(SecureStorage storage) {
  final dio = Dio(BaseOptions(baseUrl: Env.baseUrl));
  dio.interceptors.addAll([
    AuthInterceptor(dio, storage),
    LogInterceptor(responseBody: true),
  ]);
  return dio;
}

// core/network/auth_interceptor.dart
class AuthInterceptor extends Interceptor {
  @override
  void onRequest(options, handler) async {
    final token = await storage.read(key: 'access_token');
    options.headers['Authorization'] = 'Bearer $token';
    handler.next(options);
  }

  @override
  void onError(DioException err, handler) async {
    if (err.response?.statusCode == 401) {
      final refreshed = await _refreshToken();
      if (refreshed) {
        handler.resolve(await dio.fetch(err.requestOptions));
        return;
      }
      ref.read(authProvider.notifier).logout();
    }
    handler.next(err);
  }
}
```

| HTTP | UI |
|---|---|
| 401 | Auto-refresh → force logout if fails |
| 403 | SnackBar "You don't have permission" |
| 422 | Inline field validation errors |
| 5xx | SnackBar "Server error — try again" |
| No network | SnackBar "No connection" + queue on submit |

---

## 7. Offline Queue — Drift

```dart
class PendingReports extends Table {
  IntColumn     get id         => integer().autoIncrement()();
  TextColumn    get workerId   => text()();
  TextColumn    get reportType => text()();
  TextColumn    get diamondId  => text()();
  TextColumn    get audioPath  => text()();
  DateTimeColumn get createdAt => dateTime()();
  TextColumn    get syncStatus => text().withDefault(const Constant('pending'))();
  IntColumn     get retryCount => integer().withDefault(const Constant(0))();
}
```

**Sync (WorkManager one-time task, triggered by `connectivity_plus`):**
```dart
for (final row in await db.pendingReportDao.selectAll()) {
  try {
    await submitReportPipeline(row);
    await db.pendingReportDao.deleteById(row.id);
  } catch (_) {
    final count = row.retryCount + 1;
    await db.pendingReportDao.updateStatus(
      id: row.id,
      status: count >= 3 ? 'failed' : 'pending',
      retryCount: count,
    );
  }
}
```

---

## 8. Screen Specs

### 8.1 Login Screen *(Figma: "login page")*

```dart
Scaffold(backgroundColor: AppColors.loginBg)
└── Center
    └── Column
        ├── Text("Anjali Diamonds",        // white, bold, 28sp
        ├── Text("Sign in to your account") // textSecondary, 14sp
        └── Card(shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)))
            └── Padding(24)
                └── Column
                    ├── _LabeledInput("USERNAME")
                    ├── _LabeledInput("PASSWORD", obscureText: true)
                    ├── Row [ Checkbox(stayLoggedIn), Text("Stay logged in") ]
                    ├── if (error != null) Text(error, color: inactiveRed)
                    └── SizedBox(width: ∞, height: 52)
                        └── ElevatedButton("Sign In")  // primaryDark, CircleShape
```

**`_LabeledInput` spec (matches Figma exactly):**
```dart
Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
  Text(label, style: AppTextStyles.sectionLabel),   // "USERNAME" ALL CAPS
  SizedBox(height: 6),
  TextFormField(
    decoration: InputDecoration(
      filled: true, fillColor: AppColors.inputFill,
      contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppDimensions.radiusInput),
        borderSide: BorderSide(color: Color(0xFFE5E7EB)),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppDimensions.radiusInput),
        borderSide: BorderSide(color: AppColors.primary, width: 1.5),
      ),
    ),
  ),
])
```

---

### 8.2 Worker Report Screen *(Figma: "Worker — Report Page")*

**State enums:**
```dart
enum ReportType      { receive, problem }
enum RecordingState  { idle, recording, recorded }
enum SubmissionState { idle, uploading, transcribing, translating, analysing, success, error, queued }
```

**Widget tree:**
```dart
AppScaffold(tab: WorkerTab.report)
└── Column
    ├── ReportTypeTabBar
    ├── HintBanner (dismissible)
    ├── Padding(16) → DiamondIdField
    ├── Expanded
    │   └── Column(mainAxisAlignment: center)
    │       ├── MicButton
    │       ├── if recorded → WaveformDisplay
    │       └── if transcript.isNotEmpty → TranscriptBox
    └── Padding(16) → SubmitButton
```

#### ReportTypeTabBar *(Figma: orange pill active, outlined inactive)*
```dart
Container(
  padding: EdgeInsets.all(4),
  decoration: BoxDecoration(
    color: Colors.white,
    borderRadius: BorderRadius.circular(AppDimensions.radiusPill),
    border: Border.all(color: Color(0xFFE5E7EB)),
  ),
  child: Row(children: [
    _TabPill("Receive Report", active: type == receive),
    _TabPill("Problem Report", active: type == problem),
  ]),
)

// _TabPill:
// active  → filled orange bg, white text, CircleShape
// inactive→ transparent bg, textPrimary text
```

#### HintBanner *(Figma: white banner, info icon, × dismiss)*
```dart
AnimatedSize(
  duration: Duration(milliseconds: 200),
  child: dismissed ? SizedBox.shrink() : Container(
    color: Colors.white,
    padding: EdgeInsets.symmetric(horizontal: 16, vertical: 10),
    child: Row(children: [
      Icon(Icons.info_outline, size: 16, color: AppColors.textSecondary),
      SizedBox(width: 8),
      Expanded(child: Text(hintText, style: AppTextStyles.caption)),
      IconButton(icon: Icon(Icons.close, size: 16), onPressed: () => dismissed = true),
    ]),
  ),
)
```

#### DiamondIdField *(Figma: dropdown + QR icon)*
```dart
DropdownButtonFormField<String>(   // or TextFormField if free-text chosen
  decoration: InputDecoration(
    hintText: "Diamond ID",
    suffixIcon: IconButton(
      icon: Icon(Icons.qr_code_scanner, color: AppColors.textSecondary),
      onPressed: () => _launchQrScanner(),  // mobile_scanner
    ),
    // same border style as login inputs
  ),
)
```

#### MicButton *(Figma: 80dp orange circle, pulse ring while recording)*
```dart
// AnimationController — repeat, 800ms, curve: Curves.easeInOut
Stack(alignment: Alignment.center, children: [
  if (isRecording)
    AnimatedBuilder(
      animation: _pulseAnim,
      builder: (_, __) => Container(
        width: 80 + (_pulseAnim.value * 24),
        height: 80 + (_pulseAnim.value * 24),
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: AppColors.primary.withOpacity(0.3 * (1 - _pulseAnim.value)),
        ),
      ),
    ),
  GestureDetector(
    onTap: toggleRecording,
    child: Container(
      width: AppDimensions.micButtonSize,
      height: AppDimensions.micButtonSize,
      decoration: BoxDecoration(shape: BoxShape.circle, color: AppColors.primary),
      child: Icon(Icons.mic, color: Colors.white, size: 36),
    ),
  ),
])
```

#### WaveformDisplay *(Figma: orange bars on white bg)*
```dart
// audio_waveforms package — WaveformWidget or RecorderController
WaveformWidget(
  waveformType: WaveformType.multipleChannel,
  activeColor: AppColors.primary,
  inactiveColor: AppColors.primary.withOpacity(0.3),
  showMiddleLine: false,
)
```

#### SubmitButton *(Figma: orange pill, inline progress text)*
```dart
SizedBox(
  width: double.infinity, height: AppDimensions.buttonHeight,
  child: ElevatedButton(
    onPressed: canSubmit ? onSubmit : null,
    style: ElevatedButton.styleFrom(
      backgroundColor: AppColors.primary,
      disabledBackgroundColor: AppColors.inputFill,
      shape: StadiumBorder(),
    ),
    child: isProcessing
      ? Row(mainAxisAlignment: center, children: [
          SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2)),
          SizedBox(width: 8),
          Text(_progressLabel, style: AppTextStyles.buttonLabel),
        ])
      : Row(mainAxisAlignment: center, children: [
          Text("Submit", style: AppTextStyles.buttonLabel),
          SizedBox(width: 8),
          Icon(Icons.arrow_forward, color: Colors.white, size: 18),
        ]),
  ),
)

String get _progressLabel => switch (submissionState) {
  SubmissionState.uploading    => 'Uploading…',
  SubmissionState.transcribing => 'Transcribing…',
  SubmissionState.translating  => 'Translating…',
  SubmissionState.analysing    => 'Analysing…',
  _                            => 'Submit',
};
```

**Submission flow:**
```
1. state → uploading   PUT /audio/upload (multipart)  → fileUuid
2. state → transcribing POST /sarvam/stt               → transcriptOriginal
3. state → translating  POST /gemini/translate          → transcriptEnglish
4. state → analysing    POST /reports                   → {reportId, severity, defectType, chain}
5. state → success      show transcript + severity badge
   chain ran            → show attribution banner
   no network           → INSERT PendingReport → state = queued
```

---

### 8.3 Worker History Screen *(Figma: "Html → Body")*

```dart
Scaffold(appBar: AppBar(title: Text("History")))
└── Column
    ├── AppSearchBar(hint: "Search by Diamond ID…")
    ├── FilterChipRow(options: ["All Types", "Receive Report", "Problem Report"])
    └── Expanded
        └── ListView.builder → ReportHistoryCard
```

#### ReportHistoryCard *(Figma: white card, colored dot, type tag, transcript)*
```dart
Container(
  margin: EdgeInsets.symmetric(horizontal: 16, vertical: 6),
  padding: EdgeInsets.all(14),
  decoration: BoxDecoration(
    color: Colors.white,
    borderRadius: BorderRadius.circular(AppDimensions.radiusCard),
  ),
  child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
    Row(children: [
      _StatusDot(AppColors.severityColor(severity)),
      SizedBox(width: 8),
      Text(diamondId, style: AppTextStyles.cardTitle),
      Spacer(),
      Text(formattedTime, style: AppTextStyles.caption),
    ]),
    SizedBox(height: 8),
    ReportTypeTag(type: reportType),
    SizedBox(height: 6),
    Text(transcriptSnippet, style: AppTextStyles.body,
      maxLines: 2, overflow: TextOverflow.ellipsis),
  ]),
)
```

---

### 8.4 Dashboard Screen *(Figma: "Admin home")*

**Auto-refresh:**
```dart
late Timer _timer;

@override void initState() {
  super.initState();
  _timer = Timer.periodic(const Duration(seconds: 10), (_) =>
    ref.refresh(dashboardProvider));
}
@override void dispose() { _timer.cancel(); super.dispose(); }
```

```dart
AppScaffold
└── Column
    ├── KpiSummaryRow
    ├── PeriodTabBar           // Daily · Weekly · Monthly, orange underline active
    └── Expanded
        └── SingleChildScrollView
            └── Column
                ├── Padding → Text("Defect Rate by Process", style: cardTitle)
                └── DefectRateChart
```

#### KpiSummaryRow *(Figma: 3 white cards)*
```dart
Row(children: [
  Expanded(child: KpiCard("TOTAL REPORTS", totalReports.toString())),
  SizedBox(width: 8),
  Expanded(child: KpiCard("EMPLOYEES INVOLVED", employees.toString(),
    valueColor: Colors.blue)),
  SizedBox(width: 8),
  Expanded(child: SeverityKpiCard(severe: s, moderate: m, low: l)),
])

// KpiCard: white rounded-16 card, kpiValue + kpiLabel styles
// SeverityKpiCard: stacked rows — "5 Severe" orange / "2 Moderate" amber / "1 Low" green
```

#### DefectRateChart *(Figma: horizontal orange bars, count at tip)*
```dart
// fl_chart BarChart — rotated horizontal style
// OR simpler: custom ListView rows with FractionallySizedBox bars
SizedBox(
  height: data.length * 48.0,
  child: ListView.builder(
    physics: NeverScrollableScrollPhysics(),
    itemCount: data.length,
    itemBuilder: (_, i) {
      final item = data[i];
      final fraction = item.count / maxCount;
      return GestureDetector(
        onTap: () => context.push('/admin/dashboard/${item.processId}?period=$period'),
        child: SizedBox(height: 48,
          child: Row(children: [
            SizedBox(width: 80, child: Text(item.processName, style: AppTextStyles.body)),
            Expanded(
              child: Align(alignment: Alignment.centerLeft,
                child: FractionallySizedBox(
                  widthFactor: fraction.clamp(0.02, 1.0),
                  child: Container(
                    height: 12,
                    decoration: BoxDecoration(
                      color: AppColors.primary,
                      borderRadius: BorderRadius.circular(6),
                    ),
                  ),
                ),
              ),
            ),
            SizedBox(width: 8),
            Text(item.count.toString(), style: AppTextStyles.body),
          ]),
        ),
      );
    },
  ),
)
```

---

### 8.5 Report Details Screen *(Figma: "Html → Body-2")*

```dart
Scaffold
├── AppBar(
│     title: Column([Text("Report Details"), Text("$process · $period", caption)]),
│     actions: [IconButton(Icons.close)])
└── Column
    ├── StatsRow          // Total Reports · Workers · Defect %
    ├── SeverityChipsBar  // chips + gradient bar
    ├── AppSearchBar("Search reports…")
    ├── FilterRow         // All Types ▾ · All Severity ▾ · Sort: Newest
    └── Expanded → ListView.builder → ReportCard
```

#### SeverityChipsBar *(Figma: chips + gradient progress bar)*
```dart
Column(children: [
  Row(children: [
    _SeverityChip(AppColors.severe,   "$severe Severe"),
    SizedBox(width: 8),
    _SeverityChip(AppColors.moderate, "$moderate Moderate"),
    SizedBox(width: 8),
    _SeverityChip(AppColors.low,      "$low Low"),
  ]),
  SizedBox(height: 8),
  Container(
    height: 6,
    decoration: BoxDecoration(
      borderRadius: BorderRadius.circular(AppDimensions.radiusPill),
      gradient: LinearGradient(colors: [
        AppColors.severe, AppColors.moderate, AppColors.low]),
    ),
  ),
])
```

#### ReportCard *(Figma: full detail card with audio player)*
```dart
Container(
  margin: EdgeInsets.symmetric(horizontal: 16, vertical: 6),
  padding: EdgeInsets.all(14),
  decoration: BoxDecoration(color: Colors.white,
    borderRadius: BorderRadius.circular(12)),
  child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
    Row(children: [
      _StatusDot(AppColors.severityColor(severity)),
      SizedBox(width: 6),
      _DiamondIdBadge(diamondId),      // e.g. "D-67676"
      SizedBox(width: 6),
      ReportTypeTag(type: reportType),
      Spacer(),
      SeverityBadge(severity: severity),
    ]),
    SizedBox(height: 6),
    Text("$workerName · Dept: $dept", style: AppTextStyles.caption),
    SizedBox(height: 8),
    Text(gujaratiTranscript, maxLines: 3, overflow: TextOverflow.ellipsis),
    SizedBox(height: 8),
    AudioPlayerTile(url: audioUrl, durationSeconds: duration),
    SizedBox(height: 6),
    Row(children: [
      Text(formattedDateTime, style: AppTextStyles.caption),
      Spacer(),
      _DefectTypeTag(defectType),     // e.g. "Burn/Crack" orange text
    ]),
  ]),
)
```

#### AudioPlayerTile *(Figma: orange play button + waveform + time)*
```dart
// just_audio + audio_waveforms
// Global AudioPlayerNotifier (Riverpod) ensures only one plays at a time
Row(children: [
  GestureDetector(
    onTap: () => audioPlayerNotifier.toggle(url),
    child: CircleAvatar(
      radius: 20, backgroundColor: AppColors.primary,
      child: Icon(isPlaying ? Icons.pause : Icons.play_arrow,
        color: Colors.white, size: 20),
    ),
  ),
  SizedBox(width: 8),
  Expanded(child: WaveformPlayerWidget(url: url,
    activeColor: AppColors.primary,
    inactiveColor: AppColors.primary.withOpacity(0.3))),
  SizedBox(width: 8),
  Text(formatDuration(durationSeconds), style: AppTextStyles.caption),
])
```

---

### 8.6 Diamond Assistant Screen *(Figma: "Html → Body-3")*

```dart
Scaffold
├── AppBar(
│     leading: BackButton(),
│     title: Column([
│       Text("Diamond Assistant"),
│       _OnlineIndicator(),   // ● ONLINE green
│     ]),
│     actions: [TextButton("Clear", onPressed: chatNotifier.clear)])
└── Column
    ├── Expanded
    │   └── ListView.builder(reverse: true)
    │       ├── if empty → WelcomeCard
    │       ├── if empty → SuggestedPromptChips
    │       └── ChatBubble per message
    └── ChatInputBar
```

#### WelcomeCard *(Figma: robot avatar, greeting, description)*
```dart
Center(
  child: Container(
    margin: EdgeInsets.all(24),
    padding: EdgeInsets.all(24),
    decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16)),
    child: Column(children: [
      CircleAvatar(radius: 40, backgroundColor: AppColors.primary,
        child: Icon(Icons.smart_toy, color: Colors.white, size: 36)),
      SizedBox(height: 16),
      Text("Hi Admin 👋", style: AppTextStyles.cardTitle),
      SizedBox(height: 8),
      Text("I'm your AI assistant for Diamond Quality Control.\nAsk me about worker efficiency or process bottlenecks.",
        textAlign: TextAlign.center, style: AppTextStyles.caption),
    ]),
  ),
)
```

#### SuggestedPromptChips *(Figma: 3 outlined chips)*
```dart
const _prompts = [
  (Icons.trending_up,   "Top defective workers this month"),
  (Icons.warning_amber, "Severe defects today"),
  (Icons.history,       "Last night's shift summary"),
];

Column(children: _prompts.map((p) =>
  GestureDetector(
    onTap: () => chatNotifier.sendMessage(p.$2),
    child: Container(
      margin: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      padding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Color(0xFFE5E7EB)),
      ),
      child: Row(children: [
        Icon(p.$1, size: 18, color: AppColors.textSecondary),
        SizedBox(width: 10),
        Text(p.$2, style: AppTextStyles.body),
      ]),
    ),
  )).toList())
```

#### ChatBubble
```dart
// User: right-aligned, orange bg, white text
// AI: left-aligned, white card, robot avatar left
Align(
  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
  child: Container(
    constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
    margin: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
    padding: EdgeInsets.all(12),
    decoration: BoxDecoration(
      color: isUser ? AppColors.primary : Colors.white,
      borderRadius: BorderRadius.circular(12),
    ),
    child: Text(text,
      style: AppTextStyles.body.copyWith(
        color: isUser ? Colors.white : AppColors.textPrimary)),
  ),
)
```

#### ChatInputBar *(Figma: paperclip + text + mic + orange send)*
```dart
Container(
  padding: EdgeInsets.symmetric(horizontal: 8, vertical: 6),
  decoration: BoxDecoration(
    color: Colors.white,
    border: Border(top: BorderSide(color: Color(0xFFE5E7EB))),
  ),
  child: Row(children: [
    IconButton(Icons.attach_file, color: AppColors.textSecondary, onPressed: null),
    Expanded(child: TextField(controller: _controller,
      decoration: InputDecoration(hintText: "Ask anything…", border: InputBorder.none))),
    IconButton(Icons.mic, color: AppColors.textSecondary, onPressed: _recordQuery),
    CircleAvatar(
      radius: 20, backgroundColor: AppColors.primary,
      child: IconButton(icon: Icon(Icons.send, color: Colors.white, size: 18),
        onPressed: isLoading ? null : _send),
    ),
  ]),
)
// Typing indicator: AI bubble with 3 animated dots while awaiting response
```

---

### 8.7 Profile Screen *(Figma: Worker / Management / Admin Profile)*

```dart
Scaffold(appBar: AppBar(title: Text(roleTitle), leading: BackButton()))
└── SingleChildScrollView
    └── Column(children: [
        ProfileHeaderCard(),
        SizedBox(height: AppDimensions.sectionGap),
        AccountCard(),
        SizedBox(height: AppDimensions.sectionGap),
        LanguageCard(),
        SizedBox(height: AppDimensions.sectionGap),
        SignOutCard(),
    ])
```

#### ProfileHeaderCard *(Figma: orange avatar + edit pencil + name + emp code)*
```dart
Container(
  padding: EdgeInsets.all(AppDimensions.cardPadding),
  decoration: BoxDecoration(color: Colors.white,
    borderRadius: BorderRadius.circular(AppDimensions.radiusCard)),
  child: Row(children: [
    Stack(children: [
      CircleAvatar(radius: 28, backgroundColor: AppColors.primary,
        child: Text(nameInitial, style: TextStyle(color: Colors.white, fontSize: 22))),
      Positioned(right: 0, bottom: 0,
        child: CircleAvatar(radius: 10, backgroundColor: AppColors.primary,
          child: Icon(Icons.edit, size: 12, color: Colors.white))),
    ]),
    SizedBox(width: 12),
    Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(name, style: AppTextStyles.cardTitle),
      Text(empCode, style: AppTextStyles.caption),
    ]),
  ]),
)
```

#### AccountCard *(Figma: field rows + Edit button)*
```dart
Container(
  padding: EdgeInsets.all(AppDimensions.cardPadding),
  decoration: BoxDecoration(color: Colors.white,
    borderRadius: BorderRadius.circular(AppDimensions.radiusCard)),
  child: Column(children: [
    Row(children: [
      Text("ACCOUNT", style: AppTextStyles.sectionLabel),
      Spacer(),
      TextButton("Edit", onPressed: _openEditSheet,
        style: TextButton.styleFrom(foregroundColor: AppColors.primary)),
    ]),
    Divider(),
    _InfoRow("USERNAME",   username),
    _InfoRow("DEPARTMENT", department),
    if (isWorker) _InfoRow("PROCESS", process),
    _InfoRow("Mobile",     mobile),
    _InfoRow("ADDRESS",    address.isEmpty ? "—" : address),
  ]),
)
```

#### LanguageCard *(Figma: 3-pill toggle — English · ગુજરાતી · हिंदी)*
```dart
Container(
  padding: EdgeInsets.all(AppDimensions.cardPadding),
  decoration: BoxDecoration(color: Colors.white,
    borderRadius: BorderRadius.circular(AppDimensions.radiusCard)),
  child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
    Text("Language", style: AppTextStyles.cardTitle),
    SizedBox(height: 12),
    Row(children: [
      LanguagePill(label: "English",  sub: "English",  lang: "en", current: currentLang),
      SizedBox(width: 8),
      LanguagePill(label: "ગુજરાતી", sub: "Gujarati", lang: "gu", current: currentLang),
      SizedBox(width: 8),
      LanguagePill(label: "हिंदी",   sub: "Hindi",    lang: "hi", current: currentLang),
    ]),
  ]),
)

// LanguagePill:
// selected   → Container with orange border (1.5dp) + orange text
// unselected → plain Text, no border
// onTap      → PATCH /users/me + ref.read(localeProvider.notifier).set(Locale(lang))
```

#### SignOutCard
```dart
Container(
  decoration: BoxDecoration(color: Colors.white,
    borderRadius: BorderRadius.circular(AppDimensions.radiusCard)),
  child: ListTile(
    leading: Container(
      padding: EdgeInsets.all(8),
      decoration: BoxDecoration(color: Color(0xFFFFEBEB),
        borderRadius: BorderRadius.circular(10)),
      child: Icon(Icons.logout, color: AppColors.inactiveRed, size: 20),
    ),
    title: Text("Sign Out",
      style: TextStyle(color: AppColors.inactiveRed, fontWeight: FontWeight.w600)),
    onTap: () => _confirmSignOut(context),
  ),
)
```

---

### 8.8 Admin — Users List Screen *(Figma: "Admin — Users List")*

```dart
Scaffold
├── AppBar(title: "Users", actions: [
│     TextButton.icon(Icons.add, "Add",
│       style: ...(backgroundColor: AppColors.primary, rounded))
│   ])
└── Column
    ├── AppSearchBar("Search by name, username or emp code…")
    ├── FilterChipRow(["Role ▾", "Department ▾", "Status ▾"])
    └── Expanded → ListView.builder → UserListTile
```

#### UserListTile *(Figma: status dot + index + name + emp + factory)*
```dart
ListTile(
  leading: Row(mainAxisSize: MainAxisSize.min, children: [
    _StatusDot(isActive ? AppColors.activeGreen : AppColors.inactiveRed, size: 10),
    SizedBox(width: 6),
    Text("$index", style: AppTextStyles.caption),
  ]),
  title: Text(name, style: AppTextStyles.cardTitle),
  subtitle: Text("$empCode · $roleTitle", style: AppTextStyles.caption),
  trailing: Text(factoryName, style: AppTextStyles.caption),
  onTap: () => context.push('/admin/users/$userId'),
)
```

**Filter chips** tap → `showModalBottomSheet` with radio list of options.

---

### 8.9 Admin — User Detail Screen *(Figma: "Admin — User Detail")*

```dart
Scaffold
├── AppBar(title: name, bottom: Text("$factory · $status"),
│     actions: [OutlinedButton("Delete", style: ...(red))])
└── SingleChildScrollView
    └── Column
        ├── UserStatsGrid
        ├── SizedBox(16)
        ├── UserDetailsCard
        └── RecentReportsSection
```

#### UserStatsGrid *(Figma: 3×2 grid)*
```dart
GridView.count(
  crossAxisCount: 3, shrinkWrap: true,
  physics: NeverScrollableScrollPhysics(),
  childAspectRatio: 1.4,
  children: [
    _StatCell("TOTAL REPORTS", "$total",     AppColors.textPrimary),
    _StatCell("SEVERE",         "$severe",    AppColors.severe),
    _StatCell("MODERATE",       "$moderate",  AppColors.moderate),
    _StatCell("LOW",            "$low",       AppColors.low),
    _StatCell("FAULT RATE",    "$faultRate%", AppColors.inactiveRed),
    _StatCell("STATUS",         status,       statusColor),
  ],
)
// faultRate = (problemCount / totalCount * 100).round()
```

#### UserDetailsCard
```dart
Container(
  padding: EdgeInsets.all(16), color: Colors.white, borderRadius: 16,
  child: Column(children: [
    Row([Text("DETAILS", style: sectionLabel), Spacer(),
      TextButton("✎ Edit", onPressed: _openEdit)]),
    Divider(),
    _DetailRow("Emp Code",    empCode),
    _DetailRow("Username",    username),
    _PasswordRow(password),            // masked + eye toggle
    _DetailRow("Role",        role),
    _DetailRow("Department",  department),
    _DetailRow("Factory",     factory),
    _DetailRow("Floor",       floor),
    _DetailRow("Table",       table),
    _DetailRow("Process",     process),
    _DetailRow("Joining Date", joiningDate),
    _DetailRow("Mobile",      mobile),
    _DetailRow("Address",     address),
  ]),
)
```

---

### 8.10 Admin — Create User Screen *(Figma: "Html → Body-1")*

```dart
Scaffold(appBar: AppBar(title: Text("Create User")))
└── SingleChildScrollView
    └── Column(children: [
        _EmpCodeCard(),
        _IdentityCard(),
        _AssignmentCard(),
        _ContactCard(),
        SizedBox(height: 80),   // space for button
      ])
    // Pinned bottom button
    └── Positioned(bottom: 16) → _CreateUserButton()
```

#### _EmpCodeCard
```dart
// Row: Factory + Floor + Table (3 equal fields inline)
Row(children: [
  Expanded(child: _LabeledInput("Factory")),
  SizedBox(width: 8),
  Expanded(child: _LabeledInput("Floor")),
  SizedBox(width: 8),
  Expanded(child: _LabeledInput("Table")),
])
SizedBox(height: 12)
// Read-only auto-generated code field (grey bg)
Container(
  width: double.infinity, padding: EdgeInsets.all(14),
  decoration: BoxDecoration(color: AppColors.inputFill,
    borderRadius: BorderRadius.circular(AppDimensions.radiusInput)),
  child: Text(empCode, style: AppTextStyles.body),
)
Text("Auto-generated from Factory + Floor + Table", style: AppTextStyles.caption)

// Debounced: factory/floor/table onChange → GET /emp-code/next → update field
```

#### _CreateUserButton *(Figma: orange pill, + Create User)*
```dart
SizedBox(
  width: double.infinity, height: AppDimensions.buttonHeight,
  child: ElevatedButton.icon(
    icon: Icon(Icons.add, color: Colors.white),
    label: Text("Create User", style: AppTextStyles.buttonLabel),
    style: ElevatedButton.styleFrom(
      backgroundColor: AppColors.primary,
      shape: StadiumBorder(),
    ),
    onPressed: _submitForm,
  ),
)
```

---

## 9. Shared Widgets

### SeverityBadge
```dart
Container(
  padding: EdgeInsets.symmetric(horizontal: 8, vertical: 3),
  decoration: BoxDecoration(
    color: color.withOpacity(0.12),
    borderRadius: BorderRadius.circular(AppDimensions.radiusPill),
    border: Border.all(color: color, width: 0.5),
  ),
  child: Row(children: [
    Container(width: 6, height: 6,
      decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
    SizedBox(width: 4),
    Text(severity, style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.w600)),
  ]),
)
```

### ReportTypeTag
```dart
Container(
  padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
  decoration: BoxDecoration(
    color: isReceive ? AppColors.receiveTagBg : AppColors.problemTagBg,
    borderRadius: BorderRadius.circular(6),
  ),
  child: Text(isReceive ? "RECEIVE" : "PROBLEM",
    style: TextStyle(
      color: isReceive ? AppColors.receiveTagFg : AppColors.problemTagFg,
      fontSize: 11, fontWeight: FontWeight.w600)),
)
```

### AppScaffold
```dart
Scaffold(
  backgroundColor: AppColors.background,
  body: child,
  bottomNavigationBar: NavigationBar(
    backgroundColor: Colors.white,
    indicatorColor: Colors.transparent,
    selectedIndex: _currentIndex,
    onDestinationSelected: _onTap,
    destinations: _tabsForRole(role).map((t) =>
      NavigationDestination(
        icon: Icon(t.icon, color: AppColors.textSecondary),
        selectedIcon: Icon(t.icon, color: AppColors.primary),
        label: t.label,
      )).toList(),
  ),
)
```

---

## 10. Audio Pipeline

```
record package
  └── WAV, 16kHz, mono → getTemporaryDirectory()/<uuid>.wav
      └── Dio multipart PUT /audio/upload → { fileUuid }
          └── POST /sarvam/stt { fileUuid }
              → { transcript_original }       [Sarvam saarika:v2]
              └── POST /gemini/translate { text }
                  → { transcript_english }     [Gemini gemini-2.0-flash]
                  └── POST /reports { ... }
                      → { reportId, severity, defectType, chain }
                      └── Riverpod state update → UI rebuilds
```

Max recording: 120 s (Timer auto-stops).
Global `AudioPlayerNotifier` — only one `AudioPlayer` active at a time.

---

## 11. Localisation

```
lib/l10n/
  app_en.arb   # English (default)
  app_gu.arb   # Gujarati
  app_hi.arb   # Hindi
```

Worker-facing strings only in v1. Language switch via `localeProvider` + `PATCH /users/me`.

---

## 12. Permissions

| Permission | Trigger | Package |
|---|---|---|
| Microphone | First mic button tap | `permission_handler` |
| Camera | First QR icon tap | `permission_handler` |
| Notifications | First launch | `permission_handler` |

Denied → rationale dialog → `openAppSettings()`.

**AndroidManifest.xml:**
```xml
<uses-permission android:name="android.permission.RECORD_AUDIO"/>
<uses-permission android:name="android.permission.CAMERA"/>
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
```

**iOS Info.plist:**
```xml
<key>NSMicrophoneUsageDescription</key><string>Required to record defect reports</string>
<key>NSCameraUsageDescription</key><string>Required to scan diamond QR codes</string>
```

---

## 13. Build & Environment

```
# Development
flutter run --dart-define=BASE_URL=http://192.168.x.x:8000

# Production
flutter build apk --dart-define=BASE_URL=https://api.anjalidiamonds.com
flutter build ios --dart-define=BASE_URL=https://api.anjalidiamonds.com
```

- **Min Android SDK:** API 26
- **Target Android SDK:** API 35
- **iOS Deployment Target:** 15.0
- **iOS builds:** Codemagic CI (no Mac needed)

---

## 14. Testing Strategy

| Layer | Tool | What |
|---|---|---|
| Unit | `flutter_test` | Riverpod notifiers, API parsing, emp code generation, fault rate calc |
| Widget | `WidgetTester` | ReportTypeTabBar, MicButton states, SeverityBadge, ReportCard |
| Integration | `integration_test` + mock Dio | Submission E2E (mock Sarvam + Gemini), offline queue sync |
| Golden | `golden_toolkit` | LoginScreen, KPI row, ReportCard — design regression snapshots |
