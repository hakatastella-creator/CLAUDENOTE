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
def amount_cell(x, bold=False):
    k = kanji(x)
    sub = f'<span class="kj">（{k}）</span>' if k else ""
    return f'<td class="{"b" if bold else ""}">{yen(x)}{sub}</td>'


def bars(rows, fmt=yen, color=None, max_v=None):
    """rows: [(label, value, sub)]  横棒グラフ（SVGを使わずCSSで描画）"""
    rows = [r for r in rows if r[1]]
    if not rows:
        return '<div class="empty">データなし</div>'
    m = max_v or max(r[1] for r in rows)
    out = []
    for r in rows:
        label, v = r[0], r[1]
        sub = r[2] if len(r) > 2 and r[2] else ""
        w = max(1.5, v / m * 100)
        style = f"width:{w:.1f}%" + (f";background:{color}" if color else "")
        out.append(
            f'<div class="bar"><div class="bl">{esc(label)}</div>'
            f'<div class="bt"><div class="bf" style="{style}"></div></div>'
            f'<div class="bv">{fmt(v)}{f"<small>{esc(sub)}</small>" if sub else ""}</div></div>'
        )
    return '<div class="bars">' + "".join(out) + "</div>"


def pair_bars(rows, prev_label, cur_label, fmt):
    """前月・当月の比較棒"""
    m = max(max(p, c) for _, p, c in rows) or 1
    out = [f'<div class="pl"><span class="sw prev"></span>{esc(prev_label)}'
           f'<span class="sw cur"></span>{esc(cur_label)}</div>']
    for label, p, c in rows:
        out.append(
            f'<div class="bar pair"><div class="bl">{esc(label)}</div><div class="bt">'
            f'<div class="bf prev" style="width:{max(1.5, p / m * 100):.1f}%"></div>'
            f'<div class="bf" style="width:{max(1.5, c / m * 100):.1f}%"></div></div>'
            f'<div class="bv">{fmt(p)}<br>{fmt(c)}</div></div>'
        )
    return '<div class="bars">' + "".join(out) + "</div>"


def kpi(label, value, sub="", extra=""):
    return (f'<div class="kpi"><div class="kl">{label}</div><div class="kv">{value}</div>'
            f'{extra}<div class="ks">{sub}</div></div>')


def diff_n(d, unit=""):
    return ("+" if d > 0 else "±" if d == 0 else "") + f"{d:,}{unit}"


def diff_pt(d):
    v = rnd(d * 100, 1)
    return ("+" if v > 0 else "±" if v == 0 else "") + f"{v:.1f}pt"


