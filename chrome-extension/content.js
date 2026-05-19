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
      <div class="stella-section-scan">
        <button class="stella-btn-scan">🔍 未返信スキャン</button>
        <div class="stella-scan-status"></div>
      </div>
      <div class="stella-divider"></div>
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
  // 未返信スキャン
  // ============================================================
  const DASHBOARD_URL = "http://127.0.0.1:8765";
  const scanBtn = panel.querySelector(".stella-btn-scan");
  const scanStatusEl = panel.querySelector(".stella-scan-status");

  function setScanStatus(msg, type) {
    scanStatusEl.textContent = msg;
    scanStatusEl.className = "stella-scan-status " + (type || "");
  }

  scanBtn.addEventListener("click", async () => {
    scanBtn.disabled = true;
    setScanStatus("スキャン中...", "info");
    try {
      const conversations = await scanConversationList();
      setScanStatus(`${conversations.length}件取得。送信中...`, "info");
      const res = await fetch(`${DASHBOARD_URL}/scan`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ conversations }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setScanStatus(
        `送信完了: ${data.count}件。ダッシュボード（${DASHBOARD_URL}）で確認`,
        "ok",
      );
    } catch (err) {
      setScanStatus(
        `エラー: ${err.message}。ダッシュボードサーバが起動しているか確認`,
        "error",
      );
    } finally {
      scanBtn.disabled = false;
    }
  });

  /**
   * LINE Manager の会話一覧をスキャンし、各会話の最終受信時刻・本文を抽出する。
   *
   * LINE Manager の正確な DOM 構造は UI 変更で変わるため、複数のセレクタ候補で
   * 試し、抽出できなかった項目は null のまま返す。サーバ側 / ダッシュボード側で
   * 12時間閾値判定を行う。
   */
  async function scanConversationList() {
    const items = findConversationListItems();
    const out = [];
    const now = Date.now();
    for (const el of items) {
      const info = extractConversationInfo(el);
      if (!info) continue;
      if (info.last_incoming_at) {
        const ms = new Date(info.last_incoming_at).getTime();
        if (!isNaN(ms)) {
          info.elapsed_hours = Math.max(0, (now - ms) / 3600000);
        }
      }
      out.push(info);
    }
    return out;
  }

  function findConversationListItems() {
    // 既知/予想される会話リストアイテムのセレクタ候補
    const candidates = [
      '[data-testid*="chat-list"] [data-testid*="chat-item"]',
      '[data-testid*="ChatList"] li',
      '[class*="ChatList"] [class*="ChatItem"]',
      '[class*="chatList"] [class*="chatItem"]',
      '[class*="ChatList"] li',
      '[role="listitem"]',
      '[role="list"] > div',
    ];
    for (const sel of candidates) {
      const els = document.querySelectorAll(sel);
      if (els.length >= 2) return Array.from(els);
    }
    // フォールバック：左サイドの一覧らしき要素を推測
    const lists = document.querySelectorAll('ul, [role="list"]');
    let best = [];
    for (const list of lists) {
      const children = list.querySelectorAll(":scope > *");
      if (children.length > best.length && children.length >= 3) {
        best = Array.from(children);
      }
    }
    return best;
  }

  function extractConversationInfo(el) {
    const text = el.innerText || "";
    if (!text.trim()) return null;

    // 名前：先頭行を候補にする
    const lines = text.split("\n").map((l) => l.trim()).filter(Boolean);
    const name = lines[0] || null;

    // 時刻表示：例 "10:30", "昨日", "5月18日"
    const timeText = lines.find((l) =>
      /^(\d{1,2}:\d{2}|昨日|一昨日|\d{1,2}\/\d{1,2}|\d{1,2}月\d{1,2}日)$/.test(l),
    );
    const lastIncomingAt = parseRelativeTime(timeText);

    // 最後のメッセージ本文：時刻以外の末尾行
    const snippet = lines
      .filter((l) => l !== timeText && l !== name)
      .slice(-1)[0] || null;

    // 未読バッジ
    const unread =
      !!el.querySelector('[class*="unread"], [class*="Unread"], [class*="badge"]') ||
      /^\d+$/.test(lines[lines.length - 1] || "");

    // タグ（個別対応中 等）
    const tagEl = el.querySelector('[class*="tag"], [class*="Tag"], [class*="label"]');
    const tag = tagEl ? tagEl.innerText.trim() : null;

    // 最終発言が顧客かどうかは一覧画面では確定できない。
    // ヒューリスティック：「You: ...」「自分: ...」のような prefix がなければ顧客発言と推定。
    const isLastFromCustomer = !/^(You|自分|スタッフ)[:：]/.test(snippet || "");

    return {
      id: el.getAttribute("data-id") || el.id || (name + "|" + (snippet || "")),
      name,
      last_incoming_at: lastIncomingAt,
      last_incoming_text: snippet,
      unread,
      tag,
      is_last_from_customer: isLastFromCustomer,
      raw_time_label: timeText || null,
    };
  }

  function parseRelativeTime(label) {
    if (!label) return null;
    const now = new Date();
    const pad = (n) => String(n).padStart(2, "0");

    // HH:MM → 今日
    let m = label.match(/^(\d{1,2}):(\d{2})$/);
    if (m) {
      const d = new Date(now);
      d.setHours(parseInt(m[1], 10), parseInt(m[2], 10), 0, 0);
      // 未来時刻なら昨日として扱う
      if (d.getTime() > now.getTime()) d.setDate(d.getDate() - 1);
      return d.toISOString();
    }
    if (label === "昨日") {
      const d = new Date(now);
      d.setDate(d.getDate() - 1);
      d.setHours(12, 0, 0, 0);
      return d.toISOString();
    }
    if (label === "一昨日") {
      const d = new Date(now);
      d.setDate(d.getDate() - 2);
      d.setHours(12, 0, 0, 0);
      return d.toISOString();
    }
    // 5月18日 or 5/18
    m = label.match(/^(\d{1,2})[月\/](\d{1,2})/);
    if (m) {
      const d = new Date(now);
      d.setMonth(parseInt(m[1], 10) - 1, parseInt(m[2], 10));
      d.setHours(12, 0, 0, 0);
      if (d.getTime() > now.getTime()) d.setFullYear(d.getFullYear() - 1);
      return d.toISOString();
    }
    return null;
  }
})();
