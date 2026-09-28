"""Shared design kit: CSS, SVG icons, and HTML helpers for the clinic manuals (A4 PDF via Chromium)."""
import html, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "img")  # product photos
CHROME = "/opt/pw-browsers/chromium"

CAT = {  # treatment categories -> (color, tint, label)
    "cr":   ("#2a78d6", "#e8f1fc", "CR 充填"),
    "core": ("#15966a", "#e3f5ee", "支台築造"),
    "pros": ("#4a3aa7", "#ecebf8", "補綴装着"),
    "sp":   ("#b87a00", "#fdf3dc", "特殊症例"),
}

CSS = r"""
@page { size: A4; margin: 13mm 13mm 15mm 13mm;
  @bottom-center { content: counter(page) " / " counter(pages); font: 8pt "Noto Sans CJK JP"; color: #8a96a3; }
  @top-right { content: string(doctitle); font: 7.5pt "Noto Sans CJK JP"; color: #a0aab5; }
}
@page cover { margin: 0; @bottom-center { content: none } @top-right { content: none } }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font-family: "Noto Sans CJK JP", sans-serif; font-size: 9pt; line-height: 1.5; color: #1d2733; }
.doctitle { string-set: doctitle content(); display: none; }
b, strong { font-weight: 700; }
.muted { color: #6b7785; }
small { font-size: 7.6pt; color: #6b7785; }

/* ---------- chapter / section ---------- */
.chapter { break-before: page; display: flex; align-items: center; gap: 10px; margin: 0 0 10px; padding: 9px 14px;
  border-radius: 10px; color: #fff; background: var(--c); }
.chapter .no { font-size: 20pt; font-weight: 900; line-height: 1; opacity: .9 }
.chapter .t { font-size: 15pt; font-weight: 700; }
.chapter .d { margin-left: auto; font-size: 8.3pt; opacity: .92; max-width: 55%; text-align: right; line-height: 1.4 }
.chapter svg.ci { width: 30px; height: 30px; }
.sec { display: flex; align-items: baseline; gap: 8px; margin: 14px 0 6px; padding-bottom: 4px; border-bottom: 2px solid var(--c, #1f3a5f); break-after: avoid; }
.sec .no { font-weight: 900; color: var(--c, #1f3a5f); font-size: 11pt }
.sec .t { font-weight: 700; font-size: 12pt; }
.sec .tag { margin-left: 6px; font-size: 7.5pt; font-weight: 700; padding: 1px 7px; border-radius: 99px; background: #eceff3; color: #6b7785; }
.nobreak { break-inside: avoid; }

/* ---------- key point / caution ---------- */
.point { display: flex; gap: 8px; align-items: flex-start; background: var(--t, #eef3f9); border-radius: 8px; padding: 7px 11px; margin: 4px 0 8px; font-size: 9.6pt; }
.point .lb { flex: none; font-weight: 900; color: var(--c, #1f3a5f); font-size: 8pt; padding: 1px 7px; border: 1.5px solid var(--c); border-radius: 99px; background: #fff; margin-top: 1px }
.warn { display: flex; gap: 8px; align-items: flex-start; background: #fff1e6; border: 1px solid #f7c9a6; border-radius: 8px; padding: 6px 10px; margin: 6px 0; font-size: 8.8pt; break-inside: avoid; }
.warn svg { flex: none; width: 17px; height: 17px; color: #d9480f; margin-top: 1px }
.warn b { color: #b33a07 }
.note { font-size: 7.8pt; color: #5b6673; margin: 3px 0; padding-left: 1.1em; text-indent: -1.1em; }
.note:before { content: "※ "; }

/* ---------- steps ---------- */
.steps { display: flex; flex-direction: column; gap: 2px; margin: 2px 0 4px; }
.step { display: grid; grid-template-columns: 19px 24px 1fr auto; gap: 6px; align-items: center; padding: 2px 6px 2px 3px;
  border-radius: 7px; background: #f7f9fb; break-inside: avoid; }
.step .n { width: 19px; height: 19px; border-radius: 50%; background: var(--c, #1f3a5f); color: #fff; font-weight: 700; font-size: 8pt;
  display: grid; place-items: center; }
.step .ic { width: 24px; height: 24px; border-radius: 6px; background: #fff; border: 1px solid #e1e6ec; display: grid; place-items: center; color: var(--c, #1f3a5f); }
.step .ic svg { width: 16px; height: 16px; }
.step .tx { line-height: 1.4 }
.step .tx small { display: block; line-height: 1.35; margin-top: 1px }
.time { white-space: nowrap; font-weight: 700; font-size: 8.2pt; padding: 2px 8px; border-radius: 99px; background: #fff; border: 1.5px solid var(--c, #1f3a5f); color: var(--c, #1f3a5f); }
.time.led { background: #fff8d6; border-color: #e0b100; color: #7a5a00; }
.time.wait { background: #eef1f4; border-color: #9aa6b2; color: #4a5561; }
.time.no { background: #fff; border-color: #c5ccd4; color: #8a96a3; font-weight: 500 }

/* ---------- layout ---------- */
.row { display: flex; gap: 12px; align-items: flex-start; }
.grow { flex: 1; min-width: 0; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.grid3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 9px; }
.lanes { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin: 4px 0; }
.lane { border: 1px solid #e1e6ec; border-radius: 9px; padding: 0 6px 6px; background: #fff; break-inside: avoid; }
.lane h4 { margin: 0 -6px 6px; padding: 5px 8px; font-size: 9pt; color: #fff; background: var(--c); border-radius: 8px 8px 0 0; display: flex; align-items: center; gap: 6px; }
.lane h4 svg { width: 14px; height: 14px }
.lane .step { grid-template-columns: 17px 1fr; font-size: 8.4pt; row-gap: 2px }
.lane .step .time { grid-column: 2; justify-self: start; }
.lane .step .n { width: 17px; height: 17px; font-size: 7.4pt }
.lane .step .ic { display: none }
.lane .time { font-size: 7.4pt; padding: 1px 6px }

/* ---------- photos ---------- */
.photos { flex: none; width: 92px; display: flex; flex-direction: column; gap: 6px; }
.photo { text-align: center; font-size: 6.8pt; color: #52606d; line-height: 1.25 }
.photo img { width: 100%; aspect-ratio: 3/4; object-fit: cover; border-radius: 8px; border: 1px solid #e1e6ec; display: block; margin-bottom: 2px; background: #f4f6f8 }
.photos.h { flex-direction: row; width: auto; }
.photos.h .photo { width: 64px; }
.fig.sm { max-width: 330px; margin: 4px auto; }

/* ---------- tables ---------- */
table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 8.5pt; margin: 4px 0 6px; break-inside: auto; }
th { background: #1f3a5f; color: #fff; font-weight: 700; padding: 5px 7px; text-align: left; font-size: 8.2pt; }
th:first-child { border-top-left-radius: 7px } th:last-child { border-top-right-radius: 7px }
td { padding: 5px 7px; border-bottom: 1px solid #e3e8ee; vertical-align: middle; }
tr { break-inside: avoid; }
tbody tr:nth-child(even) td { background: #fafbfc; }
.chip { display: inline-block; padding: 1px 8px; border-radius: 99px; font-size: 7.8pt; font-weight: 700; background: var(--t, #eef1f4); color: var(--c, #3d4a57); border: 1px solid color-mix(in srgb, var(--c, #3d4a57) 25%, white); white-space: nowrap; margin: 1px 0; }
.chip.ok { --c: #23803d; --t: #e9f7ee; }
.chip.ng { --c: #c62828; --t: #fdecec; }
.chip.gray { --c: #7d8894; --t: #f1f3f5; }
.chip.warn { --c: #b33a07; --t: #fff1e6; }
.arrow { color: #9aa6b2; margin: 0 3px; font-weight: 700 }

/* ---------- cards ---------- */
.card { border: 1px solid #e1e6ec; border-radius: 10px; padding: 8px 10px; background: #fff; break-inside: avoid; }
.card h5 { margin: 0 0 4px; font-size: 9.6pt; display: flex; align-items: center; gap: 6px; }
.fig { border: 1px solid #e1e6ec; border-radius: 10px; padding: 6px 8px 4px; background: #fbfcfd; break-inside: avoid; }
.fig .cap { font-size: 7.6pt; color: #52606d; text-align: center; margin-top: 2px; }
.fig svg { display: block; width: 100%; height: auto; }

/* ---------- charts ---------- */
.chart { border: 1px solid #e1e6ec; border-radius: 10px; padding: 8px 10px 6px; break-inside: avoid; background: #fff; margin: 4px 0 8px; }
.chart h6 { margin: 0 0 2px; font-size: 9.6pt; }
.chart .sub { font-size: 7.6pt; color: #6b7785; margin-bottom: 4px; }
.legend { display: flex; gap: 14px; font-size: 7.6pt; color: #52606d; margin: 2px 0 4px; flex-wrap: wrap }
.legend i { display: inline-block; width: 10px; height: 10px; border-radius: 3px; margin-right: 4px; vertical-align: -1px; }
"""

