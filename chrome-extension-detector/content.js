/**
 * LINE返信漏れ検出
 *
 * manager.line.biz / chat.line.biz の画面右上に
 * 「📩 返信漏れ (N)」バッジを常時表示する。クリックすると
 * 未読バッジが付いている（=自分が返信していない）トークの
 * 一覧をドロップダウンで表示し、各行クリックで該当トークへ
 * ジャンプする。
 */

(function () {
  const BADGE_ID = "stella-unreplied-badge";
  const IFRAME_MIN_SIZE = 400;

  // iframe 内で動く場合、極端に小さいフレーム（広告/トラッキング等）には注入しない
  if (window.top !== window) {
    const w = document.documentElement.clientWidth || 0;
    const h = document.documentElement.clientHeight || 0;
    if (w < IFRAME_MIN_SIZE || h < IFRAME_MIN_SIZE) return;
  }

  ensureBadge();

  // SPA 遷移や React 再描画でバッジが消えた場合に復活させる
  const reinjectObserver = new MutationObserver(() => {
    ensureBadge();
  });
  reinjectObserver.observe(document.documentElement, {
    childList: true,
    subtree: true,
  });

  // ============================================================
  // バッジ DOM 注入
  // ============================================================
  function ensureBadge() {
    if (!document.body) return;
    if (document.getElementById(BADGE_ID)) return;

    const wrap = document.createElement("div");
    wrap.id = BADGE_ID;
    wrap.innerHTML = `
      <button class="srd-btn" title="返信漏れトーク一覧を開く">
        <span class="srd-icon">📩</span>
        <span class="srd-label">返信漏れ</span>
        <span class="srd-count">-</span>
      </button>
      <div class="srd-panel" style="display:none">
        <div class="srd-panel-header">
          <span>📩 返信漏れトーク</span>
          <div class="srd-panel-actions">
            <button class="srd-refresh" title="再取得">🔄</button>
            <button class="srd-close" title="閉じる">✕</button>
          </div>
        </div>
        <div class="srd-panel-body"></div>
        <div class="srd-panel-footer">15秒ごとに自動更新</div>
      </div>
    `;
    document.body.appendChild(wrap);

    const openBtn = wrap.querySelector(".srd-btn");
    const dropdown = wrap.querySelector(".srd-panel");
    const body = wrap.querySelector(".srd-panel-body");
    const countEl = wrap.querySelector(".srd-count");

    openBtn.addEventListener("click", () => {
      const willOpen = dropdown.style.display === "none";
      dropdown.style.display = willOpen ? "flex" : "none";
      if (willOpen) renderList();
    });
    wrap.querySelector(".srd-close").addEventListener("click", () => {
      dropdown.style.display = "none";
    });
    wrap.querySelector(".srd-refresh").addEventListener("click", renderList);

    function renderList() {
      const items = findUnrepliedTalks();
      countEl.textContent = items.length;
      body.innerHTML = "";
      if (items.length === 0) {
        const empty = document.createElement("div");
        empty.className = "srd-empty";
        empty.textContent = "返信漏れはありません 🎉";
        body.appendChild(empty);
        return;
      }
      // 未読件数が多い順
      items.sort((a, b) => b.unread - a.unread);
      for (const item of items) {
        const row = document.createElement("div");
        row.className = "srd-item";

        const nameRow = document.createElement("div");
        nameRow.className = "srd-item-name";
        nameRow.textContent = item.name;

        const badge = document.createElement("span");
        badge.className = "srd-item-badge";
        badge.textContent = item.unread;
        nameRow.appendChild(badge);

        const preview = document.createElement("div");
        preview.className = "srd-item-preview";
        preview.textContent = item.preview;

        row.appendChild(nameRow);
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

    setTimeout(() => {
      if (dropdown.style.display === "flex") renderList();
      else updateCountOnly();
    }, 1500);

    setInterval(() => {
      if (dropdown.style.display === "flex") renderList();
      else updateCountOnly();
    }, 15000);
  }

  // ============================================================
  // 未返信トーク検出（LINE 側 DOM が変わっても壊れにくいよう
  // 複数のセレクタ候補＋未読バッジ要素のヒューリスティック検出）
  // ============================================================
  function findUnrepliedTalks() {
    const rowCandidates = new Set();
    const rowSelectors = [
      '[class*="ChatList"] li',
      '[class*="TalkList"] li',
      '[class*="chatList"] li',
      '[class*="talkList"] li',
      '[class*="ChatRoom"]',
      '[class*="chatRoom"]',
      '[class*="ChatItem"]',
      '[class*="chatItem"]',
      '[role="listitem"]',
      'li[class*="item"]',
      'a[href*="/chat/"]',
    ];
    for (const sel of rowSelectors) {
      try {
        document.querySelectorAll(sel).forEach((el) => rowCandidates.add(el));
      } catch (_) {}
    }

    const results = [];
    const seenText = new Set();
    for (const el of rowCandidates) {
      if (!isVisible(el)) continue;

      // 未読バッジ的要素を探す（class 名に badge/unread/count を含み
      // テキストが 1〜3 桁の数字）
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
      const key = text.slice(0, 80);
      if (seenText.has(key)) continue;
      seenText.add(key);

      const lines = text.split("\n").map((l) => l.trim()).filter(Boolean);
      const filtered = lines.filter((l) => !/^\d{1,3}$/.test(l));
      const name = filtered[0] || "(名前不明)";
      const preview = (filtered.slice(1, 3).join(" / ") || "").slice(0, 80);

      results.push({ el, name, preview, unread });
    }
    return results;
  }

  function isVisible(el) {
    if (!el) return false;
    if (el.offsetParent !== null) return true;
    // <a> など display:contents の場合に offsetParent が null になり得る
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }
})();
