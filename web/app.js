/* CLAUDENOTE Team TODO - Frontend */
(() => {
  const LS_API_URL = 'claudenote.todo.apiUrl';
  const LS_USER = 'claudenote.todo.user';

  const state = {
    apiUrl: localStorage.getItem(LS_API_URL) || '',
    user: localStorage.getItem(LS_USER) || '',
    tasks: [],
    comments: [],
    meta: { staff: [], tags: [], statuses: ['未着手', '進行中', 'レビュー', '完了'], priorities: ['高', '中', '低'] },
    filter: { text: '', assignee: '', tag: '' },
    editingId: null,
  };

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  // ===== API =====
  async function api(action, payload = {}) {
    if (!state.apiUrl) {
      throw new Error('API URLが未設定です。⚙ 設定から登録してください。');
    }
    const res = await fetch(state.apiUrl, {
      method: 'POST',
      body: JSON.stringify({ action, ...payload }),
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || 'unknown error');
    return data.data;
  }

  function setConn(msg, cls) {
    const el = $('#connStatus');
    el.textContent = msg;
    el.className = 'conn-status ' + (cls || '');
  }

  async function reload() {
    if (!state.apiUrl) {
      setConn('未接続（⚙ から設定）', 'err');
      return;
    }
    setConn('読み込み中...', '');
    try {
      const data = await api('list');
      state.tasks = data.tasks || [];
      state.comments = data.comments || [];
      state.meta = Object.assign(state.meta, data.meta || {});
      setConn('接続OK · ' + new Date().toLocaleTimeString('ja-JP'), 'ok');
      render();
    } catch (err) {
      setConn('エラー: ' + err.message, 'err');
      console.error(err);
    }
  }

  // ===== Render =====
  function render() {
    renderFilters();
    renderBoard();
    renderDatalists();
  }

  function renderFilters() {
    const assignees = uniqueNonEmpty(state.tasks.map(t => t.assignee).concat(state.meta.staff));
    const tags = uniqueNonEmpty(flatTags(state.tasks).concat(state.meta.tags));
    fillSelect($('#filterAssignee'), '担当者: すべて', assignees, state.filter.assignee);
    fillSelect($('#filterTag'), 'タグ: すべて', tags, state.filter.tag);
  }

  function renderDatalists() {
    const staffList = $('#staffList');
    const tagList = $('#tagList');
    const assignees = uniqueNonEmpty(state.tasks.map(t => t.assignee).concat(state.meta.staff));
    const tags = uniqueNonEmpty(flatTags(state.tasks).concat(state.meta.tags));
    staffList.innerHTML = assignees.map(a => `<option value="${esc(a)}">`).join('');
    tagList.innerHTML = tags.map(t => `<option value="${esc(t)}">`).join('');
  }

  function fillSelect(el, placeholder, items, current) {
    el.innerHTML = `<option value="">${placeholder}</option>` +
      items.map(v => `<option value="${esc(v)}"${v === current ? ' selected' : ''}>${esc(v)}</option>`).join('');
  }

  function renderBoard() {
    const board = $('#board');
    board.innerHTML = '';
    const statuses = state.meta.statuses;
    const filtered = state.tasks.filter(taskMatchesFilter);

    for (const status of statuses) {
      const col = document.createElement('section');
      col.className = 'column';
      col.dataset.status = status;
      const tasksHere = filtered.filter(t => t.status === status);
      col.innerHTML = `
        <div class="column-header">
          <span>${esc(status)}</span>
          <span class="column-count">${tasksHere.length}</span>
        </div>
        <div class="column-body" data-dropzone></div>
      `;
      const body = col.querySelector('.column-body');
      for (const t of tasksHere) body.appendChild(renderCard(t));

      const addBtn = document.createElement('button');
      addBtn.className = 'add-card-btn';
      addBtn.textContent = '＋ このステータスに追加';
      addBtn.onclick = () => openTaskModal(null, { status });
      body.appendChild(addBtn);

      attachDropzone(col);
      board.appendChild(col);
    }
  }

  function renderCard(task) {
    const card = document.createElement('div');
    card.className = 'card priority-' + (task.priority || '中');
    card.draggable = true;
    card.dataset.id = task.id;

    const due = task.due;
    const overdue = due && due < todayStr() && task.status !== '完了';
    const tags = (task.tags || '').split(',').map(s => s.trim()).filter(Boolean);

    card.innerHTML = `
      <div class="card-title">${esc(task.title)}</div>
      ${task.necessity ? `<div class="card-necessity">${esc(task.necessity)}</div>` : ''}
      <div class="card-meta">
        ${task.assignee ? `<span class="chip assignee">👤 ${esc(task.assignee)}</span>` : ''}
        ${due ? `<span class="chip due${overdue ? ' overdue' : ''}">📅 ${esc(due)}</span>` : ''}
        ${task.priority ? `<span class="chip priority-${esc(task.priority)}">${esc(task.priority)}</span>` : ''}
        ${tags.map(t => `<span class="chip tag">#${esc(t)}</span>`).join('')}
      </div>
    `;
    card.onclick = () => openTaskModal(task.id);
    card.addEventListener('dragstart', (e) => {
      e.dataTransfer.setData('text/plain', task.id);
      e.dataTransfer.effectAllowed = 'move';
    });
    return card;
  }

  function attachDropzone(col) {
    col.addEventListener('dragover', (e) => {
      e.preventDefault();
      col.classList.add('drag-over');
    });
    col.addEventListener('dragleave', () => col.classList.remove('drag-over'));
    col.addEventListener('drop', async (e) => {
      e.preventDefault();
      col.classList.remove('drag-over');
      const id = e.dataTransfer.getData('text/plain');
      const newStatus = col.dataset.status;
      const task = state.tasks.find(t => t.id === id);
      if (!task || task.status === newStatus) return;
      const prev = task.status;
      task.status = newStatus;
      renderBoard();
      try {
        await api('updateTask', { id, status: newStatus });
        if (state.user) {
          await api('addComment', {
            taskId: id,
            author: state.user,
            body: `ステータスを「${prev}」→「${newStatus}」に変更しました`,
          });
        }
      } catch (err) {
        task.status = prev;
        renderBoard();
        alert('更新失敗: ' + err.message);
      }
    });
  }

  function taskMatchesFilter(t) {
    const f = state.filter;
    if (f.assignee && t.assignee !== f.assignee) return false;
    if (f.tag) {
      const tags = (t.tags || '').split(',').map(s => s.trim());
      if (!tags.includes(f.tag)) return false;
    }
    if (f.text) {
      const hay = `${t.title} ${t.necessity} ${t.assignee} ${t.tags}`.toLowerCase();
      if (!hay.includes(f.text.toLowerCase())) return false;
    }
    return true;
  }

  // ===== Task Modal =====
  function openTaskModal(id, defaults = {}) {
    state.editingId = id;
    const modal = $('#modal');
    const form = $('#taskForm');
    form.reset();
    const task = id ? state.tasks.find(t => t.id === id) : null;

    // Populate selects
    fillFormSelect(form.status, state.meta.statuses);
    fillFormSelect(form.priority, state.meta.priorities);

    if (task) {
      $('#modalTitle').textContent = 'タスク詳細';
      form.id.value = task.id;
      form.title.value = task.title;
      form.necessity.value = task.necessity || '';
      form.assignee.value = task.assignee;
      form.due.value = task.due;
      form.status.value = task.status;
      form.priority.value = task.priority || '中';
      form.tags.value = task.tags;
      $('#deleteBtn').classList.remove('hidden');
      $('#commentsSection').classList.remove('hidden');
      renderComments(task.id);
    } else {
      $('#modalTitle').textContent = '新規タスク';
      form.id.value = '';
      form.status.value = defaults.status || state.meta.statuses[0];
      form.priority.value = '中';
      $('#deleteBtn').classList.add('hidden');
      $('#commentsSection').classList.add('hidden');
    }
    modal.classList.remove('hidden');
    form.title.focus();
  }

  function fillFormSelect(el, items) {
    el.innerHTML = items.map(v => `<option value="${esc(v)}">${esc(v)}</option>`).join('');
  }

  function closeModal() {
    $('#modal').classList.add('hidden');
    $('#settingsModal').classList.add('hidden');
    state.editingId = null;
  }

  function renderComments(taskId) {
    const list = $('#commentList');
    const items = state.comments
      .filter(c => c.taskId === taskId)
      .sort((a, b) => (a.createdAt > b.createdAt ? 1 : -1));
    list.innerHTML = items.map(c => `
      <li>
        <div class="comment-meta">${esc(c.author || '名無し')} · ${formatDateTime(c.createdAt)}</div>
        <div>${esc(c.body)}</div>
      </li>
    `).join('') || '<li style="color:#9ca3af">まだコメントはありません</li>';
  }

  // ===== Event handlers =====
  function bind() {
    $('#addBtn').onclick = () => openTaskModal(null);
    $('#reloadBtn').onclick = reload;
    $('#settingsBtn').onclick = () => {
      $('#apiUrlInput').value = state.apiUrl;
      $('#settingsModal').classList.remove('hidden');
    };
    $('#saveSettingsBtn').onclick = () => {
      const url = $('#apiUrlInput').value.trim();
      state.apiUrl = url;
      localStorage.setItem(LS_API_URL, url);
      closeModal();
      reload();
    };
    $$('[data-close]').forEach(b => b.onclick = closeModal);
    [$('#modal'), $('#settingsModal')].forEach(m => {
      m.addEventListener('click', (e) => { if (e.target === m) closeModal(); });
    });

    $('#userName').value = state.user;
    $('#userName').addEventListener('input', (e) => {
      state.user = e.target.value;
      localStorage.setItem(LS_USER, state.user);
    });

    $('#filterText').addEventListener('input', (e) => {
      state.filter.text = e.target.value;
      renderBoard();
    });
    $('#filterAssignee').addEventListener('change', (e) => {
      state.filter.assignee = e.target.value;
      renderBoard();
    });
    $('#filterTag').addEventListener('change', (e) => {
      state.filter.tag = e.target.value;
      renderBoard();
    });

    $('#taskForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const fd = new FormData(e.target);
      const payload = Object.fromEntries(fd.entries());
      payload.tags = (payload.tags || '').split(',').map(s => s.trim()).filter(Boolean).join(', ');
      try {
        if (payload.id) {
          await api('updateTask', payload);
        } else {
          payload.createdBy = state.user;
          await api('createTask', payload);
        }
        closeModal();
        reload();
      } catch (err) {
        alert('保存失敗: ' + err.message);
      }
    });

    $('#deleteBtn').onclick = async () => {
      const id = state.editingId;
      if (!id) return;
      if (!confirm('このタスクを削除します。よろしいですか？')) return;
      try {
        await api('deleteTask', { id });
        closeModal();
        reload();
      } catch (err) {
        alert('削除失敗: ' + err.message);
      }
    };

    $('#commentForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const id = state.editingId;
      if (!id) return;
      const body = e.target.body.value.trim();
      if (!body) return;
      try {
        await api('addComment', { taskId: id, author: state.user, body });
        e.target.reset();
        const data = await api('list');
        state.comments = data.comments || [];
        renderComments(id);
      } catch (err) {
        alert('コメント投稿失敗: ' + err.message);
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeModal();
    });
  }

  // ===== Utilities =====
  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function uniqueNonEmpty(arr) {
    return [...new Set(arr.map(x => (x || '').toString().trim()).filter(Boolean))].sort();
  }
  function flatTags(tasks) {
    return tasks.flatMap(t => (t.tags || '').split(',').map(s => s.trim())).filter(Boolean);
  }
  function todayStr() {
    const d = new Date();
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  }
  function pad(n) { return String(n).padStart(2, '0'); }
  function formatDateTime(iso) {
    if (!iso) return '';
    try {
      const d = new Date(iso);
      return d.toLocaleString('ja-JP', { dateStyle: 'short', timeStyle: 'short' });
    } catch { return iso; }
  }

  // ===== Boot =====
  bind();
  if (!state.apiUrl) {
    setConn('未接続（⚙ から設定）', 'err');
    $('#settingsModal').classList.remove('hidden');
    $('#apiUrlInput').focus();
  } else {
    reload();
  }
  // Auto refresh every 60s
  setInterval(() => { if (state.apiUrl && !document.hidden) reload(); }, 60000);
})();
