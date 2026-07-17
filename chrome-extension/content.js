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
  // 料金表プラン定義（popup.js と同じ順序・キーで対応させること）
  const PRICE_PLANS = [
    { key: "priceImage_1", label: "① インビザラインフル（抜歯あり）" },
    { key: "priceImage_2", label: "② インビザラインフル" },
    { key: "priceImage_3", label: "③ インビザライン　モデレート" },
    { key: "priceImage_4", label: "④ インビザライン　エクスプレス" },
    { key: "priceImage_5", label: "⑤ インビザライン　ライト" },
  ];

  const panel = document.createElement("div");
  panel.id = PANEL_ID;
  panel.innerHTML = `
    <div class="stella-header">
      <span>✨ AI返信下書き</span>
      <button class="stella-toggle" title="折りたたみ">＿</button>
    </div>
    <div class="stella-body">
      <div class="stella-price-section">
        <div class="stella-price-title">📄 料金表を送る（押す→入力欄で Ctrl+V→送信）</div>
        <div class="stella-price-buttons">
          ${PRICE_PLANS.map(
            (p) =>
              `<button class="stella-btn-price" data-key="${p.key}">${p.label}</button>`
          ).join("")}
        </div>
        <div class="stella-price-status"></div>
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
  // 料金表画像の送信（クリップボードにコピー → 入力欄で貼り付け）
  // ============================================================
  const priceStatusEl = panel.querySelector(".stella-price-status");

  function setPriceStatus(msg, type) {
    priceStatusEl.textContent = msg;
    priceStatusEl.className = "stella-price-status " + (type || "");
  }

  panel.querySelectorAll(".stella-btn-price").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const key = btn.dataset.key;
      const label = btn.textContent.trim();

      const dataUrl = await getStored(key);
      if (!dataUrl) {
        setPriceStatus(
          `「${label}」の画像が未設定です。拡張機能アイコン → 設定 から登録してください。`,
          "error"
        );
        return;
      }

      setPriceStatus(`「${label}」をコピー中...`, "info");
      try {
        const pngBlob = await toPngBlob(dataUrl);
        await navigator.clipboard.write([
          new ClipboardItem({ "image/png": pngBlob }),
        ]);
        setPriceStatus(
          `「${label}」をコピーしました。入力欄をクリックして Ctrl+V → 送信してください。`,
          "ok"
        );
      } catch (err) {
        // クリップボード画像コピーが使えない場合は新規タブで開いて手動保存/添付
        try {
          window.open(dataUrl, "_blank");
          setPriceStatus(
            `自動コピーに対応していない環境のため、画像を別タブで開きました。保存して添付してください。（${err.message}）`,
            "error"
          );
        } catch (e2) {
          setPriceStatus("コピーに失敗しました: " + err.message, "error");
        }
      }
    });
  });

  function getStored(key) {
    return new Promise((resolve) => {
      chrome.storage.local.get([key], (data) => resolve(data[key] || ""));
    });
  }

  // data URL（JPEG/PNG）を、貼り付け互換性の高い PNG Blob に変換
  function toPngBlob(dataUrl) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        try {
          const canvas = document.createElement("canvas");
          canvas.width = img.naturalWidth || img.width;
          canvas.height = img.naturalHeight || img.height;
          const ctx = canvas.getContext("2d");
          // 透過画像でも白背景で潰す（料金表は白地想定）
          ctx.fillStyle = "#ffffff";
          ctx.fillRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(img, 0, 0);
          canvas.toBlob((blob) => {
            if (blob) resolve(blob);
            else reject(new Error("画像変換に失敗"));
          }, "image/png");
        } catch (e) {
          reject(e);
        }
      };
      img.onerror = () => reject(new Error("画像の読み込みに失敗"));
      img.src = dataUrl;
    });
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
