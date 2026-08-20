/**
 * 受付 TO DO — LINE で送るだけでスプレッドシートに貯まる仕組み
 *
 * LINE公式アカウントに送ったメッセージを、その月のシートに1行追加します。
 * 「一覧」「完了 12」などのコマンドにも対応。
 *
 * セットアップ手順は docs/LINE_TODO_SETUP.md を参照。
 */

const PROPS = PropertiesService.getScriptProperties();

/**
 * 設定の読み取り。スクリプトプロパティを優先し、なければ Config.gs の CONFIG を使う。
 * Config.gs は tools/setup_line_todo.py が自動生成します。
 */
function conf_(key) {
  const v = PROPS.getProperty(key);
  if (v) return v;
  if (typeof CONFIG !== 'undefined' && CONFIG[key]) return CONFIG[key];
  return '';
}

const HEADERS = ['登録日時', '種別', 'やること', '期限', '目安時間', 'メモ', '完了', '登録者'];
const COL = { AT: 1, KIND: 2, TASK: 3, DUE: 4, SPAN: 5, NOTE: 6, DONE: 7, BY: 8 };

const KINDS = ['院長から', '受付から', '定例'];
const SPANS = ['5分', '15分', '30分以上'];

const KIND_TAGS = {
  '院長': '院長から', '院長から': '院長から', '先生': '院長から',
  '受付': '受付から', '自分': '受付から',
  '定例': '定例', '毎月': '定例',
};
const SPAN_TAGS = {
  '5分': '5分', '5': '5分',
  '15分': '15分', '15': '15分',
  '30分': '30分以上', '30分以上': '30分以上', '30': '30分以上',
};

const TZ = 'Asia/Tokyo';

/* ------------------------------------------------------------------ */
/* Webhook                                                             */
/* ------------------------------------------------------------------ */

function doPost(e) {
  try {
    const body = JSON.parse(e.postData.contents);
    (body.events || []).forEach(function (ev) {
      try {
        handleEvent_(ev);
      } catch (err) {
        console.error('event error: ' + err + '\n' + (err && err.stack));
        if (ev && ev.replyToken) {
          reply_(ev.replyToken, 'エラーが起きて登録できませんでした。少し時間をおいて、もう一度送ってください。');
        }
      }
    });
  } catch (err) {
    console.error('doPost error: ' + err);
  }
  return ContentService
    .createTextOutput(JSON.stringify({ status: 'ok' }))
    .setMimeType(ContentService.MimeType.JSON);
}

function doGet() {
  return ContentService.createTextOutput('受付TODO webhook is running.');
}

