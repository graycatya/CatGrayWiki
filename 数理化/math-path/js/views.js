/* MathPath — 通用可视化渲染器
   step.data 格式约定：
   bars      { values:[], labels:[], marks:{hi:[i], done:[i], warn:[i]}, max, caption }
   fraction  { rows:[{label, n, d, cls}], caption }          每行一条分数条
   grid      { cols, rows, cells:[{v,cls}|null], caption, cellW }
   steps     { lines:[{cells:[{t,cls}], cls}], caption }     竖式 / 算式行
   numberline{ min, max, ticks:[], points:[{x,label,cls}], segments:[{a,b,label,cls}], caption }
   axis      { range:{x:[a,b],y:[c,d]}, curves:[{pts:[[x,y]..],cls,label}],
               lines:[{a:[x,y],b:[x,y],cls,label}], points:[{x,y,label,cls}],
               rects:[{x,y,w,h,cls,label}], polys:[{pts:[[x,y]..],cls,label}], caption }
   shapes    { items:[{k:'rect|circle|line|poly|text', ...}], caption, W, H }
   tree      { nodes:[{id,label,x,y,cls}], edges:[{from,to,label}], caption }
*/
(function (global) {
  'use strict';
  var MP = global.MathPath;
  var V = MP.views = {};

  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  }
  function S(tag, attrs) {
    var e = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (var k in attrs) if (attrs[k] != null) e.setAttribute(k, attrs[k]);
    return e;
  }
  function svgRoot(h) {
    var s = S('svg', { viewBox: '0 0 640 ' + (h || 300), class: 'mp-svg', preserveAspectRatio: 'xMidYMid meet' });
    return s;
  }
  function cap(host, text) {
    if (text) host.appendChild(el('div', 'mp-cap', text));
  }
  function clear(host) { host.innerHTML = ''; }
  function clsOf(i, marks, extra) {
    var c = [];
    if (marks) {
      if ((marks.hi || []).indexOf(i) >= 0) c.push('is-hi');
      if ((marks.done || []).indexOf(i) >= 0) c.push('is-done');
      if ((marks.warn || []).indexOf(i) >= 0) c.push('is-warn');
      if ((marks.dim || []).indexOf(i) >= 0) c.push('is-dim');
    }
    if (extra) c.push(extra);
    return c.join(' ');
  }
  V.el = el; V.svg = S; V.svgRoot = svgRoot; V.cap = cap; V.clsOf = clsOf;

  /* ---------- 1. bars 柱状 / 数组条 ---------- */
  V.bars = function (host, d) {
    clear(host);
    var values = d.values || [], labels = d.labels || [], marks = d.marks || {};
    var max = d.max || Math.max.apply(null, values.concat([1]));
    var wrap = el('div', 'mp-bars');
    values.forEach(function (v, i) {
      var col = el('div', 'mp-bar-col ' + clsOf(i, marks));
      var h = Math.max(4, Math.round(Math.abs(v) / (Math.abs(max) || 1) * 100));
      var bar = el('div', 'mp-bar');
      bar.style.height = h + '%';
      bar.appendChild(el('span', 'mp-bar-v', String(v)));
      col.appendChild(bar);
      col.appendChild(el('div', 'mp-bar-l', labels[i] == null ? String(i) : labels[i]));
      wrap.appendChild(col);
    });
    host.appendChild(wrap);
    cap(host, d.caption);
  };

  /* ---------- 2. fraction 分数条 ---------- */
  V.fraction = function (host, d) {
    clear(host);
    var wrap = el('div', 'mp-frac');
    (d.rows || []).forEach(function (r) {
      var row = el('div', 'mp-frac-row ' + (r.cls || ''));
      row.appendChild(el('div', 'mp-frac-label', r.label || ''));
      var bar = el('div', 'mp-frac-bar');
      var den = Math.max(1, Math.min(24, r.d || 1));
      for (var i = 0; i < den; i++) {
        var cell = el('div', 'mp-frac-cell' + (i < (r.n || 0) ? ' is-on' : ''));
        if (d.showIndex && i < (r.n || 0)) cell.appendChild(el('span', '', String(i + 1)));
        bar.appendChild(cell);
      }
      if (d.equalWidth) bar.style.width = (den * 26) + 'px';
      row.appendChild(bar);
      if (r.note) row.appendChild(el('div', 'mp-frac-note', r.note));
      wrap.appendChild(row);
    });
    host.appendChild(wrap);
    cap(host, d.caption);
  };

  /* ---------- 3. grid 方格 ---------- */
  V.grid = function (host, d) {
    clear(host);
    var cols = d.cols || 4, rows = d.rows || 1;
    var g = el('div', 'mp-grid');
    g.style.gridTemplateColumns = 'repeat(' + cols + ', ' + (d.cellW || 40) + 'px)';
    var cells = d.cells || [];
    for (var i = 0; i < cols * rows; i++) {
      var c = cells[i];
      if (c == null) c = { v: '', cls: 'is-void' };
      if (typeof c === 'string' || typeof c === 'number') c = { v: c };
      var box = el('div', 'mp-gcell ' + (c.cls || ''));
      box.textContent = c.v == null ? '' : c.v;
      g.appendChild(box);
    }
    host.appendChild(g);
    cap(host, d.caption);
  };

  /* ---------- 4. steps 算式 / 竖式 ---------- */
  V.steps = function (host, d) {
    clear(host);
    var wrap = el('div', 'mp-steps');
    (d.lines || []).forEach(function (ln) {
      var row = el('div', 'mp-step-row ' + (ln.cls || ''));
      if (ln.label) row.appendChild(el('div', 'mp-step-label', ln.label));
      (ln.cells || []).forEach(function (c) {
        if (typeof c === 'string' || typeof c === 'number') c = { t: c };
        var box = el('span', 'mp-step-cell ' + (c.cls || ''));
        box.textContent = c.t == null ? '' : c.t;
        row.appendChild(box);
      });
      wrap.appendChild(row);
    });
    host.appendChild(wrap);
    cap(host, d.caption);
  };

  /* ---------- 5. numberline 数轴 ---------- */
  V.numberline = function (host, d) {
    clear(host);
    var s = svgRoot(190);
    var min = d.min == null ? -5 : d.min, max = d.max == null ? 5 : d.max;
    var X = function (v) { return 40 + (v - min) / ((max - min) || 1) * 560; };
    var y = 110;
    s.appendChild(S('line', { x1: 30, y1: y, x2: 610, y2: y, class: 'mp-ax' }));
    s.appendChild(S('path', { d: 'M610 ' + y + ' l-9 -5 l0 10 z', class: 'mp-ax-arrow' }));
    var ticks = d.ticks;
    if (!ticks) {
      ticks = [];
      var span = max - min;
      var step = span > 30 ? 5 : span > 12 ? 2 : 1;
      for (var v = Math.ceil(min / step) * step; v <= max; v += step) ticks.push(v);
    }
    ticks.forEach(function (t) {
      s.appendChild(S('line', { x1: X(t), y1: y - 6, x2: X(t), y2: y + 6, class: 'mp-tick' }));
      var tx = S('text', { x: X(t), y: y + 24, class: 'mp-ts', 'text-anchor': 'middle' });
      tx.textContent = t; s.appendChild(tx);
    });
    (d.segments || []).forEach(function (g) {
      var yy = y - 24 - (g.level || 0) * 26;
      s.appendChild(S('line', { x1: X(g.a), y1: yy, x2: X(g.b), y2: yy, class: 'mp-seg ' + (g.cls || '') }));
      s.appendChild(S('line', { x1: X(g.a), y1: yy - 5, x2: X(g.a), y2: yy + 5, class: 'mp-seg-tick' }));
      s.appendChild(S('line', { x1: X(g.b), y1: yy - 5, x2: X(g.b), y2: yy + 5, class: 'mp-seg-tick' }));
      if (g.label) {
        var t = S('text', { x: (X(g.a) + X(g.b)) / 2, y: yy - 8, class: 'mp-ts', 'text-anchor': 'middle' });
        t.textContent = g.label; s.appendChild(t);
      }
    });
    (d.points || []).forEach(function (p) {
      s.appendChild(S('circle', { cx: X(p.x), cy: y, r: 7, class: 'mp-dot ' + (p.cls || '') }));
      if (p.label) {
        var t = S('text', { x: X(p.x), y: y - 18, class: 'mp-ts', 'text-anchor': 'middle' });
        t.textContent = p.label; s.appendChild(t);
      }
    });
    host.appendChild(s);
    cap(host, d.caption);
  };

  /* ---------- 6. axis 直角坐标系 ---------- */
  V.axis = function (host, d) {
    clear(host);
    var s = svgRoot(300);
    var r = d.range || { x: [-5, 5], y: [-5, 5] };
    var x0 = r.x[0], x1 = r.x[1], y0 = r.y[0], y1 = r.y[1];
    var X = function (v) { return 40 + (v - x0) / ((x1 - x0) || 1) * 560; };
    var Y = function (v) { return 270 - (v - y0) / ((y1 - y0) || 1) * 240; };
    var g = S('g', { class: 'mp-grid-lines' });
    for (var vx = Math.ceil(x0); vx <= x1; vx++) {
      g.appendChild(S('line', { x1: X(vx), y1: 30, x2: X(vx), y2: 270, class: 'mp-gl' }));
      var tx = S('text', { x: X(vx), y: 286, class: 'mp-ts', 'text-anchor': 'middle' });
      tx.textContent = vx; g.appendChild(tx);
    }
    for (var vy = Math.ceil(y0); vy <= y1; vy++) {
      g.appendChild(S('line', { x1: 40, y1: Y(vy), x2: 600, y2: Y(vy), class: 'mp-gl' }));
      var ty = S('text', { x: 32, y: Y(vy) + 4, class: 'mp-ts', 'text-anchor': 'end' });
      ty.textContent = vy; g.appendChild(ty);
    }
    s.appendChild(g);
    if (x0 <= 0 && x1 >= 0) s.appendChild(S('line', { x1: X(0), y1: 26, x2: X(0), y2: 274, class: 'mp-ax' }));
    if (y0 <= 0 && y1 >= 0) s.appendChild(S('line', { x1: 36, y1: Y(0), x2: 604, y2: Y(0), class: 'mp-ax' }));
    var ox = S('text', { x: 606, y: Y(0) - 8, class: 'mp-ts' }); ox.textContent = 'x'; s.appendChild(ox);
    var oy = S('text', { x: X(0) + 10, y: 26, class: 'mp-ts' }); oy.textContent = 'y'; s.appendChild(oy);

    (d.rects || []).forEach(function (q) {
      var x = X(q.x), y = Y(q.y + q.h), w = X(q.x + q.w) - X(q.x), h = Y(q.y) - Y(q.y + q.h);
      s.appendChild(S('rect', { x: x, y: y, width: w, height: h, class: 'mp-rect ' + (q.cls || '') }));
      if (q.label) {
        var t = S('text', { x: x + w / 2, y: y + h / 2 + 4, class: 'mp-ts', 'text-anchor': 'middle' });
        t.textContent = q.label; s.appendChild(t);
      }
    });
    (d.polys || []).forEach(function (p) {
      var pts = (p.pts || []).map(function (q) { return X(q[0]) + ',' + Y(q[1]); }).join(' ');
      s.appendChild(S('polygon', { points: pts, class: 'mp-poly ' + (p.cls || '') }));
      if (p.label) {
        var t = S('text', { x: X(p.pts[0][0]) + 8, y: Y(p.pts[0][1]) - 8, class: 'mp-ts' });
        t.textContent = p.label; s.appendChild(t);
      }
    });
    (d.curves || []).forEach(function (c) {
      var str = (c.pts || []).map(function (p, i) { return (i ? 'L' : 'M') + X(p[0]) + ' ' + Y(p[1]); }).join(' ');
      s.appendChild(S('path', { d: str, class: 'mp-curve ' + (c.cls || ''), fill: 'none' }));
      if (c.label && c.pts.length) {
        var last = c.pts[c.pts.length - 1];
        var t = S('text', { x: X(last[0]) + 8, y: Y(last[1]) - 6, class: 'mp-ts' });
        t.textContent = c.label; s.appendChild(t);
      }
    });
    (d.lines || []).forEach(function (l) {
      s.appendChild(S('line', { x1: X(l.a[0]), y1: Y(l.a[1]), x2: X(l.b[0]), y2: Y(l.b[1]), class: 'mp-line ' + (l.cls || '') }));
      if (l.label) {
        var t = S('text', { x: X(l.b[0]) + 8, y: Y(l.b[1]) - 6, class: 'mp-ts' });
        t.textContent = l.label; s.appendChild(t);
      }
    });
    (d.points || []).forEach(function (p) {
      s.appendChild(S('circle', { cx: X(p.x), cy: Y(p.y), r: 6, class: 'mp-dot ' + (p.cls || '') }));
      if (p.label) {
        var t = S('text', { x: X(p.x) + 10, y: Y(p.y) - 10, class: 'mp-ts' });
        t.textContent = p.label; s.appendChild(t);
      }
    });
    host.appendChild(s);
    cap(host, d.caption);
  };

  /* ---------- 7. shapes 自由图形 ---------- */
  V.shapes = function (host, d) {
    clear(host);
    var s = svgRoot(d.H || 300);
    if (d.W && d.W !== 640) s.setAttribute('viewBox', '0 0 ' + d.W + ' ' + (d.H || 300));
    (d.items || []).forEach(function (it) {
      var e, t;
      var cls = it.cls || '';
      if (it.k === 'rect') {
        e = S('rect', { x: it.x, y: it.y, width: it.w, height: it.h, rx: it.rx || 0, class: 'mp-shape ' + cls });
      } else if (it.k === 'circle') {
        e = S('circle', { cx: it.x, cy: it.y, r: it.r, class: 'mp-shape ' + cls });
      } else if (it.k === 'line') {
        e = S('line', { x1: it.x1, y1: it.y1, x2: it.x2, y2: it.y2, class: 'mp-shape-line ' + cls });
      } else if (it.k === 'poly') {
        e = S('polygon', { points: (it.pts || []).map(function (p) { return p[0] + ',' + p[1]; }).join(' '), class: 'mp-shape ' + cls });
      } else if (it.k === 'text') {
        e = S('text', { x: it.x, y: it.y, class: 'mp-shape-text ' + cls, 'text-anchor': it.anchor || 'middle' });
        e.textContent = it.t;
      } else return;
      s.appendChild(e);
      if (it.k !== 'text' && it.label) {
        t = S('text', { x: it.labelX == null ? (it.x || 0) + (it.w || 0) / 2 : it.labelX,
                         y: it.labelY == null ? (it.y || 0) + (it.h || 0) / 2 + 5 : it.labelY,
                         class: 'mp-shape-text ' + cls, 'text-anchor': 'middle' });
        t.textContent = it.label; s.appendChild(t);
      }
    });
    host.appendChild(s);
    cap(host, d.caption);
  };

  /* ---------- 8. tree 树 ---------- */
  V.tree = function (host, d) {
    clear(host);
    var s = svgRoot(d.H || 300);
    var map = {};
    (d.nodes || []).forEach(function (n) { map[n.id] = n; });
    (d.edges || []).forEach(function (e) {
      var a = map[e.from], b = map[e.to];
      if (!a || !b) return;
      s.appendChild(S('line', { x1: a.x, y1: a.y + 14, x2: b.x, y2: b.y - 14, class: 'mp-tree-edge' }));
      if (e.label) {
        var t = S('text', { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 - 4, class: 'mp-ts', 'text-anchor': 'middle' });
        t.textContent = e.label; s.appendChild(t);
      }
    });
    (d.nodes || []).forEach(function (n) {
      s.appendChild(S('circle', { cx: n.x, cy: n.y, r: n.r || 20, class: 'mp-tree-node ' + (n.cls || '') }));
      var t = S('text', { x: n.x, y: n.y + 5, class: 'mp-tree-label', 'text-anchor': 'middle' });
      t.textContent = n.label; s.appendChild(t);
    });
    host.appendChild(s);
    cap(host, d.caption);
  };

  V.render = function (host, view, data) {
    var fn = V[view] || V.steps;
    try { fn(host, data || {}); }
    catch (e) {
      clear(host);
      host.appendChild(el('div', 'mp-error', '渲染出错：' + (e && e.message)));
    }
  };

})(typeof window !== 'undefined' ? window : globalThis);
