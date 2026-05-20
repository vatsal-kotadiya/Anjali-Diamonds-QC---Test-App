# Diamond QC — Technical Requirements Document

**Version:** 2.0 (rewritten for Kotlin Multiplatform)
**Date:** 2026-05-20
**Companion doc:** PRD v1.1
**Platform:** KMP — Jetpack Compose (Android) + SwiftUI (iOS)

---

## 1. Architecture Overview

```
AnjalidDiamondsApp/
├── androidApp/                       ← Jetpack Compose UI (Android)
│   └── src/main/kotlin/com/anjali/android/
│       ├── MainActivity.kt
│       ├── DiamondApplication.kt     ← Koin init
│       ├── navigation/AppNavHost.kt
│       ├── theme/                    ← AppColors, AppTheme, AppTypography
│       └── features/
│           ├── auth/LoginScreen.kt
│           ├── worker/ReportScreen.kt, HistoryScreen.kt
│           ├── dashboard/DashboardScreen.kt, ReportDetailsScreen.kt
│           ├── admin/UsersScreen.kt, UserDetailScreen.kt, CreateUserScreen.kt
│           ├── chatbot/ChatbotScreen.kt
│           └── profile/ProfileScreen.kt
│
├── iosApp/                           ← SwiftUI UI (iOS)
│   └── iosApp/
│       ├── DiamondApp.swift          ← Koin init via shared initKoin()
│       ├── ContentView.swift
│       ├── Navigation/AppRouter.swift
│       └── Features/
│           ├── Auth/LoginView.swift
│           ├── Worker/ReportView.swift, HistoryView.swift
│           ├── Dashboard/DashboardView.swift, ReportDetailsView.swift
│           ├── Admin/UsersView.swift, UserDetailView.swift, CreateUserView.swift
│           ├── Chatbot/ChatbotView.swift
│           └── Profile/ProfileView.swift
│
└── shared/                           ← KMP shared module (business logic)
    └── src/
        ├── commonMain/kotlin/com/anjali/
        │   ├── data/
        │   │   ├── network/          ← Ktor client, interceptors, DTOs
        │   │   ├── local/            ← SQLDelight DAOs + schema
        │   │   └── repository/       ← ReportRepo, UserRepo, ChatRepo
        │   ├── domain/
        │   │   ├── model/            ← Report, User, AiAnalysis, DiamondChain
        │   │   └── usecase/          ← SubmitReport, GetDashboard, SyncPending
        │   ├── presentation/         ← ViewModels + UI state (StateFlow)
        │   │   ├── AuthViewModel.kt
        │   │   ├── ReportViewModel.kt
        │   │   ├── HistoryViewModel.kt
        │   │   ├── DashboardViewModel.kt
        │   │   ├── UsersViewModel.kt
        │   │   └── ChatViewModel.kt
        │   └── platform/             ← expect declarations
        │       ├── AudioRecorder.kt
        │       ├── SecureStorage.kt
        │       └── FileSystem.kt
        ├── androidMain/kotlin/       ← actual implementations (Android)
        └── iosMain/kotlin/           ← actual implementations (iOS)
```

---

## 2. Shared vs Platform-Specific Split

### Shared (commonMain) — write once
| Layer | What | Library |
|---|---|---|
| Networking | Ktor HttpClient, all API calls, JWT interceptor | `ktor-client-core` |
| Serialization | All request/response data classes | `kotlinx-serialization-json` |
| Local DB | Offline queue, SQLDelight queries | `SQLDelight` |
| Coroutines | All async, StateFlow, channels | `kotlinx-coroutines-core` |
| DI | Koin modules, all deps wired here | `koin-core` |
| ViewModels | StateFlow-based, consumed by both platforms | `lifecycle-viewmodel` (KMP) |
| Domain models | `Report`, `User`, `AiAnalysis`, `DiamondChain` | Plain Kotlin data classes |
| Date/time | Timestamps, period filtering | `kotlinx-datetime` |
| Preferences | Language pref, non-sensitive settings | `multiplatform-settings` |

### Platform-Specific — implement per platform via expect/actual
| Feature | Android | iOS |
|---|---|---|
| UI framework | Jetpack Compose | SwiftUI |
| Navigation | Navigation Compose | NavigationStack |
| Audio recording | `MediaRecorder` (SDK) | `AVAudioRecorder` |
| Audio playback | `ExoPlayer` (Media3) | `AVAudioPlayer` |
| Waveform | `Canvas` (Compose) | Custom `Shape` (SwiftUI) |
| QR scanning | CameraX + ML Kit | `AVFoundation` + `CoreImage` |
| Secure JWT storage | `EncryptedSharedPreferences` | Keychain |
| Background sync | `WorkManager` | `BGTaskScheduler` |
| Push notifications | FCM | APNs |
| Crash reporting | Firebase Crashlytics (Android SDK) | Firebase Crashlytics (iOS SDK) |
| Charts | Vico (`compose-m3`) | SwiftUI Charts (iOS 16+) |
| Localisation | `strings.xml` | `Localizable.strings` |

