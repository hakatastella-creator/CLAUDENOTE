"""博多ステラ歯科 月次レポート（PDF）生成

使い方:
    python monthly-report-pdf/build_report.py monthly-report-pdf/data/2026-10.json

data/YYYY-MM.json を毎月1つ追加 → 実行すると 月次レポート_YYYY-MM.pdf ができる。
（Playwright + Chromium で A4 PDF に出力）
"""

import html
import json
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

HERE = Path(__file__).parent


# ---------------------------------------------------------------- 表記
def rnd(x, n=0):
    q = Decimal(1).scaleb(-n)
    return float(Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP))


def yen(x):
    return ("-" if x < 0 else "") + f"¥{abs(round(x)):,}"


def kanji(x):
    """約1,105万4千円（千円単位で四捨五入）"""
    t = int(rnd(abs(x) / 1000))
    if t == 0:
        return ""
    man, sen = divmod(t, 10)
    s = (f"{man:,}万" if man else "") + (f"{sen}千" if sen else "")
    return f"約{s}円"


def yen_k(x):
    """¥11,053,540（約1,105万4千円）"""
    k = kanji(x)
    return f"{yen(x)}（{k}）" if k else yen(x)


def pct(x, n=1):
    return f"{rnd(x * 100, n):.{n}f}%"


def esc(s):
    return html.escape(str(s))


# ---------------------------------------------------------------- 部品
def amt(x, bold=False):
    k = kanji(x)
    sub = f'<span class="kj">（{k}）</span>' if k else ""
    return f'<td class="{"b" if bold else ""}">{yen(x)}{sub}</td>'


def cnt(n, unit="件"):
    return f"{n:,} {unit}" if n else ""


def bars(rows, fmt=yen):
    """rows: [(label, value)]  参考レポートと同じ横棒（値は棒の右）"""
    rows = [r for r in rows if r[1]]
    if not rows:
        return '<div class="empty">データなし</div>'
    m = max(r[1] for r in rows)
    out = []
    for label, v in rows:
        w = max(1.0, v / m * 72)
        out.append(
            f'<div class="bar"><div class="bl">{esc(label)}</div><div class="bt">'
            f'<div class="bf" style="width:{w:.1f}%"></div><span class="bv">{fmt(v)}</span></div></div>'
        )
    return '<div class="bars">' + "".join(out) + "</div>"


def table3(rows, head=("項目", "件数", "金額")):
    """rows: [label, cnt_html, amount_td_html, cls] / "sp" """
    body = []
    for r in rows:
        if r == "sp":
            body.append('<tr class="sp"><td colspan="3"></td></tr>')
            continue
        label, c, a_td, cls = (list(r) + [""])[:4]
        body.append(f'<tr class="{cls}"><th class="lab">{esc(label)}</th><td>{c}</td>{a_td}</tr>')
    h = "".join(f'<th class="{"lab" if i == 0 else ""}">{esc(x)}</th>' for i, x in enumerate(head))
    return f'<table class="rep"><thead><tr>{h}</tr></thead><tbody>{"".join(body)}</tbody></table>'


def kv(rows):
    """rows: [label, value, cls] / "sp" """
    body = []
    for r in rows:
        if r == "sp":
            body.append('<tr class="sp"><td colspan="2"></td></tr>')
            continue
        label, v, cls = (list(r) + [""])[:3]
        body.append(f'<tr class="{cls}"><th class="lab">{esc(label)}</th><td>{v}</td></tr>')
    return f'<table class="rep"><tbody>{"".join(body)}</tbody></table>'


def kpi(label, value, sub=""):
    return (f'<div class="kpi"><div class="kl">{label}</div><div class="kv">{value}</div>'
            f'<div class="ks">{sub}</div></div>')


def diff_n(d, unit=""):
    return ("+" if d > 0 else "±" if d == 0 else "") + f"{d:,}{unit}"


def diff_pt(d):
    v = rnd(d * 100, 1)
    return ("+" if v > 0 else "±" if v == 0 else "") + f"{v:.1f}pt"


def sec(title, left, right):
    return (f'<div class="sec"><h3>{title}</h3><div class="cols"><div>{left}</div>'
            f'<div class="chart">{right}</div></div></div>')


