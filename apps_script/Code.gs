/**
 * CLAUDENOTE Team TODO - Google Apps Script Backend
 *
 * Deploy as a Web App (Execute as: Me, Access: Anyone with the link or domain).
 * The script reads/writes two sheets in the bound spreadsheet:
 *   - "Tasks"     : id | title | assignee | due | status | priority | tags | createdAt | updatedAt | createdBy
 *   - "Comments"  : id | taskId | author | body | createdAt
 */

const TASKS_SHEET = 'Tasks';
const COMMENTS_SHEET = 'Comments';

const TASK_HEADERS = [
  'id', 'title', 'necessity', 'assignee', 'due', 'status',
  'priority', 'tags', 'createdAt', 'updatedAt', 'createdBy'
];
const COMMENT_HEADERS = ['id', 'taskId', 'author', 'body', 'createdAt'];

const DEFAULT_STATUSES = ['未着手', '進行中', 'レビュー', '完了'];

function doGet(e) {
  return handle_(e, 'GET');
}

function doPost(e) {
  return handle_(e, 'POST');
}

function handle_(e, method) {
  try {
    ensureSheets_();
    const params = e && e.parameter ? e.parameter : {};
    let payload = {};
    if (method === 'POST' && e.postData && e.postData.contents) {
      payload = JSON.parse(e.postData.contents);
    }
    const action = (payload.action || params.action || 'list').toString();

    let result;
    switch (action) {
      case 'list':       result = listAll_(); break;
      case 'createTask': result = createTask_(payload); break;
      case 'updateTask': result = updateTask_(payload); break;
      case 'deleteTask': result = deleteTask_(payload); break;
      case 'addComment': result = addComment_(payload); break;
      case 'meta':       result = meta_(); break;
      default:
        throw new Error('Unknown action: ' + action);
    }
    return json_({ ok: true, data: result });
  } catch (err) {
    return json_({ ok: false, error: err.message || String(err) });
  }
}

function json_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function ss_() {
  return SpreadsheetApp.getActiveSpreadsheet();
}

function ensureSheets_() {
  const ss = ss_();
  ensureSheet_(ss, TASKS_SHEET, TASK_HEADERS);
  ensureSheet_(ss, COMMENTS_SHEET, COMMENT_HEADERS);
}

function ensureSheet_(ss, name, headers) {
  let sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
    sh.getRange(1, 1, 1, headers.length).setValues([headers]);
    sh.setFrozenRows(1);
    return;
  }
  const lastCol = Math.max(sh.getLastColumn(), headers.length);
  const current = sh.getRange(1, 1, 1, lastCol).getValues()[0];
  let needs = false;
  for (let i = 0; i < headers.length; i++) {
    if (current[i] !== headers[i]) { needs = true; break; }
  }
  if (needs) {
    sh.getRange(1, 1, 1, headers.length).setValues([headers]);
    sh.setFrozenRows(1);
  }
}

function rowsAsObjects_(sh, headers) {
  const lastRow = sh.getLastRow();
  if (lastRow < 2) return [];
  const values = sh.getRange(2, 1, lastRow - 1, headers.length).getValues();
  return values.map(row => {
    const obj = {};
    headers.forEach((h, i) => { obj[h] = row[i]; });
    obj.__row = null;
    return obj;
  }).filter(o => o.id !== '' && o.id !== null && o.id !== undefined)
    .map((o, idx) => { o.__row = idx + 2; return o; });
}

function listAll_() {
  const ss = ss_();
  const tasks = rowsAsObjects_(ss.getSheetByName(TASKS_SHEET), TASK_HEADERS)
    .map(normalizeTask_);
  const comments = rowsAsObjects_(ss.getSheetByName(COMMENTS_SHEET), COMMENT_HEADERS)
    .map(normalizeComment_);
  return { tasks, comments, meta: meta_() };
}

