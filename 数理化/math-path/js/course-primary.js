/* MathPath — 小学段：算术基本功与图形直觉 */
(function () {
  'use strict';
  var MP = window.MathPath, U = MP.util, S = U.step;

  function C(t, cls) { return { t: t, cls: cls || '' }; }
  function L(cells, cls, label) { return { cells: cells, cls: cls || '', label: label || '' }; }
  function row(str, cls, label) { return L(String(str).split('').map(function (c) { return C(c, cls || ''); }), '', label); }
  function vertical(a, b, o) {
    o = o || {};
    var n = Math.max(String(a).length, String(b).length, String(o.result || '').length);
    function pad(s) { s = String(s); while (s.length < n) s = ' ' + s; return s.split(''); }
    var A = pad(a), B = pad(b), R = o.result == null ? null : pad(o.result);
    var lines = [];
    if (o.carry) lines.push(L(o.carry.map(function (c) { return C(c || ' ', c ? 'is-on' : ''); }), '', ''));
    lines.push(L(A.map(function (c, i) { return C(c, i === o.hi ? 'is-hi' : ''); }), '', ''));
    lines.push(L(B.map(function (c, i) { return C(c, i === o.hi ? 'is-hi' : ''); }), '', '+'));
    lines.push(L(A.map(function () { return C(' '); }), 'is-rule', ''));
    if (R) lines.push(L(R.map(function (c, i) { return C(c, i === o.hi ? 'is-hi' : (c.trim() ? 'is-done' : '')); }), '', ''));
    return { lines: lines, caption: o.caption || '' };
  }
  function T(o) { MP.registerTopic(o); }

  MP.registerUnits([
    { id: 'p-num', track: 'primary', name: '数与运算', desc: '位值、竖式、四则混合' },
    { id: 'p-frac', track: 'primary', name: '分数与小数', desc: '通分约分、百分数、近似数' },
    { id: 'p-rel', track: 'primary', name: '比与关系', desc: '比例、用字母表示数、规律' },
    { id: 'p-geo', track: 'primary', name: '图形与度量', desc: '角度、面积割补、圆、因数' }
  ]);

  /* ============ 一、数与运算 ============ */
  T({
    id: 'p-place', unit: 'p-num', title: '十进制与位值', subtitle: '同一个数字，站的位置不同，值就不同',
    goal: '理解「数位」和「位值」，能把一个多位数按位拆开',
    why: '甲种本·代数1 讲幂函数、指数记号时，10²、10³ 就是位值的推广；解析几何的坐标也是位值思想。',
    view: 'steps', minutes: 8,
    demo: function () {
      var names = ['千', '百', '十', '个'], d = ['3', '5', '8', '2'];
      var out = [];
      out.push(S('把 <b>3582</b> 写进数位表。每个数字的值 = 数字 × 它所在位置的单位。',
        { lines: [L(names.map(function (x) { return C(x, 'is-dim'); }), '', '数位'), L(d.map(function (x) { return C(x); }), '', '数字')], caption: '四个位置：千、百、十、个' }));
      ['千', '百', '十', '个'].forEach(function (nm, i) {
        var vals = [3000, 500, 80, 2];
        out.push(S('第 <b>' + (i + 1) + '</b> 位是「' + nm + '」位：数字 <b>' + d[i] + '</b> 表示 <b>' + vals[i] + '</b>。',
          { lines: [L(names.map(function (x, j) { return C(x, j === i ? 'is-hi' : 'is-dim'); }), '', '数位'),
                    L(d.map(function (x, j) { return C(x, j === i ? 'is-hi' : ''); }), '', '数字'),
                    L([C(String(vals[i]), 'is-on')], '', '这一位的值')], caption: '10 的幂：1000 / 100 / 10 / 1' }));
      });
      out.push(S('合起来：<b>3582 = 3×1000 + 5×100 + 8×10 + 2×1</b>。以后学 <code>10ⁿ</code>、多项式，都是这个写法的推广。',
        { lines: [row('3582'), row('= 3×1000 + 5×100 + 8×10 + 2', 'is-on')], caption: '按位展开' }));
      return out;
    },
    notes: [
      '<p>古人用石子记数，数大了就要搬一堆石头。十进制的天才之处是：<b>只用 0~9 十个符号，靠「位置」表示任意大的数</b>。</p>',
      '<p>从右往左，每一位的单位是前一位的 10 倍：个(1)、十(10)、百(100)、千(1000)。把一个数写成「各位数字 × 单位之和」叫按位展开。</p>',
      '<p>整数部分是 10⁰、10¹、10²…，小数部分是 10⁻¹、10⁻²…。甲种本里 <code>aⁿ</code>、科学记数法、对数的常用对数，源头都在这里。</p>'
    ],
    example: { q: '把 7045 按位展开', steps: ['7045 中 0 在百位，表示 0 个 100，但不能省略不写（否则变成 745）', '7045 = 7×1000 + 0×100 + 4×10 + 5×1'], a: '7×1000 + 0×100 + 4×10 + 5' },
    quiz: [
      { q: '数字 7 在 5731 中表示多少？', options: ['7', '70', '700', '7000'], answer: 2, explain: '7 在百位，表示 7×100 = 700。' },
      { q: '10⁴ 等于多少？', options: ['40', '1000', '10000', '100000'], answer: 2, explain: '10⁴ = 10×10×10×10 = 10000，也就是「万位」的单位。' }
    ]
  });

  T({
    id: 'p-add', unit: 'p-num', title: '竖式加法与进位', subtitle: '满十进一，从个位算起',
    goal: '掌握多位数加法的竖式与进位规则，理解为什么从个位开始',
    why: '一切代数恒等变形（合并同类项、通分、多项式相加）都在重复「相同单位才能相加」这一条。',
    view: 'steps', minutes: 8, prereq: ['p-place'],
    demo: function () {
      var o = [];
      o.push(S('计算 <b>458 + 276</b>。相同数位对齐，从<b>个位</b>开始。', vertical(458, 276, {}), { 当前位: '未开始' }));
      o.push(S('个位：<b>8 + 6 = 14</b>，写 <b>4</b>，向十位进 <b>1</b>。', vertical(458, 276, { hi: 3, carry: ['', '', '1', ''], result: '   4' }), { 进位: 1 }));
      o.push(S('十位：<b>5 + 7 + 1(进位) = 13</b>，写 <b>3</b>，再向百位进 <b>1</b>。', vertical(458, 276, { hi: 2, carry: ['', '1', '1', ''], result: '  34' }), { 进位: 1 }));
      o.push(S('百位：<b>4 + 2 + 1 = 7</b>，写 <b>7</b>。', vertical(458, 276, { hi: 1, carry: ['', '1', '1', ''], result: ' 734' }), { 进位: 0 }));
      o.push(S('结果 <b>734</b>。注意：只有<b>同一数位</b>才能直接相加，这正是「单位相同才能相加」。',
        vertical(458, 276, { carry: ['', '1', '1', ''], result: ' 734' }), { 结果: 734 }));
      return o;
    },
    notes: [
      '<p>8 个一加 6 个一是 14 个一，10 个一换成 1 个十，剩下 4 个一 —— 这就是「满十进一」。</p>',
      '<p>竖式不是死规则：对齐数位 = 对齐单位；从个位起 = 因为进位只会往高位传。</p>',
      '<p>初中合并同类项 <code>3x + 5x = 8x</code>、分数通分后相加、多项式按次幂对齐，都是同一件事换了符号。</p>'
    ],
    example: { q: '计算 397 + 528', steps: ['个位 7+8=15，写 5 进 1', '十位 9+2+1=12，写 2 进 1', '百位 3+5+1=9'], a: '925' },
    quiz: [
      { q: '计算 268 + 157 = ?', options: ['415', '425', '325', '515'], answer: 1, explain: '个位 8+7=15 进 1；十位 6+5+1=12 进 1；百位 2+1+1=4，得 425。' },
      { q: '为什么竖式要从个位算起？', options: ['习惯而已', '因为进位只会向更高位传递', '因为个位数字最大', '因为老师规定'], answer: 1, explain: '进位方向是低位→高位，先算低位才能保证高位拿到完整结果。' }
    ]
  });

  T({
    id: 'p-sub', unit: 'p-num', title: '竖式减法与借位', subtitle: '不够减时，向高位借一当十',
    goal: '掌握连续借位，尤其是被减数中间有 0 的情况',
    why: '代数里的「移项变号」「配方时补项再减去」，本质是同一个量的两种补偿。',
    view: 'steps', minutes: 9, prereq: ['p-add'],
    demo: function () {
      var o = [];
      o.push(S('计算 <b>502 − 276</b>。个位是 2 − 6，不够减，需要借位。', vertical(502, 276, {}), { 被减数: 502 }));
      o.push(S('十位是 0，没得借；继续向百位借：<b>5 个百 → 4 个百 + 10 个十</b>。', vertical(502, 276, { hi: 1, result: '   ' }), { 百位剩: 4 }));
      o.push(S('十位再借 1 个十给个位：<b>10 个十 → 9 个十 + 10 个一</b>，个位变成 <b>12</b>。', vertical(502, 276, { hi: 3, result: '   ' }), { 个位变成: 12 }));
      o.push(S('个位：<b>12 − 6 = 6</b>。', vertical(502, 276, { hi: 3, result: '   6' }), {}));
      o.push(S('十位：<b>9 − 7 = 2</b>；百位：<b>4 − 2 = 2</b>。结果 <b>226</b>。', vertical(502, 276, { result: '226' }), { 结果: 226 }));
      o.push(S('验算：<b>226 + 276 = 502</b> ✓。减法是加法的逆运算，这个「互逆」思想以后会变成反函数。',
        vertical(226, 276, { result: '502' }), { 验算: '通过' }));
      return o;
    },
    notes: [
      '<p>借位不是「变魔术」：把 1 个百拆成 10 个十，总数一点没变，只是换了零钱。</p>',
      '<p>中间有 0 时要连续借；每一步都在做「拆开一个高单位 = 十个低单位」。</p>',
      '<p>初中移项（等式两边同减）、配方法（加上再减去同一个数）、甲种本的反函数与逆映射，都是「保持总量不变的变形」。</p>'
    ],
    example: { q: '计算 1000 − 348', steps: ['连续借位：1000 = 999 + 1 的思路更稳妥', '1000 − 348 = 652'], a: '652' },
    quiz: [
      { q: '计算 604 − 279 = ?', options: ['325', '335', '425', '375'], answer: 0, explain: '连续借位后 14−9=5，9−7=2，5−2=3，得 325。' },
      { q: '「借一当十」之后总数变了吗？', options: ['变大了', '变小了', '没变，只是换了单位', '不确定'], answer: 2, explain: '1 个十 = 10 个一，只是换零钱，值不变。' }
    ]
  });

  T({
    id: 'p-mul', unit: 'p-num', title: '乘法竖式与分配律', subtitle: '把两位数乘法拆成几次一位数乘法',
    goal: '理解部分积为什么错位写，从而真正理解分配律',
    why: '分配律是整式乘法、乘法公式 (a+b)²、因式分解、二项式定理的唯一底层规则。',
    view: 'steps', minutes: 10, star: true, prereq: ['p-add'],
    demo: function () {
      var o = [];
      o.push(S('计算 <b>23 × 14</b>。先把 14 拆成 <b>4 + 10</b>，分别相乘再相加。',
        { lines: [row('23 × 14 = 23 × (4 + 10)'), row('= 23×4 + 23×10', 'is-on')], caption: '这就是分配律' }));
      o.push(S('第一层部分积：<b>23 × 4 = 92</b>。',
        { lines: [row('   23'), row('×  14', 'is-dim'), L([C(' '), C(' '), C(' '), C(' ')], 'is-rule'), row('   92', 'is-hi')], caption: '23 × 4' }));
      o.push(S('第二层部分积：<b>23 × 10 = 230</b>。因为乘的是「十位上的 1」，所以要<b>左移一位</b>。',
        { lines: [row('   23'), row('×  14', 'is-dim'), L([C(' '), C(' '), C(' '), C(' ')], 'is-rule'), row('   92'), row('  230', 'is-hi')], caption: '错位写 = 后面补一个 0' }));
      o.push(S('两层相加：<b>92 + 230 = 322</b>。',
        { lines: [row('   92'), row('+ 230'), L([C(' '), C(' '), C(' '), C(' ')], 'is-rule'), row('  322', 'is-done')], caption: '合并部分积' }));
      o.push(S('用面积看更清楚：<b>(20+3)(10+4)</b> 展开成四块，总和不变。',
        { view: 'grid', cols: 2, rows: 2, cellW: 96, cells: [
          { v: '20×10 = 200', cls: 'is-on' }, { v: '3×10 = 30', cls: 'is-on' },
          { v: '20×4 = 80', cls: 'is-on' }, { v: '3×4 = 12', cls: 'is-on' }],
          caption: '200 + 30 + 80 + 12 = 322' }));
      return o;
    },
    notes: [
      '<p>乘法竖式里「错位写」经常只被当成规矩，其实它是 <code>×10</code>：第二层乘的是十位。</p>',
      '<p>把两个因数各自拆成整十和个位，就得到四个小矩形 —— 面积模型让分配律看得见。</p>',
      '<p>同样的图把 20、3 换成 <code>a、b</code>，10、4 换成 <code>c、d</code>，就是 <code>(a+b)(c+d)=ac+ad+bc+ad</code>；甲种本代数3 的二项式定理也是它的高次版本。</p>'
    ],
    example: { q: '用分配律口算 32 × 21', steps: ['32 × 21 = 32 × (20 + 1)', '= 640 + 32 = 672'], a: '672' },
    quiz: [
      { q: '23 × 14 的第二层部分积为什么写 230 而不是 23？', options: ['为了对齐好看', '因为乘的是十位上的 1，表示 ×10', '因为 14 有两位', '写错了'], answer: 1, explain: '十位上的 1 代表 10，所以 23×10 = 230。' },
      { q: '(a + b) × c 等于？', options: ['ac + b', 'a + bc', 'ac + bc', 'abc'], answer: 2, explain: '分配律：c 要分别乘 a 和 b。' }
    ]
  });

  T({
    id: 'p-div', unit: 'p-num', title: '除法竖式与余数', subtitle: '除法就是反复减去同一个数',
    goal: '理解商和余数的含义，知道「余数必须比除数小」',
    why: '辗转相除法、带余除法、多项式除法、同余，全都建立在这一步。',
    view: 'steps', minutes: 9, prereq: ['p-mul', 'p-sub'],
    demo: function () {
      var o = [];
      o.push(S('计算 <b>84 ÷ 5</b>：问「84 里面最多有几个 5」。',
        { lines: [row('84 ÷ 5 = ?')], caption: '除法的含义是「包含几个」' }));
      o.push(S('先减去 <b>10 个 5</b>（也就是 50）：84 − 50 = 34。',
        { lines: [row('84 − 5×10 = 34', 'is-hi'), row('已经分掉 10 个 5')], caption: '第一步估商' }));
      o.push(S('再减去 <b>6 个 5</b>（也就是 30）：34 − 30 = 4。',
        { lines: [row('84 − 5×10 = 34'), row('34 − 5×6  = 4', 'is-hi'), row('又分掉 6 个 5')], caption: '第二步估商' }));
      o.push(S('剩下 <b>4</b>，比 5 小，不能再分了。一共分出 <b>10 + 6 = 16</b> 个 5。',
        { lines: [row('商 = 16'), row('余数 = 4', 'is-hi'), row('4 < 5 ✓', 'is-on')], caption: '余数必须小于除数' }));
      o.push(S('写成带余除法：<b>84 = 5 × 16 + 4</b>。验算：5×16+4 = 84 ✓。',
        { lines: [row('84 = 5 × 16 + 4', 'is-done'), row('被除数 = 除数 × 商 + 余数', 'is-dim')], caption: '这是甲种本「多项式除法」的原型' }));
      return o;
    },
    notes: [
      '<p>除法不是新运算，它是「连续减同一个数」的简便记法，也是乘法的逆运算。</p>',
      '<p>余数 r 必须满足 <code>0 ≤ r &lt; 除数</code>；否则说明商还能再大一点。</p>',
      '<p>「被除数 = 除数 × 商 + 余数」在初中是辗转相除法求最大公因数，在甲种本代数3 会原封不动变成多项式的带余除法。</p>'
    ],
    example: { q: '计算 100 ÷ 7，写出带余形式', steps: ['7 × 14 = 98，100 − 98 = 2', '2 < 7，停止'], a: '100 = 7 × 14 + 2，商 14 余 2' },
    quiz: [
      { q: '47 ÷ 6 的余数是？', options: ['3', '5', '6', '7'], answer: 1, explain: '6×7=42，47−42=5，且 5 < 6。' },
      { q: '下面哪个带余式是正确的？', options: ['23 = 4×5 + 3', '23 = 4×6 + 1', '23 = 4×4 + 7', '23 = 5×5 + 2'], answer: 0, explain: '4×5+3=23 且余数 3 < 4 才合法；C 的余数 7 大于除数，不合法。' }
    ]
  });

  T({
    id: 'p-mix', unit: 'p-num', title: '四则混合与运算律', subtitle: '先乘除后加减，本质是「先算成同一个单位」',
    goal: '熟练运算顺序，理解交换律、结合律、分配律在简算中的作用',
    why: '甲种本所有代数变形的合法性都来自这三条运算律；求导、积分的线性性也是分配律。',
    view: 'steps', minutes: 9, star: true, prereq: ['p-mul'],
    demo: function () {
      var o = [];
      o.push(S('算式 <b>3 + 4 × 2</b> 先算哪一步？', { lines: [row('3 + 4 × 2 = ?')], caption: '两种算法会给出 11 或 14' }));
      o.push(S('先算乘法：<b>4 × 2 = 8</b>。因为 4×2 表示「2 个 4 合起来」，是一个整体。',
        { lines: [L([C('3'), C('+', 'is-dim'), C('4 × 2', 'is-hi')]), L([C('= 3 + 8')])], caption: '先乘除' }));
      o.push(S('再算加法：<b>3 + 8 = 11</b>。', { lines: [L([C('3 + 8', 'is-hi')]), L([C('= 11', 'is-done')])], caption: '后加减' }));
      o.push(S('如果要先算加法，必须加括号：<b>(3+4)×2 = 14</b>。括号是改变顺序的唯一手段。',
        { lines: [L([C('(3 + 4)', 'is-hi'), C('× 2')]), L([C('= 7 × 2 = 14', 'is-done')])], caption: '括号优先' }));
      o.push(S('简算 <b>25 × 17 × 4</b>：用交换律先算 25×4=100。',
        { lines: [row('25 × 17 × 4'), row('= 25 × 4 × 17', 'is-hi'), row('= 100 × 17 = 1700', 'is-done')], caption: '交换律 + 结合律' }));
      o.push(S('三条运算律：<b>a+b=b+a</b>、<b>(a+b)+c=a+(b+c)</b>、<b>a(b+c)=ab+ac</b>。',
        { lines: [row('交换律    a + b = b + a', 'is-on'), row('结合律    (a+b)+c = a+(b+c)', 'is-on'), row('分配律    a(b+c) = ab + ac', 'is-on')], caption: '代数的全部合法性来源' }));
      return o;
    },
    notes: [
      '<p>优先级不是「老师规定」：乘法是同数连加的缩写，先把它算成一个数，才谈得上和别的数相加。</p>',
      '<p>交换律、结合律、分配律是简算的工具，也是判断两个代数式是否恒等的依据。</p>',
      '<p>初中整式运算、因式分解，甲种本二项式定理、行列式展开，本质上只是这三条律反复使用。</p>'
    ],
    example: { q: '简算 8 × 37 + 8 × 63', steps: ['提取公因数 8：= 8 × (37 + 63)', '= 8 × 100'], a: '800（分配律逆用，也就是因式分解的雏形）' },
    quiz: [
      { q: '计算 6 + 3 × 4 = ?', options: ['36', '18', '24', '13'], answer: 1, explain: '先乘：3×4=12，再 6+12=18。' },
      { q: '8 × 37 + 8 × 63 最简便的算法是？', options: ['先算两个乘法', '8 × (37+63)', '37 × (8+63)', '(8+37) × 63'], answer: 1, explain: '逆用分配律提取 8，得 8×100 = 800。' }
    ]
  });

  /* ============ 二、分数与小数 ============ */
  T({
    id: 'p-frac-mean', unit: 'p-frac', title: '分数的意义', subtitle: '把一个整体平均分，取其中几份',
    goal: '理解分母、分子、整体「1」，认识等值分数',
    why: '分式、有理数、概率、导数中的差商，都要能自由切换「整体 1」是谁。',
    view: 'fraction', minutes: 8,
    demo: function () {
      var o = [];
      o.push(S('把一个长方形看作<b>整体 1</b>，平均分成 2 份，取 1 份，就是 <b>1/2</b>。',
        { rows: [{ label: '1/2', n: 1, d: 2, cls: 'is-hi' }], caption: '分母 2 = 平均分成几份；分子 1 = 取几份' }));
      o.push(S('平均分成 4 份取 2 份，是 <b>2/4</b>；涂色部分和 1/2 <b>一样大</b>。',
        { rows: [{ label: '1/2', n: 1, d: 2 }, { label: '2/4', n: 2, d: 4, cls: 'is-hi' }], caption: '等值分数' }));
      o.push(S('再看 3/6、4/8，全都一样大。',
        { rows: [{ label: '1/2', n: 1, d: 2 }, { label: '3/6', n: 3, d: 6 }, { label: '4/8', n: 4, d: 8, cls: 'is-hi' }], caption: '分子分母同乘一个数，值不变' }));
      o.push(S('关键：<b>分子分母同时乘或除以同一个不为 0 的数，分数大小不变</b>。这就是约分和通分的全部依据。',
        { rows: [{ label: '2/3', n: 2, d: 3, cls: 'is-done' }, { label: '4/6', n: 4, d: 6, cls: 'is-done' }, { label: '6/9', n: 6, d: 9, cls: 'is-done' }], caption: '2/3 = 4/6 = 6/9' }));
      return o;
    },
    notes: [
      '<p>分数先要问「整体是谁」。同一个 1/2，半个披萨和半个操场完全不同。</p>',
      '<p>分母说「分成几份」，分子说「拿几份」；分母不能为 0，因为不能分成 0 份。</p>',
      '<p>「同乘不变」在初中就是分式的基本性质，在甲种本换底公式 <code>logₐb = log꜀b / log꜀a</code>、求导通分时天天用。</p>'
    ],
    example: { q: '把 3/5 写成分母是 20 的等值分数', steps: ['分母 5 → 20 需要乘 4', '分子也要乘 4：3×4 = 12'], a: '12/20' },
    quiz: [
      { q: '与 3/4 相等的分数是？', options: ['6/12', '9/12', '4/3', '3/8'], answer: 1, explain: '3/4 分子分母同乘 3 得 9/12。' },
      { q: '分母表示什么？', options: ['取了几份', '平均分成几份', '剩下的份数', '整体大小'], answer: 1, explain: '分母是把整体平均分成的份数。' }
    ]
  });

  T({
    id: 'p-frac-reduce', unit: 'p-frac', title: '约分与通分', subtitle: '把分数化到最简，把不同分母变相同',
    goal: '会用最大公因数约分、最小公倍数通分',
    why: '★ 甲种本最吃这一项：分式化简、换底公式、求导后的通分、圆锥曲线联立后的代数整理。',
    view: 'fraction', minutes: 12, star: true, prereq: ['p-frac-mean', 'p-factor'],
    demo: function () {
      var o = [];
      o.push(S('约分 <b>12/18</b>：先找 12 和 18 的最大公因数。',
        { rows: [{ label: '12/18', n: 12, d: 18, cls: 'is-hi' }], caption: '12 = 2×2×3，18 = 2×3×3 → 公因数 2×3 = 6' }));
      o.push(S('分子分母同除以 <b>6</b>：12÷6=2，18÷6=3，得到 <b>2/3</b>。',
        { rows: [{ label: '12/18', n: 12, d: 18 }, { label: '2/3', n: 2, d: 3, cls: 'is-done' }], caption: '2/3 已是最简分数' }));
      o.push(S('通分 <b>1/2 + 1/3</b>：分母不同，份的大小不一样，不能直接加。',
        { rows: [{ label: '1/2', n: 1, d: 2 }, { label: '1/3', n: 1, d: 3 }], caption: '2 和 3 的最小公倍数是 6' }));
      o.push(S('都化成分母 6：<b>1/2 = 3/6</b>，<b>1/3 = 2/6</b>。',
        { rows: [{ label: '3/6', n: 3, d: 6, cls: 'is-hi' }, { label: '2/6', n: 2, d: 6, cls: 'is-hi' }], caption: '现在每一份一样大了' }));
      o.push(S('分子相加：<b>3/6 + 2/6 = 5/6</b>。分母不变，因为「单位」没变。',
        { rows: [{ label: '3/6 + 2/6', n: 3, d: 6 }, { label: '5/6', n: 5, d: 6, cls: 'is-done' }], caption: '分母是单位，只把个数相加' }));
      return o;
    },
    notes: [
      '<p>约分 = 把份合并变大（同除）；通分 = 把份切细变小（同乘）。两个动作都靠「同乘同除不变」。</p>',
      '<p>通分找最小公倍数；约分找最大公因数。二者都可以用质因数分解得到。</p>',
      '<p>初中的分式加减、甲种本导数 <code>(u/v)′</code> 的推导、换底公式，出错几乎全在通分这一步。这是最值得练熟的一条前置。</p>'
    ],
    example: { q: '计算 2/3 + 1/4', steps: ['3 和 4 的最小公倍数是 12', '2/3 = 8/12，1/4 = 3/12', '8/12 + 3/12 = 11/12'], a: '11/12' },
    quiz: [
      { q: '18/24 约成最简分数是？', options: ['9/12', '6/8', '3/4', '2/3'], answer: 2, explain: '最大公因数 6，18÷6=3，24÷6=4。' },
      { q: '计算 1/2 + 1/3 = ?', options: ['2/5', '1/6', '5/6', '1'], answer: 2, explain: '通分为 3/6 + 2/6 = 5/6。' }
    ]
  });

  T({
    id: 'p-frac-ops', unit: 'p-frac', title: '分数四则运算', subtitle: '加减要通分，乘除不必',
    goal: '掌握分数加减乘除，理解「除以一个分数等于乘它的倒数」',
    why: '分式方程、有理式化简、导数商法则中的「倒数」都从这里来。',
    view: 'steps', minutes: 10, prereq: ['p-frac-reduce'],
    demo: function () {
      var o = [];
      o.push(S('<b>加减</b>要通分：<code>1/2 + 1/3 = 3/6 + 2/6 = 5/6</code>。',
        { lines: [row('1/2 + 1/3', 'is-hi'), row('= 3/6 + 2/6'), row('= 5/6', 'is-done')], caption: '单位统一才能相加' }));
      o.push(S('<b>乘法</b>直接分子乘分子、分母乘分母：<code>2/3 × 3/5 = 6/15 = 2/5</code>。',
        { lines: [row('2/3 × 3/5', 'is-hi'), row('= (2×3)/(3×5) = 6/15'), row('= 2/5', 'is-done')], caption: '「求一个数的几分之几」用乘法' }));
      o.push(S('<b>除法</b>：问 2/3 里有几个 1/6，答案是 4 个。',
        { lines: [row('2/3 ÷ 1/6 = ?'), row('2/3 = 4/6'), row('4/6 ÷ 1/6 = 4', 'is-done')], caption: '包含除' }));
      o.push(S('所以 <b>除以一个分数 = 乘它的倒数</b>：<code>2/3 ÷ 1/6 = 2/3 × 6 = 4</code>。',
        { lines: [row('a/b ÷ c/d = a/b × d/c', 'is-on'), row('倒数是把分子分母调换', 'is-dim')], caption: '这个规则在代数里天天用' }));
      return o;
    },
    notes: [
      '<p>加减法要「单位相同」所以通分；乘除法是「求几分之几」和「包含几个」，不需要同分母。</p>',
      '<p>除以 <code>c/d</code> 等于乘 <code>d/c</code>，前提是所有分母都不为 0。</p>',
      '<p>初中解分式方程、甲种本求 <code>1/x</code> 的导数、复数除法（乘共轭），都是「乘倒数」的变形。</p>'
    ],
    example: { q: '计算 3/4 ÷ 3/8', steps: ['= 3/4 × 8/3', '= 24/12'], a: '2' },
    quiz: [
      { q: '计算 2/5 × 3/4 = ?', options: ['5/9', '6/20 = 3/10', '8/15', '1/2'], answer: 1, explain: '分子乘分子 6，分母乘分母 20，约分成 3/10。' },
      { q: '计算 3/4 ÷ 1/2 = ?', options: ['3/8', '3/2', '2/3', '3'], answer: 1, explain: '= 3/4 × 2 = 3/2。' }
    ]
  });

  T({
    id: 'p-decimal', unit: 'p-frac', title: '小数、百分数与互化', subtitle: '小数是分母为 10、100 的另一种写法',
    goal: '熟练三者互化，理解百分数是「以 100 为整体」',
    why: '概率、增长率、对数换底后的近似计算、误差估计都要用。',
    view: 'grid', minutes: 9, prereq: ['p-frac-mean'],
    demo: function () {
      function g(n, cls) {
        var cells = [];
        for (var i = 0; i < 100; i++) cells.push({ v: '', cls: i < n ? cls : 'is-pending' });
        return { cols: 10, rows: 10, cellW: 22, cells: cells };
      }
      var o = [];
      o.push(S('把正方形看作 <b>1</b>，平均分成 100 小格，每格是 <b>0.01</b>。', g(0), { 每格: '0.01' }));
      o.push(S('涂 25 格，就是 <b>25/100</b>。', g(25, 'is-on'), { 涂色: 25 }));
      o.push(S('<b>25/100 = 0.25 = 25%</b>：同一个量的三种写法。',
        { cols: 1, rows: 3, cellW: 210, cells: [
          { v: '25/100  ← 分数', cls: 'is-on' }, { v: '0.25   ← 小数', cls: 'is-hi' }, { v: '25%   ← 百分数', cls: 'is-done' }] }));
      o.push(S('小数化分数看位数：0.3 = 3/10，0.25 = 25/100，0.125 = 125/1000。',
        { cols: 1, rows: 3, cellW: 230, cells: [
          { v: '0.3 = 3/10', cls: 'is-on' }, { v: '0.25 = 25/100 = 1/4', cls: 'is-on' }, { v: '0.125 = 1/8', cls: 'is-on' }] }));
      o.push(S('百分数用于「部分占整体」：全班 40 人，10 人戴眼镜 → <b>10/40 = 25%</b>。',
        { cols: 1, rows: 2, cellW: 240, cells: [
          { v: '10 ÷ 40 = 0.25', cls: 'is-hi' }, { v: '0.25 × 100% = 25%', cls: 'is-done' }] }));
      return o;
    },
    notes: [
      '<p>小数点后第几位，就对应分母 10 的几次方；小数其实是「不写分母的分数」。</p>',
      '<p>百分数把整体固定成 100，方便比较不同总量的比例。</p>',
      '<p>甲种本代数3 的概率、附录「近似计算的法则」、微积分里的误差估计，都默认这三者能瞬间互换。</p>'
    ],
    example: { q: '把 0.375 化成分数并化成百分数', steps: ['0.375 = 375/1000 = 3/8', '0.375 × 100% = 37.5%'], a: '3/8 = 37.5%' },
    quiz: [
      { q: '0.6 化成分数是？', options: ['6/100', '3/5', '1/6', '6/5'], answer: 1, explain: '0.6 = 6/10 = 3/5。' },
      { q: '某班 50 人，15 人参加社团，占百分之几？', options: ['15%', '25%', '30%', '35%'], answer: 2, explain: '15/50 = 0.3 = 30%。' }
    ]
  });

  T({
    id: 'p-approx', unit: 'p-frac', title: '近似数与四舍五入', subtitle: '精确到哪一位，就看下一位',
    goal: '会按精度取近似值，理解误差范围',
    why: '★ 甲种本第一册附录「近似计算的法则」原本计划在初中教；微积分的极限与误差也靠这个直觉。',
    view: 'steps', minutes: 9, star: true, prereq: ['p-decimal'],
    demo: function () {
      var o = [];
      o.push(S('把 <b>3.146</b> 保留两位小数。要保留到百分位（4），就看它右边一位。',
        { lines: [L([C('3'), C('.'), C('1'), C('4', 'is-hi'), C('6', 'is-warn')]), L([C('个'), C(' '), C('十分'), C('百分'), C('千分')], '', '')], caption: '保留位 = 4，判断位 = 6' }));
      o.push(S('判断位是 <b>6 ≥ 5</b>，向保留位进 1：<b>3.15</b>。',
        { lines: [row('3.146 → 3.15', 'is-done'), row('误差 < 0.005', 'is-dim')], caption: '四舍五入' }));
      o.push(S('若判断位是 4：3.144 → <b>3.14</b>，直接舍去。',
        { lines: [row('3.144 → 3.14', 'is-done'), row('4 < 5，舍去', 'is-dim')], caption: '四舍' }));
      o.push(S('「保留两位小数 3.15」的真实值范围是 <b>3.145 ≤ x &lt; 3.155</b>。',
        { lines: [row('下界 3.145  ✓ 入上来'), row('上界 3.155  ✗ 已进位'), row('误差不超过半个最小单位', 'is-on')], caption: '近似数的误差界' }));
      o.push(S('有效数字：0.00320 有 <b>3 位</b>有效数字（3、2、0），前面的 0 只定位，不算。',
        { lines: [row('0.00320'), row('有效数字：3, 2, 0', 'is-done')], caption: '末尾的 0 表示精度，不能随便删' }));
      return o;
    },
    notes: [
      '<p>取近似不是「随便删几位」，而是找一个离真值最近、位数更少的数。</p>',
      '<p>误差不超过保留位最小单位的一半；这就是「精确到 0.01」的含义。</p>',
      '<p>甲种本微积分初步第一章讲极限，用的正是「要多接近有多接近」；附录的近似计算法则讲有效数字与误差传播。</p>'
    ],
    example: { q: '把 2.785 保留一位小数', steps: ['保留到十分位 7，看百分位 8', '8 ≥ 5，进 1'], a: '2.8' },
    quiz: [
      { q: '5.274 保留两位小数是？', options: ['5.27', '5.28', '5.3', '5.20'], answer: 0, explain: '第三位是 4，舍去，得 5.27。' },
      { q: '「精确到 0.1」的近似数，误差最大约为？', options: ['0.1', '0.05', '0.01', '0.5'], answer: 1, explain: '不超过最小单位的一半，即 0.05。' }
    ]
  });

  /* ============ 三、比与关系 ============ */
  T({
    id: 'p-ratio', unit: 'p-rel', title: '比与正反比例', subtitle: '两个量一起变，关系可以保持不变',
    goal: '理解比的意义、化简比、正反比例的图像直觉',
    why: '★ 这是「函数」概念在小学的第一次出现：斜率 k、幂函数 y=x⁻¹、相似比都从这里长出来。',
    view: 'bars', minutes: 10, star: true, prereq: ['p-frac-reduce'],
    demo: function () {
      var o = [];
      o.push(S('调一杯果汁：2 杯原汁配 3 杯水，<b>原汁 : 水 = 2 : 3</b>。',
        { values: [2, 3], labels: ['原汁', '水'], marks: {}, caption: '比描述的是「相对份数」，不是具体数量' }));
      o.push(S('按同样配方做两倍：4 杯原汁配 6 杯水，味道<b>不变</b>。',
        { values: [4, 6], labels: ['原汁', '水'], marks: { hi: [0, 1] }, caption: '2:3 = 4:6 = 6:9' }));
      o.push(S('比的前项后项同乘一个数，比值不变 —— 就是分数的「同乘不变」。',
        { values: [6, 9], labels: ['原汁', '水'], marks: { done: [0, 1] }, caption: '6:9 化简回 2:3' }));
      o.push(S('<b>正比例</b>：单价 3 元，买 x 个付 y 元，<b>y = 3x</b>。x 变 2 倍，y 也变 2 倍。',
        { values: [3, 6, 9, 12], labels: ['x=1', 'x=2', 'x=3', 'x=4'], marks: { hi: [1] }, caption: '比值 y/x = 3 恒定' }));
      o.push(S('<b>反比例</b>：路程 12 固定，速度 × 时间 = 12，<b>xy = 12</b>，一个变大另一个变小。',
        { values: [12, 6, 4, 3], labels: ['v=1', 'v=2', 'v=3', 'v=4'], marks: { done: [0, 1, 2, 3] }, caption: '乘积恒定 → 初中反比例函数 y = k/x' }));
      return o;
    },
    notes: [
      '<p>比和分数是同一件事的两种说法：2:3 就是 2/3，化简比就是约分。</p>',
      '<p>正比例 <code>y/x = k</code>（商一定），反比例 <code>xy = k</code>（积一定）。判断标准是「什么量保持不变」。</p>',
      '<p>初中一次函数的斜率、甲种本幂函数里的 <code>y = x⁻¹</code>、解析几何里直线的倾斜程度，都是「比值恒定」。</p>'
    ],
    example: { q: '判断：长方形面积固定为 24，长 a 与宽 b 成什么比例？', steps: ['a × b = 24，乘积恒定', 'a 变大时 b 必须变小'], a: '反比例：b = 24/a' },
    quiz: [
      { q: '把 12 : 18 化成最简整数比', options: ['2:3', '3:2', '6:9', '4:6'], answer: 0, explain: '同除以 6 得 2:3。' },
      { q: '下面哪个是反比例关系？', options: ['y = 5x', 'y = x + 5', 'xy = 20', 'y = x/5'], answer: 2, explain: 'xy 为常数即乘积恒定，是反比例。' }
    ]
  });

  T({
    id: 'p-letter', unit: 'p-rel', title: '用字母表示数与简易方程', subtitle: '从算术走向代数的那道门槛',
    goal: '能用 x 表示未知量，会用等式性质解 ax+b=c',
    why: '★ 甲种本第一页就是「集合与映射」，不会用字母表示一般规律，整本代数都读不下去。',
    view: 'shapes', minutes: 12, star: true, prereq: ['p-mix'],
    demo: function () {
      function balance(stage) {
        var items = [
          { k: 'line', x1: 140, y1: 150, x2: 500, y2: 150, cls: stage >= 2 ? 'is-hi' : '' },
          { k: 'poly', pts: [[320, 155], [295, 205], [345, 205]], cls: '' },
          { k: 'line', x1: 130, y1: 120, x2: 210, y2: 150, cls: '' },
          { k: 'line', x1: 430, y1: 120, x2: 510, y2: 150, cls: '' },
          { k: 'line', x1: 170, y1: 120, x2: 170, y2: 150, cls: '' },
          { k: 'line', x1: 470, y1: 120, x2: 470, y2: 150, cls: '' },
          { k: 'rect', x: 100, y: 112, w: 140, h: 8, rx: 3, cls: '' },
          { k: 'rect', x: 400, y: 112, w: 140, h: 8, rx: 3, cls: '' }
        ];
        var left = stage === 0 ? [3, 4] : stage === 1 ? [3] : [3];
        left.forEach(function (n, i) {
          items.push({ k: 'rect', x: 116 + i * 34, y: 82, w: 28, h: 28, rx: 4, cls: 'is-on', label: String(n), labelY: 101 });
        });
        if (stage <= 1) items.push({ k: 'rect', x: 184, y: 82, w: 28, h: 28, rx: 4, cls: 'is-hi', label: 'x', labelY: 101 });
        var right = stage === 0 ? [10] : stage === 1 ? [6] : [6];
        right.forEach(function (n, i) {
          items.push({ k: 'rect', x: 420 + i * 34, y: 82, w: 28, h: 28, rx: 4, cls: 'is-done', label: String(n), labelY: 101 });
        });
        if (stage === 2) items.push({ k: 'rect', x: 184, y: 82, w: 28, h: 28, rx: 4, cls: 'is-hi', label: '2', labelY: 101 });
        items.push({ k: 'text', x: 320, y: 40, t: stage === 0 ? '3x + 4 = 10' : stage === 1 ? '3x = 6' : 'x = 2', cls: '' });
        return { items: items, caption: '天平两边始终保持平衡' };
      }
      var o = [];
      o.push(S('天平：左边 3 个 x 加 4，右边 10，写成 <b>3x + 4 = 10</b>。', balance(0)));
      o.push(S('两边<b>同时拿走 4</b>，仍然平衡：<b>3x = 6</b>。', balance(1)));
      o.push(S('两边<b>同时分成 3 份</b>，取一份：<b>x = 2</b>。', balance(2)));
      o.push(S('等式性质：两边同加同减、同乘同除（除数不为 0）同一个数，等式仍成立。',
        { items: [
          { k: 'rect', x: 90, y: 60, w: 460, h: 44, rx: 8, cls: 'is-on' },
          { k: 'text', x: 320, y: 88, t: 'a = b  ⟹  a ± c = b ± c', cls: '' },
          { k: 'rect', x: 90, y: 120, w: 460, h: 44, rx: 8, cls: 'is-hi' },
          { k: 'text', x: 320, y: 148, t: 'a = b  ⟹  ac = bc，a/c = b/c (c≠0)', cls: '' },
          { k: 'text', x: 320, y: 205, t: '这一条，就是甲种本所有方程变形的依据', cls: '' }
        ], caption: '等式的基本性质' }));
      return o;
    },
    notes: [
      '<p>用字母不是为了把题变难，而是为了<b>一次说清所有同类问题</b>：3x+4=10 代表一整类题。</p>',
      '<p>解方程的每一步都是「对等式两边做同一件事」，天平保持平衡就是等式的直观模型。</p>',
      '<p>移项、合并同类项、去分母，全是等式性质；甲种本解指数方程、三角方程、行列式方程组时，合法性仍来自这里。</p>'
    ],
    example: { q: '解方程 5x − 7 = 18', steps: ['两边加 7：5x = 25', '两边除以 5：x = 5'], a: 'x = 5' },
    quiz: [
      { q: '解方程 2x + 5 = 17，x = ?', options: ['4', '6', '11', '12'], answer: 1, explain: '2x = 12，x = 6。' },
      { q: '等式两边同除以 c，需要满足什么？', options: ['c > 0', 'c ≠ 0', 'c 是整数', 'c = 1'], answer: 1, explain: '0 不能作除数，只要求 c ≠ 0。' }
    ]
  });

  T({
    id: 'p-pattern', unit: 'p-rel', title: '找规律与数列', subtitle: '先看相邻两项差多少，再看差是否也成规律',
    goal: '会观察数列的差分规律并写出通项的朴素形式',
    why: '甲种本代数2 的「数列与数学归纳法」从这里起步；微积分的差分→导数也是同一思路。',
    view: 'bars', minutes: 9, prereq: ['p-letter'],
    demo: function () {
      var o = [];
      o.push(S('数列 <b>2, 4, 6, 8, ?</b>：先看相邻两项的差。',
        { values: [2, 4, 6, 8, 0], labels: ['第1项', '第2项', '第3项', '第4项', '?'], marks: { hi: [4] }, caption: '每次 +2' }));
      o.push(S('差都是 2，所以下一项是 <b>10</b>。这类叫等差数列。',
        { values: [2, 4, 6, 8, 10], labels: ['n=1', 'n=2', 'n=3', 'n=4', 'n=5'], marks: { done: [4] }, caption: '公差 d = 2' }));
      o.push(S('第 n 项怎么算？<b>2n</b>：第 1 项 2×1，第 5 项 2×5。',
        { values: [2, 4, 6, 8, 10], labels: ['2×1', '2×2', '2×3', '2×4', '2×5'], marks: { hi: [2] }, caption: '用字母表示一般规律' }));
      o.push(S('再看 <b>1, 4, 9, 16, ?</b>：差是 3、5、7，差本身也在变 —— 它们其实是 <b>n²</b>。',
        { values: [1, 4, 9, 16, 25], labels: ['1²', '2²', '3²', '4²', '5²'], marks: { done: [4] }, caption: '看不出等差时，试试平方、倍数' }));
      return o;
    },
    notes: [
      '<p>找规律的标准动作：先算一阶差；差不等再看二阶差、比值、平方数。</p>',
      '<p>把「第 n 项」写成含 n 的式子，是从算术跨到代数的关键一步。</p>',
      '<p>甲种本代数2 会给出通项公式、递推公式和数学归纳法；微积分里的「差分商」也是先看相邻两项之差。</p>'
    ],
    example: { q: '数列 3, 7, 11, 15, ? 的第 n 项？', steps: ['相邻差都是 4', '第 n 项 = 3 + 4(n−1) = 4n − 1'], a: '第 5 项 19，通项 4n − 1' },
    quiz: [
      { q: '数列 5, 8, 11, 14 的下一项是？', options: ['15', '16', '17', '18'], answer: 2, explain: '公差 3，14 + 3 = 17。' },
      { q: '数列 1, 4, 9, 16 的第 6 项是？', options: ['25', '30', '36', '24'], answer: 2, explain: 'n²，6² = 36。' }
    ]
  });

  T({
    id: 'p-unit', unit: 'p-rel', title: '单位换算与量纲', subtitle: '长度 ×10，面积 ×100，体积 ×1000',
    goal: '理解换算中「平方」「立方」带来的倍数差异',
    why: '解析几何的距离公式、立体几何的体积、微积分积分的单位都要求量纲一致。',
    view: 'grid', minutes: 8, prereq: ['p-mul'],
    demo: function () {
      var o = [];
      o.push(S('长度：1 米 = 10 分米 = 100 厘米。',
        { cols: 1, rows: 3, cellW: 240, cells: [
          { v: '1 m = 10 dm', cls: 'is-on' }, { v: '1 dm = 10 cm', cls: 'is-on' }, { v: '1 m = 100 cm', cls: 'is-hi' }] }));
      o.push(S('面积要<b>平方</b>：边长 1 m 的正方形 = 边长 100 cm 的正方形。',
        { cols: 1, rows: 2, cellW: 260, cells: [
          { v: '1 m² = (100 cm)²', cls: 'is-hi' }, { v: '= 10000 cm²', cls: 'is-done' }], caption: '不是 100，是 100×100' }));
      o.push(S('用 10×10 的格子看：1 个大格若边长 10 cm，整个面积就是 100 个小格。',
        (function () { var c = []; for (var i = 0; i < 100; i++) c.push({ v: '', cls: i < 25 ? 'is-on' : 'is-pending' }); return { cols: 10, rows: 10, cellW: 22, cells: c, caption: '25/100 = 1/4 个大正方形' }; })()));
      o.push(S('体积要<b>立方</b>：1 m³ = 100³ cm³ = 1 000 000 cm³。',
        { cols: 1, rows: 3, cellW: 250, cells: [
          { v: '长度：×10', cls: 'is-on' }, { v: '面积：×10² = ×100', cls: 'is-on' }, { v: '体积：×10³ = ×1000', cls: 'is-done' }] }));
      return o;
    },
    notes: [
      '<p>换单位时数字和单位一起换：<code>1 m = 100 cm</code>，那么 <code>1 m² = (100 cm)²</code>。</p>',
      '<p>最容易错的是把面积当成 ×10、体积当成 ×100；记住「几次方就乘几次」。</p>',
      '<p>立体几何的体积公式、微积分里积分结果的量纲（面积/体积），都靠这个直觉检查答案是否离谱。</p>'
    ],
    example: { q: '2.5 m² 等于多少 cm²？', steps: ['1 m² = 10000 cm²', '2.5 × 10000'], a: '25000 cm²' },
    quiz: [
      { q: '3 m² 等于多少 cm²？', options: ['300', '3000', '30000', '30'], answer: 2, explain: '1 m² = 10000 cm²，3 × 10000 = 30000。' },
      { q: '1 L 等于多少 mL？', options: ['10', '100', '1000', '10000'], answer: 2, explain: '1 L = 1000 mL = 1000 cm³。' }
    ]
  });

  /* ============ 四、图形与度量 ============ */
  T({
    id: 'p-angle', unit: 'p-geo', title: '角的度量与分类', subtitle: '角是「两条射线张开的程度」',
    goal: '认识锐角、直角、钝角、平角、周角，会用量角器的直觉估计',
    why: '★ 甲种本代数1 第二章「任意角的三角函数」第一步就是把角从 0°~360° 推广到任意角与弧度制。',
    view: 'shapes', minutes: 8, star: true,
    demo: function () {
      function angle(deg, label, cls) {
        var r = 100, rad = deg * Math.PI / 180;
        return { items: [
          { k: 'line', x1: 320, y1: 190, x2: 520, y2: 190, cls: '' },
          { k: 'line', x1: 320, y1: 190, x2: 320 + r * Math.cos(rad), y2: 190 - r * Math.sin(rad), cls: 'is-hi' },
          { k: 'circle', x: 320, y: 190, r: 4, cls: 'is-on' },
          { k: 'poly', pts: [[320, 190], [320 + r, 190], [320 + r * Math.cos(rad), 190 - r * Math.sin(rad)]], cls: 'is-on' },
          { k: 'text', x: 320, y: 50, t: label, cls: '' },
          { k: 'text', x: 400, y: 175, t: deg + '°', cls: '' }
        ], caption: '角与边长无关，只与张开的程度有关' };
      }
      var o = [];
      o.push(S('固定一条边，另一条边旋转，张开的量就是角。', angle(45, '锐角：0° < α < 90°')));
      o.push(S('转过 90° 是<b>直角</b>。', angle(90, '直角：α = 90°')));
      o.push(S('继续转是<b>钝角</b>。', angle(135, '钝角：90° < α < 180°')));
      o.push(S('转到一条直线是<b>平角 180°</b>，转一整圈是<b>周角 360°</b>。', angle(180, '平角：α = 180°')));
      o.push(S('甲种本会把角继续往上转：超过 360°、反向转（负角），并用<b>弧度</b>代替度数。',
        { items: [
          { k: 'circle', x: 320, y: 150, r: 90, cls: 'is-void' },
          { k: 'line', x1: 320, y1: 150, x2: 410, y2: 150, cls: 'is-hi' },
          { k: 'line', x1: 320, y1: 150, x2: 320, y2: 60, cls: 'is-on' },
          { k: 'text', x: 320, y: 40, t: '0° = 0 弧度     90° = π/2 弧度', cls: '' },
          { k: 'text', x: 320, y: 268, t: '180° = π 弧度     360° = 2π 弧度', cls: '' }
        ], caption: '这是「任意角与弧度制」的入口' }));
      return o;
    },
    notes: [
      '<p>角与画出来的边长无关：把两条边延长，角的大小不变。</p>',
      '<p>量角器把半圆分成 180 份，一份是 1°。这个「把圆周等分」的做法在高中会换成弧度。</p>',
      '<p>甲种本代数1 把角推广到任意大小与正负方向，然后用单位圆定义 sin、cos —— 全部建立在「角是旋转量」这一认识上。</p>'
    ],
    example: { q: '时钟 3 点整，时针与分针的夹角是多少？', steps: ['钟面 12 大格共 360°，每格 30°', '3 点整相隔 3 格'], a: '90°' },
    quiz: [
      { q: '120° 的角是？', options: ['锐角', '直角', '钝角', '平角'], answer: 2, explain: '90° < 120° < 180°，是钝角。' },
      { q: '180° 等于多少弧度？', options: ['π/2', 'π', '2π', '1'], answer: 1, explain: '180° = π 弧度，这是弧度制的定义。' }
    ]
  });

  T({
    id: 'p-area-rect', unit: 'p-geo', title: '面积与割补：长方形、平行四边形', subtitle: '面积 = 每份的大小 × 份数',
    goal: '理解面积公式来自「数单位方格」，会用割补推导平行四边形面积',
    why: '★ 割补是甲种本微积分「定积分 = 无限细分再求和」的原型，也是立体几何祖暅原理的原型。',
    view: 'grid', minutes: 10, star: true, prereq: ['p-unit'],
    demo: function () {
      function g(n, hi) {
        var c = []; for (var i = 0; i < 12; i++) c.push({ v: '', cls: i < n ? (hi ? 'is-hi' : 'is-on') : 'is-pending' });
        return { cols: 4, rows: 3, cellW: 34, cells: c };
      }
      var o = [];
      o.push(S('长 4、宽 3 的长方形，可以排成 3 行、每行 4 个单位方格。', g(0), { 单位方格: '1×1' }));
      o.push(S('数一数：<b>4 × 3 = 12</b> 个方格，所以面积 = 长 × 宽。', g(12), { 面积: 12 }));
      o.push(S('公式：<b>S = a × b</b>。注意「长×宽」其实是「每行个数 × 行数」。', g(12, true), { 公式: 'S = a·b' }));
      o.push(S('平行四边形：把左边突出的三角形<b>剪下来贴到右边</b>，就变成长方形。',
        { view: 'shapes', items: [
          { k: 'poly', pts: [[130, 200], [170, 90], [410, 90], [370, 200]], cls: 'is-on' },
          { k: 'poly', pts: [[130, 200], [170, 90], [170, 200]], cls: 'is-hi', label: '剪', labelX: 150, labelY: 165 },
          { k: 'line', x1: 170, y1: 90, x2: 170, y2: 200, cls: 'is-dim' },
          { k: 'text', x: 320, y: 45, t: '剪补前后，面积一点没变', cls: '' },
          { k: 'text', x: 320, y: 250, t: 'S = 底 × 高', cls: '' }
        ], caption: '割补法：形状变了，面积不变' }));
      o.push(S('所以 <b>S = 底 × 高</b>，与斜不斜无关。',
        { view: 'shapes', items: [
          { k: 'rect', x: 170, y: 90, w: 240, h: 110, cls: 'is-done' },
          { k: 'text', x: 290, y: 150, t: 'S = a × h', cls: '' },
          { k: 'text', x: 290, y: 245, t: '高是两条平行线之间的垂直距离', cls: '' }
        ], caption: '补成的长方形' }));
      return o;
    },
    notes: [
      '<p>面积公式不是背出来的：把一个 1×1 的方格当作单位，数出总共能铺多少个。</p>',
      '<p>割补法只做两件事：切开、平移，面积不变但形状变规则，于是能套用已知公式。</p>',
      '<p>三角形、梯形、圆面积都靠割补；甲种本微积分的黎曼和是把曲边图形切成无数窄条再补成长方形，思路完全一致。</p>'
    ],
    example: { q: '平行四边形底 8、高 5，面积是多少？', steps: ['割补成长 8 宽 5 的长方形', 'S = 8 × 5'], a: '40' },
    quiz: [
      { q: '长 7 宽 4 的长方形面积是？', options: ['11', '22', '28', '14'], answer: 2, explain: 'S = 7×4 = 28。' },
      { q: '平行四边形面积公式是？', options: ['底×斜边', '底×高', '两邻边相乘', '周长×高'], answer: 1, explain: '割补后是长=底、宽=高的长方形。' }
    ]
  });

  T({
    id: 'p-area-tri', unit: 'p-geo', title: '三角形与梯形面积', subtitle: '两个全等三角形拼成一个平行四边形',
    goal: '会用「倍拼」推导三角形面积，理解为什么要除以 2',
    why: '解析几何里用行列式/坐标算三角形面积、微积分里三角形面积函数，都回到这个「一半」。',
    view: 'shapes', minutes: 9, prereq: ['p-area-rect'],
    demo: function () {
      var o = [];
      o.push(S('一个底 a、高 h 的三角形，面积是多少？先不猜，<b>再拿一个一模一样的</b>。',
        { items: [
          { k: 'poly', pts: [[180, 200], [280, 200], [280, 70]], cls: 'is-on' },
          { k: 'line', x1: 280, y1: 70, x2: 280, y2: 200, cls: 'is-dim' },
          { k: 'text', x: 230, y: 225, t: '底 a', cls: '' },
          { k: 'text', x: 300, y: 140, t: '高 h', cls: '' },
          { k: 'text', x: 320, y: 40, t: '三角形面积 = ?', cls: '' }
        ], caption: '直角三角形便于观察' }));
      o.push(S('把第二个旋转 180° 拼上去，正好得到一个<b>长方形</b>（面积 a×h）。',
        { items: [
          { k: 'poly', pts: [[180, 200], [280, 200], [280, 70]], cls: 'is-on' },
          { k: 'poly', pts: [[180, 200], [280, 70], [180, 70]], cls: 'is-hi' },
          { k: 'rect', x: 180, y: 70, w: 100, h: 130, cls: 'is-void' },
          { k: 'text', x: 320, y: 40, t: '两个三角形 = 一个长方形', cls: '' }
        ], caption: '倍拼法' }));
      o.push(S('所以一个三角形是它的一半：<b>S = a×h ÷ 2</b>。',
        { items: [
          { k: 'rect', x: 170, y: 70, w: 300, h: 60, rx: 8, cls: 'is-done' },
          { k: 'text', x: 320, y: 107, t: 'S三角形 = ½ · a · h', cls: '' },
          { k: 'text', x: 320, y: 175, t: '别忘了除以 2', cls: '' }
        ], caption: '那个 ½ 是「两个拼一个」来的' }));
      o.push(S('梯形同理：两个全等梯形拼成平行四边形，底是 <b>(上底+下底)</b>。',
        { items: [
          { k: 'rect', x: 170, y: 70, w: 300, h: 60, rx: 8, cls: 'is-on' },
          { k: 'text', x: 320, y: 107, t: 'S梯形 = ½ (a + b) h', cls: '' },
          { k: 'rect', x: 170, y: 145, w: 300, h: 50, rx: 8, cls: 'is-hi' },
          { k: 'text', x: 320, y: 178, t: '把上底看作 0，就退化成三角形', cls: '' }
        ], caption: '公式之间是连着的' }));
      return o;
    },
    notes: [
      '<p>「除以 2」不是规定，而是因为用了两个全等三角形才拼成已知图形。</p>',
      '<p>锐角、钝角三角形同样可以倍拼成平行四边形，结论不变。</p>',
      '<p>甲种本平面解析几何用坐标算三角形面积（行列式）、微积分初步算曲边梯形面积，本质仍是「切成可算的块再相加」。</p>'
    ],
    example: { q: '三角形底 10、高 6，面积？', steps: ['S = ½ × 10 × 6'], a: '30' },
    quiz: [
      { q: '三角形底 8、高 5，面积是？', options: ['40', '20', '13', '26'], answer: 1, explain: 'S = ½×8×5 = 20。' },
      { q: '梯形上底 3、下底 7、高 4，面积是？', options: ['20', '40', '10', '28'], answer: 0, explain: '½×(3+7)×4 = 20。' }
    ]
  });

  T({
    id: 'p-circle', unit: 'p-geo', title: '圆的周长与面积', subtitle: 'π 是周长与直径的固定比值',
    goal: '理解 π 的含义，会用「切扇形拼成长方形」推导圆面积',
    why: '★ 弧度制、三角函数定义、单位圆、极坐标，全部建立在 π 和圆周上。',
    view: 'shapes', minutes: 10, star: true, prereq: ['p-area-rect'],
    demo: function () {
      var o = [];
      o.push(S('量任何圆：<b>周长 ÷ 直径</b> 总是同一个数，叫 <b>π ≈ 3.14159</b>。',
        { items: [
          { k: 'circle', x: 320, y: 150, r: 90, cls: 'is-on' },
          { k: 'line', x1: 230, y1: 150, x2: 410, y2: 150, cls: 'is-hi' },
          { k: 'text', x: 320, y: 140, t: '直径 d', cls: '' },
          { k: 'text', x: 320, y: 40, t: 'C / d = π', cls: '' }
        ], caption: 'π 是比值，不是某个圆的专属数字' }));
      o.push(S('所以 <b>C = πd = 2πr</b>。半圆弧长就是 πr。',
        { items: [
          { k: 'rect', x: 150, y: 70, w: 340, h: 55, rx: 8, cls: 'is-done' },
          { k: 'text', x: 320, y: 105, t: 'C = 2πr', cls: '' },
          { k: 'rect', x: 150, y: 140, w: 340, h: 55, rx: 8, cls: 'is-on' },
          { k: 'text', x: 320, y: 175, t: '半圆 = πr', cls: '' }
        ], caption: '圆周长公式' }));
      o.push(S('面积：把圆切成许多小扇形，<b>交错拼起来</b>，越切越像一个长方形。',
        { items: [
          { k: 'circle', x: 200, y: 150, r: 80, cls: 'is-on' },
          { k: 'line', x1: 200, y1: 150, x2: 280, y2: 150, cls: 'is-hi' },
          { k: 'line', x1: 200, y1: 150, x2: 200, y2: 70, cls: 'is-hi' },
          { k: 'line', x1: 200, y1: 150, x2: 120, y2: 150, cls: 'is-hi' },
          { k: 'line', x1: 200, y1: 150, x2: 200, y2: 230, cls: 'is-hi' },
          { k: 'text', x: 320, y: 40, t: '切成 16、32、64… 份', cls: '' },
          { k: 'rect', x: 370, y: 110, w: 220, h: 80, cls: 'is-hi' },
          { k: 'text', x: 480, y: 155, t: '≈ 长方形', cls: '' }
        ], caption: '化曲为直' }));
      o.push(S('这个长方形的长 ≈ 半周长 <b>πr</b>，宽 ≈ 半径 <b>r</b>，所以 <b>S = πr²</b>。',
        { items: [
          { k: 'rect', x: 170, y: 100, w: 300, h: 90, cls: 'is-on' },
          { k: 'text', x: 320, y: 150, t: '长 πr  ×  宽 r  =  πr²', cls: '' },
          { k: 'text', x: 320, y: 240, t: '切得越细，越接近精确值', cls: '' }
        ], caption: '这就是「极限」的第一次出现' }));
      return o;
    },
    notes: [
      '<p>π 是<b>比值</b>，所有圆都一样；3.14 只是近似值，甲种本微积分里会看到更精确的处理。</p>',
      '<p>把圆切成扇形拼成长方形，用的是小学的割补法，但「切到无限细」已经是微积分的思想。</p>',
      '<p>弧度制的定义就是「弧长 ÷ 半径」，整圈 = 2πr/r = 2π 弧度；单位圆、正弦曲线、极坐标全由此展开。</p>'
    ],
    example: { q: '半径 3 的圆，周长和面积各是多少？', steps: ['C = 2π×3 = 6π', 'S = π×3² = 9π'], a: '周长 6π ≈ 18.84，面积 9π ≈ 28.26' },
    quiz: [
      { q: '半径 2 的圆面积是？', options: ['2π', '4π', '8π', 'π'], answer: 1, explain: 'S = πr² = π×4 = 4π。' },
      { q: '整圈等于多少弧度？', options: ['π', '2π', '360', '1'], answer: 1, explain: '弧长 2πr 除以半径 r 得 2π 弧度。' }
    ]
  });

  T({
    id: 'p-factor', unit: 'p-geo', title: '因数、倍数与质数合数', subtitle: '一个数能摆成几种长方形',
    goal: '会分解质因数、求最大公因数与最小公倍数',
    why: '★ 约分通分、整式因式分解、甲种本代数3「一元多项式与高次方程」都靠分解。',
    view: 'grid', minutes: 10, star: true, prereq: ['p-div', 'p-mul'],
    demo: function () {
      function rects(rows, cols, hi) {
        var c = []; for (var i = 0; i < rows * cols; i++) c.push({ v: '', cls: hi ? 'is-hi' : 'is-on' });
        return { cols: cols, rows: rows, cellW: 32, cells: c, caption: '12 个方格摆成 ' + rows + ' × ' + cols + ' 的长方形' };
      }
      var o = [];
      o.push(S('把 <b>12</b> 个小方格摆成长方形，有几种摆法？先看 3×4。', rects(3, 4), { 摆法: '3×4' }));
      o.push(S('还能摆 2×6：说明 <b>2 和 6 都是 12 的因数</b>。', rects(2, 6, true), { 因数: '2, 6' }));
      o.push(S('12 的全部因数：1, 2, 3, 4, 6, 12。只有 1 和它本身两个因数的是<b>质数</b>。',
        { cols: 6, rows: 2, cellW: 40, cells: [
          { v: '1', cls: 'is-done' }, { v: '2', cls: 'is-hi' }, { v: '3', cls: 'is-hi' }, { v: '4', cls: 'is-done' },
          { v: '6', cls: 'is-done' }, { v: '12', cls: 'is-done' },
          { v: '2|12', cls: 'is-on' }, { v: '3|12', cls: 'is-on' }, { v: '4|12', cls: 'is-on' },
          { v: '6|12', cls: 'is-on' }, { v: '2,3 是质数', cls: 'is-hi' }, { v: '其余是合数', cls: 'is-dim' }] }));
      o.push(S('分解质因数：<b>12 = 2 × 2 × 3 = 2² × 3</b>。',
        { view: 'tree', nodes: [
          { id: 'a', label: '12', x: 320, y: 50, cls: 'is-hi' },
          { id: 'b', label: '2', x: 220, y: 140, cls: 'is-done' },
          { id: 'c', label: '6', x: 420, y: 140, cls: '' },
          { id: 'd', label: '2', x: 370, y: 235, cls: 'is-done' },
          { id: 'e', label: '3', x: 470, y: 235, cls: 'is-done' }
        ], edges: [{ from: 'a', to: 'b' }, { from: 'a', to: 'c' }, { from: 'c', to: 'd' }, { from: 'c', to: 'e' }],
          caption: '除到全是质数为止，这叫分解质因数' }));
      o.push(S('有了分解式，最大公因数和最小公倍数就能直接读出来：',
        { cols: 1, rows: 2, cellW: 330, cells: [
          { v: '12 = 2²×3,  18 = 2×3²  →  最大公因数 2×3 = 6', cls: 'is-hi' },
          { v: '最小公倍数 2²×3² = 36（每种质因数取最高次）', cls: 'is-done' }] }));
      return o;
    },
    notes: [
      '<p>能整除就是因数；「摆长方形」让抽象的整除变成看得见的排列。</p>',
      '<p>分解质因数像把一个数拆成「不能再拆的积木」，而且拆法唯一（算术基本定理）。</p>',
      '<p>初中把 12 换成多项式，就是因式分解；甲种本代数3 讲一元多项式的因式定理、高次方程求根，是同一套思路的升级版。</p>'
    ],
    example: { q: '求 24 和 36 的最大公因数与最小公倍数', steps: ['24 = 2³×3，36 = 2²×3²', '最大公因数取较小次：2²×3 = 12', '最小公倍数取较大次：2³×3² = 72'], a: '最大公因数 12，最小公倍数 72' },
    quiz: [
      { q: '下面哪个是质数？', options: ['21', '27', '29', '33'], answer: 2, explain: '29 只有 1 和 29 两个因数。' },
      { q: '18 的质因数分解是？', options: ['2×9', '3×6', '2×3²', '2²×3'], answer: 2, explain: '18 = 2 × 3 × 3 = 2×3²。' }
    ]
  });

})();