---

## 3. Libraries

### shared/build.gradle.kts

```kotlin
plugins {
    alias(libs.plugins.kotlinMultiplatform)
    alias(libs.plugins.kotlinSerialization)
    alias(libs.plugins.sqlDelight)
    id("co.touchlab.skie") version "0.8.x"          // Swift coroutine bridging
}

kotlin {
    androidTarget()
    iosX64(); iosArm64(); iosSimulatorArm64()

    sourceSets {
        commonMain.dependencies {
            // Networking
            implementation("io.ktor:ktor-client-core:2.3.x")
            implementation("io.ktor:ktor-client-auth:2.3.x")
            implementation("io.ktor:ktor-client-content-negotiation:2.3.x")
            implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.x")
            implementation("io.ktor:ktor-client-logging:2.3.x")

            // Coroutines + serialization + datetime
            implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.x")
            implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.x")
            implementation("org.jetbrains.kotlinx:kotlinx-datetime:0.5.x")

            // DB
            implementation("app.cash.sqldelight:coroutines-extensions:2.x")

            // DI
            implementation("io.insert-koin:koin-core:3.5.x")

            // ViewModel (KMP-compatible)
            implementation("androidx.lifecycle:lifecycle-viewmodel:2.8.x")

            // Preferences
            implementation("com.russhwolf:multiplatform-settings:1.1.x")
            implementation("com.russhwolf:multiplatform-settings-coroutines:1.1.x")

            // SKIE annotations (Swift coroutine bridge)
            implementation("co.touchlab.skie:configuration-annotations:0.8.x")
        }

        androidMain.dependencies {
            implementation("io.ktor:ktor-client-okhttp:2.3.x")
            implementation("app.cash.sqldelight:android-driver:2.x")
            implementation("io.insert-koin:koin-android:3.5.x")
            implementation("io.insert-koin:koin-androidx-compose:3.5.x")
            implementation("androidx.work:work-runtime-ktx:2.9.x")
        }

        iosMain.dependencies {
            implementation("io.ktor:ktor-client-darwin:2.3.x")
            implementation("app.cash.sqldelight:native-driver:2.x")
        }
    }
}
```

### androidApp/build.gradle.kts

```kotlin
dependencies {
    implementation(project(":shared"))

    // Compose BOM
    implementation(platform("androidx.compose:compose-bom:2024.x"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.foundation:foundation")
    implementation("androidx.compose.ui:ui-tooling-preview")

    // Navigation
    implementation("androidx.navigation:navigation-compose:2.7.x")

    // Lifecycle
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.x")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.8.x")

    // DI
    implementation("io.insert-koin:koin-androidx-compose:3.5.x")

    // Audio playback
    implementation("androidx.media3:media3-exoplayer:1.3.x")
    implementation("androidx.media3:media3-ui:1.3.x")

    // Charts
    implementation("com.patrykandpatrick.vico:compose-m3:1.x")

    // QR scanning
    implementation("androidx.camera:camera-camera2:1.3.x")
    implementation("androidx.camera:camera-lifecycle:1.3.x")
    implementation("androidx.camera:camera-view:1.3.x")
    implementation("com.google.mlkit:barcode-scanning:17.x")

    // Crash reporting
    implementation("com.google.firebase:firebase-crashlytics-ktx")
    implementation("com.google.firebase:firebase-analytics-ktx")
}
```

### iosApp — Swift Package Manager (SPM)

```swift
// Package.swift dependencies (or via Xcode SPM UI)
.package(url: "https://github.com/firebase/firebase-ios-sdk", from: "10.x.x")

// Frameworks used (all built-in, no SPM needed):
// AVFoundation    — audio recording + playback + QR scanning
// Security        — Keychain access
// BackgroundTasks — BGTaskScheduler
// Charts          — SwiftUI Charts (iOS 16+)
```

---

## 4. expect/actual Declarations

### AudioRecorder

```kotlin
// commonMain/platform/AudioRecorder.kt
expect class AudioRecorder() {
    fun start(outputPath: String)
    fun stop(): String          // returns final file path
    val isRecording: StateFlow<Boolean>
}
```

```kotlin
// androidMain
actual class AudioRecorder actual constructor() {
    private var recorder: MediaRecorder? = null
    private val _isRecording = MutableStateFlow(false)
    actual val isRecording: StateFlow<Boolean> = _isRecording

    actual fun start(outputPath: String) {
        recorder = MediaRecorder().apply {
            setAudioSource(MediaRecorder.AudioSource.MIC)
            setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
            setAudioSamplingRate(16000)
            setAudioChannels(1)
            setOutputFile(outputPath)
            prepare(); start()
        }
        _isRecording.value = true
    }

    actual fun stop(): String {
        recorder?.stop(); recorder?.release(); recorder = null
        _isRecording.value = false
        return outputPath
    }
}
```