# ---------------- icons (24x24, stroke = currentColor) ----------------
_S = 'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'
ICONS = {
    "apply":  f'<g {_S}><path d="M14 4l6 6-8.5 8.5a3 3 0 01-4.2 0l-1.8-1.8a3 3 0 010-4.2z"/><path d="M4 20l3-3"/></g>',
    "rinse":  f'<g {_S}><path d="M8 3c2.5 3.5 4 5.6 4 7.5a4 4 0 01-8 0C4 8.6 5.5 6.5 8 3z"/><path d="M17 10c1.6 2.3 2.6 3.7 2.6 4.9a2.6 2.6 0 01-5.2 0c0-1.2 1-2.6 2.6-4.9z"/></g>',
    "air":    f'<g {_S}><path d="M3 8h11a3 3 0 10-3-3"/><path d="M3 12h16a3 3 0 11-3 3"/><path d="M3 16h7"/></g>',
    "light":  f'<g {_S}><path d="M9 17h6M10 20h4"/><path d="M12 3a5.5 5.5 0 00-3.3 9.9c.6.5 1 1.2 1 2V15h4.6v-.1c0-.8.4-1.5 1-2A5.5 5.5 0 0012 3z"/><path d="M3 9h1.5M19.5 9H21M5 3.5l1 1M19 3.5l-1 1"/></g>',
    "etch":   f'<g {_S}><path d="M4 20l5-5"/><path d="M8 12l4 4"/><rect x="9.5" y="3.5" width="6" height="12" rx="1" transform="rotate(45 12.5 9.5)"/><path d="M17 3l4 4"/></g>',
    "blast":  f'<g {_S}><path d="M3 14h6l2-4H5z"/><path d="M11 12h2"/></g><g fill="currentColor"><circle cx="16" cy="8" r="1.1"/><circle cx="19" cy="11" r="1.1"/><circle cx="16.5" cy="14" r="1.1"/><circle cx="20" cy="16" r="1.1"/><circle cx="18" cy="5" r="1.1"/></g>',
    "wait":   f'<g {_S}><circle cx="12" cy="13" r="8"/><path d="M12 9v4l2.5 2.5M9 2h6"/></g>',
    "mix":    f'<g {_S}><path d="M7 3c2 2.8 3.2 4.5 3.2 6a3.2 3.2 0 01-6.4 0C3.8 7.5 5 5.8 7 3z"/><path d="M17 3c2 2.8 3.2 4.5 3.2 6a3.2 3.2 0 01-6.4 0c0-1.5 1.2-3.2 3.2-6z"/><path d="M5 16.5a7 3.5 0 0014 0"/></g>',
    "place":  f'<g {_S}><path d="M6 11c0-3 2.5-5 6-5s6 2 6 5v2H6z"/><path d="M12 2v2M8 17h8l-1 4H9z"/></g>',
    "clean":  f'<g {_S}><path d="M12 3l1.8 4.2L18 9l-4.2 1.8L12 15l-1.8-4.2L6 9l4.2-1.8z"/><path d="M18 15l.8 1.7 1.7.8-1.7.8L18 20l-.8-1.7-1.7-.8 1.7-.8z"/></g>',
    "check":  f'<g {_S}><circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.7 2.7L16 9.8"/></g>',
    "shield": f'<g {_S}><path d="M12 3l7 3v5c0 5-3.2 8.3-7 10-3.8-1.7-7-5-7-10V6z"/><path d="M9 12l2 2 4-4"/></g>',
    "layer":  f'<g {_S}><path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/></g>',
    "remove": f'<g {_S}><path d="M4 20h16"/><path d="M6 16l9-9 3 3-9 9H6z"/></g>',
    "polish": f'<g {_S}><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/></g>',
    "fill":   f'<g {_S}><path d="M5 20h14"/><path d="M8 20v-5a4 4 0 018 0v5"/><path d="M12 3v7"/><path d="M9.5 7.5L12 10l2.5-2.5"/></g>',
    "prep":   f'<g {_S}><path d="M4 20l7-7"/><path d="M11 13l2 2 7-7-2-2z"/><path d="M15 5l4 4"/></g>',
    "warn":   f'<g {_S}><path d="M12 3.5l9.5 16.5h-19z"/><path d="M12 10v4.5"/><circle cx="12" cy="17.3" r=".6" fill="currentColor"/></g>',
    "tooth":  f'<g {_S}><path d="M7 3c-2.5 0-4 2-4 4.5 0 3 1.3 4.5 2 7 .6 2.4 1 6.5 2.8 6.5 1.6 0 1.6-4.5 4.2-4.5s2.6 4.5 4.2 4.5c1.8 0 2.2-4.1 2.8-6.5.7-2.5 2-4 2-7C21 5 19.5 3 17 3c-2 0-3 1-5 1S9 3 7 3z"/></g>',
    "crown":  f'<g {_S}><path d="M5 18h14l1-9-4.5 3.5L12 6l-3.5 6.5L4 9z"/></g>',
    "post":   f'<g {_S}><path d="M10 3h4v14l-2 4-2-4z"/><path d="M10 7h4"/></g>',
    "cube":   f'<g {_S}><path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M4 7.5l8 4.5 8-4.5M12 12v9"/></g>',
    "fridge": f'<g {_S}><rect x="6" y="2.5" width="12" height="19" rx="2"/><path d="M6 10h12M9 5.5v2M9 13v3"/></g>',
    "thermo": f'<g {_S}><path d="M10 4a2 2 0 014 0v9.5a4 4 0 11-4 0z"/><path d="M12 9v6"/></g>',
    "floss":  f'<g {_S}><path d="M4 4c5 4 11 12 16 16"/><path d="M4 9c3 1 5 3 6 6"/></g>',
    "hand":   f'<g {_S}><path d="M12 21v-9M8 17l4 4 4-4"/><rect x="7" y="3" width="10" height="6" rx="2"/></g>',
    "x":      f'<g {_S}><circle cx="12" cy="12" r="9"/><path d="M9 9l6 6M15 9l-6 6"/></g>',
    "book":   f'<g {_S}><path d="M4 5a2 2 0 012-2h13v16H6a2 2 0 00-2 2z"/><path d="M4 19V5M8 7h7"/></g>',
}