# ---------------------------------------------------------------- 本体
def build(d):
    r = d["rececon"]
    hoken = r["points"] * 10
    jihi = r["jihi"]
    hanbai = r["hanbai"]
    sales = hoken + jihi + hanbai
    goal = d.get("goal", 10_000_000)
    rate = sales / goal
    per_day = sales / r["days"]

    # 自費内訳
    cats = d["jihi_items"]
    cat_tot = {c: sum(i[2] for i in items) for c, items in cats.items()}
    item_total = sum(cat_tot.values())
    jdiff = item_total - jihi

    # エアフロー
    af = d["airflow"]
    af_unit = af["amount"] / af["count"] if af["count"] else 0
    af_share = af["amount"] / hanbai if hanbai else 0
    af_gap = af["count"] - af["apotool"]

    # Apotool
    a = d["apotool"]
    pm, cm = d["prev_label"], d["cur_label"]

    def raiin(i):
        return a["yoyaku"][i] - a["cancel"][i]

    def crate(i):
        return a["cancel"][i] / (raiin(i) + a["cancel"][i])

    cr_p, cr_c = crate(0), crate(1)

    # ---- KPI
    gap = sales - goal
    prog = min(rate, 1.5) / 1.5 * 100
    kpis = "".join([
        kpi("月売上", yen(sales), kanji(sales)),
        kpi("目標達成率", pct(rate),
            f"目標 {kanji(goal).replace('約', '')}／{'+' if gap >= 0 else '−'}{kanji(abs(gap)).replace('約', '')}",
            f'<div class="prog"><div style="width:{prog:.1f}%"></div><i style="left:{100 / 1.5:.1f}%"></i></div>'),
        kpi("新患", f"{r['shinkan']:,} 人", f"診療日数 {r['days']}日・平均点数 {r['avg_points']:,}点"),
        kpi("キャンセル率", pct(cr_c), f"前月 {pct(cr_p)}（{diff_pt(cr_c - cr_p)}）"),
    ])

    # ---- 売上
    sales_tbl = f"""
    <table class="rep">
      <thead><tr><th class="lab">項目</th><th>数量</th><th>金額</th></tr></thead>
      <tbody>
        <tr><th class="lab">保険（合計点数×10）</th><td>{r['points']:,} 点</td>{amount_cell(hoken)}</tr>
        <tr><th class="lab">自費（個人別 自費請求額）</th><td></td>{amount_cell(jihi)}</tr>
        <tr><th class="lab">販売品目</th><td></td>{amount_cell(hanbai)}</tr>
        <tr class="total"><th class="lab">月売上 合計</th><td></td>{amount_cell(sales, True)}</tr>
        <tr class="sp"><td colspan="3"></td></tr>
        <tr><th class="lab">月目標</th><td></td>{amount_cell(goal)}</tr>
        <tr><th class="lab">目標との差</th><td></td>{amount_cell(gap)}</tr>
        <tr class="sub"><th class="lab">達成率</th><td></td><td class="b">{pct(rate)}</td></tr>
        <tr><th class="lab">1日あたり売上（{r['days']}日）</th><td></td>{amount_cell(per_day)}</tr>
      </tbody>
    </table>"""
    sales_chart = bars([
        ("保険", hoken, pct(hoken / sales)),
        ("自費", jihi, pct(jihi / sales)),
        ("販売品目", hanbai, pct(hanbai / sales)),
    ])

    # ---- 自費内訳
    rows = []
    for c, items in cats.items():
        for name, n, amt in items:
            rows.append(f'<tr><th class="lab ind">{esc(name)}</th><td>{f"{n:,} 件" if n else ""}</td>{amount_cell(amt)}</tr>')
        cn = sum(i[1] or 0 for i in items)
        rows.append(f'<tr class="sub"><th class="lab">{esc(c)} 計</th><td>{cn:,} 件</td>{amount_cell(cat_tot[c], True)}</tr>')
        rows.append('<tr class="sp"><td colspan="3"></td></tr>')
    rows.append(f'<tr class="total"><th class="lab">自費項目別 合計</th><td></td>{amount_cell(item_total, True)}</tr>')
    rows.append(f'<tr><th class="lab">個人別 自費請求額（売上に計上）</th><td></td>{amount_cell(jihi)}</tr>')
    rows.append(f'<tr><th class="lab">差額（値引・訂正と推定）</th><td></td>{amount_cell(jdiff)}</tr>')
    jihi_tbl = ('<table class="rep"><thead><tr><th class="lab">項目</th><th>件数</th><th>金額</th></tr></thead><tbody>'
                + "".join(rows) + "</tbody></table>")
    jihi_chart = (
        '<div class="ct">区分別</div>'
        + bars([(c, v, pct(v / item_total)) for c, v in cat_tot.items()])
        + "".join(
            f'<div class="ct">{esc(c)} 内訳</div>' + bars([(i[0], i[2]) for i in items][:6])
            for c, items in cats.items()
        )
    )

    # ---- エアフロー
    af_tbl = f"""
    <table class="rep">
      <tbody>
        <tr><th class="lab">件数（販売品目）</th><td class="b">{af['count']:,} 件</td></tr>
        <tr><th class="lab">売上</th>{amount_cell(af['amount'], True)}</tr>
        <tr><th class="lab">単価</th>{amount_cell(af_unit)}</tr>
        <tr class="sub"><th class="lab">物販（販売品目）に占める割合</th><td class="b">{pct(af_share)}</td></tr>
        <tr class="sp"><td colspan="2"></td></tr>
        <tr><th class="lab">Apotool イベント登録</th><td>{af['apotool']:,} 件</td></tr>
        <tr><th class="lab">未登録（販売件数 − 登録件数）</th><td class="warn">{af_gap:,} 件</td></tr>
      </tbody>
    </table>"""
    af_chart = '<div class="ct">物販（販売品目）の内訳</div>' + bars([
        ("エアフロー", af["amount"], pct(af_share)),
        ("その他物販", hanbai - af["amount"], pct(1 - af_share)),
    ]) + '<div class="ct">件数：販売 vs Apotool登録</div>' + bars(
        [("販売品目", af["count"]), ("Apotool登録", af["apotool"])], fmt=lambda v: f"{v:,} 件")

    # ---- 予約・キャンセル
    def trow(label, p, c, fmt, dfmt, cls=""):
        return (f'<tr class="{cls}"><th class="lab">{label}</th><td>{fmt(p)}</td><td>{fmt(c)}</td>'
                f'<td class="dim">{dfmt(c, p)}</td></tr>')

    n = lambda u: (lambda v: f"{v:,} {u}")
    dn = lambda u: (lambda c, p: diff_n(c - p, u))
    dp = lambda c, p: diff_pt(c - p)
    apo_tbl = f"""
    <table class="rep">
      <thead><tr><th class="lab">項目</th><th>{pm}</th><th>{cm}</th><th>増減</th></tr></thead>
      <tbody>
        {trow("総予約件数", a['yoyaku'][0], a['yoyaku'][1], n("件"), dn("件"))}
        {trow("来院件数", raiin(0), raiin(1), n("件"), dn("件"))}
        {trow("キャンセル数", a['cancel'][0], a['cancel'][1], n("件"), dn("件"))}
        {trow("キャンセル率", cr_p, cr_c, pct, dp, "sub")}
        <tr class="sp"><td colspan="4"></td></tr>
        {trow("事前キャンセル", a['jizen'][0], a['jizen'][1], n("件"), dn("件"))}
        {trow("当日キャンセル", a['toujitsu'][0], a['toujitsu'][1], n("件"), dn("件"))}
        {trow("無断キャンセル", a['mudan'][0], a['mudan'][1], n("件"), dn("件"))}
      </tbody>
    </table>
    <div class="note">キャンセル率 ＝ キャンセル数 ÷（来院件数＋キャンセル数）。来院件数 ＝ 総予約件数 − キャンセル数。</div>"""
    apo_chart = '<div class="ct">キャンセル内訳（件）</div>' + pair_bars(
        [("事前", *a["jizen"]), ("当日", *a["toujitsu"]), ("無断", *a["mudan"])],
        pm, cm, lambda v: f"{v:,}")

    recall_tbl = f"""
    <table class="rep">
      <thead><tr><th class="lab">項目</th><th>{pm}</th><th>{cm}</th><th>増減</th></tr></thead>
      <tbody>
        {trow("定期検診来院率", a['teiki'][0], a['teiki'][1], pct, dp, "sub")}
        {trow("中断患者数", a['chudan'][0], a['chudan'][1], n("人"), dn("人"))}
      </tbody>
    </table>"""
    recall_chart = '<div class="ct">中断患者数（人）</div>' + pair_bars(
        [("中断患者", *a["chudan"])], pm, cm, lambda v: f"{v:,}")

    # ---- 参考・所見
    wh = d.get("whitening")
    ref = ""
    if wh:
        ref = f"""
        <div class="sec"><h3>参考：ホワイトニング（株式会社ステラ）</h3>
          <table class="rep half"><tbody>
            <tr><th class="lab">{cm} 合計</th>{amount_cell(wh, True)}</tr>
          </tbody></table>
          <div class="note">別法人のため、月売上・達成率には含めていません。</div>
        </div>"""
    memo = "".join(f"<li>{esc(m)}</li>" for m in d.get("memo", []))
    memo_sec = f'<div class="sec"><h3>所見</h3><ul class="memo">{memo}</ul></div>' if memo else ""

    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<title>月次レポート_{d['month']}</title>