function handleEvent_(ev) {
  if (ev.type === 'follow') {
    reply_(ev.replyToken, usageText_(ev.source.userId));
    return;
  }
  if (ev.type !== 'message' || !ev.message || ev.message.type !== 'text') return;

  const userId = ev.source.userId || '';
  if (!isAllowed_(userId)) {
    reply_(ev.replyToken,
      'このアカウントはまだ登録されていません。\n' +
      '下のIDを管理者に伝えて、登録してもらってください。\n\n' + userId);
    return;
  }

  const text = String(ev.message.text || '').trim();
  if (!text) return;

  const head = text.split(/\s+/)[0];

  if (/^(ヘルプ|使い方|help)$/i.test(head)) {
    reply_(ev.replyToken, usageText_(userId));
    return;
  }
  if (/^(一覧|リスト|list|todo)$/i.test(head)) {
    reply_(ev.replyToken, listText_());
    return;
  }
  const m = text.match(/^(完了|済|done|取消|戻す|削除)\s*[#＃]?\s*(\d+)$/i);
  if (m) {
    reply_(ev.replyToken, applyCommand_(m[1], Number(m[2]), displayName_(userId)));
    return;
  }

  reply_(ev.replyToken, addTask_(text, displayName_(userId)));
}

/* ------------------------------------------------------------------ */
/* 追加・更新                                                          */
/* ------------------------------------------------------------------ */

function addTask_(text, by) {
  const parsed = parseText_(text);
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const sh = monthSheet_(new Date());
    const row = sh.getLastRow() + 1;
    sh.getRange(row, COL.AT).setValue(new Date());
    sh.getRange(row, COL.KIND).setValue(parsed.kind);
    sh.getRange(row, COL.TASK).setValue(parsed.task);
    if (parsed.due) sh.getRange(row, COL.DUE).setValue(parsed.due);
    if (parsed.span) sh.getRange(row, COL.SPAN).setValue(parsed.span);
    if (parsed.note) sh.getRange(row, COL.NOTE).setValue(parsed.note);
    sh.getRange(row, COL.DONE).setValue(false);
    sh.getRange(row, COL.BY).setValue(by);
    styleRow_(sh, row);

    const bits = ['#' + row + '　' + parsed.task, '種別：' + parsed.kind];
    if (parsed.due) bits.push('期限：' + fmtDate_(parsed.due));
    if (parsed.span) bits.push('目安：' + parsed.span);
    if (parsed.note) bits.push('メモ：' + parsed.note);
    return '追加しました。\n' + bits.join('\n');
  } finally {
    lock.releaseLock();
  }
}

function applyCommand_(cmd, row, by) {
  const sh = monthSheet_(new Date());
  if (row < 2 || row > sh.getLastRow()) {
    return '#' + row + ' は見つかりませんでした。「一覧」で番号を確認してください。';
  }
  const task = sh.getRange(row, COL.TASK).getValue();
  if (/^(完了|済|done)$/i.test(cmd)) {
    sh.getRange(row, COL.DONE).setValue(true);
    return '完了にしました。\n#' + row + '　' + task;
  }
  if (/^(取消|戻す)$/.test(cmd)) {
    sh.getRange(row, COL.DONE).setValue(false);
    return '未完了に戻しました。\n#' + row + '　' + task;
  }
  sh.deleteRow(row);
  return '削除しました。\n' + task + '\n（以降の番号がひとつずつ繰り上がります）';
}

function listText_() {
  const sh = monthSheet_(new Date());
  const last = sh.getLastRow();
  if (last < 2) return '未完了はありません。';

  const values = sh.getRange(2, 1, last - 1, HEADERS.length).getValues();
  const lines = [];
  values.forEach(function (v, i) {
    if (v[COL.DONE - 1] === true) return;
    const row = i + 2;
    let line = '#' + row + '　' + v[COL.TASK - 1];
    const tail = [];
    if (v[COL.KIND - 1] === '院長から') tail.push('院長');
    if (v[COL.DUE - 1]) tail.push(fmtDate_(v[COL.DUE - 1]) + 'まで');
    if (v[COL.SPAN - 1]) tail.push(v[COL.SPAN - 1]);
    if (tail.length) line += '（' + tail.join('・') + '）';
    lines.push(line);
  });

  if (!lines.length) return '未完了はありません。';
  const head = '未完了 ' + lines.length + '件（' + sh.getName() + '）';
  const shown = lines.slice(0, 20);
  const more = lines.length > 20 ? '\n…ほか ' + (lines.length - 20) + '件' : '';
  return head + '\n\n' + shown.join('\n') + more + '\n\n終わったら「完了 番号」と送ってください。';
}

/* ------------------------------------------------------------------ */
/* 文面の解釈                                                          */
/* ------------------------------------------------------------------ */

/**
 * 1行目＝やること、2行目以降＝メモ。
 * #院長 #5分 のようなタグと、「8/25まで」「明日まで」などの期限を拾う。
 */
function parseText_(text) {
  const lines = text.split(/\r?\n/);
  let first = lines[0];
  const note = lines.slice(1).join('\n').trim();

  let kind = '受付から';
  let span = '';

  first = first.replace(/[#＃]([^\s#＃]+)/g, function (all, tag) {
    if (KIND_TAGS[tag]) { kind = KIND_TAGS[tag]; return ''; }
    if (SPAN_TAGS[tag]) { span = SPAN_TAGS[tag]; return ''; }
    return all;
  });

  const due = extractDue_(first);
  if (due.matched) first = first.replace(due.matched, '');

  const task = first.replace(/\s+/g, ' ').trim() || '(内容なし)';
  return { kind: kind, task: task, due: due.date, span: span, note: note };
}

function extractDue_(text) {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

  let m = text.match(/(今日|本日)(まで|中)?/);
  if (m) return { date: today, matched: m[0] };

  m = text.match(/明日(まで|中)?/);
  if (m) return { date: addDays_(today, 1), matched: m[0] };

  m = text.match(/明後日(まで|中)?/);
  if (m) return { date: addDays_(today, 2), matched: m[0] };

  m = text.match(/(\d{1,2})[\/月](\d{1,2})日?(まで)?/);
  if (m) {
    const mo = Number(m[1]);
    const d = Number(m[2]);
    let y = today.getFullYear();
    const cand = new Date(y, mo - 1, d);
    // 過ぎた日付は翌年とみなす（12月に「1/5」と書く場合）
    if (cand < addDays_(today, -30)) cand.setFullYear(y + 1);
    return { date: cand, matched: m[0] };
  }

  m = text.match(/(\d{1,2})日(まで)?/);
  if (m) {
    const d = Number(m[1]);
    const cand = new Date(today.getFullYear(), today.getMonth(), d);
    if (cand < today) cand.setMonth(cand.getMonth() + 1);
    return { date: cand, matched: m[0] };
  }

  return { date: null, matched: '' };
}

function addDays_(d, n) {
  const x = new Date(d.getTime());
  x.setDate(x.getDate() + n);
  return x;
}

function fmtDate_(d) {
  return Utilities.formatDate(new Date(d), TZ, 'M/d');
}

/* ------------------------------------------------------------------ */
/* シート                                                              */
/* ------------------------------------------------------------------ */

function spreadsheet_() {
  const id = conf_('SPREADSHEET_ID');
  return id ? SpreadsheetApp.openById(id) : SpreadsheetApp.getActiveSpreadsheet();
}

function monthSheet_(date) {
  const ss = spreadsheet_();
  const name = Utilities.formatDate(date, TZ, 'yyyy年M月');
  let sh = ss.getSheetByName(name);
  if (sh) return sh;

  sh = ss.insertSheet(name, 0);
  sh.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS])
    .setFontWeight('bold').setFontColor('#ffffff').setBackground('#0f5f55')
    .setHorizontalAlignment('center');
  sh.setFrozenRows(1);
  [140, 90, 380, 90, 90, 260, 60, 100].forEach(function (w, i) {
    sh.setColumnWidth(i + 1, w);
  });
  sh.getRange('A:A').setNumberFormat('M/d HH:mm');
  sh.getRange('D:D').setNumberFormat('yyyy/M/d');
  sh.setTabColor('#0f5f55');

  const max = sh.getMaxRows();
  sh.getRange(2, COL.KIND, max - 1, 1).setDataValidation(
    SpreadsheetApp.newDataValidation().requireValueInList(KINDS, true).build());
  sh.getRange(2, COL.SPAN, max - 1, 1).setDataValidation(
    SpreadsheetApp.newDataValidation().requireValueInList(SPANS, true).build());
  sh.getRange(2, COL.DONE, max - 1, 1).insertCheckboxes();

  const body = sh.getRange(2, 1, max - 1, HEADERS.length);
  sh.setConditionalFormatRules([
    SpreadsheetApp.newConditionalFormatRule()
      .whenFormulaSatisfied('=$G2=TRUE')
      .setFontColor('#95a5a1').setStrikethrough(true)
      .setRanges([body]).build(),
    SpreadsheetApp.newConditionalFormatRule()
      .whenFormulaSatisfied('=AND($D2<>"",$D2<TODAY(),$G2=FALSE)')
      .setBackground('#fce9e6').setFontColor('#c0392b')
      .setRanges([body]).build(),
    SpreadsheetApp.newConditionalFormatRule()
      .whenFormulaSatisfied('=AND($B2="院長から",$G2=FALSE)')
      .setBackground('#fbf0dc')
      .setRanges([body]).build(),
  ]);
  return sh;
}