def icon(name, size=None, cls=""):
    s = f' width="{size}" height="{size}"' if size else ""
    return f'<svg viewBox="0 0 24 24"{s} class="{cls}" aria-hidden="true">{ICONS[name]}</svg>'

def md(s):
    """**bold** -> <b>, escape the rest."""
    parts = re.split(r"(\*\*[^*]+\*\*)", str(s))
    return "".join(f"<b>{html.escape(p[2:-2])}</b>" if p.startswith("**") else html.escape(p) for p in parts)

# ---------------- components ----------------
def chapter(no, title, cat=None, desc="", ic=None, color=None, newpage=True):
    c = color or (CAT[cat][0] if cat else "#1f3a5f")
    i = icon(ic, cls="ci") if ic else ""
    st = "" if newpage else "break-before:auto;margin-top:16px;"
    return f'<div class="chapter" style="{st}--c:{c}">{i}<span class="no">{no}</span><span class="t">{md(title)}</span><span class="d">{md(desc)}</span></div>'

def sec(no, title, cat=None, tag=None):
    c = CAT[cat][0] if cat else "#1f3a5f"
    t = f'<span class="tag">{md(tag)}</span>' if tag else ""
    return f'<div class="sec" style="--c:{c}"><span class="no">{no}</span><span class="t">{md(title)}</span>{t}</div>'