```kotlin
// iosMain — delegates to AVAudioRecorder via Objective-C interop
actual class AudioRecorder actual constructor() {
    private var recorder: AVAudioRecorder? = null
    private val _isRecording = MutableStateFlow(false)
    actual val isRecording: StateFlow<Boolean> = _isRecording

    actual fun start(outputPath: String) {
        val url = NSURL.fileURLWithPath(outputPath)
        val settings = mapOf(
            AVFormatIDKey to kAudioFormatMPEG4AAC,
            AVSampleRateKey to 16000,
            AVNumberOfChannelsKey to 1
        )
        recorder = AVAudioRecorder(url, settings, null)
        recorder?.record()
        _isRecording.value = true
    }

    actual fun stop(): String {
        recorder?.stop(); recorder = null
        _isRecording.value = false
        return outputPath
    }
}
```

### SecureStorage

```kotlin
// commonMain/platform/SecureStorage.kt
expect class SecureStorage() {
    fun putString(key: String, value: String)
    fun getString(key: String): String?
    fun clear()
}
```

```kotlin
// androidMain — EncryptedSharedPreferences
actual class SecureStorage actual constructor() {
    private val prefs = EncryptedSharedPreferences.create(
        "diamond_secure", MasterKey.Builder(context).build(),
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )
    actual fun putString(key: String, value: String) = prefs.edit().putString(key, value).apply()
    actual fun getString(key: String) = prefs.getString(key, null)
    actual fun clear() = prefs.edit().clear().apply()
}
```

```kotlin
// iosMain — Keychain
actual class SecureStorage actual constructor() {
    actual fun putString(key: String, value: String) { /* SecItemAdd/SecItemUpdate */ }
    actual fun getString(key: String): String? { /* SecItemCopyMatching */ }
    actual fun clear() { /* SecItemDelete for all app keys */ }
}
```

### FileSystem

```kotlin
// commonMain/platform/FileSystem.kt
expect fun getTempDir(): String

// androidMain
actual fun getTempDir(): String = context.cacheDir.absolutePath

// iosMain
actual fun getTempDir(): String = NSTemporaryDirectory()
```

### BackgroundSync

```kotlin
// commonMain/platform/BackgroundSync.kt
expect fun scheduleSync()

// androidMain
actual fun scheduleSync() {
    val request = OneTimeWorkRequestBuilder<SyncWorker>()
        .setConstraints(Constraints(NetworkType.CONNECTED))
        .build()
    WorkManager.getInstance(context).enqueueUniqueWork(
        "pending_sync", ExistingWorkPolicy.KEEP, request)
}

// iosMain
actual fun scheduleSync() {
    val request = BGProcessingTaskRequest("com.anjali.sync")
    request.requiresNetworkConnectivity = true
    BGTaskScheduler.shared.submit(request, null)
}
```

---

## 5. State Management (ViewModel + StateFlow)

ViewModels live in `shared/commonMain/presentation/`. Both platforms consume them identically in terms of logic — only the observation syntax differs.

```kotlin
// shared — ReportViewModel.kt
data class ReportUiState(
    val reportType: ReportType = ReportType.RECEIVE,
    val diamondId: String = "",
    val recordingState: RecordingState = RecordingState.IDLE,
    val submissionState: SubmissionState = SubmissionState.IDLE,
    val transcriptOriginal: String = "",
    val transcriptEnglish: String = "",
    val severity: String? = null,
    val chainAttribution: String? = null,
    val error: String? = null,
)

class ReportViewModel(
    private val submitReportUseCase: SubmitReportUseCase,
    private val audioRecorder: AudioRecorder,
) : ViewModel() {
    private val _uiState = MutableStateFlow(ReportUiState())
    val uiState: StateFlow<ReportUiState> = _uiState.asStateFlow()

    fun setReportType(type: ReportType) { _uiState.update { it.copy(reportType = type) } }
    fun setDiamondId(id: String)        { _uiState.update { it.copy(diamondId = id) } }

    fun toggleRecording() {
        if (audioRecorder.isRecording.value) stopRecording() else startRecording()
    }

    private fun startRecording() {
        val path = "${getTempDir()}/rec_${Clock.System.now().epochSeconds}.m4a"
        audioRecorder.start(path)
        _uiState.update { it.copy(recordingState = RecordingState.RECORDING) }
    }

    private fun stopRecording() {
        audioRecorder.stop()
        _uiState.update { it.copy(recordingState = RecordingState.RECORDED) }
    }

    fun submit() = viewModelScope.launch {
        submitReportUseCase(
            diamondId   = _uiState.value.diamondId,
            reportType  = _uiState.value.reportType,
            audioPath   = audioRecorder.lastFilePath,
            onProgress  = { state -> _uiState.update { it.copy(submissionState = state) } },
        ).onSuccess { result ->
            _uiState.update { it.copy(
                submissionState    = SubmissionState.SUCCESS,
                transcriptOriginal = result.transcriptOriginal,
                transcriptEnglish  = result.transcriptEnglish,
                severity           = result.severity,
                chainAttribution   = result.chainAttribution,
            )}
        }.onFailure { err ->
            _uiState.update { it.copy(submissionState = SubmissionState.ERROR, error = err.message) }
        }
    }
}
```

