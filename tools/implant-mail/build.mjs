/*
 * インプラント予定患者表「要対応の朝メール」の本文を組み立てる。
 *
 *   node tools/implant-mail/build.mjs <ライブ版index.htmlのパス> [YYYY-MM-DD]
 *
 * 判定ロジックはこのファイルに持たない。引数で渡した index.html の中から
 * SEQ / nextOf() / rankOf() をそのまま切り出して実行する。
 * 表を直せばメールの基準も自動で追従する（＝二重管理をしない）。
 *
 * 標準出力に {subject, text, html, count, lateCount, targets} の JSON を出す。
 * 該当0件なら count:0。そのときはメールを送らないこと。
 */
import fs from "node:fs";

const URL_TABLE = "https://claude.ai/artifact/3iqndAxU3UZKVmM1jLY2jf";
const CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩⑪";

/* ---------- ページ本体からロジックを借りてくる ---------- */

function sliceBetween(src, startMark, endMark, what){
  const a = src.indexOf(startMark);
  if(a < 0) throw new Error(`index.html の中に ${what} の開始目印が見つかりません: ${startMark}`);
  const b = src.indexOf(endMark, a);
  if(b < 0) throw new Error(`index.html の中に ${what} の終了目印が見つかりません: ${endMark}`);
  return src.slice(a, b);
}

function loadLogic(html, todayStr){
  // 定数（GUIDE_DAYS 〜 STALE_DAYS）と、日付の道具 〜 rankOf() までを切り出す。
  // その間に KR_HOLIDAYS / STEPS / SEQ / nextOf / arriveOf も入っている。
  const consts = sliceBetween(html, "var LS_STATE", "var cases = [], deleted = [];", "定数");
  const logic  = sliceBetween(html, "/* ---------- 日付の道具 ---------- */",
                                    "/* ---------- 保存（このページ自身に書き込む） ---------- */", "判定ロジック");
  // today() はコンテナの時刻（UTC）を返すので、日本時間の今日で上書きする。
  const override = `\n today = function(){ return ${JSON.stringify(todayStr)}; };\n`;
  const src = consts + logic + override +
              " return { nextOf: nextOf, rankOf: rankOf, today: today, STEPS: STEPS, SEQ: SEQ };";
  return new Function(src)();
}

function loadData(html){
  const m = html.match(/<script id="implant-data"[^>]*>([\s\S]*?)<\/script>/);
  if(!m) throw new Error("index.html の中に <script id=\"implant-data\"> が見つかりません");
  return JSON.parse(m[1]);
}

/* ---------- 表示の道具 ---------- */

const WD = ["日","月","火","水","木","金","土"];
function parts(s){
  const p = String(s || "").split("-");
  if(p.length !== 3) return null;
  const d = new Date(Date.UTC(+p[0], +p[1]-1, +p[2]));
  return { y:+p[0], m:+p[1], d:+p[2], w: WD[d.getUTCDay()] };
}
const md   = s => { const p = parts(s); return p ? `${p.m}/${p.d}` : ""; };
const long = s => { const p = parts(s); return p ? `${p.m}月${p.d}日（${p.w}）` : ""; };
const esc  = s => String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");

// 緊急度ごとの色。late と today は赤、soon は橙、window は青、stale は灰。
const TONE = {
  late:   { bar:"#dc2626", pillBg:"#fee2e2", pillFg:"#991b1b" },
  today:  { bar:"#dc2626", pillBg:"#fee2e2", pillFg:"#991b1b" },
  soon:   { bar:"#d97706", pillBg:"#fef3c7", pillFg:"#92400e" },
  window: { bar:"#0284c7", pillBg:"#e0f2fe", pillFg:"#075985" },
  stale:  { bar:"#64748b", pillBg:"#e2e8f0", pillFg:"#334155" }
};
const tone = k => TONE[k] || TONE.stale;

// 遅れているときは表と同じく lateLabel に差し替える（index.html の描画と同じ扱い）。
function labelOf(a, r){ return (r.kind === "late" && a.lateLabel) ? a.lateLabel : a.label; }

// 期限の書き方。window は「時期の幅」なので期限とは言わない。
function dueLine(a, r){
  if(a.window) {
    return r.kind === "late"
      ? `${long(a.window.to)} を ${r.text}（連絡の時期を過ぎています）`
      : `${long(a.window.from)} 〜 ${long(a.window.to)} が連絡の時期です`;
  }
  if(a.due) return `${long(a.due)}　${r.text}`;
  if(a.since) return `${long(a.since)} から ${r.text}`;
  return r.text;
}

function memosOf(e, steps){
  const out = [];
  steps.forEach((st, i) => {
    const v = (e[st.memo] || "").trim();
    if(v) out.push({ no: CIRCLED[i] || String(i+1), nm: st.nm, text: v });
  });
  return out;
}

/* ---------- 組み立て ---------- */

