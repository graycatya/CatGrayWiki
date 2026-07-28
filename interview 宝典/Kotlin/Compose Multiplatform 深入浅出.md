# Compose Multiplatform 深入浅出

> 一份深入浅出的 Compose Multiplatform (CMP) 学习指南，从核心概念到与 Jetpack Compose 的区别，帮你系统掌握跨平台声明式 UI 开发。

---

## 目录

1. [什么是 Compose Multiplatform？](#一什么是-compose-multiplatform)
2. [Compose Multiplatform vs Jetpack Compose](#二compose-multiplatform-vs-jetpack-compose)
3. [核心概念：共享 UI 层](#三核心概念共享-ui-层)
4. [项目结构详解](#四项目结构详解)
5. [expect/actual 在 UI 中的使用](#五expectactual-在-ui-中的使用)
6. [平台差异处理](#六平台差异处理)
7. [资源与依赖管理](#七资源与依赖管理)
8. [导航方案](#八导航方案)
9. [项目实战：跨平台 App](#九项目实战跨平台-app)
10. [从 Jetpack Compose 迁移到 CMP](#十从-jetpack-compose-迁移到-cmp)
11. [常见问题与最佳实践](#十一常见问题与最佳实践)

---

## 一、什么是 Compose Multiplatform？

**Compose Multiplatform (CMP)** 是 JetBrains 推出的跨平台声明式 UI 框架，基于 Jetpack Compose 的 runtime 核心，将 Compose 能力扩展到 Android 之外的多平台。

### CMP 的支持矩阵

| 平台 | 状态 | 备注 |
|------|------|------|
| Android | ✅ 稳定 | 复用 Jetpack Compose |
| iOS | ✅ 稳定 | 自绘引擎渲染 |
| Desktop (Windows/macOS/Linux) | ✅ 稳定 | 自绘引擎渲染 |
| Web (Kotlin/Wasm) | 🧪 Beta | 通过 Canvas/Skia 渲染 |

### CMP 的本质

```
┌──────────────────────────────────────────────────────┐
│              Compose Multiplatform                    │
│                                                      │
│   ┌────────────────────────────────────────────┐     │
│   │        Compose Runtime (跨平台核心)         │     │
│   │   - 组合 (Composition)                     │     │
│   │   - 重组 (Recomposition)                   │     │
│   │   - 状态管理 (Snapshot State System)       │     │
│   │   - 副作用 API (Effects)                   │     │
│   └────────────────────────────────────────────┘     │
│                       │                              │
│   ┌───────────────────┼───────────────────┐          │
│   │        ┌──────────┴──────────┐        │          │
│   │        │  commonMain (共享)  │        │          │
│   │        │  Compose UI 代码     │        │          │
│   │        └──────────┬──────────┘        │          │
│   │                   │                   │          │
│   │   ┌───────┐  ┌────┴────┐  ┌───────┐   │          │
│   │   │Android│  │   iOS   │  │Desktop│   │          │
│   │   │ Canvas│  │ Canvas  │  │ Canvas│   │          │
│   │   │ (View)│  │(Skia)   │  │(Skia) │   │          │
│   │   └───────┘  └─────────┘  └───────┘   │          │
│   └───────────────────────────────────────┘          │
└──────────────────────────────────────────────────────┘
```

---

## 二、Compose Multiplatform vs Jetpack Compose

### 一句话总结差异

> **Jetpack Compose** = Android 原生 UI 框架（Google 维护，仅 Android）
> **Compose Multiplatform** = 基于 Jetpack Compose Runtime 的跨平台 UI 框架（JetBrains 维护，Android/iOS/Desktop/Web）

### 核心差异对比

| 维度 | Jetpack Compose | Compose Multiplatform |
|------|----------------|----------------------|
| **维护方** | Google | JetBrains |
| **目标平台** | Android only | Android / iOS / Desktop / Web |
| **版本发布** | 跟随 Android Jetpack | 独立发布节奏（版本号字母 + 数字） |
| **渲染引擎** | Android Canvas（Skia） | Android: View Canvas / 其他: Skiko (Skia 封装) |
| **命名空间** | `androidx.compose.*` | `org.jetbrains.compose.*`（Android 端重定向到 `androidx.compose.*`） |
| **Navigation** | `androidx.navigation:navigation-compose` | 需第三方方案（Voyager/Decompose） |
| **资源管理** | `R.drawable.*` / `R.string.*` | `compose.resources` 多平台资源系统 |
| **Material 版本** | Material3（Google 正版） | Material3（JetBrains 移植实现） |
| **互操作性** | 与 Android View 双向桥接 | 仅 Android 端支持 View 互操作 |
| **生命周期感知** | `LifecycleOwner` / `collectAsStateWithLifecycle()` | 仅 Android 端可用 |
| **Hilt 集成** | `@HiltViewModel` 原生支持 | 仅 Android 端可用 |

### 架构对比

```
Jetpack Compose 架构：
┌──────────────────────────────┐
│  Jetpack Compose (androidx)  │
├──────────────────────────────┤
│  Compose UI (Android Canvas) │
├──────────────────────────────┤
│  Compose Runtime             │
├──────────────────────────────┤
│  Android Framework           │
└──────────────────────────────┘
     支持的平台：仅 Android


Compose Multiplatform 架构：
┌──────────────────────────────────────┐
│  Compose Multiplatform (jetbrains)   │
├──────────┬──────────┬───────────────┤
│  Android │   iOS    │    Desktop    │
│ (Canvas) │ (Skiko) │   (Skiko)     │
├──────────┴──────────┴───────────────┤
│        Compose Runtime              │
├─────────────────────────────────────┤
│  Kotlin Multiplatform               │
├─────────────────────────────────────┤
│  Android │  iOS   │  Desktop  │ Web │
└─────────────────────────────────────┘
     支持的平台：全部
```

### 代码差异示例

```kotlin
// ===== Jetpack Compose =====
// 命名空间：androidx.compose.*
import androidx.compose.material3.Text
import androidx.compose.ui.Modifier

// 资源：使用 Android 原生 R 系统
Image(
    painter = painterResource(id = R.drawable.logo),
    contentDescription = null
)

// 生命周期感知
val state by viewModel.uiState.collectAsStateWithLifecycle()

// Navigation 原生支持
NavHost(navController, startDestination = "home") { ... }


// ===== Compose Multiplatform =====
// 命名空间：org.jetbrains.compose.*
// （Android 端自动映射到 androidx.compose.*）
import org.jetbrains.compose.material3.Text
import androidx.compose.ui.Modifier  // Modifier 等基础组件仍然是 androidx

// 资源：使用 compose.resources（跨平台）
import org.jetbrains.compose.resources.painterResource
import cmpapp.generated.resources.Res
import cmpapp.generated.resources.logo

Image(
    painter = painterResource(Res.drawable.logo),
    contentDescription = null
)

// 需第三方导航（如 Voyager）
@Composable
fun App() {
    Navigator(HomeScreen())
}

class HomeScreen : Screen {
    @Composable
    override fun Content() { ... }
}
```

### 什么时候用哪个？

```
选择 Jetpack Compose：
  ✅ 纯 Android 项目
  ✅ 需要最新的 Google 特性（如 Predictive Back Gesture）
  ✅ 深度依赖 Android 特有库（Hilt、LiveData、Room）
  ✅ 不需要跨平台

选择 Compose Multiplatform：
  ✅ 有跨平台需求（Android + iOS + Desktop）
  ✅ 已在用 KMP 共享业务逻辑，想进一步共享 UI
  ✅ 新项目希望一套 UI 代码多端运行
  ✅ 内部工具/管理后台（Desktop 端天然优势）
```

---

## 三、核心概念：共享 UI 层

### CMP 的共享哲学

> **Write once, render everywhere. 但保留平台差异处理能力。**

CMP 不止能共享 UI，还允许你在需要时做平台差异化处理：

```
┌────────────────────────────────────────┐
│          commonMain (共享 90%+)        │
│                                        │
│  @Composable                           │
│  fun App() {                           │
│      MaterialTheme {                   │
│          Column {                      │
│              TitleBar()         ← 共享  │
│              ContentArea()      ← 共享  │
│              PlatformBottomBar() ← 差异 │
│          }                             │
│      }                                 │
│  }                                     │
└────────┬──────────┬──────────┬─────────┘
         │          │          │
    ┌────▼───┐ ┌───▼────┐ ┌───▼────┐
    │Android │ │  iOS   │ │Desktop │
    │ expect │ │ actual │ │ actual │
    │BottomBar│BottomBar│BottomBar│
    └────────┘ └────────┘ └────────┘
```

### 可共享的 UI 内容

```
✅ 完全可共享：
  - Compose 布局系统（Column/Row/Box/LazyColumn）
  - Modifier 链（padding, background, clip 等）
  - Material3 组件（Button, Card, TextField 等）
  - 自定义 Composable 函数
  - 动画 API（animate*AsState, AnimatedVisibility 等）
  - 主题系统（MaterialTheme, 自定义 Color/Shape/Typography）
  - 手势系统（clickable, draggable, transformable 等）
  - Canvas 自定义绘制
  - 文本输入与编辑
  - Dialog / BottomSheet 等弹窗
```

### 不可共享或需差异处理的内容

```
⚠️ 需要平台差异处理：
  - Navigation（需第三方库或 expect/actual）
  - 状态栏/导航栏样式
  - 键盘交互行为
  - 返回手势（iOS 侧滑、桌面无返回键）
  - 文件选择器
  - 相机/相册调用
  - 推送通知 UI
  - 权限请求对话框
  - 生命周期感知（仅 Android 有 Lifecycle）
```

---

## 四、项目结构详解

### 典型 CMP 项目结构

```
MyCMPProject/
├── composeApp/                          # Compose 应用模块（共享 UI）
│   ├── build.gradle.kts                # Gradle 构建脚本
│   └── src/
│       ├── commonMain/                 # 全平台共享 UI + 逻辑
│       │   ├── composeResources/       # 多平台资源目录
│       │   │   ├── drawable/           # 图片资源
│       │   │   ├── values/             # 字符串
│       │   │   └── font/               # 字体
│       │   └── kotlin/
│       │       └── com/example/app/
│       │           ├── App.kt          # 全局入口 @Composable
│       │           ├── theme/
│       │           │   └── Theme.kt    # 共享主题
│       │           ├── ui/
│       │           │   ├── HomeScreen.kt
│       │           │   ├── DetailScreen.kt
│       │           │   └── components/
│       │           │       └── SharedCard.kt
│       │           └── platform/
│       │               └── Platform.kt # expect 声明
│       ├── androidMain/
│       │   ├── AndroidManifest.xml
│       │   └── kotlin/
│       │       ├── MainActivity.kt     # Android 入口 Activity
│       │       └── platform/
│       │           └── Platform.android.kt
│       ├── iosMain/
│       │   └── kotlin/
│       │       ├── MainViewController.kt # iOS 入口 ViewController
│       │       └── platform/
│       │           └── Platform.ios.kt
│       └── desktopMain/
│           └── kotlin/
│               ├── Main.kt             # Desktop 入口 main()
│               └── platform/
│                   └── Platform.desktop.kt
├── iosApp/                              # iOS Xcode 项目（壳工程）
│   └── iosApp/
│       ├── ContentView.swift            # SwiftUI 壳
│       └── iOSApp.swift
├── build.gradle.kts
└── settings.gradle.kts
```

### Gradle 配置详解

```kotlin
// composeApp/build.gradle.kts
plugins {
    kotlin("multiplatform")
    id("org.jetbrains.compose")          // Compose Multiplatform 插件
    id("org.jetbrains.kotlin.plugin.compose") // Compose 编译器插件
    id("com.android.application")        // Android 应用插件
}

kotlin {
    // 目标平台声明
    androidTarget {
        compilations.all {
            kotlinOptions {
                jvmTarget = "17"
            }
        }
    }
    
    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach {
        it.binaries.framework {
            baseName = "ComposeApp"     // 导出给 iOS 的 framework 名
            isStatic = true
        }
    }
    
    // Desktop 目标（JVM）
    jvm("desktop")

    sourceSets {
        commonMain.dependencies {
            implementation(compose.runtime)           // Compose Runtime
            implementation(compose.foundation)        // 基础布局/手势
            implementation(compose.material3)         // Material3 组件
            implementation(compose.ui)                // UI 核心
            implementation(compose.components.resources) // 资源管理
            implementation("org.jetbrains.androidx.lifecycle:lifecycle-viewmodel-compose:2.8.0") // ViewModel
        }

        androidMain.dependencies {
            implementation("androidx.activity:activity-compose:1.9.0")
            implementation("androidx.core:core-ktx:1.13.0")
            // Android 上 compose.* 依赖自动映射到 androidx.compose.*
        }

        // Desktop 需要额外指定运行环境
        val desktopMain by getting {
            dependencies {
                implementation(compose.desktop.currentOs)
            }
        }
    }
}
```

### 各平台入口代码

```kotlin
// ===== commonMain/App.kt =====
// 这是所有平台共享的 UI 入口
@Composable
fun App() {
    AppTheme {
        val navigator = rememberNavigator()
        AppNavHost(navigator)
    }
}

// ===== androidMain/MainActivity.kt =====
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            App()  // 直接调用 shared UI
        }
    }
}

// ===== iosMain/MainViewController.kt =====
fun MainViewController() = ComposeUIViewController {
    App()  // 包装为 UIViewController
}

// ===== desktopMain/Main.kt =====
fun main() = application {
    Window(
        onCloseRequest = ::exitApplication,
        title = "My CMP App"
    ) {
        App()  // 在 Window 中渲染
    }
}
```

---

## 五、expect/actual 在 UI 中的使用

### 平台差异化 UI 组件

```kotlin
// ===== commonMain/PlatformComponents.kt =====
// 声明期望的平台特定 UI 组件
@Composable
expect fun PlatformBottomBar(
    currentRoute: String,
    onNavigate: (String) -> Unit
)

// 在主界面中使用
@Composable
fun MainScreen() {
    var currentRoute by remember { mutableStateOf("home") }
    
    Scaffold(
        bottomBar = {
            PlatformBottomBar(
                currentRoute = currentRoute,
                onNavigate = { currentRoute = it }
            )
        }
    ) { padding ->
        // 内容区域
        Content(modifier = Modifier.padding(padding))
    }
}

// ===== androidMain/PlatformComponents.android.kt =====
@Composable
actual fun PlatformBottomBar(
    currentRoute: String,
    onNavigate: (String) -> Unit
) {
    NavigationBar {
        NavigationBarItem(
            icon = { Icon(Icons.Default.Home, null) },
            label = { Text("Home") },
            selected = currentRoute == "home",
            onClick = { onNavigate("home") }
        )
        NavigationBarItem(
            icon = { Icon(Icons.Default.Settings, null) },
            label = { Text("Settings") },
            selected = currentRoute == "settings",
            onClick = { onNavigate("settings") }
        )
    }
}

// ===== iosMain/PlatformComponents.ios.kt =====
@Composable
actual fun PlatformBottomBar(
    currentRoute: String,
    onNavigate: (String) -> Unit
) {
    // iOS 风格底部导航（使用 Compose 模拟 iOS 外观）
    Surface(
        color = MaterialTheme.colorScheme.surface,
        tonalElevation = 3.dp,
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 32.dp, vertical = 8.dp)
                .safeContentPadding(),  // 避开底部安全区
            horizontalArrangement = Arrangement.SpaceAround
        ) {
            PlatformTabItem("Home", "home", currentRoute, onNavigate)
            PlatformTabItem("Settings", "settings", currentRoute, onNavigate)
        }
    }
}
```

### 平台 API 访问

```kotlin
// ===== commonMain/PlatformUtils.kt =====
expect class PlatformContext

expect fun getPlatformName(): String

expect fun openUrl(url: String)

// ===== androidMain/PlatformUtils.android.kt =====
actual typealias PlatformContext = android.content.Context

actual fun getPlatformName(): String = "Android ${Build.VERSION.SDK_INT}"

actual fun openUrl(url: String) {
    // 通过 Context 打开浏览器
}

// ===== iosMain/PlatformUtils.ios.kt =====
actual class PlatformContext

actual fun getPlatformName(): String = 
    "iOS ${UIDevice.currentDevice.systemVersion}"

actual fun openUrl(url: String) {
    val nsUrl = NSURL.URLWithString(url) ?: return
    UIApplication.sharedApplication.openURL(nsUrl)
}
```

---

## 六、平台差异处理

### 安全区域（Safe Area）

```kotlin
// commonMain — 通用安全区域处理
@Composable
fun Modifier.safeContentPadding(): Modifier = this

// iosMain — iOS 需要避开刘海和底部指示条
@Composable
actual fun Modifier.safeContentPadding(): Modifier = this.then(
    WindowInsets.safeContent.asPaddingValues().let { padding ->
        this.padding(padding)
    }
)
```

### 键盘行为差异

```kotlin
@Composable
fun ChatScreen() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .imePadding()  // Android: 键盘弹起时上推内容
            .navigationBarsPadding()
    ) {
        LazyColumn(
            modifier = Modifier.weight(1f)
        ) {
            items(messages) { msg -> MessageBubble(msg) }
        }
        
        MessageInput(
            modifier = Modifier.fillMaxWidth()
        )
    }
}
```

### 窗口大小调整（Desktop 特有）

```kotlin
// desktopMain 中设置窗口
fun main() = application {
    var isMaximized by remember { mutableStateOf(false) }
    
    Window(
        onCloseRequest = ::exitApplication,
        state = rememberWindowState(
            width = 1024.dp,
            height = 768.dp
        ),
        title = "My App"
    ) {
        // Desktop 特有的窗口大小感知
        val windowSizeClass = calculateWindowSizeClass()
        
        AppAdaptiveLayout(windowSizeClass)
    }
}

@Composable
fun AppAdaptiveLayout(windowSizeClass: WindowSizeClass) {
    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> CompactLayout()
        WindowWidthSizeClass.Medium -> MediumLayout()
        WindowWidthSizeClass.Expanded -> ExpandedLayout()
    }
}
```

### 滚动行为差异

```kotlin
// Desktop: 鼠标滚轮
// iOS: 惯性滚动、橡皮筋效果
// Android: 原生滚动行为

@Composable
fun PlatformAwareScrollableList(items: List<String>) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        // Desktop 端显示滚动条
        // iOS/Android 端自动处理 fling 行为
        flingBehavior = rememberScrollbarFlingBehavior()
    ) {
        items(items, key = { it }) { item ->
            ListItem(item)
        }
    }
}
```

---

## 七、资源与依赖管理

### compose.resources 资源系统

```
composeApp/src/commonMain/composeResources/
├── drawable/                    # 图片资源
│   ├── ic_logo.xml             # Vector Drawable
│   ├── ic_logo.png             # PNG（自动多分辨率）
│   └── background.jpg
├── values/                      # 字符串资源
│   ├── strings.xml
│   └── strings-zh.xml          # 中文翻译
├── values-night/                # 暗色主题值
│   └── colors.xml
├── font/                        # 字体资源
│   ├── Inter-Regular.ttf
│   └── Inter-Bold.ttf
├── files/                       # 原始文件
│   └── privacy_policy.txt
└── raw/                         # Raw 资源
    └── sample_data.json
```

```kotlin
// 使用资源
import cmpapp.generated.resources.*

@Composable
fun ResourceDemo() {
    // 图片（自动处理多分辨率）
    Image(
        painter = painterResource(Res.drawable.ic_logo),
        contentDescription = null
    )
    
    // 字符串（自动本地化）
    Text(stringResource(Res.string.app_name))
    
    // 颜色
    Text(
        text = "Colored",
        color = colorResource(Res.color.primary)
    )
    
    // 字体
    Text(
        text = "Custom Font",
        fontFamily = FontFamily(Font(Res.font.Inter_Regular))
    )
}
```

### 依赖适配指南

```kotlin
// commonMain — 跨平台依赖
sourceSets {
    commonMain.dependencies {
        // ✅ 支持 KMP 的库，直接放在 commonMain
        implementation("io.ktor:ktor-client-core:2.3.12")
        implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.1")
        implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.3")
        
        // ✅ Compose 库，跨平台可用（JetBrains 移植版）
        implementation(compose.material3)
        implementation(compose.components.resources)
    }
    
    // androidMain — Android 专有依赖
    androidMain.dependencies {
        // ✅ Android 原生库仍可用
        implementation("io.coil-kt:coil-compose:2.7.0")  // 图片加载（仅 Android）
    }
    
    // 如果 iOS 也需要图片加载，需找跨平台方案
    commonMain.dependencies {
        // ✅ 用跨平台替代品：coil3 开始支持 KMP
        implementation("io.coil-kt.coil3:coil-compose:3.0.0")
    }
}
```

---

## 八、导航方案

Jetpack Compose 的 Navigation Compose 不支持 CMP，需要以下替代方案：

### 方案一：Voyager（推荐，最流行）

```kotlin
// commonMain
class HomeScreen : Screen {
    @Composable
    override fun Content() {
        val navigator = LocalNavigator.currentOrThrow
        
        Column(
            modifier = Modifier.fillMaxSize().padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text("Home", style = MaterialTheme.typography.headlineLarge)
            
            Button(onClick = {
                navigator.push(DetailScreen(itemId = "123"))
            }) {
                Text("Go to Detail")
            }
        }
    }
}

class DetailScreen(val itemId: String) : Screen {
    @Composable
    override fun Content() {
        val navigator = LocalNavigator.currentOrThrow
        
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Detail: $itemId")
            Button(onClick = { navigator.pop() }) {
                Text("Back")
            }
        }
    }
}

// 入口
@Composable
fun App() {
    Navigator(HomeScreen())
}
```

### 方案二：Decompose（适合复杂架构）

```kotlin
// 适合需要生命周期管理、状态保持的高级场景
// 比 Voyager 更重量，但提供更好的架构约束
interface RootComponent {
    val childStack: Value<ChildStack<*, Child>>
    
    sealed class Child {
        class Home(val component: HomeComponent) : Child()
        class Detail(val component: DetailComponent) : Child()
    }
}
```

### 方案三：简单场景用 expect/actual

```kotlin
// commonMain — 声明导航接口
@Composable
expect fun rememberAppNavigator(): AppNavigator

interface AppNavigator {
    fun navigateTo(route: String)
    fun goBack(): Boolean
}

// androidMain — 使用 Navigation Compose
@Composable
actual fun rememberAppNavigator(): AppNavigator {
    val navController = rememberNavController() // 仅 Android
    return AndroidNavigator(navController)
}

// iosMain/desktopMain — 自建简单导航栈
@Composable
actual fun rememberAppNavigator(): AppNavigator {
    var stack by remember { mutableStateOf(listOf("home")) }
    return SimpleNavigator(
        currentRoute = { stack.last() },
        navigateTo = { stack = stack + it },
        goBack = {
            if (stack.size > 1) {
                stack = stack.dropLast(1)
                true
            } else false
        }
    )
}
```

---

## 九、项目实战：跨平台 App

### 初始化项目

```
方式一：KMP Wizard（推荐）
https://kmp.jetbrains.com/
→ 勾选 Android + iOS + Desktop
→ 勾选 "Share UI" (Compose Multiplatform)
→ 下载项目

方式二：IntelliJ IDEA / Android Studio 模板
File → New → Project → Kotlin Multiplatform
→ 选择 "Compose Multiplatform" 模板
```

### 编写跨平台代码

```kotlin
// commonMain/App.kt
@Composable
fun App() {
    ComposeMultiplatformTheme {
        var showContent by remember { mutableStateOf(false) }
        val greeting = remember { Greeting().greet() }
        
        Column(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Button(onClick = { showContent = !showContent }) {
                Text("Click me!")
            }
            
            AnimatedVisibility(showContent) {
                Column(
                    modifier = Modifier.padding(top = 16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Image(
                        painter = painterResource(Res.drawable.compose_multiplatform),
                        contentDescription = null,
                        modifier = Modifier.size(128.dp)
                    )
                    Text(
                        text = greeting,
                        style = MaterialTheme.typography.headlineSmall,
                        textAlign = TextAlign.Center
                    )
                }
            }
        }
    }
}

// commonMain/Greeting.kt
class Greeting {
    private val platform = getPlatform()
    
    fun greet(): String {
        return "Hello, ${platform.name}!"
    }
}

// expect/actual 平台信息
expect fun getPlatform(): Platform

data class Platform(val name: String)
```

### 构建与运行

```
Android:
  1. 选择运行配置: composeApp (android)
  2. 选择模拟器或真机
  3. 点击 Run ▶

iOS:
  1. macOS 环境 + Xcode 已安装
  2. 打开 iosApp/iosApp.xcodeproj
  3. 选择 iOS 模拟器
  4. 点击 Run ▶
  或者在 Android Studio 中直接运行 iosApp 配置

Desktop:
  1. 选择运行配置: composeApp (desktop)
  2. 点击 Run ▶
  或执行: ./gradlew :composeApp:run

Web (Beta):
  ./gradlew :composeApp:wasmJsBrowserRun
```

---

## 十、从 Jetpack Compose 迁移到 CMP

### 迁移路线图

```
阶段一：评估（1~2 天）
  ├── 盘点当前项目用了哪些 Jetpack Compose 特性
  ├── 识别哪些依赖不支持 KMP
  └── 制定迁移范围

阶段二：提取共享（1~2 周）
  ├── 创建 KMP 模块，迁移业务逻辑到 commonMain
  ├── 保留原生 UI（XML 或 Jetpack Compose）
  └── 验证 Android 端功能正常

阶段三：迁移 UI（2~4 周）
  ├── 将 Compose UI 代码从 androidApp 迁移到 composeApp/commonMain
  ├── 替换 Android 特有能力为 expect/actual
  ├── 添加 iOS/Desktop 平台入口
  └── 逐屏测试各平台
```

### 迁移对照表

| Jetpack Compose (Android) | Compose Multiplatform (通用) |
|---------------------------|------------------------------|
| `androidx.compose.material3.*` | `org.jetbrains.compose.material3.*` |
| `R.drawable.xxx` / `painterResource(R.drawable.xxx)` | `Res.drawable.xxx` / `painterResource(Res.drawable.xxx)` |
| `R.string.xxx` / `stringResource(R.string.xxx)` | `Res.string.xxx` / `stringResource(Res.string.xxx)` |
| `androidx.navigation.compose.*` | Voyager / Decompose / 自定义 |
| `collectAsStateWithLifecycle()` | `collectAsState()` + 手动生命周期 |
| `LocalContext.current` | 仅 Android 端可用 |
| `LocalLifecycleOwner.current` | 仅 Android 端可用 |
| `@HiltViewModel` | 仅 Android 端可用（Koin 替代） |
| `Modifier.imePadding()` | 仅 Android 端可用 |
| `Modifier.navigationBarsPadding()` | 仅 Android 端可用 |

### 实际迁移示例

```kotlin
// ===== 迁移前（Jetpack Compose Android 项目）=====
// HomeScreen.kt (androidApp)
@Composable
fun HomeScreen(viewModel: HomeViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val navController = LocalNavController.current
    val context = LocalContext.current
    
    Scaffold(
        topBar = {
            TopAppBar(title = { Text(stringResource(R.string.app_name)) })
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier.padding(padding)
        ) {
            items(uiState.items) { item ->
                Card(
                    modifier = Modifier.clickable {
                        navController.navigate("detail/${item.id}")
                    }
                ) {
                    AsyncImage(
                        model = ImageRequest.Builder(context)
                            .data(item.imageUrl)
                            .build(),
                        contentDescription = null
                    )
                    Text(item.title)
                }
            }
        }
    }
}

// ===== 迁移后（Compose Multiplatform commonMain）=====
@Composable
fun HomeScreen(viewModel: HomeViewModel) {  // 不用 Hilt，改用 Koin
    val uiState by viewModel.uiState.collectAsState()  // 暂不用 Lifecycle
    val navigator = LocalNavigator.currentOrThrow      // 使用 Voyager
    
    Scaffold(
        topBar = {
            TopAppBar(title = { Text(stringResource(Res.string.app_name)) })
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier.padding(padding)
        ) {
            items(uiState.items, key = { it.id }) { item ->
                Card(
                    modifier = Modifier.clickable {
                        navigator.push(DetailScreen(item.id))
                    }
                ) {
                    // 跨平台图片加载
                    AsyncImage(
                        model = item.imageUrl,
                        contentDescription = null,
                        imageLoader = LocalImageLoader.current  // Coil3 (KMP)
                    )
                    Text(item.title)
                }
            }
        }
    }
}
```

---

## 十一、常见问题与最佳实践

### 最佳实践清单

#### 1. 架构分层
```
✅ DO:
  - commonMain: 所有共享 UI + ViewModel + Repository
  - androidMain/iosMain: 仅平台特定实现
  - 使用 expect/actual 封装平台差异，不要用 if-else

❌ DON'T:
  - 在 commonMain 中使用 android.* / apple.* API
  - 将导航逻辑硬编码到 UI 组件中
  - 忽略 iOS safe area（刘海屏适配）
```

#### 2. 依赖选择
```kotlin
// ✅ 优先选择有 KMP 版本的库
implementation("io.ktor:ktor-client-core:2.3.0")      // 网络
implementation("org.jetbrains.kotlinx:kotlinx-datetime:0.6.0") // 日期
implementation("io.coil-kt.coil3:coil-compose:3.0.0")  // 图片（KMP）

// ❌ 避免使用仅 Android 的库
// implementation("androidx.room:room-runtime:*")  // Room 现在也已支持 KMP
```

#### 3. 资源管理
```kotlin
// ✅ 使用 compose.resources
stringResource(Res.string.welcome)
painterResource(Res.drawable.logo)

// ❌ 使用 Android R 文件（仅 Android 可用）
// R.string.welcome
// painterResource(R.drawable.logo)
```

#### 4. 主题适配
```kotlin
// ✅ 在 commonMain 中定义跨平台主题
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = if (darkTheme) DarkColors else LightColors,
        typography = Typography,
        content = content
    )
}

// ✅ 使用 System Appearance 读取暗色模式（仅 Android 有 isSystemInDarkTheme）
// 跨平台方案：
@Composable
expect fun isDarkMode(): Boolean

// androidMain
@Composable
actual fun isDarkMode(): Boolean = isSystemInDarkTheme()

// iosMain
@Composable
actual fun isDarkMode(): Boolean {
    // 读取 UITraitCollection
    return UITraitCollection.currentTraitCollection.userInterfaceStyle 
        == UIUserInterfaceStyle.Dark
}
```

#### 5. 性能优化
```kotlin
// ✅ 使用 @Immutable 标记数据类（减少重组）
@Immutable
data class UiState(
    val title: String,
    val items: ImmutableList<Item>
)

// ✅ 大列表使用 key 参数
LazyColumn {
    items(items, key = { it.id }) { item -> ItemRow(item) }
}

// ✅ 提取不依赖状态的子组件
@Composable
fun HeavyParent(state: State) {
    Column {
        Text(state.title)        // 重组时更新
        StaticBackground()        // 不变，被跳过
    }
}

@Composable  // 不接收 state 参数，重组时被跳过
fun StaticBackground() { ... }
```

### 常见坑与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `Unresolved reference: R` | 使用了 Android R 资源系统 | 改用 `compose.resources` 的 `Res.*` |
| iOS 文字被刘海遮挡 | 未处理 safe area | 使用 `WindowInsets.safeContent` |
| Desktop 窗口无法打开 | 缺少 JVM target | 添加 `jvm("desktop")` 和 `compose.desktop.currentOs` |
| Navigation 报错 | 使用了仅 Android 的 Navigation Compose | 改用 Voyager 或 Decompose |
| 第三方库报 `NoClassDefFoundError` | 库不支持 KMP | 查找 KMP 兼容版或用 expect/actual 封装 |
| Compose 版本冲突 | JetBrains 版和 Google 版混用 | Android 端统一用 `org.jetbrains.compose` |
| iOS 模拟器无法运行 | Xcode 配置问题 | 检查 `iosApp.xcodeproj` 的 Framework Search Paths |

### 推荐 CMP 技术栈

```
📦 Compose 核心：
  - Compose Multiplatform  → 跨平台 UI 框架
  - compose.resources      → 多平台资源管理
  - compose.material3      → Material3 组件

🧭 导航：
  - Voyager                → 轻量级跨平台导航（推荐）
  - Decompose              → 架构级导航 + 生命周期

💉 依赖注入：
  - Koin                   → 跨平台 DI（最流行）
  - Kotlin-inject          → 编译时 DI（无反射）

🌐 网络：
  - Ktor Client            → 跨平台 HTTP 客户端
  - kotlinx.serialization  → JSON 序列化

💾 数据存储：
  - Room (KMP)             → 跨平台数据库
  - DataStore (Android)    → Android 键值存储
  - NSUserDefaults (iOS)   → iOS 键值存储

🖼️ 图片加载：
  - Coil3 (KMP)            → 跨平台图片加载

🧪 测试：
  - Compose UI Test (KMP)  → 跨平台 UI 测试
  - kotlin.test            → 跨平台单元测试

📐 架构：
  - MVVM / MVI             → 推荐架构模式
  - kotlinx.coroutines     → 异步处理
```

---

## 总结

Compose Multiplatform 是 Kotlin 跨平台生态的 UI 层解决方案，在设计上追求**最大代码共享 + 保留平台灵活性**：

1. **共享 UI 层** — 一套 Compose 代码运行在 Android/iOS/Desktop/Web
2. **基于 Jetpack Compose Runtime** — 成熟的 Snapshot State System 和重组机制
3. **JetBrains 维护** — 独立发布节奏，与 Google Jetpack Compose 并行演进
4. **expect/actual** — 在需要时精准处理平台差异，不必为所有平台写全套 UI
5. **渐进式采用** — 从 KMP 共享逻辑起步，逐步扩展到共享 UI

### Jetpack Compose vs Compose Multiplatform 速查

```
Jetpack Compose:
  平台: 仅 Android
  维护: Google
  特性: 最新、最全（Navigation、Hilt、Lifecycle）
  资源: Android R 系统
  场景: 纯 Android 项目

Compose Multiplatform:
  平台: Android + iOS + Desktop + Web
  维护: JetBrains
  特性: 跨平台为主（需第三方导航、DI）
  资源: compose.resources（多平台）
  场景: 跨平台 UI 共享、KMP 项目
```

> **两者不是竞争关系。Jetpack Compose 是引擎，Compose Multiplatform 是装上这个引擎的跨平台飞机。**
