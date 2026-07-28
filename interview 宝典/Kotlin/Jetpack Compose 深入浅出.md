# Jetpack Compose 深入浅出

> 一份深入浅出的 Jetpack Compose 学习指南，从核心概念到项目实战，帮你系统掌握 Android 声明式 UI 开发。

---

## 目录

1. [什么是 Jetpack Compose？](#一什么是-jetpack-compose)
2. [为什么选择 Jetpack Compose？](#二为什么选择-jetpack-compose)
3. [核心概念：声明式 UI 与组合](#三核心概念声明式-ui-与组合)
4. [Composable 函数详解](#四composable-函数详解)
5. [状态管理与重组](#五状态管理与重组)
6. [布局系统](#六布局系统)
7. [Modifier 修饰符体系](#七modifier-修饰符体系)
8. [主题与样式](#八主题与样式)
9. [副作用 API](#九副作用-api)
10. [导航](#十导航)
11. [Compose 与 View 互操作](#十一compose-与-view-互操作)
12. [常见问题与最佳实践](#十二常见问题与最佳实践)

---

## 一、什么是 Jetpack Compose？

**Jetpack Compose** 是 Google 推出的 Android 原生声明式 UI 框架，使用 Kotlin 语言编写，彻底改变了 Android UI 开发方式。

### Compose 不是什么？

| Compose **不是** | 说明 |
|-------------|------|
| ❌ 不是对 XML 布局的封装 | 是完全独立的 UI 框架 |
| ❌ 不是 WebView 渲染方案 | 直接编译为原生 Android View |
| ❌ 不是跨平台 UI 框架 | 仅支持 Android（Compose Multiplatform 可跨平台） |
| ❌ 不需要 Activity 就能运行 | 仍需嵌入 Activity/Fragment 中 |

### Compose 的核心哲学

```
┌─────────────────────────────────────────────┐
│              声明式 UI 编程模型               │
│                                              │
│   UI = f(State)                              │
│                                              │
│   给定相同的 State，生成相同的 UI              │
│   State 变化 → UI 自动更新                    │
└─────────────────────────────────────────────┘
         │                    │
    ┌────▼───┐          ┌────▼───┐
    │ State  │ ──变化──→ │   UI   │
    │ (数据)  │          │ (界面)  │
    └────────┘          └────────┘
```

---

## 二、为什么选择 Jetpack Compose？

### 核心优势

1. **代码量大幅减少**：相比 XML + View 体系，代码量减少 30%~50%
2. **声明式语法**：直接描述 UI "应该是什么样"，而非"如何构建"
3. **Kotlin 原生**：充分利用 Kotlin 语言特性（lambda、扩展函数、协程）
4. **状态驱动**：自动响应数据变化，无需手动 `findViewById` 和 `setText`
5. **独立于系统版本**：通过 Jetpack 库分发，不受 Android 版本限制
6. **与 View 体系共存**：渐进式迁移，可在现有项目中逐步采用

### 与 XML View 体系对比

| 特性 | Jetpack Compose | XML + View |
|------|----------------|------------|
| 语言 | Kotlin DSL | XML + Kotlin/Java |
| 编程范式 | 声明式 | 命令式 |
| UI 更新 | 自动（重组） | 手动（findViewById + setter） |
| 列表性能 | 惰性布局（LazyColumn） | RecyclerView + Adapter |
| 动画 | 内置 API，简单易用 | 相对复杂 |
| 预览 | `@Preview` 注解 | Design 视图 / 独立工具 |
| 主题 | MaterialTheme DSL | styles.xml + themes.xml |
| 学习曲线 | 中（新概念） | 低（传统但繁琐） |

### 谁在用 Compose？

- **Google 官方应用**：Play Store、Gmail、Messages
- **Twitter (X)**：逐步采用 Compose 重写
- **Airbnb**：设计系统迁移到 Compose
- **Tinder**：新功能使用 Compose
- **Lyft**：共享模块用 Compose Multiplatform

---

## 三、核心概念：声明式 UI 与组合

Compose 的核心设计哲学：

> **UI 是状态的函数：UI = f(State)**

### 命令式 vs 声明式

```kotlin
// ❌ 命令式（传统 XML View 方式）
val textView = findViewById<TextView>(R.id.title)
textView.text = "Hello"
button.setOnClickListener {
    textView.text = "Clicked!"
}

// ✅ 声明式（Compose 方式）
@Composable
fun Greeting() {
    var text by remember { mutableStateOf("Hello") }
    
    Column {
        Text(text = text)
        Button(onClick = { text = "Clicked!" }) {
            Text("Click Me")
        }
    }
}
```

### 组合（Composition）与重组（Recomposition）

```
┌──────────┐  State 变化   ┌──────────┐
│ 首次组合  │ ───────────→ │   重组    │
│Composition│              │Recomposition│
└──────────┘              └──────────┘
     │                         │
     ▼                         ▼
 构建完整 UI 树          仅重建受影响部分
```

### 智能重组

```kotlin
@Composable
fun UserProfile(user: User, onClick: () -> Unit) {
    Column {
        // 只有当 user.name 变化时才重组此 Text
        Text(text = user.name)
        
        // 只有当 user.avatar 变化时才重组此 Image
        AsyncImage(model = user.avatar)
        
        // Lambda 引用稳定，不会触发重组
        Button(onClick = onClick) {
            Text("Follow")
        }
    }
}
```

---

## 四、Composable 函数详解

### 基本规则

```kotlin
@Composable                          // 必须是 @Composable 注解
fun MyComponent(                     // 命名规范：大驼峰
    title: String,                   // 参数决定 UI 内容
    onAction: () -> Unit             // 回调处理事件
) {
    // 1. 可以调用其他 @Composable 函数
    Text(text = title)
    
    // 2. 不能返回值（返回 Unit）
    // ❌ return "result"  // 编译错误
    
    // 3. 必须是幂等的（同一输入，同一输出）
    // ❌ 不要在组合期间产生副作用
    
    // 4. 可以以任意顺序执行
    // 不要依赖执行顺序
}
```

### 常用基础组件

```kotlin
// 文本
Text(
    text = "Hello Compose",
    fontSize = 18.sp,
    fontWeight = FontWeight.Bold,
    color = Color.Blue,
    maxLines = 2,
    overflow = TextOverflow.Ellipsis
)

// 按钮
Button(
    onClick = { /* 处理点击 */ },
    colors = ButtonDefaults.buttonColors(
        containerColor = Color.Red
    )
) {
    Text("Click Me")
}

// 图片
Image(
    painter = painterResource(id = R.drawable.ic_avatar),
    contentDescription = "Avatar",
    modifier = Modifier.size(48.dp).clip(CircleShape),
    contentScale = ContentScale.Crop
)

// 输入框
var text by remember { mutableStateOf("") }
TextField(
    value = text,
    onValueChange = { text = it },
    label = { Text("Username") },
    leadingIcon = { Icon(Icons.Default.Person, null) }
)
```

### 组合函数不能做什么

```
❌ Composable 函数限制：
  - 不能返回非 Unit 值
  - 不能在普通函数中被调用
  - 不能在协程中直接调用（需在 Composition 上下文中）
  - 不要读写全局变量（除 State 外）
  - 不要在组合期间执行耗时操作
```

---

## 五、状态管理与重组

### State 核心类型

```kotlin
// 1. mutableStateOf — 最基础的状态
var count by remember { mutableStateOf(0) }

// 2. mutableStateListOf — 列表状态
val items = remember { mutableStateListOf<String>() }

// 3. mutableStateMapOf — Map 状态
val map = remember { mutableStateMapOf<String, Int>() }

// 4. derivedStateOf — 派生状态（避免不必要的重组）
val isExpensive by remember {
    derivedStateOf { list.filter { it.price > 100 }.size }
}
```

### remember 的生命周期

```kotlin
@Composable
fun RememberDemo() {
    // remember: 在组合期间记住值，重组时不丢失
    var count by remember { mutableStateOf(0) }
    
    // remember(key): 当 key 变化时重新计算
    val filteredData by remember(searchQuery) {
        mutableStateOf(allData.filter { it.contains(searchQuery) })
    }
    
    // rememberSaveable: 跨进程恢复时保留
    var text by rememberSaveable { mutableStateOf("") }
    
    // ❌ 没有 remember，每次重组都会重置为 0
    // var count by mutableStateOf(0)
}
```

### 状态提升（State Hoisting）

```kotlin
// ❌ 不好的做法：状态私有，不可复用
@Composable
fun BadSearchBar() {
    var query by remember { mutableStateOf("") }
    TextField(value = query, onValueChange = { query = it })
}

// ✅ 好的做法：状态提升到父组件
@Composable
fun GoodSearchBar(
    query: String,
    onQueryChange: (String) -> Unit
) {
    TextField(
        value = query,
        onValueChange = onQueryChange,
        placeholder = { Text("Search...") }
    )
}

// 使用
@Composable
fun Screen() {
    var query by remember { mutableStateOf("") }
    GoodSearchBar(query = query, onQueryChange = { query = it })
}
```

### 状态管理架构对比

```
┌──────────────────────────────────────────────────┐
│                   状态管理方案                     │
├──────────────┬──────────────┬────────────────────┤
│  remember    │ ViewModel    │ 第三方 (MVI)       │
├──────────────┼──────────────┼────────────────────┤
│ 简单 UI 状态  │ 屏幕级状态    │ 复杂业务状态        │
│ 组件内部状态  │ 配置变更存活  │ 单一数据源          │
│ 不需 ViewModel│ 与生命周期绑定 │ 可测试性强          │
└──────────────┴──────────────┴────────────────────┘
```

---

## 六、布局系统

### 三大基础布局

```kotlin
// Column — 垂直排列
Column(
    modifier = Modifier.fillMaxWidth(),
    verticalArrangement = Arrangement.Center,  // 垂直对齐
    horizontalAlignment = Alignment.CenterHorizontally // 水平对齐
) {
    Text("Item 1")
    Text("Item 2")
}

// Row — 水平排列
Row(
    modifier = Modifier.fillMaxWidth(),
    horizontalArrangement = Arrangement.SpaceBetween,
    verticalAlignment = Alignment.CenterVertically
) {
    Icon(Icons.Default.Star, null)
    Text("Title")
    Icon(Icons.Default.MoreVert, null)
}

// Box — 堆叠布局（类似 FrameLayout）
Box(
    modifier = Modifier.fillMaxSize(),
    contentAlignment = Alignment.Center
) {
    Image(/* 背景图 */)
    Text("叠加的文字") // 覆盖在上面
}
```

### 约束布局

```kotlin
@Composable
fun ConstraintLayoutDemo() {
    ConstraintLayout(modifier = Modifier.fillMaxWidth()) {
        val (title, subtitle, button) = createRefs()
        
        Text(
            text = "Title",
            modifier = Modifier.constrainAs(title) {
                top.linkTo(parent.top, 16.dp)
                start.linkTo(parent.start, 16.dp)
            }
        )
        
        Text(
            text = "Subtitle",
            modifier = Modifier.constrainAs(subtitle) {
                top.linkTo(title.bottom, 8.dp)
                start.linkTo(parent.start, 16.dp)
            }
        )
        
        Button(
            onClick = {},
            modifier = Modifier.constrainAs(button) {
                top.linkTo(parent.top, 16.dp)
                end.linkTo(parent.end, 16.dp)
            }
        ) { Text("Action") }
    }
}
```

### 惰性列表（相当于 RecyclerView）

```kotlin
@Composable
fun LazyListDemo(items: List<String>) {
    // LazyColumn — 垂直滚动列表
    LazyColumn {
        // 单个 item
        item { Text("Header", style = MaterialTheme.typography.h6) }
        
        // 批量 item（推荐提供 key 以提高性能）
        items(
            items = items,
            key = { it }  // 稳定的 key 避免不必要的重组
        ) { item ->
            Text(
                text = item,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp)
                    .animateItem()  // item 动画
            )
        }
    }
    
    // LazyRow — 水平滚动
    LazyRow { items(items) { Text(it) } }
    
    // LazyVerticalGrid — 网格布局
    LazyVerticalGrid(
        columns = GridCells.Fixed(2)  // 或 GridCells.Adaptive(120.dp)
    ) {
        items(items) { item -> CardItem(item) }
    }
}
```

### 布局测量流程

```
┌─────────────────────────────────────┐
│  Compose 布局三阶段                   │
│                                     │
│  1. 测量 (Measure)                   │
│     └ 父节点 → 子节点：传递约束       │
│                                     │
│  2. 放置 (Layout)                    │
│     └ 子节点 → 父节点：报告尺寸       │
│                                     │
│  3. 绘制 (Draw)                      │
│     └ 在 Canvas 上绘制内容            │
└─────────────────────────────────────┘
与 View 体系的区别：Compose 仅测量一次（单次遍历）
```

---

## 七、Modifier 修饰符体系

### Modifier 链式调用

```kotlin
@Composable
fun ModifierDemo() {
    Text(
        text = "Styled Text",
        modifier = Modifier
            .padding(16.dp)        // 外间距
            .fillMaxWidth()        // 填充宽度
            .background(Color.Gray) // 背景色
            .padding(8.dp)         // 内间距
            .clickable { }         // 点击事件
            .clip(RoundedCornerShape(8.dp)) // 裁剪圆角
            .border(1.dp, Color.Blue, RoundedCornerShape(8.dp))
    )
}

// 规则：Modifier 顺序至关重要！
// 外面先应用，影响内部
```

### 常用 Modifier

```kotlin
// 尺寸
Modifier.size(48.dp)
Modifier.fillMaxWidth()
Modifier.fillMaxSize()
Modifier.widthIn(min = 100.dp, max = 200.dp)
Modifier.height(IntrinsicSize.Min)

// 间距
Modifier.padding(16.dp)
Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
Modifier.offset(x = 10.dp, y = 5.dp)

// 外观
Modifier.background(Color.White, RoundedCornerShape(8.dp))
Modifier.border(2.dp, Color.Red, CircleShape)
Modifier.clip(RoundedCornerShape(8.dp))
Modifier.shadow(elevation = 4.dp)

// 交互
Modifier.clickable { /* onClick */ }
Modifier.combinedClickable(
    onClick = {},
    onLongClick = {}
)
Modifier.draggable(/* ... */)
Modifier.scrollable(/* ... */)

// 动画
Modifier.animateContentSize()
Modifier.graphicsLayer { alpha = 0.5f }
```

### 自定义 Modifier

```kotlin
// 自定义布局 Modifier
fun Modifier.customPadding(all: Dp) = this.then(
    layout { measurable, constraints ->
        val paddingPx = all.roundToPx()
        val horizontalPadding = paddingPx * 2
        val verticalPadding = paddingPx * 2
        
        val placeable = measurable.measure(
            constraints.offset(-horizontalPadding, -verticalPadding)
        )
        
        layout(
            placeable.width + horizontalPadding,
            placeable.height + verticalPadding
        ) {
            placeable.place(paddingPx, paddingPx)
        }
    }
)

// 自定义绘制 Modifier
fun Modifier.drawCircle(color: Color) = this.then(
    drawBehind {
        drawCircle(color = color, radius = size.minDimension / 2)
    }
)
```

---

## 八、主题与样式

### Material3 主题

```kotlin
// Theme.kt
private val LightColorScheme = lightColorScheme(
    primary = Color(0xFF6200EE),
    onPrimary = Color.White,
    secondary = Color(0xFF03DAC5),
    background = Color(0xFFFFFBFE),
    surface = Color(0xFFFFFBFE),
    error = Color(0xFFB00020)
)

@Composable
fun MyAppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme
    
    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,   // 字体排版
        shapes = Shapes,           // 圆角形状
        content = content
    )
}

// 使用
@Composable
fun ThemedComponent() {
    Text(
        text = "Hello",
        style = MaterialTheme.typography.headlineMedium,
        color = MaterialTheme.colorScheme.primary
    )
    Surface(
        color = MaterialTheme.colorScheme.surface,
        shape = MaterialTheme.shapes.medium
    ) {
        // 内容
    }
}
```

### 自定义排版（Typography）

```kotlin
val AppTypography = Typography(
    displayLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Bold,
        fontSize = 32.sp,
        lineHeight = 40.sp
    ),
    headlineMedium = TextStyle(
        fontSize = 24.sp,
        fontWeight = FontWeight.SemiBold
    ),
    bodyLarge = TextStyle(
        fontSize = 16.sp,
        lineHeight = 24.sp
    ),
    labelSmall = TextStyle(
        fontSize = 11.sp,
        letterSpacing = 0.5.sp
    )
)
```

### 自定义形状（Shapes）

```kotlin
val AppShapes = Shapes(
    small = RoundedCornerShape(4.dp),   // 小按钮 / Chips
    medium = RoundedCornerShape(8.dp),  // 卡片 / Dialog
    large = RoundedCornerShape(16.dp)   // 底部 Sheet / 大容器
)
```

### 条件样式

```kotlin
@Composable
fun ConditionalStyledText(isSelected: Boolean, text: String) {
    Text(
        text = text,
        color = if (isSelected) {
            MaterialTheme.colorScheme.primary
        } else {
            MaterialTheme.colorScheme.onSurface
        },
        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
        modifier = Modifier
            .background(
                color = if (isSelected) {
                    MaterialTheme.colorScheme.primary.copy(alpha = 0.1f)
                } else {
                    Color.Transparent
                },
                shape = RoundedCornerShape(8.dp)
            )
            .padding(8.dp)
    )
}
```

---

## 九、副作用 API

副作用是在 Composable 函数作用域之外发生的操作（如网络请求、数据库操作、弹 Toast）。

### 副作用全家桶

```kotlin
// 1. LaunchedEffect — 在组合中启动协程
@Composable
fun LaunchedEffectDemo(userId: String) {
    var user by remember { mutableStateOf<User?>(null) }
    
    LaunchedEffect(key1 = userId) {
        // 当 userId 变化时，取消旧协程，启动新协程
        user = api.fetchUser(userId)
    }
    
    user?.let { UserCard(it) }
}

// 2. DisposableEffect — 需要清理的副作用
@Composable
fun DisposableEffectDemo() {
    val context = LocalContext.current
    
    DisposableEffect(Unit) {
        val observer = LifecycleEventObserver { _, event ->
            // 监听生命周期
        }
        (context as? LifecycleOwner)?.lifecycle?.addObserver(observer)
        
        onDispose {
            // 离开组合时清理
            (context as? LifecycleOwner)?.lifecycle?.removeObserver(observer)
        }
    }
}

// 3. SideEffect — 每次重组后执行（同步非挂起操作）
@Composable
fun SideEffectDemo(analytics: Analytics) {
    SideEffect {
        analytics.logScreenView("HomeScreen")
    }
}

// 4. rememberCoroutineScope — 获取组合感知的协程作用域
@Composable
fun CoroutineScopeDemo() {
    val scope = rememberCoroutineScope()
    
    Button(onClick = {
        scope.launch {
            // 在 Composable 作用域外启动协程（如点击事件中）
            doAsyncWork()
        }
    }) { Text("Start") }
}

// 5. derivedStateOf — 派生状态
@Composable
fun DerivedStateDemo(list: List<Item>) {
    val expensiveResult by remember {
        derivedStateOf {
            list.filter { it.price > 100 }.sumOf { it.price }
        }
    }
    // 仅当结果实际变化时才触发重组
    Text("Total: $expensiveResult")
}

// 6. produceState — 将非 Compose 状态转为 Compose State
@Composable
fun ProduceStateDemo(userId: String): State<User?> {
    return produceState<User?>(initialValue = null, key1 = userId) {
        value = api.fetchUser(userId)
    }
}
```

### 副作用选择指南

```
需要异步操作（协程）    → LaunchedEffect
需要清理资源            → DisposableEffect
同步通知非 Compose 代码  → SideEffect
事件处理中启动协程       → rememberCoroutineScope
避免不必要的重组         → derivedStateOf
转换外部数据到 State     → produceState
```

---

## 十、导航

### Navigation Compose 基础

```kotlin
// 添加依赖
// implementation("androidx.navigation:navigation-compose:2.7.0")

// 定义路由
object Routes {
    const val HOME = "home"
    const val DETAIL = "detail/{itemId}"
    fun detail(itemId: String) = "detail/$itemId"
}

@Composable
fun AppNavigation() {
    val navController = rememberNavController()
    
    NavHost(
        navController = navController,
        startDestination = Routes.HOME
    ) {
        composable(Routes.HOME) {
            HomeScreen(
                onItemClick = { itemId ->
                    navController.navigate(Routes.detail(itemId))
                }
            )
        }
        
        composable(
            route = Routes.DETAIL,
            arguments = listOf(navArgument("itemId") { type = NavType.StringType })
        ) { backStackEntry ->
            val itemId = backStackEntry.arguments?.getString("itemId")
            DetailScreen(itemId = itemId ?: "")
        }
    }
}
```

### 类型安全导航（推荐）

```kotlin
// Kotlin Serialization 方式
@Serializable
sealed class Route {
    @Serializable
    data object Home : Route()
    
    @Serializable
    data class Detail(val itemId: String) : Route()
}

@Composable
fun TypeSafeNavigation() {
    val navController = rememberNavController()
    
    NavHost(
        navController = navController,
        startDestination = Route.Home
    ) {
        composable<Route.Home> {
            HomeScreen(onItemClick = { itemId ->
                navController.navigate(Route.Detail(itemId))
            })
        }
        
        composable<Route.Detail> { backStackEntry ->
            val route: Route.Detail = backStackEntry.toRoute()
            DetailScreen(itemId = route.itemId)
        }
    }
}
```

### 导航与返回栈

```kotlin
// 基础导航
navController.navigate("detail/123")
navController.popBackStack()                          // 返回上一页
navController.popBackStack(Routes.HOME, false)         // 返回到 HOME
navController.navigate(Routes.HOME) {
    popUpTo(Routes.HOME) { inclusive = true }          // 清除所有回退栈
    launchSingleTop = true                             // 避免重复创建
}

// Bottom Navigation 集成
@Composable
fun BottomNavBar(navController: NavHostController) {
    val items = listOf(
        BottomNavItem("home", "Home", Icons.Default.Home),
        BottomNavItem("profile", "Profile", Icons.Default.Person)
    )
    
    NavigationBar {
        val currentRoute = navController.currentBackStackEntryAsState().value?.destination?.route
        
        items.forEach { item ->
            NavigationBarItem(
                icon = { Icon(item.icon, null) },
                label = { Text(item.label) },
                selected = currentRoute == item.route,
                onClick = {
                    navController.navigate(item.route) {
                        popUpTo(navController.graph.findStartDestination().id) {
                            saveState = true
                        }
                        launchSingleTop = true
                        restoreState = true
                    }
                }
            )
        }
    }
}
```

---

## 十一、Compose 与 View 互操作

### 在 Compose 中使用 View（AndroidView）

```kotlin
@Composable
fun MapViewComposable() {
    // 简单用法
    AndroidView(
        factory = { context ->
            MapView(context).apply {
                // 初始化操作
            }
        },
        modifier = Modifier.fillMaxSize()
    )
    
    // 需要更新时
    AndroidView(
        factory = { context -> MapView(context) },
        update = { mapView ->
            // 当 Compose 状态变化时，更新 View
            mapView.setLocation(lat, lng)
        },
        modifier = Modifier.fillMaxSize()
    )
}

// WebView 示例
@Composable
fun WebViewComposable(url: String) {
    AndroidView(
        factory = { context ->
            WebView(context).apply {
                settings.javaScriptEnabled = true
                loadUrl(url)
            }
        },
        update = { webView ->
            webView.loadUrl(url)
        }
    )
}
```

### 在 View 中使用 Compose（ComposeView）

```kotlin
// 在 Activity 中
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        setContent {
            MyAppTheme {
                MainScreen()
            }
        }
    }
}

// 在 Fragment 中
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return ComposeView(requireContext()).apply {
            setContent {
                MyAppTheme {
                    FragmentContent()
                }
            }
        }
    }
}

// 在 XML 布局中内嵌 Compose
// <androidx.compose.ui.platform.ComposeView
//     android:id="@+id/composeView"
//     android:layout_width="match_parent"
//     android:layout_height="wrap_content" />
findViewById<ComposeView>(R.id.composeView).setContent {
    MyComposableContent()
}
```

### 互操作注意事项

```
✅ DO:
  - 将 Compose 视为 View 的升级替代
  - 使用 AndroidView 包裹复杂的原生 View
  - 逐步迁移，而非一次性重写

❌ DON'T:
  - 在同一个组件中混合大量 View 和 Compose
  - 在 Compose 重组中频繁创建 AndroidView
  - 忽略生命周期管理
```

---

## 十二、常见问题与最佳实践

### 最佳实践清单

#### 1. 状态管理
```kotlin
// ✅ 好的做法：使用 ViewModel + StateFlow
class MainViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(MainUiState())
    val uiState: StateFlow<MainUiState> = _uiState.asStateFlow()
    
    fun onAction(action: MainAction) { /* ... */ }
}

@Composable
fun MainScreen(viewModel: MainViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    // 渲染 UI
}

// ❌ 避免：在 Composable 中做网络请求
// @Composable
// fun BadScreen() {
//     val data = api.fetchData() // 每次重组都会触发请求！
// }
```

#### 2. 稳定性优化
```kotlin
// ✅ 给数据类添加 @Stable 或 @Immutable 注解
@Immutable
data class User(
    val id: String,
    val name: String,
    val avatar: String
)

// ✅ 对 Lambda 使用 remember
@Composable
fun StableLambdaDemo(onEvent: () -> Unit) {
    val stableOnEvent = remember { onEvent }
    Button(onClick = stableOnEvent) { Text("Click") }
}

// ❌ 不要传递不稳定的参数（如未注解的 data class）
```

#### 3. 列表性能
```kotlin
// ✅ 提供稳定的 key
LazyColumn {
    items(
        items = users,
        key = { user -> user.id }  // 关键！
    ) { user ->
        UserItem(user)
    }
}

// ✅ 避免在 item 中创建 Modifier 对象（提取到 remember）
@Composable
fun UserItem(user: User) {
    val modifier = remember { Modifier.padding(16.dp) }
    Text(user.name, modifier = modifier)
}
```

#### 4. 避免不必要的重组
```kotlin
// ✅ 使用 derivedStateOf 过滤
@Composable
fun FilteredList(items: List<String>, query: String) {
    val filtered by remember(query) {
        derivedStateOf {
            items.filter { it.contains(query, ignoreCase = true) }
        }
    }
    LazyColumn { items(filtered) { Text(it) } }
}

// ✅ 将不需要重组的部分提取到独立 Composable
@Composable
fun ExpensiveParent() {
    val state by viewModel.state.collectAsState()
    
    Column {
        Text(state.title)           // 需要重组
        StaticHeavyContent()        // 不需要重组，被跳过
    }
}
```

#### 5. 预览与调试
```kotlin
// 多预览
@Preview(name = "Light Mode", showBackground = true)
@Preview(name = "Dark Mode", uiMode = Configuration.UI_MODE_NIGHT_YES, showBackground = true)
@Preview(name = "Large Font", fontScale = 1.5f)
@Composable
fun MyComponentPreview() {
    MyAppTheme {
        MyComponent(title = "Preview Title")
    }
}

// 使用 @PreviewParameter 批量测试
@Preview
@Composable
fun ListPreview(
    @PreviewParameter(UserPreviewProvider::class) users: List<User>
) {
    UserList(users = users)
}
```

### 常见坑与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 状态丢失（配置变更） | 未使用 ViewModel | 使用 `viewModel()` 获取 |
| 无限重组循环 | 在组合中修改状态 | 将状态修改移到 `LaunchedEffect` 或事件回调中 |
| LazyColumn 滚动位置丢失 | item key 不稳定 | 提供稳定的 key（如 id） |
| Modifier 顺序导致效果异常 | Modifier 链顺序错误 | 理解 padding/background 等顺序含义 |
| SideEffect 执行多次 | 未指定 key | 为 `LaunchedEffect` 指定正确的 key |
| Preview 不显示 | 缺少 Theme 包裹 | 在 Preview 中包裹 `MyAppTheme { }` |
| 性能问题 | 大量不必要的重组 | 使用 Layout Inspector 定位，添加 `@Stable` 注解 |

### 推荐 Compose 技术栈

```
📦 核心：
  - Jetpack Compose UI       → 声明式 UI 框架
  - Compose Material3        → Material Design 3 组件
  - Compose Foundation       → 基础布局与手势

🏗️ 架构：
  - ViewModel                → 状态持有者
  - Navigation Compose       → 导航
  - Hilt                     → 依赖注入

🌐 网络：
  - Retrofit + OkHttp        → HTTP 客户端
  - kotlinx.serialization    → JSON 序列化

💾 本地存储：
  - Room                     → 数据库
  - DataStore                → 键值存储

🖼️ 图片加载：
  - Coil                     → 图片加载（Compose 原生支持）

🧪 测试：
  - Compose UI Test          → UI 测试
  - Turbine                  → Flow 测试
  - MockK / Mockito          → 单元测试 Mock
```

---

## 总结

Jetpack Compose 的核心思想是**声明式 UI = f(State)**。它彻底改变了 Android UI 开发方式：

1. **声明式 > 命令式** → 描述 UI "是什么"，而非 "怎么做"
2. **状态驱动** → State 是唯一真相来源，UI 自动响应变化
3. **Kotlin 原生** → 充分利用 Kotlin 语言的所有特性
4. **渐进式采用** → 与 View 体系无缝共存，逐步迁移

记住 Compose 的核心原则：

> **UI 是状态的函数。用声明式思维描述 UI，让框架处理更新逻辑。**

而从 KMP 的角度来看，Jetpack Compose 是 Android 侧的原生 UI 方案，同时 Compose Multiplatform 也让它具备了跨平台能力，两者相辅相成，是 Kotlin 生态中 UI 开发的现在与未来。
