"""シフト表CSVから、指定した人の出勤日を「かわいい」カード型カレンダー画像(PNG)にする。

使い方:
    python3 cute_calendar.py <シフト表.csv> <出力.png> --names 阿比留,片山 [--title 受付シフト]
        [--note "年末年始は…休診です。"]

- 1人なら出勤日のマスを色で塗る(患者さん向けの「院長診療日」と同じデザイン)
- 複数人なら、マスの中に人ごとの色のラベルを並べる(AM/PM は小さく添える)
- 休診日(全員休み)はグレー
- 画像は Playwright(Chromium)で描く。フォントは Google Fonts の Zen Maru Gothic
"""
import argparse
import calendar
import datetime
import html
import json
import subprocess
import tempfile
from pathlib import Path

from make_calendar import read_csv, holidays_around

COLORS = ["#2f6f8f", "#d97a6c", "#3f8a6b", "#8a6bb8", "#c79a2e"]
PART = {"A": "AM", "P": "PM", "フ": ""}
WD = "月火水木金土日"


def build_days(year, month, ndays, sections, names):
    people = {n: c for _, ps in sections for n, c in ps}
    days = {}
    for d in range(1, ndays + 1):
        closed = all(c[d - 1] == "休" for _, ps in sections for _, c in ps)
        on = [(n, PART[people[n][d - 1]]) for n in names if people[n][d - 1] != "休"]
        days[d] = {"closed": closed, "on": on}
    return days


