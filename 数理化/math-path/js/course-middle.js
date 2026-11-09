/* MathPath — 初中段：代数、函数、平面几何（甲种本的真实前置） */
(function () {
  'use strict';
  var MP = window.MathPath, U = MP.util, S = U.step;

  function C(t, cls) { return { t: t, cls: cls || '' }; }
  function L(cells, cls, label) { return { cells: cells, cls: cls || '', label: label || '' }; }
  function row(str, cls, label) { return L(String(str).split('').map(function (c) { return C(c, cls || ''); }), '', label); }
  function lines(arr) { return { lines: arr.map(function (s) { return typeof s === 'string' ? row(s) : s; }), caption: '' }; }
  function curve(f, a, b, n) {
    var p = [], k = n || 60;
    for (var i = 0; i <= k; i++) { var x = a + (b - a) * i / k; p.push([x, U.round(f(x), 4)]); }
    return p;
  }
  function R(x, y) { return { range: { x: x, y: y } }; }
  function T(o) { MP.registerTopic(o); }

  MP.registerUnits([
    { id: 'm-num', track: 'middle', name: '数与式', desc: '实数、幂、整式、因式分解、分式' },
    { id: 'm-eq', track: 'middle', name: '方程与不等式', desc: '消元、一元二次、不等式解集' },
    { id: 'm-func', track: 'middle', name: '函数与坐标', desc: '坐标系、一次/反比例/二次函数、图像变换' },
    { id: 'm-geo', track: 'middle', name: '平面几何', desc: '平行线、全等相似、勾股、圆、解三角形' },
    { id: 'm-stat', track: 'middle', name: '统计与概率', desc: '数据、方差、树状图' }
  ]);

  /* ============ 一、数与式 ============ */
  T({
    id: 'm-rational', unit: 'm-num', title: '有理数、数轴与绝对值', subtitle: '负数让减法永远做得下去',
    goal: '理解相反数、绝对值与数轴上的距离，熟练有理数四则',
    why: '甲种本第一册第一章「集合」首先要认清 N、Z、Q、R；解析几何的有向线段与定比分点也靠正负方向。',
    view: 'numberline', minutes: 10, prereq: ['p-place', 'p-sub'],
    demo: function () {
      var o = [];
      o.push(S('在数轴上，0 右边为正，左边为负。<b>−3</b> 与 <b>+3</b> 关于原点对称。',
        { min: -5, max: 5, points: [{ x: -3, label: '−3', cls: 'is-hi' }, { x: 3, label: '+3' }], caption: '相反数：只有方向不同' }));
      o.push(S('<b>|a|</b> 是 a 到原点的<b>距离</b>，所以永远非负：|−3| = 3，|3| = 3。',
        { min: -5, max: 5, points: [{ x: 0, label: '0' }], segments: [{ a: -3, b: 0, label: '|−3| = 3', cls: 'is-hi' }], caption: '绝对值 = 距离' }));
      o.push(S('两数之和为 0 叫互为相反数；引入负数后，<b>3 − 5 = 3 + (−5) = −2</b>，减法总能做。',
        { min: -5, max: 5, points: [{ x: 3, label: '起点 3' }], segments: [{ a: -2, b: 3, label: '向左走 5', cls: 'is-hi' }], caption: '减去一个数 = 加上它的相反数' }));
      o.push(S('比较大小：数轴上<b>右边总比左边大</b>，所以 −2 > −5。',
        { min: -6, max: 2, points: [{ x: -5, label: '−5' }, { x: -2, label: '−2', cls: 'is-hi' }], caption: '−5 < −2 < 0 < 2' }));
      return o;
    },
    notes: [
      '<p>负数的意义是「方向」：欠 5 元、零下 5 度、向左 5 米，都可以用同一个 −5 表示。</p>',
      '<p>绝对值把有方向的量变成非负的距离；<code>|a−b|</code> 就是数轴上 a 与 b 的距离。</p>',
      '<p>甲种本平面解析几何第一章「有向线段、定比分点」把这条数轴搬到平面；不等式 <code>|x−a| &lt; d</code> 的解集也是距离。</p>'
    ],
    example: { q: '求 |−7| 与 |3 − 8|', steps: ['|−7| = 7', '3 − 8 = −5，|−5| = 5'], a: '7 与 5' },
    quiz: [
      { q: '|−4| 的值是？', options: ['−4', '4', '0', '±4'], answer: 1, explain: '绝对值表示到原点的距离，恒非负。' },
      { q: '−3 与 −7 哪个大？', options: ['−7', '−3', '一样大', '无法比较'], answer: 1, explain: '数轴上 −3 在 −7 右边，所以 −3 > −7。' }
    ]
  });

  T({
    id: 'm-real', unit: 'm-num', title: '平方根、立方根与实数', subtitle: '√2 不是分数，但它确实在数轴上',
    goal: '理解无理数，会化简根式，知道实数与数轴一一对应',
    why: '★ 解析几何两点距离、圆锥曲线方程、微积分的极限，都要求接受「不能写成分数的数」。',
    view: 'steps', minutes: 10, star: true, prereq: ['m-rational'],
    demo: function () {
      var o = [];
      o.push(S('问：哪个数的平方等于 2？<b>1²=1，2²=4</b>，答案在 1 和 2 之间。',
        { view: 'numberline', min: 0, max: 2, ticks: [0, 1, 2], points: [{ x: 1.414, label: '√2 ≈ 1.414', cls: 'is-hi' }], caption: '逐步逼近' }));
      o.push(S('继续夹逼：<b>1.4² = 1.96</b>，<b>1.5² = 2.25</b>，所以 1.4 &lt; √2 &lt; 1.5。',
        lines(['1.4² = 1.96  < 2', '1.5² = 2.25  > 2', '√2 = 1.4142135…（无限不循环）'])));
      o.push(S('它<b>不能写成两个整数之比</b>，叫无理数。有理数 + 无理数 = <b>实数</b>。',
        lines(['实数 R', '├─ 有理数 Q（整数、有限小数、循环小数）', '└─ 无理数（√2、π、e … 无限不循环）'])));
      o.push(S('平方根记号：<b>√a</b> 专指非负的那个；方程 x²=9 有两个根 ±3。',
        lines(['√9 = 3（算术平方根）', 'x² = 9  →  x = ±3', '这个 ± 在解一元二次方程时不能丢'])));
      o.push(S('化简：<b>√12 = √(4×3) = 2√3</b>；<b>√a² = |a|</b>（不是 a！）。',
        lines(['√12 = 2√3', '√(a²) = |a|   ← 易错点', '甲种本求距离公式时必然遇到'])));
      return o;
    },
    notes: [
      '<p>无理数的发现曾引发第一次数学危机：正方形对角线无法用「整数之比」度量。</p>',
      '<p>用「平方后比较」夹逼，可以要多精确有多精确 —— 这已经是极限的雏形。</p>',
      '<p>甲种本微积分初步第一章讲极限，正是把这种「无限逼近」变成严格语言；解析几何距离公式 <code>√((x₁−x₂)²+(y₁−y₂)²)</code> 也离不开根式。</p>'
    ],
    example: { q: '化简 √50 与 √( (−3)² )', steps: ['√50 = √(25×2) = 5√2', '√((−3)²) = |−3| = 3'], a: '5√2 与 3' },
    quiz: [
      { q: '√18 化简后是？', options: ['2√3', '3√2', '9√2', '4.5'], answer: 1, explain: '√18 = √(9×2) = 3√2。' },
      { q: '√(a²) 等于？', options: ['a', '−a', '|a|', 'a²'], answer: 2, explain: '算术平方根非负，所以是 |a|。' }
    ]
  });

  T({
    id: 'm-power', unit: 'm-num', title: '幂的运算与科学记数法', subtitle: '指数法则是指数函数和对数的地基',
    goal: '熟练同底数幂、幂的乘方、积的乘方、负指数与零指数',
    why: '★ 甲种本代数1 第三章「幂函数、指数函数和对数函数」全部建立在这些法则上。',
    view: 'steps', minutes: 10, star: true, prereq: ['m-rational', 'p-place'],
    demo: function () {
      var o = [];
      o.push(S('同底数相乘，指数<b>相加</b>：<code>aᵐ · aⁿ = aᵐ⁺ⁿ</code>。',
        lines(['2³ × 2² = (2×2×2) × (2×2)', '= 2⁵ = 32', '指数相加：3 + 2 = 5'])));
      o.push(S('幂的乘方，指数<b>相乘</b>：<code>(aᵐ)ⁿ = aᵐⁿ</code>。',
        lines(['(2³)² = 2³ × 2³ = 2⁶ = 64', '积的乘方：(ab)ⁿ = aⁿbⁿ'])));
      o.push(S('同底数相除，指数<b>相减</b>：<code>aᵐ ÷ aⁿ = aᵐ⁻ⁿ</code>。',
        lines(['2⁵ ÷ 2² = 2³', '那 2² ÷ 2⁵ = ?  指数变成 −3'])));
      o.push(S('为使法则继续成立，定义 <b>a⁰ = 1</b>、<b>a⁻ⁿ = 1/aⁿ</b>（a≠0）。',
        lines(['2⁰ = 1', '2⁻³ = 1/2³ = 1/8', '负指数 = 倒数，不是负数'])));
      o.push(S('科学记数法：<b>0.000 032 = 3.2 × 10⁻⁵</b>；大数 320 000 = 3.2 × 10⁵。',
        { view: 'grid', cols: 1, rows: 3, cellW: 270, cells: [
          { v: '3.2 × 10⁵  = 320 000', cls: 'is-on' },
          { v: '3.2 × 10⁻⁵ = 0.000 032', cls: 'is-hi' },
          { v: '10⁰ = 1', cls: 'is-done' }] }));
      o.push(S('把整数指数推广到分数：<code>a^(1/2) = √a</code>。这一步就是甲种本的<b>幂函数</b>。',
        lines(['a^(1/2) = √a', 'a^(m/n) = ⁿ√(aᵐ)', 'y = x^α（α 为任意实数）→ 幂函数'])));
      return o;
    },
    notes: [
      '<p>所有指数法则都来自一句话：「aᵐ 是 m 个 a 相乘」，乘起来就数一共有几个 a。</p>',
      '<p>零指数、负指数不是新规定，而是为了「让 aᵐ÷aⁿ = aᵐ⁻ⁿ 在 m&lt;n 时依然成立」而做的延拓。</p>',
      '<p>甲种本代数1 讨论 y = x^α 的定义域、单调性和图象，再用反函数引出对数；分数指数幂是必经之路。</p>'
    ],
    example: { q: '计算 (3²)³ ÷ 3⁴', steps: ['(3²)³ = 3⁶', '3⁶ ÷ 3⁴ = 3²'], a: '9' },
    quiz: [
      { q: 'a⁵ · a³ = ?', options: ['a¹⁵', 'a⁸', 'a²', '2a⁸'], answer: 1, explain: '同底数相乘，指数相加得 a⁸。' },
      { q: '2⁻³ 等于？', options: ['−8', '−6', '1/8', '8'], answer: 2, explain: '负指数表示倒数：1/2³ = 1/8。' }
    ]
  });

  T({
    id: 'm-poly', unit: 'm-num', title: '整式运算与乘法公式', subtitle: '把小学的面积模型换成字母',
    goal: '熟练合并同类项、分配律、平方差与完全平方公式',
    why: '★ 因式分解、二项式定理、圆锥曲线方程展开、求导之前的代数整理都靠这些公式。',
    view: 'shapes', minutes: 11, star: true, prereq: ['m-power', 'p-mul', 'p-letter'],
    demo: function () {
      var o = [];
      o.push(S('合并同类项：<b>3x² + 5x² = 8x²</b>，但 3x² 与 5x 不能合并（不是同类）。',
        { view: 'steps', lines: [
          row('3x² + 5x² = (3+5)x² = 8x²', 'is-done'),
          row('3x² + 5x   不能合并', 'is-dim')] }));
      o.push(S('完全平方公式用面积看：边长 <b>a+b</b> 的正方形分成四块。',
        { view: 'shapes', items: [
          { k: 'rect', x: 180, y: 70, w: 150, h: 150, cls: 'is-on', label: 'a²', labelX: 255, labelY: 150 },
          { k: 'rect', x: 330, y: 70, w: 100, h: 150, cls: 'is-hi', label: 'ab', labelX: 380, labelY: 150 },
          { k: 'rect', x: 180, y: 220, w: 150, h: 100, cls: 'is-hi', label: 'ab', labelX: 255, labelY: 275 },
          { k: 'rect', x: 330, y: 220, w: 100, h: 100, cls: 'is-done', label: 'b²', labelX: 380, labelY: 275 },
          { k: 'text', x: 320, y: 45, t: '边长 a + b', cls: '' }
        ], caption: 'a² + 2ab + b²' }));
      o.push(S('所以 <b>(a+b)² = a² + 2ab + b²</b>。注意中间那项<b>不能丢</b>。',
        { view: 'steps', lines: [
          row('(a+b)² = a² + 2ab + b²', 'is-hi'),
          row('(a−b)² = a² − 2ab + b²', 'is-on'),
          row('常见错误：(a+b)² = a² + b²  ✗', 'is-dim')] }));
      o.push(S('平方差：<b>(a+b)(a−b) = a² − b²</b>，交叉项正好抵消。',
        { view: 'steps', lines: [
          row('(a+b)(a−b) = a² − ab + ab − b²'),
          row('= a² − b²', 'is-done')] }));
      o.push(S('代入检验：a=5, b=2，(5+2)² = 49，而 5²+2² = 29 —— <b>公式记错一算就知道</b>。',
        { view: 'steps', lines: [
          row('(5+2)² = 49'),
          row('5² + 2·5·2 + 2² = 25+20+4 = 49 ✓', 'is-done')] }));
      return o;
    },
    notes: [
      '<p>整式运算只有两条依据：合并同类项（单位相同才能加）、分配律（每项都要乘到）。</p>',
      '<p>三个乘法公式要能双向使用：从左到右是展开，从右到左就是因式分解。</p>',
      '<p>甲种本代数3 的二项式定理是 (a+b)ⁿ 的一般化，解析几何里把直线代入圆/椭圆后展开，也全靠这些公式不出错。</p>'
    ],
    example: { q: '展开 (2x + 3)²', steps: ['= (2x)² + 2·(2x)·3 + 3²'], a: '4x² + 12x + 9' },
    quiz: [
      { q: '(x + 4)² 展开是？', options: ['x² + 16', 'x² + 8x + 16', 'x² + 4x + 16', 'x² + 8x + 8'], answer: 1, explain: '中间项 2·x·4 = 8x。' },
      { q: '(a + b)(a − b) = ?', options: ['a² + b²', 'a² − 2ab + b²', 'a² − b²', 'a² + ab − b²'], answer: 2, explain: '交叉项抵消，得平方差。' }
    ]
  });

  T({
    id: 'm-factor', unit: 'm-num', title: '因式分解', subtitle: '把多项式拆成因式的乘积',
    goal: '掌握提公因式、公式法、十字相乘，能分解二次三项式',
    why: '★★ 甲种本代数3「一元多项式与高次方程」、解析几何联立后求根、微积分因式约分，全都卡在这一步。',
    view: 'steps', minutes: 14, star: true, prereq: ['m-poly', 'p-factor'],
    demo: function () {
      var o = [];
      o.push(S('因式分解是整式乘法的<b>逆运算</b>：把和差变回乘积。',
        lines(['展开：  (x+2)(x+3) = x² + 5x + 6', '分解：  x² + 5x + 6 = (x+2)(x+3)'])));
      o.push(S('第一招 <b>提公因式</b>：6x² + 9x = 3x(2x + 3)。',
        lines(['6x² + 9x', '= 3x · 2x + 3x · 3', '= 3x(2x + 3)', '← 先找每一项都有的因子'])));
      o.push(S('第二招 <b>公式法</b>：平方差、完全平方。',
        lines(['x² − 9 = (x+3)(x−3)', 'x² + 6x + 9 = (x+3)²', 'x² − 4x + 4 = (x−2)²'])));
      o.push(S('第三招 <b>十字相乘</b>：分解 x² + 5x + 6，要找 p·q = 6 且 p+q = 5。',
        { view: 'grid', cols: 3, rows: 3, cellW: 62, cells: [
          { v: 'p·q = 6', cls: 'is-on' }, { v: 'p+q = 5', cls: 'is-on' }, { v: '待定', cls: 'is-pending' },
          { v: '1 × 6', cls: '' }, { v: '和 = 7', cls: '' }, { v: '✗', cls: 'is-void' },
          { v: '2 × 3', cls: 'is-hi' }, { v: '和 = 5', cls: 'is-hi' }, { v: '✓', cls: 'is-done' }],
          caption: '试出 p=2, q=3' }));
      o.push(S('所以 <b>x² + 5x + 6 = (x+2)(x+3)</b>。验算展开即可确认。',
        lines(['(x+2)(x+3) = x² + 3x + 2x + 6', '= x² + 5x + 6 ✓'])));
      o.push(S('分解到<b>不能再分为止</b>：2x³ − 8x = 2x(x²−4) = <b>2x(x+2)(x−2)</b>。',
        lines(['2x³ − 8x', '= 2x(x² − 4)', '= 2x(x+2)(x−2)   ← 平方差别漏掉'])));
      return o;
    },
    notes: [
      '<p>顺序永远是：先提公因式 → 再看公式 → 最后十字相乘 / 分组。分解完要检查每个因式还能不能再分。</p>',
      '<p>十字相乘的本质是韦达定理的雏形：p+q = 一次项系数，pq = 常数项。</p>',
      '<p>甲种本代数3 讲因式定理「若 f(a)=0 则 (x−a) 是因式」、高次方程求根；解析几何里直线与圆锥曲线联立后也靠分解求交点。</p>'
    ],
    example: { q: '分解 x² − 7x + 12', steps: ['找 p·q = 12、p+q = −7', 'p = −3, q = −4'], a: '(x − 3)(x − 4)' },
    quiz: [
      { q: 'x² − 5x + 6 分解是？', options: ['(x−2)(x−3)', '(x+2)(x+3)', '(x−1)(x−6)', '(x−6)(x+1)'], answer: 0, explain: '(−2)+(−3) = −5，(−2)(−3) = 6。' },
      { q: '4x² − 25 分解是？', options: ['(4x−5)(x+5)', '(2x−5)(2x+5)', '(2x−5)²', '(4x+5)(x−5)'], answer: 1, explain: '平方差：a=2x, b=5。' }
    ]
  });

  T({
    id: 'm-frac-expr', unit: 'm-num', title: '分式与二次根式', subtitle: '分母含字母时，先想清楚谁不能为 0',
    goal: '会分式化简、通分、有理化，理解增根',
    why: '★ 甲种本求导后的通分、换底公式、圆锥曲线方程整理，出错绝大多数在这一步。',
    view: 'steps', minutes: 11, star: true, prereq: ['m-factor', 'm-real'],
    demo: function () {
      var o = [];
      o.push(S('分式 <code>(x²−4)/(x−2)</code>：先分解再约，注意 <b>x ≠ 2</b>。',
        lines(['(x² − 4)/(x − 2)', '= (x+2)(x−2)/(x−2)', '= x + 2   （x ≠ 2）', '← 定义域不能随手丢掉'])));
      o.push(S('分式加减要通分：<code>1/x + 1/y = (x+y)/(xy)</code>。',
        lines(['1/x + 1/y', '= y/(xy) + x/(xy)', '= (x + y)/(xy)'])));
      o.push(S('解分式方程要<b>验根</b>：两边同乘含 x 的式子，可能引入使分母为 0 的假根。',
        lines(['1/(x−1) = 2/(x−1)  → 两边乘 (x−1)', '得 1 = 2，无解', '若解出 x=1，必须舍去（增根）'])));
      o.push(S('分母有理化：<code>1/√2 = √2/2</code>，分子分母同乘 √2。',
        lines(['1/√2 = (1×√2)/(√2×√2)', '= √2 / 2', '共轭相乘：(a+√b)(a−√b) = a² − b'])));
      o.push(S('这里用的还是小学那条「同乘不变」：<b>分式基本性质</b>。',
        { view: 'grid', cols: 1, rows: 2, cellW: 320, cells: [
          { v: '小学：2/3 = 4/6（分子分母同乘 2）', cls: 'is-on' },
          { v: '初中：a/b = ac/bc（c ≠ 0）', cls: 'is-hi' }],
          caption: '同一条规则，只是把数字换成字母' }));
      return o;
    },
    notes: [
      '<p>分式的每次变形都要保证分母不为 0，这是与整式运算最大的区别。</p>',
      '<p>化简顺序：先分解因式 → 再找公分母 → 再约分。</p>',
      '<p>甲种本微积分初步中 <code>(u/v)′</code> 的推导、代数1 的换底公式、解析几何联立后的整理，本质都是反复通分与约分。</p>'
    ],
    example: { q: '化简 (x² − 9)/(x + 3) 并写出限制条件', steps: ['分子分解为 (x+3)(x−3)', '约去 (x+3)'], a: 'x − 3，且 x ≠ −3' },
    quiz: [
      { q: '化简 (x²−1)/(x−1) 的结果是？', options: ['x−1', 'x+1（x≠1）', '1', 'x²'], answer: 1, explain: '分解为 (x+1)(x−1)，约分后 x+1，且 x≠1。' },
      { q: '1/(x−2) 中 x 不能取？', options: ['0', '1', '2', '−2'], answer: 2, explain: 'x = 2 时分母为 0，无意义。' }
    ]
  });

  /* ============ 二、方程与不等式 ============ */
  T({
    id: 'm-eq-sys', unit: 'm-eq', title: '方程组与消元', subtitle: '两个未知数，就设法先消掉一个',
    goal: '熟练代入消元与加减消元，理解方程组的几何意义',
    why: '甲种本代数2「行列式和线性方程组」把消元系统化；解析几何求两条直线交点就是解方程组。',
    view: 'steps', minutes: 10, prereq: ['p-letter', 'm-poly'],
    demo: function () {
      var o = [];
      o.push(S('解方程组：<b>x + y = 7</b> 且 <b>x − y = 1</b>。',
        lines(['①  x + y = 7', '②  x − y = 1'])));
      o.push(S('加减消元：① + ②，y 与 −y 抵消 → <b>2x = 8</b>。',
        lines(['① + ② :  2x = 8', 'x = 4', '← 消元的核心：制造相反系数'])));
      o.push(S('回代：4 + y = 7 → <b>y = 3</b>。',
        lines(['x = 4 代入 ①', '4 + y = 7', 'y = 3'])));
      o.push(S('验算：4+3=7 ✓，4−3=1 ✓。',
        lines(['解为 (x, y) = (4, 3)', '几何上：两条直线的交点'])));
      o.push(S('把两条直线画出来，方程组的解就是<b>交点坐标</b>。',
        { view: 'axis', range: { x: [-1, 8], y: [-1, 8] }, curves: [
          { pts: curve(function (x) { return 7 - x; }, -1, 8, 20), cls: '', label: 'x+y=7' },
          { pts: curve(function (x) { return x - 1; }, -1, 8, 20), cls: 'is-hi', label: 'x−y=1' }
        ], points: [{ x: 4, y: 3, label: '(4,3)', cls: 'is-hi' }], caption: '代数 ↔ 几何的第一次会合' }));
      return o;
    },
    notes: [
      '<p>消元思想：把「两个未知数」变成「一个未知数」这个已经会解的问题，这就是化归。</p>',
      '<p>代入消元适合某个未知数系数为 1；加减消元适合系数相同或相反。</p>',
      '<p>甲种本平面解析几何第一章「两条直线的位置关系」、代数2 的行列式与线性方程组，都是把这件事推广到一般情形。</p>'
    ],
    example: { q: '解 2x + y = 8，x − y = 1', steps: ['两式相加：3x = 9，x = 3', '代回：3 − y = 1，y = 2'], a: '(3, 2)' },
    quiz: [
      { q: '方程组 x+y=5, x−y=1 的解是？', options: ['(2,3)', '(3,2)', '(4,1)', '(1,4)'], answer: 1, explain: '相加得 2x=6，x=3，y=2。' },
      { q: '二元一次方程组的解在图像上对应？', options: ['两条直线', '两直线交点', '一个区域', '原点'], answer: 1, explain: '同时满足两个方程的点就是交点。' }
    ]
  });

  T({
    id: 'm-eq2', unit: 'm-eq', title: '一元二次方程与判别式', subtitle: '配方 → 求根公式 → Δ → 韦达定理',
    goal: '掌握四种解法，理解判别式与根与系数的关系',
    why: '★★ 解析几何里直线与圆锥曲线联立必然得到一元二次方程；甲种本代数3 高次方程也以它为模板。',
    view: 'steps', minutes: 15, star: true, prereq: ['m-factor', 'm-real'],
    demo: function () {
      var o = [];
      o.push(S('解 <b>x² + 6x + 5 = 0</b>。先试因式分解：找 p+q=6、pq=5。',
        lines(['x² + 6x + 5 = (x+1)(x+5)', 'x = −1 或 x = −5'])));
      o.push(S('不是所有式子都好分解，于是学<b>配方</b>：把 x²+6x 补成完全平方。',
        lines(['x² + 6x + 5 = 0', 'x² + 6x + 9 − 9 + 5 = 0', '(x+3)² = 4', 'x+3 = ±2  →  x = −1, −5'])));
      o.push(S('对一般式 <code>ax²+bx+c=0</code> 配方，得到<b>求根公式</b>。',
        lines(['x = (−b ± √(b² − 4ac)) / (2a)', 'Δ = b² − 4ac 叫判别式'])));
      o.push(S('<b>Δ</b> 决定根的个数，也决定抛物线与 x 轴有几个交点。',
        { view: 'axis', range: { x: [-4, 4], y: [-3, 6] }, curves: [
          { pts: curve(function (x) { return x * x - 1; }, -2.5, 2.5, 40), cls: '', label: 'Δ>0 两根' },
          { pts: curve(function (x) { return x * x; }, -2.5, 2.5, 40), cls: 'is-dim', label: 'Δ=0 一根' },
          { pts: curve(function (x) { return x * x + 2; }, -2.5, 2.5, 40), cls: 'is-hi', label: 'Δ<0 无实根' }
        ], caption: '判别式的几何含义' }));
      o.push(S('<b>韦达定理</b>：x₁ + x₂ = −b/a，x₁x₂ = c/a。不解方程就能知道两根的和与积。',
        lines(['x² − 5x + 6 = 0', '两根和 = 5，两根积 = 6', '→ 两根是 2 和 3'])));
      return o;
    },
    notes: [
      '<p>配方的要诀：加上并减去「一次项系数一半的平方」，把式子凑成 (x+m)²。</p>',
      '<p>判别式 Δ 是代数（根的个数）与几何（交点个数）之间的桥，这个视角在解析几何里极其重要。</p>',
      '<p>甲种本平面解析几何求直线与椭圆/双曲线/抛物线的交点、判断相切，全部转化为联立后看 Δ；代数2 的复数为 Δ&lt;0 补上复根。</p>'
    ],
    example: { q: '不解方程，求 x² − 7x + 10 = 0 的两根和与积', steps: ['由韦达定理：和 = −b/a = 7', '积 = c/a = 10'], a: '和 7，积 10（两根为 2 和 5）' },
    quiz: [
      { q: '方程 x² − 4x + 4 = 0 的根的情况是？', options: ['两个不等实根', '两个相等实根', '无实根', '一个根为 0'], answer: 1, explain: 'Δ = 16 − 16 = 0，是完全平方 (x−2)²。' },
      { q: 'x² − 3x − 4 = 0 的两根之和是？', options: ['−3', '3', '4', '−4'], answer: 1, explain: '韦达定理：和 = −b/a = 3。' }
    ]
  });

  T({
    id: 'm-ineq', unit: 'm-eq', title: '不等式与解集', subtitle: '两边同乘负数，不等号要转向',
    goal: '会解一元一次不等式（组），能在数轴上表示解集',
    why: '★ 甲种本代数2 第三章「不等式」直接从这里往上讲绝对值不等式、均值不等式与证明。',
    view: 'numberline', minutes: 10, star: true, prereq: ['m-rational', 'p-letter'],
    demo: function () {
      var o = [];
      o.push(S('解 <b>2x − 6 &lt; 0</b>：两边加 6 → 2x &lt; 6 → <b>x &lt; 3</b>。',
        { min: -1, max: 7, ticks: [-1, 0, 1, 2, 3, 4, 5, 6, 7], points: [{ x: 3, label: '3', cls: 'is-hi' }], segments: [{ a: -1, b: 3, label: 'x < 3', cls: 'is-hi' }], caption: '解集是数轴上的一段区间' }));
      o.push(S('<b>关键陷阱</b>：两边同乘（除）以负数，不等号<b>方向必须反转</b>。',
        { view: 'steps', lines: [
          row('−2x < 6'), row('两边 ÷ (−2)： x > −3', 'is-hi'),
          row('验证 x=0：−2·0=0 < 6 ✓', 'is-done')] }));
      o.push(S('为什么？数轴上乘 −1 相当于关于原点<b>翻折</b>，左右次序整体颠倒。',
        { min: -6, max: 6, ticks: [-6, -3, 0, 3, 6], segments: [
          { a: 3, b: 6, label: 'x > 3', cls: '' }, { a: -6, b: -3, label: '−x < −3', cls: 'is-hi', level: 1 }], caption: '翻折后大小关系反转' }));
      o.push(S('不等式组取各个解集的<b>交集</b>：x &gt; 1 且 x &lt; 4 → 1 &lt; x &lt; 4。',
        { min: -1, max: 7, ticks: [-1, 0, 1, 2, 3, 4, 5, 6, 7], segments: [
          { a: 1, b: 7, label: 'x > 1', cls: '' }, { a: -1, b: 4, label: 'x < 4', cls: '', level: 1 },
          { a: 1, b: 4, label: '交集', cls: 'is-hi', level: 2 }], caption: '「且」取交集，「或」取并集' }));
      return o;
    },
    notes: [
      '<p>不等式的变形和等式几乎一样，唯一的区别是乘除负数时方向反转。</p>',
      '<p>解集不是一个数，而是一段区间；画数轴比死记规则可靠得多。</p>',
      '<p>甲种本代数2 讲不等式的性质与证明、含绝对值不等式、均值不等式；微积分里用不等式估计误差与夹逼求极限。</p>'
    ],
    example: { q: '解 −3x + 6 ≤ 0', steps: ['−3x ≤ −6', '两边除以 −3，方向反转'], a: 'x ≥ 2' },
    quiz: [
      { q: '解不等式 −2x > 8', options: ['x > −4', 'x < −4', 'x > 4', 'x < 4'], answer: 1, explain: '除以 −2 要变号，得 x < −4。' },
      { q: '不等式组 x > 2 且 x < 5 的解集是？', options: ['x > 2', 'x < 5', '2 < x < 5', '空集'], answer: 2, explain: '两个条件同时满足，取交集。' }
    ]
  });

  /* ============ 三、函数与坐标 ============ */
  T({
    id: 'm-coord', unit: 'm-func', title: '平面直角坐标系与两点距离', subtitle: '把数轴搬成两张，数就变成了点',
    goal: '会由点写坐标、由坐标描点，掌握两点距离与中点公式',
    why: '★★ 甲种本《平面解析几何》整本书的第一章就是「有向线段、定比分点」，起点正在这里。',
    view: 'axis', minutes: 10, star: true, prereq: ['m-rational', 'm-real'],
    demo: function () {
      var o = [];
      o.push(S('两条互相垂直的数轴组成坐标系：点 <b>P(3, 2)</b> 表示横坐标 3、纵坐标 2。',
        { range: { x: [-1, 6], y: [-1, 5] }, points: [{ x: 3, y: 2, label: 'P(3,2)', cls: 'is-hi' }],
          lines: [{ a: [3, 0], b: [3, 2], cls: 'is-dim' }, { a: [0, 2], b: [3, 2], cls: 'is-dim' }], caption: '先横后纵，顺序不能反' }));
      o.push(S('四个象限的符号：(+,+)、(−,+)、(−,−)、(+,−)。',
        { range: { x: [-4, 4], y: [-4, 4] }, points: [
          { x: 2, y: 2, label: 'Ⅰ (+,+)', cls: 'is-on' }, { x: -2, y: 2, label: 'Ⅱ (−,+)', cls: '' },
          { x: -2, y: -2, label: 'Ⅲ (−,−)', cls: '' }, { x: 2, y: -2, label: 'Ⅳ (+,−)', cls: '' }] }));
      o.push(S('两点 <b>A(1,1)</b>、<b>B(4,5)</b> 的距离：横差 3、纵差 4，构成直角三角形。',
        { range: { x: [-1, 6], y: [-1, 6] }, points: [
          { x: 1, y: 1, label: 'A(1,1)', cls: 'is-on' }, { x: 4, y: 5, label: 'B(4,5)', cls: 'is-hi' }],
          lines: [{ a: [1, 1], b: [4, 1], cls: 'is-dim' }, { a: [4, 1], b: [4, 5], cls: 'is-dim' }, { a: [1, 1], b: [4, 5], cls: 'is-hi' }],
          caption: '勾股定理 + 坐标' }));
      o.push(S('所以 <b>|AB| = √((4−1)² + (5−1)²) = √(9+16) = 5</b>。',
        { view: 'steps', lines: [
          row('|AB| = √((x₂−x₁)² + (y₂−y₁)²)', 'is-hi'),
          row('= √(3² + 4²) = 5', 'is-done'),
          row('中点 M = ((x₁+x₂)/2, (y₁+y₂)/2)', 'is-on')] }));
      return o;
    },
    notes: [
      '<p>坐标把「几何的点」翻译成「代数的数对」，这是解析几何的全部起点。</p>',
      '<p>距离公式就是勾股定理：横差、纵差是两条直角边。</p>',
      '<p>甲种本平面解析几何第一章从有向线段与定比分点出发，第二章「曲线和方程」把圆、椭圆等写成方程 —— 用的就是这一步的翻译能力。</p>'
    ],
    example: { q: '求 A(−1, 2) 与 B(3, 5) 的距离', steps: ['横差 = 4，纵差 = 3', '√(16+9) = √25'], a: '5' },
    quiz: [
      { q: '点 (−3, 4) 在第几象限？', options: ['Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ'], answer: 1, explain: '横负纵正，是第二象限。' },
      { q: 'A(0,0) 与 B(3,4) 的距离是？', options: ['3', '4', '5', '7'], answer: 2, explain: '√(3²+4²) = 5。' }
    ]
  });

  T({
    id: 'm-linear-fn', unit: 'm-func', title: '一次函数 y = kx + b', subtitle: 'k 管倾斜，b 管上下平移',
    goal: '理解斜率的几何意义，会由两点求直线方程',
    why: '★ 甲种本《平面解析几何》第一章「直线的方程」、微积分里导数作为切线斜率，都从这里出发。',
    view: 'axis', minutes: 11, star: true, prereq: ['m-coord', 'p-ratio'],
    demo: function () {
      function pic(items, cap) { return { view: 'axis', range: { x: [-4, 4], y: [-5, 6] }, curves: items, caption: cap }; }
      var o = [];
      o.push(S('<b>b = 0</b> 时 y = kx 过原点；k 是「x 每增加 1，y 增加多少」。',
        pic([
          { pts: [[-4, -4], [4, 4]], cls: '', label: 'k=1' },
          { pts: [[-2, -4], [2, 4]], cls: 'is-hi', label: 'k=2' },
          { pts: [[-4, -2], [4, 2]], cls: 'is-dim', label: 'k=1/2' }
        ], 'k 越大，直线越陡')));
      o.push(S('<b>k &lt; 0</b> 时直线从左上到右下，函数递减。',
        pic([{ pts: [[-4, 4], [4, -4]], cls: 'is-hi', label: 'k=−1' }], '负斜率')));
      o.push(S('改变 <b>b</b> 只会让直线<b>整体上下平移</b>，倾斜程度不变。',
        pic([
          { pts: [[-4, -3], [4, 5]], cls: '', label: 'b=1' },
          { pts: [[-4, -1], [4, 7]], cls: 'is-hi', label: 'b=3' },
          { pts: [[-4, -5], [4, 3]], cls: 'is-dim', label: 'b=−1' }
        ], '相同的 k = 1，互相平行')));
      o.push(S('由两点求 k：<b>k = (y₂−y₁)/(x₂−x₁)</b>，也就是「纵差 ÷ 横差」。',
        { view: 'steps', lines: [
          row('过 (1,2) 与 (3,6)：k = (6−2)/(3−1) = 2', 'is-hi'),
          row('代入 (1,2)：2 = 2×1 + b  →  b = 0', 'is-on'),
          row('所以 y = 2x', 'is-done')] }));
      o.push(S('甲种本会用「倾斜角 α」表示斜率：<b>k = tan α</b>。这与锐角三角函数接上了。',
        { view: 'steps', lines: [
          row('k = Δy / Δx = tan α', 'is-hi'),
          row('导数 f′(x) 就是曲线在该点切线的 k', 'is-done')] }));
      return o;
    },
    notes: [
      '<p>k 是变化率，b 是 x=0 时的值。看到直线先找这两件事。</p>',
      '<p>「纵差 ÷ 横差」与小学的「比值恒定」是同一个量；相似三角形保证直线上任意两点算出的 k 都相同。</p>',
      '<p>甲种本解析几何把它写成点斜式、一般式和 tan α；微积分初步的导数，则是把这个「斜率」推广到曲线上每一点。</p>'
    ],
    example: { q: '求过 (0,3)、(2,7) 的直线方程', steps: ['k = (7−3)/(2−0) = 2', 'b = 3（x=0 时的 y）'], a: 'y = 2x + 3' },
    quiz: [
      { q: '直线 y = −2x + 5 的斜率是？', options: ['5', '2', '−2', '−5'], answer: 2, explain: 'k 是 x 的系数，等于 −2。' },
      { q: '两条直线平行，则它们的？', options: ['b 相同', 'k 相同', '都过原点', '截距相反'], answer: 1, explain: '平行意味着倾斜程度相同，即斜率相等。' }
    ]
  });

  T({
    id: 'm-inverse-fn', unit: 'm-func', title: '反比例函数 y = k/x', subtitle: '乘积恒定，图像是双曲线',
    goal: '理解 k 的符号对分支位置的影响，认识渐近线',
    why: '甲种本代数1「幂函数」里 y = x⁻¹ 是重点；解析几何的双曲线也与它同源。',
    view: 'axis', minutes: 9, prereq: ['m-linear-fn', 'p-ratio'],
    demo: function () {
      var o = [];
      o.push(S('<b>y = 6/x</b>：x 与 y 的乘积恒为 6。列几个点。',
        { view: 'grid', cols: 6, rows: 2, cellW: 52, cells: [
          { v: 'x=1', cls: 'is-on' }, { v: 'x=2', cls: 'is-on' }, { v: 'x=3', cls: 'is-on' },
          { v: 'x=6', cls: 'is-on' }, { v: 'x=−1', cls: 'is-dim' }, { v: 'x=−2', cls: 'is-dim' },
          { v: 'y=6', cls: 'is-hi' }, { v: 'y=3', cls: 'is-hi' }, { v: 'y=2', cls: 'is-hi' },
          { v: 'y=1', cls: 'is-hi' }, { v: 'y=−6', cls: 'is-dim' }, { v: 'y=−3', cls: 'is-dim' }] }));
      o.push(S('描点连成两支曲线：<b>k &gt; 0</b> 时在第一、三象限。',
        { range: { x: [-6, 6], y: [-6, 6] }, curves: [
          { pts: curve(function (x) { return 6 / x; }, 1, 6, 30), cls: '', label: 'y=6/x' },
          { pts: curve(function (x) { return 6 / x; }, -6, -1, 30), cls: '' }
        ], caption: 'x 不能取 0' }));
      o.push(S('x 越接近 0，|y| 越大；x 越大，y 越接近 0 —— 两条坐标轴是<b>渐近线</b>。',
        { range: { x: [-6, 6], y: [-6, 6] }, curves: [
          { pts: curve(function (x) { return 6 / x; }, 0.9, 6, 40), cls: 'is-hi' },
          { pts: curve(function (x) { return 6 / x; }, -6, -0.9, 40), cls: 'is-hi' }
        ], points: [{ x: 1, y: 6, label: '(1,6)', cls: 'is-on' }], caption: '永远不与坐标轴相交' }));
      o.push(S('这就是小学「反比例」的图像版，也是甲种本幂函数 <b>y = x⁻¹</b>。',
        { view: 'steps', lines: [
          row('小学：  xy = k（乘积恒定）', 'is-on'),
          row('初中：  y = k/x（反比例函数）', 'is-on'),
          row('甲种本：y = x⁻¹（幂函数 α = −1）', 'is-hi')] }));
      return o;
    },
    notes: [
      '<p>反比例函数定义域不含 0，图像由两支组成，且不连续 —— 与一次函数很不一样。</p>',
      '<p>k &gt; 0 分支在Ⅰ、Ⅲ象限，k &lt; 0 在Ⅱ、Ⅳ象限；每支上 y 随 x 增大而减小（k&gt;0 时）。</p>',
      '<p>甲种本代数1 讨论幂函数 y=x^α 的图象与性质时，α=−1 是最典型的非单调整体例子；解析几何里等轴双曲线也是它。</p>'
    ],
    example: { q: 'y = k/x 过点 (2, 5)，求 k', steps: ['k = xy', '= 2 × 5'], a: 'k = 10' },
    quiz: [
      { q: '反比例函数 y = 12/x 的图像在哪些象限？', options: ['Ⅰ、Ⅱ', 'Ⅰ、Ⅲ', 'Ⅱ、Ⅳ', 'Ⅲ、Ⅳ'], answer: 1, explain: 'k = 12 > 0，在 first 与 third 象限。' },
      { q: 'y = 3/x 中 x 可以取 0 吗？', options: ['可以，y=0', '可以，y 无穷大', '不可以', '取决于 k'], answer: 2, explain: '分母不能为 0，x=0 不在定义域。' }
    ]
  });

  T({
    id: 'm-quad-fn', unit: 'm-func', title: '二次函数与抛物线', subtitle: '顶点、对称轴、与 x 轴的交点',
    goal: '会配方求顶点，理解系数 a、判别式对图像的影响',
    why: '★★ 甲种本《平面解析几何》第二章「抛物线」直接以它为原型；导数应用里的极值也先在这里建立直觉。',
    view: 'axis', minutes: 13, star: true, prereq: ['m-eq2', 'm-linear-fn'],
    demo: function () {
      var o = [];
      o.push(S('<b>y = x²</b>：把 (−3,9) 到 (3,9) 的点描出来，得到关于 y 轴对称的抛物线。',
        { range: { x: [-4, 4], y: [-2, 10] }, curves: [
          { pts: curve(function (x) { return x * x; }, -3.1, 3.1, 50), cls: '', label: 'y=x²' }
        ], points: [{ x: 0, y: 0, label: '顶点 (0,0)', cls: 'is-hi' }], caption: 'a > 0 开口向上' }));
      o.push(S('配方 <b>y = x² − 4x + 3 = (x−2)² − 1</b>，立刻读出顶点 <b>(2, −1)</b> 与对称轴 x=2。',
        { range: { x: [-2, 6], y: [-3, 8] }, curves: [
          { pts: curve(function (x) { return x * x - 4 * x + 3; }, -1, 5, 50), cls: '', label: 'y=x²−4x+3' }
        ], lines: [{ a: [2, -3], b: [2, 8], cls: 'is-dim', label: 'x=2' }],
          points: [{ x: 2, y: -1, label: '(2,−1)', cls: 'is-hi' }], caption: '配方 → 顶点式' }));
      o.push(S('与 x 轴交点就是 <b>x² − 4x + 3 = 0</b> 的根：x=1、x=3，对应 Δ = 4 &gt; 0。',
        { range: { x: [-2, 6], y: [-3, 8] }, curves: [
          { pts: curve(function (x) { return x * x - 4 * x + 3; }, -1, 5, 50), cls: '' }
        ], points: [{ x: 1, y: 0, label: 'x=1', cls: 'is-hi' }, { x: 3, y: 0, label: 'x=3', cls: 'is-hi' }],
          caption: '函数零点 ↔ 方程根 ↔ 图像交点' }));
      o.push(S('Δ = 0 时顶点正好落在 x 轴上（相切）；Δ &lt; 0 时整条抛物线在 x 轴上方。',
        { range: { x: [-4, 4], y: [-2, 8] }, curves: [
          { pts: curve(function (x) { return x * x; }, -3, 3, 40), cls: '', label: 'Δ=0' },
          { pts: curve(function (x) { return x * x + 2; }, -3, 3, 40), cls: 'is-hi', label: 'Δ<0' },
          { pts: curve(function (x) { return x * x - 2; }, -3, 3, 40), cls: 'is-dim', label: 'Δ>0' }
        ] }));
      o.push(S('甲种本解析几何里的抛物线 <b>y² = 2px</b> 只是把它转了 90°；微积分里顶点就是导数为 0 的点。',
        { view: 'steps', lines: [
          row('顶点横坐标 x = −b/(2a)', 'is-hi'),
          row('此点切线斜率 = 0  →  f′(x) = 0', 'is-done')] }));
      return o;
    },
    notes: [
      '<p>配成 y = a(x−h)² + k 后，顶点 (h,k)、对称轴 x=h、最值 k 都能直接读出来。</p>',
      '<p>「函数零点 = 方程的根 = 图像与 x 轴交点」是三位一体，判别式是它们的开关。</p>',
      '<p>甲种本解析几何第二章讲圆锥曲线时，抛物线作为到定点与定直线等距的轨迹出现；微积分初步第三章用导数求极值，第一个例子往往就是二次函数。</p>'
    ],
    example: { q: '求 y = x² + 2x − 3 的顶点与零点', steps: ['配方 = (x+1)² − 4，顶点 (−1, −4)', '解 x²+2x−3=0 → (x+3)(x−1)=0'], a: '顶点 (−1,−4)，零点 x=−3 与 x=1' },
    quiz: [
      { q: 'y = (x − 3)² + 2 的顶点是？', options: ['(3,2)', '(−3,2)', '(3,−2)', '(2,3)'], answer: 0, explain: '顶点式 y=a(x−h)²+k 的顶点是 (h,k)。' },
      { q: '抛物线 y = x² + 1 与 x 轴有几个交点？', options: ['0', '1', '2', '3'], answer: 0, explain: 'x²+1=0 的 Δ = −4 < 0，无实根，图像整体在 x 轴上方。' }
    ]
  });

  T({
    id: 'm-transform', unit: 'm-func', title: '图像平移与对称', subtitle: '左加右减，上加下减',
    goal: '掌握 y=f(x±a)、y=f(x)±b 的平移规律与关于坐标轴/原点对称',
    why: '★ 甲种本《平面解析几何》第三章「坐标变换：平移和旋转」就是这套规律的系统化。',
    view: 'axis', minutes: 11, star: true, prereq: ['m-quad-fn'],
    demo: function () {
      function p(f, cls, label) { return { pts: curve(f, -2.5, 4.5, 50), cls: cls, label: label }; }
      var o = [];
      o.push(S('把 <b>y = x²</b> 与 <b>y = (x−2)²</b> 画在一起：图像整体<b>向右移 2</b>。',
        { range: { x: [-3, 5], y: [-1, 9] }, curves: [
          p(function (x) { return x * x; }, 'is-dim', 'y=x²'),
          p(function (x) { return (x - 2) * (x - 2); }, 'is-hi', 'y=(x−2)²')],
          caption: 'x 换成 x−2 → 右移 2（左加右减）' }));
      o.push(S('再看 <b>y = x² + 2</b>：整体<b>上移 2</b>。',
        { range: { x: [-3, 5], y: [-1, 9] }, curves: [
          p(function (x) { return x * x; }, 'is-dim', 'y=x²'),
          p(function (x) { return x * x + 2; }, 'is-hi', 'y=x²+2')],
          caption: '在函数值外加 → 上加下减' }));
      o.push(S('关于 x 轴对称：y → −y；关于 y 轴对称：x → −x；关于原点：两者都换。',
        { range: { x: [-3, 5], y: [-9, 9] }, curves: [
          p(function (x) { return x * x - 4; }, 'is-dim', 'y=x²−4'),
          p(function (x) { return -(x * x - 4); }, 'is-hi', 'y=−x²+4')],
          caption: '开口翻向下方' }));
      o.push(S('坐标平移公式：新原点移到 (h,k) 时，<b>x = X + h，y = Y + k</b>。',
        { view: 'steps', lines: [
          row('点 P(x, y) 在新系中为 (X, Y)', 'is-on'),
          row('x = X + h,   y = Y + k', 'is-hi'),
          row('代入原方程即得新方程', 'is-done')] }));
      o.push(S('甲种本用这个把一般二次方程化成标准形，从而识别它是椭圆、双曲线还是抛物线。',
        { view: 'steps', lines: [
          row('x² + y² − 2x − 4y + 1 = 0', 'is-dim'),
          row('配方 → (x−1)² + (y−2)² = 4', 'is-hi'),
          row('圆心 (1,2)，半径 2 的圆', 'is-done')] }));
      return o;
    },
    notes: [
      '<p>「左加右减」容易记反：想让图像在 x=2 处取得原来 x=0 的值，就要把 x 换成 x−2。</p>',
      '<p>平移不改变形状，只改变位置；对称会改变朝向。这是坐标变换里最基础的两类。</p>',
      '<p>甲种本平面解析几何第三章先讲平移与旋转，再讨论一般二元二次方程的化简；圆锥曲线的标准方程都由配方与平移得到。</p>'
    ],
    example: { q: '把 y = x² 向左移 3、向下移 1，写出新方程', steps: ['左移 3：x → x+3', '下移 1：整体 −1'], a: 'y = (x+3)² − 1' },
    quiz: [
      { q: 'y = (x − 5)² 是把 y = x² 怎样移动得到的？', options: ['左移 5', '右移 5', '上移 5', '下移 5'], answer: 1, explain: 'x 减 5 对应图像右移 5。' },
      { q: '方程 x² + y² − 4x = 0 配方后表示？', options: ['圆心 (0,0) 半径 2', '圆心 (2,0) 半径 2', '圆心 (−2,0) 半径 2', '抛物线'], answer: 1, explain: '(x−2)² + y² = 4，圆心 (2,0)，半径 2。' }
    ]
  });

  /* ============ 四、平面几何 ============ */
  T({
    id: 'm-lines-angle', unit: 'm-geo', title: '平行线、相交线与三角形内角和', subtitle: '几何证明从这里开始',
    goal: '会用同位角/内错角、对顶角，证明三角形内角和 180°',
    why: '★ 立体几何第一章「空间两条直线 / 空间直线和平面」把平面里的平行与垂直推广到三维。',
    view: 'shapes', minutes: 9, prereq: ['p-angle'],
    demo: function () {
      var o = [];
      o.push(S('两条平行线被第三条直线所截，<b>同位角相等、内错角相等</b>。',
        { items: [
          { k: 'line', x1: 100, y1: 90, x2: 540, y2: 90, cls: '' },
          { k: 'line', x1: 100, y1: 210, x2: 540, y2: 210, cls: '' },
          { k: 'line', x1: 200, y1: 40, x2: 440, y2: 260, cls: 'is-hi' },
          { k: 'text', x: 265, y: 112, t: '∠1', cls: '' },
          { k: 'text', x: 385, y: 190, t: '∠2', cls: '' },
          { k: 'text', x: 320, y: 32, t: '∠1 = ∠2（内错角）', cls: '' }
        ], caption: '平行 ⇒ 角相等；反过来角相等 ⇒ 平行' }));
      o.push(S('三角形内角和：过顶点作一条<b>平行于底边</b>的直线。',
        { items: [
          { k: 'poly', pts: [[200, 220], [440, 220], [320, 100]], cls: 'is-on' },
          { k: 'line', x1: 150, y1: 100, x2: 500, y2: 100, cls: 'is-hi' },
          { k: 'text', x: 320, y: 60, t: '过顶点作平行线', cls: '' }
        ], caption: '把三个角搬到同一条直线上' }));
      o.push(S('利用内错角，三角形的三个角正好拼成<b>平角 180°</b>。',
        { items: [
          { k: 'rect', x: 150, y: 110, w: 340, h: 56, rx: 8, cls: 'is-done' },
          { k: 'text', x: 320, y: 145, t: '∠A + ∠B + ∠C = 180°', cls: '' },
          { k: 'text', x: 320, y: 210, t: '这是所有「角度计算」的起点', cls: '' }
        ], caption: '三角形内角和定理' }));
      o.push(S('推论：外角等于不相邻两内角之和；n 边形内角和 = (n−2)×180°。',
        { view: 'steps', lines: [
          row('三角形 180°，四边形 360°', 'is-on'),
          row('n 边形内角和 (n−2) × 180°', 'is-hi')] }));
      return o;
    },
    notes: [
      '<p>几何证明的套路是「用已知相等关系搬角」，平行线是最常用的搬运工具。</p>',
      '<p>三角形内角和 180° 只在平面（欧氏几何）成立；甲种本立体几何会讨论空间中的类似问题。</p>',
      '<p>甲种本立体几何第一章「平面、空间两条直线、空间直线和平面」，判定与性质定理几乎都是把这里的平行垂直关系加上「不在同一平面」的条件。</p>'
    ],
    example: { q: '三角形两角为 50° 和 65°，第三角？', steps: ['180° − 50° − 65°'], a: '65°' },
    quiz: [
      { q: '两直线平行，同旁内角之和是？', options: ['90°', '180°', '270°', '不确定'], answer: 1, explain: '同旁内角互补，和为 180°。' },
      { q: '五边形内角和是？', options: ['360°', '540°', '720°', '900°'], answer: 1, explain: '(5−2)×180° = 540°。' }
    ]
  });

  T({
    id: 'm-congruent', unit: 'm-geo', title: '全等三角形', subtitle: '能完全重合的两个三角形',
    goal: '掌握 SSS、SAS、ASA、AAS、HL 判定，会写证明链条',
    why: '相似、解直角三角形、立体几何中的距离与角，都要先会用全等把未知量搬到可算的位置。',
    view: 'shapes', minutes: 10, prereq: ['m-lines-angle'],
    demo: function () {
      function tri(x, cls) {
        return { items: [
          { k: 'poly', pts: [[x, 210], [x + 170, 210], [x + 60, 80]], cls: cls },
          { k: 'text', x: x + 85, y: 250, t: '底边', cls: '' }
        ] };
      }
      var o = [];
      o.push(S('两个三角形<b>形状大小完全相同</b>，能重合，就叫全等，记为 ≌。', tri(90, 'is-on')));
      o.push(S('判定一 <b>SSS</b>：三边对应相等，形状就被唯一确定。',
        { items: [
          { k: 'poly', pts: [[90, 210], [260, 210], [150, 80]], cls: 'is-on', label: '3,4,5', labelX: 175, labelY: 165 },
          { k: 'poly', pts: [[350, 210], [520, 210], [410, 80]], cls: 'is-hi', label: '3,4,5', labelX: 435, labelY: 165 },
          { k: 'text', x: 320, y: 45, t: '三边确定 ⇒ 三角形唯一', cls: '' }
        ], caption: '这也是三角形稳定性的原因' }));
      o.push(S('其余判定：<b>SAS</b>（两边及夹角）、<b>ASA / AAS</b>（两角一边）、<b>HL</b>（直角三角形斜边直角边）。',
        { view: 'grid', cols: 2, rows: 2, cellW: 150, cells: [
          { v: 'SSS 三边', cls: 'is-on' }, { v: 'SAS 两边夹角', cls: 'is-on' },
          { v: 'ASA / AAS 两角一边', cls: 'is-hi' }, { v: 'HL 直角三角形', cls: 'is-hi' }] }));
      o.push(S('注意 <b>SSA 不能判定</b>全等（可能画出两个不同的三角形），AAA 也只能判相似。',
        { view: 'steps', lines: [
          row('SSA ✗   AAA ✗（只保证形状）', 'is-hi'),
          row('全等 ⇒ 对应边、对应角都相等', 'is-done')] }));
      return o;
    },
    notes: [
      '<p>全等是最强的「相等」：一旦证明全等，所有对应边和角都可以直接搬用。</p>',
      '<p>证明时先列出已知，再找缺的条件，最后套一个判定定理。</p>',
      '<p>甲种本立体几何里证明两条空间直线相等、两个角相等，常用「构造全等三角形」把空间问题拉回平面。</p>'
    ],
    example: { q: '已知 AB=DE, AC=DF, ∠A=∠D，能判定 △ABC ≌ △DEF 吗？', steps: ['两边及其夹角对应相等', '符合 SAS'], a: '能，由 SAS 判定全等' },
    quiz: [
      { q: '下列不能判定三角形全等的是？', options: ['SSS', 'SAS', 'ASA', 'SSA'], answer: 3, explain: 'SSA 可能出现两种不同三角形。' },
      { q: '全等三角形的对应角？', options: ['互补', '相等', '成比例', '不确定'], answer: 1, explain: '全等即完全重合，对应角相等。' }
    ]
  });

  T({
    id: 'm-similar', unit: 'm-geo', title: '相似三角形与比例线段', subtitle: '形状相同，大小可以不同',
    goal: '掌握 AA 判定、相似比、对应边成比例，理解平行线分线段成比例',
    why: '★★ 锐角三角函数、直线斜率、解析几何定比分点、圆锥曲线的缩放，全部建立在「比值不变」上。',
    view: 'shapes', minutes: 12, star: true, prereq: ['m-congruent', 'p-ratio'],
    demo: function () {
      var o = [];
      o.push(S('两个三角形<b>三个角对应相等</b>，就相似：形状一样，边长按同一倍数缩放。',
        { items: [
          { k: 'poly', pts: [[110, 210], [270, 210], [110, 90]], cls: 'is-on', label: '3-4-5', labelX: 185, labelY: 170 },
          { k: 'poly', pts: [[360, 210], [600, 210], [360, 30]], cls: 'is-hi', label: '6-8-10', labelX: 470, labelY: 150 },
          { k: 'text', x: 320, y: 265, t: '相似比 k = 2', cls: '' }
        ], caption: '对应边成比例：6/3 = 8/4 = 10/5 = 2' }));
      o.push(S('判定：两角对应相等（<b>AA</b>）即可；平行于三角形一边的直线截出相似三角形。',
        { items: [
          { k: 'poly', pts: [[200, 230], [440, 230], [300, 70]], cls: 'is-on' },
          { k: 'line', x1: 250, y1: 150, x2: 370, y2: 150, cls: 'is-hi' },
          { k: 'text', x: 320, y: 45, t: 'DE ∥ BC  ⇒  △ADE ∽ △ABC', cls: '' }
        ], caption: '平行线截出相似' }));
      o.push(S('关键性质：<b>对应边之比相等</b>，与具体大小无关 —— 这正是斜率 k 恒定的原因。',
        { view: 'steps', lines: [
          row('AD/AB = AE/AC = DE/BC = k', 'is-hi'),
          row('直线上任意两点：Δy/Δx 恒相同', 'is-on'),
          row('所以一次函数图像是直线', 'is-done')] }));
      o.push(S('面积比 = <b>相似比的平方</b>（长度 ×2 → 面积 ×4）。',
        { view: 'grid', cols: 1, rows: 2, cellW: 300, cells: [
          { v: '长度比 = k', cls: 'is-on' },
          { v: '面积比 = k²   体积比 = k³', cls: 'is-hi' }],
          caption: '和单位换算的 ×100、×1000 是同一件事' }));
      return o;
    },
    notes: [
      '<p>相似把「相等」放宽成「成比例」，是几何里最有力的工具之一。</p>',
      '<p>AA 判定最常用：只要找到两组对应角相等（平行线、公共角、对顶角都好用）。</p>',
      '<p>斜率的合理性、锐角三角函数的定义（比值只与角有关）、甲种本解析几何的定比分点，根子都在相似三角形。</p>'
    ],
    example: { q: '两相似三角形相似比 3:5，面积比？', steps: ['面积比 = (3/5)²'], a: '9 : 25' },
    quiz: [
      { q: '两个相似三角形对应边比 2:3，面积比是？', options: ['2:3', '4:9', '3:2', '8:27'], answer: 1, explain: '面积比是相似比的平方。' },
      { q: '判定两三角形相似，最常用的是？', options: ['SSS', 'AA', 'HL', 'SAS 全等'], answer: 1, explain: '两角对应相等即可判相似。' }
    ]
  });

  T({
    id: 'm-pyth', unit: 'm-geo', title: '勾股定理', subtitle: 'a² + b² = c²，面积事实而非口诀',
    goal: '会用面积拼图理解定理，掌握逆定理与常见勾股数',
    why: '★ 距离公式、三角函数恒等式 sin²+cos²=1、单位圆、空间两点距离都从这里来。',
    view: 'grid', minutes: 10, star: true, prereq: ['m-real', 'p-area-tri'],
    demo: function () {
      var o = [];
      o.push(S('直角三角形两直角边 a=3、b=4，斜边 c=5。以三边为边长向外作正方形。',
        { view: 'shapes', items: [
          { k: 'poly', pts: [[280, 100], [400, 100], [280, 190]], cls: 'is-on' },
          { k: 'rect', x: 190, y: 190, w: 90, h: 90, cls: 'is-hi', label: 'a²=9', labelX: 235, labelY: 240 },
          { k: 'rect', x: 280, y: 10, w: 120, h: 90, cls: 'is-done', label: 'c²=25', labelX: 340, labelY: 60 },
          { k: 'rect', x: 280, y: 100, w: 120, h: 90, cls: 'is-void' },
          { k: 'text', x: 320, y: 300, t: 'a=3, b=4, c=5', cls: '' }
        ], caption: '三个正方形的面积关系' }));
      o.push(S('数格子：<b>9 + 16 = 25</b>，也就是 <b>a² + b² = c²</b>。',
        { cols: 1, rows: 3, cellW: 220, cells: [
          { v: 'a² = 3² = 9', cls: 'is-on' }, { v: 'b² = 4² = 16', cls: 'is-on' },
          { v: 'c² = 5² = 25', cls: 'is-hi' }], caption: '9 + 16 = 25' }));
      o.push(S('<b>逆定理</b>：若 a²+b²=c²，则这个三角形是直角三角形（可用于判定垂直）。',
        { view: 'steps', lines: [
          row('3² + 4² = 5²  → 直角三角形', 'is-on'),
          row('5² + 12² = 13²，6² + 8² = 10²', 'is-done')] }));
      o.push(S('搬到坐标系：横差 Δx、纵差 Δy 是直角边 → <b>d = √(Δx² + Δy²)</b>。',
        { view: 'steps', lines: [
          row('d² = (x₂−x₁)² + (y₂−y₁)²', 'is-hi'),
          row('单位圆上：cos²θ + sin²θ = 1', 'is-done')] }));
      return o;
    },
    notes: [
      '<p>勾股定理说的是<b>面积</b>：两个小正方形拼起来等于大正方形，不只是三个数字的巧合。</p>',
      '<p>逆定理给出「用长度判断直角」的方法，是解析几何判断垂直的代数依据。</p>',
      '<p>甲种本代数1 单位圆上 sin²θ+cos²θ=1 就是勾股定理；解析几何两点距离、立体几何空间对角线同理。</p>'
    ],
    example: { q: '直角三角形两直角边 5 和 12，斜边？', steps: ['c² = 25 + 144 = 169'], a: '13' },
    quiz: [
      { q: '直角边 6 和 8，斜边是？', options: ['10', '12', '14', '√28'], answer: 0, explain: '√(36+64) = √100 = 10。' },
      { q: '三边 5, 12, 13 的三角形是？', options: ['锐角', '直角', '钝角', '无法判断'], answer: 1, explain: '25+144=169=13²，由逆定理是直角三角形。' }
    ]
  });

  T({
    id: 'm-circle', unit: 'm-geo', title: '圆：圆周角与切线', subtitle: '圆心角是同弧圆周角的两倍',
    goal: '掌握垂径定理、圆周角定理、切线性质',
    why: '甲种本解析几何第二章「圆」把这里几何性质翻译成方程；单位圆与三角函数也以此为基础。',
    view: 'shapes', minutes: 10, prereq: ['m-pyth', 'm-lines-angle'],
    demo: function () {
      var cc = { x: 320, y: 155, r: 100 };
      var o = [];
      o.push(S('圆心 O、半径 r。垂直于弦的直径<b>平分这条弦</b>（垂径定理）。',
        { items: [
          { k: 'circle', x: cc.x, y: cc.y, r: cc.r, cls: 'is-on' },
          { k: 'line', x1: 320, y1: 55, x2: 320, y2: 255, cls: 'is-hi' },
          { k: 'line', x1: 245, y1: 130, x2: 395, y2: 130, cls: '' },
          { k: 'circle', x: 320, y: 155, r: 4, cls: 'is-hi' },
          { k: 'text', x: 320, y: 35, t: '直径 ⊥ 弦 ⇒ 平分弦', cls: '' }
        ], caption: '圆的轴对称性是所有垂径问题的源头' }));
      o.push(S('同弧所对的<b>圆周角 = 圆心角的一半</b>；直径所对圆周角是 90°。',
        { items: [
          { k: 'circle', x: cc.x, y: cc.y, r: cc.r, cls: 'is-on' },
          { k: 'line', x1: 220, y1: 155, x2: 420, y2: 155, cls: 'is-dim' },
          { k: 'line', x1: 220, y1: 155, x2: 320, y2: 55, cls: 'is-hi' },
          { k: 'line', x1: 420, y1: 155, x2: 320, y2: 55, cls: 'is-hi' },
          { k: 'text', x: 320, y: 45, t: '直径所对圆周角 = 90°', cls: '' }
        ], caption: '泰勒斯定理' }));
      o.push(S('切线垂直于过切点的半径：<b>OP ⊥ l</b>。',
        { items: [
          { k: 'circle', x: cc.x, y: cc.y, r: cc.r, cls: 'is-on' },
          { k: 'line', x1: 320, y1: 155, x2: 420, y2: 155, cls: 'is-hi' },
          { k: 'line', x1: 420, y1: 45, x2: 420, y2: 265, cls: 'is-hi' },
          { k: 'text', x: 320, y: 35, t: 'P 为切点，OP ⊥ 切线', cls: '' }
        ], caption: '解析几何里「相切 ⇔ Δ=0」的几何原型' }));
      o.push(S('圆的标准方程：圆心 (a,b)、半径 r → <b>(x−a)² + (y−b)² = r²</b>，来自距离公式。',
        { view: 'steps', lines: [
          row('点 P(x,y) 到圆心距离恒为 r', 'is-on'),
          row('√((x−a)²+(y−b)²) = r', 'is-hi'),
          row('两边平方 → 圆的标准方程', 'is-done')] }));
      return o;
    },
    notes: [
      '<p>圆的问题几乎都可以归结为「半径相等」和「等腰三角形」，作辅助线时常连半径。</p>',
      '<p>圆周角定理把角度与弧联系起来，是后面「圆心角 → 弧度制 → 任意角」的桥梁。</p>',
      '<p>甲种本平面解析几何第二章把圆写成二次方程；直线与圆相切的判定用 Δ=0 或「圆心到直线距离 = r」，后者正是切线性质。</p>'
    ],
    example: { q: '圆心 (2,−1)、半径 3，写出圆的方程', steps: ['代入 (x−a)²+(y−b)²=r²'], a: '(x−2)² + (y+1)² = 9' },
    quiz: [
      { q: '直径所对的圆周角是？', options: ['45°', '60°', '90°', '180°'], answer: 2, explain: '圆心角 180° 的一半是 90°。' },
      { q: '圆心 (0,0) 半径 4 的圆方程是？', options: ['x²+y²=4', 'x²+y²=16', '(x−4)²+y²=16', 'x+y=4'], answer: 1, explain: 'r² = 16。' }
    ]
  });

  T({
    id: 'm-trig', unit: 'm-geo', title: '锐角三角函数与解直角三角形', subtitle: '角定了，边的比值就定了',
    goal: '理解 sin/cos/tan 定义，会解直角三角形，记住特殊角值',
    why: '★★ 甲种本代数1 第二章「任意角的三角函数」就是把这里 0°~90° 的定义推广到任意角；解析几何的斜率 k=tanα 也在此。',
    view: 'shapes', minutes: 13, star: true, prereq: ['m-similar', 'm-pyth'],
    demo: function () {
      var o = [];
      o.push(S('直角三角形中，锐角 A 定了，<b>三边之比就定了</b>（相似三角形）。',
        { items: [
          { k: 'poly', pts: [[180, 230], [460, 230], [180, 90]], cls: 'is-on' },
          { k: 'text', x: 205, y: 215, t: 'A', cls: '' },
          { k: 'text', x: 320, y: 248, t: '邻边 b', cls: '' },
          { k: 'text', x: 165, y: 165, t: '对边 a', cls: '' },
          { k: 'text', x: 330, y: 150, t: '斜边 c', cls: '' },
          { k: 'text', x: 320, y: 40, t: '含 30° 的直角三角形，边长比恒为 1 : √3 : 2', cls: '' }
        ], caption: '比值只与角有关，与三角形大小无关' }));
      o.push(S('三个定义：<b>sin A = 对/斜，cos A = 邻/斜，tan A = 对/邻</b>。',
        { view: 'grid', cols: 1, rows: 3, cellW: 260, cells: [
          { v: 'sin A = a / c', cls: 'is-on' }, { v: 'cos A = b / c', cls: 'is-on' },
          { v: 'tan A = a / b', cls: 'is-hi' }] }));
      o.push(S('特殊角要记牢（由 30°-60°-90° 与等腰直角三角形推出）。',
        { view: 'grid', cols: 4, rows: 3, cellW: 78, cells: [
          { v: '角', cls: 'is-done' }, { v: '30°', cls: 'is-done' }, { v: '45°', cls: 'is-done' }, { v: '60°', cls: 'is-done' },
          { v: 'sin', cls: 'is-on' }, { v: '1/2', cls: '' }, { v: '√2/2', cls: '' }, { v: '√3/2', cls: '' },
          { v: 'cos', cls: 'is-on' }, { v: '√3/2', cls: '' }, { v: '√2/2', cls: '' }, { v: '1/2', cls: '' }] }));
      o.push(S('由勾股定理立刻得到 <b>sin²A + cos²A = 1</b>，以及 <b>tan A = sin A / cos A</b>。',
        { view: 'steps', lines: [
          row('(a/c)² + (b/c)² = (a²+b²)/c² = 1', 'is-hi'),
          row('tan A = (a/c) ÷ (b/c) = a/b', 'is-done')] }));
      o.push(S('甲种本把角放大到任意角：在<b>单位圆</b>上，点的坐标就是 <b>(cos θ, sin θ)</b>。',
        { view: 'shapes', items: [
          { k: 'circle', x: 300, y: 160, r: 100, cls: 'is-on' },
          { k: 'line', x1: 300, y1: 160, x2: 380, y2: 100, cls: 'is-hi' },
          { k: 'line', x1: 380, y1: 100, x2: 380, y2: 160, cls: 'is-dim' },
          { k: 'circle', x: 380, y: 100, r: 5, cls: 'is-hi' },
          { k: 'text', x: 300, y: 35, t: 'P(cos θ, sin θ)', cls: '' },
          { k: 'text', x: 445, y: 135, t: 'sin θ', cls: '' },
          { k: 'text', x: 340, y: 180, t: 'cos θ', cls: '' }
        ], caption: '这是「任意角的三角函数」的核心图' }));
      return o;
    },
    notes: [
      '<p>三角函数不是新运算，而是给「直角三角形的边长比」起名字；因为相似，比值只由角决定。</p>',
      '<p>解直角三角形：已知两边求角用比值，已知一角一边求边用乘除。</p>',
      '<p>甲种本代数1 第二章用单位圆把定义域从 0°~90° 扩到任意角，再画正弦曲线；解析几何里 tan α 就是直线斜率，参数方程也常用 cos/sin。</p>'
    ],
    example: { q: '直角三角形中 ∠A=30°，斜边 10，求对边', steps: ['sin 30° = 对边/斜边 = 1/2', '对边 = 10 × 1/2'], a: '5' },
    quiz: [
      { q: 'sin 30° 的值是？', options: ['1/2', '√2/2', '√3/2', '1'], answer: 0, explain: '30° 所对直角边是斜边的一半。' },
      { q: 'tan 45° 等于？', options: ['0', '1/2', '1', '√3'], answer: 2, explain: '等腰直角三角形两直角边相等，比值为 1。' }
    ]
  });

  /* ============ 五、统计与概率 ============ */
  T({
    id: 'm-stat', unit: 'm-stat', title: '统计图表与方差', subtitle: '不只看平均，还要看分散程度',
    goal: '会算平均数、中位数、方差，理解数据波动',
    why: '甲种本代数3 第三章「概率」以及微积分中的误差估计都以「数据分布」为基础。',
    view: 'bars', minutes: 9, prereq: ['p-decimal'],
    demo: function () {
      var o = [];
      o.push(S('两组同学的成绩：<b>A = 70, 80, 90</b>；<b>B = 79, 80, 81</b>。',
        { values: [70, 80, 90], labels: ['A1', 'A2', 'A3'], marks: { hi: [0, 2] }, caption: '两组平均数都是 80' }));
      o.push(S('平均数一样，但 A 波动大得多。用<b>方差</b>衡量：各数与均值之差的平方的平均。',
        { values: [79, 80, 81], labels: ['B1', 'B2', 'B3'], marks: { done: [0, 1, 2] }, caption: 'B 组紧紧靠在 80 附近' }));
      o.push(S('计算 A 的方差：<b>((−10)² + 0² + 10²)/3 = 200/3 ≈ 66.7</b>。',
        { view: 'steps', lines: [
          row('s² = Σ(xᵢ − x̄)² / n', 'is-hi'),
          row('A: (100 + 0 + 100)/3 ≈ 66.7', 'is-on'),
          row('B: (1 + 0 + 1)/3 ≈ 0.67', 'is-done')] }));
      o.push(S('方差越小越稳定。标准差是方差的算术平方根，单位与原数据一致。',
        { view: 'grid', cols: 1, rows: 2, cellW: 290, cells: [
          { v: '方差 s²：平方平均', cls: 'is-on' },
          { v: '标准差 s = √s²：与原单位一致', cls: 'is-hi' }] }));
      return o;
    },
    notes: [
      '<p>平均数描述「集中位置」，方差描述「分散程度」，两者合起来才看得清一组数据。</p>',
      '<p>为什么要平方？避免正负偏差互相抵消；也可以用绝对值，但平方便于代数处理。</p>',
      '<p>甲种本代数3 的概率、微积分初步的误差估计，都把「离均值多远」当作核心量。</p>'
    ],
    example: { q: '数据 2, 4, 6 的方差？', steps: ['均值 = 4', '偏差平方：4, 0, 4'], a: '8/3 ≈ 2.67' },
    quiz: [
      { q: '数据 5, 5, 5 的方差是？', options: ['0', '5', '25', '1'], answer: 0, explain: '完全没有波动，方差为 0。' },
      { q: '数据 1, 2, 3, 4, 100 中，哪个量最不受极端值影响？', options: ['平均数', '中位数', '方差', '总和'], answer: 1, explain: '中位数只看位置，对极端值稳健。' }
    ]
  });

  T({
    id: 'm-prob', unit: 'm-stat', title: '概率初步与树状图', subtitle: '把所有可能结果数清楚',
    goal: '会列举样本空间，用树状图算多步事件概率',
    why: '★ 甲种本代数3 第三章「概率」、第二章「排列组合」都从这里升级到计数公式。',
    view: 'tree', minutes: 10, star: true, prereq: ['p-frac-ops', 'p-decimal'],
    demo: function () {
      var o = [];
      o.push(S('抛一枚均匀硬币：可能结果 {正, 反}，<b>P(正) = 1/2</b>。',
        { nodes: [{ id: 'r', label: '开始', x: 320, y: 50, cls: 'is-hi' },
                  { id: 'h', label: '正 1/2', x: 220, y: 160, cls: 'is-on' },
                  { id: 't', label: '反 1/2', x: 420, y: 160, cls: 'is-on' }],
          edges: [{ from: 'r', to: 'h' }, { from: 'r', to: 't' }], caption: '所有等可能结果共 2 个' }));
      o.push(S('抛两次：用<b>树状图</b>列出 4 种等可能结果。',
        { H: 280, nodes: [
          { id: 'r', label: '开始', x: 320, y: 35, cls: '' },
          { id: 'a', label: '正', x: 180, y: 105, cls: '' }, { id: 'b', label: '反', x: 460, y: 105, cls: '' },
          { id: 'c', label: '正正', x: 100, y: 200, cls: 'is-on' }, { id: 'd', label: '正反', x: 250, y: 200, cls: 'is-on' },
          { id: 'e', label: '反正', x: 400, y: 200, cls: 'is-on' }, { id: 'f', label: '反反', x: 550, y: 200, cls: 'is-on' }],
          edges: [{ from: 'r', to: 'a' }, { from: 'r', to: 'b' }, { from: 'a', to: 'c' }, { from: 'a', to: 'd' },
                  { from: 'b', to: 'e' }, { from: 'b', to: 'f' }], caption: '2 × 2 = 4 种结果' }));
      o.push(S('「恰好一次正面」包含正反、反正两种 → <b>P = 2/4 = 1/2</b>。',
        { view: 'steps', lines: [
          row('P = 有利结果数 / 所有等可能结果数', 'is-hi'),
          row('= 2 / 4 = 1/2', 'is-done')] }));
      o.push(S('多步实验用<b>乘法原理</b>：每步 2 种，两步 2×2 = 4 种；n 步就是 2ⁿ。',
        { view: 'grid', cols: 1, rows: 3, cellW: 290, cells: [
          { v: '分类用加法，分步用乘法', cls: 'is-on' },
          { v: '2 步抛硬币：2² = 4', cls: 'is-hi' },
          { v: '甲种本：排列 A(n,m)、组合 C(n,m)', cls: 'is-done' }] }));
      return o;
    },
    notes: [
      '<p>算概率的第一步永远是「把等可能的结果不重不漏地列出来」，树状图是最可靠的工具。</p>',
      '<p>分步完成用乘法原理，分类完成用加法原理 —— 这是全部计数公式的来源。</p>',
      '<p>甲种本代数3 第二章排列组合与二项式定理、第三章概率，就是把这套手工列举升级为公式与分布。</p>'
    ],
    example: { q: '掷一枚骰子，出现偶数的概率？', steps: ['等可能结果 6 个', '偶数有 2、4、6 共 3 个'], a: '3/6 = 1/2' },
    quiz: [
      { q: '抛两枚硬币，两枚都是正面的概率是？', options: ['1/2', '1/3', '1/4', '1/8'], answer: 2, explain: '4 种等可能结果中只有 1 种符合。' },
      { q: '掷骰子出现点数大于 4 的概率是？', options: ['1/6', '1/3', '1/2', '2/3'], answer: 1, explain: '5 和 6 两种，2/6 = 1/3。' }
    ]
  });

})();
