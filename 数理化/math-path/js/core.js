/* MathPath — 课程引擎：数据模型、进度存储、步骤播放器 */
(function (global) {
  'use strict';

  var MP = global.MathPath = global.MathPath || {};

  /* ---------------- 三层结构 ---------------- */
  MP.TRACKS = [
    { id: 'primary', name: '小学', sub: '算术基本功', desc: '把数、运算和图形变成看得见的东西', color: 'green' },
    { id: 'middle', name: '初中', sub: '代数 + 平面几何', desc: '符号化、坐标系、逻辑推理的起点', color: 'blue' },
    { id: 'bridge', name: '甲种本', sub: '六年制高中课本', desc: '1983 人教版较高要求版，共六册', color: 'amber' }
  ];

  MP.units = [];
  MP.topics = [];
  MP.books = [];
  MP.byId = {};
  MP.unitById = {};

  MP.registerUnits = function (list) {
    list.forEach(function (u) { MP.units.push(u); MP.unitById[u.id] = u; });
  };

  /* topic: { id, unit, title, subtitle, goal, why, star, minutes,
              view, demo(seed) -> steps, notes[3], example, quiz[], prereq[] } */
  MP.registerTopic = function (t) {
    t.track = (MP.unitById[t.unit] || {}).track || 'primary';
    t.star = !!t.star;
    t.minutes = t.minutes || 10;
    t.notes = t.notes || [];
    t.quiz = t.quiz || [];
    t.prereq = t.prereq || [];
    MP.topics.push(t);
    MP.byId[t.id] = t;
    return t;
  };

  MP.registerBooks = function (list) {
    list.forEach(function (b) { MP.books.push(b); });
  };

  MP.topicsOf = function (unitId) {
    return MP.topics.filter(function (t) { return t.unit === unitId; });
  };
  MP.unitsOf = function (trackId) {
    return MP.units.filter(function (u) { return u.track === trackId; });
  };

  /* ---------------- 工具 ---------------- */
  var U = MP.util = {
    esc: function (s) {
      return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
      });
    },
    gcd: function (a, b) { a = Math.abs(a); b = Math.abs(b); while (b) { var t = a % b; a = b; b = t; } return a; },
    lcm: function (a, b) { return Math.abs(a * b) / U.gcd(a, b); },
    frac: function (n, d) {
      if (d === 0) return '∞';
      if (d < 0) { n = -n; d = -d; }
      var g = U.gcd(n, d) || 1; n /= g; d /= g;
      return d === 1 ? String(n) : n + '/' + d;
    },
    rnd: function (a, b) { return a + Math.floor(Math.random() * (b - a + 1)); },
    range: function (n) { var a = []; for (var i = 0; i < n; i++) a.push(i); return a; },
    sum: function (a) { return a.reduce(function (x, y) { return x + y; }, 0); },
    round: function (x, p) { var m = Math.pow(10, p || 0); return Math.round(x * m) / m; },
    shuffle: function (a) {
      a = a.slice();
      for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; }
      return a;
    },
    /* 供 course 文件构造步骤 */
    step: function (msg, data, info) { return { msg: msg, data: data || {}, info: info || {} }; }
  };

  /* ---------------- 进度存储 ---------------- */
  var KEY = 'mathpath.v1';
  function blank() {
    return { version: 1, visited: {}, mastered: {}, quiz: {}, wrong: [], diagnostic: null, current: null, started: Date.now() };
  }
  /* 学习顺序：小学 → 初中 → 衔接课 → 按阅读顺序的六册 */
  MP.topicRank = function (t) {
    if (t.track === 'primary') return 0;
    if (t.track === 'middle') return 1;
    var u = MP.unitById[t.unit] || {};
    if (!u.book) return 2;
    var b = null;
    for (var i = 0; i < MP.books.length; i++) if (MP.books[i].id === u.book) b = MP.books[i];
    return 3 + (b ? b.order : 0);
  };
  MP.orderedTopics = function () {
    return MP.topics.map(function (t, i) { return { t: t, i: i, r: MP.topicRank(t) }; })
      .sort(function (a, b) { return a.r - b.r || a.i - b.i; })
      .map(function (x) { return x.t; });
  };

  var P = MP.progress = {
    data: blank(),
    load: function () {
      try {
        var raw = global.localStorage && global.localStorage.getItem(KEY);
        if (raw) {
          var d = JSON.parse(raw);
          if (d && d.version === 1) {
            var base = blank();
            for (var k in base) if (!(k in d)) d[k] = base[k];
            P.data = d;
          }
        }
      } catch (e) { /* file:// 或隐私模式下不可用 */ }
      return P.data;
    },
    save: function () {
      try { global.localStorage && global.localStorage.setItem(KEY, JSON.stringify(P.data)); } catch (e) {}
    },
    visit: function (id) { P.data.visited[id] = Date.now(); P.data.current = id; P.save(); },
    isVisited: function (id) { return !!P.data.visited[id]; },
    isMastered: function (id) { return !!P.data.mastered[id]; },
    master: function (id, on) {
      if (on === false) delete P.data.mastered[id]; else P.data.mastered[id] = Date.now();
      P.save();
    },
    recordQuiz: function (id, results) {
      var ok = results.filter(function (r) { return r.ok; }).length;
      P.data.quiz[id] = { ok: ok, total: results.length, last: Date.now() };
      results.forEach(function (r) {
        if (r.ok) return;
        P.data.wrong = P.data.wrong.filter(function (w) { return !(w.id === id && w.q === r.q); });
        P.data.wrong.unshift({ id: id, q: r.q, answer: r.answer, yours: r.yours, ts: Date.now() });
      });
      if (results.length && ok === results.length) P.data.mastered[id] = Date.now();
      P.data.wrong = P.data.wrong.slice(0, 60);
      P.save();
      return { ok: ok, total: results.length };
    },
    stats: function (trackId) {
      var list = MP.topics.filter(function (t) {
        return trackId === 'bridge' ? t.track === 'bridge' : t.track === trackId;
      });
      var done = list.filter(function (t) { return P.isMastered(t.id); }).length;
      return { total: list.length, done: done, pct: list.length ? Math.round(done / list.length * 100) : 0 };
    },
    overall: function () {
      var done = MP.topics.filter(function (t) { return P.isMastered(t.id); }).length;
      return { total: MP.topics.length, done: done, pct: MP.topics.length ? Math.round(done / MP.topics.length * 100) : 0 };
    },
    /* 下一个推荐：第一个未掌握的、且前置已掌握的知识点 */
    recommend: function () {
      var list = MP.orderedTopics();
      for (var i = 0; i < list.length; i++) {
        var t = list[i];
        if (P.isMastered(t.id)) continue;
        var ready = t.prereq.every(function (p) { return !MP.byId[p] || P.isMastered(p); });
        if (ready) return t;
      }
      return list[0] || MP.topics[0];
    },
    reset: function () { P.data = blank(); P.save(); }
  };

  /* ---------------- 步骤播放器 ---------------- */
  MP.Player = function (onChange) {
    this.steps = [];
    this.i = 0;
    this.speed = 1;
    this.playing = false;
    this.timer = null;
    this.onChange = onChange || function () {};
  };
  MP.Player.prototype.load = function (steps) {
    this.pause();
    this.steps = steps || [];
    this.i = 0;
    this.emit();
  };
  MP.Player.prototype.emit = function () {
    this.onChange(this.steps[this.i] || null, this.i, this.steps.length);
  };
  MP.Player.prototype.seek = function (i) {
    this.i = Math.max(0, Math.min(this.steps.length - 1, i));
    this.emit();
  };
  MP.Player.prototype.next = function () {
    if (this.i >= this.steps.length - 1) { this.pause(); return false; }
    this.i++; this.emit(); return true;
  };
  MP.Player.prototype.prev = function () { if (this.i > 0) { this.i--; this.emit(); } };
  MP.Player.prototype.tick = function () {
    var self = this;
    this.pause();
    this.playing = true;
    this.timer = setInterval(function () {
      if (!self.next()) self.pause();
    }, 900 / this.speed);
    this.onChange(this.steps[this.i], this.i, this.steps.length);
  };
  MP.Player.prototype.play = function () {
    if (this.playing) return;
    if (this.i >= this.steps.length - 1) this.i = 0;
    this.tick();
  };
  MP.Player.prototype.pause = function () {
    var wasPlaying = this.playing;
    if (this.timer) clearInterval(this.timer);
    this.timer = null; this.playing = false;
    if (wasPlaying) this.emit();
  };
  MP.Player.prototype.toggle = function () { this.playing ? this.pause() : this.play(); };
  MP.Player.prototype.setSpeed = function (s) {
    this.speed = s;
    if (this.playing) this.tick();
  };

})(typeof window !== 'undefined' ? window : globalThis);
