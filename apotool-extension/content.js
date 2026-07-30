/**
 * アポツールの各画面に「🗓 月次レポート出力」パネルを注入する。
 *
 * 流れ:
 *   1. ②クリニックデータ ③全ての予約 ④イベント の各画面で「取り込む」
 *   2. 取り込んだ項目を確認・手直し（PIIは除外済み）→「この画面を保存」
 *   3. どの画面からでも「Excel出力」で3画面分をまとめた月次.xlsxをダウンロード
 *
 * データは chrome.storage.local に月(YYYY-MM)・画面ごとに保存。
 */
(function () {
  "use strict";

  const PANEL_ID = "stella-monthly-panel";
  if (document.getElementById(PANEL_ID)) return;
  if (!window.__apoScrape || !window.__apoXlsx) return;

  const SCREENS = window.__apoScrape.SCREENS;
  const STORAGE_KEY = "apotoolMonthly";
  const CLINIC_NAME = "博多ステラ歯科";

  const screenKey = window.__apoScrape.screenKeyFromPath(location.pathname);

  // ============================================================
  // ユーティリティ
  // ============================================================
  function currentMonth() {
    const d = new Date();
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0");
  }

  function monthLabel(ym) {
    const [y, m] = (ym || "").split("-");
    return y && m ? `${y}年${Number(m)}月` : ym;
  }

  function loadAll() {
    return new Promise((resolve) => {
      chrome.storage.local.get([STORAGE_KEY], (data) => resolve(data[STORAGE_KEY] || {}));
    });
  }

  function saveAll(all) {
    return new Promise((resolve) => {
      chrome.storage.local.set({ [STORAGE_KEY]: all }, resolve);
    });
  }

  function toNumberOrString(v) {
    // "1,234" -> 1234（数値）, "3.2%" -> そのまま文字列
    if (v == null) return "";
    const s = String(v).trim();
    if (/^-?[\d,]+(\.\d+)?$/.test(s)) {
      const n = Number(s.replace(/,/g, ""));
      if (isFinite(n)) return n;
    }
    return s;
  }

  // ============================================================
  // パネル UI
  // ============================================================
  const panel = document.createElement("div");
  panel.id = PANEL_ID;
  panel.innerHTML = `
    <div class="smp-header">
      <span>🗓 月次レポート出力</span>
      <button class="smp-toggle" title="折りたたみ">＿</button>
    </div>
    <div class="smp-body">
      <div class="smp-row">
        <label>対象月</label>
        <input type="month" class="smp-month" />
      </div>

      <div class="smp-screen">
        <div class="smp-screen-name"></div>
        <div class="smp-actions-top">
          <button class="smp-btn smp-capture">🔍 画面から自動取り込み</button>
        </div>
        <details class="smp-paste-wrap">
          <summary>うまく取れない時は「貼り付けて解析」</summary>
          <textarea class="smp-paste" placeholder="画面のKPI部分をドラッグ選択してコピー→ここに貼り付け→下のボタン。&#10;例)&#10;キャンセル率 3.2%&#10;無断キャンセル 5&#10;総予約件数 1234"></textarea>
          <button class="smp-btn smp-parse">📋 貼り付けを解析</button>
        </details>
      </div>

      <div class="smp-list-head">
        <span>取り込んだ項目（確認・手直しできます）</span>
        <button class="smp-btn-mini smp-add">＋行</button>
      </div>
      <div class="smp-list"></div>

      <div class="smp-actions">
        <button class="smp-btn smp-save">💾 この画面を保存</button>
      </div>

      <div class="smp-captured"></div>

      <div class="smp-actions">
        <button class="smp-btn smp-export">📊 Excel出力（まとめて）</button>
        <button class="smp-btn smp-clear">🗑 今月分を消去</button>
      </div>

      <div class="smp-status"></div>
      <div class="smp-note">※ 集計値・ラベルのみを扱います。患者の氏名・電話番号などは取り込みません。</div>
    </div>
  `;
  document.body.appendChild(panel);

  const $ = (sel) => panel.querySelector(sel);
  const monthInput = $(".smp-month");
  const listEl = $(".smp-list");
  const statusEl = $(".smp-status");
  const capturedEl = $(".smp-captured");
  const screenNameEl = $(".smp-screen-name");

  monthInput.value = currentMonth();

  // 折りたたみ
  const body = $(".smp-body");
  $(".smp-toggle").addEventListener("click", () => {
    const hidden = body.style.display === "none";
    body.style.display = hidden ? "flex" : "none";
    $(".smp-toggle").textContent = hidden ? "＿" : "▢";
  });

  // 画面名の表示
  if (screenKey) {
    screenNameEl.innerHTML = `この画面：<b>${SCREENS[screenKey].label}</b> <span class="smp-dim">${SCREENS[screenKey].hint}</span>`;
  } else {
    screenNameEl.innerHTML = `<span class="smp-warn">この画面は対象外です。②クリニックデータ / ③全ての予約 / ④イベント のいずれかを開いてください。<br>（貼り付け解析は使えます）</span>`;
  }

  function setStatus(msg, type) {
    statusEl.textContent = msg || "";
    statusEl.className = "smp-status " + (type || "");
  }

  // ============================================================
  // 項目リスト（編集可能）
  // ============================================================
  function renderList(items) {
    listEl.innerHTML = "";
    (items || []).forEach((it) => addRow(it.name, it.value));
    if (!items || !items.length) addRow("", "");
  }

  function addRow(name, value) {
    const row = document.createElement("div");
    row.className = "smp-item";
    row.innerHTML = `
      <input class="smp-item-name" placeholder="項目名" />
      <input class="smp-item-value" placeholder="値" />
      <button class="smp-btn-mini smp-del" title="削除">✕</button>
    `;
    row.querySelector(".smp-item-name").value = name || "";
    row.querySelector(".smp-item-value").value = value || "";
    row.querySelector(".smp-del").addEventListener("click", () => row.remove());
    listEl.appendChild(row);
  }

  function readList() {
    const items = [];
    listEl.querySelectorAll(".smp-item").forEach((row) => {
      const name = row.querySelector(".smp-item-name").value.trim();
      const value = row.querySelector(".smp-item-value").value.trim();
      if (name || value) items.push({ name, value });
    });
    return items;
  }

  $(".smp-add").addEventListener("click", () => addRow("", ""));

  // ============================================================
  // 取り込み状況の表示
  // ============================================================
  async function refreshCaptured() {
    const all = await loadAll();
    const month = monthInput.value;
    const rec = all[month] || {};
    const parts = [];
    for (const key of ["clinic", "reservation", "event"]) {
      const has = rec[key] && rec[key].items && rec[key].items.length;
      parts.push(
        `<span class="smp-chip ${has ? "ok" : ""}">${SCREENS[key].label}：${has ? rec[key].items.length + "項目" : "未取込"}</span>`
      );
    }
    capturedEl.innerHTML = `<div class="smp-captured-title">${monthLabel(month)} の取込状況</div>${parts.join("")}`;
  }

  // 月を変えたら、その月・この画面の保存済みデータをリストに反映
  async function loadCurrentIntoList() {
    if (!screenKey) {
      renderList([]);
      return;
    }
    const all = await loadAll();
    const rec = (all[monthInput.value] || {})[screenKey];
    renderList(rec ? rec.items : []);
  }

  monthInput.addEventListener("change", async () => {
    await loadCurrentIntoList();
    await refreshCaptured();
  });

  // ============================================================
  // ボタン: 自動取り込み / 貼り付け解析 / 保存
  // ============================================================
  $(".smp-capture").addEventListener("click", () => {
    if (!screenKey) {
      setStatus("この画面は自動取り込み対象外です。貼り付け解析をお使いください。", "error");
      return;
    }
    const items = window.__apoScrape.harvest(screenKey);
    if (!items.length) {
      setStatus("自動で拾えませんでした。「貼り付けて解析」をお試しください。", "error");
      return;
    }
    // 既存の入力に追記マージ（重複は名前+値で除外）
    const existing = readList();
    const seen = new Set(existing.map((i) => i.name + "::" + i.value));
    for (const it of items) {
      const k = it.name + "::" + it.value;
      if (!seen.has(k)) {
        existing.push(it);
        seen.add(k);
      }
    }
    renderList(existing);
    setStatus(`${items.length} 件の候補を取り込みました。内容を確認してください。`, "ok");
  });

  $(".smp-parse").addEventListener("click", () => {
    const text = $(".smp-paste").value;
    const items = window.__apoScrape.parsePasted(text);
    if (!items.length) {
      setStatus("解析できる行が見つかりませんでした。「ラベル 数値」の形で貼り付けてください。", "error");
      return;
    }
    const existing = readList();
    const seen = new Set(existing.map((i) => i.name + "::" + i.value));
    for (const it of items) {
      const k = it.name + "::" + it.value;
      if (!seen.has(k)) {
        existing.push(it);
        seen.add(k);
      }
    }
    renderList(existing);
    setStatus(`${items.length} 件を解析しました。内容を確認してください。`, "ok");
  });

  $(".smp-save").addEventListener("click", async () => {
    if (!screenKey) {
      setStatus("保存先の画面が特定できません。②③④のいずれかで保存してください。", "error");
      return;
    }
    const items = readList();
    if (!items.length) {
      setStatus("保存する項目がありません。", "error");
      return;
    }
    const all = await loadAll();
    const month = monthInput.value;
    all[month] = all[month] || {};
    all[month][screenKey] = {
      label: SCREENS[screenKey].label,
      items,
      capturedAt: new Date().toISOString(),
    };
    await saveAll(all);
    await refreshCaptured();
    setStatus(`「${SCREENS[screenKey].label}」を ${monthLabel(month)} 分として保存しました（${items.length}項目）。`, "ok");
  });

  // ============================================================
  // Excel 出力
  // ============================================================
  // 取り込んだ項目から先頭の数値を取り出す（"12件"→12, "11人"→11）
  function firstInt(items, includes, excludes) {
    for (const it of items || []) {
      const n = it.name || "";
      if (excludes && excludes.some((e) => n.includes(e))) continue;
      if (includes.some((k) => n.includes(k))) {
        const m = String(it.value).replace(/,/g, "").match(/-?\d+(?:\.\d+)?/);
        if (m) return parseFloat(m[0]);
      }
    }
    return null;
  }

  function pct(a, b) {
    if (a == null || b == null || b === 0) return null;
    return Math.round((a / b) * 1000) / 10 + "%";
  }

  // 件数から率・合計を自動計算（画面の率表示に頼らず算出する）
  function computeMetrics(rec) {
    const ev = (rec.event && rec.event.items) || [];
    const cl = (rec.clinic && rec.clinic.items) || [];
    const out = [];

    const soudan = firstInt(ev, ["相談"]);
    const kensa = firstInt(ev, ["検査"], ["再検査"]);
    const keiyaku = firstInt(ev, ["契約"]);
    if (soudan != null && kensa != null) {
      const p = pct(kensa, soudan);
      if (p) out.push({ name: "相談→検査率（検査÷相談）", value: p });
    }
    if (soudan != null && keiyaku != null) {
      const p = pct(keiyaku, soudan);
      if (p) out.push({ name: "矯正成約率（契約÷相談）", value: p });
    }

    const chiryo = firstInt(cl, ["治療中断"]);
    const recall = firstInt(cl, ["リコール中断"]);
    if (chiryo != null && recall != null) {
      out.push({ name: "当月中断合計（治療＋リコール, 人）", value: chiryo + recall });
    }
    return out;
  }

  function buildRows(month, rec) {
    const rows = [];
    rows.push([{ v: `${CLINIC_NAME}　月次レポート（自動集計）　${monthLabel(month)}`, bold: true }]);
    rows.push([]);

    const order = [
      ["event", "■ 診療ステップ件数（イベント：矯正の相談〜保定）"],
      ["clinic", "■ リコール・予約・キャンセル（クリニックデータ）"],
      ["reservation", "■ 予約区分（全ての予約）"],
    ];

    let any = false;
    for (const [key, heading] of order) {
      const sec = rec[key];
      if (!sec || !sec.items || !sec.items.length) continue;
      any = true;
      rows.push([{ v: heading, bold: true }]);
      rows.push([{ v: "項目", bold: true }, { v: "値", bold: true }]);
      for (const it of sec.items) {
        rows.push([it.name, toNumberOrString(it.value)]);
      }
      rows.push([]);
    }

    const computed = computeMetrics(rec);
    if (computed.length) {
      rows.push([{ v: "▶ 算出指標（件数から自動計算）", bold: true }]);
      rows.push([{ v: "項目", bold: true }, { v: "値", bold: true }]);
      for (const it of computed) {
        rows.push([it.name, toNumberOrString(it.value)]);
      }
      rows.push([]);
    }

    rows.push([]);
    rows.push([{ v: "出典：アポツール（画面表示の集計値）。売上金額・患者個人情報は含みません。" }]);
    rows.push([{ v: "作成日時：" + new Date().toLocaleString("ja-JP") }]);
    return { rows, any };
  }

  function download(bytes, filename) {
    const blob = new Blob([bytes], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }

  $(".smp-export").addEventListener("click", async () => {
    const all = await loadAll();
    const month = monthInput.value;
    const rec = all[month];
    if (!rec) {
      setStatus(`${monthLabel(month)} の保存データがありません。先に各画面で取り込み→保存してください。`, "error");
      return;
    }
    const { rows, any } = buildRows(month, rec);
    if (!any) {
      setStatus("出力できる項目がありません。", "error");
      return;
    }
    try {
      const bytes = window.__apoXlsx.build("月次レポート", rows);
      download(bytes, `月次レポート_${month}_${CLINIC_NAME}.xlsx`);
      setStatus(`Excelを出力しました：月次レポート_${month}_${CLINIC_NAME}.xlsx`, "ok");
    } catch (e) {
      setStatus("Excel生成でエラー: " + e.message, "error");
    }
  });

  $(".smp-clear").addEventListener("click", async () => {
    const month = monthInput.value;
    if (!confirm(`${monthLabel(month)} の保存データ（②③④すべて）を消去します。よろしいですか？`)) return;
    const all = await loadAll();
    delete all[month];
    await saveAll(all);
    renderList([]);
    await refreshCaptured();
    setStatus(`${monthLabel(month)} 分を消去しました。`, "ok");
  });

  // ============================================================
  // 初期表示
  // ============================================================
  (async function init() {
    await loadCurrentIntoList();
    await refreshCaptured();
  })();
})();