def point(text, cat=None):
    c, t, _ = CAT[cat] if cat else ("#1f3a5f", "#eef3f9", "")
    return f'<div class="point" style="--c:{c};--t:{t}"><span class="lb">ポイント</span><span>{md(text)}</span></div>'

def warn(text):
    return f'<div class="warn">{icon("warn")}<span>{md(text)}</span></div>'

def note(text):
    return f'<div class="note">{md(text)}</div>'

def time_pill(t):
    if not t: return ""
    kind = ""
    if t.startswith("LED"): kind = "led"
    elif t.startswith("待"):
        return f'<span class="time wait">{icon("wait", 10)} {md(t[1:].strip())}</span>'
    elif t.startswith("-"): kind, t = "no", t[1:]
    return f'<span class="time {kind}">{md(t)}</span>'

def steps(items, cat=None):
    """items: (icon, text, time?, sub?)"""
    c = CAT[cat][0] if cat else "#1f3a5f"
    out = []
    for i, it in enumerate(items, 1):
        ic, tx, tm, sub = (list(it) + [None, None])[:4]
        s = f"<small>{md(sub)}</small>" if sub else ""
        out.append(f'<div class="step"><span class="n">{i}</span><span class="ic">{icon(ic)}</span>'
                   f'<span class="tx">{md(tx)}{s}</span>{time_pill(tm)}</div>')
    return f'<div class="steps" style="--c:{c}">{"".join(out)}</div>'