**Android — observe in Compose:**
```kotlin
@Composable
fun ReportScreen(vm: ReportViewModel = koinViewModel()) {
    val state by vm.uiState.collectAsStateWithLifecycle()
    // use state.recordingState, state.submissionState, etc.
}
```

**iOS — observe in SwiftUI via SKIE:**
```swift
struct ReportView: View {
    @StateObject var vm = ReportViewModel(...)

    var body: some View {
        // SKIE converts StateFlow<ReportUiState> → Swift AsyncStream automatically
        // Access vm.uiState as a published property
    }
}
```

---

## 6. Networking — Ktor Client

```kotlin
// shared/data/network/ApiClient.kt
fun createHttpClient(engine: HttpClientEngine): HttpClient = HttpClient(engine) {
    install(ContentNegotiation) { json(Json { ignoreUnknownKeys = true }) }
    install(Logging) { level = LogLevel.BODY }
    install(Auth) {
        bearer {
            loadTokens {
                val access  = secureStorage.getString("access_token")
                val refresh = secureStorage.getString("refresh_token")
                if (access != null && refresh != null) BearerTokens(access, refresh) else null
            }
            refreshTokens {
                val response = client.post("/auth/refresh") {
                    markAsRefreshTokenRequest()
                    setBody(RefreshRequest(secureStorage.getString("refresh_token") ?: ""))
                }
                val tokens = response.body<TokenResponse>()
                secureStorage.putString("access_token",  tokens.accessToken)
                secureStorage.putString("refresh_token", tokens.refreshToken)
                BearerTokens(tokens.accessToken, tokens.refreshToken)
            }
        }
    }
    defaultRequest { url("https://api.anjalidiamonds.com") }
}
```

**API response wrapper:**
```kotlin
@Serializable
data class ApiResponse<T>(
    val data: T? = null,
    val error: String? = null,
)

// Error handling mapped to UI
suspend fun <T> safeApiCall(block: suspend () -> T): Result<T> =
    runCatching { block() }
        .recoverCatching { e ->
            when (e) {
                is ClientRequestException  -> throw AppError.fromHttp(e.response.status.value)
                is IOException             -> throw AppError.NoNetwork
                else                       -> throw e
            }
        }
```

---

## 7. Local Database — SQLDelight

### Schema files

```sql
-- shared/src/commonMain/sqldelight/com/anjali/PendingReport.sq
CREATE TABLE PendingReport (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  worker_id   TEXT    NOT NULL,
  report_type TEXT    NOT NULL,
  diamond_id  TEXT    NOT NULL,
  audio_path  TEXT    NOT NULL,
  created_at  INTEGER NOT NULL,
  sync_status TEXT    NOT NULL DEFAULT 'pending',
  retry_count INTEGER NOT NULL DEFAULT 0
);

selectAll:
SELECT * FROM PendingReport ORDER BY created_at ASC;

insertPending:
INSERT INTO PendingReport(worker_id, report_type, diamond_id, audio_path, created_at)
VALUES (?, ?, ?, ?, ?);

updateStatus:
UPDATE PendingReport SET sync_status = ?, retry_count = ? WHERE id = ?;

deleteById:
DELETE FROM PendingReport WHERE id = ?;

countByStatus:
SELECT COUNT(*) FROM PendingReport WHERE sync_status = ?;
```

### Database factory (expect/actual)

```kotlin
// commonMain
expect fun createDatabase(): DiamondDatabase

// androidMain
actual fun createDatabase(): DiamondDatabase =
    DiamondDatabase(AndroidSqliteDriver(DiamondDatabase.Schema, context, "diamond.db"))

// iosMain
actual fun createDatabase(): DiamondDatabase =
    DiamondDatabase(NativeSqliteDriver(DiamondDatabase.Schema, "diamond.db"))
```

---

## 8. Dependency Injection — Koin

```kotlin
// shared/di/SharedModule.kt
val sharedModule = module {
    single { createHttpClient(get()) }
    single { createDatabase() }
    single { SecureStorage() }
    single { AudioRecorder() }

    // Repositories
    single { ReportRepository(get(), get()) }
    single { UserRepository(get()) }
    single { ChatRepository(get()) }

    // Use cases
    factory { SubmitReportUseCase(get(), get()) }
    factory { GetDashboardUseCase(get()) }
    factory { SyncPendingUseCase(get(), get()) }

    // ViewModels
    viewModel { ReportViewModel(get(), get()) }
    viewModel { HistoryViewModel(get()) }
    viewModel { DashboardViewModel(get()) }
    viewModel { UsersViewModel(get()) }
    viewModel { ChatViewModel(get()) }
    viewModel { (userId: Int) -> UserDetailViewModel(get(), userId) }
}

// Shared entry point called by both platforms
fun initKoin() = startKoin { modules(sharedModule) }
```

```kotlin
// androidMain — DiamondApplication.kt
class DiamondApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        initKoin()
    }
}
```

