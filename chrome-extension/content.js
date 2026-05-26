/**
 * LINE Official Account Manager / chat.line.biz 上に
 * 「✨ AI下書き」サイドパネルを注入する。
 */

(function () {
  const PANEL_ID = "stella-reply-panel";
  if (document.getElementById(PANEL_ID)) return;

  // ============================================================
  // サイドパネル UI
  // ============================================================
  const panel = document.createElement("div");
  panel.id = PANEL_ID;
  panel.innerHTML = `
    <div class="stella-header">
      <span>✨ AI返信下書き</span>
      <button class="stella-toggle" title="折りたたみ">＿</button>
    </div>
    <div class="stella-body">
      <button class="stella-btn-capture">📋 画面から会話を読み取る</button>
      <textarea class="stella-context" placeholder="ここに過去のやり取り（古い順）。&#10;&#10;[相手] こんにちは&#10;[本人] お世話になっております&#10;&#10;...などを貼り付け、または上のボタンで自動取得"></textarea>
      <textarea class="stella-incoming" placeholder="返信したい受信メッセージ本文"></textarea>
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
  // 会話読み取り
  // ============================================================
  const captureBtn = panel.querySelector(".stella-btn-capture");
  const contextArea = panel.querySelector(".stella-context");
  const incomingArea = panel.querySelector(".stella-incoming");

  captureBtn.addEventListener("click", () => {
    const result = captureConversation();
    if (result.error) {
      setStatus(result.error, "error");
      return;
    }
    contextArea.value = result.history;
    incomingArea.value = result.latestIncoming;
    setStatus(`${result.count} 件のメッセージを読み取りました`, "ok");
  });

  function captureConversation() {
    // LINE Manager のチャットエリアを推測して取得
    // 既知のセレクタ候補（UI変更に備えて複数試す）
    const candidates = [
      '[data-testid="chat-list"]',
      '[class*="ChatList"]',
      '[class*="messageList"]',
      '[class*="MessageList"]',
      '[role="log"]',
    ];
    let container = null;
    for (const sel of candidates) {
      const el = document.querySelector(sel);
      if (el && el.innerText && el.innerText.length > 50) {
        container = el;
        break;
      }
    }

    if (!container) {
      // フォールバック: 一番大きいスクロール可能エリアを探す
      const all = document.querySelectorAll("div");
      let best = null;
      let bestLen = 0;
      for (const el of all) {
        const style = getComputedStyle(el);
        if (
          (style.overflowY === "auto" || style.overflowY === "scroll") &&
          el.innerText &&
          el.innerText.length > bestLen
        ) {
          bestLen = el.innerText.length;
          best = el;
        }
      }
      container = best;
    }

    if (!container) {
      return { error: "会話エリアが見つかりませんでした。手動で貼り付けてください。" };
    }

    const text = container.innerText.trim();
    const lines = text
      .split("\n")
      .map((l) => l.trim())
      .filter((l) => l.length > 0);

    // 最後の発言を「受信メッセージ」とみなす
    // ※ LINE Managerの正確な構造が不明なので、ヒューリスティック
    const latestIncoming = lines.slice(-3).join("\n");
    const history = lines.join("\n");

    return {
      history,
      latestIncoming,
      count: lines.length,
    };
  }

  // ============================================================
  // Claude API 呼び出し
  // ============================================================
  const generateBtn = panel.querySelector(".stella-btn-generate");
  const outputArea = panel.querySelector(".stella-output");

  generateBtn.addEventListener("click", async () => {
    const apiKey = await getApiKey();
    if (!apiKey) {
      setStatus("APIキー未設定。拡張機能アイコンから設定してください。", "error");
      return;
    }
    const incoming = incomingArea.value.trim();
    if (!incoming) {
      setStatus("受信メッセージを入力してください。", "error");
      return;
    }
    const context = contextArea.value.trim();

    setStatus("生成中...", "info");
    generateBtn.disabled = true;
    outputArea.value = "";

    try {
      const draft = await callClaude(apiKey, context, incoming);
      outputArea.value = draft;
      setStatus("下書き完成！", "ok");
    } catch (err) {
      setStatus("エラー: " + err.message, "error");
    } finally {
      generateBtn.disabled = false;
    }
  });

  async function getApiKey() {
    return new Promise((resolve) => {
      chrome.storage.sync.get(["anthropicApiKey"], (data) => {
        resolve(data.anthropicApiKey || "");
      });
    });
  }

  async function callClaude(apiKey, context, incoming) {
    const systemPrompt = `あなたはユーザーの代わりにビジネス連絡の返信下書きを作成するアシスタントです。

絶対ルール:
1. 過去のやり取りから本人の文体・トーン・敬語レベル・語尾・絵文字や顔文字の使用傾向を学習し反映する
2. 確定していない事実（日時・金額・約束）は絶対に作らない。必要なら「【要確認】」と明記
3. 出力は返信本文のみ。前置きや説明は書かない

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
- 絵文字は過去のやり取りで使われていれば適度に使用、なければ使わない
`;

    const userPrompt = `# 過去のやり取り（古い順、本人の文体学習用）
${context || "（過去のやり取りなし）"}

# 今回の受信メッセージ
${incoming}

---
本人の文体を再現した返信下書きを作成してください。`;

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
  // コピー / 入力欄に挿入 / クリア
  // ============================================================
  panel.querySelector(".stella-btn-copy").addEventListener("click", () => {
    if (!outputArea.value) return;
    navigator.clipboard.writeText(outputArea.value);
    setStatus("クリップボードにコピーしました", "ok");
  });

  panel.querySelector(".stella-btn-insert").addEventListener("click", () => {
    if (!outputArea.value) return;
    const ok = insertIntoMessageBox(outputArea.value);
    if (ok) {
      setStatus("入力欄に挿入しました", "ok");
    } else {
      setStatus("入力欄が見つかりません。コピーしてください。", "error");
    }
  });

  panel.querySelector(".stella-btn-clear").addEventListener("click", () => {
    contextArea.value = "";
    incomingArea.value = "";
    outputArea.value = "";
    setStatus("");
  });

  function insertIntoMessageBox(text) {
    // LINE Manager の入力欄を探す
    const candidates = [
      'textarea[placeholder*="メッセージ"]',
      'textarea[placeholder*="入力"]',
      'div[contenteditable="true"]',
      "textarea",
    ];
    let input = null;
    for (const sel of candidates) {
      const els = document.querySelectorAll(sel);
      for (const el of els) {
        if (el === contextArea || el === incomingArea || el === outputArea) continue;
        if (el.offsetParent !== null) {
          input = el;
          break;
        }
      }
      if (input) break;
    }

    if (!input) return false;

    if (input.tagName === "TEXTAREA" || input.tagName === "INPUT") {
      const setter = Object.getOwnPropertyDescriptor(
        window.HTMLTextAreaElement.prototype,
        "value"
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
  // 返信漏れバッジ（画面右上に常時表示）
  // ============================================================
  injectUnrepliedBadge();

  function injectUnrepliedBadge() {
    const BADGE_ID = "stella-unreplied-badge";
    if (document.getElementById(BADGE_ID)) return;

    const wrap = document.createElement("div");
    wrap.id = BADGE_ID;
    wrap.innerHTML = `
      <button class="stella-unreplied-btn" title="返信漏れトーク一覧">
        <span class="stella-unreplied-icon">📩</span>
        <span class="stella-unreplied-label">返信漏れ</span>
        <span class="stella-unreplied-count">-</span>
      </button>
      <div class="stella-unreplied-panel" style="display:none">
        <div class="stella-unreplied-header">
          <span>📩 返信漏れトーク</span>
          <div>
            <button class="stella-unreplied-refresh" title="再取得">🔄</button>
            <button class="stella-unreplied-close" title="閉じる">✕</button>
          </div>
        </div>
        <div class="stella-unreplied-body"></div>
      </div>
    `;
    document.body.appendChild(wrap);

    const openBtn = wrap.querySelector(".stella-unreplied-btn");
    const dropdown = wrap.querySelector(".stella-unreplied-panel");
    const body = wrap.querySelector(".stella-unreplied-body");
    const countEl = wrap.querySelector(".stella-unreplied-count");

    openBtn.addEventListener("click", () => {
      const willOpen = dropdown.style.display === "none";
      dropdown.style.display = willOpen ? "flex" : "none";
      if (willOpen) renderList();
    });
    wrap.querySelector(".stella-unreplied-close").addEventListener("click", () => {
      dropdown.style.display = "none";
    });
    wrap.querySelector(".stella-unreplied-refresh").addEventListener("click", renderList);

    function renderList() {
      const items = findUnrepliedTalks();
      countEl.textContent = items.length;
      body.innerHTML = "";
      if (items.length === 0) {
        const empty = document.createElement("div");
        empty.className = "stella-unreplied-empty";
        empty.textContent = "返信漏れはありません 🎉";
        body.appendChild(empty);
        return;
      }
      for (const item of items) {
        const row = document.createElement("div");
        row.className = "stella-unreplied-item";
        const name = document.createElement("div");
        name.className = "stella-unreplied-name";
        name.textContent = item.name;
        const preview = document.createElement("div");
        preview.className = "stella-unreplied-preview";
        preview.textContent = item.preview;
        const badge = document.createElement("span");
        badge.className = "stella-unreplied-itembadge";
        badge.textContent = item.unread;
        name.appendChild(badge);
        row.appendChild(name);
        row.appendChild(preview);
        row.addEventListener("click", () => {
          try {
            item.el.click();
          } catch (_) {}
          dropdown.style.display = "none";
        });
        body.appendChild(row);
      }
    }

    function updateCountOnly() {
      const items = findUnrepliedTalks();
      countEl.textContent = items.length;
    }

    // 初回・定期更新（パネル開いてる間はrenderListが既に動く）
    setTimeout(updateCountOnly, 1500);
    setInterval(() => {
      if (dropdown.style.display === "flex") {
        renderList();
      } else {
        updateCountOnly();
      }
    }, 15000);
  }

  function findUnrepliedTalks() {
    // LINE Manager / chat.line.biz のトーク一覧から「未読件数バッジ」を持つ行を探す。
    // UIが変わっても壊れにくいよう、複数のセレクタ候補＋数字バッジ検出のヒューリスティック。
    const rowCandidates = new Set();
    const rowSelectors = [
      '[class*="ChatList"] li',
      '[class*="TalkList"] li',
      '[class*="chatList"] li',
      '[class*="talkList"] li',
      '[class*="ChatRoom"]',
      '[class*="chatRoom"]',
      '[role="listitem"]',
      'li[class*="item"]',
      'a[href*="/chat/"]',
    ];
    for (const sel of rowSelectors) {
      document.querySelectorAll(sel).forEach((el) => rowCandidates.add(el));
    }

    const results = [];
    const seenText = new Set();
    for (const el of rowCandidates) {
      // 表示されている要素のみ
      if (!el.offsetParent && el.tagName !== "A") continue;

      // バッジ的要素を探す（class名にbadge/unreadを含む、または短い数字テキスト）
      let unread = 0;
      const badgeCandidates = el.querySelectorAll(
        '[class*="badge"],[class*="Badge"],[class*="unread"],[class*="Unread"],[class*="count"],[class*="Count"]'
      );
      for (const b of badgeCandidates) {
        const t = (b.textContent || "").trim();
        if (/^\d{1,3}$/.test(t)) {
          unread = parseInt(t, 10);
          break;
        }
      }
      if (unread === 0) continue;

      const text = (el.innerText || "").trim();
      if (!text) continue;
      // 重複排除（同じ行が複数セレクタで拾われる）
      const key = text.slice(0, 80);
      if (seenText.has(key)) continue;
      seenText.add(key);

      const lines = text.split("\n").map((l) => l.trim()).filter(Boolean);
      // 数字だけの行（バッジ自身）は除外
      const filtered = lines.filter((l) => !/^\d{1,3}$/.test(l));
      const name = filtered[0] || "(名前不明)";
      const preview = (filtered.slice(1, 3).join(" / ") || "").slice(0, 80);

      results.push({ el, name, preview, unread });
    }
    return results;
  }
})();
