/**
 * アポツールの画面から「集計値のみ」を取り出すためのヘルパー群。
 *
 * 重要な設計方針:
 *  - 患者の個人情報（氏名・電話番号・生年月日など）は取り込まない。
 *    数値の抽出前に PII らしきテキストを除外する。
 *  - DOM の正確な構造は環境で変わりうるため、
 *    「自動取り込み（キーワード）」＋「貼り付けて解析」の2系統で拾い、
 *    最後に人が確認・編集する前提のヒューリスティック実装。
 *
 * window.__apoScrape に公開:
 *   screenKeyFromPath(path) -> "clinic" | "reservation" | "event" | null
 *   SCREENS                 -> 画面メタ情報
 *   harvest(screenKey)      -> [{name, value}]   画面からの自動抽出
 *   parsePasted(text)       -> [{name, value}]   貼り付けテキストの解析
 */
(function () {
  "use strict";

  // 画面ごとのメタ情報とキーワード
  const SCREENS = {
    clinic: {
      label: "クリニックデータ",
      hint: "/user/dashboard/（マンスリーレポート）",
      keywords: [
        "キャンセル率",
        "無断キャンセル",
        "事前キャンセル",
        "当日キャンセル",
        "予約未定率",
        "予約未定者率",
        "定期検診来院率",
        "定期検診",
        "来院人数",
        "来院数",
        "来院率",
        "総予約件数",
        "予約件数",
        "自費件数",
        "保険件数",
        "自費率",
        "予約取得率",
        "対象者数",
        "予約者数",
        "キャンセル後",
        "中断患者",
        "中断メニュー",
        "患者ランク",
        "目標",
      ],
    },
    reservation: {
      label: "全ての予約",
      hint: "/user/patient/reservation（今月の予約サマリ）",
      keywords: [
        "予約総数",
        "今月の予約",
        "予約件数",
        "自費",
        "保険",
        "Cure",
        "Care",
        "Web予約",
        "ウェブ予約",
        "新規",
        "既存",
        "再診",
      ],
    },
    event: {
      label: "イベント",
      hint: "/user/event/（メニュー別 月間件数）",
      keywords: [
        "矯正相談",
        "検査",
        "治療計画説明",
        "保定コンサル",
        "リコール",
        "コンサル",
        "説明",
        "相談",
        "件",
      ],
    },
  };

  function screenKeyFromPath(path) {
    const p = path || "";
    if (p.includes("/user/dashboard")) return "clinic";
    if (p.includes("/user/patient/reservation")) return "reservation";
    if (p.includes("/user/event")) return "event";
    return null;
  }

  // ---- PII（患者個人情報）判定 ---------------------------------------
  // 電話番号 / 携帯 / 生年月日らしき並び、氏名+様 などを弾く
  const PHONE_RE = /0\d{1,4}[-\s]?\d{1,4}[-\s]?\d{3,4}/;
  const DOB_RE = /(19|20)\d{2}[\/\-年]\s?\d{1,2}[\/\-月]\s?\d{1,2}/;
  const NAME_RE = /[^\s]{1,10}\s?(様|さん)$/;

  function containsPII(text) {
    if (!text) return false;
    if (PHONE_RE.test(text)) return true;
    if (DOB_RE.test(text)) return true;
    if (NAME_RE.test(text)) return true;
    return false;
  }

  // ---- 数値抽出補助 ---------------------------------------------------
  const NUM_RE = /-?[\d,]+(?:\.\d+)?\s?[%％]?/;

  function firstNumber(text) {
    const m = (text || "").match(NUM_RE);
    return m ? normalizeValue(m[0]) : "";
  }

  function normalizeValue(raw) {
    return String(raw).replace(/\s+/g, "").replace(/％/g, "%");
  }

  function cleanLabel(text, keyword) {
    // ラベルが長すぎる/数値混じりならキーワードを優先
    let t = (text || "").replace(/\s+/g, " ").trim();
    // ラベル末尾から数値部分を落とす
    t = t.replace(/[:：]?\s*-?[\d,]+(?:\.\d+)?\s?[%％]?\s*(件|人|回|名)?\s*$/, "").trim();
    if (!t || t.length > 24 || /^\d/.test(t)) return keyword;
    return t;
  }

  // ---- 画面からの自動取り込み ----------------------------------------
  function harvest(screenKey) {
    const meta = SCREENS[screenKey];
    if (!meta) return [];
    const keywords = meta.keywords;
    const results = [];
    const seen = new Set();

    const els = document.body ? document.body.querySelectorAll("*") : [];
    for (const el of els) {
      // 大きなコンテナは飛ばす（見出し＋数値の小さな塊だけ狙う）
      if (el.children.length > 4) continue;
      let txt = "";
      try {
        txt = (el.innerText || "").trim();
      } catch (e) {
        continue;
      }
      if (!txt || txt.length > 60) continue;
      if (containsPII(txt)) continue;

      for (const kw of keywords) {
        if (!txt.includes(kw)) continue;

        let value = firstNumber(txt);
        if (!value) {
          // 同じ要素に数値が無ければ隣接要素を軽く見る
          const sib = el.nextElementSibling;
          if (sib) {
            let st = "";
            try {
              st = (sib.innerText || "").trim();
            } catch (e) {
              st = "";
            }
            if (st && st.length < 24 && !containsPII(st)) value = firstNumber(st);
          }
        }
        if (!value) break;

        const name = cleanLabel(txt, kw);
        const key = name + "::" + value;
        if (!seen.has(key)) {
          seen.add(key);
          results.push({ name, value });
        }
        break;
      }
    }
    return results;
  }

  // ---- 貼り付けテキストの解析 ----------------------------------------
  // 「ラベル 数値(%/件/人)」または「ラベル行→数値行」を拾う
  function parsePasted(text) {
    const lines = (text || "")
      .split(/\r?\n/)
      .map((l) => l.trim())
      .filter(Boolean);

    const out = [];
    const inline = /^(.+?)[\s:：]+(-?[\d,]+(?:\.\d+)?)\s?([%％])?\s*(件|人|回|名)?\s*$/;
    const numOnly = /^(-?[\d,]+(?:\.\d+)?)\s?([%％])?\s*(件|人|回|名)?$/;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (containsPII(line)) continue;

      const m = line.match(inline);
      if (m) {
        const pct = m[3] ? "%" : "";
        out.push({ name: m[1].trim(), value: normalizeValue(m[2] + pct) });
        continue;
      }

      // 数値だけの行 → 直前の非数値行をラベルとして対にする
      const nm = line.match(numOnly);
      if (nm && i > 0) {
        const prev = lines[i - 1];
        if (prev && !/\d/.test(prev.replace(/\s/g, "")) && !containsPII(prev)) {
          const pct = nm[2] ? "%" : "";
          out.push({ name: prev, value: normalizeValue(nm[1] + pct) });
        }
      }
    }
    return out;
  }

  window.__apoScrape = {
    SCREENS,
    screenKeyFromPath,
    harvest,
    parsePasted,
    containsPII,
  };
})();
