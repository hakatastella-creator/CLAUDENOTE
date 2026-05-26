/**
 * LINE Official Account Manager / chat.line.biz 上に
 *  ・常時表示のサイドパネル（学習・下書き生成）
 *  ・入力欄の横に出る「✨」インラインボタン
 * を注入する。
 */

(function () {
  const PANEL_ID = "stella-reply-panel";
  const INLINE_BTN_ID = "stella-inline-btn";
  const STORAGE_SAMPLES_KEY = "stellaStyleSamples"; // 学習済みサンプル
  const MAX_SAMPLES_IN_PROMPT = 5;
  const MAX_STORED_SAMPLES = 30;

  if (document.getElementById(PANEL_ID)) return;

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
        <button class="stella-btn-capture">📋 会話を読み取る</button>
        <button class="stella-btn-learn" title="この会話を文体学習サンプルとして保存">📚 この会話を学習</button>
      </div>
      <textarea class="stella-context" placeholder="過去のやり取り（古い順）。&#10;[相手] / [本人] で区切られた形式で貼り付け、または上のボタンで自動取得"></textarea>
      <textarea class="stella-incoming" placeholder="返信したい受信メッセージ"></textarea>
      <button class="stella-btn-generate">✨ 下書きを生成</button>
      <div class="stella-status"></div>
      <textarea class="stella-output" placeholder="生成された下書きがここに表示されます" readonly></textarea>
      <div class="stella-actions">
        <button class="stella-btn-copy">📋 コピー</button>
        <button class="stella-btn-insert">▶ 入力欄に挿入</button>
        <button class="stella-btn-clear">🗑 クリア</button>
      </div>
    </div>
  `;
  document.body.appendChild(panel);

  // 折りたたみ
  const toggleBtn = panel.querySelector(".stella-toggle");
  const body = panel.querySelector(".stella-body");
  toggleBtn.addEventListener("click", () => {
    const hidden = body.style.display === "none";
    body.style.display = hidden ? "flex" : "none";
    toggleBtn.textContent = hidden ? "＿" : "▢";
  });

  // ============================================================
  // 学習サンプル数の表示
  // ============================================================
  const sampleCountEl = panel.querySelector(".stella-sample-count");
  async function refreshSampleCount() {
    const samples = await loadSamples();
    sampleCountEl.textContent = `📚 ${samples.length}`;
  }
  refreshSampleCount();

  // ============================================================
  // 会話読み取り（DOM ヒューリスティック）
  // ============================================================
  const captureBtn = panel.querySelector(".stella-btn-capture");
  const learnBtn = panel.querySelector(".stella-btn-learn");
  const contextArea = panel.querySelector(".stella-context");
  const incomingArea = panel.querySelector(".stella-incoming");

  captureBtn.addEventListener("click", () => {
    const result = captureConversation();
    if (result.error) return setStatus(result.error, "error");
    contextArea.value = result.history;
    incomingArea.value = result.latestIncoming;
    setStatus(`${result.count} 件のメッセージを読み取りました`, "ok");
  });

  learnBtn.addEventListener("click", async () => {
    const result = captureConversation();
    if (result.error) return setStatus(result.error, "error");
    if (!result.history || result.history.length < 30) {
      return setStatus("会話が短すぎます。もう少しスクロールしてから再度お試しください。", "error");
    }
    await addSample(result.history);
    await refreshSampleCount();
    setStatus(`学習サンプルに追加しました（合計 ${(await loadSamples()).length} 件）`, "ok");
  });

  /**
   * 現在のチャットから会話を取得。
   * 各メッセージが「本人」「相手」どちらかを推測してタグ付けする。
   */
  function captureConversation() {
    const container = findChatContainer();
    if (!container) {
      return { error: "会話エリアが見つかりませんでした。手動で貼り付けてください。" };
    }

    const messages = extractMessages(container);
    if (messages.length === 0) {
      // フォールバック: 改行で分割
      const text = container.innerText.trim();
      const lines = text.split("\n").map((l) => l.trim()).filter(Boolean);
      const history = lines.join("\n");
      return { history, latestIncoming: lines.slice(-3).join("\n"), count: lines.length };
    }

    const history = messages
      .map((m) => `[${m.from === "self" ? "本人" : "相手"}] ${m.text}`)
      .join("\n");

    // 最後の「相手」メッセージを受信メッセージ候補に
    const lastIncoming = [...messages].reverse().find((m) => m.from === "other");
    const latestIncoming = lastIncoming ? lastIncoming.text : "";

    return { history, latestIncoming, count: messages.length };
  }

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
    // フォールバック: 一番大きいスクロール可能エリア
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

  /**
   * チャットコンテナ内のメッセージ要素を列挙し、自分(self)/相手(other) を推定。
   * LINE Manager は通常、自分の発言が右寄せ、相手が左寄せ。
   */
  function extractMessages(container) {
    const rect = container.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;

    // メッセージらしき要素を候補化:
    // 「テキストを持つ」「子のテキストノードが短すぎない」要素のうち、
    // 同一階層に複数並んでいるものをメッセージ行とみなす。
    const all = container.querySelectorAll("li, [class*='message'], [class*='Message'], [class*='bubble'], [class*='Bubble']");
    const messages = [];
    const seen = new Set();

    for (const el of all) {
      const text = (el.innerText || "").trim();
      if (!text || text.length < 1 || text.length > 2000) continue;
      // 親要素ですでに拾っていればスキップ
      if (seen.has(text)) continue;

      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) continue;

      // 右寄せか左寄せか: 要素の中心が container の中央より右なら自分
      const elCenter = r.left + r.width / 2;
      const from = elCenter > centerX ? "self" : "other";

      messages.push({ text, from, top: r.top });
      seen.add(text);
    }

    // 上→下順
    messages.sort((a, b) => a.top - b.top);
    return messages.map(({ text, from }) => ({ text, from }));
  }

  // ============================================================
  // 学習サンプルの永続化
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
  // Claude API 呼び出し
  // ============================================================
  const generateBtn = panel.querySelector(".stella-btn-generate");
  const outputArea = panel.querySelector(".stella-output");

  generateBtn.addEventListener("click", () => runGenerate({ fromInline: false }));

  async function runGenerate({ fromInline }) {
    const apiKey = await getApiKey();
    if (!apiKey) {
      setStatus("APIキー未設定。拡張機能アイコンから設定してください。", "error");
      return;
    }

    // インラインボタンから呼ばれた場合は、その場で会話を再取得
    if (fromInline) {
      const result = captureConversation();
      if (result.error) return setStatus(result.error, "error");
      contextArea.value = result.history;
      incomingArea.value = result.latestIncoming;
    }

    const incoming = incomingArea.value.trim();
    if (!incoming) return setStatus("受信メッセージを入力してください。", "error");
    const context = contextArea.value.trim();

    setStatus("生成中...", "info");
    generateBtn.disabled = true;
    outputArea.value = "";

    try {
      const samples = await loadSamples();
      const draft = await callClaude(apiKey, context, incoming, samples);
      outputArea.value = draft;
      setStatus("下書き完成！", "ok");
      // 自動でパネルを展開
      if (body.style.display === "none") {
        body.style.display = "flex";
        toggleBtn.textContent = "＿";
      }
    } catch (err) {
      setStatus("エラー: " + err.message, "error");
    } finally {
      generateBtn.disabled = false;
    }
  }

  async function getApiKey() {
    return new Promise((resolve) => {
      chrome.storage.sync.get(["anthropicApiKey"], (data) => {
        resolve(data.anthropicApiKey || "");
      });
    });
  }

  async function callClaude(apiKey, context, incoming, samples) {
    const styleExamples = samples
      .slice(-MAX_SAMPLES_IN_PROMPT)
      .map((s, i) => `### サンプル${i + 1}\n${s.text}`)
      .join("\n\n");

    const systemPrompt = `あなたはユーザー（博多ステラ歯科）の代わりにLINE返信下書きを作成するアシスタントです。

絶対ルール:
1. 過去のやり取り・学習サンプルから本人の文体・トーン・敬語レベル・語尾・絵文字や顔文字の使用傾向を学習し忠実に反映する
2. 確定していない事実（日時・金額・約束）は絶対に作らない。必要なら「【要確認】」と明記
3. 出力は返信本文のみ。前置きや説明・コードブロックは書かない

文章スタイル:
- 適度に柔らかいトーン（堅すぎず、馴れ馴れしくもない）
- 「ありがとうございます」「お手数ですが」などの気遣いを自然に
- 文末は単調にせず「〜です。」「〜ます。」「〜ですね。」を使い分ける

読みやすさ:
- 2〜3文ごとに必ず空行を入れる
- 1段落 = 2〜4文程度
- 冒頭挨拶 → 本題 → 締め挨拶 を空行で区切る

LINE特有の配慮:
- メールよりやや短く、改行多め
- 絵文字は過去のやり取り/学習サンプルで使われていれば適度に使用、なければ使わない

${styleExamples ? `# 本人の文体学習サンプル（過去の実際のやり取り。\`[本人]\` の発言を中心に文体を真似る）\n\n${styleExamples}` : ""}`;

    const userPrompt = `# 直近のやり取り（古い順）
${context || "（直近のやり取りなし）"}

# 今回返信する受信メッセージ
${incoming}

---
本人の文体を忠実に再現した返信下書きを作成してください。`;

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
  // コピー / 挿入 / クリア
  // ============================================================
  panel.querySelector(".stella-btn-copy").addEventListener("click", () => {
    if (!outputArea.value) return;
    navigator.clipboard.writeText(outputArea.value);
    setStatus("クリップボードにコピーしました", "ok");
  });

  panel.querySelector(".stella-btn-insert").addEventListener("click", () => {
    if (!outputArea.value) return;
    const ok = insertIntoMessageBox(outputArea.value);
    setStatus(ok ? "入力欄に挿入しました" : "入力欄が見つかりません。コピーしてください。", ok ? "ok" : "error");
  });

  panel.querySelector(".stella-btn-clear").addEventListener("click", () => {
    contextArea.value = "";
    incomingArea.value = "";
    outputArea.value = "";
    setStatus("");
  });

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
        if (el === contextArea || el === incomingArea || el === outputArea) continue;
        if (el.closest(`#${PANEL_ID}`)) continue;
        if (el.offsetParent === null) continue;
        const r = el.getBoundingClientRect();
        if (r.width < 80 || r.height < 20) continue;
        return el;
      }
    }
    return null;
  }

  function insertIntoMessageBox(text) {
    const input = findMessageInput();
    if (!input) return false;
    if (input.tagName === "TEXTAREA" || input.tagName === "INPUT") {
      const setter = Object.getOwnPropertyDescriptor(
        window.HTMLTextAreaElement.prototype, "value"
      ).set;
      setter.call(input, text);
      input.dispatchEvent(new Event("input", { bubbles: true }));
    } else {
      input.focus();
      input.innerText = text;
      input.dispatchEvent(new Event("input", { bubbles: true }));
    }
    return true;
  }

  // ============================================================
  // ステータス表示
  // ============================================================
  const statusEl = panel.querySelector(".stella-status");
  function setStatus(msg, type) {
    statusEl.textContent = msg;
    statusEl.className = "stella-status " + (type || "");
  }

  // ============================================================
  // インラインボタン（入力欄の横に常時表示）
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
      btn.title = "AIで返信下書きを生成（クリックでこの会話から自動取得）";
      btn.innerHTML = "✨";
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        runGenerate({ fromInline: true });
      });
      document.body.appendChild(btn);
    }

    // 入力欄の右上に絶対配置
    const r = input.getBoundingClientRect();
    btn.style.display = "flex";
    btn.style.top = `${window.scrollY + r.top - 8}px`;
    btn.style.left = `${window.scrollX + r.right - 40}px`;
  }

  // 入力欄の出現や移動を監視
  const positionObserver = new MutationObserver(() => ensureInlineButton());
  positionObserver.observe(document.body, { childList: true, subtree: true });
  window.addEventListener("resize", ensureInlineButton);
  window.addEventListener("scroll", ensureInlineButton, true);
  setInterval(ensureInlineButton, 1500); // SPA遷移用の保険
  ensureInlineButton();

  // 他タブからの学習サンプル変更を反映
  chrome.storage.onChanged.addListener((changes, area) => {
    if (area === "local" && changes[STORAGE_SAMPLES_KEY]) refreshSampleCount();
  });
})();
