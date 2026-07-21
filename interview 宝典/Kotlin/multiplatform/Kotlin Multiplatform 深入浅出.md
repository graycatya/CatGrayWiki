# Kotlin Multiplatform (KMP) 深入浅出

> 一份深入浅出的 KMP 学习指南，从核心概念到项目实战，帮你系统掌握跨平台开发。

---

## 目录

1. [什么是 KMP？](#一什么是-kmp)
2. [为什么选择 KMP？](#二为什么选择-kmp)
3. [核心概念：共享逻辑，不共享 UI](#三核心概念共享逻辑不共享-ui)
4. [项目结构详解](#四项目结构详解)
5. [expect / actual 机制](#五expect--actual-机制)
6. [层级项目结构](#六层级项目结构)
7. [Compose Multiplatform：共享 UI](#七compose-multiplatform共享-ui)
8. [第一个 KMP 项目实战](#八第一个-kmp-项目实战)
9. [平台特定 API 访问策略](#九平台特定-api-访问策略)
10. [常见问题与最佳实践](#十常见问题与最佳实践)

---

## 一、什么是 KMP？

**Kotlin Multiplatform (KMP)** 是 JetBrains 推出的跨平台开发技术，允许开发者使用 Kotlin 语言编写一次业务逻辑代码，然后编译到多个平台（Android、iOS、Web、桌面、服务端）。

### KMP 不是什么？

| KMP **不是** | 说明 |
|-------------|------|
| ❌ 不是"一次编写，到处运行"的框架 | 不像 Flutter/React Native 那样统一所有代码 |
| ❌ 不是编译所有 Kotlin 代码到所有平台 | 不同平台有各自的编译产物 |
| ❌ 不是强制共享 UI | UI 层面保持原生（除非使用 Compose Multiplatform） |

### KMP 的本质

```
┌─────────────────────────────────────┐
│         共享业务逻辑层 (Kotlin)       │
│   ┌─────────────────────────────┐   │
│   │   commonMain (通用代码)      │   │
│   │   - 数据模型                 │   │
│   │   - 网络请求                 │   │
│   │   - 业务规则                 │   │
│   │   - 状态管理                 │   │
│   └─────────────────────────────┘   │
└─────────────────────────────────────┘
         │           │           │
    ┌────▼───┐ ┌────▼───┐ ┌────▼───┐
    │ Android│ │   iOS  │ │ Desktop│
    │原生 UI │ │原生 UI │ │原生 UI │
    │(Jetpack│ │(SwiftUI│ │(Compose│
    │Compose)│ │/UIKit) │ │Desktop)│
    └────────┘ └────────┘ └────────┘
```

---

## 二、为什么选择 KMP？

### 核心优势

1. **代码复用最大化**：共享 50%~80% 的业务逻辑代码
2. **原生 UI 体验**：各平台使用原生 UI 框架，性能无损失
3. **渐进式采用**：可以从一个模块开始，逐步扩展
4. **无锁定风险**：随时可以回退到纯原生开发
5. **Kotlin 生态**：利用 Kotlin 的现代语言特性（协程、Flow、密封类等）

### 与竞品对比

| 特性 | KMP | Flutter | React Native |
|------|-----|---------|-------------|
| 语言 | Kotlin | Dart | JavaScript |
| UI 方式 | 原生 UI（或 Compose） | 自绘引擎 | 原生桥接 |
| 共享范围 | 业务逻辑 | 全部代码 | 全部代码 |
| 原生访问 | 直接调用 | 需要 Channel | 需要 Bridge |
| 学习曲线 | 中（需了解各平台） | 低 | 低 |
| 性能 | 原生级 | 接近原生 | 接近原生 |
| 适用场景 | 已有原生项目扩展 | 新项目 | 新项目 |

### 谁在用 KMP？

- **BiliBili（哔哩哔哩）**：即时消息模块
- **Netflix**：客户端数据处理
- **McDonald's**：全球移动应用
- **Forbes**：内容管理
- **Cash App**：核心业务逻辑

---

## 三、核心概念：共享逻辑，不共享 UI

KMP 的核心设计哲学：

> **共享你想要的，不共享你不想的。**

### 什么应该共享？

```
✅ 应该共享：
  - 数据模型（DTO/Entity）
  - 网络层（API 调用、序列化/反序列化）
  - 数据库操作（SQLDelight/Room）
  - 业务逻辑（验证、计算、状态管理）
  - 依赖注入（Koin）
  - 单元测试
```

### 什么不应该共享？

```
❌ 不应共享（或需平台特定实现）：
  - UI 层（除非用 Compose Multiplatform）
  - 平台特定 API（相机、GPS、推送通知）
  - 文件系统访问
  - 平台特定动画/交互
```

### 共享策略

```kotlin
// ✅ 好的做法：共享纯业务逻辑
// commonMain/Calculator.kt
class Calculator {
    fun add(a: Int, b: Int): Int = a + b
    fun calculateTax(price: Double, rate: Double): Double = price * rate
}

// ❌ 不好的做法：试图在 commonMain 访问平台 API
// commonMain/FileHelper.kt
// fun readFile(path: String): String = java.io.File(path).readText() // 编译错误！
```

---

## 四、项目结构详解

### 典型 KMP 项目结构

```
MyKMPProject/
├── shared/                          # 共享模块
│   ├── build.gradle.kts            # Gradle 构建脚本
│   └── src/
│       ├── commonMain/             # 全平台共享代码
│       │   └── kotlin/
│       │       ├── Greeting.kt
│       │       ├── Platform.kt     # expect 声明
│       │       └── model/
│       │           └── User.kt
│       ├── commonTest/             # 共享测试
│       ├── androidMain/            # Android 特定代码
│       │   └── kotlin/
│       │       └── Platform.android.kt  # actual 实现
│       ├── iosMain/                # iOS 特定代码
│       │   └── kotlin/
│       │       └── Platform.ios.kt
│       └── desktopMain/            # 桌面特定代码
│           └── kotlin/
│               └── Platform.desktop.kt
├── androidApp/                      # Android 应用模块
│   ├── build.gradle.kts
│   └── src/main/
├── iosApp/                          # iOS 应用 (Xcode 项目)
│   └── iosApp.xcodeproj
└── build.gradle.kts                 # 根构建脚本
```

### Gradle 配置详解

```kotlin
// shared/build.gradle.kts
plugins {
    kotlin("multiplatform")    // KMP 插件
    id("com.android.library")  // Android 库插件
    kotlin("plugin.serialization") // 序列化插件
}

kotlin {
    // 1. 声明目标平台
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
            baseName = "shared"  // 导出给 iOS 的 framework 名称
            isStatic = true
        }
    }
    
    // 2. 配置源集
    sourceSets {
        // 公共代码
        val commonMain by getting {
            dependencies {
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.0")
                implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")
            }
        }
        
        val commonTest by getting {
            dependencies {
                implementation(kotlin("test"))
            }
        }
        
        // Android 特定依赖
        val androidMain by getting {
            dependencies {
                implementation("androidx.core:core-ktx:1.12.0")
            }
        }
        
        // iOS 特定依赖
        val iosX64Main by getting
        val iosArm64Main by getting
        val iosSimulatorArm64Main by getting
        val iosMain by creating {
            dependsOn(commonMain)
            iosX64Main.dependsOn(this)
            iosArm64Main.dependsOn(this)
            iosSimulatorArm64Main.dependsOn(this)
        }
    }
}
```

### 源集（Source Sets）关系图

```
                    ┌─────────────┐
                    │ commonMain  │ ← 所有平台共享
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
    ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │ androidMain │ │   iosMain   │ │ desktopMain │ ← 平台特定
    └─────────────┘ └──────┬──────┘ └─────────────┘
                    ┌───────┼───────┐
              ┌─────▼────┐┌────▼────┐┌─────▼────┐
              │iosArm64 ││ iosX64  ││iosSim... │ ← 具体设备
              │  Main   ││  Main   ││Arm64Main │
              └─────────┘└─────────┘└──────────┘
```

### 编译过程

当编译到 iOS 真机时，Kotlin 编译器收集以下源集一起编译：

```
commonMain → iosMain → iosArm64Main
```

---

## 五、expect / actual 机制

这是 KMP 最核心的语言特性，用于处理平台差异。

### 工作原理

```
┌──────────────────────────────────────────┐
│  commonMain                              │
│  expect fun getPlatformName(): String    │ ← 声明"期望"，不实现
└──────────┬───────────────┬───────────────┘
           │               │
    ┌──────▼──────┐ ┌──────▼──────┐
    │ androidMain │ │   iosMain   │
    │ actual fun  │ │ actual fun  │           ← 各平台"实际"实现
    │ = "Android" │ │ = "iOS"     │
    └─────────────┘ └─────────────┘
```

### 基本示例

```kotlin
// ========== commonMain/Platform.kt ==========
// 声明期望的接口和函数
expect fun getPlatform(): Platform

expect class Platform() {
    val name: String
    val version: String
}

// ========== androidMain/Platform.android.kt ==========
actual fun getPlatform(): Platform = AndroidPlatform()

actual class Platform actual constructor() {
    actual val name: String = "Android"
    actual val version: String = android.os.Build.VERSION.SDK_INT.toString()
}

// ========== iosMain/Platform.ios.kt ==========
actual fun getPlatform(): Platform = IOSPlatform()

actual class Platform actual constructor() {
    actual val name: String = 
        platform.UIKit.UIDevice.currentDevice.systemName()
    actual val version: String = 
        platform.UIKit.UIDevice.currentDevice.systemVersion
}
```

### 使用场景示例

```kotlin
// 场景1：生成 UUID
// commonMain
expect fun randomUUID(): String

// androidMain
actual fun randomUUID() = java.util.UUID.randomUUID().toString()

// iosMain
actual fun randomUUID(): String = platform.Foundation.NSUUID().UUIDString()

// 场景2：获取当前时间戳
// commonMain
expect fun currentTimeMillis(): Long

// androidMain
actual fun currentTimeMillis(): Long = System.currentTimeMillis()

// iosMain
actual fun currentTimeMillis(): Long = 
    (platform.Foundation.NSDate().timeIntervalSince1970 * 1000).toLong()

// 场景3：平台特定配置
// commonMain
expect class AppConfig() {
    val apiBaseUrl: String
    val isDebug: Boolean
}

// androidMain
actual class AppConfig actual constructor() {
    actual val apiBaseUrl: String = BuildConfig.API_BASE_URL
    actual val isDebug: Boolean = BuildConfig.DEBUG
}

// iosMain
actual class AppConfig actual constructor() {
    actual val apiBaseUrl: String = "https://api.production.com"
    actual val isDebug: Boolean = false
}
```

### expect/actual 支持的类型

| 声明类型 | 是否支持 | 说明 |
|---------|---------|------|
| 函数 | ✅ | 最常用 |
| 类 | ✅ | 构造函数签名需匹配 |
| 接口 | ✅ | 常用于依赖注入 |
| 属性 | ✅ | val/var |
| 枚举类 | ✅ | |
| 注解 | ✅ | |
| 对象声明 | ✅ | object/companion object |
| 类型别名 | ✅ | |

---

## 六、层级项目结构

KMP 支持**中间源集（Intermediate Source Sets）**，实现更细粒度的代码共享。

### 为什么需要层级结构？

假设你需要在所有 Apple 平台（iOS + macOS）共享某些代码，但不能影响 Android：

```
                    ┌─────────────┐
                    │ commonMain  │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
    ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │ androidMain │ │  appleMain  │ │   jsMain    │ ← 中间源集
    └─────────────┘ └──────┬──────┘ └─────────────┘
                    ┌───────┼───────┐
              ┌─────▼────┐┌────▼────┐
              │  iosMain ││macosMain│
              └──────────┘└─────────┘
```

### 默认层级模板

Kotlin Gradle 插件内置了默认层级模板，会根据声明的目标自动创建中间源集：

```kotlin
kotlin {
    androidTarget()
    iosArm64()
    iosSimulatorArm64()
    // 插件自动创建: appleMain, iosMain, nativeMain 等
    
    sourceSets {
        // 可以直接访问自动创建的中间源集
        val appleMain by getting {
            dependencies {
                // 所有 Apple 平台共享的依赖
            }
        }
    }
}
```

### 自动创建的源集关系

```
nativeMain          ← 所有 Native 目标 (iOS, macOS, Linux, Windows)
  ├── appleMain     ← 所有 Apple 目标 (iOS, macOS, watchOS, tvOS)
  │     ├── iosMain ← iOS 真机 + 模拟器
  │     └── macosMain
  ├── linuxMain
  └── mingwMain
```

---

## 七、Compose Multiplatform：共享 UI

**Compose Multiplatform (CMP)** 是 JetBrains 推出的跨平台 UI 框架，基于 Jetpack Compose。

### CMP vs 原生 UI

| 方案 | 优势 | 劣势 |
|------|------|------|
| **CMP（共享 UI）** | 一套 UI 代码多平台运行 | 无法使用平台原生控件 |
| **原生 UI** | 完美原生体验 | 每个平台需单独编写 UI |

### CMP 支持的平台

| 平台 | 状态 |
|------|------|
| Android | ✅ 稳定（通过 Jetpack Compose） |
| iOS | ✅ 稳定 |
| Desktop（Windows/macOS/Linux） | ✅ 稳定 |
| Web | 🧪 Beta（基于 Kotlin/Wasm） |

### 快速示例

```kotlin
// sharedUI/src/commonMain/
@Composable
fun App() {
    MaterialTheme {
        var text by remember { mutableStateOf("Hello, KMP!") }
        
        Column(
            modifier = Modifier.fillMaxSize().padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = text,
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Button(onClick = { text = "Button Clicked!" }) {
                Text("Click Me")
            }
        }
    }
}
```

### 何时使用 CMP？

```
✅ 适合 CMP 的场景：
  - 新项目从零开始
  - UI 设计统一，不需要平台特定外观
  - 团队熟悉 Jetpack Compose
  - 内部工具/管理后台

❌ 适合原生 UI 的场景：
  - 已有成熟的 iOS 项目，只想共享逻辑
  - UI 需要严格遵循平台设计规范
  - 需要使用复杂的平台特定控件
```

---

## 八、第一个 KMP 项目实战

### 环境准备

1. **安装 IntelliJ IDEA**（Community 或 Ultimate）
2. **安装 Kotlin Multiplatform 插件**
3. **Android Studio**（用于 Android 编译）
4. **Xcode**（用于 iOS 编译，仅 macOS）

### 创建项目

```
File → New → Project → Kotlin Multiplatform

配置：
├── Project Name: MyFirstKMP
├── Project ID: com.example.myfirstkmp
├── Targets: ☑ Android  ☑ iOS
└── iOS UI: "Do not share UI"
```

### 编写第一个共享代码

```kotlin
// shared/src/commonMain/kotlin/Greeting.kt
data class Greeting(
    val message: String,
    val platform: String
)

class GreetingHelper {
    fun createGreeting(name: String): Greeting {
        return Greeting(
            message = "Hello, $name! Welcome to KMP 🎉",
            platform = getPlatform().name
        )
    }
}
```

### Android 端调用

```kotlin
// androidApp/src/main/kotlin/MainActivity.kt
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            val greeting = GreetingHelper().createGreeting("Android Developer")
            
            Text(
                text = "${greeting.message}\nRunning on: ${greeting.platform}",
                modifier = Modifier.padding(16.dp)
            )
        }
    }
}
```

### iOS 端调用

```swift
// iosApp/ContentView.swift
import SwiftUI
import shared  // 导入 KMP 导出的 framework

struct ContentView: View {
    let greeting = GreetingHelper().createGreeting(name: "iOS Developer")
    
    var body: some View {
        VStack {
            Text(greeting.message)
            Text("Running on: \(greeting.platform)")
        }
        .padding()
    }
}
```

### 运行项目

```
Android:
  1. 选择运行配置: androidApp
  2. 选择模拟器
  3. 点击 Run ▶

iOS:
  1. 启动一次 Xcode 加载模拟器
  2. 选择运行配置: iosApp
  3. 选择 iOS 模拟器
  4. 点击 Run ▶
```

---

## 九、平台特定 API 访问策略

当业务逻辑需要访问平台 API 时，有三种主流策略：

### 策略一：expect/actual 函数（简单场景）

```kotlin
// commonMain
expect class ImagePicker {
    suspend fun pickImage(): ByteArray
}

// androidMain
actual class ImagePicker actual constructor() {
    actual suspend fun pickImage(): ByteArray {
        // 使用 Android Activity Result API
    }
}

// iosMain
actual class ImagePicker actual constructor() {
    actual suspend fun pickImage(): ByteArray {
        // 使用 UIImagePickerController
    }
}
```

### 策略二：接口 + 依赖注入（复杂场景）

```kotlin
// commonMain - 定义接口
interface PlatformServices {
    fun getDeviceInfo(): DeviceInfo
    fun getNetworkStatus(): NetworkStatus
    suspend fun pickImage(): ByteArray
}

// 在共享模块中通过接口使用
class UserRepository(
    private val platformServices: PlatformServices
) {
    suspend fun uploadAvatar() {
        val image = platformServices.pickImage()
        val device = platformServices.getDeviceInfo()
        // 上传逻辑...
    }
}

// androidMain - Android 实现
class AndroidPlatformServices : PlatformServices {
    override fun getDeviceInfo(): DeviceInfo = DeviceInfo(
        model = Build.MODEL,
        osVersion = Build.VERSION.SDK_INT.toString()
    )
    // ... 其他实现
}

// iosMain - iOS 实现
class IOSPlatformServices : PlatformServices {
    override fun getDeviceInfo(): DeviceInfo = DeviceInfo(
        model = UIDevice.currentDevice.model,
        osVersion = UIDevice.currentDevice.systemVersion
    )
    // ... 其他实现
}
```

### 策略三：Koin 依赖注入（推荐）

```kotlin
// commonMain - 定义模块
val commonModule = module {
    single<ApiClient> { ApiClientImpl() }
    single<UserRepository> { UserRepository(get(), get()) }
}

// 使用 expect 声明平台模块
expect val platformModule: Module

// 在 Application 中组装
fun initKoin() {
    startKoin {
        modules(commonModule + platformModule)
    }
}

// androidMain - Android 平台模块
actual val platformModule: Module = module {
    single<PlatformServices> { AndroidPlatformServices() }
    single<ImagePicker> { AndroidImagePicker() }
}

// iosMain - iOS 平台模块
actual val platformModule: Module = module {
    single<PlatformServices> { IOSPlatformServices() }
    single<ImagePicker> { IOSImagePicker() }
}
```

---

## 十、常见问题与最佳实践

### 最佳实践清单

#### 1. 项目结构
```
✅ DO:
  - 共享模块只包含业务逻辑
  - 保持 commonMain 纯净（无平台依赖）
  - 使用清晰的分层架构（data/domain/presentation）

❌ DON'T:
  - 在 commonMain 中引入平台特定库
  - 把所有代码都塞进 commonMain
  - 忽略源集的层级关系
```

#### 2. 平台差异处理
```kotlin
// ✅ 好：用 expect/actual 封装差异
expect fun generateId(): String

// ❌ 差：用 if-else 判断平台（commonMain 中无法做到）
// fun generateId() = if (Platform.isAndroid) ... else ...
```

#### 3. 线程与协程
```kotlin
// ✅ 使用 kotlinx.coroutines（跨平台）
class UserViewModel {
    private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    
    fun loadUser() {
        scope.launch {
            val user = withContext(Dispatchers.Default) {
                userRepository.getUser()
            }
            // 更新 UI
        }
    }
}
```

#### 4. 序列化
```kotlin
// 使用 kotlinx.serialization（跨平台）
@Serializable
data class User(
    val id: String,
    val name: String,
    val email: String
)

// commonMain
val json = Json { ignoreUnknownKeys = true }
val user = json.decodeFromString<User>(jsonString)
```

#### 5. 网络请求
```kotlin
// 使用 Ktor Client（跨平台 HTTP 客户端）
// commonMain
val client = HttpClient {
    install(ContentNegotiation) {
        json(Json { ignoreUnknownKeys = true })
    }
}

suspend fun fetchUsers(): List<User> {
    return client.get("https://api.example.com/users").body()
}
```

### 常见坑与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `Unresolved reference` 在 commonMain | 引用了平台特定 API | 使用 expect/actual 封装 |
| iOS 编译失败 "framework not found" | Xcode 未正确配置 | 检查 Framework Search Paths |
| 协程在 iOS 上行为异常 | 未正确使用 Main Dispatcher | 使用 `Dispatchers.Main` 并确保主线程 |
| 第三方库不兼容 KMP | 库未提供 KMP 版本 | 查找替代方案或用 expect/actual 封装 |
| Android 模块找不到共享代码 | 依赖配置错误 | 检查 `implementation(project(":shared"))` |

### 推荐 KMP 技术栈

```
📦 核心：
  - kotlinx.coroutines     → 异步/并发
  - kotlinx.serialization  → JSON 序列化
  - kotlinx.datetime       → 跨平台日期时间

🌐 网络：
  - Ktor Client            → HTTP 客户端

💾 数据存储：
  - SQLDelight             → 跨平台数据库
  - DataStore (Android)    → 键值存储

🖼️ UI：
  - Compose Multiplatform  → 跨平台 UI
  - Jetpack Compose        → Android UI

💉 依赖注入：
  - Koin                   → 轻量级 DI

🧪 测试：
  - kotlin.test            → 跨平台测试
  - Turbine                → Flow 测试
```

---

## 总结

KMP 的核心思想是**渐进式共享**——从业务逻辑开始，逐步扩展到更多层次。它不是"全有或全无"的方案，你可以：

1. **从共享数据模型开始** → 用 KMP 写 DTO/Entity
2. **扩展到网络层** → 共享 API 调用和序列化
3. **共享业务逻辑** → 验证、计算、状态管理
4. **（可选）共享 UI** → 使用 Compose Multiplatform

记住 KMP 的黄金法则：

> **共享你想要的，不共享你不想的。原生 UI 永远是最安全的选择。**