```swift
// iosApp — DiamondApp.swift
@main struct DiamondApp: App {
    init() { SharedModuleKt.doInitKoin() }
    var body: some Scene { WindowGroup { ContentView() } }
}
```

---

## 9. Navigation

### Android — Navigation Compose

```kotlin
// androidApp/navigation/AppNavHost.kt
sealed class Route(val path: String) {
    object Login              : Route("login")
    object WorkerReport       : Route("worker/report")
    object WorkerHistory      : Route("worker/history")
    object WorkerProfile      : Route("worker/profile")
    object Dashboard          : Route("dashboard")
    object ReportDetails      : Route("dashboard/{processId}?period={period}")
    object Chatbot            : Route("chatbot")
    object ManagementProfile  : Route("management/profile")
    object Users              : Route("admin/users")
    object CreateUser         : Route("admin/users/create")
    object UserDetail         : Route("admin/users/{userId}")
    object Settings           : Route("admin/settings")
    object AdminProfile       : Route("admin/profile")
}

@Composable
fun AppNavHost(navController: NavHostController, role: String) {
    NavHost(navController, startDestination = startRouteForRole(role)) {
        composable(Route.Login.path)          { LoginScreen(navController) }
        composable(Route.WorkerReport.path)   { ReportScreen(navController) }
        // ... etc
        composable(Route.ReportDetails.path,
            arguments = listOf(navArgument("processId") { type = NavType.IntType })
        ) { backStackEntry ->
            ReportDetailsScreen(
                processId = backStackEntry.arguments!!.getInt("processId"),
                navController = navController,
            )
        }
    }
}
```

**Bottom nav scaffold:**
```kotlin
@Composable
fun AppScaffold(role: UserRole, content: @Composable () -> Unit) {
    Scaffold(
        bottomBar = {
            NavigationBar(containerColor = Color.White) {
                bottomNavItemsForRole(role).forEach { item ->
                    NavigationBarItem(
                        selected = currentRoute == item.route,
                        onClick  = { navController.navigate(item.route) },
                        icon     = { Icon(item.icon, contentDescription = item.label) },
                        colors   = NavigationBarItemDefaults.colors(
                            selectedIconColor   = AppColors.Primary,
                            unselectedIconColor = AppColors.TextSecondary,
                            indicatorColor      = Color.Transparent,
                        )
                    )
                }
            }
        }
    ) { content() }
}
```

### iOS — SwiftUI NavigationStack

```swift
// iosApp/Navigation/AppRouter.swift
enum Route: Hashable {
    case workerReport, workerHistory, workerProfile
    case dashboard, reportDetails(processId: Int, period: String)
    case chatbot
    case users, createUser, userDetail(userId: Int)
    case profile
}

struct RootView: View {
    @State private var path = NavigationPath()
    let role: UserRole

    var body: some View {
        NavigationStack(path: $path) {
            homeViewForRole(role)
                .navigationDestination(for: Route.self) { route in
                    switch route {
                    case .workerHistory:          HistoryView()
                    case .dashboard:              DashboardView()
                    case .reportDetails(let id, let period):
                                                  ReportDetailsView(processId: id, period: period)
                    case .userDetail(let id):     UserDetailView(userId: id)
                    default:                      EmptyView()
                    }
                }
        }
    }
}
```

---

## 10. Design Tokens — Android (Compose)

```kotlin
// androidApp/theme/AppColors.kt
object AppColors {
    val Primary        = Color(0xFFE8491B)
    val PrimaryDark    = Color(0xFF0F1A2E)
    val LoginBg        = Color(0xFF3B0A0A)
    val Background     = Color(0xFFF5F5F5)
    val Surface        = Color(0xFFFFFFFF)
    val InputFill      = Color(0xFFF0F0F0)
    val Severe         = Color(0xFFE8491B)
    val Moderate       = Color(0xFFFFC107)
    val Low            = Color(0xFF4CAF50)
    val ActiveGreen    = Color(0xFF4CAF50)
    val InactiveRed    = Color(0xFFE53935)
    val TextPrimary    = Color(0xFF1A1A1A)
    val TextSecondary  = Color(0xFF6B7280)
    val TextHint       = Color(0xFF9CA3AF)
    val ReceiveTagBg   = Color(0xFFEBF5FF)
    val ReceiveTagFg   = Color(0xFF1D72E8)
    val ProblemTagBg   = Color(0xFFFFF0EB)
    val ProblemTagFg   = Color(0xFFE8491B)
}

// androidApp/theme/AppTheme.kt
val AppShapes = Shapes(
    small  = RoundedCornerShape(8.dp),
    medium = RoundedCornerShape(12.dp),
    large  = RoundedCornerShape(16.dp),
)
// Pill-shaped buttons: shape = CircleShape (50% radius)

// androidApp/theme/AppTypography.kt
val AppTypography = Typography(
    titleLarge   = TextStyle(fontSize = 18.sp, fontWeight = FontWeight.Bold),
    bodyLarge    = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Normal),
    bodyMedium   = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Normal),
    labelSmall   = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold,
                             letterSpacing = 0.8.sp),
)
```

