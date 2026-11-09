/* MathPath — 应用界面 */
(function () {
  'use strict';
  var MP = window.MathPath, P = MP.progress, V = MP.views, U = MP.util;
  function $(id) { return document.getElementById(id); }
  var els = {
    content: $('content'), crumb: $('crumb'), navTree: $('navTree'), trackTabs: $('trackTabs'),
    footPct: $('footPct'), footFill: $('footFill'), footNote: $('footNote'),
    wrongCount: $('wrongCount'), toast: $('toast'), sidebar: $('sidebar')
  };
  var state = { view: 'map', topicId: null, track: 'primary', seed: 0, quiz: null, diag: null, exOpen: false };
  P.load();

  var NOTE_KEYS = ['看得见', '怎么做', '往下接'];
  var player = new MP.Player(onStep);
  player.setSpeed(1);

  function toast(msg) {
    els.toast.textContent = msg;
    els.toast.classList.add('show');
    clearTimeout(toast._t);
    toast._t = setTimeout(function () { els.toast.classList.remove('show'); }, 2200);
  }
  function esc(s) { return U.esc(s); }

  /* ---------------- 侧栏 ---------------- */
  function renderTabs() {
    els.trackTabs.innerHTML = MP.TRACKS.map(function (t) {
      return '<button class="track-tab t-' + t.color + (state.track === t.id ? ' on' : '') +
        '" data-track="' + t.id + '">' + t.name + '</button>';
    }).join('');
    Array.prototype.forEach.call(els.trackTabs.querySelectorAll('.track-tab'), function (b) {
      b.onclick = function () { state.track = b.dataset.track; renderTabs(); renderNav(); };
    });
  }

  function unitHtml(u) {
    var list = MP.topicsOf(u.id);
    var done = list.filter(function (t) { return P.isMastered(t.id); }).length;
    var h = '<div class="nav-unit"><div class="nav-unit-head"><span class="u-dot"></span>' + u.name +
      '<span class="u-num">' + done + '/' + list.length + '</span></div>';
    list.forEach(function (t) {
      h += '<div class="nav-topic' + (t.id === state.topicId && state.view === 'topic' ? ' on' : '') +
        (P.isMastered(t.id) ? ' done' : '') + '" data-id="' + t.id + '">' +
        '<span class="t-state"></span><span>' + t.title + '</span>' +
        (t.star ? '<span class="t-star">★</span>' : '') + '</div>';
    });
    return h + '</div>';
  }
  function renderNav() {
    var html = '';
    if (state.track === 'bridge') {
      var plain = MP.unitsOf('bridge').filter(function (u) { return !u.book; });
      if (plain.length) {
        html += '<div class="nav-book">衔接课 · 通向甲种本</div>' + plain.map(unitHtml).join('');
      }
      MP.books.slice().sort(function (a, b) { return a.order - b.order; }).forEach(function (b) {
        var us = MP.unitsOf('bridge').filter(function (u) { return u.book === b.id; });
        if (!us.length) return;
        html += '<div class="nav-book">第 ' + b.order + ' 本 · ' + b.name + '</div>' + us.map(unitHtml).join('');
      });
      html += '<div class="nav-unit"><div class="nav-unit-head"><span class="u-dot"></span>课本总览</div>' +
        '<div class="nav-topic" data-act="books"><span class="t-state"></span><span>查看六本目录与入学检查 →</span></div></div>';
    } else {
      html = MP.unitsOf(state.track).map(unitHtml).join('');
    }
    els.navTree.innerHTML = html;
    Array.prototype.forEach.call(els.navTree.querySelectorAll('[data-id]'), function (n) {
      n.onclick = function () { openTopic(n.dataset.id); closeSidebar(); };
    });
    var b = els.navTree.querySelector('[data-act="books"]');
    if (b) b.onclick = function () {
      showMap();
      setTimeout(function () { var e = $('books'); if (e) e.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 60);
      closeSidebar();
    };
  }

  function renderFoot() {
    var s = P.overall();
    els.footPct.textContent = s.pct + '%';
    els.footFill.style.width = s.pct + '%';
    els.footNote.textContent = s.done + ' / ' + s.total + ' 个知识点已掌握';
    var n = P.data.wrong.length;
    els.wrongCount.textContent = n ? n : '';
    els.wrongCount.style.display = n ? '' : 'none';
  }
  function renderChrome() { renderTabs(); renderNav(); renderFoot(); }
  function closeSidebar() { els.sidebar.classList.remove('open'); }

  /* ---------------- 课本对照索引（全量 OCR 生成） ---------------- */
  var CN_CH = { '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10 };
  var BOOK_NAMES = {
    alg1: '代数 第一册', alg2: '代数 第二册', alg3: '代数 第三册',
    analytic: '平面解析几何 全一册', solid: '立体几何 全一册', calc: '微积分初步 全一册'
  };
  function chapterNo(name) {
    var m = String(name || '').match(/第([一二三四五六七八九十]+)章/);
    return m ? (CN_CH[m[1]] || 0) : 0;
  }
  function textbookInfo(t) {
    var u = MP.unitById[t.unit] || {};
    if (!u.book || !MP.TEXTBOOK_INDEX) return null;
    var b = MP.TEXTBOOK_INDEX[u.book];
    if (!b || !b.chapters) return null;
    var ch = chapterNo(u.name);
    var c = b.chapters[String(ch)];
    return c ? { book: u.book, ch: ch, c: c, b: b } : null;
  }
  function textbookCardHtml(t) {
    var info = textbookInfo(t);
    if (!info) return '';
    var c = info.c, b = info.b;
    var ex = (c.examples || []).length
      ? c.examples.map(function (x) { return '例' + x; }).join('、') : '本章未识别到例题编号';
    var sec = (c.sections || []).length ? c.sections.join('；') : '—';
    return '<div class="tb-card"><div class="tb-k">课本依据 · 全量 OCR 索引</div>' +
      '<div class="tb-row"><span>章次</span><b>第 ' + info.ch + ' 章 ' + esc(c.title || '') + '</b></div>' +
      '<div class="tb-row"><span>扫描页</span><b>PDF 第 ' + c.start + '–' + c.end + ' 页 · 全册 ' + b.pages + ' 页</b></div>' +
      '<div class="tb-row"><span>例题</span><b>' + esc(ex) + '</b></div>' +
      '<div class="tb-row"><span>练习</span><b>出现在 ' + (c.exercisePages || []).length + ' 页，最大题号 ' + (c.exerciseMax || 0) + '</b></div>' +
      '<div class="tb-row"><span>小节</span><b>' + esc(sec) + '</b></div>' +
      '<div class="tb-note">题号由课本扫描页 OCR 提取；公式与图形无法可靠识别，仅作定位与检索用，不是课本原文。</div></div>';
  }
  function showTextbook() {
    state.view = 'index'; state.topicId = null; player.pause();
    els.crumb.textContent = '课本对照索引';
    var idx = MP.TEXTBOOK_INDEX || {}, refs = MP.TEXTBOOK_REFS || {};
    var html = '<div class="wrap"><div class="map-hero"><div class="map-eyebrow">甲种本 · 原文定位</div>' +
      '<h1>课本对照索引</h1><p class="map-lead">六册课本与六本教学参考书已全量扫描识别。这里按章列出例题编号、练习所在页与小节标题，可用来把软件里的每一课定位到课本具体位置。公式与图形因 OCR 打散，需回看原页。</p></div>';
    Object.keys(BOOK_NAMES).forEach(function (b) {
      var d = idx[b];
      html += '<div class="block"><div class="block-head"><span class="bh-num">▤</span>' + BOOK_NAMES[b] +
        '<span class="bh-hint">' + (d ? d.pages : 0) + ' 页</span></div>';
      if (d && d.chapters) {
        Object.keys(d.chapters).sort(function (a, c) { return +a - +c; }).forEach(function (ch) {
          var c = d.chapters[ch];
          html += '<details class="idx-ch"><summary>第 ' + ch + ' 章 ' + esc(c.title || '') +
            ' <span>PDF ' + c.start + '–' + c.end + ' 页 · 例题 ' + (c.examples || []).length + ' 处</span></summary>' +
            '<div class="idx-body"><div class="idx-row"><span>小节</span><b>' + esc((c.sections || []).join('；') || '—') + '</b></div>' +
            '<div class="idx-row"><span>例题编号</span><b>' + esc((c.examples || []).map(function (x) { return '例' + x; }).join('、') || '—') + '</b></div>' +
            '<div class="idx-row"><span>练习</span><b>出现在 PDF 第 ' + (c.exercisePages || []).join('、') + ' 页 · 最大题号 ' + (c.exerciseMax || 0) + '</b></div></div></details>';
        });
      } else html += '<div class="empty">该册索引尚未生成</div>';
      html += '</div>';
    });
    html += '<div class="block"><div class="block-head"><span class="bh-num">▤</span>六本教学参考书</div>';
    Object.keys(refs).forEach(function (r) {
      var d = refs[r], hits = d.hits || {};
      html += '<div class="idx-row"><span>' + esc(d.label) + '</span><b>' + d.pages + ' 页 · 练习 ' + (hits['练习'] || 0) +
        ' 处 · 习题 ' + (hits['习题'] || 0) + ' 处 · 提示 ' + (hits['提示'] || 0) +
        ' 处 · 教学要求 ' + (hits['教学要求'] || 0) + ' 处 · 课时 ' + (hits['课时'] || 0) + ' 处</b></div>';
    });
    html += '<p class="sec-sub" style="margin:12px 0 0">教参含教材说明、各章教材分析、教学要求、习题提示与课时安排，可作为后续逐章精修的依据。</p></div></div>';
    els.content.innerHTML = html;
    renderChrome();
    els.content.scrollTop = 0;
  }

  /* ---------------- 学习地图 ---------------- */
  function bookReadiness(b) {
    var ok = b.req.filter(function (id) { return P.isMastered(id); }).length;
    return { ok: ok, total: b.req.length, pct: Math.round(ok / b.req.length * 100) };
  }
  function bridgePct() {
    if (!MP.books.length) return 0;
    var sum = MP.books.reduce(function (a, b) { return a + bookReadiness(b).pct; }, 0);
    return Math.round(sum / MP.books.length);
  }
  function bookTopics(b) {
    var ids = {};
    MP.units.forEach(function (u) { if (u.book === b.id) ids[u.id] = 1; });
    return MP.topics.filter(function (t) { return ids[t.unit]; });
  }
  function bridgeCourseStats() {
    var list = [];
    MP.books.forEach(function (b) { list = list.concat(bookTopics(b)); });
    var done = list.filter(function (t) { return P.isMastered(t.id); }).length;
    return { total: list.length, done: done, pct: list.length ? Math.round(done / list.length * 100) : 0 };
  }
  function mapTrackCard(t) {
    var s = t.id === 'bridge' ? bridgeCourseStats() : P.stats(t.id);
    var chips = t.id === 'bridge'
      ? MP.books.slice().sort(function (a, b) { return a.order - b.order; }).map(function (b) { return b.name; }).slice(0, 3)
      : MP.unitsOf(t.id).map(function (u) { return u.name; });
    return '<div class="track-card" data-track="' + t.id + '">' +
      '<div class="tc-head"><b>' + t.name + '</b><span>' + t.sub + '</span>' +
      '<span class="tc-pct ' + (t.color === 'green' ? 'g' : t.color === 'blue' ? 'b' : 'a') + '">' + s.pct + '%</span></div>' +
      '<div class="tc-bar"><i class="' + (t.color === 'green' ? 'g' : t.color === 'blue' ? 'b' : 'a') + '" style="width:' + s.pct + '%"></i></div>' +
      '<div class="tc-desc">' + (t.id === 'bridge'
        ? '六册按章拆成 ' + s.total + ' 课，已掌握 ' + s.done + ' 课；入学检查平均通过率 ' + bridgePct() + '%'
        : t.desc) + '</div>' +
      '<div class="tc-list">' + chips.map(function (c) { return '<span>' + esc(c) + '</span>'; }).join('') + '</div></div>';
  }
  function bookCard(b) {
    var r = bookReadiness(b);
    var ts = bookTopics(b);
    var done = ts.filter(function (t) { return P.isMastered(t.id); }).length;
    var pct = ts.length ? Math.round(done / ts.length * 100) : 0;
    var chips = b.req.map(function (id) {
      var t = MP.byId[id];
      if (!t) return '';
      var ok = P.isMastered(id);
      return '<span class="chip ' + (ok ? 'ok' : 'no') + '" data-id="' + id + '">' +
        esc(t.title) + (ok ? ' ✓' : '') + '</span>';
    }).join('');
    return '<div class="book-card"><h3>第 ' + b.order + ' 本 · ' + b.name + '</h3>' +
      '<div class="book-meta">' + esc(b.sub) + '</div>' +
      '<div class="book-chapters">' + esc(b.chapters) + '</div>' +
      '<div class="book-progress"><div class="bp-row"><span>课程进度 ' + done + ' / ' + ts.length + ' 课</span><b>' + pct + '%</b></div>' +
      '<div class="bp-bar"><i style="width:' + pct + '%"></i></div></div>' +
      '<div class="book-req">入学检查：<b>' + r.ok + '/' + r.total + ' 项前置已掌握（' + r.pct + '%）</b>' +
      (r.pct === 100 ? ' · 可以开读' : ' · 点红色标签直达对应知识点') + '</div>' +
      '<div style="margin-top:7px">' + chips + '</div>' +
      '<div class="book-meta" style="margin:9px 0 0">' + esc(b.note) + '</div>' +
      '<div class="book-start"><button class="btn btn-primary" data-start-book="' + b.id + '">进入这一册 →</button></div></div>';
  }
  function showMap() {
    state.view = 'map'; state.topicId = null; player.pause();
    els.crumb.textContent = '学习地图';
    var rec = P.recommend();
    var d = P.data.diagnostic;
    var diagLine = d
      ? '上次诊断：' + d.score + '/' + d.total + ' 题正确，建议从「' + (MP.byId[d.suggest] || {}).title + '」开始'
      : '建议先做一次入学诊断，系统会判断该从小学、初中还是衔接课开始。';
    els.content.innerHTML = '<div class="wrap">' +
      '<div class="map-hero"><div class="map-eyebrow">MathPath · 系统重建数学基础</div>' +
      '<h1>从小学算术，一路走到微积分</h1>' +
      '<p class="map-lead">这套软件以 1983 年人教版《数学甲种本》为终点，倒推出完整的前置知识链：小学重建算术与图形直觉，初中补齐代数、函数与平面几何，再做六节衔接课，最后进入甲种本六册。</p>' +
      '<p class="lead-note">' + MP.topics.length + ' 个知识点 · ' + MP.units.length + ' 个单元 · 6 本目标课本 · 进度自动保存在本机。甲种本层依课本目录与抽样正文编排，讲解为配套讲义，非课本原文。</p>' +
      '<div class="flow-line">' +
      '<span class="flow-node g">小学 · 算术基本功 ' + P.stats('primary').done + '/' + P.stats('primary').total + '</span>' +
      '<span class="flow-arrow">→</span>' +
      '<span class="flow-node b">初中 · 代数 + 平面几何 ' + P.stats('middle').done + '/' + P.stats('middle').total + '</span>' +
      '<span class="flow-arrow">→</span>' +
      '<span class="flow-node a">甲种本 · 六册</span></div></div>' +
      '<div class="map-rec"><div><div class="rec-k">' + (d ? '为你推荐' : '下一步') + '</div>' +
      '<div class="rec-t">' + esc(rec.title) + '</div>' +
      '<div class="rec-s">' + esc(diagLine) + '</div></div>' +
      '<div style="display:flex;gap:8px;white-space:nowrap"><button class="btn" id="btnGoIndex">课本索引</button>' +
      '<button class="btn btn-primary" id="btnStart">开始这一课 →</button></div></div>' +
      '<div class="map-tracks" id="trackCards">' + MP.TRACKS.map(mapTrackCard).join('') + '</div>' +
      '<h2 class="sec-title" id="books">目标层 · 甲种本六册</h2>' +
      '<p class="sec-sub">六册已按章拆成可逐课学习的知识点。每本给出课程进度、入学检查（读它之前必须掌握的前置，点标签直达）与推荐阅读顺序。</p>' +
      '<div class="book-grid">' + MP.books.slice().sort(function (a, b) { return a.order - b.order; }).map(bookCard).join('') + '</div>' +
      '</div>';

    $('btnStart').onclick = function () { openTopic(rec.id); };
    $('btnGoIndex').onclick = function () { showTextbook(); };
    Array.prototype.forEach.call($('trackCards').querySelectorAll('.track-card'), function (c) {
      c.onclick = function () {
        state.track = c.dataset.track; renderTabs(); renderNav();
        if (state.track !== 'bridge') {
          var first = MP.topics.filter(function (t) { return t.track === state.track; })[0];
          if (first) openTopic(first.id);
        } else {
          var e = $('books'); if (e) e.scrollIntoView({ behavior: 'smooth', block: 'start' });
          toast('六册已按章开课，点每本下方的「进入这一册」开始');
        }
      };
    });
    Array.prototype.forEach.call(els.content.querySelectorAll('[data-start-book]'), function (btn) {
      btn.onclick = function () {
        var b = MP.books.filter(function (x) { return x.id === btn.dataset.startBook; })[0];
        var ts = b ? bookTopics(b) : [];
        if (ts.length) openTopic(ts[0].id);
        else toast('这一册的课程正在编写中');
      };
    });
    Array.prototype.forEach.call(els.content.querySelectorAll('.chip[data-id]'), function (c) {
      c.onclick = function () { openTopic(c.dataset.id); };
    });
    renderChrome();
  }

  /* ---------------- 知识点页 ---------------- */
  function onStep(step, i, total) {
    var host = $('demoStage');
    if (!host || state.view !== 'topic' || !state.topicId) return;
    var t = MP.byId[state.topicId];
    if (!t) return;
    var msg = $('demoMsg'), info = $('demoInfo'), cnt = $('stepCount');
    if (msg) msg.innerHTML = step ? step.msg : '这一课还没有演示';
    if (cnt) cnt.textContent = '第 ' + (total ? i + 1 : 0) + ' / ' + total + ' 步';
    if (info) info.innerHTML = step && step.info ? Object.keys(step.info).map(function (k) {
      return '<span>' + esc(k) + '：' + esc(step.info[k]) + '</span>';
    }).join('') : '';
    var viewHost = $('viewHost');
    if (viewHost) V.render(viewHost, (step && step.data && step.data.view) || t.view, step ? step.data : {});
    var pb = $('playIcon');
    if (pb) pb.innerHTML = player.playing
      ? '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg>'
      : '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5l12 7-12 7z"/></svg>';
  }

  function openTopic(id) {
    var t = MP.byId[id];
    if (!t) return;
    state.view = 'topic'; state.topicId = id; state.seed = 0; state.exOpen = false;
    state.quiz = { answers: t.quiz.map(function () { return null; }), locked: t.quiz.map(function () { return false; }), done: false };
    P.visit(id);
    player.pause();
    var unit = MP.unitById[t.unit] || { name: '' };
    var track = MP.TRACKS.filter(function (x) { return x.id === t.track; })[0] || MP.TRACKS[0];
    var book = unit.book ? MP.books.filter(function (b) { return b.id === unit.book; })[0] : null;
    var place = book ? '第 ' + book.order + ' 本 · ' + book.name + ' / ' + unit.name : track.name + ' · ' + unit.name;
    els.crumb.textContent = book ? '甲种本 · ' + book.name + ' · ' + t.title : track.name + ' · ' + unit.name + ' · ' + t.title;
    state.track = t.track; renderTabs();

    var meta = '<span class="meta-chip">' + esc(place) + '</span>' +
      '<span class="meta-chip">约 ' + t.minutes + ' 分钟</span>' +
      (t.star ? '<span class="meta-chip star">★ 甲种本关键前置</span>' : '') +
      (P.isMastered(id) ? '<span class="meta-chip done">✓ 已掌握</span>' : '');

    els.content.innerHTML = '<div class="wrap">' +
      '<div class="topic-head"><div class="topic-eyebrow">' + esc(place) + '</div>' +
      '<h1 class="topic-title" id="topic-title">' + esc(t.title) + '</h1>' +
      '<p class="topic-sub">' + esc(t.subtitle) + '</p>' +
      '<div class="topic-meta">' + meta + '</div></div>' +
      '<div class="why-box"><b>学习目标：</b>' + esc(t.goal) + '<br><b>为什么学它：</b>' + esc(t.why) + '</div>' +
      textbookCardHtml(t) +

      '<div class="block"><div class="block-head"><span class="bh-num">1</span>分步演示' +
      '<span class="bh-hint">按空格播放 / ←→ 单步</span></div>' +
      '<div class="demo-toolbar"><button class="btn" id="btnReplay">↺ 再看一遍</button>' +
      '<span class="step-label" id="stepCount">第 1 步</span></div>' +
      '<div class="demo-stage" id="demoStage">' +
      '<div class="demo-msg" id="demoMsg"></div><div id="viewHost"></div>' +
      '<div class="demo-info" id="demoInfo"></div></div>' +
      '<div class="demo-ctrl">' +
      '<button class="ctrl-btn" id="cFirst" title="第一步">|◀</button>' +
      '<button class="ctrl-btn" id="cPrev" title="上一步">◀</button>' +
      '<button class="ctrl-btn play" id="cPlay" title="播放/暂停"><span id="playIcon"></span></button>' +
      '<button class="ctrl-btn" id="cNext" title="下一步">▶</button>' +
      '<button class="ctrl-btn" id="cLast" title="最后一步">▶|</button>' +
      '<div class="speed">速度 <input type="range" id="cSpeed" min="0.5" max="3" step="0.5" value="1"><span id="speedVal">1×</span></div>' +
      '</div></div>' +

      '<div class="block"><div class="block-head"><span class="bh-num">2</span>三层讲解</div>' +
      '<div class="note-grid">' + t.notes.map(function (n, i) {
        return '<div class="note-card"><div class="note-k">' + NOTE_KEYS[i] + '</div><div class="note-body">' + n + '</div></div>';
      }).join('') + '</div></div>' +

      (t.example ? '<div class="block"><div class="block-head"><span class="bh-num">3</span>典型例题</div>' +
        '<div class="ex-q">' + esc(t.example.q) + '</div>' +
        '<button class="ex-toggle" id="exToggle">▸ 看解题过程</button>' +
        '<div id="exBody" style="display:none"><ol class="ex-steps">' +
        t.example.steps.map(function (s) { return '<li>' + esc(s) + '</li>'; }).join('') +
        '</ol><div class="ex-ans">答案：' + esc(t.example.a) + '</div></div></div>' : '') +

      '<div class="block"><div class="block-head"><span class="bh-num">4</span>自测 · 全对自动标记掌握' +
      '<span class="bh-hint">' + t.quiz.length + ' 题</span></div><div id="quizBody"></div>' +
      '<div class="quiz-foot"><span class="quiz-score" id="quizScore">全部作答后显示结果</span>' +
      '<button class="btn" id="btnQuizReset" style="margin-left:auto">重做</button></div></div>' +

      '<div class="topic-foot">' + prevNextHtml(t) +
      '<span class="spacer"></span>' +
      '<button class="btn ' + (P.isMastered(id) ? '' : 'btn-ok') + '" id="btnMaster">' +
      (P.isMastered(id) ? '取消已掌握' : '✓ 我已掌握') + '</button>' +
      '<button class="btn btn-primary" id="btnNextTopic">下一课 →</button></div>' +
      '</div>';

    bindTopic(t);
    renderQuiz(t);
    player.load(t.demo(0));
    renderChrome();
    els.content.scrollTop = 0;
  }

  function prevNextHtml(t) {
    var list = MP.orderedTopics(), i = list.indexOf(t), prev = list[i - 1];
    return prev ? '<button class="btn" data-goto="' + prev.id + '">← ' + esc(prev.title) + '</button>' : '';
  }
  function nextTopic(t) {
    var list = MP.orderedTopics(), i = list.indexOf(t);
    return list[i + 1] || P.recommend() || t;
  }

  function bindTopic(t) {
    $('btnReplay').onclick = function () { state.seed++; player.load(t.demo(state.seed)); toast('已回到第一步'); };
    $('cFirst').onclick = function () { player.pause(); player.seek(0); };
    $('cPrev').onclick = function () { player.pause(); player.prev(); };
    $('cNext').onclick = function () { player.pause(); player.next(); };
    $('cLast').onclick = function () { player.pause(); player.seek(player.steps.length - 1); };
    $('cPlay').onclick = function () { player.toggle(); onStep(player.steps[player.i], player.i, player.steps.length); };
    $('cSpeed').oninput = function () {
      player.setSpeed(parseFloat(this.value));
      $('speedVal').textContent = this.value + '×';
    };
    var ex = $('exToggle');
    if (ex) ex.onclick = function () {
      state.exOpen = !state.exOpen;
      $('exBody').style.display = state.exOpen ? '' : 'none';
      ex.textContent = state.exOpen ? '▾ 收起解题过程' : '▸ 看解题过程';
    };
    $('btnQuizReset').onclick = function () {
      state.quiz = { answers: t.quiz.map(function () { return null; }), locked: t.quiz.map(function () { return false; }), done: false };
      renderQuiz(t);
    };
    $('btnMaster').onclick = function () {
      var on = !P.isMastered(t.id);
      P.master(t.id, on);
      toast(on ? '已标记为掌握 ✓' : '已取消掌握标记');
      renderChrome(); openTopic(t.id);
    };
    $('btnNextTopic').onclick = function () { openTopic(nextTopic(t).id); };
    Array.prototype.forEach.call(els.content.querySelectorAll('[data-goto]'), function (b) {
      b.onclick = function () { openTopic(b.dataset.goto); };
    });
  }

  /* ---------------- 自测 ---------------- */
  function renderQuiz(t) {
    var host = $('quizBody');
    if (!host) return;
    var q = state.quiz;
    host.innerHTML = t.quiz.map(function (item, i) {
      var opts = (item.options || []).map(function (o, j) {
        var cls = 'quiz-opt';
        if (q.locked[i]) {
          if (j === item.answer) cls += ' right';
          else if (q.answers[i] === j) cls += ' wrong';
        } else if (q.answers[i] === j) cls += ' sel';
        return '<button class="' + cls + '" data-q="' + i + '" data-o="' + j + '">' + esc(o) + '</button>';
      }).join('');
      var input = item.options ? '' :
        '<input class="quiz-input" data-input="' + i + '" placeholder="填写答案" value="' + esc(q.answers[i] == null ? '' : q.answers[i]) + '">' +
        '<button class="btn" data-submit="' + i + '">确定</button>';
      var ok = q.locked[i] && isRight(item, q.answers[i]);
      var ex = q.locked[i]
        ? '<div class="quiz-explain show ' + (ok ? 'ok' : 'no') + '">' +
          (ok ? '✓ 正确。' : '✗ 正确答案：' + esc(item.options ? item.options[item.answer] : item.answer) + '。') +
          ' ' + esc(item.explain || '') + '</div>' : '';
      return '<div class="quiz-item"><div class="quiz-q">' + (i + 1) + '. ' + esc(item.q) + '</div>' +
        '<div class="quiz-opts">' + opts + input + '</div>' + ex + '</div>';
    }).join('');

    Array.prototype.forEach.call(host.querySelectorAll('[data-o]'), function (b) {
      b.onclick = function () {
        var i = +b.dataset.q;
        if (q.locked[i]) return;
        q.answers[i] = +b.dataset.o; q.locked[i] = true;
        renderQuiz(t); checkAll(t);
      };
    });
    Array.prototype.forEach.call(host.querySelectorAll('[data-submit]'), function (b) {
      b.onclick = function () {
        var i = +b.dataset.submit;
        var inp = host.querySelector('[data-input="' + i + '"]');
        q.answers[i] = (inp.value || '').trim(); q.locked[i] = true;
        renderQuiz(t); checkAll(t);
      };
    });
    if (q.done) {
      var ok = t.quiz.filter(function (item, i) { return isRight(item, q.answers[i]); }).length;
      $('quizScore').innerHTML = '得分 <b>' + ok + ' / ' + t.quiz.length + '</b>' +
        (ok === t.quiz.length ? ' · 已自动标记掌握 ✓' : ' · 错题已收进错题本');
    } else {
      $('quizScore').textContent = '全部作答后显示结果';
    }
  }
  function isRight(item, a) {
    if (item.options) return a === item.answer;
    if (a == null) return false;
    var want = Array.isArray(item.answer) ? item.answer : [item.answer];
    return want.some(function (w) { return String(w).trim().toLowerCase() === String(a).trim().toLowerCase(); });
  }
  function checkAll(t) {
    var q = state.quiz;
    if (!q.locked.every(Boolean) || q.done) return;
    q.done = true;
    var results = t.quiz.map(function (item, i) {
      return { ok: isRight(item, q.answers[i]), q: item.q,
               answer: item.options ? item.options[item.answer] : item.answer,
               yours: item.options ? (item.options[q.answers[i]] || '') : q.answers[i] };
    });
    var r = P.recordQuiz(t.id, results);
    renderQuiz(t); renderChrome();
    toast(r.ok === r.total ? '全对！已标记掌握 ✓' : '得 ' + r.ok + '/' + r.total + '，错题已记录');
  }

  /* ---------------- 入学诊断 ---------------- */
  var DIAG_IDS = ['p-add', 'p-frac-reduce', 'p-ratio', 'p-letter', 'p-factor',
                  'm-rational', 'm-factor', 'm-eq2', 'm-ineq', 'm-linear-fn',
                  'm-quad-fn', 'm-trig', 'm-similar', 'm-frac-expr'];
  function diagQuestions() {
    return DIAG_IDS.map(function (id) {
      var t = MP.byId[id];
      return t && t.quiz && t.quiz[0] ? { id: id, t: t, q: t.quiz[0] } : null;
    }).filter(Boolean);
  }
  function showDiagnostic() {
    state.view = 'diag'; state.topicId = null; player.pause();
    els.crumb.textContent = '入学诊断';
    var qs = diagQuestions();
    state.diag = { answers: qs.map(function () { return null; }), submitted: false };
    var prev = P.data.diagnostic;
    els.content.innerHTML = '<div class="wrap">' +
      '<div class="map-hero"><div class="map-eyebrow">起点定位</div><h1>入学诊断</h1>' +
      '<p class="map-lead">' + qs.length + ' 道题，覆盖小学与初中最关键的 ' + qs.length + ' 个前置知识点。不计时，做错也没关系 —— 目的是判断该从哪一层开始，避免直接从甲种本硬啃。</p></div>' +
      (prev ? '<div class="diag-result"><h3>上次结果：' + prev.score + ' / ' + prev.total + '</h3>' +
        '<p>建议起点：' + esc((MP.byId[prev.suggest] || {}).title || '小学第一课') +
        (prev.weak.length ? ' · 薄弱单元：' + prev.weak.map(function (u) { return esc((MP.unitById[u] || {}).name || u); }).join('、') : '') + '</p></div>' : '') +
      '<div id="diagResult"></div>' +
      qs.map(function (x, i) {
        return '<div class="diag-q"><div class="dq-t"><span class="dq-tag">' + (x.t.track === 'primary' ? '小学' : '初中') + ' · ' + esc(x.t.title) + '</span>' +
          esc(x.q.q) + '</div><div class="quiz-opts">' +
          x.q.options.map(function (o, j) {
            return '<button class="quiz-opt" data-dq="' + i + '" data-do="' + j + '">' + esc(o) + '</button>';
          }).join('') + '</div></div>';
      }).join('') +
      '<div style="margin-top:16px"><button class="btn btn-primary" id="diagSubmit">提交并生成学习建议</button></div></div>';

    Array.prototype.forEach.call(els.content.querySelectorAll('[data-dq]'), function (b) {
      b.onclick = function () {
        var i = +b.dataset.dq;
        state.diag.answers[i] = +b.dataset.do;
        Array.prototype.forEach.call(els.content.querySelectorAll('[data-dq="' + i + '"]'), function (x) { x.classList.remove('sel'); });
        b.classList.add('sel');
      };
    });
    $('diagSubmit').onclick = function () {
      var d = state.diag;
      var primary = qs.filter(function (x) { return x.t.track === 'primary'; });
      var middle = qs.filter(function (x) { return x.t.track !== 'primary'; });
      function score(list) {
        return list.filter(function (x) { return d.answers[qs.indexOf(x)] === x.q.answer; }).length;
      }
      var pOk = score(primary), mOk = score(middle), total = pOk + mOk;
      var weak = {}, weakList = [];
      qs.forEach(function (x, i) {
        if (d.answers[i] !== x.q.answer) {
          weak[x.t.unit] = 1;
          P.data.wrong.unshift({ id: x.id, q: x.q.q, answer: x.q.options[x.q.answer],
                                 yours: x.q.options[d.answers[i]] || '未作答', ts: Date.now() });
        }
      });
      for (var u in weak) weakList.push(u);
      P.data.wrong = P.data.wrong.slice(0, 60);
      var suggest;
      if (pOk < primary.length - 1) suggest = 'p-place';
      else if (mOk < middle.length * 0.7) {
        suggest = weakList.length && MP.byId[DIAG_IDS[qs.findIndex(function (x) { return x.t.unit === weakList[0]; })]] ? DIAG_IDS[qs.findIndex(function (x) { return x.t.unit === weakList[0]; })] : 'm-rational';
      } else suggest = 'b-angle-rad';
      P.data.diagnostic = { score: total, total: qs.length, pOk: pOk, pTotal: primary.length,
                            mOk: mOk, mTotal: middle.length, weak: weakList, suggest: suggest, ts: Date.now() };
      P.save();
      var advice = pOk < primary.length - 1
        ? '小学算术还有缺口，建议从小学第一单元开始。甲种本里几乎所有卡壳，最后都能追到分数、比例或字母表示数。'
        : mOk < middle.length * 0.7
          ? '小学基础扎实，但初中代数/几何还有薄弱项。建议先补下面列出的单元，再进衔接课。'
          : '前置知识基本齐了。可以直接做六节衔接课，然后开读《代数 第一册》。';
      $('diagResult').innerHTML = '<div class="diag-result"><h3>' + total + ' / ' + qs.length + ' 题正确（小学 ' + pOk + '/' + primary.length + '，初中 ' + mOk + '/' + middle.length + '）</h3>' +
        '<p>' + advice + '</p>' +
        (weakList.length ? '<p>需要复习：' + weakList.map(function (u) { return esc((MP.unitById[u] || {}).name || u); }).join('、') + '</p>' : '') +
        '<p style="margin-top:10px"><button class="btn btn-primary" id="diagGo">按建议开始 → ' + esc((MP.byId[suggest] || {}).title || '') + '</button></p></div>';
      $('diagGo').onclick = function () { openTopic(suggest); };
      renderChrome();
      $('diagResult').scrollIntoView({ behavior: 'smooth', block: 'start' });
    };
    renderChrome();
    els.content.scrollTop = 0;
  }

  /* ---------------- 错题本 ---------------- */
  function showWrong() {
    state.view = 'wrong'; state.topicId = null; player.pause();
    els.crumb.textContent = '错题本';
    var list = P.data.wrong || [];
    els.content.innerHTML = '<div class="wrap"><div class="map-hero"><div class="map-eyebrow">复习</div>' +
      '<h1>错题本</h1><p class="map-lead">自测和诊断里做错的题会收集到这里。点「去复习」回到对应知识点重看演示并重做。</p></div>' +
      (list.length ? list.map(function (w) {
        var t = MP.byId[w.id];
        return '<div class="wrong-item"><div class="wrong-q">' + esc(w.q) + '</div>' +
          '<div class="wrong-a">你的答案：' + esc(w.yours) + ' · 正确答案：<b>' + esc(w.answer) + '</b>' +
          (t ? ' · 来自「' + esc(t.title) + '」' : '') + '</div>' +
          (t ? '<div style="margin-top:9px"><button class="btn" data-fix="' + t.id + '">去复习 →</button></div>' : '') + '</div>';
      }).join('') : '<div class="empty">还没有错题。去做一次入学诊断，或随便挑一课做自测吧。</div>') +
      (list.length ? '<div style="margin-top:16px"><button class="btn" id="btnClearWrong">清空错题本</button></div>' : '') +
      '</div>';
    Array.prototype.forEach.call(els.content.querySelectorAll('[data-fix]'), function (b) {
      b.onclick = function () { openTopic(b.dataset.fix); };
    });
    var c = $('btnClearWrong');
    if (c) c.onclick = function () { P.data.wrong = []; P.save(); showWrong(); toast('错题本已清空'); };
    renderChrome();
    els.content.scrollTop = 0;
  }

  /* ---------------- 全局事件 ---------------- */
  $('btnMap').onclick = function () { showMap(); closeSidebar(); };
  $('btnDiag').onclick = function () { showDiagnostic(); closeSidebar(); };
  $('btnWrong').onclick = function () { showWrong(); closeSidebar(); };
  $('btnIndex').onclick = function () { showTextbook(); closeSidebar(); };
  $('menuBtn').onclick = function () { els.sidebar.classList.toggle('open'); };
  $('btnReset').onclick = function () {
    if (!window.confirm('确定清空全部学习记录吗？已掌握标记、测验成绩、诊断结果和错题本都会删除，且无法恢复。')) return;
    P.reset(); state.quiz = null; state.diag = null;
    showMap(); toast('进度已重置');
  };
  document.addEventListener('keydown', function (e) {
    if (state.view !== 'topic') return;
    var tag = (e.target && e.target.tagName) || '';
    if (tag === 'INPUT' || tag === 'TEXTAREA') return;
    if (e.key === ' ') { e.preventDefault(); player.toggle(); onStep(player.steps[player.i], player.i, player.steps.length); }
    else if (e.key === 'ArrowRight') { e.preventDefault(); player.pause(); player.next(); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); player.pause(); player.prev(); }
    else if (e.key === 'Escape') showMap();
  });

  /* ---------------- 启动 ---------------- */
  renderChrome();
  var qs = '';
  try { qs = location.search || ''; } catch (e) { qs = ''; }
  var qTopic = (function () {
    var m = qs.match(/[?&]topic=([^&]+)/);
    try { return m ? decodeURIComponent(m[1]) : null; } catch (e) { return null; }
  })();
  var qView = (function () { var m = qs.match(/[?&]view=([^&]+)/); return m ? m[1] : null; })();
  if (qView === 'diagnostic') showDiagnostic();
  else if (qView === 'wrong') showWrong();
  else if (qView === 'index') showTextbook();
  else if (qTopic && MP.byId[qTopic]) openTopic(qTopic);
  else if (P.data.current && MP.byId[P.data.current] && /[?&]resume=1/.test(qs)) openTopic(P.data.current);
  else showMap();

  window.__mathPath = { state: state, player: player, showMap: showMap, openTopic: openTopic,
                        showDiagnostic: showDiagnostic, showWrong: showWrong, showTextbook: showTextbook,
                        progress: P, topics: MP.topics };
})();