# ---------------------------------------------------------------- 本体
def build(d):
    r = d["rececon"]
    s = d["sales"]
    hoken = r["points"] * 10
    jihi = r["jihi"]           # 個人別 自費請求額（売上に計上）
    hanbai = r["hanbai"]
    total = hoken + jihi + hanbai
    goal = d.get("goal", 10_000_000)
    rate = total / goal

    ky = s["矯正"]
    jh = s["自費"]
    cn_n, cn_amt = s["キャンセル料"]
    ky_sum = sum(i[2] for i in ky)
    jh_sum = sum(i[2] for i in jh)
    ky_n = sum(i[1] or 0 for i in ky)
    jh_n = sum(i[1] or 0 for i in jh)
    jihi_items = ky_sum + jh_sum + cn_amt          # 自費総額（項目別）
    adj = jihi - jihi_items                        # 値引・訂正（推定）

    a = d["apotool"]
    pm, cm = d["prev_label"], d["cur_label"]
    raiin = [a["yoyaku"][i] - a["cancel"][i] for i in (0, 1)]
    crate = [a["cancel"][i] / (raiin[i] + a["cancel"][i]) for i in (0, 1)]

    starts = d.get("ortho_start", [])
    start_n = sum(n for _, n in starts)
    start_sub = "・".join(f"{k}{n}" for k, n in starts) or "内訳なし"

    # ---- KPI
    kpis = "".join([
        kpi("合計売上高", yen(total), f"{kanji(total)}・達成率 {pct(rate)}"),
        kpi("来院件数", f"{raiin[1]:,} 件", f"新患 {r['shinkan']:,}・診療日数 {r['days']}日"),
        kpi("キャンセル率", pct(crate[1]), f"前月 {pct(crate[0])}（{diff_pt(crate[1] - crate[0])}）"),
        kpi("矯正開始", f"{start_n:,} 件", start_sub),
    ])

    # ---- 売上
    rows = [["保険点数（売上）", f"{r['points']:,} 点", amt(hoken)], "sp"]
    rows += [[n, cnt(c), amt(v)] for n, c, v, _ in ky]
    rows += [["矯正 計", cnt(ky_n), amt(ky_sum, True), "sub"], "sp"]
    rows += [[n, cnt(c), amt(v)] for n, c, v, _ in jh]
    rows += [["自費 計", cnt(jh_n), amt(jh_sum, True), "sub"], "sp"]
    rows += [["キャンセル料", cnt(cn_n), amt(cn_amt)], "sp"]
    rows += [["自費総額（項目別）", "", amt(jihi_items, True), "sub"],
             ["値引・訂正（推定）", "", amt(adj)],
             ["自費請求額（個人別）", "", amt(jihi, True), "sub"], "sp"]
    rows += [["物販（販売品目）", cnt(r.get("hanbai_n")), amt(hanbai)], "sp"]
    rows += [["合計売上高", "", amt(total, True), "total"],
             ["月目標", "", amt(goal)],
             ["達成率", "", f'<td class="b">{pct(rate)}</td>', "sub"]]
    sales_tbl = table3(rows)
    sales_chart = (
        '<div class="ct">売上構成（カテゴリ別）</div>'
        + bars([("保険点数", hoken), ("矯正", ky_sum), ("自費", jh_sum), ("キャンセル料", cn_amt), ("物販", hanbai)])
        + '<div class="ct">矯正 内訳</div>' + bars([(i[3], i[2]) for i in ky])
        + '<div class="ct">自費 内訳</div>' + bars([(i[3], i[2]) for i in jh])
        + '<div class="note">合計売上高 ＝ 保険点数×10 ＋ 自費請求額（個人別） ＋ 物販。未収金は含みません。</div>'
    )

    # ---- エアフロー
    af = d["airflow"]
    af_unit = af["amount"] / af["count"] if af["count"] else 0
    af_share = af["amount"] / hanbai if hanbai else 0
    af_tbl = kv([
        ["件数（販売品目）", f"{af['count']:,} 件"],
        ["売上", f"{yen(af['amount'])}<span class='kj'>（{kanji(af['amount'])}）</span>"],
        ["単価", yen(af_unit)],
        ["物販に占める割合", pct(af_share), "sub"],
        "sp",
        ["Apotool イベント登録", f"{af['apotool']:,} 件"],
        ["未登録（販売 − 登録）", f"{af['count'] - af['apotool']:,} 件", "sub"],
    ])
    af_chart = ('<div class="ct">物販 内訳</div>'
                + bars([("エアフロー", af["amount"]), ("その他物販", hanbai - af["amount"])])
                + '<div class="ct">件数（販売・Apotool登録）</div>'
                + bars([("販売", af["count"]), ("Apotool登録", af["apotool"])], fmt=lambda v: f"{v:,}"))

    # ---- 予約・来院／キャンセル
    def r3(label, i, fmt, cls=""):
        return f'<tr class="{cls}"><th class="lab">{label}</th><td>{fmt(i[0])}</td><td>{fmt(i[1])}</td></tr>'

    nk = lambda u: (lambda v: f"{v:,} {u}")
    yoyaku_tbl = f"""<table class="rep"><thead><tr><th class="lab">項目</th><th>{pm}</th><th>{cm}</th></tr></thead><tbody>
      {r3("総予約件数", a['yoyaku'], nk("件"))}
      {r3("来院件数", raiin, nk("件"))}
      <tr class="sp"><td colspan="3"></td></tr>
      {r3("キャンセル数", a['cancel'], nk("件"))}
      {r3("事前キャンセル", a['jizen'], nk("件"))}
      {r3("当日キャンセル", a['toujitsu'], nk("件"))}
      {r3("無断キャンセル", a['mudan'], nk("件"))}
      {r3("キャンセル率", crate, pct, "sub")}
    </tbody></table>
    <div class="note">キャンセル率 ＝ キャンセル数 ÷（来院件数＋キャンセル数）／来院件数 ＝ 総予約件数 − キャンセル数</div>"""
    shin_tbl = kv([["新患", f"{r['shinkan']:,} 人"], ["平均点数", f"{r['avg_points']:,} 点"],
                   ["診療日数", f"{r['days']} 日"]])
    yoyaku_chart = ('<div class="ct">キャンセル内訳（件・' + cm + '）</div>'
                    + bars([("事前", a["jizen"][1]), ("当日", a["toujitsu"][1]), ("無断", a["mudan"][1])],
                           fmt=lambda v: f"{v:,}")
                    + '<div class="ct">新患・診療</div>' + shin_tbl)

    # ---- 矯正
    oc = d.get("ortho_counts", [])
    ortho_tbl = kv([["矯正開始（フル・モデ・ライト・EX）", f"{start_n:,} 件", "sub"]]
                   + [[k, f"{n:,} 件"] for k, n in oc])
    ortho_chart = '<div class="ct">矯正 件数（種類別）</div>' + bars(oc, fmt=lambda v: f"{v:,}")

    # ---- リコール（定期検診・中断）
    recall_tbl = f"""<table class="rep"><thead><tr><th class="lab">項目</th><th>{pm}</th><th>{cm}</th></tr></thead><tbody>
      {r3("定期検診来院率", a['teiki'], pct, "sub")}
      {r3("中断患者数", a['chudan'], nk("人"))}
    </tbody></table>"""
    recall_chart = ('<div class="ct">中断患者数（人）</div>'
                    + bars([(pm, a["chudan"][0]), (cm, a["chudan"][1])], fmt=lambda v: f"{v:,}"))

    wh = d.get("whitening")
    ref = ""
    if wh:
        ref = (f'<div class="sec"><h3>参考：ホワイトニング（株式会社ステラ）</h3>'
               + '<div class="cols"><div>' + kv([[f"{cm} 合計", f"{yen(wh)}<span class='kj'>（{kanji(wh)}）</span>"]])
               + '</div><div class="note" style="margin-top:6px">別法人のため合計売上高・達成率には含めていません。</div></div></div>')
    memo = "".join(f"<li>{esc(m)}</li>" for m in d.get("memo", []))
    memo_sec = f'<div class="sec"><h3>所見</h3><ul class="memo">{memo}</ul></div>' if memo else ""

    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<title>月次レポート_{d['month']}</title>