---

## 11. Screen Specs — Android (Compose)

### 11.1 Login Screen

```kotlin
@Composable
fun LoginScreen(navController: NavController, vm: AuthViewModel = koinViewModel()) {
    val state by vm.uiState.collectAsStateWithLifecycle()

    Box(Modifier.fillMaxSize().background(AppColors.LoginBg)) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text("Anjali Diamonds", color = Color.White, style = AppTypography.titleLarge)
            Text("Sign in to your account", color = AppColors.TextSecondary)

            Card(shape = RoundedCornerShape(20.dp)) {
                Column(Modifier.padding(24.dp)) {
                    LabeledTextField("USERNAME", vm.username, { vm.username = it })
                    LabeledTextField("PASSWORD", vm.password, { vm.password = it },
                        visualTransformation = PasswordVisualTransformation())
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Checkbox(state.stayLoggedIn, { vm.toggleStayLoggedIn() })
                        Text("Stay logged in")
                    }
                    Button(
                        onClick = { vm.login() },
                        modifier = Modifier.fillMaxWidth().height(52.dp),
                        shape = CircleShape,
                        colors = ButtonDefaults.buttonColors(containerColor = AppColors.PrimaryDark),
                    ) {
                        if (state.isLoading) CircularProgressIndicator(color = Color.White, size = 20.dp)
                        else Text("Sign In", style = AppTypography.bodyLarge)
                    }
                    if (state.error != null)
                        Text(state.error!!, color = AppColors.InactiveRed, fontSize = 13.sp)
                }
            }
        }
    }
}
```

### 11.2 Worker Report Screen

**State enums (shared):**
```kotlin
enum class ReportType    { RECEIVE, PROBLEM }
enum class RecordingState{ IDLE, RECORDING, RECORDED }
enum class SubmissionState { IDLE, UPLOADING, TRANSCRIBING, TRANSLATING, ANALYSING, SUCCESS, ERROR, QUEUED }
```

**Composable structure:**
```kotlin
@Composable
fun ReportScreen(vm: ReportViewModel = koinViewModel()) {
    val state by vm.uiState.collectAsStateWithLifecycle()

    Column(Modifier.fillMaxSize().background(AppColors.Background)) {
        ReportTypeTabBar(state.reportType, vm::setReportType)
        if (!state.hintDismissed)
            HintBanner(hintTextFor(state.reportType)) { vm.dismissHint() }
        DiamondIdField(state.diamondId, vm::setDiamondId)
        Box(Modifier.weight(1f), contentAlignment = Alignment.Center) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                MicButton(state.recordingState) { vm.toggleRecording() }
                if (state.recordingState != RecordingState.IDLE)
                    WaveformDisplay(...)
                if (state.transcriptOriginal.isNotEmpty())
                    TranscriptBox(state.transcriptOriginal)
            }
        }
        SubmitButton(state) { vm.submit() }
    }
}
```

**MicButton — pulse animation while recording:**
```kotlin
@Composable
fun MicButton(state: RecordingState, onClick: () -> Unit) {
    val infiniteTransition = rememberInfiniteTransition()
    val pulseAlpha by infiniteTransition.animateFloat(
        0f, 0.4f, infiniteRepeatable(tween(800), RepeatMode.Reverse)
    )
    Box(contentAlignment = Alignment.Center) {
        if (state == RecordingState.RECORDING)
            Box(Modifier.size(100.dp).background(
                AppColors.Primary.copy(alpha = pulseAlpha), CircleShape))
        Box(
            Modifier.size(80.dp).background(AppColors.Primary, CircleShape).clickable(onClick = onClick),
            contentAlignment = Alignment.Center,
        ) { Icon(Icons.Default.Mic, tint = Color.White, modifier = Modifier.size(36.dp)) }
    }
}
```

**SubmitButton — inline progress text:**
```kotlin
@Composable
fun SubmitButton(state: ReportUiState, onSubmit: () -> Unit) {
    val label = when (state.submissionState) {
        SubmissionState.UPLOADING     -> "Uploading…"
        SubmissionState.TRANSCRIBING  -> "Transcribing…"
        SubmissionState.TRANSLATING   -> "Translating…"
        SubmissionState.ANALYSING     -> "Analysing…"
        else                          -> "Submit"
    }
    val enabled = state.diamondId.isNotBlank()
               && state.recordingState == RecordingState.RECORDED
               && state.submissionState == SubmissionState.IDLE
    Button(
        onClick = onSubmit, enabled = enabled,
        modifier = Modifier.fillMaxWidth().padding(16.dp).height(52.dp),
        shape = CircleShape,
        colors = ButtonDefaults.buttonColors(containerColor = AppColors.Primary),
    ) { Text(label, color = Color.White) }
}
```

### 11.3 Dashboard Screen

