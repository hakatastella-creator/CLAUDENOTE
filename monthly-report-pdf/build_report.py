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
    v = d["visits"]
    hoken = r["points"] * 10
    jihi = r["jihi"]           # 個人別 自費請求額（売上に計上）
    hanbai = r["hanbai"]
    total = hoken + jihi + hanbai
    goal = d.get("goal", 10_000_000)
    rate = total / goal

    groups = d["sales"]
    for g in groups:
        g["sum"] = sum(i[2] for i in g["items"])
        g["n"] = sum(i[1] or 0 for i in g["items"])
    cn_n, cn_amt = d["cancel_fee"]
    jihi_items = sum(g["sum"] for g in groups) + cn_amt   # 自費総額（レセコン項目別）
    adj = jihi - jihi_items

    a = d["apotool"]
    pm, cm = d["prev_label"], d["cur_label"]
    raiin_apo = [a["yoyaku"][i] - a["cancel"][i] for i in (0, 1)]
    crate = [a["cancel"][i] / (raiin_apo[i] + a["cancel"][i]) for i in (0, 1)]

    o = d["ortho"]
    start_n = sum(n for _, n in o["start"])
    start_sub = "・".join(f"{k}{n}" for k, n in o["start"]) or "内訳なし"

    # ---- KPI（8月と同じ4枚）
    kpis = "".join([
        kpi("合計売上高", yen(total), f"{kanji(total)}・達成率 {pct(rate)}"),
        kpi("来院人数", f"{v['raiin']:,} 人", f"新患 {v['shinkan']:,}・自費 {v['jihi_n']:,}"),
        kpi("キャンセル率", pct(crate[1]), f"前月 {pct(crate[0])}（{diff_pt(crate[1] - crate[0])}）"),
        kpi("矯正開始", f"{start_n:,} 件", start_sub),
    ])

    # ---- 売上（8月と同じ並び）
    rows = [["保険点数（売上）", f"{r['points']:,} 点", amt(hoken)], "sp"]
    notes = []
    for g in groups:
        if g["items"]:
            rows += [[n, cnt(c), amt(x)] for n, c, x, _ in g["items"]]
        else:
            rows += [[f"{g['name']}（該当なし）", "", '<td class="dim">—</td>']]
        rows += [[f"{g['name']} 計", cnt(g["n"]), amt(g["sum"], True), "sub"], "sp"]
        if g.get("notes"):
            notes.append(g["notes"])
        if g.get("empty_note"):
            notes.append(f"{g['name']}：{g['empty_note']}")
    rows += [["キャンセル料", cnt(cn_n), amt(cn_amt)],
             ["物販（販売品目）", cnt(r.get("hanbai_n")), amt(hanbai)], "sp"]
    rows += [["自費総額（項目別）", "", amt(jihi_items, True), "sub"],
             ["差額（個人別との差）", "", amt(adj)],
             ["自費請求額（個人別）", "", amt(jihi, True), "sub"], "sp"]
    rows += [["合計売上高", "", amt(total, True), "total"],
             ["月目標", "", amt(goal)],
             ["達成率", "", f'<td class="b">{pct(rate)}</td>', "sub"]]
    sales_tbl = table3(rows) + "".join(f'<div class="note">※{esc(n)}</div>' for n in notes)
    cat = [("保険点数", hoken)] + [(g["name"], g["sum"]) for g in groups] + [("物販", hanbai)]
    sales_chart = '<div class="ct">売上構成（カテゴリ別）</div>' + bars(cat)
    for g in groups:
        if g["items"]:
            sales_chart += f'<div class="ct">{esc(g["name"])} 内訳</div>' + bars([(i[3], i[2]) for i in g["items"]])
    sales_chart += ('<div class="note">合計売上高 ＝ 保険点数×10 ＋ 自費請求額（個人別） ＋ 物販（販売品目）。'
                    '未収金は含みません。</div>')

    # ---- 予約・来院／初再診・キャンセル（8月と同じ）
    shosai = v["shinkan"] + v["saisho"] + v["saishin"]
    jihi_rate = v["jihi_n"] / (v["jihi_n"] + v["hoken_n"])
    raiin_tbl = (
        kv([["来院人数", f"{v['raiin']:,} 人"]])
        + '<div style="height:6px"></div>'
        + kv([["新患", f"{v['shinkan']:,} 人"], ["再初診", f"{v['saisho']:,} 人"],
              ["再診", f"{v['saishin']:,} 人"], ["初再診 計", f"{shosai:,} 人", "sub"]])
        + '<div style="height:6px"></div>'
        + f"""<table class="rep"><thead><tr><th class="lab">キャンセル（Apotool）</th><th>{pm}</th><th>{cm}</th></tr></thead><tbody>
          <tr class="sub"><th class="lab">キャンセル率</th><td>{pct(crate[0])}</td><td>{pct(crate[1])}</td></tr>
          <tr><th class="lab">キャンセル数</th><td>{a['cancel'][0]:,} 件</td><td>{a['cancel'][1]:,} 件</td></tr>
          <tr><th class="lab">事前</th><td>{a['jizen'][0]:,} 件</td><td>{a['jizen'][1]:,} 件</td></tr>
          <tr><th class="lab">当日</th><td>{a['toujitsu'][0]:,} 件</td><td>{a['toujitsu'][1]:,} 件</td></tr>
          <tr><th class="lab">無断</th><td>{a['mudan'][0]:,} 件</td><td>{a['mudan'][1]:,} 件</td></tr>
          </tbody></table>
          <div class="note">キャンセル率 ＝ キャンセル数 ÷（来院件数＋キャンセル数）、来院件数 ＝ 総予約{a['yoyaku'][1]:,}件 − キャンセル数</div>"""
    )
    raiin_chart = (
        '<div class="ct">初再診 内訳（人）</div>'
        + bars([("新患", v["shinkan"]), ("再初診", v["saisho"]), ("再診", v["saishin"])], fmt=lambda x: f"{x:,}")
        + '<div class="ct">自費・保険</div>'
        + kv([["自費件数", f"{v['jihi_n']:,} 件"], ["保険件数", f"{v['hoken_n']:,} 件"],
              ["自費率", pct(jihi_rate), "sub"]])
        + '<div class="note">自費件数＝自費来院人数、保険件数＝保険来院人数（レセコン個人別）</div>'
    )

    # ---- 矯正（8月と同じ）
    ortho_tbl = kv([["矯正開始（フル・モデ・ライト・EX）", f"{start_n:,} 件", "sub"]]
                   + [[k, f"{n:,} 件"] for k, n in o["rows"]])
    ortho_chart = '<div class="ct">矯正 件数（種類別）</div>' + bars(o["rows"], fmt=lambda x: f"{x:,}")

    # ---- リコール（8月と同じ）
    rc = d["recall"]
    rc_val = lambda x: f"{x:,} 件" if x is not None else '<span class="dim">要確認（Apotool）</span>'
    recall_tbl = kv([["リコール件数", rc_val(rc["recall"])], ["リコオリ件数", rc_val(rc["recall_ori"])]])
    recall_chart = ('<div class="ct">リコール・リコオリ（件）</div>'
                    + bars([("リコール", rc["recall"] or 0), ("リコオリ", rc["recall_ori"] or 0)],
                           fmt=lambda x: f"{x:,}"))

    # ---- エアフロー（毎月）
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
                + bars([("販売", af["count"]), ("Apotool登録", af["apotool"])], fmt=lambda x: f"{x:,}"))

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
  {sec("予約・来院／初再診・キャンセル", raiin_tbl, raiin_chart)}
  {sec("矯正", ortho_tbl, ortho_chart)}
  {sec("リコール", recall_tbl, recall_chart)}
  {sec("エアフロー", af_tbl, af_chart)}
  {ref}
  {memo_sec}
  <div class="ft">出典：レセコン 日計業務（個人別・自費項目別・販売品目別）／Apotool（クリニックデータ）。金額の（約〜）は千円単位で四捨五入。未収金は含みません。患者個人情報は含みません。</div>