<style>{CSS}</style></head><body><div class="page">
  <div class="hd"><div class="clinic">{esc(d['clinic'])}</div><div class="title">月次レポート</div>
    <div class="month">{esc(d['label'])}</div></div>
  <div class="kpis">{kpis}</div>

  <div class="sec"><h3>売上 <span>月売上 ＝ 合計点数×10 ＋ 自費請求額 ＋ 販売品目</span></h3>
    <div class="cols"><div>{sales_tbl}</div>
      <div><div class="ct">売上構成</div>{sales_chart}
        <div class="big">{yen_k(sales)}</div></div></div></div>

  <div class="sec split"><h3>自費の内訳</h3>
    <div class="cols"><div>{jihi_tbl}</div><div>{jihi_chart}</div></div></div>

  <div class="sec"><h3>エアフロー</h3>
    <div class="cols"><div>{af_tbl}</div><div>{af_chart}</div></div></div>

  <div class="sec"><h3>予約・キャンセル（Apotool）</h3>
    <div class="cols"><div>{apo_tbl}</div><div>{apo_chart}</div></div></div>

  <div class="sec"><h3>定期検診・中断（Apotool）</h3>
    <div class="cols"><div>{recall_tbl}</div><div>{recall_chart}</div></div></div>

  {ref}
  {memo_sec}
  <div class="ft">出典：レセコン 日計業務（個人別・自費項目別・販売品目別）／Apotool。金額は千円単位で四捨五入して漢字表記を併記。未収金は含みません。</div>