function build(html, todayStr){
  const L = loadLogic(html, todayStr);
  const data = loadData(html);

  const targets = [];
  for(const e of (data.cases || [])){
    const a = L.nextOf(e);
    const r = L.rankOf(a);
    if(r.rank <= 2) targets.push({ e, a, r });
  }
  // 遅れを先に、次いで期限の早い順。
  const ORDER = { late:0, today:1, soon:2, window:3, stale:4 };
  const dueKey = t => t.a.due || (t.a.window && t.a.window.to) || t.a.since || "9999-99-99";
  targets.sort((x, y) =>
    (ORDER[x.r.kind] ?? 9) - (ORDER[y.r.kind] ?? 9) || dueKey(x).localeCompare(dueKey(y)));

  const n = targets.length;
  const late = targets.filter(t => t.r.kind === "late").length;
  if(n === 0) return { count:0, lateCount:0, subject:"", text:"", html:"", targets:[] };

  // 件名は固定の形。`インプラント要対応` の並びは Gmail の振り分けに使うので変えない。
  const subject = late > 0
    ? `🦷ステラ インプラント要対応 ${n}件 🔴遅れ${late}件（${md(todayStr)}）`
    : `🦷ステラ インプラント要対応 ${n}件（${md(todayStr)}）`;

  /* --- プレーンテキスト版（HTMLを表示できない環境用） --- */
  const tl = [`${long(todayStr)}時点で、対応が必要なインプラント患者が ${n} 名います。`, ""];
  for(const { e, a, r } of targets){
    tl.push(`■ ${e.name} 様（カルテ ${e.patientNo}／${e.site || "部位未記入"}）　${r.text}`);
    tl.push(`　次にやること：${labelOf(a, r)}`);
    tl.push(`　${dueLine(a, r)}`);
    if(a.caution) tl.push(`　${a.caution.text}`);
    for(const m of memosOf(e, L.STEPS)) tl.push(`　${m.no}${m.nm}のメモ：${m.text}`);
    tl.push("");
  }
  tl.push("インプラント予定患者表", URL_TABLE);
  const text = tl.join("\n");

  /* --- HTML版 --- */
  const cards = targets.map(({ e, a, r }) => {
    const t = tone(r.kind);
    const memos = memosOf(e, L.STEPS).map(m =>
      `<div style="margin-top:6px;font-size:12px;line-height:1.6;color:#475569;background:#f8fafc;border-radius:6px;padding:8px 10px;">`
      + `<span style="color:#94a3b8;">${m.no}${esc(m.nm)}</span>　${esc(m.text)}</div>`).join("");
    const caution = a.caution
      ? `<div style="margin-top:8px;font-size:12px;line-height:1.6;color:${a.caution.major ? "#991b1b" : "#92400e"};`
        + `background:${a.caution.major ? "#fef2f2" : "#fffbeb"};border-radius:6px;padding:8px 10px;">`
        + `${esc(a.caution.text)}</div>`
      : "";
    return `
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:separate;margin:0 0 12px;">
        <tr>
          <td style="background:#ffffff;border:1px solid #e2e8f0;border-left:4px solid ${t.bar};border-radius:8px;padding:14px 16px;">
            <div style="font-size:11px;font-weight:700;color:${t.pillFg};background:${t.pillBg};display:inline-block;padding:3px 10px;border-radius:99px;">${esc(r.text)}</div>
            <div style="margin-top:8px;font-size:17px;font-weight:700;color:#0f172a;">${esc(e.name)} 様</div>
            <div style="margin-top:2px;font-size:12px;color:#64748b;">カルテ ${esc(e.patientNo)}　／　${esc(e.site || "部位未記入")}</div>
            <div style="margin-top:10px;font-size:15px;line-height:1.6;color:#0f172a;font-weight:700;">${esc(labelOf(a, r))}</div>
            <div style="margin-top:4px;font-size:13px;line-height:1.6;color:#475569;">${esc(dueLine(a, r))}</div>
            ${caution}${memos}
          </td>
        </tr>
      </table>`;
  }).join("");

  const headline = late > 0
    ? `要対応 ${n}件（うち遅れ ${late}件）`
    : `要対応 ${n}件`;

  const htmlBody = `<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(subject)}</title></head>
<body style="margin:0;padding:0;background:#eef2f5;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#eef2f5;">
<tr><td align="center" style="padding:16px 12px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;font-family:'Hiragino Kaku Gothic ProN','Yu Gothic','Meiryo',sans-serif;">
  <tr><td style="background:${late > 0 ? "#b91c1c" : "#0f766e"};border-radius:10px 10px 0 0;padding:16px 18px;">
    <div style="font-size:18px;font-weight:700;color:#ffffff;">${esc(headline)}</div>
    <div style="margin-top:3px;font-size:12px;color:#ffffff;opacity:.85;">インプラント予定患者表　${esc(long(todayStr))}</div>
  </td></tr>
  <tr><td style="background:#ffffff;border:1px solid #dbe3ea;border-top:0;border-radius:0 0 10px 10px;padding:16px;">
    ${cards}
    <a href="${URL_TABLE}" style="display:block;margin-top:4px;padding:13px;text-align:center;background:#0f766e;color:#ffffff;text-decoration:none;font-size:15px;font-weight:700;border-radius:8px;">表をひらいて入力する</a>
    <div style="margin-top:14px;font-size:11px;line-height:1.7;color:#94a3b8;">
      このメールは表の「要対応」と同じ基準で、対応が必要な患者がいる日の朝だけ届きます。<br>
      該当がない日は送られません。
    </div>
  </td></tr>
</table>
</td></tr></table>
</body></html>`;

  return { count:n, lateCount:late, subject, text, html:htmlBody,
           targets: targets.map(t => ({ name:t.e.name, kind:t.r.kind, text:t.r.text,
                                        label: labelOf(t.a, t.r) })) };
}

/* ---------- 実行 ---------- */

const [, , htmlPath, dateArg] = process.argv;
if(!htmlPath){
  console.error("使い方: node tools/implant-mail/build.mjs <index.htmlのパス> [YYYY-MM-DD]");
  process.exit(2);
}
// 日付を省いたら日本時間の今日。コンテナは UTC なので必ず Asia/Tokyo で出す。
const todayStr = dateArg ||
  new Intl.DateTimeFormat("sv-SE", { timeZone:"Asia/Tokyo" }).format(new Date());

console.log(JSON.stringify(build(fs.readFileSync(htmlPath, "utf8"), todayStr), null, 1));