**Bar chart using Vico:**
```kotlin
@Composable
fun DefectRateChart(data: List<ProcessDefectCount>, onProcessTap: (Int) -> Unit) {
    // Vico ColumnChart with horizontal scroll disabled
    // Each entry = one process, orange bars
    // Tap on entry → onProcessTap(processId)
    val model = CartesianChartModelProducer.build {
        columnSeries { series(data.map { it.count.toFloat() }) }
    }
    CartesianChartHost(
        chart = rememberCartesianChart(
            rememberColumnCartesianLayer(
                ColumnCartesianLayer.ColumnProvider.series(
                    rememberLineComponent(color = AppColors.Primary, thickness = 12.dp)
                )
            ),
            startAxis = rememberStartAxis(/* process names */),
        ),
        modelProducer = model,
    )
}
```

**Auto-refresh:**
```kotlin
// In DashboardViewModel
init {
    viewModelScope.launch {
        while (true) {
            loadDashboard()
            delay(10_000)
        }
    }
}
```

### 11.4 Shared Composables

**SeverityBadge:**
```kotlin
@Composable
fun SeverityBadge(severity: String) {
    val (bg, fg) = when (severity) {
        "Severe"   -> AppColors.Severe.copy(0.12f)   to AppColors.Severe
        "Moderate" -> AppColors.Moderate.copy(0.15f) to AppColors.Moderate
        else       -> AppColors.Low.copy(0.12f)      to AppColors.Low
    }
    Row(
        Modifier.background(bg, CircleShape).border(0.5.dp, fg, CircleShape).padding(horizontal=8.dp, vertical=3.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(Modifier.size(6.dp).background(fg, CircleShape))
        Spacer(Modifier.width(4.dp))
        Text(severity, color = fg, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
    }
}
```

**ReportTypeTag:**
```kotlin
@Composable
fun ReportTypeTag(type: String) {
    val isReceive = type == "receive"
    Box(
        Modifier.background(
            if (isReceive) AppColors.ReceiveTagBg else AppColors.ProblemTagBg,
            RoundedCornerShape(6.dp)
        ).padding(horizontal = 8.dp, vertical = 4.dp)
    ) {
        Text(
            text = if (isReceive) "RECEIVE" else "PROBLEM",
            color = if (isReceive) AppColors.ReceiveTagFg else AppColors.ProblemTagFg,
            fontSize = 11.sp, fontWeight = FontWeight.SemiBold,
        )
    }
}
```

**AudioPlayerRow:**
```kotlin
// Uses ExoPlayer via AndroidView (or Media3 Compose when stable)
@Composable
fun AudioPlayerRow(url: String, durationSeconds: Int) {
    val context = LocalContext.current
    val player = remember { ExoPlayer.Builder(context).build() }
    var isPlaying by remember { mutableStateOf(false) }

    DisposableEffect(url) {
        player.setMediaItem(MediaItem.fromUri(url))
        player.prepare()
        onDispose { player.release() }
    }

    Row(verticalAlignment = Alignment.CenterVertically) {
        IconButton(onClick = { if (isPlaying) player.pause() else player.play(); isPlaying = !isPlaying }) {
            Icon(
                if (isPlaying) Icons.Default.Pause else Icons.Default.PlayArrow,
                tint = Color.White,
                modifier = Modifier.background(AppColors.Primary, CircleShape).size(40.dp).padding(8.dp),
            )
        }
        WaveformBar(Modifier.weight(1f))                    // static amplitude bars
        Text(formatDuration(durationSeconds), style = AppTypography.bodyMedium)
    }
}
```

---

## 12. Screen Specs — iOS (SwiftUI)

SwiftUI screens mirror the Compose screens structurally. Key patterns:

```swift
// Observe shared ViewModel via SKIE
struct ReportView: View {
    @StateObject private var vm: ReportViewModel = KoinHelper.shared.reportViewModel()
    // SKIE converts uiState: StateFlow<ReportUiState> into a @Published-like observable

    var body: some View {
        VStack {
            ReportTypeTabBar(selected: vm.uiState.reportType) { vm.setReportType($0) }
            // ...
            MicButton(state: vm.uiState.recordingState) { vm.toggleRecording() }
        }
    }
}

// Colors defined in Assets.xcassets (match Compose values exactly)
extension Color {
    static let primary      = Color("Primary")       // #E8491B
    static let primaryDark  = Color("PrimaryDark")   // #0F1A2E
    static let loginBg      = Color("LoginBg")       // #3B0A0A
}

// Charts — SwiftUI Charts (iOS 16+)
Chart(defectData) { item in
    BarMark(x: .value("Count", item.count), y: .value("Process", item.processName))
        .foregroundStyle(Color.primary)
        .cornerRadius(6)
}
.onTapGesture { /* navigate to ReportDetailsView */ }
```

---

## 13. Audio Pipeline

