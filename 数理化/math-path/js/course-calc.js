/* MathPath — 甲种本《微积分初步》（按真实章节分单元） */
(function () {
  'use strict';
  var MP = window.MathPath, U = MP.util, S = U.step;
  function row(s, cls) { return { cells: String(s).split('').map(function (c) { return { t: c, cls: cls || '' }; }) }; }
  function st(arr, cap) {
    return { view: 'steps', lines: arr.map(function (a) { return typeof a === 'string' ? row(a) : a; }), caption: cap || '' };
  }
  function ax(r, x) { var o = { view: 'axis', range: r }; for (var k in x) o[k] = x[k]; return o; }
  function gr(cols, rows, cells, cap, w) { return { view: 'grid', cols: cols, rows: rows, cells: cells, cellW: w || 60, caption: cap || '' }; }
  function br(values, labels, marks, cap) { return { view: 'bars', values: values, labels: labels, marks: marks || {}, caption: cap || '' }; }
  function curve(f, a, b, n) {
    var p = [], k = n || 50;
    for (var i = 0; i <= k; i++) { var x = a + (b - a) * i / k; p.push([x, U.round(f(x), 4)]); }
    return p;
  }
  function line(a, b, cls, label) { return { a: a, b: b, cls: cls || '', label: label || '' }; }
  function pt(x, y, label, cls) { return { x: x, y: y, label: label || '', cls: cls || '' }; }
  function T(o) { o.view = 'steps'; MP.registerTopic(o); }

  MP.registerUnits([
    { id: 'ca-c1', track: 'bridge', book: 'calc', name: '第一章 极限' },
    { id: 'ca-c2', track: 'bridge', book: 'calc', name: '第二章 导数和微分' },
    { id: 'ca-c3', track: 'bridge', book: 'calc', name: '第三章 导数的应用' },
    { id: 'ca-c4', track: 'bridge', book: 'calc', name: '第四章 不定积分' },
    { id: 'ca-c5', track: 'bridge', book: 'calc', name: '第五章 定积分及其应用' }
  ]);

  /* ================= 第一章 极限 ================= */
  T({
    id: 'ca-seq-limit', unit: 'ca-c1', title: '数列的极限', subtitle: '把「越来越接近」写成严格的数学语言',
    goal: '理解 ε−N 定义、收敛与发散，会求简单数列极限',
    why: '《微积分初步》第一章（p1 起，含 1.2「数列极限的四则运算」、无穷等比数列各项的和、例 5「循环小数化分数」）是整本书的地基。',
    minutes: 13, star: true, prereq: ['a2-seq-geom', 'p-approx'],
    demo: function () {
      var o = [];
      o.push(S('看数列 <b>aₙ = 1/n</b>：1, 1/2, 1/3, 1/4, … 越来越接近 0。',
        br([100, 50, 33, 25, 20], ['n=1', 'n=2', 'n=3', 'n=4', 'n=5'], { done: [4] }, '数值已乘 100 便于显示')));
      o.push(S('小学只能说「越来越近」。极限要回答：<b>要有多近，就能有多近</b>。',
        st(['给定任意小的 ε > 0', '总能找到 N，使 n > N 时 |aₙ − 0| < ε', '则称 lim aₙ = 0'])));
      o.push(S('几何上看：任给一条宽度为 2ε 的带子，数列从第 N 项起全部落在带子内。',
        ax({ x: [0, 12], y: [-0.5, 1.2] }, { curves: [
          { pts: (function () { var p = []; for (var n = 1; n <= 12; n++) p.push([n, U.round(1 / n, 4)]); return p; })(), cls: 'is-dim' }
        ], rects: [{ x: 0, y: -0.2, w: 12, h: 0.4, cls: 'is-hi', label: '|aₙ| < 0.2' }],
          caption: 'ε = 0.2 时，n ≥ 6 之后的点都在带内' })));
      o.push(S('常用结论：lim(1/n)=0；lim qⁿ = 0（|q|&lt;1）；常数数列极限是它本身。',
        st(['收敛：极限存在且有限', '发散：如 n² → ∞，或 (−1)ⁿ 来回摆动', '无穷递缩等比数列之和就是级数求和的雏形'])));
      o.push(S('极限的四则运算（课本 1.2）：和差积商的极限等于极限的和差积商（分母极限不为 0）。',
        st(['lim(1/n + 1/n²) = 0 + 0 = 0', '注意 ∞/∞、0/0 要先化简'])));
      o.push(S('课本接着定义<b>无穷等比数列各项的和</b>，并用它把循环小数化成分数（例 4、例 5）。',
        st(['0.3 + 0.03 + 0.003 + … = 0.333… = 1/3', 'S = a₁/(1−q)，要求 |q| < 1', '例 5：把循环小数化成分数', '这是极限在代数里的第一个实际应用'], '甲种本把「无限项相加」放在极限章，而非数列章')));
      return o;
    },
    notes: [
      '<p>ε−N 定义的精髓是「先给精度，再找项数」：不是逼近到某一步停，而是任意精度都能保证。</p>',
      '<p>这与小学的「四舍五入」和初中「√2 夹逼」是同一条直觉，只是把误差界说清楚了。</p>',
      '<p>下一节函数极限、第二章导数定义，全都是这个 ε 语言的重复使用。</p>'
    ],
    example: { q: '求 lim (2n+1)/(3n−1)', steps: ['分子分母同除以 n', '= (2 + 1/n)/(3 − 1/n)'], a: '2/3' },
    quiz: [
      { q: 'lim (1/n) = ?', options: ['0', '1', '∞', '不存在'], answer: 0, explain: 'n 越大，1/n 越接近 0。' },
      { q: '|q|<1 时 lim qⁿ = ?', options: ['0', '1', 'q', '发散'], answer: 0, explain: '几何衰减趋于 0，也是无穷递缩和的前提。' }
    ]
  });

  T({
    id: 'ca-func-limit', unit: 'ca-c1', title: '函数的极限与连续性', subtitle: 'x 趋近某点时，f(x) 趋近什么',
    goal: '掌握左右极限、连续性、两个重要极限',
    why: '《微积分初步》第一章「极限」，是导数定义前的最后一步。',
    minutes: 13, star: true, prereq: ['ca-seq-limit', 'a1-trig-graph'],
    demo: function () {
      var o = [];
      o.push(S('记 <b>lim(x→x₀) f(x) = A</b>：x 从两侧趋近 x₀ 时 f(x) 趋近 A，与 f(x₀) 本身取什么值无关。',
        ax({ x: [-3, 5], y: [-2, 6] }, { curves: [
          { pts: curve(function (x) { return x + 1; }, -3, 2, 40), cls: '', label: 'f(x)=x+1' },
          { pts: curve(function (x) { return x + 1; }, 2, 5, 20), cls: '' }
        ], points: [pt(2, 3, '空心 (2,3)', 'is-hi'), pt(2, 5, 'f(2)=5', 'is-on')],
          caption: '极限只看趋近过程，不看该点取值' })));
      o.push(S('左右极限相等，极限才存在；三者都等于 f(x₀) 时函数在该点<b>连续</b>。',
        st(['lim(x→x₀⁻) f = lim(x→x₀⁺) f = A', '连续：A = f(x₀)', '分段函数在分界点要特别检查'])));
      o.push(S('第一个重要极限：<b>lim(x→0) sin x / x = 1</b>。用单位圆夹逼可得。',
        ax({ x: [-4, 4], y: [-0.3, 1.3] }, { curves: [
          { pts: curve(function (x) { return Math.sin(x) / x; }, -4, -0.05, 60), cls: '' },
          { pts: curve(function (x) { return Math.sin(x) / x; }, 0.05, 4, 60), cls: '' }
        ], caption: 'x→0 时曲线趋近 y=1' })));
      o.push(S('第二个重要极限：<b>lim(n→∞) (1+1/n)ⁿ = e ≈ 2.71828</b>。',
        st(['n=1: 2      n=10: 2.594', 'n=100: 2.705   n→∞: e', '自然对数 ln 与指数函数 eˣ 由此而来'])));
      o.push(S('无穷小的比较：若 lim(α/β)=0，则 α 是比 β 更高阶的无穷小；这是求导数时舍弃高阶项的语言。',
        st(['x→0 时，x² 比 x 更快趋于 0', '1 − cos x ~ x²/2', '「略去高阶无穷小」是微分近似的核心'])));
      return o;
    },
    notes: [
      '<p>函数极限与数列极限的差别：自变量是连续趋近而非只取整数，需要区分左右两侧。</p>',
      '<p>两个重要极限分别给出三角函数与指数函数在 0 附近的局部行为，是求导公式的来源。</p>',
      '<p>第二章导数定义就是 0/0 型极限：分子分母同时趋于 0，必须先化简再取极限。</p>'
    ],
    example: { q: '求 lim(x→2) (x²−4)/(x−2)', steps: ['直接代入得 0/0，先因式分解', '(x²−4)/(x−2) = x+2（x≠2）'], a: '4' },
    quiz: [
      { q: 'lim(x→0) sin x / x = ?', options: ['0', '1', '∞', 'x'], answer: 1, explain: '第一个重要极限。' },
      { q: '函数在 x₀ 连续需要？', options: ['极限存在', 'f(x₀) 有定义', '极限 = f(x₀)', '三者都要'], answer: 3, explain: '三个条件缺一不可。' }
    ]
  });

  /* ================= 第二章 导数和微分 ================= */
  T({
    id: 'ca-deriv-concept', unit: 'ca-c2', title: '导数的概念', subtitle: '课本用自由落体引入，再给出求导三步法',
    goal: '按课本顺序理解瞬时速度、求导三步法、导函数与切线斜率',
    why: '《微积分初步》第二章「一 导数概念」（p52）：课本由自由落体 s=½gt² 在 t=3 的瞬时速度引入，给出「求改变量→求比→求极限」三步法与例 1。',
    minutes: 14, star: true, prereq: ['ca-func-limit', 'm-linear-fn', 'm-quad-fn'],
    demo: function () {
      var o = [];
      o.push(S('课本从<b>瞬时速度</b>引入：自由落体 s = ½gt²，求 t = 3 秒时的速度。先算一小段时间内的平均速度。',
        st(['时间间隔从 3 到 3+Δt', 'Δs = ½g(3+Δt)² − ½g·3²', '平均速度 = Δs / Δt', '令 Δt→0，得 v = 3g = 29.4 米/秒'], '课本 p52 的引入方式：物理问题 → 极限')));
      o.push(S('把这个做法抽象出来，课本由导数定义直接给出<b>求导三步法</b>：',
        st(['1. 求改变量  Δy = f(x₀+Δx) − f(x₀)', '2. 求比      Δy / Δx', '3. 求极限  lim(Δx→0) Δy / Δx'], '这三步是本章所有求导计算的标准流程')));
      o.push(S('课本例 1：求 <b>y = x² 在点 x = 1 处的导数</b>。',
        st(['Δy = (1+Δx)² − 1² = 2Δx + (Δx)²', 'Δy / Δx = 2 + Δx', 'lim(Δx→0) (2+Δx) = 2', '∴ y′|x=1 = 2'])));
      o.push(S('若函数在开区间 (a,b) 内每一点都可导，就说它在 (a,b) 内可导；每个 x 对应一个 f′(x)，构成的新函数叫<b>导函数</b>。',
        st(['导函数记为 f′(x) 或 y′', '必要指明自变量时记作 y′ₓ', '由导数定义即可得出各基本函数的导函数'])));
      o.push(S('几何意义：f′(x₀) 是曲线在该点<b>切线的斜率</b>。割线斜率随 Δx→0 趋近它。',
        ax({ x: [-1, 4], y: [-1, 9] }, { curves: [
          { pts: curve(function (x) { return x * x; }, -0.5, 3, 50), cls: '' }
        ], points: [pt(1, 1, 'P(1,1)', 'is-hi')], lines: [
          line([1, 1], [2.5, 6.25], 'is-dim'), line([1, 1], [2, 4], 'is-dim'),
          line([-0.5, -2], [3, 3], 'is-hi', '切线 y=2x−1')
        ], caption: '割线斜率 3.5 → 3 → … → 2，与例 1 结果一致' })));
      o.push(S('可导必连续，连续不一定可导（如 y=|x| 在 x=0 有尖角）。',
        ax({ x: [-3, 3], y: [-1, 4] }, { curves: [
          { pts: [[-3, 3], [0, 0], [3, 3]], cls: 'is-hi', label: 'y=|x|' }
        ], points: [pt(0, 0, '尖角', 'is-on')], caption: '左右导数不相等 ⇒ 不可导' })));
      return o;
    },
    notes: [
      '<p>课本的次序是「物理问题（瞬时速度）→ 抽象成三步法 → 例题 → 导函数 → 几何意义」，不是一上来就讲切线。</p>',
      '<p>三步法里最关键的是第 2 步化简差商：不先化简，第 3 步就是 0/0 型极限，无法直接代入。</p>',
      '<p>下一节把三步法对各类函数各算一遍，得到求导公式表；第三章用 f′ 判断单调与极值。</p>'
    ],
    example: { q: '按课本三步法求 y=x² 在 x=2 处的导数', steps: ['Δy = (2+Δx)² − 4 = 4Δx + (Δx)²', 'Δy/Δx = 4 + Δx', 'lim(Δx→0) (4+Δx) = 4'], a: '4' },
    quiz: [
      { q: '课本例 1 中 y=x² 在 x=1 处的导数是？', options: ['1', '2', '3', '4'], answer: 1, explain: 'Δy/Δx = 2+Δx，取极限得 2。' },
      { q: '课本给出的求导三步法顺序是？', options: ['求极限→求比→求改变量', '求改变量→求比→求极限', '求比→求导→求极限', '求改变量→求导→代入'], answer: 1, explain: 'p52 明确列出：1.求改变量 2.求比 3.求极限。' },
      { q: '可导与连续的关系是？', options: ['连续必可导', '可导必连续', '等价', '无关'], answer: 1, explain: '可导 ⇒ 连续，反之不成立。' }
    ]
  });

  T({
    id: 'ca-deriv-rules', unit: 'ca-c2', title: '求导方法与基本公式', subtitle: '不必每次都用定义，用公式表即可',
    goal: '掌握四则运算求导法则与基本初等函数导数表',
    why: '《微积分初步》第二章（p69 起）：2.5 几种常见函数的导数、2.7 复合函数的导数、2.8 三角函数的导数、2.14 二阶导数。',
    minutes: 13, star: true, prereq: ['ca-deriv-concept', 'm-frac-expr'],
    demo: function () {
      var o = [];
      o.push(S('基本导数表（由定义推一次，之后直接查用）：',
        gr(2, 4, [
          { v: "(c)' = 0", cls: 'is-on' }, { v: "(xⁿ)' = n xⁿ⁻¹", cls: 'is-on' },
          { v: "(sin x)' = cos x", cls: 'is-on' }, { v: "(cos x)' = −sin x", cls: 'is-on' },
          { v: "(eˣ)' = eˣ", cls: 'is-hi' }, { v: "(ln x)' = 1/x", cls: 'is-hi' },
          { v: "(aˣ)' = aˣ ln a", cls: 'is-done' }, { v: "(logₐx)' = 1/(x ln a)", cls: 'is-done' }], '', 150)));
      o.push(S('四则运算法则：',
        st(['(u ± v)′ = u′ ± v′', '(uv)′ = u′v + uv′', '(u/v)′ = (u′v − uv′)/v²  (v≠0)', '常数可以提出： (cf)′ = c f′'])));
      o.push(S('例：求 f(x) = x³ + 2sin x − ln x 的导数。',
        st(['f′(x) = 3x² + 2cos x − 1/x', '逐项求导再相加，靠的是导数的线性性'])));
      o.push(S('商的导数分母是 v²，分子是「上导下不导 减 上不导下导」，顺序不能反。',
        st(['(x²/(x+1))′ = (2x(x+1) − x²)/(x+1)²', '= (x² + 2x)/(x+1)²'])));
      o.push(S('课本 2.8 节单列<b>三角函数的导数</b>：它们由第一个重要极限 lim(x→0) sin x / x = 1 推得。',
        st(["(sin x)′ = lim[sin(x+h) − sin x]/h = cos x", '(cos x)′ = −sin x', '(tg x)′ = 1/cos²x  （甲种本用 tg）', '2.14 节再把导数求一次得二阶导数'], '2.7 复合、2.8 三角、2.14 二阶是本章三个专节')));
      return o;
    },
    notes: [
      '<p>求导是「局部线性」运算：加减直接拆，乘积与商要多出交叉项，别漏掉。</p>',
      '<p>基本公式表要熟到不假思索；复合函数与隐函数只是再套一层链式法则。</p>',
      '<p>第三章用 f′ 的符号判断单调性，第四章不定积分是这张表的「反向查表」。</p>'
    ],
    example: { q: '求 (x²·sin x)′', steps: ['套乘积法则 u′v + uv′', 'u=x², v=sin x'], a: '2x sin x + x² cos x' },
    quiz: [
      { q: "(x⁴)' = ?", options: ['4x³', 'x³', '4x⁴', 'x⁵/5'], answer: 0, explain: '幂函数求导公式。' },
      { q: "(sin x)' = ?", options: ['−sin x', 'cos x', '−cos x', 'tan x'], answer: 1, explain: '正弦的导数是余弦。' }
    ]
  });

  T({
    id: 'ca-chain', unit: 'ca-c2', title: '复合函数求导与高阶导数', subtitle: '一层套一层，就一层一层乘',
    goal: '掌握链式法则、隐函数与二阶导数',
    why: '《微积分初步》第二章「二 求导方法」及 *第三章「二 二阶导数的应用」。',
    minutes: 13, prereq: ['ca-deriv-rules'],
    demo: function () {
      var o = [];
      o.push(S('若 y = f(u)、u = g(x)，则 <b>dy/dx = f′(u)·g′(x)</b>，即链式法则。',
        st(['y = sin(x²)', '外层 sin u 的导数 cos u', '内层 x² 的导数 2x', 'y′ = cos(x²)·2x'])));
      o.push(S('可以理解为「变化率相乘」：x 变一点 → u 变 g′ 倍 → y 再变 f′ 倍。',
        ax({ x: [-3, 3], y: [-1.5, 1.5] }, { curves: [
          { pts: curve(function (x) { return Math.sin(x * x); }, -2.5, 2.5, 90), cls: 'is-hi', label: 'sin(x²)' }
        ], caption: '振荡越来越快，因为内层导数 2x 在增大' })));
      o.push(S('常用形式：(f(ax+b))′ = a f′(ax+b)；(uⁿ)′ = n uⁿ⁻¹ u′。',
        st(['(e^(3x))′ = 3e^(3x)', '(ln(2x+1))′ = 2/(2x+1)', '((x²+1)⁵)′ = 5(x²+1)⁴·2x'])));
      o.push(S('二阶导数是对导数再求一次导：<b>f″(x) = (f′(x))′</b>。',
        st(['f(x)=x³ → f′=3x² → f″=6x', '物理上：位移 → 速度 → 加速度', 'f″>0 曲线下凸（凹向上），f″<0 上凸'])));
      return o;
    },
    notes: [
      '<p>链式法则的关键是分清「外层函数」与「内层函数」，漏乘内层导数是最高频错误。</p>',
      '<p>复合层数不限，逐层剥开逐层相乘即可；隐函数求导本质也是链式法则加方程两边同求导。</p>',
      '<p>*二阶导数用于判断凹凸与拐点；甲种本把它列为选学，但物理意义（加速度）很好懂。</p>'
    ],
    example: { q: '求 y = (2x+1)⁴ 的导数', steps: ['外层 u⁴ → 4u³', '内层 u=2x+1 → u′=2'], a: '8(2x+1)³' },
    quiz: [
      { q: 'y = sin(3x) 的导数是？', options: ['cos(3x)', '3cos(3x)', '−3cos(3x)', '3sin(3x)'], answer: 1, explain: '链式法则要乘内层导数 3。' },
      { q: 'f(x)=x³ 的二阶导数是？', options: ['3x²', '6x', '6', 'x'], answer: 1, explain: 'f′=3x²，f″=6x。' }
    ]
  });

  T({
    id: 'ca-differential', unit: 'ca-c2', title: '微分与线性近似', subtitle: '用切线代替曲线，算一小段变化',
    goal: '理解 dy = f′(x)dx，会用微分做近似计算与误差估计',
    why: '《微积分初步》第二章「三 微分」（p107）及《代数 第一册》附录 I「近似计算的法则」。',
    minutes: 12, prereq: ['ca-deriv-rules', 'p-approx'],
    demo: function () {
      var o = [];
      o.push(S('当 Δx 很小时，曲线在 P 附近几乎就是切线：函数增量可用切线上的增量近似。',
        ax({ x: [-0.5, 3], y: [-1, 9] }, { curves: [
          { pts: curve(function (x) { return x * x; }, -0.5, 3, 50), cls: '' }
        ], points: [pt(1, 1, 'P', 'is-hi'), pt(1.5, 2.25, '曲线', 'is-on')],
          lines: [line([0.5, 0], [2.5, 3], 'is-hi', '切线 y=2x−1')],
          caption: '在 P 附近，切线与曲线几乎重合' })));
      o.push(S('把自变量增量记作 dx，则<b>微分 dy = f′(x) dx</b>，而 Δy = dy + 高阶无穷小。',
        st(['Δy = f(x+Δx) − f(x)', 'dy = f′(x)Δx', 'Δy ≈ dy（误差是比 Δx 更高阶的无穷小）'])));
      o.push(S('例：求 √4.01 的近似值。取 f(x)=√x、x=4、dx=0.01。',
        st(["f′(x) = 1/(2√x) ⇒ f′(4) = 1/4", 'dy = (1/4)(0.01) = 0.0025', '√4.01 ≈ 2 + 0.0025 = 2.0025'])));
      o.push(S('误差估计：|Δy − dy| 与 dx² 同阶，所以 dx 越小近似越好。',
        st(['这正是附录 I「近似计算的法则」的理论依据', '工程上大量测量误差都这样估计'])));
      return o;
    },
    notes: [
      '<p>微分就是「局部线性化」：在足够小的范围内，任何光滑曲线都可以当成直线来处理。</p>',
      '<p>dy 与 Δy 的差是高阶无穷小，这就是为什么近似公式在 dx 很小时非常准。</p>',
      '<p>微积分初步第三章的极值判断、第五章的定积分（把每段看成矩形），都是同一思想的不同用法。</p>'
    ],
    example: { q: '用微分估算 (1.02)³', steps: ['f(x)=x³, f′(1)=3', 'dy = 3×0.02 = 0.06'], a: '≈ 1.06（精确值 1.061208）' },
    quiz: [
      { q: 'dy 等于？', options: ['f(x)dx', "f'(x)dx", 'Δy', "f''(x)dx"], answer: 1, explain: '微分是导数乘以自变量增量。' },
      { q: '微分近似在什么时候最准？', options: ['dx 很大', 'dx 很小', '任意', '函数为常数时'], answer: 1, explain: '误差是高阶无穷小，dx 越小越准。' }
    ]
  });

  /* ================= 第三章 导数的应用 ================= */
  T({
    id: 'ca-deriv-apply', unit: 'ca-c3', title: '一阶导数的应用：单调与极值', subtitle: 'f′ 的正负，就是函数的上坡下坡',
    goal: '会用导数判断单调区间、求极值与闭区间最值',
    why: '《微积分初步》第三章「一 一阶导数的应用」(p127)、*「二 二阶导数的应用」(p156)。',
    minutes: 14, star: true, prereq: ['ca-deriv-rules', 'a2-amgm'],
    demo: function () {
      var f = function (x) { return x * x * x - 3 * x; };
      var o = [];
      o.push(S('定理：<b>f′(x) &gt; 0 ⇒ 递增；f′(x) &lt; 0 ⇒ 递减</b>。',
        ax({ x: [-3, 3], y: [-4, 4] }, { curves: [
          { pts: curve(f, -2.2, 2.2, 70), cls: '', label: 'f(x)=x³−3x' }
        ], points: [pt(-1, 2, '极大', 'is-hi'), pt(1, -2, '极小', 'is-on')],
          caption: '上坡 → 峰 → 下坡 → 谷 → 上坡' })));
      o.push(S('令 f′(x)=0 求<b>驻点</b>：3x²−3=0 ⇒ x=±1，它们把定义域分成三段。',
        st(['f′(x) = 3x² − 3 = 3(x−1)(x+1)', 'x < −1：f′ > 0 递增', '−1 < x < 1：f′ < 0 递减', 'x > 1：f′ > 0 递增'])));
      o.push(S('在 x=−1 处 f′ 由正变负 ⇒ 极大值 f(−1)=2；x=1 处由负变正 ⇒ 极小值 f(1)=−2。',
        gr(1, 3, [
          { v: '+ → −  极大', cls: 'is-on' }, { v: '− → +  极小', cls: 'is-on' },
          { v: '不变号  非极值', cls: 'is-hi' }], '关键看是否变号，而不只是 f′=0', 145)));
      o.push(S('闭区间上求最值：把驻点与<b>端点</b>的函数值都算出来比较。',
        st(['在 [−2, 2] 上：f(−2)=−2, f(−1)=2, f(1)=−2, f(2)=2', '最大值 2，最小值 −2', '端点最容易被漏掉'])));
      o.push(S('*二阶导数：f″(x₀)&gt;0 且在驻点 ⇒ 极小；f″&lt;0 ⇒ 极大；f″=0 的点可能是拐点。',
        st(['f″(x) = 6x，x=1 时 6>0 ⇒ 极小 ✓', 'x=−1 时 −6<0 ⇒ 极大 ✓', '凹凸性由 f″ 的符号决定'])));
      return o;
    },
    notes: [
      '<p>导数符号表是解这类题的标准工具：先求驻点，再分区间判号，最后看变号方向。</p>',
      '<p>f′=0 只是极值的必要条件（可导时），不充分；f(x)=x³ 在 x=0 导数为 0 但不是极值。</p>',
      '<p>甲种本代数2 用均值不等式求的最值，这里用导数得到了更一般的方法；物理里的最大射程、最省材料同理。</p>'
    ],
    example: { q: '求 f(x)=x²−4x+3 的极小值', steps: ["f'(x)=2x−4=0 ⇒ x=2", 'f′ 由负变正'], a: 'x=2 处极小值 −1' },
    quiz: [
      { q: "f'(x)>0 说明函数在该区间？", options: ['递增', '递减', '取极值', '连续但不一定可导'], answer: 0, explain: '导数为正即上坡。' },
      { q: '闭区间求最值时必须比较？', options: ['只有驻点', '只有端点', '驻点与端点', '只看 f″'], answer: 2, explain: '端点常常就是最值点。' }
    ]
  });

  /* ================= 第四章 不定积分 ================= */
  T({
    id: 'ca-indef-integral', unit: 'ca-c4', title: '不定积分与原函数', subtitle: '求导的逆运算，答案带一个常数 C',
    goal: '理解原函数、不定积分，会用基本积分表与线性性',
    why: '《微积分初步》第四章「不定积分」（p181）及附表「简易积分表」。',
    minutes: 13, star: true, prereq: ['ca-deriv-rules', 'a2-complex'],
    demo: function () {
      var o = [];
      o.push(S('若 F′(x) = f(x)，则 F 叫 f 的一个<b>原函数</b>；全体原函数写成 <b>∫f(x)dx = F(x) + C</b>。',
        st(["(x³)' = 3x²", '⇒ ∫3x² dx = x³ + C', '常数 C 不能漏：任意常数求导都是 0'])));
      o.push(S('基本积分表就是导数表反过来读：',
        gr(2, 4, [
          { v: '∫xⁿ dx = xⁿ⁺¹/(n+1)+C', cls: 'is-on' }, { v: '∫1/x dx = ln|x|+C', cls: 'is-on' },
          { v: '∫eˣ dx = eˣ + C', cls: 'is-on' }, { v: '∫aˣ dx = aˣ/ln a + C', cls: 'is-on' },
          { v: '∫sin x dx = −cos x + C', cls: 'is-hi' }, { v: '∫cos x dx = sin x + C', cls: 'is-hi' },
          { v: '∫k f dx = k∫f dx', cls: 'is-done' }, { v: '∫(f+g) = ∫f + ∫g', cls: 'is-done' }], '', 150)));
      o.push(S('线性性：和的积分等于积分的和，常数可提出。逐项积分即可。',
        st(['∫(3x² + 2x + 1)dx', '= x³ + x² + x + C'])));
      o.push(S('两类常用技巧：<b>换元积分</b>（凑微分，链式法则反过来）、<b>分部积分</b>（乘积法则反过来）。',
        st(['∫2x cos(x²)dx：令 u=x², du=2x dx', '= ∫cos u du = sin u + C = sin(x²)+C', '分部：∫u dv = uv − ∫v du'])));
      o.push(S('验算永远是最低成本的检查：把结果求导，看能不能回到被积函数。',
        st(['(sin(x²)+C)′ = 2x cos(x²) ✓', '这就是甲种本附表「简易积分表」的用法'])));
      return o;
    },
    notes: [
      '<p>不定积分是一族函数而不是一个函数，因为求导会丢掉常数信息。</p>',
      '<p>换元与分部不是新技巧，分别是链式法则和乘积法则的逆用；凑微分时先找「内层函数的导数」。</p>',
      '<p>第五章定积分用 F(b)−F(a) 计算，因此求原函数是整个积分学的计算核心。</p>'
    ],
    example: { q: '求 ∫(2x + 3)dx', steps: ['逐项积分：x² + 3x', '加常数'], a: 'x² + 3x + C' },
    quiz: [
      { q: '∫2x dx = ?', options: ['x²', 'x² + C', '2 + C', '2x² + C'], answer: 1, explain: '原函数是 x²，别漏常数 C。' },
      { q: '∫cos x dx = ?', options: ['sin x + C', '−sin x + C', '−cos x + C', 'tan x + C'], answer: 0, explain: '(sin x)′ = cos x。' }
    ]
  });

  /* ================= 第五章 定积分及其应用 ================= */
  T({
    id: 'ca-def-integral', unit: 'ca-c5', title: '定积分与牛顿—莱布尼茨公式', subtitle: '无限多个窄矩形之和，等于原函数在端点的差',
    goal: '理解黎曼和、定积分定义与微积分基本定理',
    why: '《微积分初步》第五章「一 定积分的概念和计算」（p213）。',
    minutes: 14, star: true, prereq: ['ca-indef-integral', 'p-area-rect'],
    demo: function () {
      function rects(n) {
        var out = [], a = 0, b = 3, dx = (b - a) / n;
        for (var i = 0; i < n; i++) {
          var x = a + i * dx;
          out.push({ x: x, y: 0, w: U.round(dx, 4), h: U.round(x * x / 2, 4), cls: '' });
        }
        return out;
      }
      var o = [];
      o.push(S('求 y = x²/2 在 [0,3] 下方面积：把区间切成 n 个窄条，每条用矩形近似。',
        ax({ x: [-0.3, 3.3], y: [-0.3, 5] }, { curves: [
          { pts: curve(function (x) { return x * x / 2; }, 0, 3, 50), cls: 'is-hi' }
        ], rects: rects(6), caption: 'n = 6，矩形面积之和还明显偏小' })));
      o.push(S('把 n 加大到 12、24……矩形越来越贴合曲线，和趋于一个确定的数。',
        ax({ x: [-0.3, 3.3], y: [-0.3, 5] }, { curves: [
          { pts: curve(function (x) { return x * x / 2; }, 0, 3, 50), cls: 'is-hi' }
        ], rects: rects(16), caption: 'n = 16，误差显著变小' })));
      o.push(S('这个极限就是<b>定积分</b>：∫ₐᵇ f(x)dx = lim(n→∞) Σ f(xᵢ)Δx。',
        st(['分割 → 近似代替 → 求和 → 取极限', '四步与小学「数方格 / 割补」一脉相承'])));
      o.push(S('<b>牛顿—莱布尼茨公式</b>：若 F′=f，则 <b>∫ₐᵇ f(x)dx = F(b) − F(a)</b>。',
        st(['∫₀³ (x²/2)dx = [x³/6]₀³', '= 27/6 − 0 = 4.5', '不必真的去算无穷多个矩形！'])));
      o.push(S('这条定理把「无限求和」与「求导的逆运算」连起来，是微积分最主要的结果。',
        st(['微分与积分互为逆运算', '定积分是一个数，不定积分是一族函数', '几何意义：曲边梯形的有向面积'])));
      return o;
    },
    notes: [
      '<p>定积分的定义是「细分 → 近似 → 求和 → 取极限」，正是小学割补求面积、圆面积推导的严格化。</p>',
      '<p>牛顿—莱布尼茨公式是计算上的飞跃：把极限运算换成找原函数再代两端点。</p>',
      '<p>下一节用它求面积、体积、弧长；物理中的功、压力、质心也都是同一个积分。</p>'
    ],
    example: { q: '计算 ∫₀² 3x² dx', steps: ['原函数 F(x)=x³', 'F(2)−F(0)'], a: '8' },
    quiz: [
      { q: '∫₀¹ 2x dx = ?', options: ['0', '1', '2', '1/2'], answer: 1, explain: '原函数 x²，1²−0² = 1。' },
      { q: '牛顿—莱布尼茨公式把定积分化成？', options: ['黎曼和', 'F(b)−F(a)', "f'(b)−f'(a)", '无穷级数'], answer: 1, explain: '原函数在两端点之差。' }
    ]
  });

  T({
    id: 'ca-integral-apply', unit: 'ca-c5', title: '定积分的应用', subtitle: '面积、旋转体体积与累加量',
    goal: '会用定积分求平面图形面积与旋转体体积',
    why: '《微积分初步》第五章「二 定积分的应用」（p228）。',
    minutes: 13, star: true, prereq: ['ca-def-integral', 'so-volume'],
    demo: function () {
      var o = [];
      o.push(S('两曲线 y=f(x)、y=g(x) 之间从 a 到 b 的面积：<b>∫ₐᵇ |f(x)−g(x)| dx</b>。',
        ax({ x: [-1, 4], y: [-1, 5] }, { curves: [
          { pts: curve(function (x) { return x; }, 0, 3, 30), cls: '', label: 'y=x' },
          { pts: curve(function (x) { return x * x / 3; }, 0, 3, 40), cls: 'is-hi', label: 'y=x²/3' }
        ], rects: [
          { x: 0.5, y: 0.083, w: 0.5, h: 0.417, cls: '' },
          { x: 1.5, y: 0.75, w: 0.5, h: 0.75, cls: '' },
          { x: 2.5, y: 2.083, w: 0.4, h: 0.417, cls: '' }
        ], caption: '每个窄条高度 = 上函数 − 下函数' })));
      o.push(S('例：求 y=x 与 y=x²/3 围成的面积，先解交点 x²/3 = x ⇒ x=0、3。',
        st(['S = ∫₀³ (x − x²/3)dx', '= [x²/2 − x³/9]₀³', '= 9/2 − 3 = 3/2'])));
      o.push(S('旋转体体积：把 y=f(x) 下的区域绕 x 轴旋转，每个薄片是半径 f(x) 的圆盘。',
        ax({ x: [-0.3, 3.3], y: [-0.3, 5] }, { curves: [
          { pts: curve(function (x) { return x * x / 2; }, 0, 3, 50), cls: 'is-hi' }
        ], rects: [
          { x: 0.6, y: 0, w: 0.5, h: 0.18, cls: '' },
          { x: 1.6, y: 0, w: 0.5, h: 1.28, cls: '' },
          { x: 2.6, y: 0, w: 0.4, h: 3.38, cls: '' }
        ], caption: '薄片面积 π f(x)²，沿 x 累加' })));
      o.push(S('<b>V = π ∫ₐᵇ f(x)² dx</b>。由此可严格推出立体几何里的球体积公式。',
        st(['半球：f(x)=√(R²−x²)', 'V = π∫₋R^R (R²−x²)dx = 4/3 πR³', '祖暅原理的结论在这里被算出来'])));
      o.push(S('一般规律：若某个量随位置变化，把它切成微元再积分，就得到总量。',
        st(['变力做功 W = ∫F(x)dx', '路程 s = ∫v(t)dt', '概率密度下的面积 = 概率'])));
      return o;
    },
    notes: [
      '<p>应用题的固定套路：确定积分变量与区间 → 写出微元（面积/体积/功） → 积分 → 代入端点。</p>',
      '<p>求两曲线间面积时，若上下关系在区间内交换，必须分段积分或取绝对值。</p>',
      '<p>这一节把《立体几何》的体积公式、《代数 第一册》的近似计算、《物理》的功统一到同一个工具下，是整套甲种本的终点。</p>'
    ],
    example: { q: '求 y=x 与 x 轴在 [0,2] 围成的面积', steps: ['S = ∫₀² x dx', '= [x²/2]₀²'], a: '2' },
    quiz: [
      { q: 'y=f(x) 绕 x 轴旋转所得体积是？', options: ['∫f dx', 'π∫f² dx', '2π∫f dx', '∫f³ dx'], answer: 1, explain: '圆盘法：每个薄片面积 π f(x)²。' },
      { q: '两曲线间面积应积分？', options: ['上函数 − 下函数', '上 + 下', '两函数之积', '两函数平均值'], answer: 0, explain: '微元高度是上下之差。' }
    ]
  });

})();