def render_html(year, month, ndays, days, names, title, lead, note):
    colors = {n: COLORS[i % len(COLORS)] for i, n in enumerate(names)}
    single = len(names) == 1
    hol = holidays_around(year)
    first = datetime.date(year, month, 1)
    cells = ['<div class="c empty"></div>'] * first.weekday()
    for d in range(1, ndays + 1):
        dt = datetime.date(year, month, d)
        cls = ["c"]
        if dt.weekday() == 5:
            cls.append("sat")
        if dt.weekday() == 6 or dt in hol:
            cls.append("sun")
        info = days[d]
        body = ""
        style = ""
        if info["closed"]:
            cls.append("closed")
            body = '<span class="off">休診</span>'
        elif info["on"]:
            if single:
                n, part = info["on"][0]
                cls.append("on")
                style = f' style="background:{colors[n]}"'
                body = f'<span class="pill" style="color:{colors[n]}">{html.escape(n)}</span>'
                if part:
                    body += f'<span class="part">{part}のみ</span>'
            else:
                cls.append("work")
                body = "".join(
                    f'<span class="tag" style="background:{colors[n]}">{html.escape(n)}'
                    f'{f"<small>{part}</small>" if part else ""}</span>'
                    for n, part in info["on"])
        cells.append(f'<div class="{" ".join(cls)}"{style} data-day="{d}" '
                     f'data-on=\'{json.dumps(info["on"], ensure_ascii=False)}\' '
                     f'data-closed="{int(info["closed"])}"><span class="num">{d}</span>{body}</div>')
    while len(cells) % 7:
        cells.append('<div class="c empty"></div>')
    rows = len(cells) // 7
    head = "".join(f'<div class="{"sat" if i == 5 else "sun" if i == 6 else ""}">{w}</div>'
                   for i, w in enumerate(WD))
    legend = "".join(f'<span><span class="sw" style="background:{colors[n]}"></span>{html.escape(n)}</span>'
                     for n in names)
    legend += '<span><span class="sw" style="background:#e9e6e1"></span>休診日</span>'
    main = colors[names[0]]
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@500;700;900&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:1350px;background:#f6f3ee;font-family:'Zen Maru Gothic',sans-serif;color:#3a3a3a}}
.wrap{{padding:64px 64px 48px;height:100%;display:flex;flex-direction:column}}
.clinic{{font-size:30px;font-weight:700;color:{main};letter-spacing:.08em}}
h1{{font-size:64px;font-weight:900;margin-top:14px;line-height:1.25}}
h1 em{{font-style:normal;color:{main}}}
.lead{{font-size:28px;margin-top:14px;color:#555}}
.cal{{margin-top:36px;background:#fff;border-radius:28px;padding:28px 24px 24px;box-shadow:0 6px 24px rgba(0,0,0,.06)}}
.head,.grid{{display:grid;grid-template-columns:repeat(7,1fr);gap:10px}}
.head div{{text-align:center;font-size:26px;font-weight:700;padding-bottom:12px;color:#666}}
.head .sat{{color:#3d6fd1}} .head .sun{{color:#d9534f}}
.c{{height:{118 if rows <= 5 else 100}px;border-radius:18px;background:#fbfaf8;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px}}
.c.empty{{background:transparent}}
.num{{font-size:36px;font-weight:700;line-height:1}}
.c.sat .num{{color:#3d6fd1}} .c.sun .num{{color:#d9534f}}
.c.on .num{{color:#fff}}
.pill{{font-size:22px;font-weight:700;background:#fff;border-radius:999px;padding:2px 14px}}
.part{{font-size:18px;color:#fff;font-weight:700}}
.c.work{{justify-content:flex-start;padding-top:12px;gap:4px}}
.c.work .num{{font-size:30px;margin-bottom:2px}}
.tag{{font-size:18px;font-weight:700;color:#fff;border-radius:999px;padding:1px 10px;white-space:nowrap;line-height:1.35}}
.tag small{{font-size:14px;margin-left:4px;opacity:.95}}
.c.closed{{background:#e9e6e1}} .c.closed .num{{color:#aaa}}
.off{{font-size:22px;color:#999;font-weight:700}}
.legend{{display:flex;gap:36px;justify-content:center;margin-top:34px;font-size:26px;align-items:center}}
.sw{{display:inline-block;width:34px;height:34px;border-radius:10px;vertical-align:middle;margin-right:10px}}
.notes{{margin-top:auto;font-size:24px;line-height:1.7;color:#555;text-align:center}}
</style></head><body><div class="wrap">
<div class="clinic">博多ステラ歯科</div>
<h1>{month}月の<em>{html.escape(title)}</em></h1>
{f'<p class="lead">{html.escape(lead)}</p>' if lead else ''}
<div class="cal"><div class="head">{head}</div><div class="grid">{''.join(cells)}</div></div>
<div class="legend">{legend}</div>
<div class="notes">{html.escape(note) if note else ''}</div>
</div></body></html>"""


SHOT_JS = r"""
const { chromium } = require('playwright');
(async () => {
  const [src, out] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  await p.goto('file://' + src);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(500);
  const cells = await p.$$eval('[data-day]', els => els.map(e => {
    const r = e.getBoundingClientRect();
    const over = [...e.children].some(k => { const q = k.getBoundingClientRect();
      return q.left < r.left - 1 || q.right > r.right + 1 || q.top < r.top - 1 || q.bottom > r.bottom + 1; });
    return { day: +e.dataset.day, on: JSON.parse(e.dataset.on), closed: e.dataset.closed === '1',
             text: e.innerText, over };
  }));
  await p.screenshot({ path: out });
  console.log(JSON.stringify(cells));
  await b.close();
})();
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("out")
    ap.add_argument("--names", required=True, help="カンマ区切り。例: 阿比留,片山")
    ap.add_argument("--title", help="見出し(省略時は「〇〇の出勤日」)")
    ap.add_argument("--lead", default="")
    ap.add_argument("--note", default="※予定は変更になる場合があります。")
    a = ap.parse_args()

    year, month, ndays, sections = read_csv(a.csv)
    names = [n.strip() for n in a.names.replace("、", ",").split(",") if n.strip()]
    known = {n for _, ps in sections for n, _ in ps}
    missing = [n for n in names if n not in known]
    if missing:
        raise SystemExit(f"CSVにいない名前: {'・'.join(missing)}")
    days = build_days(year, month, ndays, sections, names)
    title = a.title or f"{'・'.join(names)}の出勤日"
    page = render_html(year, month, ndays, days, names, title, a.lead, a.note)

    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "cal.html").write_text(page, encoding="utf-8")
        Path(tmp, "shot.js").write_text(SHOT_JS, encoding="utf-8")
        r = subprocess.run(["node", f"{tmp}/shot.js", f"{tmp}/cal.html", str(Path(a.out).resolve())],
                           check=True, capture_output=True, text=True, timeout=120, cwd=tmp)
    cells = json.loads(r.stdout.strip().splitlines()[-1])

    # 描いた画像の各マスを、CSVと照合する
    people = {n: c for _, ps in sections for n, c in ps}
    errors = []
    if [c["day"] for c in cells] != list(range(1, ndays + 1)):
        errors.append("日付が欠けている/重複している")
    for c in cells:
        d = c["day"]
        exp = [[n, PART[people[n][d - 1]]] for n in names if people[n][d - 1] != "休"]
        closed = all(cc[d - 1] == "休" for cc in people.values())
        if c["closed"] != closed or (not closed and c["on"] != exp):
            errors.append(f"{month}/{d}: 画像={c['on']} CSV={exp}")
        if not closed:
            for n, part in exp:
                if n not in c["text"] or (part and part not in c["text"]):
                    errors.append(f"{month}/{d}: 「{n}{part}」が表示されていない")
        if c["over"]:
            errors.append(f"{month}/{d}: 文字がマスからはみ出している")
    if errors:
        raise SystemExit("照合エラー:\n" + "\n".join(errors))
    print(f"照合OK: {len(names)}人 × {ndays}日、食い違い0件")
    print(f"画像: {a.out}")


if __name__ == "__main__":
    main()