function styleRow_(sh, row) {
  sh.getRange(row, COL.TASK).setWrap(true);
  sh.getRange(row, COL.NOTE).setWrap(true);
  sh.getRange(row, COL.AT).setNumberFormat('M/d HH:mm');
  sh.getRange(row, COL.DUE).setNumberFormat('yyyy/M/d');
}

/* ------------------------------------------------------------------ */
/* LINE API                                                            */
/* ------------------------------------------------------------------ */

function token_() {
  const t = conf_('LINE_CHANNEL_ACCESS_TOKEN');
  if (!t) throw new Error('LINE_CHANNEL_ACCESS_TOKEN が未設定です（Config.gs またはスクリプトプロパティ）');
  return t;
}

function reply_(replyToken, text) {
  if (!replyToken) return;
  UrlFetchApp.fetch('https://api.line.me/v2/bot/message/reply', {
    method: 'post',
    contentType: 'application/json',
    headers: { Authorization: 'Bearer ' + token_() },
    payload: JSON.stringify({
      replyToken: replyToken,
      messages: [{ type: 'text', text: String(text).slice(0, 4900) }],
    }),
    muteHttpExceptions: true,
  });
}

function push_(userId, text) {
  UrlFetchApp.fetch('https://api.line.me/v2/bot/message/push', {
    method: 'post',
    contentType: 'application/json',
    headers: { Authorization: 'Bearer ' + token_() },
    payload: JSON.stringify({
      to: userId,
      messages: [{ type: 'text', text: String(text).slice(0, 4900) }],
    }),
    muteHttpExceptions: true,
  });
}

