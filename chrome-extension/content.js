/**
 * LINE Official Account Manager / chat.line.biz 拡張:
 *  ・入力欄の隣に常時表示される「✨」ボタン
 *    → 返信欄に書いたメモを本人の文体で清書し、返信欄を置き換える
 *  ・サイドパネル:
 *    🚀 一括学習 (チャット一覧を自動巡回して最大1000件学習)
 *    📚 この会話を学習 (1件ずつ手動)
 *    ✏️ 手動下書き生成（メモを直接書いて生成）
 */

(function () {
  const PANEL_ID = "stella-reply-panel";
  const INLINE_BTN_ID = "stella-inline-btn";
  const STORAGE_SAMPLES_KEY = "stellaStyleSamples";
  const MAX_SAMPLES_IN_PROMPT = 5;
  const MAX_STORED_SAMPLES = 80;
  const BULK_TARGET = 1000;
  const BULK_WAIT_MS = 1800;

  if (document.getElementById(PANEL_ID)) return;

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  let bulkRunning = false;
  let bulkCancel = false;

  // ============================================================
  // サイドパネル UI
  // ============================================================
  const panel = document.createElement("div");
  panel.id = PANEL_ID;
  panel.innerHTML = `
    <div class="stella-header">
      <span>✨ AI返信下書き</span>
      <span class="stella-sample-count" title="学習済みサンプル数">📚 0</span>
      <button class="stella-toggle" title="折りたたみ">＿</button>
    </div>
    <div class="stella-body">
      <div class="stella-actions-top">
        <button class="stella-btn-bulk">🚀 一括学習 (最大1000件)</button>
        <button class="stella-btn-learn" title="今開いているチャットだけを学習">📚 この会話を学習</button>
      </div>
      <div class="stella-bulk-progress" style="display:none;">
        <div class="stella-bulk-text">準備中…</div>
        <button class="stella-btn-bulk-cancel">🛑 中止</button>
      </div>
      <hr/>
      <div class="stella-hint">
        💡 通常の使い方:<br/>
        LINEの返信欄にメモ（例:「6・11 10時半」）を書いて、入力欄右上の <b>✨</b> を押すと、本人の文体で清書して返信欄を置き換えます。
      </div>
      <details class="stella-manual">
        <summary>✏️ 手動でメモから生成する</summary>
        <div class="stella-manual-body">
          <button class="stella-btn-capture">📋 現在の会話を読み取る</button>
          <textarea class="stella-context" placeholder="会話履歴（自動取得・必要なら編集）"></textarea>
          <textarea class="stella-memo" placeholder="返信メモ（例: 6・11 10時半 / キャンセル可 / 変更可いつでも）"></textarea>
          <button class="stella-btn-generate">✨ 下書きを生成</button>
          <textarea class="stella-output" placeholder="生成結果がここに" readonly></textarea>
          <div class="stella-actions">
            <button class="stella-btn-copy">📋 コピー</button>
            <button class="stella-btn-insert">▶ 返信欄に挿入</button>
            <button class="stella-btn-clear">🗑 クリア</button>
          </div>
        </div>
      </details>
      <div class="stella-status"></div>
    </div>
  `;
  document.body.appendChild(panel);

  const toggleBtn = panel.querySelector(".stella-toggle");
  const body = panel.querySelector(".stella-body");
  toggleBtn.addEventListener("click", () => {
    const hidden = body.style.display === "none";
    body.style.display = hidden ? "flex" : "none";
    toggleBtn.textContent = hidden ? "＿" : "▢";
  });

  const sampleCountEl = panel.querySelector(".stella-sample-count");
  const statusEl = panel.querySelector(".stella-status");

  function setStatus(msg, type) {
    statusEl.textContent = msg;
    statusEl.className = "stella-status " + (type || "");
  }
  function setBulkProgress(msg) {
    panel.querySelector(".stella-bulk-text").textContent = msg;
  }

  async function refreshSampleCount() {
    const samples = await loadSamples();
    sampleCountEl.textContent = `📚 ${samples.length}`;
  }
  refreshSampleCount();

  // ============================================================
  // 会話読み取り
  // ============================================================
  function findChatContainer() {
    const candidates = [
      '[data-testid="chat-list"]',
      '[class*="ChatList"]',
      '[class*="messageList"]',
      '[class*="MessageList"]',
      '[role="log"]',
    ];
    for (const sel of candidates) {
      const el = document.querySelector(sel);
      if (el && el.innerText && el.innerText.length > 50) return el;
    }
    let best = null, bestLen = 0;
    for (const el of document.querySelectorAll("div")) {
      const style = getComputedStyle(el);
      if ((style.overflowY === "auto" || style.overflowY === "scroll") &&
          el.innerText && el.innerText.length > bestLen) {
        bestLen = el.innerText.length;
        best = el;
      }
    }
    return best;
  }

  function extractMessages(container) {
    const rect = container.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const all = container.querySelectorAll(
      "li, [class*='message'], [class*='Message'], [class*='bubble'], [class*='Bubble']"
    );
    const messages = [];
    const seen = new Set();
    for (const el of all) {
      const text = (el.innerText || "").trim();
      if (!text || text.length < 1 || text.length > 2000) continue;
      if (seen.has(text)) continue;
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) continue;
      const elCenter = r.left + r.width / 2;
      const from = elCenter > centerX ? "self" : "other";
      messages.push({ text, from, top: r.top });
      seen.add(text);
    }
    messages.sort((a, b) => a.top - b.top);
    return messages.map(({ text, from }) => ({ text, from }));
  }

  function captureConversation() {
    const container = findChatContainer();
    if (!container) return { error: "会話エリアが見つかりませんでした。" };
    const messages = extractMessages(container);
    if (messages.length === 0) {
      const text = container.innerText.trim();
      const lines = text.split("\n").map((l) => l.trim()).filter(Boolean);
      return { history: lines.join("\n"), count: lines.length };
    }
    const history = messages
      .map((m) => `[${m.from === "self" ? "本人" : "相手"}] ${m.text}`)
      .join("\n");
    return { history, count: messages.length };
  }

  // ============================================================
  // 学習サンプル永続化
  // ============================================================
  async function loadSamples() {
    return new Promise((resolve) => {
      chrome.storage.local.get([STORAGE_SAMPLES_KEY], (data) => {
        resolve(data[STORAGE_SAMPLES_KEY] || []);
      });
    });
  }
  async function saveSamples(samples) {
    return new Promise((resolve) => {
      chrome.storage.local.set({ [STORAGE_SAMPLES_KEY]: samples }, resolve);
    });
  }
  async function addSample(historyText) {
    const samples = await loadSamples();
    samples.push({ at: Date.now(), text: historyText.slice(0, 4000) });
    while (samples.length > MAX_STORED_SAMPLES) samples.shift();
    await saveSamples(samples);
  }

  // ============================================================
  // 一括学習 (チャット一覧を自動巡回)
  // ============================================================
  function findChatList() {
    const direct = [
      '[data-testid="chat-list"]',
      '[class*="ChatList"]',
      '[class*="chatList"]',
      '[role="list"]',
    ];
    for (const sel of direct) {
      const el = document.querySelector(sel);
      if (el && el.children && el.children.length >= 3) return el;
    }
    // ヒューリスティック: 左半分にあって、スクロール可能で、似た高さの行が多いコンテナ
    const viewportCenter = window.innerWidth / 2;
    let best = null, bestScore = 0;
    for (const el of document.querySelectorAll("div, ul, ol")) {
      const r = el.getBoundingClientRect();
      if (r.left > viewportCenter) continue;
      if (r.width < 150 || r.width > viewportCenter + 120) continue;
      if (r.height < 200) continue;
      const style = getComputedStyle(el);
      if (style.overflowY !== "auto" && style.overflowY !== "scroll") continue;
      const children = Array.from(el.children);
      if (children.length < 5) continue;
      const heights = children.map((c) => c.getBoundingClientRect().height);
      heights.sort((a, b) => a - b);
      const median = heights[Math.floor(heights.length / 2)];
      if (median < 40 || median > 140) continue;
      const similar = heights.filter((h) => Math.abs(h - median) < 12).length;
      if (similar > bestScore) {
        bestScore = similar;
        best = el;
      }
    }
    return best;
  }

  function getChatItems(chatList) {
    let items = Array.from(chatList.children);
    // ラッパーが1段挟まっているケースに対応
    if (items.length < 5 && items[0] && items[0].children && items[0].children.length >= 5) {
      items = Array.from(items[0].children);
    }
    return items.filter((el) => {
      const r = el.getBoundingClientRect();
      return r.height >= 30 && r.height <= 160 && r.width > 100;
    });
  }

  /**
   * ユーザーに1件目のチャットをクリックしてもらい、
   * クリックされた要素から「チャット一覧」コンテナを推定する。
   */
  async function pickChatItem() {
    return new Promise((resolve) => {
      document.body.style.cursor = "crosshair";
      const overlay = document.createElement("div");
      overlay.id = "stella-pick-overlay";
      overlay.textContent = "📍 チャット一覧から1件目のチャットをクリックしてください（Escでキャンセル）";
      document.body.appendChild(overlay);

      const cleanup = () => {
        document.body.style.cursor = "";
        overlay.remove();
        document.removeEventListener("click", onClick, true);
        document.removeEventListener("keydown", onKey, true);
      };
      const onClick = (e) => {
        if (e.target.closest(`#${PANEL_ID}`)) return;
        if (e.target.id === "stella-pick-overlay") return;
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        cleanup();
        resolve(e.target);
      };
      const onKey = (e) => {
        if (e.key === "Escape") {
          cleanup();
          resolve(null);
        }
      };
      document.addEventListener("click", onClick, true);
      document.addEventListener("keydown", onKey, true);
    });
  }

  /**
   * クリックされた子孫要素から親を辿って「兄弟が似た高さで並ぶリスト」を探す
   */
  function inferChatListFromClick(clicked) {
    let el = clicked;
    while (el && el.parentElement && el !== document.body) {
      const parent = el.parentElement;
      const siblings = Array.from(parent.children);
      if (siblings.length >= 3) {
        const heights = siblings
          .map((s) => s.getBoundingClientRect().height)
          .filter((h) => h > 0);
        if (heights.length >= 3) {
          const sorted = [...heights].sort((a, b) => a - b);
          const median = sorted[Math.floor(sorted.length / 2)];
          const similar = heights.filter((h) => Math.abs(h - median) < 14).length;
          if (similar >= 3 && median >= 30 && median <= 260) {
            return { chatList: parent, chatItem: el };
          }
        }
      }
      el = parent;
    }
    return { chatList: null, chatItem: null };
  }

  async function bulkLearn() {
    if (bulkRunning) return setStatus("すでに一括学習中です。", "error");

    setStatus("📍 チャット一覧から1件目のチャットをクリックしてください…", "info");
    panel.querySelector(".stella-btn-bulk").disabled = true;

    const clicked = await pickChatItem();
    if (!clicked) {
      setStatus("キャンセルしました", "info");
      panel.querySelector(".stella-btn-bulk").disabled = false;
      return;
    }

    const { chatList, chatItem } = inferChatListFromClick(clicked);
    if (!chatList || !chatItem) {
      setStatus("チャット一覧の構造を検出できませんでした。別の場所をクリックしてみてください。", "error");
      panel.querySelector(".stella-btn-bulk").disabled = false;
      return;
    }

    bulkRunning = true;
    bulkCancel = false;
    panel.querySelector(".stella-bulk-progress").style.display = "flex";

    try {
      // 1件目: クリックされたチャットを開く
      chatItem.scrollIntoView({ block: "center" });
      chatItem.click();
      await sleep(BULK_WAIT_MS);

      let totalMessages = 0;
      let chatProcessed = 0;
      let scrollAttempts = 0;
      const visited = new WeakSet();
      visited.add(chatItem);

      const tryCapture = async () => {
        const result = captureConversation();
        if (!result.error && result.history && result.history.length > 30) {
          await addSample(result.history);
          totalMessages += result.count || 0;
          chatProcessed++;
          await refreshSampleCount();
        }
        setBulkProgress(
          `学習中: ${chatProcessed}チャット / ${totalMessages}メッセージ (目標 ${BULK_TARGET})`
        );
      };

      await tryCapture();

      while (totalMessages < BULK_TARGET && !bulkCancel) {
        const items = Array.from(chatList.children).filter((el) => {
          const r = el.getBoundingClientRect();
          return r.height >= 30 && r.height <= 260 && r.width > 80;
        });
        const next = items.find((el) => !visited.has(el));
        if (!next) {
          if (scrollAttempts >= 5) break;
          chatList.scrollTop = chatList.scrollHeight;
          await sleep(1200);
          scrollAttempts++;
          continue;
        }
        scrollAttempts = 0;
        visited.add(next);
        next.scrollIntoView({ block: "center" });
        next.click();
        await sleep(BULK_WAIT_MS);
        await tryCapture();
      }

      if (bulkCancel) {
        setStatus(`中止しました（${chatProcessed}チャット、${totalMessages}メッセージ学習済み）`, "info");
      } else {
        setStatus(`✅ 完了: ${chatProcessed}チャットから${totalMessages}件のメッセージを学習しました`, "ok");
      }
    } finally {
      bulkRunning = false;
      panel.querySelector(".stella-bulk-progress").style.display = "none";
      panel.querySelector(".stella-btn-bulk").disabled = false;
      await refreshSampleCount();
    }
  }

  panel.querySelector(".stella-btn-bulk").addEventListener("click", bulkLearn);
  panel.querySelector(".stella-btn-bulk-cancel").addEventListener("click", () => {
    bulkCancel = true;
    setBulkProgress("中止しています…");
  });

  // ============================================================
  // 単発学習
  // ============================================================
  panel.querySelector(".stella-btn-learn").addEventListener("click", async () => {
    const result = captureConversation();
    if (result.error) return setStatus(result.error, "error");
    if (!result.history || result.history.length < 30) {
      return setStatus("会話が短すぎます。", "error");
    }
    await addSample(result.history);
    await refreshSampleCount();
    setStatus(`学習サンプルに追加しました（合計 ${(await loadSamples()).length} 件）`, "ok");
  });

  // ============================================================
  // 手動セクション (展開可能)
  // ============================================================
  const contextArea = panel.querySelector(".stella-context");
  const memoArea = panel.querySelector(".stella-memo");
  const outputArea = panel.querySelector(".stella-output");

  panel.querySelector(".stella-btn-capture").addEventListener("click", () => {
    const result = captureConversation();
    if (result.error) return setStatus(result.error, "error");
    contextArea.value = result.history;
    setStatus(`${result.count} 件のメッセージを読み取りました`, "ok");
  });

  panel.querySelector(".stella-btn-generate").addEventListener("click", async () => {
    const memo = memoArea.value.trim();
    if (!memo) return setStatus("メモを入力してください", "error");
    const context = contextArea.value.trim();
    const apiKey = await getApiKey();
    if (!apiKey) return setStatus("APIキー未設定", "error");
    setStatus("生成中…", "info");
    try {
      const samples = await loadSamples();
      const draft = await callClaude(apiKey, context, memo, samples);
      outputArea.value = draft;
      setStatus("下書き完成", "ok");
    } catch (err) {
      setStatus("エラー: " + err.message, "error");
    }
  });

  panel.querySelector(".stella-btn-copy").addEventListener("click", () => {
    if (!outputArea.value) return;
    navigator.clipboard.writeText(outputArea.value);
    setStatus("クリップボードにコピーしました", "ok");
  });
  panel.querySelector(".stella-btn-insert").addEventListener("click", () => {
    if (!outputArea.value) return;
    const ok = replaceInputContent(findMessageInput(), outputArea.value);
    setStatus(ok ? "返信欄に挿入しました" : "入力欄が見つかりません", ok ? "ok" : "error");
  });
  panel.querySelector(".stella-btn-clear").addEventListener("click", () => {
    contextArea.value = "";
    memoArea.value = "";
    outputArea.value = "";
    setStatus("");
  });

  // ============================================================
  // インラインボタン: 返信欄のメモを清書して置き換える
  // ============================================================
  async function getApiKey() {
    return new Promise((resolve) => {
      chrome.storage.sync.get(["anthropicApiKey"], (data) => {
        resolve(data.anthropicApiKey || "");
      });
    });
  }

  function findMessageInput() {
    const candidates = [
      'textarea[placeholder*="メッセージ"]',
      'textarea[placeholder*="入力"]',
      'div[contenteditable="true"][role="textbox"]',
      'div[contenteditable="true"]',
      "textarea",
    ];
    for (const sel of candidates) {
      const els = document.querySelectorAll(sel);
      for (const el of els) {
        if (el.closest(`#${PANEL_ID}`)) continue;
        if (el.offsetParent === null) continue;
        const r = el.getBoundingClientRect();
        if (r.width < 80 || r.height < 20) continue;
        return el;
      }
    }
    return null;
  }

  function readInputContent(input) {
    if (!input) return "";
    if (input.tagName === "TEXTAREA" || input.tagName === "INPUT") return input.value || "";
    return input.innerText || "";
  }

  function replaceInputContent(input, text) {
    if (!input) return false;
    if (input.tagName === "TEXTAREA" || input.tagName === "INPUT") {
      const setter = Object.getOwnPropertyDescriptor(
        window.HTMLTextAreaElement.prototype, "value"
      ).set;
      setter.call(input, text);
      input.dispatchEvent(new Event("input", { bubbles: true }));
    } else {
      input.focus();
      // contenteditable: 全選択 → 削除 → 挿入
      const sel = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(input);
      sel.removeAllRanges();
      sel.addRange(range);
      document.execCommand("insertText", false, text);
      // フォールバック
      if (input.innerText.trim() !== text.trim()) {
        input.innerText = text;
        input.dispatchEvent(new Event("input", { bubbles: true }));
      }
    }
    return true;
  }

  async function runInlineGenerate() {
    const input = findMessageInput();
    if (!input) return setStatus("入力欄が見つかりません", "error");

    const memo = readInputContent(input).trim();
    if (!memo) {
      return setStatus(
        "返信欄にメモ（例: 6・11 10時半 / キャンセル可）を書いてから ✨ を押してください",
        "error"
      );
    }

    const apiKey = await getApiKey();
    if (!apiKey) return setStatus("APIキー未設定。拡張機能アイコンから設定してください。", "error");

    const conv = captureConversation();
    const context = conv.error ? "" : conv.history;

    setStatus("✨ 生成中…", "info");
    const btn = document.getElementById(INLINE_BTN_ID);
    if (btn) btn.classList.add("loading");

    try {
      const samples = await loadSamples();
      const draft = await callClaude(apiKey, context, memo, samples);
      const ok = replaceInputContent(input, draft);
      setStatus(ok ? "✅ 返信欄を清書しました" : "挿入に失敗。コピーをご利用ください", ok ? "ok" : "error");
    } catch (err) {
      setStatus("エラー: " + err.message, "error");
    } finally {
      if (btn) btn.classList.remove("loading");
    }
  }

  // ============================================================
  // Claude API
  // ============================================================
  async function callClaude(apiKey, conversationHistory, memo, samples) {
    // 学習サンプルからランダムに最大N件
    const picked = [];
    const pool = samples.slice();
    while (picked.length < MAX_SAMPLES_IN_PROMPT && pool.length) {
      const i = Math.floor(Math.random() * pool.length);
      picked.push(pool.splice(i, 1)[0]);
    }
    const styleExamples = picked
      .map((s, i) => `### サンプル${i + 1}\n${s.text}`)
      .join("\n\n");

    const systemPrompt = `あなたは博多ステラ歯科のスタッフの代わりに、LINEの返信文を清書するアシスタントです。

# タスク
スタッフが返信欄に書いた「メモ」を、本人の文体に沿った自然で丁寧なLINE返信文に展開する。
メモは略記やキーワードだけのことが多い。前後の会話文脈と矛盾しないように展開する。

## 展開の例
- 「6・11 10時半」→ 次回のご予約を6月11日10時半でお取りした旨を伝える文
- 「キャンセル可」→ ご予約のキャンセルが可能である旨を丁寧に伝える文
- 「変更可 いつでも」→ 予約変更が可能、希望日時を伺う文
- 「予約取れない」→ お詫び＋代替案を伺う文
- 「ありがとう」→ お礼の返信
- 「了解」「OK」→ 了承した旨を丁寧に伝える文

# 絶対ルール
1. メモにある事実（日時・回答内容）は必ず正確に含める
2. メモに無い事実（別日時・追加情報・約束）は絶対に作らない
3. 学習サンプルから本人の文体・トーン・敬語レベル・語尾・絵文字や顔文字の使用傾向を学習し忠実に反映する
4. 出力は返信本文のみ。前置きや説明・コードブロックは書かない

# 文章スタイル
- 適度に柔らかいトーン（堅すぎず、馴れ馴れしくもない）
- 文末は「〜です。」「〜ます。」「〜ですね。」を使い分け
- 2〜3文ごとに空行を入れる
- LINEなのでメールより短く、改行多め
- 絵文字は学習サンプルで使われていれば自然に、なければ使わない

${styleExamples ? `# 本人の文体学習サンプル（[本人] の発言を中心に文体を真似る）\n\n${styleExamples}` : "（学習サンプルなし。一般的な丁寧な文体で書く。）"}`;

    const userPrompt = `# 直近の会話履歴（古い順）
${conversationHistory || "（会話履歴を取得できませんでした）"}

# スタッフが返信欄に書いたメモ
${memo}

---
このメモを、上記の会話文脈に合うように本人の文体で自然な返信文に展開してください。`;

    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
        "anthropic-dangerous-direct-browser-access": "true",
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-5",
        max_tokens: 1500,
        system: systemPrompt,
        messages: [{ role: "user", content: userPrompt }],
      }),
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`API ${res.status}: ${errText.slice(0, 200)}`);
    }
    const data = await res.json();
    return data.content[0].text.trim();
  }

  // ============================================================
  // インラインボタン配置
  // ============================================================
  function ensureInlineButton() {
    const input = findMessageInput();
    const existing = document.getElementById(INLINE_BTN_ID);
    if (!input) {
      if (existing) existing.style.display = "none";
      return;
    }
    let btn = existing;
    if (!btn) {
      btn = document.createElement("button");
      btn.id = INLINE_BTN_ID;
      btn.type = "button";
      btn.title = "返信欄のメモを本人の文体で清書する";
      btn.innerHTML = "✨";
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        runInlineGenerate();
      });
      document.body.appendChild(btn);
    }
    const r = input.getBoundingClientRect();
    btn.style.display = "flex";
    btn.style.top = `${window.scrollY + r.top - 8}px`;
    btn.style.left = `${window.scrollX + r.right - 40}px`;
  }

  const positionObserver = new MutationObserver(() => ensureInlineButton());
  positionObserver.observe(document.body, { childList: true, subtree: true });
  window.addEventListener("resize", ensureInlineButton);
  window.addEventListener("scroll", ensureInlineButton, true);
  setInterval(ensureInlineButton, 1500);
  ensureInlineButton();

  chrome.storage.onChanged.addListener((changes, area) => {
    if (area === "local" && changes[STORAGE_SAMPLES_KEY]) refreshSampleCount();
  });
})();