<style>{CSS}</style></head><body><div class="page">
  <div class="hd"><div class="clinic">{esc(d['clinic'])}</div><div class="title">月次レポート</div>
    <div class="month">{esc(d['label'])}</div></div>
  <div class="kpis">{kpis}</div>
  {sec("売上", sales_tbl, sales_chart)}
  {sec("エアフロー", af_tbl, af_chart)}
  {sec("予約・来院／キャンセル", yoyaku_tbl, yoyaku_chart)}
  {sec("矯正", ortho_tbl, ortho_chart)}
  {sec("リコール（定期検診・中断）", recall_tbl, recall_chart)}
  {ref}
  {memo_sec}
  <div class="ft">出典：レセコン 日計業務（個人別・自費項目別・販売品目別）／Apotool（クリニックデータ）。金額の（約〜）は千円単位で四捨五入。未収金は含みません。患者個人情報は含みません。</div>
</div></body></html>"""


CSS = """
@page { size: A4; margin: 12mm 12mm; }
:root { --green:#1f8a5b; --green-d:#176c47; --line:#d5dce3; --ink:#1f2933; --ink2:#52514e;
        --muted:#898781; --series:#2a78d6; --th:#eef4fb; --sub:#f7fafc; --total:#f2f7f4; }
* { box-sizing:border-box; }
body { margin:0; font-family:"Noto Sans CJK JP","Hiragino Kaku Gothic ProN","Yu Gothic",Meiryo,sans-serif;
       color:var(--ink); background:#fff; line-height:1.5; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.hd { border-bottom:3px solid var(--green); padding-bottom:10px; margin-bottom:16px; }
.clinic { font-size:12px; color:var(--ink2); }
.title { font-size:21px; font-weight:800; margin:2px 0; }
.month { font-size:14px; font-weight:700; color:var(--green-d); }
.kpis { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:18px; }
.kpi { border:1px solid var(--line); border-top:4px solid var(--green); border-radius:12px; padding:10px 13px;
       background:linear-gradient(180deg,#f6faf8 0%,#fff 60%); box-shadow:0 1px 3px rgba(0,0,0,.05); }
.kl { font-size:10.5px; font-weight:600; color:var(--ink2); }
.kv { font-size:21px; font-weight:800; color:var(--green-d); line-height:1.2; margin:2px 0 1px;
      font-variant-numeric:tabular-nums; white-space:nowrap; }
.ks { font-size:9.5px; color:var(--muted); }
.sec { margin:0 0 18px; break-inside:avoid; }
.sec h3 { font-size:13.5px; font-weight:700; color:var(--green-d); border-left:4px solid var(--green);
          padding-left:8px; margin:0 0 8px; }
.cols { display:grid; grid-template-columns:1fr 1fr; gap:16px; align-items:start; }
table.rep { width:100%; border-collapse:collapse; font-size:11px; }
table.rep th, table.rep td { border:1px solid var(--line); padding:3.5px 8px; }
table.rep th { background:var(--th); text-align:left; font-weight:600; color:var(--ink2); white-space:nowrap; }
table.rep thead th { text-align:right; } table.rep thead th.lab { text-align:left; }
table.rep td { text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }
table.rep td.b { font-weight:700; }
table.rep tr.sub th, table.rep tr.sub td { background:var(--sub); font-weight:700; }
table.rep tr.total th, table.rep tr.total td { background:var(--total); font-weight:700; }
table.rep tr.sp td { border:none; height:6px; padding:0; background:#fff; }
.kj { font-size:8.5px; color:var(--muted); font-weight:400; margin-left:2px; }
.ct { font-size:10.5px; color:var(--muted); margin:12px 0 4px; }
.chart > .ct:first-child { margin-top:0; }
.bars { display:flex; flex-direction:column; gap:5px; }
.bar { display:grid; grid-template-columns:84px 1fr; align-items:center; gap:6px; font-size:9.5px; }
.bl { color:var(--ink2); text-align:right; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.bt { display:flex; align-items:center; gap:5px; }
.bf { height:11px; background:var(--series); border-radius:0 2px 2px 0; }
.bv { font-weight:700; font-variant-numeric:tabular-nums; white-space:nowrap; font-size:9.5px; }
.note { font-size:9.5px; color:var(--muted); margin-top:6px; }
.empty { font-size:10px; color:var(--muted); }
ul.memo { margin:0; padding-left:18px; font-size:11px; line-height:1.75; }
.ft { margin-top:12px; padding-top:8px; border-top:1px solid var(--line); font-size:9px; color:var(--muted); }
"""


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "data" / "2026-10.json"
    d = json.loads(src.read_text(encoding="utf-8"))
    html_path = HERE / f"月次レポート_{d['month']}.html"
    pdf_path = HERE / f"月次レポート_{d['month']}.pdf"
    html_path.write_text(build(d), encoding="utf-8")

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page()
            pg.goto(html_path.resolve().as_uri())
            pg.pdf(path=str(pdf_path), format="A4", print_background=True, prefer_css_page_size=True)
            b.close()
    except ImportError:
        # Python版が無ければ Node.js の playwright で出力
        import subprocess

        js = (
            "const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();"
            "const p=await b.newPage();await p.goto(process.argv[1]);"
            "await p.pdf({path:process.argv[2],format:'A4',printBackground:true,preferCSSPageSize:true});"
            "await b.close();})();"
        )
        subprocess.run(["node", "-e", js, html_path.resolve().as_uri(), str(pdf_path)], check=True)
    print(pdf_path)


if __name__ == "__main__":
    main()
