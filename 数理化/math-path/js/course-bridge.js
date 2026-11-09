/* MathPath — 甲种本目标层：六册目录地图、入学检查、衔接课 */
(function () {
  'use strict';
  var MP = window.MathPath, U = MP.util, S = U.step;

  function C(t, cls) { return { t: t, cls: cls || '' }; }
  function row(str, cls) { return { cells: String(str).split('').map(function (c) { return C(c, cls || ''); }) }; }
  function st(arr) { return { view: 'steps', lines: arr.map(function (s) { return typeof s === 'string' ? row(s) : s; }) }; }
  function curve(f, a, b, n) {
    var p = [], k = n || 50;
    for (var i = 0; i <= k; i++) { var x = a + (b - a) * i / k; p.push([x, U.round(f(x), 4)]); }
    return p;
  }
  function T(o) { MP.registerTopic(o); }

  MP.registerUnits([
    { id: 'b-bridge', track: 'bridge', name: '衔接课 · 通向甲种本', desc: '把初中知识接到高中课本的第一页' }
  ]);

  /* 六本课本（目录逐本核对自 F:\download\数学甲种本） */
  MP.registerBooks([
    {
      id: 'alg1', name: '代数 第一册', sub: '高一上 · 每周 3 课时 · 1983 人教版',
      chapters: '第一章 幂函数、指数函数和对数函数（集合 / 映射与函数 / 幂函数 / 指数函数和对数函数）；第二章 三角函数（任意角的三角函数 / 三角函数的图象和性质）；第三章 两角和与差的三角函数；附录 近似计算的法则、换底公式',
      note: '六本里最该先读的一本。它一上来就默认你会「用字母表示一般规律」「通分」「根式与指数」，且把锐角三角函数直接推广到任意角。',
      req: ['p-letter', 'p-frac-reduce', 'p-approx', 'p-place', 'm-rational', 'm-real', 'm-power', 'm-frac-expr', 'm-trig', 'm-quad-fn'],
      order: 1
    },
    {
      id: 'alg2', name: '代数 第二册', sub: '高一 / 高二',
      chapters: '第一章 反三角函数和简单三角方程；第二章 数列与数学归纳法；第三章 不等式；第四章 行列式和线性方程组；第五章 复数',
      note: '数列需要「找规律 + 用 n 表示通项」；不等式是初中解集往上加证明；复数由 Δ<0 的一元二次方程引出。',
      req: ['p-pattern', 'p-letter', 'm-eq2', 'm-ineq', 'm-eq-sys', 'm-factor', 'm-trig'],
      order: 4
    },
    {
      id: 'alg3', name: '代数 第三册', sub: '高二 / 高三 · 部分选学',
      chapters: '*第一章 一元多项式和高次方程；第二章 排列、组合、二项式定理；第三章 概率',
      note: '标 * 的第一章是选学。多项式与高次方程就是「整数的质因数分解」换成了多项式；排列组合是树状图的公式化。',
      req: ['p-factor', 'p-mul', 'p-frac-ops', 'm-factor', 'm-poly', 'm-eq2', 'm-prob'],
      order: 5
    },
    {
      id: 'analytic', name: '平面解析几何 全一册', sub: '高二',
      chapters: '第一章 直线（有向线段、定比分点 / 直线的方程 / 两条直线的位置关系）；第二章 圆锥曲线（曲线和方程 / 圆 / 椭圆 / 双曲线 / 抛物线）；第三章 坐标变换（平移和旋转 / *一般二元二次方程的讨论）；第四章 参数方程、极坐标',
      note: '最吃前置的一本：每求一次交点都要解一元二次方程、看判别式；每条曲线都要靠配方与平移化成标准形。',
      req: ['m-coord', 'm-linear-fn', 'm-eq2', 'm-quad-fn', 'm-transform', 'm-circle', 'm-pyth', 'm-trig', 'm-factor'],
      order: 2
    },
    {
      id: 'solid', name: '立体几何 全一册', sub: '高二',
      chapters: '第一章 直线和平面（平面 / 空间两条直线 / 空间直线和平面 / 空间两个平面）；第二章 多面体和旋转体及体积；*第三章 多面角和正多面体；附录 公式表',
      note: '把平面几何里的平行、垂直、全等、相似搬到三维，多了「不在同一平面」的情形。面积割补直觉直接变成体积与祖暅原理。',
      req: ['m-lines-angle', 'm-congruent', 'm-similar', 'm-pyth', 'm-circle', 'p-area-rect', 'p-unit'],
      order: 3
    },
    {
      id: 'calc', name: '微积分初步 全一册', sub: '高三 · 甲种本特色',
      chapters: '第一章 极限；第二章 导数和微分（导数概念 / 求导方法 / 微分）；第三章 导数的应用；第四章 不定积分；第五章 定积分及其应用；附表 简易积分表',
      note: '乙种本没有这本。极限是「无限逼近」的严格化，导数是割线斜率的极限，积分是割补求面积的极限 —— 小学的三个直觉在这里汇合。',
      req: ['p-approx', 'p-area-rect', 'p-circle', 'm-quad-fn', 'm-linear-fn', 'm-frac-expr', 'm-ineq', 'm-rational', 'm-trig'],
      order: 6
    }
  ]);

  /* ---------------- 衔接课 ---------------- */
  T({
    id: 'b-angle-rad', unit: 'b-bridge', title: '从锐角三角函数到任意角与弧度', subtitle: '把角转出 0°~90°，用单位圆重新定义 sin、cos',
    goal: '理解弧度制、任意角、单位圆定义，知道 sin²+cos²=1 的来源',
    why: '对应甲种本《代数 第一册》第二章「任意角的三角函数」与「三角函数的图象和性质」',
    view: 'shapes', minutes: 12, star: true,
    prereq: ['m-trig', 'p-circle', 'p-angle'],
    demo: function () {
      var o = [];
      o.push(S('初中：sin A = 对边/斜边，只在<b>直角三角形</b>里定义，角被限制在 0°~90°。',
        { view: 'shapes', items: [
          { k: 'poly', pts: [[180, 220], [430, 220], [180, 90]], cls: 'is-on' },
          { k: 'text', x: 205, y: 205, t: 'A', cls: '' },
          { k: 'text', x: 320, y: 45, t: 'sin A = 对边 / 斜边', cls: '' }
        ], caption: '定义依赖一个具体的直角三角形' }));
      o.push(S('高中：把角的顶点放在原点、始边放在 x 轴正半轴，终边可以<b>任意旋转</b>。',
        { view: 'shapes', items: [
          { k: 'line', x1: 60, y1: 160, x2: 580, y2: 160, cls: 'is-dim' },
          { k: 'line', x1: 300, y1: 280, x2: 300, y2: 30, cls: 'is-dim' },
          { k: 'circle', x: 300, y: 160, r: 100, cls: 'is-on' },
          { k: 'line', x1: 300, y1: 160, x2: 380, y2: 92, cls: 'is-hi' },
          { k: 'circle', x: 380, y: 92, r: 5, cls: 'is-hi' },
          { k: 'text', x: 300, y: 25, t: '终边落在第几象限，就按该象限符号取正/负', cls: '' }
        ], caption: '任意角：超过 360° 继续转，反向转为负角' }));
      o.push(S('半径取 1（单位圆）：终边与圆交点 <b>P(x, y)</b>，直接定义 <b>cos θ = x，sin θ = y</b>。',
        { view: 'shapes', items: [
          { k: 'line', x1: 60, y1: 160, x2: 580, y2: 160, cls: 'is-dim' },
          { k: 'line', x1: 300, y1: 280, x2: 300, y2: 30, cls: 'is-dim' },
          { k: 'circle', x: 300, y: 160, r: 100, cls: 'is-on' },
          { k: 'line', x1: 300, y1: 160, x2: 370, y2: 89, cls: 'is-hi' },
          { k: 'line', x1: 370, y1: 89, x2: 370, y2: 160, cls: 'is-hi' },
          { k: 'text', x: 430, y: 120, t: 'sin θ = y', cls: '' },
          { k: 'text', x: 335, y: 180, t: 'cos θ = x', cls: '' },
          { k: 'text', x: 300, y: 25, t: 'P(cos θ, sin θ)', cls: '' }
        ], caption: '斜边 = 1，所以「比值」直接就是坐标' }));
      o.push(S('由勾股定理：<b>cos²θ + sin²θ = 1</b>。所有三角恒等式都从这一条长出来。',
        st(['x² + y² = 1', '⇒ cos²θ + sin²θ = 1', '⇒ tan θ = sin θ / cos θ'])));
      o.push(S('弧度制：用「弧长 ÷ 半径」量角，整圈 = 2πr/r = <b>2π</b>。',
        st(['180° = π 弧度     90° = π/2 弧度', '弧长 l = |α| · r  （公式变简单了）', '甲种本从此一律用弧度'])));
      return o;
    },
    notes: [
      '<p>初中定义靠「直角三角形」，高中定义靠「圆」：前者只能处理锐角，后者对任意角都成立。</p>',
      '<p>单位圆上 cos 是横坐标、sin 是纵坐标，于是符号、周期性、图象都能直接读出来。</p>',
      '<p>甲种本接着讲正弦曲线 y=sin x 的图象与性质、两角和与差的公式、反三角函数与简单三角方程。</p>'
    ],
    example: { q: '120° 等于多少弧度？sin 120° 是正还是负？', steps: ['120° × π/180 = 2π/3', '120° 终边在第二象限，y > 0'], a: '2π/3 弧度，sin 120° 为正（= √3/2）' },
    quiz: [
      { q: '90° 等于多少弧度？', options: ['π/4', 'π/2', 'π', '2π'], answer: 1, explain: '180° = π，所以 90° = π/2。' },
      { q: '单位圆上点 P 的坐标是 (cos θ, ?)', options: ['tan θ', 'sin θ', '1', 'θ'], answer: 1, explain: '横坐标 cos θ，纵坐标 sin θ。' }
    ]
  });

  T({
    id: 'b-func-map', unit: 'b-bridge', title: '从函数到集合、映射与反函数', subtitle: '甲种本第一页的抽象语言',
    goal: '会读 N/Z/Q/R、集合运算，理解映射、一一映射与反函数',
    why: '对应甲种本《代数 第一册》第一章「集合」「映射与函数」',
    view: 'shapes', minutes: 11, star: true,
    prereq: ['m-rational', 'm-real', 'm-linear-fn'],
    demo: function () {
      var o = [];
      o.push(S('常用数集记号：<b>N</b> 自然数、<b>Z</b> 整数、<b>Q</b> 有理数、<b>R</b> 实数，层层包含。',
        { view: 'shapes', items: [
          { k: 'rect', x: 100, y: 50, w: 440, h: 200, rx: 16, cls: 'is-void' },
          { k: 'rect', x: 130, y: 78, w: 380, h: 145, rx: 12, cls: 'is-on' },
          { k: 'rect', x: 160, y: 105, w: 320, h: 92, rx: 10, cls: 'is-hi' },
          { k: 'rect', x: 190, y: 130, w: 260, h: 44, rx: 8, cls: 'is-done' },
          { k: 'text', x: 320, y: 40, t: 'R ⊃ Q ⊃ Z ⊃ N', cls: '' },
          { k: 'text', x: 320, y: 156, t: 'N 自然数', cls: '' },
          { k: 'text', x: 320, y: 235, t: 'R 实数', cls: '' }
        ], caption: '小学的「数」在这里被分层命名' }));
      o.push(S('集合运算：交集 A∩B、并集 A∪B、补集 ∁A；「元素属于集合」记作 a ∈ A。',
        st(['A = {1,2,3},  B = {3,4,5}', 'A ∩ B = {3}', 'A ∪ B = {1,2,3,4,5}'])));
      o.push(S('映射：给 A 中<b>每个</b>元素，按规则 f 在 B 中找<b>唯一</b>对应的元素。',
        { view: 'shapes', items: [
          { k: 'rect', x: 90, y: 60, w: 120, h: 180, rx: 12, cls: 'is-on' },
          { k: 'rect', x: 430, y: 60, w: 120, h: 180, rx: 12, cls: 'is-on' },
          { k: 'text', x: 150, y: 48, t: '定义域 A', cls: '' }, { k: 'text', x: 490, y: 48, t: '值域所在 B', cls: '' },
          { k: 'text', x: 150, y: 100, t: '1', cls: '' }, { k: 'text', x: 150, y: 150, t: '2', cls: '' }, { k: 'text', x: 150, y: 200, t: '3', cls: '' },
          { k: 'text', x: 490, y: 100, t: '2', cls: '' }, { k: 'text', x: 490, y: 150, t: '4', cls: '' }, { k: 'text', x: 490, y: 200, t: '6', cls: '' },
          { k: 'line', x1: 175, y1: 96, x2: 465, y2: 96, cls: 'is-hi' },
          { k: 'line', x1: 175, y1: 146, x2: 465, y2: 146, cls: 'is-hi' },
          { k: 'line', x1: 175, y1: 196, x2: 465, y2: 196, cls: 'is-hi' },
          { k: 'text', x: 320, y: 275, t: 'f(x) = 2x', cls: '' }
        ], caption: '每个 x 只能有一个 f(x)' }));
      o.push(S('函数 = 定义域 + 值域 + 对应法则三件套。两个函数相同，要三者都相同。',
        st(['f(x) = x²  与  g(x) = x² (x ≥ 0)', '法则一样，但定义域不同 ⇒ 不是同一函数'])));
      o.push(S('若映射是<b>一一对应</b>，就能反过来定义<b>反函数</b>：y = 2x ⇔ x = y/2。',
        { view: 'axis', range: { x: [-1, 4], y: [-1, 4] }, curves: [
          { pts: [[0, 0], [2, 4]], cls: '', label: 'y=2x' },
          { pts: [[0, 0], [4, 2]], cls: 'is-hi', label: 'y=x/2' },
          { pts: [[0, 0], [4, 4]], cls: 'is-dim', label: 'y=x' }
        ], caption: '互为反函数的图像关于 y=x 对称' }));
      return o;
    },
    notes: [
      '<p>集合是「把一堆东西整体看待」，映射是「两个集合之间的规则」，函数是数集之间的映射。</p>',
      '<p>初中说「y 随 x 变化」，高中改写为「f: A → B」，多了定义域与值域的明确要求。</p>',
      '<p>甲种本用它引出幂函数、指数函数，再由「一一映射可逆」引出对数函数与反三角函数。</p>'
    ],
    example: { q: 'f(x)=2x+1 的反函数是什么？', steps: ['由 y = 2x+1 解出 x', 'x = (y−1)/2，交换 x/y'], a: 'f⁻¹(x) = (x−1)/2' },
    quiz: [
      { q: '记号 Q 表示哪个数集？', options: ['自然数', '整数', '有理数', '实数'], answer: 2, explain: 'N 自然数、Z 整数、Q 有理数、R 实数。' },
      { q: '互为反函数的两个图像关于什么对称？', options: ['x 轴', 'y 轴', 'y = x', '原点'], answer: 2, explain: '交换 x 与 y 相当于关于直线 y=x 翻折。' }
    ]
  });

  T({
    id: 'b-exp-log', unit: 'b-bridge', title: '从幂运算到指数函数与对数', subtitle: '把「求幂」倒过来，就是求对数',
    goal: '理解 aˣ 与 logₐx 互为反函数，会读换底公式',
    why: '对应甲种本《代数 第一册》第一章「指数函数和对数函数」及附录「换底公式」',
    view: 'axis', minutes: 12, star: true,
    prereq: ['m-power', 'm-frac-expr', 'b-func-map'],
    demo: function () {
      var o = [];
      o.push(S('整数指数 → 分数指数 → 实数指数：把 <b>2ⁿ</b> 中的 n 从整数扩展到任意实数。',
        st(['2³ = 8        2⁰ = 1', '2⁻¹ = 1/2    2^(1/2) = √2', 'y = 2ˣ  ← 指数函数'])));
      o.push(S('画出 <b>y = 2ˣ</b>：恒过点 (0,1)，x 越大增长越快，永远为正。',
        { range: { x: [-3, 3], y: [-1, 8] }, curves: [
          { pts: curve(function (x) { return Math.pow(2, x); }, -3, 3, 50), cls: '', label: 'y=2ˣ' }
        ], points: [{ x: 0, y: 1, label: '(0,1)', cls: 'is-hi' }], caption: '底数 a > 1 时单调递增' }));
      o.push(S('反过来问「2 的几次方等于 8」→ <b>log₂8 = 3</b>。对数就是指数的逆运算。',
        st(['2³ = 8   ⇔   log₂8 = 3', 'aᵇ = N  ⇔  logₐN = b', '条件：a > 0 且 a ≠ 1，N > 0'])));
      o.push(S('所以 <b>y = log₂x</b> 与 y = 2ˣ 的图像关于 y = x 对称。',
        { range: { x: [-2, 6], y: [-2, 6] }, curves: [
          { pts: curve(function (x) { return Math.pow(2, x); }, -2, 2.5, 40), cls: '', label: 'y=2ˣ' },
          { pts: curve(function (x) { return Math.log(x) / Math.LN2; }, 0.18, 6, 45), cls: 'is-hi', label: 'y=log₂x' },
          { pts: [[-1, -1], [6, 6]], cls: 'is-dim', label: 'y=x' }
        ], caption: '互为反函数' }));
      o.push(S('换底公式（第一册附录）：<b>logₐb = log꜀b / log꜀a</b>，用通分和指数律即可推出。',
        st(['logₐb = ln b / ln a', '这一条让任意底的对数都能用计算器算', '也解释了为什么它原本安排在初中教：本质是分式'])));
      return o;
    },
    notes: [
      '<p>指数函数回答「a 的 x 次方是多少」，对数函数回答「a 的几次方等于这个数」，互为反函数。</p>',
      '<p>运算律也是互逆的：<code>aᵐ·aⁿ = aᵐ⁺ⁿ</code> 对应 <code>log(MN) = logM + logN</code>。</p>',
      '<p>甲种本第一册接着讨论它们的图象、单调性、指数方程与对数方程；附录的近似计算法则与换底公式是配套工具。</p>'
    ],
    example: { q: '求 log₃27 与 log₂(1/8)', steps: ['3³ = 27，所以 log₃27 = 3', '2⁻³ = 1/8，所以 log₂(1/8) = −3'], a: '3 与 −3' },
    quiz: [
      { q: 'log₅125 = ?', options: ['2', '3', '5', '25'], answer: 1, explain: '5³ = 125。' },
      { q: 'y = 2ˣ 的图像一定经过哪个点？', options: ['(0,0)', '(0,1)', '(1,0)', '(1,1)'], answer: 1, explain: 'a⁰ = 1，所以过 (0,1)。' }
    ]
  });

  T({
    id: 'b-conic', unit: 'b-bridge', title: '从二次函数与圆到圆锥曲线', subtitle: '用一个平面去切圆锥，切出三种曲线',
    goal: '认识椭圆、双曲线、抛物线的标准方程与几何定义',
    why: '对应甲种本《平面解析几何》第二章「圆锥曲线」与第三章「坐标变换」',
    view: 'axis', minutes: 13, star: true,
    prereq: ['m-quad-fn', 'm-circle', 'm-eq2', 'm-transform'],
    demo: function () {
      var o = [];
      o.push(S('初中已有两条曲线：<b>y = x²</b>（抛物线）和 <b>(x−a)²+(y−b)²=r²</b>（圆）。',
        { range: { x: [-4, 4], y: [-2, 6] }, curves: [
          { pts: curve(function (x) { return x * x / 3; }, -4, 4, 50), cls: '', label: '抛物线' },
          { pts: curve(function (x) { return 1 + Math.sqrt(Math.max(0, 4 - x * x)); }, -2, 2, 40), cls: 'is-hi' },
          { pts: curve(function (x) { return 1 - Math.sqrt(Math.max(0, 4 - x * x)); }, -2, 2, 40), cls: 'is-hi', label: '圆' }
        ], caption: '都用「到定点的距离」或坐标关系定义' }));
      o.push(S('<b>椭圆</b>：到两定点 F₁、F₂ 距离之和为常数 2a。标准方程 <b>x²/a² + y²/b² = 1</b>。',
        { range: { x: [-5, 5], y: [-3, 3] }, curves: [
          { pts: curve(function (x) { return 2 * Math.sqrt(Math.max(0, 1 - x * x / 16)); }, -4, 4, 60), cls: '' },
          { pts: curve(function (x) { return -2 * Math.sqrt(Math.max(0, 1 - x * x / 16)); }, -4, 4, 60), cls: '' }
        ], points: [{ x: -3.46, y: 0, label: 'F₁', cls: 'is-hi' }, { x: 3.46, y: 0, label: 'F₂', cls: 'is-hi' }],
          caption: '|PF₁| + |PF₂| = 2a = 8' }));
      o.push(S('<b>双曲线</b>：到两定点距离之<b>差</b>为常数。标准方程 <b>x²/a² − y²/b² = 1</b>。',
        { range: { x: [-6, 6], y: [-5, 5] }, curves: [
          { pts: curve(function (x) { return 2 * Math.sqrt(Math.max(0, x * x / 9 - 1)); }, 3, 6, 30), cls: 'is-hi' },
          { pts: curve(function (x) { return -2 * Math.sqrt(Math.max(0, x * x / 9 - 1)); }, 3, 6, 30), cls: 'is-hi' },
          { pts: curve(function (x) { return 2 * Math.sqrt(Math.max(0, x * x / 9 - 1)); }, -6, -3, 30), cls: 'is-hi' },
          { pts: curve(function (x) { return -2 * Math.sqrt(Math.max(0, x * x / 9 - 1)); }, -6, -3, 30), cls: 'is-hi' }
        ], caption: '两支，且有渐近线' }));
      o.push(S('<b>抛物线</b>：到定点（焦点）与定直线（准线）<b>距离相等</b>。标准方程 y² = 2px。',
        { range: { x: [-2, 6], y: [-5, 5] }, curves: [
          { pts: curve(function (y) { return y * y / 4; }, -4.4, 4.4, 50).map(function (p) { return [p[1], p[0]]; }), cls: 'is-hi' }
        ], lines: [{ a: [-1, -5], b: [-1, 5], cls: 'is-dim', label: '准线' }],
          points: [{ x: 1, y: 0, label: '焦点', cls: 'is-on' }], caption: '把 y=x² 转 90° 就是它' }));
      o.push(S('直线与圆锥曲线联立 → <b>一元二次方程</b> → 看判别式 Δ：Δ&gt;0 相交、Δ=0 相切、Δ&lt;0 相离。',
        st(['把 y = kx+b 代入 x²/a² + y²/b² = 1', '整理成 Ax² + Bx + C = 0', 'Δ = B² − 4AC 决定交点个数', '← 初中的判别式在这里成为主角'])));
      return o;
    },
    notes: [
      '<p>三种曲线都能用「到定点/定直线的距离关系」统一定义，也都能用一个平面切圆锥得到。</p>',
      '<p>把一般二次方程配方、平移坐标轴化成标准形，是第三章「坐标变换」的任务。</p>',
      '<p>甲种本第二章按「曲线和方程 → 圆 → 椭圆 → 双曲线 → 抛物线」逐一展开；求交点和切线时全靠初中的一元二次方程与判别式。</p>'
    ],
    example: { q: '椭圆 x²/25 + y²/9 = 1 的长半轴 a 是多少？', steps: ['标准形式 x²/a² + y²/b² = 1', 'a² = 25'], a: 'a = 5' },
    quiz: [
      { q: '椭圆的定义是到两定点距离的？', options: ['差为常数', '和为常数', '积为常数', '比为常数'], answer: 1, explain: '和 = 2a；差为常数是双曲线。' },
      { q: '直线与圆联立后 Δ = 0 表示？', options: ['相交两点', '相切', '相离', '直线不存在'], answer: 1, explain: '一个重根，对应相切。' }
    ]
  });

  T({
    id: 'b-sequence', unit: 'b-bridge', title: '从找规律到数列与数学归纳法', subtitle: '把「第 n 项」写通，再证明它永远成立',
    goal: '理解通项公式、递推公式与数学归纳法两步',
    why: '对应甲种本《代数 第二册》第二章「数列与数学归纳法」',
    view: 'bars', minutes: 11, star: true,
    prereq: ['p-pattern', 'p-letter', 'm-poly'],
    demo: function () {
      var o = [];
      o.push(S('小学：2, 4, 6, 8, ? 靠猜相邻差。高中：把第 n 项写成 <b>aₙ = 2n</b>。',
        { values: [2, 4, 6, 8, 10], labels: ['a₁', 'a₂', 'a₃', 'a₄', 'a₅'], marks: { hi: [4] }, caption: '通项公式一次回答所有项' }));
      o.push(S('等差数列：<b>aₙ = a₁ + (n−1)d</b>；前 n 项和 <b>Sₙ = n(a₁+aₙ)/2</b>。',
        { values: [3, 6, 9, 12, 15], labels: ['a₁', 'a₂', 'a₃', 'a₄', 'a₅'], marks: { done: [0, 1, 2, 3, 4] }, caption: 'a₁=3, d=3' }));
      o.push(S('高斯配对：1+2+…+100，首尾配对共 50 对、每对 101 → 5050。',
        { view: 'steps', lines: [
          { cells: [C('1 + 100 = 101'), C('   2 + 99 = 101'), C('   …')] },
          { cells: [C('50 对 × 101 = 5050', 'is-done')] }] }));
      o.push(S('等比数列：<b>aₙ = a₁qⁿ⁻¹</b>；递推公式则用前一项定义后一项。',
        { values: [2, 4, 8, 16, 32], labels: ['q¹', 'q²', 'q³', 'q⁴', 'q⁵'], marks: { hi: [4] }, caption: 'a₁=2, q=2' }));
      o.push(S('数学归纳法两步：① 验证 n=1 成立；② 假设 n=k 成立，推出 n=k+1 也成立。',
        { view: 'steps', lines: [
          { cells: [C('① 奠基：n = 1 ✓', 'is-on')] },
          { cells: [C('② 递推：k 成立 ⇒ k+1 成立', 'is-hi')] },
          { cells: [C('⇒ 对所有正整数 n 成立', 'is-done')] }],
          caption: '像多米诺骨牌：第一块倒 + 每块能推倒下一块' }));
      return o;
    },
    notes: [
      '<p>数列就是定义在正整数上的函数；通项公式是「显式」，递推公式是「逐步」。</p>',
      '<p>归纳法不是「看前几项猜规律」，而是用逻辑保证从 n=1 一路推到无穷。</p>',
      '<p>甲种本代数2 会系统讲等差/等比数列、求和、极限的初步以及归纳法证明；微积分里的数列极限是它的延续。</p>'
    ],
    example: { q: '等差数列 a₁=5, d=3，求 a₁₀ 与 S₁₀', steps: ['a₁₀ = 5 + 9×3 = 32', 'S₁₀ = 10(5+32)/2'], a: 'a₁₀=32，S₁₀=185' },
    quiz: [
      { q: '等差数列 3, 7, 11, … 的公差 d 是？', options: ['3', '4', '7', '11'], answer: 1, explain: '相邻两项差为 4。' },
      { q: '数学归纳法必须包含哪两步？', options: ['验证 n=1 与 n=2', '奠基与递推', '猜通项与验证', '求和与取极限'], answer: 1, explain: '先证起点，再证「k ⇒ k+1」。' }
    ]
  });

  T({
    id: 'b-limit', unit: 'b-bridge', title: '从近似、割补到极限与导数', subtitle: '小学的两个直觉，在高中变成严格工具',
    goal: '理解「无限逼近」、割线斜率趋于切线斜率、矩形和趋于面积',
    why: '对应甲种本《微积分初步》第一章「极限」、第二章「导数和微分」、第五章「定积分」',
    view: 'axis', minutes: 14, star: true,
    prereq: ['p-approx', 'p-area-rect', 'p-circle', 'm-linear-fn', 'm-quad-fn'],
    demo: function () {
      var o = [];
      o.push(S('小学取近似：3.146 → 3.15；切圆成扇形 → 拼成长方形。两处都用了「<b>越来越接近</b>」。',
        { view: 'steps', lines: [
          { cells: [C('近似数：误差可以任意小', 'is-on')] },
          { cells: [C('割补：切得越细，越接近真值', 'is-on')] },
          { cells: [C('微积分：把「越来越」写成极限', 'is-hi')] }] }));
      o.push(S('导数：在曲线 y=x² 上取 P 与 Q，割线 PQ 的斜率是 <b>Δy/Δx</b>。',
        { range: { x: [-1, 4], y: [-1, 9] }, curves: [
          { pts: curve(function (x) { return x * x; }, -0.5, 3, 50), cls: '' }
        ], points: [{ x: 1, y: 1, label: 'P', cls: 'is-hi' }, { x: 2.5, y: 6.25, label: 'Q', cls: 'is-on' }],
          lines: [{ a: [1, 1], b: [2.5, 6.25], cls: 'is-hi' }], caption: '割线斜率 = (6.25−1)/(2.5−1) = 3.5' }));
      o.push(S('让 Q 沿曲线<b>不断靠近 P</b>，割线斜率依次 3.5 → 3 → 2.1 → … 趋于 <b>2</b>。',
        { range: { x: [-1, 4], y: [-1, 9] }, curves: [
          { pts: curve(function (x) { return x * x; }, -0.5, 3, 50), cls: '' }
        ], points: [{ x: 1, y: 1, label: 'P(1,1)', cls: 'is-hi' }],
          lines: [
            { a: [1, 1], b: [2.5, 6.25], cls: 'is-dim' },
            { a: [1, 1], b: [2, 4], cls: 'is-dim' },
            { a: [0.5, -0.5], b: [2.5, 3.5], cls: 'is-hi', label: '切线 y=2x−1' }
          ], caption: 'P 处切线斜率 = 2·1 = 2' }));
      o.push(S('用代数算：( (1+h)² − 1 ) / h = 2 + h → 当 h→0 时极限为 <b>2</b>。这就是 <b>f′(1)=2</b>。',
        { view: 'steps', lines: [
          { cells: [C('f′(x) = lim(h→0) [f(x+h) − f(x)] / h', 'is-hi')] },
          { cells: [C('f(x)=x²  ⇒  f′(x) = 2x', 'is-done')] },
          { cells: [C('导数 = 曲线在该点切线的斜率', 'is-on')] }] }));
      o.push(S('定积分：把曲边图形切成 n 个窄矩形求和，n→∞ 时极限就是面积。',
        { range: { x: [0, 3], y: [0, 5] }, curves: [
          { pts: curve(function (x) { return x * x / 2; }, 0, 3, 40), cls: 'is-hi' }
        ], rects: [
          { x: 0, y: 0, w: 0.5, h: 0.125, cls: 'is-dim' }, { x: 0.5, y: 0, w: 0.5, h: 0.125 * 4, cls: 'is-dim' },
          { x: 1, y: 0, w: 0.5, h: 0.5, cls: 'is-dim' }, { x: 1.5, y: 0, w: 0.5, h: 1.125, cls: 'is-dim' },
          { x: 2, y: 0, w: 0.5, h: 2, cls: 'is-dim' }, { x: 2.5, y: 0, w: 0.5, h: 3.125, cls: 'is-dim' }
        ], caption: '黎曼和：小学数方格的高中版本' }));
      o.push(S('于是小学的「数方格」、初中的「斜率」、近似数的「误差」在甲种本汇成一句话：',
        { view: 'steps', lines: [
          { cells: [C('极限 → 导数（变化率）', 'is-on')] },
          { cells: [C('极限 → 定积分（累积量）', 'is-on')] },
          { cells: [C('两者由微积分基本定理连起来', 'is-done')] }] }));
      return o;
    },
    notes: [
      '<p>极限把「无限接近但不等于」变成可以运算的对象，这是微积分与初等数学的分界线。</p>',
      '<p>导数是割线斜率的极限（局部变化率），积分是矩形面积和的极限（整体累积），互为逆运算。</p>',
      '<p>甲种本《微积分初步》按「极限 → 导数与微分 → 导数应用 → 不定积分 → 定积分应用」展开，是整套教材的终点。</p>'
    ],
    example: { q: 'f(x)=x²，求 f′(3)', steps: ['f′(x) = 2x', '代入 x=3'], a: '6（该点切线斜率为 6）' },
    quiz: [
      { q: 'f(x)=x² 在 x=2 处的切线斜率是？', options: ['2', '4', '8', '1'], answer: 1, explain: 'f′(x)=2x，f′(2)=4。' },
      { q: '定积分的几何意义是？', options: ['切线斜率', '曲线长度', '曲边图形面积', '函数最大值'], answer: 2, explain: '矩形面积和取极限得到曲边梯形面积。' }
    ]
  });

})();