def lanes(cols, cat="pros"):
    """cols: [(title, icon, steps)]"""
    c = CAT[cat][0]
    h = []
    for title, ic, st in cols:
        h.append(f'<div class="lane" style="--c:{c}"><h4>{icon(ic)}{md(title)}</h4>{steps(st, cat)}</div>')
    return f'<div class="lanes">{"".join(h)}</div>'

def photo(name, cap):
    return f'<div class="photo"><img src="{IMG}/{name}.jpg">{md(cap)}</div>'

def photos(items, horizontal=False):
    return f'<div class="photos{" h" if horizontal else ""}">{"".join(photo(n, c) for n, c in items)}</div>'

def with_photos(body, items):
    return f'<div class="row"><div class="grow">{body}</div>{photos(items)}</div>'

def chip(text, kind="", cat=None, style=""):
    st = f"--c:{CAT[cat][0]};--t:{CAT[cat][1]};" if cat else ""
    return f'<span class="chip {kind}" style="{st}{style}">{md(text)}</span>'

def chain(*items):
    return '<span class="arrow">→</span>'.join(items)

def table(headers, rows, widths=None, cls=""):
    cg = "".join(f'<col style="width:{w}">' for w in widths) if widths else ""
    th = "".join(f"<th>{md(h)}</th>" for h in headers)
    tr = "".join("<tr>" + "".join(c if str(c).startswith("<td") else f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table class="{cls}"><colgroup>{cg}</colgroup><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'

def fig(svg, cap=""):
    return f'<div class="fig">{svg}{f"<div class=cap>{md(cap)}</div>" if cap else ""}</div>'

def doc(title, body):
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>{CSS}</style></head><body><div class="doctitle">{html.escape(title)}｜博多ステラ歯科・矯正歯科クリニック</div>{body}</body></html>"""

def render(html_path, pdf_path):
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    "--allow-file-access-from-files", f"--print-to-pdf={pdf_path}", "file://" + html_path],
                   check=True, capture_output=True, timeout=180)
    print("rendered", pdf_path)

CSS += """
.illu { display: flex; gap: 8px; align-items: center; }
.illu svg { flex: 0 0 52%; width: 52%; }
.illu .lg { flex: 1; display: flex; flex-direction: column; gap: 4px; font-size: 8pt; line-height: 1.3 }
.illu .lg > div { display: flex; gap: 5px; align-items: flex-start }
.illu .lg small { display: block; font-size: 7.2pt }
.illu .lg .mk { flex: none; width: 15px; height: 15px; border-radius: 50%; color: #fff; font-weight: 700; font-size: 7.5pt; display: grid; place-items: center; margin-top: 1px }
"""
