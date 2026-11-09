/* MathPath — 甲种本《代数》第一、二、三册（按真实章节分单元） */
(function () {
  'use strict';
  var MP = window.MathPath, U = MP.util, S = U.step;
  function C(t, cls) { return { t: t, cls: cls || '' }; }
  function row(s, cls) { return { cells: String(s).split('').map(function (c) { return C(c, cls || ''); }) }; }
  function st(arr, cap) {
    return { view: 'steps', lines: arr.map(function (a) { return typeof a === 'string' ? row(a) : a; }), caption: cap || '' };
  }
  function ax(r, x) { var o = { view: 'axis', range: r }; for (var k in x) o[k] = x[k]; return o; }
  function sh(items, cap) { return { view: 'shapes', items: items, caption: cap || '' }; }
  function gr(cols, rows, cells, cap, w) { return { view: 'grid', cols: cols, rows: rows, cells: cells, cellW: w || 60, caption: cap || '' }; }
  function nl(min, max, x) { var o = { view: 'numberline', min: min, max: max }; for (var k in x) o[k] = x[k]; return o; }
  function br(values, labels, marks, cap) { return { view: 'bars', values: values, labels: labels, marks: marks || {}, caption: cap || '' }; }
  function tr(nodes, edges, cap) { return { view: 'tree', nodes: nodes, edges: edges, caption: cap || '' }; }
  function curve(f, a, b, n) {
    var p = [], k = n || 50;
    for (var i = 0; i <= k; i++) { var x = a + (b - a) * i / k; p.push([x, U.round(f(x), 4)]); }
    return p;
  }
  function T(o) { o.view = 'steps'; MP.registerTopic(o); }

  MP.registerUnits([
    { id: 'a1-c1', track: 'bridge', book: 'alg1', name: '第一章 幂函数、指数函数和对数函数' },
    { id: 'a1-c2', track: 'bridge', book: 'alg1', name: '第二章 三角函数' },
    { id: 'a1-c3', track: 'bridge', book: 'alg1', name: '第三章 两角和与差的三角函数' },
    { id: 'a2-c1', track: 'bridge', book: 'alg2', name: '第一章 反三角函数和简单三角方程' },
    { id: 'a2-c2', track: 'bridge', book: 'alg2', name: '第二章 数列与数学归纳法' },
    { id: 'a2-c3', track: 'bridge', book: 'alg2', name: '第三章 不等式' },
    { id: 'a2-c4', track: 'bridge', book: 'alg2', name: '第四章 行列式和线性方程组' },
    { id: 'a2-c5', track: 'bridge', book: 'alg2', name: '第五章 复数' },
    { id: 'a3-c1', track: 'bridge', book: 'alg3', name: '*第一章 一元多项式和高次方程' },
    { id: 'a3-c2', track: 'bridge', book: 'alg3', name: '第二章 排列、组合、二项式定理' },
    { id: 'a3-c3', track: 'bridge', book: 'alg3', name: '第三章 概率' }
  ]);

  /* ================= 代数 第一册 ================= */
  T({
    id: 'a1-set', unit: 'a1-c1', title: '集合与集合运算', subtitle: '甲种本第一页：把「一堆对象」当作一个整体',
    goal: '会读 ∈、⊆、∩、∪、∅，能做交集并集补集运算',
    why: '《代数 第一册》第一章「一 集合」（p1～p5，练习第 1～14 题）。',
    minutes: 11, prereq: ['b-func-map'],
    demo: function () {
      var base = [
        { k: 'rect', x: 100, y: 55, w: 440, h: 190, rx: 14, cls: 'is-void' },
        { k: 'circle', x: 260, y: 150, r: 78, cls: 'is-on' },
        { k: 'circle', x: 380, y: 150, r: 78, cls: 'is-hi' },
        { k: 'text', x: 195, y: 150, t: 'A', cls: '' }, { k: 'text', x: 445, y: 150, t: 'B', cls: '' },
        { k: 'text', x: 320, y: 38, t: '全集 U', cls: '' }
      ];
      var o = [];
      o.push(S('课本从「一组确定的对象」讲起：全体叫<b>集合</b>，其中每个叫元素。<b>a ∈ A</b> 表示属于，<b>a ∉ A</b> 表示不属于。',
        sh(base, '韦恩图：矩形是全集 U，两个圆是集合 A、B')));
      o.push(S('集合的两种表示法（课本练习第 11～13 题）：<b>列举法</b>逐一列出元素，<b>描述法</b>写出元素满足的条件。',
        st(['列举法：{2, 4, 6, 8, 10}', '描述法：{x | x 是小于 11 的正偶数}', '描述法：{x | x² + 5x + 6 > 0}'], '竖线读作「满足」')));
      o.push(S('按元素个数分<b>有限集</b>与<b>无限集</b>（课本练习第 6～10 题要求逐题判断）。',
        gr(1, 2, [
          { v: '有限集：太阳系的行星', cls: 'is-on' },
          { v: '无限集：大于 0 的偶数', cls: 'is-hi' }], '', 190)));
      o.push(S('用 ∈ 或 ∉ 判断元素属于哪个数集（课本练习第 14 题）。',
        st(['1 ∈ N,  −3 ∉ N,  0.5 ∉ Z', '√2 ∉ Q,  √2 ∈ R', 'N ⊂ Z ⊂ Q ⊂ R'])));
      o.push(S('课本接着讲<b>子集</b>：A 的每个元素都属于 B，记作 A ⊆ B；A ⊆ B 且 A ≠ B 时叫真子集（课本例 1）。',
        st(['{a,b} 的全部子集：∅, {a}, {b}, {a,b}', '其中真子集：∅, {a}, {b}', '空集是任何集合的子集'], '列举时不要漏掉空集与自身')));
      o.push(S('交集 <b>A ∩ B</b>：既在 A 又在 B 的部分。',
        sh(base.concat([{ k: 'circle', x: 320, y: 150, r: 45, cls: 'is-done' },
                        { k: 'text', x: 320, y: 155, t: 'A ∩ B', cls: '' }]), '公共部分')));
      o.push(S('并集 <b>A ∪ B</b>：在 A 或 B 中的全部；补集 <b>∁A</b>：U 中不在 A 的部分。',
        st(['A = {1,2,3},  B = {3,4,5}', 'A ∩ B = {3}', 'A ∪ B = {1,2,3,4,5}', '若 U={1..6}，∁A = {4,5,6}'])));
      o.push(S('常用数集：N 自然数、Z 整数、Q 有理数、R 实数，且 <b>N ⊂ Z ⊂ Q ⊂ R</b>。',
        gr(1, 4, [
          { v: 'N 自然数', cls: 'is-on' }, { v: 'Z 整数', cls: 'is-on' },
          { v: 'Q 有理数', cls: 'is-on' }, { v: 'R 实数', cls: 'is-hi' }], '逐层包含', 200)));
      return o;
    },
    notes: [
      '<p>课本这一节的次序是：集合与元素、∈ 与 ∉ → 列举法/描述法 → 有限集/无限集 → 子集与真子集 → 交、并、补运算。描述法 {x | p(x)} 的竖线读作「满足」。</p>',
      '<p>∩ 取公共、∪ 取合并、∁ 取剩余；用韦恩图比死记定义可靠。集合不计顺序、不重复计数。</p>',
      '<p>下一节「映射与函数」要求定义域、值域都是集合；不等式解集、解析几何轨迹，也都用集合语言书写。</p>'
    ],
    example: { q: '用另一种方法表示 {2, 4, 6, 8, 10}（课本练习第 11 题）', steps: ['观察：都是正偶数，且小于 11', '改写成描述法'], a: '{x | x 是小于 11 的正偶数}' },
    quiz: [
      { q: 'A={1,2,3}，B={3,4}，A∩B 是？', options: ['{1,2,3,4}', '{3}', '{1,2}', '∅'], answer: 1, explain: '交集取公共元素 3。' },
      { q: '符号 ∈ 表示？', options: ['集合包含', '元素属于集合', '空集', '并集'], answer: 1, explain: 'a ∈ A 表示 a 是 A 的元素；不属于写 ∉。' },
      { q: '课本练习第 10 题「大于 0 的偶数」是？', options: ['有限集', '无限集', '空集', '不是集合'], answer: 1, explain: '偶数有无穷多个，是无限集。' }
    ]
  });

  T({
    id: 'a1-map', unit: 'a1-c1', title: '映射与函数三要素', subtitle: '每个 x 只能对应唯一一个 y',
    goal: '理解映射、一一映射、函数的定义域/值域/对应法则',
    why: '《代数 第一册》第一章「二 映射与函数」（p18），是幂函数、指数函数、反函数的共同语言。',
    minutes: 12, prereq: ['a1-set'],
    demo: function () {
      var o = [];
      o.push(S('映射 f: A→B：A 中<b>每一个</b>元素，按规则在 B 中有<b>唯一</b>的像。',
        sh([
          { k: 'rect', x: 90, y: 55, w: 130, h: 190, rx: 12, cls: 'is-on' },
          { k: 'rect', x: 420, y: 55, w: 130, h: 190, rx: 12, cls: 'is-on' },
          { k: 'text', x: 155, y: 42, t: 'A', cls: '' }, { k: 'text', x: 485, y: 42, t: 'B', cls: '' },
          { k: 'text', x: 155, y: 95, t: '1', cls: '' }, { k: 'text', x: 155, y: 150, t: '2', cls: '' }, { k: 'text', x: 155, y: 205, t: '3', cls: '' },
          { k: 'text', x: 485, y: 95, t: '2', cls: '' }, { k: 'text', x: 485, y: 150, t: '4', cls: '' }, { k: 'text', x: 485, y: 205, t: '6', cls: '' },
          { k: 'line', x1: 180, y1: 92, x2: 460, y2: 92, cls: 'is-hi' },
          { k: 'line', x1: 180, y1: 147, x2: 460, y2: 147, cls: 'is-hi' },
          { k: 'line', x1: 180, y1: 202, x2: 460, y2: 202, cls: 'is-hi' },
          { k: 'text', x: 320, y: 275, t: 'f(x) = 2x', cls: '' }
        ], '允许多对一，不允许一对多')));
      o.push(S('函数三要素：<b>定义域 A、值域、对应法则 f</b>。三者相同才是同一个函数。',
        st(['y = x²  (x ∈ R)', 'y = x²  (x ≥ 0)', '法则相同但定义域不同 ⇒ 不同函数'])));
      o.push(S('若 B 中每个元素也恰好被对应一次，叫<b>一一映射</b>，此时存在逆映射。',
        st(['一一映射 ⇒ 反函数存在', 'y = 2x + 1  ⇔  x = (y−1)/2', '这是下一册「反三角函数」的合法性来源'])));
      o.push(S('区间记号：开区间 (a,b)、闭区间 [a,b]、无穷区间 (a,+∞)。',
        nl(-2, 6, { ticks: [-2, 0, 2, 4, 6], segments: [{ a: 0, b: 4, label: '[0,4]', cls: 'is-hi' }], caption: '闭区间两端都取到' })));
      return o;
    },
    notes: [
      '<p>映射只要求「每个 x 有唯一 y」，不要求不同的 x 得到不同的 y；允许多个 x 映到同一个 y。</p>',
      '<p>判断两个函数是否相同，先看定义域，再看对应法则，值域由前两者决定。</p>',
      '<p>一一映射可逆：第一章末尾的对数函数、第二章的反三角函数、第五章的复数运算都靠这个概念建立。</p>'
    ],
    example: { q: 'f(x)=3x−2 的反函数？', steps: ['从 y=3x−2 解出 x=(y+2)/3', '交换 x 与 y'], a: 'f⁻¹(x) = (x+2)/3' },
    quiz: [
      { q: '函数 f(x)=1/(x−1) 的定义域是？', options: ['R', 'x ≠ 1', 'x > 1', 'x ≠ 0'], answer: 1, explain: '分母不能为 0，所以 x≠1。' },
      { q: '哪个条件保证反函数存在？', options: ['定义域是 R', '函数连续', '是一一映射', '值域是 R'], answer: 2, explain: '只有一一映射才能唯一地反解。' }
    ]
  });

  T({
    id: 'a1-power-fn', unit: 'a1-c1', title: '幂函数 y = xᵅ', subtitle: '同一个形式，α 不同图象完全不同',
    goal: '会按 α 讨论定义域、奇偶性、单调性与图象',
    why: '《代数 第一册》第一章「三 幂函数」（p29），是甲种本第一次系统研究函数族。',
    minutes: 12, prereq: ['a1-map', 'm-power'],
    demo: function () {
      var o = [];
      o.push(S('把指数法则里的 aⁿ 中的 n 换成任意实数 α，固定底为自变量，得 <b>y = xᵅ</b>。',
        st(['α = 2  →  y = x²', 'α = 3  →  y = x³', 'α = 1/2 → y = √x', 'α = −1 → y = 1/x'])));
      o.push(S('α &gt; 0 时都过 (1,1)；α &lt; 0 时在 x=0 无定义，且有渐近线。',
        ax({ x: [-3, 3], y: [-2, 6] }, { curves: [
          { pts: curve(function (x) { return x * x; }, -2.4, 2.4, 40), cls: '', label: 'α=2' },
          { pts: curve(function (x) { return x * x * x; }, -1.8, 1.8, 40), cls: 'is-hi', label: 'α=3' }
        ], points: [{ x: 1, y: 1, label: '(1,1)', cls: 'is-on' }], caption: 'α>0 的幂函数' })));
      o.push(S('α = 1/2 时定义域只有 x ≥ 0，图象是抛物线的上半支。',
        ax({ x: [-1, 5], y: [-1, 3] }, { curves: [
          { pts: curve(function (x) { return Math.sqrt(x); }, 0, 4.5, 40), cls: 'is-hi', label: 'y=√x' },
          { pts: curve(function (x) { return x * x; }, 0, 1.7, 25), cls: 'is-dim', label: 'y=x²' }
        ], caption: '互为反函数（关于 y=x 对称）' })));
      o.push(S('α = −1 即初中的反比例函数：定义域 x≠0，两支双曲线。',
        ax({ x: [-5, 5], y: [-5, 5] }, { curves: [
          { pts: curve(function (x) { return 2 / x; }, 0.5, 5, 35), cls: '', label: 'y=2/x' },
          { pts: curve(function (x) { return 2 / x; }, -5, -0.5, 35), cls: '' }
        ] })));
      o.push(S('奇偶性看 α 的分子分母：x²、x⁴ 是偶函数（关于 y 轴对称），x³、x 是奇函数（关于原点对称）。',
        gr(2, 2, [
          { v: 'α=2 偶函数', cls: 'is-on' }, { v: 'α=3 奇函数', cls: 'is-on' },
          { v: 'α=−1 奇函数', cls: 'is-on' }, { v: 'α=1/2 非奇非偶', cls: 'is-hi' }], '', 140)));
      return o;
    },
    notes: [
      '<p>研究幂函数的固定套路：先定定义域，再看奇偶性，最后看第一象限内的单调性。</p>',
      '<p>所有 α&gt;0 的幂函数都过 (0,0) 与 (1,1)；α&lt;0 的都过 (1,1)，但 x=0 是禁区。</p>',
      '<p>甲种本接着用同样的方法研究指数函数与对数函数；微积分里 xᵅ 的求导公式也按 α 分类讨论。</p>'
    ],
    example: { q: 'y = x⁻² 的定义域与奇偶性？', steps: ['x⁻² = 1/x²，x ≠ 0', 'f(−x) = 1/(−x)² = f(x)'], a: '定义域 x≠0，偶函数' },
    quiz: [
      { q: 'y = x^(1/2) 的定义域是？', options: ['R', 'x ≥ 0', 'x ≠ 0', 'x > 1'], answer: 1, explain: '平方根要求被开方数非负。' },
      { q: '下列哪个是奇函数？', options: ['y=x²', 'y=x³', 'y=x²+1', 'y=|x|'], answer: 1, explain: 'f(−x)=−f(x)，x³ 关于原点对称。' }
    ]
  });

  T({
    id: 'a1-exp-fn', unit: 'a1-c1', title: '指数函数 y = aˣ', subtitle: '底数 a 决定增减，全图恒在 x 轴上方',
    goal: '掌握 a>1 与 0<a<1 的图象、性质与指数方程',
    why: '《代数 第一册》第一章「四 指数函数和对数函数」（p58）。',
    minutes: 11, prereq: ['a1-power-fn', 'b-exp-log'],
    demo: function () {
      var o = [];
      o.push(S('定义 <b>y = aˣ</b>（a &gt; 0 且 a ≠ 1）。因 a⁰=1，所有指数函数都过 <b>(0,1)</b>。',
        ax({ x: [-3, 3], y: [-1, 6] }, { curves: [
          { pts: curve(function (x) { return Math.pow(2, x); }, -3, 2.5, 45), cls: '', label: 'y=2ˣ' }
        ], points: [{ x: 0, y: 1, label: '(0,1)', cls: 'is-hi' }] })));
      o.push(S('a &gt; 1 单调递增；0 &lt; a &lt; 1 单调递减，两者关于 y 轴对称。',
        ax({ x: [-3, 3], y: [-1, 6] }, { curves: [
          { pts: curve(function (x) { return Math.pow(2, x); }, -3, 2.5, 40), cls: '', label: 'a=2' },
          { pts: curve(function (x) { return Math.pow(0.5, x); }, -2.5, 3, 40), cls: 'is-hi', label: 'a=1/2' }
        ] })));
      o.push(S('值域恒为 (0,+∞)；x 轴是水平渐近线，图象永远不与它相交。',
        st(['y > 0 恒成立', 'aˣ · aʸ = aˣ⁺ʸ', '(aˣ)ʸ = aˣʸ', '单调性由 a 与 1 的大小决定'])));
      o.push(S('解指数方程：把两边化成同底。<b>2ˣ = 8 = 2³ ⇒ x = 3</b>。',
        st(['4ˣ = 32  →  2²ˣ = 2⁵', '2x = 5  →  x = 5/2'])));
      return o;
    },
    notes: [
      '<p>指数函数把「幂」的指数变成变量，增长/衰减速度远超幂函数 —— 这是它与幂函数最本质的区别。</p>',
      '<p>比较大小时先统一底数，再用单调性；注意 0&lt;a&lt;1 时不等号方向会反转。</p>',
      '<p>下一节取它的反函数得到对数函数；甲种本第二册的复利、第三册的概率分布里也会反复出现。</p>'
    ],
    example: { q: '解 3^(2x−1) = 27', steps: ['27 = 3³', '2x − 1 = 3'], a: 'x = 2' },
    quiz: [
      { q: 'y = (1/3)ˣ 的单调性是？', options: ['递增', '递减', '先增后减', '常数'], answer: 1, explain: '0<a<1 时指数函数单调递减。' },
      { q: '所有 y=aˣ 都经过哪个点？', options: ['(0,0)', '(0,1)', '(1,0)', '(1,1)'], answer: 1, explain: 'a⁰ = 1。' }
    ]
  });

  T({
    id: 'a1-log-fn', unit: 'a1-c1', title: '对数函数与换底公式', subtitle: '指数函数的反函数，把乘法变加法',
    goal: '掌握 log 运算律、图象与换底公式，会解对数方程',
    why: '《代数 第一册》第一章「四」及附录 II「换底公式」（p226，原计划安排在初中）。',
    minutes: 13, prereq: ['a1-exp-fn', 'm-frac-expr'],
    demo: function () {
      var o = [];
      o.push(S('由 aᵇ = N ⇔ <b>logₐN = b</b>（a&gt;0, a≠1, N&gt;0）。对数就是「求指数」。',
        st(['2³ = 8   ⇔   log₂8 = 3', '10² = 100 ⇔  lg 100 = 2', '定义域 N > 0，值域 R'])));
      o.push(S('y = log₂x 的图象与 y = 2ˣ 关于 <b>y = x</b> 对称，过 (1,0)。',
        ax({ x: [-2, 5], y: [-3, 5] }, { curves: [
          { pts: curve(function (x) { return Math.pow(2, x); }, -2, 2.3, 35), cls: 'is-dim', label: 'y=2ˣ' },
          { pts: curve(function (x) { return Math.log(x) / Math.LN2; }, 0.15, 5, 45), cls: 'is-hi', label: 'y=log₂x' },
          { pts: [[-2, -2], [5, 5]], cls: 'is-dim', label: 'y=x' }
        ], points: [{ x: 1, y: 0, label: '(1,0)', cls: 'is-on' }] })));
      o.push(S('运算律来自指数律：<b>log(MN)=logM+logN</b>、log(M/N)=logM−logN、log Mⁿ = n log M。',
        st(['log₂(8×4) = 3 + 2 = 5', 'log₂(8/4) = 3 − 2 = 1', 'log₂ 8³ = 3 × 3 = 9'])));
      o.push(S('<b>换底公式</b>：logₐb = log꜀b / log꜀a（c&gt;0, c≠1）。推导只用到分式与指数律。',
        st(['设 x = logₐb，则 aˣ = b', '两边取以 c 为底的对数：x·log꜀a = log꜀b', 'x = log꜀b / log꜀a   （附录 II）'])));
      o.push(S('它让任意底都能换成常用对数或自然对数，也是附录 I「近似计算的法则」的工具。',
        st(['log₂5 = lg5 / lg2 ≈ 0.6990/0.3010 ≈ 2.32', '真数必须 > 0：解方程后要验根'])));
      return o;
    },
    notes: [
      '<p>对数把乘法降为加法、乘方降为乘法，这是它被发明出来的理由，也是解指数方程的关键。</p>',
      '<p>换底公式的形式和分式通分很像：分子分母同取一种「公共的底」，本质仍是分式基本性质。</p>',
      '<p>甲种本附录 I 讲近似计算与有效数字、附录 II 讲换底；微积分里 ln x 的导数与积分还会再用到它。</p>'
    ],
    example: { q: '计算 log₃9 + log₃(1/3)', steps: ['log₃9 = 2', 'log₃(1/3) = −1'], a: '1' },
    quiz: [
      { q: 'log₂16 = ?', options: ['2', '4', '8', '16'], answer: 1, explain: '2⁴ = 16。' },
      { q: '换底公式 logₐb 等于？', options: ['log_b a', 'log꜀b / log꜀a', 'log꜀a / log꜀b', 'a / b'], answer: 1, explain: '分子是新真数，分母是原底数。' }
    ]
  });

  T({
    id: 'a1-trig-any', unit: 'a1-c2', title: '任意角、弧度制与单位圆', subtitle: '角不再限于 0°~90°，sin/cos 变成坐标',
    goal: '掌握弧度制、终边、象限符号、同角三角函数关系',
    why: '《代数 第一册》第二章「一 任意角的三角函数」（p83）。',
    minutes: 13, star: true, prereq: ['b-angle-rad', 'm-trig'],
    demo: function () {
      var o = [];
      o.push(S('角看作<b>射线绕端点旋转的量</b>：逆时针为正，顺时针为负，可以超过 360°。',
        sh([
          { k: 'line', x1: 60, y1: 170, x2: 580, y2: 170, cls: 'is-dim' },
          { k: 'line', x1: 300, y1: 290, x2: 300, y2: 40, cls: 'is-dim' },
          { k: 'circle', x: 300, y: 170, r: 100, cls: 'is-on' },
          { k: 'line', x1: 300, y1: 170, x2: 380, y2: 100, cls: 'is-hi' },
          { k: 'text', x: 300, y: 30, t: '始边在 x 轴正半轴，终边任意', cls: '' }
        ], '终边相同的角相差 360° 的整数倍')));
      o.push(S('弧度制：用<b>弧长 ÷ 半径</b>量角，整圈 2πr/r = <b>2π</b>。',
        st(['180° = π，90° = π/2，360° = 2π', '弧长 l = |α| r', '扇形面积 S = ½ l r = ½ α r²'])));
      o.push(S('单位圆（r=1）上终边交点 <b>P(x,y)</b>：定义 <b>cos α = x，sin α = y</b>。',
        sh([
          { k: 'line', x1: 60, y1: 170, x2: 580, y2: 170, cls: 'is-dim' },
          { k: 'line', x1: 300, y1: 290, x2: 300, y2: 40, cls: 'is-dim' },
          { k: 'circle', x: 300, y: 170, r: 100, cls: 'is-on' },
          { k: 'line', x1: 300, y1: 170, x2: 370, y2: 88, cls: 'is-hi' },
          { k: 'line', x1: 370, y1: 88, x2: 370, y2: 170, cls: 'is-hi' },
          { k: 'circle', x: 370, y: 88, r: 5, cls: 'is-hi' },
          { k: 'text', x: 440, y: 125, t: 'sin α = y', cls: '' },
          { k: 'text', x: 335, y: 190, t: 'cos α', cls: '' }
        ], '斜边 = 1，比值即坐标')));
      o.push(S('由勾股定理得 <b>sin²α + cos²α = 1</b>，以及 <b>tan α = sin α / cos α</b>。',
        st(['x² + y² = 1  ⇒  sin²α + cos²α = 1', 'tan α = y / x', 'cos α = 0 时 tan α 无定义'], '甲种本写作 tg α、ctg α，即 tan、cot')));
      o.push(S('符号看象限：一全正、二正弦正、三正切正、四余弦正。',
        gr(2, 2, [
          { v: 'Ⅱ sin +', cls: 'is-on' }, { v: 'Ⅰ 全 +', cls: 'is-done' },
          { v: 'Ⅲ tan +', cls: 'is-on' }, { v: 'Ⅳ cos +', cls: 'is-hi' }], '按象限记忆', 105)));
      o.push(S('课本 2.7 节「用单位圆中的线段表示三角函数值」：过 P 作 x 轴垂线得<b>正弦线 MP</b>，横坐标 OM 是余弦线，过 A(1,0) 作切线得<b>正切线 AT</b>。',
        st(['有向线段 MP = sin α（正弦线）', '有向线段 OM = cos α（余弦线）', '有向线段 AT = tg α（正切线）', '三角函数值于是可以直接在圆上量出来'], '这是画正弦曲线的几何依据')));
      return o;
    },
    notes: [
      '<p>把角从「三角形的一个内角」改成「旋转量」，定义域一下子扩展到全体实数，这是本章最关键的一步。</p>',
      '<p>单位圆把三角函数变成坐标，于是符号、周期性、单调区间都能从圆上直接读出来。</p>',
      '<p>下一节用这个定义画 y=sin x 的图象；第三章用单位圆上两点距离推导 cos(α−β)，全部公式由此展开。</p>'
    ],
    example: { q: '求 sin(5π/6) 与 cos(5π/6)', steps: ['5π/6 = 150°，终边在第二象限', '参考角 π/6，sin 为正、cos 为负'], a: 'sin = 1/2，cos = −√3/2' },
    quiz: [
      { q: '240° 等于多少弧度？', options: ['4π/3', '5π/4', '3π/2', '7π/6'], answer: 0, explain: '240° × π/180 = 4π/3。' },
      { q: 'sin²α + cos²α = ?', options: ['0', '1', 'tan α', '2'], answer: 1, explain: '单位圆上 x²+y²=1。' }
    ]
  });

  T({
    id: 'a1-trig-graph', unit: 'a1-c2', title: '三角函数的图象和性质', subtitle: '把单位圆的转动摊开成波浪',
    goal: '掌握正弦/余弦曲线的周期、振幅、奇偶性与 y=Asin(ωx+φ)',
    why: '《代数 第一册》第二章「二 三角函数的图象和性质」（p130）。',
    minutes: 13, star: true, prereq: ['a1-trig-any'],
    demo: function () {
      var o = [];
      o.push(S('让角 α 从 0 匀速增大，把每一点的 sin α 值按横坐标 α 描出来，就是<b>正弦曲线</b>。',
        ax({ x: [-1, 7], y: [-1.5, 1.5] }, { curves: [
          { pts: curve(function (x) { return Math.sin(x); }, 0, 6.28, 80), cls: '', label: 'y=sin x' }
        ], points: [{ x: 1.57, y: 1, label: 'π/2 → 1', cls: 'is-hi' }], caption: '0 → 1 → 0 → −1 → 0' })));
      o.push(S('周期 <b>2π</b>：sin(x+2π)=sin x；奇函数，关于原点对称。余弦曲线是它左移 π/2。',
        ax({ x: [-1, 7], y: [-1.5, 1.5] }, { curves: [
          { pts: curve(function (x) { return Math.sin(x); }, 0, 6.28, 70), cls: '', label: 'sin' },
          { pts: curve(function (x) { return Math.cos(x); }, 0, 6.28, 70), cls: 'is-hi', label: 'cos' }
        ], points: [{ x: 0, y: 1, label: 'cos0=1', cls: 'is-on' }] })));
      o.push(S('y = A sin(ωx+φ)：<b>A</b> 管振幅、<b>ω</b> 管周期 T=2π/ω、<b>φ</b> 管左右平移。',
        ax({ x: [-1, 7], y: [-2.2, 2.2] }, { curves: [
          { pts: curve(function (x) { return Math.sin(x); }, 0, 6.28, 70), cls: 'is-dim', label: 'sin x' },
          { pts: curve(function (x) { return 2 * Math.sin(2 * x); }, 0, 6.28, 90), cls: 'is-hi', label: '2sin2x' }
        ], caption: '振幅 ×2，周期缩短为 π' })));
      o.push(S('单调区间：sin x 在 [−π/2+2kπ, π/2+2kπ] 上递增；tan x 周期 π，有竖直渐近线。',
        st(['sin 最大值 1，最小值 −1', 'tan x 在 x = π/2 + kπ 处无定义', '这些性质是下一册解三角方程与反三角函数的基础'])));
      return o;
    },
    notes: [
      '<p>正弦曲线就是「单位圆上点的纵坐标随时间变化」的记录；把圆摊开成时间轴，就得到波。</p>',
      '<p>三个参数各司其职：A 纵向拉伸、ω 横向压缩、φ 平移。判断顺序先 A 再 ω 最后 φ。</p>',
      '<p>甲种本第三章和差角公式、第二册反三角函数，都建立在这条曲线的周期性与单调区间上；解析几何的参数方程也用它。</p>'
    ],
    example: { q: 'y = 3sin(2x + π/3) 的振幅与周期？', steps: ['A = 3', 'T = 2π/ω = 2π/2'], a: '振幅 3，周期 π' },
    quiz: [
      { q: 'y = sin x 的最小正周期是？', options: ['π', '2π', 'π/2', '4π'], answer: 1, explain: 'sin(x+2π) = sin x，且没有更小的正周期。' },
      { q: 'y = 2sin(3x) 的振幅是？', options: ['1', '2', '3', '6'], answer: 1, explain: '振幅是 |A| = 2。' }
    ]
  });

  T({
    id: 'a1-trig-add', unit: 'a1-c3', title: '两角和与差的三角函数', subtitle: '从单位圆上两点的距离推出全部公式',
    goal: '掌握 cos(α±β)、sin(α±β)、tan(α±β) 及二倍角公式',
    why: '《代数 第一册》第三章「两角和与差的三角函数」（p173）：正文含 3.2「二倍角的正弦、余弦、正切」与 3.4「三角函数的积化和差与和差化积」两个独立小节。',
    minutes: 14, star: true, prereq: ['a1-trig-any'],
    demo: function () {
      var o = [];
      o.push(S('在单位圆上取 A(cos α, sin α)、B(cos β, sin β)，两点距离只与 <b>α−β</b> 有关。',
        sh([
          { k: 'line', x1: 60, y1: 160, x2: 580, y2: 160, cls: 'is-dim' },
          { k: 'line', x1: 300, y1: 280, x2: 300, y2: 30, cls: 'is-dim' },
          { k: 'circle', x: 300, y: 160, r: 100, cls: 'is-on' },
          { k: 'line', x1: 300, y1: 160, x2: 380, y2: 80, cls: 'is-hi' },
          { k: 'line', x1: 300, y1: 160, x2: 395, y2: 155, cls: 'is-hi' },
          { k: 'line', x1: 380, y1: 80, x2: 395, y2: 155, cls: 'is-done' },
          { k: 'text', x: 300, y: 25, t: '弦 AB 的长度由 α−β 决定', cls: '' }
        ], '旋转不改变距离')));
      o.push(S('用距离公式展开 |AB|²，与把 α−β 旋转到起点算出的式子比较，得<b>余弦差角公式</b>。',
        st(['|AB|² = (cosα−cosβ)² + (sinα−sinβ)²', '= 2 − 2(cosαcosβ + sinαsinβ)', '又 |AB|² = 2 − 2cos(α−β)', '∴ cos(α−β) = cosαcosβ + sinαsinβ'])));
      o.push(S('把 β 换成 −β，或配合诱导公式，得到一组公式。',
        st(['cos(α+β) = cosαcosβ − sinαsinβ', 'sin(α+β) = sinαcosβ + cosαsinβ', 'sin(α−β) = sinαcosβ − cosαsinβ', 'tan(α+β) = (tanα+tanβ)/(1−tanαtanβ)'])));
      o.push(S('令 β = α 得<b>二倍角</b>：sin2α = 2sinαcosα，cos2α = cos²α − sin²α。',
        st(['sin2α = 2 sinα cosα', 'cos2α = 2cos²α − 1 = 1 − 2sin²α', '半角公式由 cos2α 反解得到'])));
      o.push(S('应用：求 <b>sin 75°</b> = sin(45°+30°) = (√6+√2)/4。',
        st(['= sin45 cos30 + cos45 sin30', '= (√2/2)(√3/2) + (√2/2)(1/2)', '= (√6 + √2) / 4'])));
      o.push(S('课本把<b>二倍角公式</b>单列为 3.2 节：令 β=α 得 sin2α、cos2α、tg2α；由 cos2α 反解又得半角公式。',
        st(['sin2α = 2sinα cosα', 'cos2α = cos²α − sin²α = 2cos²α − 1', 'tg2α = 2tgα / (1 − tg²α)'])));
      o.push(S('课本 3.4 节还有<b>积化和差与和差化积</b>：把和差公式相加相减、再令 α+β=u、α−β=v 即可。',
        st(['sinα cosβ = ½[sin(α+β) + sin(α−β)]', 'cosα cosβ = ½[cos(α+β) + cos(α−β)]', 'sinα + sinβ = 2 sin((α+β)/2) cos((α−β)/2)', '这套公式在微积分求三角积分时很有用'])));
      return o;
    },
    notes: [
      '<p>所有和差角公式都源于「旋转不改变距离」：把弦长用两种方式算一遍，等式就出来了。</p>',
      '<p>不要死记八个公式，记住 cos(α−β) 与 sin(α+β) 两条，其余用 −β、β=α、商数关系推出来。</p>',
      '<p>甲种本第二册的简单三角方程、微积分里的三角函数求导与积分、解析几何的参数方程旋转，都要用这组公式化简。</p>'
    ],
    example: { q: '已知 sinα=3/5 且 α 为锐角，求 sin2α', steps: ['cosα = 4/5', 'sin2α = 2·(3/5)·(4/5)'], a: '24/25' },
    quiz: [
      { q: 'cos(α−β) = ?', options: ['cosαcosβ + sinαsinβ', 'cosαcosβ − sinαsinβ', 'sinαcosβ + cosαsinβ', 'sinαsinβ − cosαcosβ'], answer: 0, explain: '差角公式中间是加号。' },
      { q: 'sin 2α = ?', options: ['2sinα', 'sin²α', '2sinαcosα', 'cos²α−sin²α'], answer: 2, explain: '二倍角正弦公式。' }
    ]
  });

  /* ================= 代数 第二册 ================= */
  T({
    id: 'a2-arcsin', unit: 'a2-c1', title: '反三角函数', subtitle: '限制一段单调区间，才能给三角函数找反函数',
    goal: '按课本掌握 arc sin / arc cos / arc tg / arc ctg 四种反三角函数及主值区间',
    why: '《代数 第二册》第一章「一 反三角函数」（p1～p19）：课本用 tg、ctg 表示正切余切，写作 arc sin x、arc cos x、arc tg x、arc ctg x，并讨论 sin(arc sin x)=x 与 arc sin(sin x) 的区别。',
    minutes: 11, prereq: ['a1-map', 'a1-trig-graph'],
    demo: function () {
      var o = [];
      o.push(S('y = sin x 在整个 R 上不是一一映射（周期重复），所以<b>不能直接取反函数</b>。',
        ax({ x: [-4, 7], y: [-1.5, 1.5] }, { curves: [
          { pts: curve(function (x) { return Math.sin(x); }, -3, 6.5, 90), cls: '', label: 'y=sin x' }
        ], caption: '同一个 y 对应无穷多个 x' })));
      o.push(S('把定义域限制在 <b>[−π/2, π/2]</b>，这段上 sin 单调递增，于是一一对应。',
        ax({ x: [-2, 2], y: [-1.5, 1.5] }, { curves: [
          { pts: curve(function (x) { return Math.sin(x); }, -1.57, 1.57, 40), cls: 'is-hi', label: '主值区间' },
          { pts: curve(function (x) { return Math.sin(x); }, -2, -1.57, 10), cls: 'is-dim' },
          { pts: curve(function (x) { return Math.sin(x); }, 1.57, 2, 10), cls: 'is-dim' }
        ] })));
      o.push(S('课本把反函数写作 <b>arc sin x</b>（有的书上写 sin⁻¹x），现代教材多写作 arcsin x。定义域 [−1,1]，值域 [−π/2, π/2]。',
        st(['arc sin(1/2) = π/6', 'arc cos x：[−1,1] → [0, π]', 'arc tg x：R → (−π/2, π/2)', 'arc ctg x：R → (0, π)'], '课本共讲四种反三角函数，含反余切')));
      o.push(S('课本例 4 特别提醒：由定义有 <b>sin(arc sin x) = x</b>，但 <b>arc sin(sin x)</b> 不一定等于 x。',
        st(['例：sin(5π/6) = 1/2', 'arc sin(sin 5π/6) = arc sin(1/2) = π/6 ≠ 5π/6', '因为主值区间只取 [−π/2, π/2]'])));
      o.push(S('互为反函数的图象关于 <b>y = x</b> 对称。',
        ax({ x: [-1.6, 1.6], y: [-1.6, 1.6] }, { curves: [
          { pts: curve(function (x) { return Math.sin(x); }, -1.57, 1.57, 40), cls: 'is-hi', label: 'sin' },
          { pts: curve(function (x) { return Math.asin(x); }, -1, 1, 40), cls: '', label: 'arcsin' },
          { pts: [[-1.5, -1.5], [1.5, 1.5]], cls: 'is-dim', label: 'y=x' }
        ] })));
      return o;
    },
    notes: [
      '<p>反函数存在的前提是一一映射；周期函数必须先「截取一段单调区间」，这叫取主值。课本记号是 arc sin / arc cos / arc tg / arc ctg，其中 tg、ctg 是当年的正切、余切写法。</p>',
      '<p>输出是角（弧度）而不是三角函数值；写答案时务必带上主值区间，并注意 arc sin(sin x) 未必等于 x。</p>',
      '<p>下一节解简单三角方程，正是用 arc sin 写出一个特解，再用周期补齐通解。</p>'
    ],
    example: { q: '求 arcsin(−√2/2)', steps: ['主值区间 [−π/2, π/2]', 'sin(−π/4) = −√2/2'], a: '−π/4' },
    quiz: [
      { q: 'arcsin x 的值域是？', options: ['[0,π]', '[−π/2,π/2]', 'R', '[−1,1]'], answer: 1, explain: '反正弦主值区间是 [−π/2, π/2]。' },
      { q: 'arccos(1/2) = ?', options: ['π/6', 'π/3', 'π/2', '2π/3'], answer: 1, explain: 'cos(π/3)=1/2 且 π/3 ∈ [0,π]。' }
    ]
  });

  T({
    id: 'a2-trig-eq', unit: 'a2-c1', title: '简单三角方程', subtitle: '先求一个特解，再用周期写出通解',
    goal: '会解 sin x = a、cos x = a、tan x = a 及可化为这些形式的方程',
    why: '《代数 第二册》第一章「二 简单三角方程」（p20）。',
    minutes: 12, prereq: ['a2-arcsin', 'a1-trig-any'],
    demo: function () {
      var o = [];
      o.push(S('解 <b>sin x = 1/2</b>：在单位圆上，纵坐标为 1/2 的射线有两条。',
        sh([
          { k: 'line', x1: 60, y1: 160, x2: 580, y2: 160, cls: 'is-dim' },
          { k: 'line', x1: 300, y1: 280, x2: 300, y2: 30, cls: 'is-dim' },
          { k: 'circle', x: 300, y: 160, r: 100, cls: 'is-on' },
          { k: 'line', x1: 220, y1: 110, x2: 380, y2: 110, cls: 'is-hi' },
          { k: 'line', x1: 300, y1: 160, x2: 387, y2: 110, cls: 'is-hi' },
          { k: 'line', x1: 300, y1: 160, x2: 213, y2: 110, cls: 'is-hi' },
          { k: 'text', x: 300, y: 25, t: 'x = π/6 与 5π/6（在一个周期内）', cls: '' }
        ], '一个周期内通常有两个解')));
      o.push(S('主值给一个特解：x₀ = arcsin(1/2) = π/6；另一个是 π − x₀ = 5π/6。',
        st(['sin x = a  ⇒  x = arcsin a + 2kπ', '或 x = π − arcsin a + 2kπ  (k ∈ Z)'])));
      o.push(S('加上周期得<b>通解</b>：x = π/6 + 2kπ 或 x = 5π/6 + 2kπ。',
        st(['k 取遍所有整数', '写通解时不能漏掉 k ∈ Z', 'tan x = a 的周期是 π，只需一组'])));
      o.push(S('可化为同名的方程，如 <b>2sin²x − sin x − 1 = 0</b>，先当一元二次方程分解。',
        st(['(2sin x + 1)(sin x − 1) = 0', 'sin x = −1/2 或 sin x = 1', '分别写出通解，注意 |a| ≤ 1 才有解'])));
      return o;
    },
    notes: [
      '<p>解三角方程的固定流程：化简成同名一次式 → 用反三角函数求特解 → 用单位圆补齐一个周期内的其他解 → 加周期。</p>',
      '<p>常见失分点：漏 k∈Z、漏掉第二个解、忘记检查 |a|≤1、变形中两边同除可能丢根。</p>',
      '<p>甲种本解析几何里求交点角度、微积分里求极值点，都会出现这类方程。</p>'
    ],
    example: { q: '解 tan x = 1', steps: ['特解 x₀ = π/4', 'tan 周期为 π'], a: 'x = π/4 + kπ（k∈Z）' },
    quiz: [
      { q: 'sin x = 1/2 在 [0, 2π) 内有几个解？', options: ['1', '2', '3', '4'], answer: 1, explain: 'π/6 与 5π/6。' },
      { q: 'tan x = √3 的通解是？', options: ['π/6 + 2kπ', 'π/3 + 2kπ', 'π/3 + kπ', 'π/6 + kπ'], answer: 2, explain: '特解 π/3，周期 π。' }
    ]
  });

  T({
    id: 'a2-seq-arith', unit: 'a2-c2', title: '等差数列', subtitle: '相邻两项差恒定，一切都能由 a₁ 与 d 算出',
    goal: '掌握通项、前 n 项和公式及性质，会解相关应用题',
    why: '《代数 第二册》第二章「一 数列」（p39）。',
    minutes: 11, prereq: ['b-sequence'],
    demo: function () {
      var o = [];
      o.push(S('定义：<b>aₙ₊₁ − aₙ = d</b>（常数）。a₁=3、d=2 时数列是 3,5,7,9,11…',
        br([3, 5, 7, 9, 11], ['a₁', 'a₂', 'a₃', 'a₄', 'a₅'], { hi: [2] }, '每步 +2')));
      o.push(S('通项：<b>aₙ = a₁ + (n−1)d</b>。因为从 a₁ 到 aₙ 要加 n−1 次 d。',
        st(['a₅ = 3 + 4×2 = 11', '一般地 aₙ = a₁ + (n−1)d', '图象是一群等距的点（定义在正整数上）'])));
      o.push(S('前 n 项和用<b>高斯配对</b>：首尾相加都等于 a₁+aₙ，共 n/2 对。',
        st(['Sₙ = a₁ + a₂ + … + aₙ', '倒写相加：2Sₙ = n(a₁ + aₙ)', 'Sₙ = n(a₁+aₙ)/2 = na₁ + n(n−1)d/2'])));
      o.push(S('性质：若 m+n = p+q，则 <b>aₘ + aₙ = aₚ + a_q</b>；aₙ 是 n 的一次函数。',
        st(['a₁ + a₅ = a₂ + a₄ = 2a₃', '等差中项：A = (a+b)/2'])));
      return o;
    },
    notes: [
      '<p>等差数列只有两个自由度：首项 a₁ 和公差 d，所有量都能由它们表示。</p>',
      '<p>求和的倒序相加法，本质是「配对后每对相等」，与小学高斯配对完全一样。</p>',
      '<p>甲种本第二章接着讲等比数列与数学归纳法；微积分第一章的数列极限也以等差数列为最简单的例子。</p>'
    ],
    example: { q: 'a₁=2、d=3，求 a₁₀ 与 S₁₀', steps: ['a₁₀ = 2 + 9×3 = 29', 'S₁₀ = 10(2+29)/2'], a: 'a₁₀=29，S₁₀=155' },
    quiz: [
      { q: '等差数列 4, 7, 10, … 的 a₈ 是？', options: ['22', '25', '28', '31'], answer: 1, explain: 'a₈ = 4 + 7×3 = 25。' },
      { q: '等差数列前 n 项和 Sₙ = ?', options: ['n·aₙ', 'n(a₁+aₙ)/2', 'a₁·dⁿ', '(a₁+aₙ)/2'], answer: 1, explain: '倒序相加得到。' }
    ]
  });

  T({
    id: 'a2-seq-geom', unit: 'a2-c2', title: '等比数列与无穷递缩和', subtitle: '每一项是前一项乘 q',
    goal: '掌握通项、求和公式、无穷递缩等比数列之和',
    why: '《代数 第二册》第二章「一 数列」及微积分初步第一章「极限」的衔接点。',
    minutes: 12, prereq: ['a2-seq-arith'],
    demo: function () {
      var o = [];
      o.push(S('定义：<b>aₙ₊₁ / aₙ = q</b>（常数）。a₁=2、q=2 时为 2,4,8,16,32…',
        br([2, 4, 8, 16, 32], ['a₁', 'a₂', 'a₃', 'a₄', 'a₅'], { hi: [4] }, '每步 ×2')));
      o.push(S('通项 <b>aₙ = a₁qⁿ⁻¹</b>；求和用「错位相减」。',
        st(['Sₙ = a₁ + a₁q + … + a₁qⁿ⁻¹', 'qSₙ =     a₁q + … + a₁qⁿ', '相减：(1−q)Sₙ = a₁(1−qⁿ)', 'q≠1 时 Sₙ = a₁(1−qⁿ)/(1−q)'])));
      o.push(S('当 <b>|q| &lt; 1</b> 且 n→∞ 时 qⁿ→0，得到无穷递缩和 <b>S = a₁/(1−q)</b>。',
        st(['1 + 1/2 + 1/4 + 1/8 + … = 2', '这是甲种本第一次正式遇到「无限项求和」', '严格定义要等《微积分初步》第一章的极限'])));
      o.push(S('等比中项：G² = ab（a、b 同号时 G = ±√ab）。',
        st(['aₘ·aₙ = aₚ·a_q  当 m+n = p+q', '与等差数列的「和相等」性质对应'])));
      return o;
    },
    notes: [
      '<p>等差看「差」，等比看「比」；两个数列的公式与性质几乎一一对应，可以对照记忆。</p>',
      '<p>求和公式必须讨论 q=1（此时 Sₙ = na₁）；无穷和只在 |q|&lt;1 时存在。</p>',
      '<p>甲种本微积分初步第一章用极限给出「无穷多项相加」的严格意义，第二册复利的三角形式也会用到 qⁿ。</p>'
    ],
    example: { q: '求 1 + 1/3 + 1/9 + … 的和', steps: ['a₁=1, q=1/3，|q|<1', 'S = 1/(1 − 1/3)'], a: '3/2' },
    quiz: [
      { q: '等比数列 3, 6, 12, … 的 a₅ 是？', options: ['24', '36', '48', '96'], answer: 2, explain: 'a₅ = 3×2⁴ = 48。' },
      { q: '无穷和 1 + 1/2 + 1/4 + … = ?', options: ['1', '2', '3', '发散'], answer: 1, explain: 'S = 1/(1−1/2) = 2。' }
    ]
  });

  T({
    id: 'a2-induction', unit: 'a2-c2', title: '数学归纳法', subtitle: '第一块骨牌倒下，且每块都能推倒下一块',
    goal: '掌握两步证明格式，能证明简单的等式与整除命题',
    why: '《代数 第二册》第二章（p65 起）：课本 2.4「数学归纳法」、2.5「数学归纳法的应用举例」，明确要求用归纳法严格证明等差、等比数列前 n 项和公式。',
    minutes: 12, prereq: ['a2-seq-arith'],
    demo: function () {
      var o = [];
      o.push(S('要证明与正整数 n 有关的命题 P(n)，只做两步：',
        st(['① 奠基：证明 P(1) 成立', '② 递推：假设 P(k) 成立，证明 P(k+1) 成立', '⇒ P(n) 对一切正整数 n 成立'])));
      o.push(S('例：证明 <b>1 + 3 + 5 + … + (2n−1) = n²</b>。先看前几项找规律。',
        br([1, 4, 9, 16, 25], ['n=1', 'n=2', 'n=3', 'n=4', 'n=5'], { done: [0, 1, 2, 3, 4] }, '前 n 个奇数之和恰是平方数')));
      o.push(S('① n=1：左边 1，右边 1² = 1，成立。',
        st(['P(1) ✓'])));
      o.push(S('② 设 n=k 时成立，则 n=k+1 时：',
        st(['1+3+…+(2k−1) + (2k+1)', '= k² + 2k + 1', '= (k+1)²  ✓', '∴ 命题对一切 n 成立'])));
      o.push(S('两个步骤缺一不可：只有奠基没有递推，推不到后面；只有递推没有奠基，整排骨牌没被推倒。',
        st(['常见错误：递推步骤里没有用上归纳假设', '归纳法证明的是「所有」，不是「前几个看起来对」'])));
      o.push(S('课本 2.5 节专门举例：用归纳法严格证明<b>等差、等比数列前 n 项和公式</b>，以及二项式定理、整除性命题。',
        st(['Sₙ = na₁ + n(n−1)d/2 可用归纳法验证', 'Sₙ = a₁(1−qⁿ)/(1−q) 同理', '课本把「先猜公式再严格证明」作为数列章的收尾'])));
      return o;
    },
    notes: [
      '<p>归纳法是演绎证明，不是不完全归纳；递推步骤必须明确使用「假设 P(k) 成立」。</p>',
      '<p>起点不一定是 n=1（可从 n₀ 开始），也可用于整除性、不等式、几何计数等命题。</p>',
      '<p>甲种本第三章不等式证明、第三册二项式定理的证明，都会再用这套格式。</p>'
    ],
    example: { q: '用归纳法证明 1+2+…+n = n(n+1)/2 的递推步', steps: ['假设 n=k 成立：Sₖ = k(k+1)/2', 'Sₖ₊₁ = Sₖ + (k+1) = (k+1)(k+2)/2'], a: '整理后即 (k+1)((k+1)+1)/2 ✓' },
    quiz: [
      { q: '数学归纳法的两步是？', options: ['验证 n=1、n=2', '奠基与递推', '猜想与验证', '求和与取极限'], answer: 1, explain: '先证起点，再证 k ⇒ k+1。' },
      { q: '递推步骤中必须用到什么？', options: ['归纳假设 P(k)', '计算器', '图象', '反例'], answer: 0, explain: '没有使用归纳假设的"证明"是无效的。' }
    ]
  });

  T({
    id: 'a2-ineq-proof', unit: 'a2-c3', title: '不等式的性质与证明', subtitle: '比较法、综合法、分析法',
    goal: '掌握不等式基本性质与三种常用证明方法，会解绝对值不等式',
    why: '《代数 第二册》第三章「不等式」（p80）。',
    minutes: 13, star: true, prereq: ['m-ineq', 'a1-set'],
    demo: function () {
      var o = [];
      o.push(S('基本性质：a &gt; b ⇔ a − b &gt; 0；两边同乘正数不变号，同乘负数变号。',
        st(['a > b, c > 0 ⇒ ac > bc', 'a > b, c < 0 ⇒ ac < bc', 'a > b > 0 ⇒ 1/a < 1/b'])));
      o.push(S('<b>比较法</b>：要证 A &gt; B，只证 A − B &gt; 0（常配方或因式分解）。',
        st(['证 a² + b² ≥ 2ab', 'a² + b² − 2ab = (a−b)² ≥ 0', '∴ 不等式成立，等号当 a=b'])));
      o.push(S('<b>综合法</b>由已知性质推出结论；<b>分析法</b>从结论倒推到已知，书写时再反过来。',
        st(['综合法：已知 → 性质 → 结论', '分析法：要证…只需证…显然成立', '复杂题常「分析找路、综合书写」'])));
      o.push(S('绝对值不等式：<b>|x| &lt; a ⇔ −a &lt; x &lt; a</b>；|x| &gt; a ⇔ x &lt; −a 或 x &gt; a。',
        nl(-5, 5, { ticks: [-5, -2, 0, 2, 5], segments: [
          { a: -2, b: 2, label: '|x| < 2', cls: 'is-hi' }], caption: '到原点距离小于 2' })));
      o.push(S('分式不等式要<b>先移项通分</b>，不要随手两边乘含 x 的式子（可能为负）。',
        st(['(x−1)/(x+2) > 0', '⇔ (x−1)(x+2) > 0 且 x ≠ −2', '解集 x < −2 或 x > 1'])));
      return o;
    },
    notes: [
      '<p>不等式证明的核心是把「大小」化成「差的正负」，再配方或分解。</p>',
      '<p>所有变形都要保证等价：乘除含未知量的式子、平方、取倒数都可能改变解集。</p>',
      '<p>甲种本微积分初步第一章用 ε−δ 语言定义极限时，本质上就是反复解这类不等式。</p>'
    ],
    example: { q: '解 |2x − 1| < 3', steps: ['−3 < 2x − 1 < 3', '−2 < 2x < 4'], a: '−1 < x < 2' },
    quiz: [
      { q: '|x| > 3 的解集是？', options: ['−3<x<3', 'x>3', 'x<−3 或 x>3', 'x<3'], answer: 2, explain: '到原点距离大于 3，落在两侧。' },
      { q: '证明 a²+b² ≥ 2ab 最常用的方法是？', options: ['比较法配方', '数学归纳法', '反证法', '画图'], answer: 0, explain: '作差得 (a−b)² ≥ 0。' }
    ]
  });

  T({
    id: 'a2-amgm', unit: 'a2-c3', title: '均值不等式与最值', subtitle: '和定积最大，积定和最小',
    goal: '掌握 (a+b)/2 ≥ √ab 及「一正二定三相等」',
    why: '《代数 第二册》第三章「不等式」，也是微积分之前最重要的代数最值工具。',
    minutes: 12, star: true, prereq: ['a2-ineq-proof', 'm-pyth'],
    demo: function () {
      var o = [];
      o.push(S('对 a,b &gt; 0，<b>(a+b)/2 ≥ √(ab)</b>，等号当且仅当 a=b。',
        st(['由 (√a − √b)² ≥ 0 展开即得', 'a + b ≥ 2√(ab)', '算术平均数 ≥ 几何平均数'])));
      o.push(S('几何证明：半圆中直径上两段为 a、b，半弦高恒 ≤ 半径。',
        sh([
          { k: 'line', x1: 120, y1: 200, x2: 520, y2: 200, cls: 'is-hi' },
          { k: 'circle', x: 320, y: 200, r: 200, cls: 'is-void' },
          { k: 'line', x1: 220, y1: 200, x2: 220, y2: 40, cls: 'is-on' },
          { k: 'line', x1: 220, y1: 40, x2: 120, y2: 200, cls: 'is-dim' },
          { k: 'line', x1: 220, y1: 40, x2: 520, y2: 200, cls: 'is-dim' },
          { k: 'text', x: 170, y: 220, t: 'a', cls: '' }, { k: 'text', x: 370, y: 220, t: 'b', cls: '' },
          { k: 'text', x: 195, y: 120, t: '√ab', cls: '' },
          { k: 'text', x: 320, y: 25, t: '半径 = (a+b)/2 ≥ √ab', cls: '' }
        ], '垂线高 = √(ab)，不超过半径')));
      o.push(S('用「一正二定三相等」求最值：各项为正、和或积为定值、能取到等号。',
        st(['若 x + y = 10（定值），则 xy ≤ 25，x=y=5 时最大', '若 xy = 36（定值），则 x + y ≥ 12，x=y=6 时最小'])));
      o.push(S('推广到 n 个正数：(a₁+…+aₙ)/n ≥ (a₁…aₙ)^(1/n)。',
        st(['三元：a+b+c ≥ 3(abc)^(1/3)', '常用于求面积/体积最值', '微积分的导数法会给出更一般的做法'])));
      return o;
    },
    notes: [
      '<p>均值不等式成立有三个前提：正数、有定值、等号能取到。少一个就不能直接用。</p>',
      '<p>「和定积最大、积定和最小」是它的直接推论，配凑常数让和或积成为定值是常见技巧。</p>',
      '<p>甲种本微积分初步第三章用导数求极值时会重新得到这些结论，并推广到更一般的函数。</p>'
    ],
    example: { q: 'x>0，求 x + 4/x 的最小值', steps: ['两项积 x·(4/x)=4 为定值', 'x + 4/x ≥ 2√4 = 4'], a: '最小值 4（x=2 时）' },
    quiz: [
      { q: 'x + 9/x（x>0）的最小值是？', options: ['3', '6', '9', '18'], answer: 1, explain: '≥ 2√9 = 6，x=3 时取到。' },
      { q: '均值不等式等号成立条件是？', options: ['a+b=0', 'a=b', 'ab=1', 'a>b'], answer: 1, explain: '各项相等时取等号。' }
    ]
  });

  T({
    id: 'a2-det', unit: 'a2-c4', title: '行列式与线性方程组', subtitle: '把消元结果写成一个数',
    goal: '会算二阶、三阶行列式，用克拉默法则解二元与三元线性方程组',
    why: '《代数 第二册》第四章（p115）：课文含 4.1 二阶行列式和二元线性方程组、4.3 三阶行列式的性质、4.5 三元线性方程组。',
    minutes: 12, prereq: ['m-eq-sys'],
    demo: function () {
      var o = [];
      o.push(S('二阶行列式定义：<b>|a b; c d| = ad − bc</b>（主对角线减副对角线）。',
        gr(2, 2, [
          { v: 'a', cls: 'is-on' }, { v: 'b', cls: 'is-dim' },
          { v: 'c', cls: 'is-dim' }, { v: 'd', cls: 'is-on' }], '主对角线 a·d 减去 b·c', 62)));
      o.push(S('解方程组 <b>2x + 3y = 7，x − y = 1</b>。先算系数行列式 D。',
        st(['D = |2  3; 1  −1| = 2(−1) − 3·1 = −5', 'D ≠ 0 ⇒ 方程组有唯一解'])));
      o.push(S('把常数列替换第 1 列得 Dₓ，替换第 2 列得 Dᵧ：<b>x = Dₓ/D，y = Dᵧ/D</b>。',
        st(['Dₓ = |7  3; 1  −1| = −7 − 3 = −10', 'Dᵧ = |2  7; 1   1| = 2 − 7 = −5', 'x = (−10)/(−5) = 2，y = (−5)/(−5) = 1'])));
      o.push(S('验算：2·2 + 3·1 = 7 ✓，2 − 1 = 1 ✓。若 D=0，则无解或无穷多解。',
        st(['D ≠ 0：唯一解', 'D = 0 且 Dₓ=Dᵧ=0：可能无穷多解', 'D = 0 但分子不为 0：无解'])));
      o.push(S('课本 4.3 节讲<b>三阶行列式</b>：按第一行展开，或用对角线法则（三条主对角线之和减三条副对角线之和）。',
        gr(3, 3, [
          { v: 'a₁', cls: 'is-on' }, { v: 'b₁', cls: '' }, { v: 'c₁', cls: '' },
          { v: 'a₂', cls: '' }, { v: 'b₂', cls: 'is-on' }, { v: 'c₂', cls: '' },
          { v: 'a₃', cls: '' }, { v: 'b₃', cls: '' }, { v: 'c₃', cls: 'is-on' }],
          'D = a₁b₂c₃ + b₁c₂a₃ + c₁a₂b₃ − c₁b₂a₃ − b₁a₂c₃ − a₁c₂b₃', 66)));
      o.push(S('课本 4.5 节把克拉默法则推广到<b>三元线性方程组</b>：D≠0 时 x = Dₓ/D、y = Dᵧ/D、z = D_z/D。',
        st(['每个 Dₓ、Dᵧ、D_z 都是把对应列换成常数列', '行列式性质（对调变号、某行乘 k 提 k、两行成比例则为 0）用来简化计算', '这正是初中「加减消元」在三元情形的一般化'])));
      o.push(S('这正是初中加减消元的一般化：把「制造相反系数」用行列式一次写清。',
        st(['二阶行列式 = 消元后的分母', '甲种本用它讨论三元方程组与直线位置关系'])));
      return o;
    },
    notes: [
      '<p>行列式是把方程组的系数按规则算出的一个数，它是否为 0 决定了方程组有没有唯一解。</p>',
      '<p>克拉默法则的形式很整齐，但计算量大；实际解题仍常用消元，行列式更适合做理论判断。</p>',
      '<p>甲种本平面解析几何判断两直线平行/重合/相交、求三角形面积（行列式形式）时都会用到。</p>'
    ],
    example: { q: '计算 |3 1; 2 4|', steps: ['主对角线 3×4 = 12', '副对角线 1×2 = 2'], a: '12 − 2 = 10' },
    quiz: [
      { q: '|1 2; 3 4| = ?', options: ['−2', '2', '10', '−10'], answer: 0, explain: '1×4 − 2×3 = −2。' },
      { q: '系数行列式 D=0 说明二元方程组？', options: ['必有唯一解', '无解或无穷多解', '必无解', '必有无穷多解'], answer: 1, explain: '需再看分子行列式才能区分。' }
    ]
  });

  T({
    id: 'a2-complex', unit: 'a2-c5', title: '复数的概念与运算', subtitle: '让 x² = −1 有解，把数从直线扩到平面',
    goal: '理解 i²=−1、复平面、共轭，会做加减乘除',
    why: '《代数 第二册》第五章「一 复数的概念 / 二 复数的运算」（p191、p201）。',
    minutes: 13, star: true, prereq: ['m-eq2', 'm-coord'],
    demo: function () {
      var o = [];
      o.push(S('一元二次方程 x²+1=0 在实数内无解（Δ&lt;0）。引入 <b>i² = −1</b>，解为 ±i。',
        st(['x² + 1 = 0  ⇒  x = ±i', '复数 z = a + bi（a 实部，b 虚部）', 'b = 0 时退化为实数'])));
      o.push(S('复数与<b>复平面</b>上的点一一对应：横轴实轴、纵轴虚轴。',
        ax({ x: [-4, 4], y: [-3, 3] }, { points: [{ x: 3, y: 2, label: 'z = 3+2i', cls: 'is-hi' }],
          lines: [{ a: [0, 0], b: [3, 2], cls: 'is-on' }, { a: [3, 0], b: [3, 2], cls: 'is-dim' }, { a: [0, 2], b: [3, 2], cls: 'is-dim' }],
          caption: '横轴实数，纵轴虚数' })));
      o.push(S('加减法按实部虚部分别合并；乘法按多项式展开并用 i²=−1。',
        st(['(3+2i) + (1−i) = 4 + i', '(1+i)² = 1 + 2i + i² = 2i', '(a+bi)(a−bi) = a² + b²'])));
      o.push(S('除法：分子分母同乘<b>共轭复数</b>，把分母实数化（和分母有理化同一招）。',
        st(['1/(1+i) = (1−i)/((1+i)(1−i))', '= (1−i)/2 = ½ − ½i'])));
      return o;
    },
    notes: [
      '<p>复数不是「假想的数」，它是把数轴扩成平面后得到的数系，且与平面向量一一对应。</p>',
      '<p>共轭 z̄=a−bi 的乘积 z·z̄ = a²+b² 恒为非负实数，这是除法与求模的关键。</p>',
      '<p>下一节用模与辐角写三角形式；甲种本第三册高次方程、微积分里欧拉公式都会用到复数。</p>'
    ],
    example: { q: '计算 (2+i)(2−i) 与 1/i', steps: ['(2+i)(2−i) = 4 − i² = 5', '1/i = i/i² = −i'], a: '5 与 −i' },
    quiz: [
      { q: 'i² 等于？', options: ['1', '−1', '0', 'i'], answer: 1, explain: '这是虚数单位的定义。' },
      { q: '(1+2i)(1−2i) = ?', options: ['1', '3', '5', '−3'], answer: 2, explain: '1² + 2² = 5。' }
    ]
  });

  T({
    id: 'a2-complex-tri', unit: 'a2-c5', title: '复数的三角形式与棣莫佛定理', subtitle: '用模与辐角表示，把乘方变成角翻倍',
    goal: '会写 r(cosθ + i sinθ)，掌握乘法与棣莫佛定理',
    why: '《代数 第二册》第五章「三 复数的三角形式」（p212）。',
    minutes: 13, prereq: ['a2-complex', 'a1-trig-any'],
    demo: function () {
      var o = [];
      o.push(S('复数 z=a+bi 的<b>模</b> r = √(a²+b²)，<b>辐角</b> θ 满足 cosθ=a/r、sinθ=b/r。',
        ax({ x: [-4, 4], y: [-3, 3] }, { points: [{ x: 2, y: 2, label: 'z', cls: 'is-hi' }],
          lines: [{ a: [0, 0], b: [2, 2], cls: 'is-on' }, { a: [2, 0], b: [2, 2], cls: 'is-dim' }],
          caption: 'r = |Oz|，θ 是与实轴正方向的夹角' })));
      o.push(S('三角形式：<b>z = r(cos θ + i sin θ)</b>。例如 1+i = √2(cos π/4 + i sin π/4)。',
        st(['r = √(1²+1²) = √2', 'cosθ = 1/√2, sinθ = 1/√2 ⇒ θ = π/4'])));
      o.push(S('乘法：模相乘、辐角相加（用两角和公式展开即可验证）。',
        st(['z₁z₂ = r₁r₂[cos(θ₁+θ₂) + i sin(θ₁+θ₂)]', '除法：模相除、辐角相减'])));
      o.push(S('<b>棣莫佛定理</b>：zⁿ = rⁿ(cos nθ + i sin nθ)。乘方变成角度乘 n。',
        st(['(cosθ + i sinθ)² = cos2θ + i sin2θ', '(1+i)⁸ = (√2)⁸(cos 2π + i sin 2π) = 16'])));
      o.push(S('由此可求 n 次单位根：zⁿ=1 的 n 个根均匀分布在单位圆上。',
        sh([
          { k: 'circle', x: 320, y: 150, r: 100, cls: 'is-on' },
          { k: 'line', x1: 60, y1: 150, x2: 580, y2: 150, cls: 'is-dim' },
          { k: 'line', x1: 320, y1: 280, x2: 320, y2: 20, cls: 'is-dim' },
          { k: 'circle', x: 420, y: 150, r: 6, cls: 'is-hi' },
          { k: 'circle', x: 220, y: 150, r: 6, cls: 'is-hi' },
          { k: 'circle', x: 320, y: 50, r: 6, cls: 'is-hi' },
          { k: 'circle', x: 320, y: 250, r: 6, cls: 'is-hi' },
          { k: 'text', x: 320, y: 12, t: 'z⁴ = 1 的四个根（4 等分圆周）', cls: '' }
        ], '代数与几何在这里合一')));
      return o;
    },
    notes: [
      '<p>三角形式把复数乘法从「展开四项」变成「长度相乘、角度相加」，几何意义一目了然。</p>',
      '<p>棣莫佛定理是和差角公式的直接推论，也是推导 n 倍角公式、单位根的捷径。</p>',
      '<p>甲种本第三册高次方程在复数域内恰有 n 个根；微积分里的欧拉公式 e^(iθ)=cosθ+i sinθ 是这一节的延续。</p>'
    ],
    example: { q: '把 −1 + i 写成三角形式', steps: ['r = √2', '点在第二象限，θ = 3π/4'], a: '√2(cos 3π/4 + i sin 3π/4)' },
    quiz: [
      { q: '复数 1+i 的模是？', options: ['1', '√2', '2', '√3'], answer: 1, explain: '√(1²+1²) = √2。' },
      { q: '棣莫佛定理中 (cosθ+i sinθ)ⁿ = ?', options: ['cos θⁿ + i sin θⁿ', 'cos nθ + i sin nθ', 'n(cosθ+i sinθ)', 'cos θ + i sin nθ'], answer: 1, explain: '角度乘 n，模为 1。' }
    ]
  });

  /* ================= 代数 第三册 ================= */
  T({
    id: 'a3-poly', unit: 'a3-c1', title: '一元多项式、综合除法与因式定理', subtitle: '把整数的除法搬进多项式',
    goal: '掌握带余除法、综合除法、余数定理与因式定理',
    why: '《代数 第三册》*第一章 1.1～1.5（p1～p17）：课本专设「综合除法」「余数定理（又称余式定理、裴蜀定理）」「因式定理」「利用综合除法、因式定理分解因式」等小节。',
    minutes: 13, prereq: ['m-poly', 'p-div'],
    demo: function () {
      var o = [];
      o.push(S('整数除法 <b>84 = 5×16 + 4</b> 中，余数小于除数。多项式完全类似。',
        st(['f(x) = g(x)·q(x) + r(x)', '其中 r(x) = 0 或 deg r < deg g', '这就是多项式的带余除法'])));
      o.push(S('例：用 x−1 除 f(x) = x³ − 2x² + 3x − 2，逐项消去最高次。',
        st(['x³ − 2x² + 3x − 2', '减去 x²(x−1) = x³ − x² → 余 −x² + 3x − 2', '减去 (−x)(x−1) = −x² + x → 余 2x − 2', '减去 2(x−1) = 2x − 2 → 余 0'])));
      o.push(S('所以 f(x) = (x−1)(x² − x + 2)，余式为 0，即 <b>x−1 是因式</b>。',
        st(['余式 r = 0 ⇔ g(x) 整除 f(x)', '与整数「整除」概念完全对应'])));
      o.push(S('课本称它为<b>余数定理</b>（也叫余式定理、剩余定理或裴蜀定理）：f(x) 除以 x−b 的余数等于 f(b)。',
        st(['f(1) = 1 − 2 + 3 − 2 = 0  ✓ 与上面一致', '由此得因式定理：有因式 x−b ⇔ f(b)=0（充要条件）', '求根时先试 ±1、±2 等常数项因数'])));
      o.push(S('课本还专门讲<b>综合除法</b>：只写降幂排列的系数、逐次乘加，比长除快得多，是本章分解因式的主力工具。',
        st(['1.1 一元多项式与带余除法', '1.2 综合除法（系数表运算）', '1.3 余数定理 / 裴蜀定理', '1.4 因式定理（充要条件与证明）', '1.5 利用综合除法、因式定理分解因式', '1.6 一元 n 次方程根的个数'], '本章主线是「因式分解」，不是单纯求根')));
      return o;
    },
    notes: [
      '<p>多项式与整数高度平行：带余除法、整除、因式分解，都可以对照小学的质因数分解理解。</p>',
      '<p>课本用综合除法把「除法」压缩成系数表运算，再用余数定理判断 f(b) 是否为 0，从而快速找出一次因式。</p>',
      '<p>因式定理把「求根」和「找因式」变成同一件事；本章标 * 为选学，但解析几何联立方程、微积分有理式分解仍会用到。</p>'
    ],
    example: { q: 'f(x)=x²−5x+6，验证 x−2 是否为因式', steps: ['算 f(2) = 4 − 10 + 6', '= 0'], a: '是，f(x)=(x−2)(x−3)' },
    quiz: [
      { q: 'f(x) 除以 (x−a) 的余式是？', options: ['f(0)', 'f(a)', 'a', 'f′(a)'], answer: 1, explain: '这就是余式定理。' },
      { q: '若 f(3)=0，则下列哪项一定是因式？', options: ['x+3', 'x−3', '3x', 'x²−3'], answer: 1, explain: '因式定理：f(a)=0 ⇔ (x−a) 是因式。' }
    ]
  });

  T({
    id: 'a3-high-eq', unit: 'a3-c1', title: '高次方程与韦达定理的推广', subtitle: '降次、试根、在复数域内数根',
    goal: '会用因式分解解简单高次方程，理解 n 次方程恰有 n 个复根',
    why: '《代数 第三册》*第一章「二 高次方程」（p17）。',
    minutes: 12, prereq: ['a3-poly', 'a2-complex'],
    demo: function () {
      var o = [];
      o.push(S('解 <b>x³ − 6x² + 11x − 6 = 0</b>：先试常数项的因数 ±1、±2、±3。',
        st(['f(1) = 1 − 6 + 11 − 6 = 0  ✓', '⇒ (x−1) 是因式'])));
      o.push(S('做带余除法降次：',
        st(['x³ − 6x² + 11x − 6 = (x−1)(x² − 5x + 6)', '再分解二次式：x² − 5x + 6 = (x−2)(x−3)'])));
      o.push(S('三个根为 <b>1、2、3</b>。因式分解是把高次降为一次的唯一实用手段。',
        st(['(x−1)(x−2)(x−3) = 0', '⇒ x = 1, 2, 3'])));
      o.push(S('若二次式判别式 Δ&lt;0（如 x²+1），就要到<b>复数域</b>里补上两个根 ±i。',
        st(['实系数 n 次方程在复数域恰有 n 个根（计重数）', '这就是引入复数的根本理由之一'])));
      o.push(S('韦达定理推广：三根之和 = −b/a，两两积之和 = c/a，三根之积 = −d/a。',
        st(['对 x³ − 6x² + 11x − 6 = 0', '和 = 6，两两积之和 = 11，积 = 6', '与根 1,2,3 完全吻合'])));
      return o;
    },
    notes: [
      '<p>解高次方程没有通用公式（五次以上），实际手段是「试有理根 → 因式定理降次 → 解低次方程」。</p>',
      '<p>因式分解在这里的分量与初中完全相同，只是对象从数字换成多项式。</p>',
      '<p>甲种本把这一章列为选学；但「n 次方程有 n 个复根」的结论在解析几何讨论交点个数时会用到。</p>'
    ],
    example: { q: '方程 x³ − x = 0 的所有实根？', steps: ['提取 x：x(x²−1)=0', '再分解平方差'], a: 'x = 0, 1, −1' },
    quiz: [
      { q: 'x³ − 6x² + 11x − 6 = 0 的根是？', options: ['1,2,3', '−1,−2,−3', '1,2,6', '0,1,2'], answer: 0, explain: '代入验证并分解为 (x−1)(x−2)(x−3)。' },
      { q: '实系数二次方程 Δ<0 时，根在哪个数域？', options: ['有理数域', '实数域', '复数域', '无根'], answer: 2, explain: '在复数域有一对共轭复根。' }
    ]
  });

  T({
    id: 'a3-perm', unit: 'a3-c2', title: '排列', subtitle: '分步用乘法，取出还要排顺序',
    goal: '掌握乘法原理、排列数 A(n,m) 与常见限制条件',
    why: '《代数 第三册》第二章「一 排列与组合」（p42）。',
    minutes: 11, prereq: ['m-prob'],
    demo: function () {
      var o = [];
      o.push(S('从 a、b、c 三个字母里取 2 个<b>排成一列</b>，有多少种？',
        tr([
          { id: 'r', label: '第1位', x: 320, y: 40, cls: 'is-on' },
          { id: 'a', label: 'a', x: 140, y: 130, cls: '' }, { id: 'b', label: 'b', x: 320, y: 130, cls: '' }, { id: 'c', label: 'c', x: 500, y: 130, cls: '' },
          { id: 'ab', label: 'ab', x: 90, y: 235, cls: 'is-done' }, { id: 'ac', label: 'ac', x: 210, y: 235, cls: 'is-done' },
          { id: 'ba', label: 'ba', x: 310, y: 235, cls: 'is-done' }, { id: 'bc', label: 'bc', x: 410, y: 235, cls: 'is-done' },
          { id: 'ca', label: 'ca', x: 500, y: 235, cls: 'is-done' }, { id: 'cb', label: 'cb', x: 590, y: 235, cls: 'is-done' }
        ], [
          { from: 'r', to: 'a' }, { from: 'r', to: 'b' }, { from: 'r', to: 'c' },
          { from: 'a', to: 'ab' }, { from: 'a', to: 'ac' }, { from: 'b', to: 'ba' }, { from: 'b', to: 'bc' },
          { from: 'c', to: 'ca' }, { from: 'c', to: 'cb' }
        ], '3 × 2 = 6 种（顺序有关）')));
      o.push(S('第 1 位有 n 种选法，第 2 位剩 n−1 种……由<b>乘法原理</b>得排列数。',
        st(['A(n,m) = n(n−1)…(n−m+1)', '= n! / (n−m)!', 'A(5,3) = 5×4×3 = 60'])));
      o.push(S('特例：全排列 A(n,n) = n!；规定 0! = 1。',
        st(['A(4,4) = 4! = 24', '5! = 120', '阶乘增长极快'])));
      o.push(S('有限制条件时，优先安排特殊元素或特殊位置（如「0 不能排在首位」）。',
        st(['分类用加法，分步用乘法', '「至少 / 至多」常用间接法：总数减去不合要求的'])));
      return o;
    },
    notes: [
      '<p>排列与组合的唯一区别是「是否考虑顺序」；先判断这一点，公式就不会选错。</p>',
      '<p>两个原理：完成一件事分若干步用乘法，分若干类用加法。</p>',
      '<p>甲种本下一节组合、二项式定理、第三章概率，全部建立在这两个原理上。</p>'
    ],
    example: { q: '5 人中选 3 人分别担任班长、学习委员、文体委员，有几种？', steps: ['职务不同 ⇒ 顺序有关，用排列', 'A(5,3) = 5×4×3'], a: '60 种' },
    quiz: [
      { q: 'A(5,2) = ?', options: ['10', '20', '25', '60'], answer: 1, explain: '5×4 = 20。' },
      { q: '从 4 个数中取 2 个排列，考虑顺序吗？', options: ['考虑', '不考虑', '看情况', '只考虑大小'], answer: 0, explain: '排列与顺序有关，ab 与 ba 是两种。' }
    ]
  });

  T({
    id: 'a3-comb', unit: 'a3-c2', title: '组合与组合数性质', subtitle: '只挑出来，不排顺序',
    goal: '掌握 C(n,m) 公式与对称性、递推式',
    why: '《代数 第三册》第二章「一 排列与组合」（p42）。',
    minutes: 11, prereq: ['a3-perm'],
    demo: function () {
      var o = [];
      o.push(S('从 a、b、c 中取 2 个<b>不计顺序</b>，只有 {a,b}、{a,c}、{b,c} 三种。',
        gr(1, 3, [
          { v: '{a, b}', cls: 'is-on' }, { v: '{a, c}', cls: 'is-on' }, { v: '{b, c}', cls: 'is-on' }], 'C(3,2) = 3', 110)));
      o.push(S('排列数比组合数多了「把取出的 m 个再排一遍」这一步，所以 <b>C(n,m) = A(n,m)/m!</b>。',
        st(['C(n,m) = n! / (m!(n−m)!)', 'C(5,2) = (5×4)/(2×1) = 10'])));
      o.push(S('两条重要性质：<b>C(n,m) = C(n,n−m)</b>、<b>C(n,m) = C(n−1,m−1) + C(n−1,m)</b>。',
        st(['对称性：选 m 个留下 ⇔ 选 n−m 个去掉', '递推式：按「含不含某个特定元素」分类', '这正是杨辉三角的生成规则'])));
      o.push(S('杨辉三角：每行两端为 1，中间每个数等于肩上两数之和。',
        gr(1, 5, [
          { v: '1', cls: 'is-on' }, { v: '1  1', cls: 'is-on' }, { v: '1  2  1', cls: 'is-on' },
          { v: '1  3  3  1', cls: 'is-hi' }, { v: '1  4  6  4  1', cls: 'is-done' }], '第 5 行就是 (a+b)⁴ 的系数', 170)));
      return o;
    },
    notes: [
      '<p>组合数解决「选多少人、多少物」，与顺序无关；应用题里先问「交换两个元素算不算新方案」。</p>',
      '<p>对称性常用来化简 C(n, n−m)；递推式既是证明工具，也是杨辉三角的来源。</p>',
      '<p>下一节二项式定理的系数正是组合数，第三章古典概型也要用它数「有利结果数」。</p>'
    ],
    example: { q: '从 8 人中选 3 人组成小组，有几种？', steps: ['不计顺序，用组合', 'C(8,3) = (8×7×6)/(3×2×1)'], a: '56 种' },
    quiz: [
      { q: 'C(6,2) = ?', options: ['12', '15', '30', '36'], answer: 1, explain: '(6×5)/2 = 15。' },
      { q: 'C(10,8) 等于？', options: ['C(10,2)', 'A(10,2)', 'C(8,2)', '10!'], answer: 0, explain: '由对称性 C(n,m)=C(n,n−m)。' }
    ]
  });

  T({
    id: 'a3-binom', unit: 'a3-c2', title: '二项式定理', subtitle: '展开 (a+b)ⁿ 不用逐次相乘',
    goal: '掌握展开式、通项公式与系数性质',
    why: '《代数 第三册》第二章「二 二项式定理」（p68）。',
    minutes: 12, star: true, prereq: ['a3-comb', 'm-poly'],
    demo: function () {
      var o = [];
      o.push(S('从 (a+b)² = a²+2ab+b²、(a+b)³ = a³+3a²b+3ab²+b³ 观察系数。',
        gr(1, 3, [
          { v: 'n=1:  1  1', cls: 'is-on' }, { v: 'n=2:  1  2  1', cls: 'is-on' },
          { v: 'n=3:  1  3  3  1', cls: 'is-hi' }], '系数就是杨辉三角', 170)));
      o.push(S('一般形式：<b>(a+b)ⁿ = Σ C(n,k) aⁿ⁻ᵏ bᵏ</b>。',
        st(['(a+b)⁴ = a⁴ + 4a³b + 6a²b² + 4ab³ + b⁴', '系数 1,4,6,4,1 = C(4,k)'])));
      o.push(S('为什么系数是组合数？n 个括号里选 k 个取 b、其余取 a，方案数就是 <b>C(n,k)</b>。',
        st(['每项都来自「从 n 个因式中挑 k 个 b」', '这正是组合的定义'])));
      o.push(S('通项公式 <b>Tₖ₊₁ = C(n,k) aⁿ⁻ᵏ bᵏ</b>，可直接求指定项或某项系数。',
        st(['求 (x+2)⁵ 中 x³ 的系数', '取 k=2：C(5,2)·2² = 10×4 = 40'])));
      o.push(S('系数和：令 a=b=1 得 ΣC(n,k) = <b>2ⁿ</b>；奇数项和 = 偶数项和 = 2ⁿ⁻¹。',
        st(['(1+1)ⁿ = 2ⁿ', '(1−1)ⁿ = 0 ⇒ 交错和为 0'])));
      return o;
    },
    notes: [
      '<p>二项式定理是分配律的 n 次版本；系数 C(n,k) 来自「从 n 个括号里选 k 个」的计数。</p>',
      '<p>遇到「指定项、常数项、系数和」三类题，分别用通项公式、令字母指数为 0、赋值法。</p>',
      '<p>甲种本第三章概率的二项分布、微积分里 (1+x)ⁿ 的近似与级数展开，都是它的延伸。</p>'
    ],
    example: { q: '求 (x + 1)⁶ 展开式中 x⁴ 的系数', steps: ['通项 C(6,k)x⁶⁻ᵏ', '令 6−k=4 ⇒ k=2'], a: 'C(6,2) = 15' },
    quiz: [
      { q: '(a+b)⁴ 中 a²b² 的系数是？', options: ['4', '6', '8', '12'], answer: 1, explain: 'C(4,2) = 6。' },
      { q: '所有二项式系数之和 ΣC(n,k) = ?', options: ['n', 'n²', '2ⁿ', 'n!'], answer: 2, explain: '令 a=b=1 即得。' }
    ]
  });

  T({
    id: 'a3-prob', unit: 'a3-c3', title: '概率：古典概型与独立事件', subtitle: '把树状图升级成公式',
    goal: '掌握 P(A)=m/n、加法公式、乘法公式与独立重复试验',
    why: '《代数 第三册》第三章「概率」（p84）。',
    minutes: 12, prereq: ['a3-comb', 'm-prob'],
    demo: function () {
      var o = [];
      o.push(S('古典概型：所有结果等可能时，<b>P(A) = 有利结果数 / 总结果数</b>。',
        st(['掷一枚骰子出现偶数：3/6 = 1/2', '计数工具就是排列组合'])));
      o.push(S('互斥事件用加法：<b>P(A∪B) = P(A) + P(B)</b>；对立事件 P(Ā) = 1 − P(A)。',
        st(['掷骰子出现 1 或 2：1/6 + 1/6 = 1/3', '「至少一个」常用 1 − P(一个都没有)'])));
      o.push(S('独立事件用乘法：<b>P(A∩B) = P(A)P(B)</b>。两次抛硬币都用树状图数。',
        tr([
          { id: 'r', label: '开始', x: 320, y: 35, cls: '' },
          { id: 'a', label: '正', x: 180, y: 105, cls: '' }, { id: 'b', label: '反', x: 460, y: 105, cls: '' },
          { id: 'c', label: '正正', x: 100, y: 200, cls: 'is-on' }, { id: 'd', label: '正反', x: 250, y: 200, cls: 'is-on' },
          { id: 'e', label: '反正', x: 400, y: 200, cls: 'is-on' }, { id: 'f', label: '反反', x: 550, y: 200, cls: 'is-on' }
        ], [
          { from: 'r', to: 'a' }, { from: 'r', to: 'b' }, { from: 'a', to: 'c' }, { from: 'a', to: 'd' },
          { from: 'b', to: 'e' }, { from: 'b', to: 'f' }
        ], '每个分支概率 1/2，沿路径相乘')));
      o.push(S('n 次独立重复试验中恰好成功 k 次的概率（二项分布）：',
        st(['P = C(n,k) pᵏ (1−p)ⁿ⁻ᵏ', '系数 C(n,k) 正是上一节的组合数', '例：抛 3 次恰好 2 次正面 = C(3,2)(1/2)³ = 3/8'])));
      return o;
    },
    notes: [
      '<p>本章把初中「数等可能结果」升级为公式：复杂计数交给排列组合，多步事件交给乘法原理。</p>',
      '<p>「互斥」不能同时发生，用加法；「独立」互不影响，用乘法；两者不要混淆。</p>',
      '<p>二项分布是甲种本概率章的终点，也是大学概率统计的起点；微积分里求连续分布时会把求和换成积分。</p>'
    ],
    example: { q: '抛 3 枚硬币，恰好 2 枚正面的概率？', steps: ['C(3,2) = 3 种有利结果', '总结果 2³ = 8'], a: '3/8' },
    quiz: [
      { q: '掷两枚骰子，点数和为 7 的概率是？', options: ['1/6', '1/12', '1/9', '1/36'], answer: 0, explain: '6 种有利结果 / 36 种 = 1/6。' },
      { q: '两独立事件同时发生的概率用？', options: ['加法', '乘法', '减法', '取最大'], answer: 1, explain: '独立时用 P(A)P(B)。' }
    ]
  });

})();