</div></body></html>"""


CSS = """
@page { size: A4; margin: 12mm 11mm; }
:root { --gold:#B08A2E; --gold-d:#7A5C12; --gold-l:#E9D9AE; --cream:#FBF6E9; --th:#F6EFDC;
        --line:#E3D6B4; --ink:#2F2a1E; --ink2:#5A5243; --muted:#8C826C; }
* { box-sizing: border-box; }
body { margin:0; font-family:"Noto Sans CJK JP","Hiragino Kaku Gothic ProN","Yu Gothic",Meiryo,sans-serif;
       color:var(--ink); background:#fff; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.page { width:100%; }
.hd { border-bottom:3px solid var(--gold); padding-bottom:8px; margin-bottom:14px; }
.clinic { font-size:12px; color:var(--ink2); }
.title { font-size:22px; font-weight:800; margin:1px 0; }
.month { font-size:15px; font-weight:700; color:var(--gold-d); }
.kpis { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:18px; }
.kpi { border:1px solid var(--line); border-top:4px solid var(--gold); border-radius:10px; padding:10px 12px;
       background:linear-gradient(180deg,var(--cream) 0%,#fff 70%); }
.kl { font-size:10.5px; font-weight:700; color:var(--ink2); }
.kv { font-size:21px; font-weight:800; color:var(--gold-d); line-height:1.25; margin:2px 0 1px;
      font-variant-numeric:tabular-nums; white-space:nowrap; }
.ks { font-size:9.5px; color:var(--muted); }
.prog { position:relative; height:5px; background:#EFE6CC; border-radius:3px; margin:3px 0 4px; }
.prog div { height:100%; background:var(--gold); border-radius:3px; }
.prog i { position:absolute; top:-2px; width:1.5px; height:9px; background:var(--gold-d); }
.sec { margin:0 0 16px; break-inside:avoid; }
.sec.split { break-inside:auto; }
.sec h3 { font-size:13.5px; font-weight:700; color:var(--gold-d); border-left:4px solid var(--gold);
          padding-left:8px; margin:0 0 8px; }
.sec h3 span { font-size:10px; font-weight:400; color:var(--muted); margin-left:8px; }
.cols { display:grid; grid-template-columns:1.25fr 1fr; gap:16px; align-items:start; }
table.rep { width:100%; border-collapse:collapse; font-size:11px; }
table.rep.half { width:52%; }
table.rep th, table.rep td { border:1px solid var(--line); padding:3px 6px; }
table.rep thead th { background:var(--th); color:var(--ink2); text-align:right; font-weight:700; }
table.rep thead th.lab { text-align:left; }
table.rep th.lab { background:var(--th); text-align:left; font-weight:600; color:var(--ink2); white-space:nowrap; }
table.rep th.ind { font-weight:400; padding-left:12px; background:#FBF8EF; }
table.rep td { text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }
table.rep td.b { font-weight:700; }
table.rep td.dim { color:var(--ink2); }
table.rep td.warn { color:#9A5B12; font-weight:700; }
.kj { font-size:8.5px; color:var(--muted); font-weight:400; margin-left:2px; }
table.rep tr.sub th, table.rep tr.sub td { background:#F8F1DE; font-weight:700; }
table.rep tr.total th, table.rep tr.total td { background:var(--gold-l); font-weight:800; color:var(--ink); }
table.rep tr.sp td { border:none; height:6px; padding:0; }
.ct { font-size:10.5px; color:var(--muted); margin:8px 0 3px; }
.ct:first-child { margin-top:0; }
.bars { display:flex; flex-direction:column; gap:4px; }
.bar { display:grid; grid-template-columns:128px 1fr 92px; align-items:center; gap:6px; font-size:10px; }
.bl { color:var(--ink2); text-align:right; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.bt { height:11px; }
.bf { height:11px; background:var(--gold); border-radius:0 3px 3px 0; }
.bar.pair .bt { height:auto; display:flex; flex-direction:column; gap:2px; }
.bar.pair .bf { height:8px; }
.bf.prev, .sw.prev { background:#DCCB9A; }
.sw { display:inline-block; width:9px; height:9px; background:var(--gold); margin:0 3px 0 10px; vertical-align:-1px; }
.pl { font-size:9.5px; color:var(--muted); text-align:right; margin-bottom:2px; }
.bv { font-weight:700; font-variant-numeric:tabular-nums; white-space:nowrap; }
.bv small { font-weight:400; color:var(--muted); margin-left:4px; }
.bar.pair .bv { font-size:9px; line-height:1.15; }
.big { margin-top:12px; padding:9px 10px; border:1px solid var(--line); border-radius:8px; background:var(--cream);
       font-size:13px; font-weight:800; color:var(--gold-d); text-align:center; }
.note { font-size:9.5px; color:var(--muted); margin-top:4px; }
.empty { font-size:10px; color:var(--muted); }
ul.memo { margin:0; padding-left:18px; font-size:11px; line-height:1.7; }
.ft { margin-top:10px; padding-top:6px; border-top:1px solid var(--line); font-size:9px; color:var(--muted); }
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