function displayName_(userId) {
  if (!userId) return '';
  const cache = CacheService.getScriptCache();
  const hit = cache.get('name_' + userId);
  if (hit) return hit;
  try {
    const res = UrlFetchApp.fetch('https://api.line.me/v2/bot/profile/' + userId, {
      headers: { Authorization: 'Bearer ' + token_() },
      muteHttpExceptions: true,
    });
    const name = JSON.parse(res.getContentText()).displayName || '';
    if (name) cache.put('name_' + userId, name, 21600);
    return name;
  } catch (err) {
    return '';
  }
}

function allowedIds_() {
  return (conf_('ALLOWED_USER_IDS') || '')
    .split(',').map(function (s) { return s.trim(); }).filter(String);
}

function isAllowed_(userId) {
  const ids = allowedIds_();
  return ids.length === 0 || ids.indexOf(userId) >= 0;
}

/* ------------------------------------------------------------------ */
/* 毎朝のリマインド（時間主導型トリガーで daily を実行）               */
/* ------------------------------------------------------------------ */

function daily() {
  const ids = allowedIds_();
  if (!ids.length) return;
  const text = listText_();
  ids.forEach(function (id) { push_(id, 'おはようございます。\n' + text); });
}

/* ------------------------------------------------------------------ */

function usageText_(userId) {
  return [
    '受付TODOです。思いついたことをそのまま送ってください。1通が1件になります。',
    '',
    '【書き方】',
    '・そのまま送る → 受付からのタスクとして登録',
    '・#院長 を付ける → 院長からの依頼',
    '・#5分 #15分 #30分 → 空き時間の目安',
    '・「8/25まで」「明日まで」→ 期限',
    '・改行して2行目以降を書くと、メモになります',
    '',
    '【コマンド】',
    '一覧 … 今月の未完了を表示',
    '完了 12 … 番号のタスクを完了に',
    '戻す 12 … 未完了に戻す',
    '削除 12 … 削除',
    '',
    'あなたのID：' + (userId || '(取得できませんでした)'),
  ].join('\n');
}