</div></body></html>"""


CSS = """
@page { size: A4; margin: 10mm 12mm; }
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
.sec { margin:0 0 13px; break-inside:avoid; }
.sec h3 { font-size:13.5px; font-weight:700; color:var(--green-d); border-left:4px solid var(--green);
          padding-left:8px; margin:0 0 8px; }
.cols { display:grid; grid-template-columns:1fr 1fr; gap:16px; align-items:start; }
table.rep { width:100%; border-collapse:collapse; font-size:11px; }
table.rep th, table.rep td { border:1px solid var(--line); padding:2.6px 8px; }
table.rep th { background:var(--th); text-align:left; font-weight:600; color:var(--ink2); white-space:nowrap; }
table.rep thead th { text-align:right; } table.rep thead th.lab { text-align:left; }
table.rep td { text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }
table.rep td.b { font-weight:700; }
.dim, table.rep td.dim { color:var(--muted); font-weight:400; }
table.rep tr.sub th, table.rep tr.sub td { background:var(--sub); font-weight:700; }
table.rep tr.total th, table.rep tr.total td { background:var(--total); font-weight:700; }
table.rep tr.sp td { border:none; height:6px; padding:0; background:#fff; }
.kj { font-size:8.5px; color:var(--muted); font-weight:400; margin-left:2px; }
.ct { font-size:10.5px; color:var(--muted); margin:9px 0 3px; }
.chart > .ct:first-child { margin-top:0; }
.bars { display:flex; flex-direction:column; gap:5px; }
.bar { display:grid; grid-template-columns:84px 1fr; align-items:center; gap:6px; font-size:9.5px; }
.bl { color:var(--ink2); text-align:right; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.bt { display:flex; align-items:center; gap:5px; }
.bf { height:11px; background:var(--series); border-radius:0 2px 2px 0; }
.bv { font-weight:700; font-variant-numeric:tabular-nums; white-space:nowrap; font-size:9.5px; }
.note { font-size:9.5px; color:var(--muted); margin-top:6px; }
.empty { font-size:10px; color:var(--muted); }
ul.memo { margin:0; padding-left:18px; font-size:10.5px; line-height:1.6; }
.ft { margin-top:6px; padding-top:5px; border-top:1px solid var(--line); font-size:9px; color:var(--muted); }
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
