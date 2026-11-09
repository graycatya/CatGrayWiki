/* 内容结构校验：node test/check-content.js */
'use strict';
global.window = {};
require('../js/core.js');
require('../js/views.js');
require('../js/course-primary.js');
require('../js/course-middle.js');
require('../js/course-bridge.js');
require('../js/course-alg.js');
require('../js/course-geo.js');
require('../js/course-calc.js');

var MP = window.MathPath;
var EXPECT = {
  bars: ['values'], fraction: ['rows'], grid: ['cells', 'cols'], steps: ['lines'],
  numberline: ['points', 'segments', 'ticks'], axis: ['range', 'curves', 'points', 'lines', 'rects', 'polys'],
  shapes: ['items'], tree: ['nodes', 'edges']
};
var problems = [];
function fail(s) { problems.push(s); }

var byTrack = {};
MP.topics.forEach(function (t) {
  byTrack[t.track] = (byTrack[t.track] || 0) + 1;
  ['id', 'unit', 'title', 'subtitle', 'goal', 'why', 'view', 'demo'].forEach(function (k) {
    if (!t[k]) fail(t.id + ': 缺字段 ' + k);
  });
  if (!MP.unitById[t.unit]) fail(t.id + ': 单元不存在 ' + t.unit);
  if (t.notes.length !== 3) fail(t.id + ': 讲解不是三段');
  if (!t.example || !t.example.q || !t.example.steps || !t.example.a) fail(t.id + ': 例题不完整');
  if (!t.quiz || t.quiz.length < 2) fail(t.id + ': 自测题不足 2 道');
  t.quiz.forEach(function (q, j) {
    if (!q.q || !q.explain) fail(t.id + '#' + j + ': 题目或解析缺失');
    if (q.options) {
      if (!(q.answer >= 0 && q.answer < q.options.length)) fail(t.id + '#' + j + ': 答案索引越界');
    } else if (q.answer == null) fail(t.id + '#' + j + ': 缺答案');
  });
  (t.prereq || []).forEach(function (p) { if (!MP.byId[p]) fail(t.id + ': 前置不存在 ' + p); });

  [0, 1].forEach(function (seed) {
    var steps;
    try { steps = t.demo(seed); }
    catch (e) { fail(t.id + ': demo(' + seed + ') 抛错 ' + e.message); return; }
    if (!steps || steps.length < 3) { fail(t.id + ': 演示步骤不足 3 步'); return; }
    steps.forEach(function (s, i) {
      if (!s || typeof s.msg !== 'string' || !s.msg.trim()) fail(t.id + '#' + i + ': 步骤说明缺失');
      var d = s.data || {};
      var v = d.view || t.view;
      if (!MP.views[v]) { fail(t.id + '#' + i + ': 未知视图 ' + v); return; }
      var keys = EXPECT[v] || [];
      if (!keys.some(function (k) { return d[k] != null; })) {
        fail(t.id + '#' + i + ': ' + v + ' 视图缺少数据键 (' + keys.join('/') + ')');
      }
      if (d.caption != null && typeof d.caption !== 'string') fail(t.id + '#' + i + ': caption 非字符串');
    });
  });
});

var ids = {};
MP.topics.forEach(function (t) { if (ids[t.id]) fail('重复 id: ' + t.id); ids[t.id] = 1; });
MP.books.forEach(function (b) {
  if (!b.chapters || !b.note || !b.order) fail('课本字段不完整: ' + b.id);
  (b.req || []).forEach(function (r) { if (!MP.byId[r]) fail('课本 ' + b.id + ' 引用不存在: ' + r); });
  var us = MP.units.filter(function (u) { return u.book === b.id; });
  if (!us.length) fail('课本 ' + b.id + ' 没有任何章节单元');
  var ids = {}; us.forEach(function (u) { ids[u.id] = 1; });
  var ts = MP.topics.filter(function (t) { return ids[t.unit]; });
  if (ts.length < 5) fail('课本 ' + b.id + ' 课程太少: ' + ts.length);
  us.forEach(function (u) {
    if (!MP.topicsOf(u.id).length) fail('章节单元为空: ' + u.id);
  });
});
var order = MP.orderedTopics();
if (order.length !== MP.topics.length) fail('学习顺序丢失知识点');
for (var i = 1; i < order.length; i++) {
  if (MP.topicRank(order[i]) < MP.topicRank(order[i - 1])) fail('学习顺序未按学段/册序排列: ' + order[i].id);
}

console.log('知识点 ' + MP.topics.length + ' 个：' + JSON.stringify(byTrack));
console.log('单元 ' + MP.units.length + ' 个，目标课本 ' + MP.books.length + ' 本，自测题 ' +
  MP.topics.reduce(function (a, t) { return a + t.quiz.length; }, 0) + ' 道');
if (problems.length) {
  console.log('发现 ' + problems.length + ' 个问题：');
  problems.slice(0, 40).forEach(function (p) { console.log('  - ' + p); });
  process.exit(1);
}
console.log('内容校验全部通过 ✓');
