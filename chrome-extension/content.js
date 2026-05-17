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
    const container = findThreadContainer();
    if (!container) {
      return {
        error:
          "会話エリアが特定できませんでした。会話を開いた状態で再度お試しいただくか、手動で貼り付けてください。",
      };
    }

    // .chat-main 内の個別メッセージ要素から構造化して読み取る。
    // .chat-item.baloon が1メッセージ、.chat-item-text がその本文。
    const items = container.querySelectorAll(".chat-item.baloon, .chat-item");
    let history = "";
    let latestIncoming = "";
    let count = 0;
    if (items.length > 0) {
      const formatted = [];
      for (const item of items) {
        const textEl = item.querySelector(".chat-item-text");
        const body = cleanText((textEl ? textEl.innerText : item.innerText));
        if (!body) continue;
        // 送信/受信の判定: クラス名に send/sent/self/my/own があれば本人発信
        const cls = item.className.toLowerCase();
        const isOutgoing = /(send|sent|self|own|my-|-my|outgoing)/.test(cls);
        const role = isOutgoing ? "[本人]" : "[相手]";
        formatted.push(`${role} ${body}`);
        if (!isOutgoing) latestIncoming = body;
        count++;
      }
      history = formatted.join("\n");
    } else {
      // 構造が想定と違った場合のフォールバック: テキスト全部
      const text = cleanText(container.innerText);
      const lines = text
        .split("\n")
        .map((l) => l.trim())
        .filter((l) => l.length > 0);
      history = lines.join("\n");
      latestIncoming = lines.slice(-3).join("\n");
      count = lines.length;
    }

    return {
      history,
      latestIncoming,
      count,
    };
  }

  // LINE Manager が末尾に挿入するゼロ幅スペース等のノイズを除去する。
  // 「â€‹」はゼロ幅スペース(U+200B)のUTF-8バイト列(E2 80 8B)を
  // Windows-1252として誤デコードした結果の典型的な文字化けパターン。
  function cleanText(s) {
    if (!s) return "";
    return s
      .replace(/â€‹|â€/g, "")
      .replace(/[​-‍﻿]/g, "")
      .trim();
  }

  // 開いている会話スレッドのスクロール領域を特定する。
  // 最優先: LINE Manager 既知のクラス `.chat-main`（今開いている1人分の会話）。
  // それで取れない場合は、入力欄を起点にDOMを遡って探すヒューリスティック。
  function findThreadContainer() {
    const known = document.querySelector(".chat-main");
    if (known && known.innerText && known.innerText.length > 0) return known;

    const input = findMessageInput();

    // 入力欄が見つかった場合: 入力欄の祖先をたどり、その中で
    // スクロール可能 & 入力欄自身を含まない最大の領域を探す。
    if (input) {
      let node = input.parentElement;
      let best = null;
      let bestArea = 0;
      while (node && node !== document.body) {
        // node の中のスクロール可能な子孫を全部見る
        const scrollables = node.querySelectorAll("div, section, main, ul");
        for (const el of scrollables) {
          if (el.contains(input)) continue; // 入力欄を含む箱は会話本体ではない
          const style = getComputedStyle(el);
          const oy = style.overflowY;
          if (oy !== "auto" && oy !== "scroll") continue;
          const rect = el.getBoundingClientRect();
          if (rect.width < 200 || rect.height < 150) continue;
          const area = rect.width * rect.height;
          if (area > bestArea && el.innerText && el.innerText.length > 20) {
            bestArea = area;
            best = el;
          }
        }
        if (best) return best;
        node = node.parentElement;
      }
    }

    // フォールバック: 画面右半分にあるスクロール可能領域のうち最大のもの。
    // 友だち一覧は通常左側にあるので、これで一定避けられる。
    const viewportMidX = window.innerWidth / 2;
    const all = document.querySelectorAll("div, section, main, ul");
    let best = null;
    let bestArea = 0;
    for (const el of all) {
      const style = getComputedStyle(el);
      const oy = style.overflowY;
      if (oy !== "auto" && oy !== "scroll") continue;
      const rect = el.getBoundingClientRect();
      if (rect.width < 200 || rect.height < 150) continue;
      // 左端が画面中央より左 = 友だち一覧の可能性が高いのでスキップ
      if (rect.left < viewportMidX - 100) continue;
      const area = rect.width * rect.height;
      if (area > bestArea && el.innerText && el.innerText.length > 20) {
        bestArea = area;
        best = el;
      }
    }
    return best;
  }

  // LINE Manager の返信入力欄を探す（パネル内のtextareaは除外）。
  function findMessageInput() {
    const selectors = [
      'textarea[placeholder*="メッセージ"]',
      'textarea[placeholder*="入力"]',
      'div[contenteditable="true"]',
      "textarea",
    ];
    for (const sel of selectors) {
      const els = document.querySelectorAll(sel);
      for (const el of els) {
        if (panel.contains(el)) continue; // 自分のパネルは除外
        if (el.offsetParent === null) continue; // 非表示は除外
        const rect = el.getBoundingClientRect();
        if (rect.width < 100 || rect.height < 20) continue;
        return el;
      }
    }
    return null;
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
})();