function normalizeTask_(t) {
  return {
    id: String(t.id),
    title: String(t.title || ''),
    necessity: String(t.necessity || ''),
    assignee: String(t.assignee || ''),
    due: t.due ? Utilities.formatDate(new Date(t.due), Session.getScriptTimeZone(), 'yyyy-MM-dd') : '',
    status: String(t.status || DEFAULT_STATUSES[0]),
    priority: String(t.priority || '中'),
    tags: String(t.tags || ''),
    createdAt: t.createdAt ? new Date(t.createdAt).toISOString() : '',
    updatedAt: t.updatedAt ? new Date(t.updatedAt).toISOString() : '',
    createdBy: String(t.createdBy || '')
  };
}

function normalizeComment_(c) {
  return {
    id: String(c.id),
    taskId: String(c.taskId),
    author: String(c.author || ''),
    body: String(c.body || ''),
    createdAt: c.createdAt ? new Date(c.createdAt).toISOString() : ''
  };
}

function findTaskRow_(taskId) {
  const sh = ss_().getSheetByName(TASKS_SHEET);
  const tasks = rowsAsObjects_(sh, TASK_HEADERS);
  const found = tasks.find(t => String(t.id) === String(taskId));
  if (!found) throw new Error('Task not found: ' + taskId);
  return { sheet: sh, row: found.__row, task: found };
}

function uuid_() {
  return Utilities.getUuid();
}

function createTask_(p) {
  const sh = ss_().getSheetByName(TASKS_SHEET);
  const now = new Date();
  const id = uuid_();
  const row = [
    id,
    String(p.title || '').trim() || '(無題)',
    String(p.necessity || ''),
    String(p.assignee || ''),
    p.due || '',
    String(p.status || DEFAULT_STATUSES[0]),
    String(p.priority || '中'),
    String(p.tags || ''),
    now,
    now,
    String(p.createdBy || p.author || '')
  ];
  sh.appendRow(row);
  return { id };
}

function updateTask_(p) {
  if (!p.id) throw new Error('id is required');
  const { sheet, row } = findTaskRow_(p.id);
  const editable = ['title', 'necessity', 'assignee', 'due', 'status', 'priority', 'tags'];
  editable.forEach(field => {
    if (p[field] !== undefined) {
      const col = TASK_HEADERS.indexOf(field) + 1;
      sheet.getRange(row, col).setValue(p[field]);
    }
  });
  const updatedCol = TASK_HEADERS.indexOf('updatedAt') + 1;
  sheet.getRange(row, updatedCol).setValue(new Date());
  return { id: p.id };
}

function deleteTask_(p) {
  if (!p.id) throw new Error('id is required');
  const { sheet, row } = findTaskRow_(p.id);
  sheet.deleteRow(row);
  const cSh = ss_().getSheetByName(COMMENTS_SHEET);
  const comments = rowsAsObjects_(cSh, COMMENT_HEADERS);
  for (let i = comments.length - 1; i >= 0; i--) {
    if (String(comments[i].taskId) === String(p.id)) {
      cSh.deleteRow(comments[i].__row);
    }
  }
  return { id: p.id };
}

function addComment_(p) {
  if (!p.taskId) throw new Error('taskId is required');
  if (!p.body) throw new Error('body is required');
  const sh = ss_().getSheetByName(COMMENTS_SHEET);
  const id = uuid_();
  const now = new Date();
  sh.appendRow([id, String(p.taskId), String(p.author || ''), String(p.body), now]);
  const tSh = ss_().getSheetByName(TASKS_SHEET);
  const { row } = findTaskRow_(p.taskId);
  tSh.getRange(row, TASK_HEADERS.indexOf('updatedAt') + 1).setValue(now);
  return { id };
}

function meta_() {
  const props = PropertiesService.getScriptProperties();
  const staffRaw = props.getProperty('STAFF') || '';
  const tagsRaw = props.getProperty('TAGS') || '';
  const statusesRaw = props.getProperty('STATUSES') || DEFAULT_STATUSES.join(',');
  const prioritiesRaw = props.getProperty('PRIORITIES') || '高,中,低';
  return {
    staff: staffRaw.split(',').map(s => s.trim()).filter(Boolean),
    tags: tagsRaw.split(',').map(s => s.trim()).filter(Boolean),
    statuses: statusesRaw.split(',').map(s => s.trim()).filter(Boolean),
    priorities: prioritiesRaw.split(',').map(s => s.trim()).filter(Boolean)
  };
}
