/* 完整 UI 回归：NODE_PATH=/tmp/al-check/node_modules node test/dom-test.js */
'use strict';
const { JSDOM } = require('jsdom');
const path = require('path');
const file = path.resolve(__dirname, '..', 'index.html');
const errors = [];

JSDOM.fromFile(file, {
  runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true,
  url: 'file://' + file
}).then(dom => {
  const { window } = dom;
  const doc = window.document;
  window.Element.prototype.scrollIntoView = function () {};
  window.addEventListener('error', e => errors.push('window.error: ' + e.message));
  const origErr = window.console.error;
  window.console.error = function (...a) { errors.push('console.error: ' + a.map(String).join(' ')); origErr.apply(window.console, a); };

  window.addEventListener('load', () => setTimeout(run, 350));

  function run() {
    if (!window.__mathPath) { console.log('FATAL: app.js 未初始化'); process.exit(1); }
    const MP = window.MathPath, api = window.__mathPath;
    const $ = id => doc.getElementById(id);
    let bad = 0, checks = 0;
    const report = [];
    function ck(cond, msg) { checks++; if (!cond) { bad++; report.push(msg); } }

    /* 1. 首页地图 */
    ck($('trackCards').querySelectorAll('.track-card').length === 3, '地图应有三张学段卡');
    ck(doc.querySelectorAll('.book-card').length === 6, '地图应列出六本甲种本');
    ck(!!$('btnStart'), '地图应有开始按钮');
    ck(doc.querySelectorAll('.book-card .chip[data-id]').length > 30, '入学检查标签应完整');

    /* 2. 遍历全部知识点 */
    MP.topics.forEach(t => {
      const before = errors.length;
      let issues = [];
      try {
        api.openTopic(t.id);
      } catch (e) { issues.push('openTopic 抛错: ' + e.message); }

      const title = document_title();
      function document_title() { return $('topic-title') ? $('topic-title').textContent : ''; }
      if (!title || title !== t.title) issues.push('标题不符: ' + title);
      if (!$('demoMsg') || !$('demoMsg').textContent.trim()) issues.push('演示说明为空');
      if (!$('viewHost') || !$('viewHost').children.length) issues.push('视图未渲染');
      if (!$('stepCount') || !/第 \d+ \/ \d+ 步/.test($('stepCount').textContent)) issues.push('步骤计数异常');
      if (doc.querySelectorAll('#quizBody .quiz-item').length !== t.quiz.length) issues.push('自测题数量不符');
      if (!$('btnNextTopic')) issues.push('缺下一课按钮');

      /* 探针步骤 */
      const total = api.player.steps.length;
      [0, Math.floor(total / 2), total - 1].forEach(i => {
        try { api.player.seek(i); } catch (e) { issues.push('seek(' + i + ') 抛错: ' + e.message); }
        if (!$('viewHost') || !$('viewHost').children.length) issues.push('step' + i + ' 视图为空');
        if (!$('demoMsg').textContent.trim()) issues.push('step' + i + ' 说明为空');
      });

      /* 例题展开 */
      if ($('exToggle')) {
        try {
          $('exToggle').click();
          if ($('exBody').style.display === 'none') issues.push('例题未展开');
        } catch (e) { issues.push('例题交互抛错: ' + e.message); }
      }

      /* 全部答对 -> 自动掌握 */
      t.quiz.forEach((q, i) => {
        const btn = doc.querySelector('[data-q="' + i + '"][data-o="' + q.answer + '"]');
        if (!btn) { issues.push('第 ' + i + ' 题缺正确选项'); return; }
        try { btn.click(); } catch (e) { issues.push('答题抛错: ' + e.message); }
      });
      if (!MP.progress.isMastered(t.id)) issues.push('全对后未标记掌握');
      if (!$('quizScore').textContent.includes('/')) issues.push('未显示得分');

      const newErrs = errors.slice(before);
      if (newErrs.length) issues.push('运行时错误: ' + newErrs.join(' | '));
      if (issues.length) report.push('【' + t.id + '】' + issues.join('；'));
      bad += issues.length;
      checks += 12;
    });

    /* 3. 诊断 */
    api.showDiagnostic();
    const dqs = doc.querySelectorAll('[data-dq]');
    ck(dqs.length >= 14 * 2, '诊断题选项不足');
    const groups = {};
    dqs.forEach(b => { groups[b.dataset.dq] = (groups[b.dataset.dq] || 0) + 1; });
    const diagCount = Object.keys(groups).length;
    ck(diagCount === 14, '诊断题数应为 14，实际 ' + diagCount);
    /* 全部选第一个选项（不保证对，但必须能提交） */
    Object.keys(groups).forEach(i => {
      const b = doc.querySelector('[data-dq="' + i + '"][data-do="0"]');
      if (b) b.click();
    });
    try { $('diagSubmit').click(); } catch (e) { report.push('诊断提交抛错: ' + e.message); bad++; }
    ck(!!$('diagResult').textContent.trim(), '诊断未生成建议');
    ck(!!MP.progress.data.diagnostic, '诊断结果未保存');
    ck(!!$('diagGo'), '诊断缺少按建议开始按钮');

    /* 4. 错题本 */
    api.showWrong();
    ck($('crumb').textContent === '错题本', '错题本面包屑异常');
    ck(doc.querySelectorAll('.wrong-item').length > 0, '错题本应有错题');
    ck(!!doc.querySelector('[data-fix]'), '错题本缺少去复习按钮');

    /* 5. 回到地图，进度应更新 */
    api.showMap();
    ck($('footPct').textContent === '100%', '全部掌握后总进度应为 100%，实际 ' + $('footPct').textContent);
    ck(doc.querySelectorAll('.chip.ok').length > 0, '入学检查应有已掌握标签');
    ck($('crumb').textContent === '学习地图', '地方面包屑异常');

    /* 6. 标记 / 取消掌握 */
    api.openTopic('p-place');
    $('btnMaster').click();
    ck(!MP.progress.isMastered('p-place'), '取消掌握失败');
    $('btnMaster').click();
    ck(MP.progress.isMastered('p-place'), '重新标记掌握失败');

    /* 7. 课本对照索引 */
    api.showTextbook();
    ck($('crumb').textContent === '课本对照索引', '索引页面包屑异常');
    ck(doc.querySelectorAll('.block').length >= 7, '索引页应列出六册与教参');
    ck(doc.querySelectorAll('.idx-ch').length > 0, '索引页应有章条目');
    ck(!!(window.MathPath.TEXTBOOK_INDEX && Object.keys(window.MathPath.TEXTBOOK_INDEX).length >= 6), '索引数据应覆盖六册');
    api.openTopic('a1-set');
    ck(!!doc.querySelector('.tb-card'), '甲种本知识点页应显示课本依据卡片');
    api.openTopic('p-add');
    ck(!doc.querySelector('.tb-card'), '小学知识点页不应显示课本依据卡片');

    console.log('检查点 ' + checks + ' 个，遍历知识点 ' + MP.topics.length + ' 个，运行时错误 ' + errors.length + ' 条');
    if (errors.length) errors.slice(0, 8).forEach(e => console.log('  ! ' + e));
    if (bad) {
      console.log('问题 ' + bad + ' 项：');
      report.slice(0, 30).forEach(r => console.log('  - ' + r));
      process.exit(1);
    }
    console.log('DOM 全量回归通过 ✓');
  }
}).catch(e => { console.log('FATAL', e); process.exit(1); });