```
AudioRecorder.start() [expect/actual]          → local file: getTempDir()/rec_<ts>.m4a
AudioRecorder.stop()  [expect/actual]          → returns filePath
    ↓
Ktor multipart PUT /audio/upload               → { fileUuid }
    ↓
Ktor POST /sarvam/stt { fileUuid }             → { transcriptOriginal }  [Sarvam saarika:v2]
    ↓
Ktor POST /gemini/translate { text }           → { transcriptEnglish }   [Gemini]
    ↓
Ktor POST /reports { diamondId, type, ... }    → { reportId, severity, defectType, chainAttribution }
    ↓
StateFlow update → UI re-renders (Compose / SwiftUI)

On network failure:
    → SQLDelight INSERT PendingReport
    → scheduleSync() [expect/actual — WorkManager / BGTaskScheduler]
```

---

## 14. Offline Sync Flow

```kotlin
// shared/domain/usecase/SyncPendingUseCase.kt
class SyncPendingUseCase(
    private val localDb: DiamondDatabase,
    private val api: ApiClient,
) {
    suspend operator fun invoke() {
        localDb.pendingReportQueries.selectAll().executeAsList().forEach { pending ->
            runCatching {
                // full submission pipeline (upload → STT → translate → submit)
                submitReport(pending)
                localDb.pendingReportQueries.deleteById(pending.id)
            }.onFailure {
                val newCount = pending.retry_count + 1
                val newStatus = if (newCount >= 3) "failed" else "pending"
                localDb.pendingReportQueries.updateStatus(newStatus, newCount, pending.id)
            }
        }
    }
}
```

---

## 15. Localisation

| Platform | File | Location |
|---|---|---|
| Android | `strings.xml` | `androidApp/src/main/res/values/strings.xml` (EN) `values-gu/strings.xml` (GU) `values-hi/strings.xml` (HI) |
| iOS | `Localizable.strings` | `iosApp/iosApp/en.lproj/Localizable.strings` `gu.lproj/Localizable.strings` `hi.lproj/Localizable.strings` |

**Language switching at runtime:**

```kotlin
// Android — restart Activity with new locale config
fun applyLocale(context: Context, languageCode: String) {
    val locale = Locale(languageCode)
    val config = context.resources.configuration
    config.setLocale(locale)
    context.createConfigurationContext(config)
    (context as Activity).recreate()
}
```

```swift
// iOS — update environment locale
@AppStorage("language") var language = "en"
ContentView().environment(\.locale, Locale(identifier: language))
```

---

## 16. Permissions

| Permission | Android | iOS |
|---|---|---|
| Microphone | `RECORD_AUDIO` in manifest + runtime | `NSMicrophoneUsageDescription` in Info.plist |
| Camera (QR) | `CAMERA` in manifest + runtime | `NSCameraUsageDescription` in Info.plist |
| Notifications | `POST_NOTIFICATIONS` (API 33+) + runtime | `UNUserNotificationCenter.requestAuthorization` |

---

## 17. Project Setup — Step by Step

1. **Create KMP project** at [kmp.jetbrains.com](https://kmp.jetbrains.com)
   - Targets: Android + iOS
   - Android UI: Jetpack Compose ✓
   - iOS UI: SwiftUI ✓
   - Uncheck "Share UI" (no Compose Multiplatform)

2. **Add SKIE Gradle plugin** to `shared/build.gradle.kts` — enables clean Swift async/await for StateFlow

3. **Configure SQLDelight plugin** — add `sqldelight { databases { create("DiamondDatabase") { ... } } }` block, write `.sq` files, sync to generate type-safe Kotlin DAOs

4. **Set up Koin** — write `SharedModule.kt`, call `initKoin()` from `DiamondApplication.kt` (Android) and `DiamondApp.swift` (iOS)

5. **Implement expect/actual** — `AudioRecorder`, `SecureStorage`, `FileSystem`, `BackgroundSync` for both `androidMain` and `iosMain`

6. **Build shared layer** in order:
   - DTOs + serialization models
   - Ktor `ApiClient` with JWT interceptor
   - SQLDelight DAOs
   - Repository implementations
   - Use cases
   - ViewModels + UiState data classes

7. **Build Android UI** screen by screen using Jetpack Compose, consuming shared ViewModels via `koinViewModel()`

8. **Build iOS UI** screen by screen using SwiftUI, consuming shared ViewModels via SKIE-generated Swift async streams

9. **Wire navigation** separately: `AppNavHost.kt` (Android), `AppRouter.swift` (iOS)

10. **Add `strings.xml` + `Localizable.strings`** for EN/GU/HI on both platforms

---

## 18. Testing Strategy

| Layer | Tool | What |
|---|---|---|
| Shared unit | `kotlin.test` | ViewModel logic, use cases, API response parsing, emp code generation, fault rate |
| Shared DB | SQLDelight in-memory driver | Offline queue insert/update/delete cycles |
| Android UI | Compose Test (`composeTestRule`) | ReportScreen tab toggle, MicButton states, SeverityBadge rendering |
| Android integration | `MockEngine` (Ktor) | Full submission flow (mock Sarvam + Gemini) |
| iOS unit | XCTest | ViewModel state via SKIE async, SecureStorage Keychain |
| Android snapshot | Paparazzi | LoginScreen, Dashboard KPI row, ReportCard |
