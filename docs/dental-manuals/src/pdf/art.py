"""SVG charts and schematic illustrations."""
from html import escape as e

INK, INK2, MUTED, GRID = "#1d2733", "#52606d", "#8a96a3", "#e6eaef"
FONT = 'font-family="Noto Sans CJK JP" '

def T(x, y, s, size=10, fill=INK, anchor="start", weight=400, extra=""):
    return f'<text x="{x}" y="{y}" {FONT}font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" {extra}>{e(str(s))}</text>'

# ------------------------------------------------------------------ charts
def range_chart(rows, xmin, xmax, ticks, unit, W=560, label_w=170, row_h=22, bands=(), fmt=lambda v: f"{v:g}", note_w=150):
    """rows: dict(label, lo, hi, color, text, sub) ; lo/hi None -> label only (text shown in plot)."""
    pw = W - label_w - note_w
    H = 26 + row_h * len(rows) + 6
    x = lambda v: label_w + (v - xmin) / (xmax - xmin) * pw
    s = []
    for (lo, hi, fill, lab) in bands:
        s.append(f'<rect x="{x(lo):.1f}" y="16" width="{x(hi)-x(lo):.1f}" height="{H-22}" fill="{fill}" rx="4"/>')
        s.append(T((x(lo)+x(hi))/2, 12, lab, 8, INK2, "middle", 700))
    for t in ticks:
        s.append(f'<line x1="{x(t):.1f}" x2="{x(t):.1f}" y1="18" y2="{H-6}" stroke="{GRID}" stroke-width="1"/>')
        s.append(T(x(t), H + 6, f"{fmt(t)}", 8, MUTED, "middle"))
    s.append(T(label_w + pw, H + 18, unit, 8, MUTED, "end"))
    for i, r in enumerate(rows):
        cy = 26 + i * row_h + row_h / 2
        s.append(T(label_w - 8, cy + 3.5, r["label"], 9, INK, "end", 700 if r.get("bold") else 400))
        if r.get("lo") is None:
            s.append(T(label_w + 4, cy + 3.5, r.get("text", ""), 8.5, MUTED))
            continue
        lo, hi, c = r["lo"], r["hi"], r["color"]
        if hi - lo < 1e-9:
            s.append(f'<circle cx="{x(lo):.1f}" cy="{cy}" r="5" fill="{c}" stroke="#fff" stroke-width="2"/>')
            end = x(lo) + 6
        else:
            s.append(f'<rect x="{x(lo):.1f}" y="{cy-6}" width="{max(x(hi)-x(lo), 4):.1f}" height="12" rx="4" fill="{c}"/>')
            end = x(hi)
        if r.get("text"):
            s.append(T(end + 6, cy + 3.5, r["text"], 8.5, INK2))
    return f'<svg viewBox="0 {-2} {W} {H+22}" xmlns="http://www.w3.org/2000/svg">{"".join(s)}</svg>'

def bar_chart(rows, xmax, ticks, unit, W=560, label_w=180, row_h=20, fmt=lambda v: f"{v:g}"):
    """rows: dict(label, v, color, text, group?) ; group rows print a small heading."""
    pw = W - label_w - 70
    H = 10 + row_h * len(rows)
    x = lambda v: label_w + v / xmax * pw
    s = []
    for t in ticks:
        s.append(f'<line x1="{x(t):.1f}" x2="{x(t):.1f}" y1="4" y2="{H}" stroke="{GRID}"/>')
        s.append(T(x(t), H + 12, fmt(t), 8, MUTED, "middle"))
    s.append(T(label_w + pw, H + 24, unit, 8, MUTED, "end"))
    s.append(f'<line x1="{label_w}" x2="{label_w}" y1="4" y2="{H}" stroke="#b8c1cb"/>')
    for i, r in enumerate(rows):
        cy = 10 + i * row_h + row_h / 2 - 4
        s.append(T(label_w - 8, cy + 3.5, r["label"], 8.8, INK, "end"))
        w = max(x(r["v"]) - label_w, 3)
        s.append(f'<rect x="{label_w}" y="{cy-5.5}" width="{w:.1f}" height="11" rx="4" fill="{r["color"]}"/>'
                 f'<rect x="{label_w}" y="{cy-5.5}" width="4" height="11" fill="{r["color"]}"/>')
        s.append(T(label_w + w + 5, cy + 3.5, r.get("text", fmt(r["v"])), 8.5, INK2, weight=700))
    return f'<svg viewBox="0 0 {W} {H+28}" xmlns="http://www.w3.org/2000/svg">{"".join(s)}</svg>'

# ------------------------------------------------------------------ illustration primitives
ENAMEL, ENAMEL_S, DENTIN, PULP = "#fdfaf2", "#b9ad92", "#f3e5c4", "#f3a9a9"
CR, CR_S, EVX, BOND = "#dce9f8", "#8fb3dd", "#1fae7b", "#2a78d6"

_LB = []
def label_line(x1, y1, x2, y2, text, sub=None, color=INK, anchor="start"):
    """Leader line ending in a numbered marker; the text goes to an HTML legend (readable at any scale)."""
    _LB.append((text, sub, color))
    n = len(_LB)
    return (f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{INK2}" stroke-width="1.2" fill="none"/><circle cx="{x1}" cy="{y1}" r="2.4" fill="{INK2}"/>'
            f'<circle cx="{x2}" cy="{y2}" r="10" fill="{color if color != INK else "#1f3a5f"}" stroke="#fff" stroke-width="2"/>'
            + T(x2, y2 + 4.5, n, 12, "#fff", "middle", 700))

def legend_html():
    items = "".join(f'<div><span class="mk" style="background:{c if c != INK else "#1f3a5f"}">{k}</span><span><b>{e(t)}</b>'
                    f'{f"<small>{e(s)}</small>" if s else ""}</span></div>' for k, (t, s, c) in enumerate(_LB, 1))
    _LB.clear()
    return f'<div class="lg">{items}</div>'

MOLAR = ("M60,30 Q60,15 80,14 L120,18 Q150,10 180,18 L220,14 Q240,15 240,30 L236,95 Q233,110 215,112 "
         "Q212,150 195,168 Q182,150 175,112 L125,112 Q118,150 105,168 Q88,150 85,112 Q67,110 64,95 Z")
MOLAR_DENTIN = ("M72,34 Q74,26 90,26 L210,26 Q226,26 228,34 L224,94 Q220,104 206,106 Q204,140 195,156 "
                "Q188,140 184,106 L116,106 Q112,140 105,156 Q96,140 94,106 Q80,104 76,94 Z")

def svg(w, h, body, left=0):
    s = f'<svg viewBox="{-left} 0 {w + left} {h}" xmlns="http://www.w3.org/2000/svg">{body}</svg>'
    return f'<div class="illu">{s}{legend_html()}</div>' if _LB else s

def ill_layering():
    b = [f'<path d="{MOLAR}" fill="{ENAMEL}" stroke="{ENAMEL_S}" stroke-width="1.5"/>',
         f'<path d="{MOLAR_DENTIN}" fill="{DENTIN}"/>',
         f'<path d="M118,98 Q150,90 182,98 L180,104 Q150,99 120,104 Z" fill="{PULP}"/>']
    # cavity layers (bottom -> top)
    b.append(f'<path d="M100,70 L200,70 L200,82 Q200,88 194,88 L106,88 Q100,88 100,82 Z" fill="{EVX}"/>')
    for i, (y0, y1) in enumerate([(52, 70), (34, 52), (15, 34)]):
        b.append(f'<rect x="100" y="{y0}" width="100" height="{y1-y0}" fill="{CR}" stroke="{CR_S}" stroke-width="1"/>')
    b.append(f'<path d="M100,15 L100,82 Q100,88 106,88 L194,88 Q200,88 200,82 L200,15" fill="none" stroke="{BOND}" stroke-width="2"/>')
    b.append(label_line(196, 24, 262, 24, "CR（2mm 以下ずつ）", "各層を光照射。最表層は必ず CR"))
    b.append(label_line(190, 80, 262, 80, "everX Flow（約 2mm）", "LED 20 秒。表面に出さない", "#0d7a54"))
    b.append(label_line(102, 60, 40, 150, "Quick 2（ボンド層）", None, BOND, "end") if False else "")
    b.append(label_line(200, 50, 262, 52, "ボンド層（Quick 2）", "LED 10 秒", BOND))
    return svg(280, 176, "".join(b))

def ill_pulpcap():
    b = [f'<path d="{MOLAR}" fill="{ENAMEL}" stroke="{ENAMEL_S}" stroke-width="1.5"/>',
         f'<path d="{MOLAR_DENTIN}" fill="{DENTIN}"/>',
         f'<path d="M112,96 Q130,88 146,74 Q150,70 154,74 Q170,88 188,96 L186,106 Q150,100 114,106 Z" fill="{PULP}"/>']
    b.append(f'<path d="M110,14 L110,68 Q110,76 118,76 L182,76 Q190,76 190,68 L190,14 Z" fill="#fff" stroke="{ENAMEL_S}" stroke-dasharray="3 2"/>')
    b.append(f'<path d="M126,76 L126,70 Q150,66 174,70 L174,76 Q150,80 126,76 Z" fill="#9aa9b8"/>')  # capping material
    b.append(f'<circle cx="150" cy="75" r="3" fill="#d95757"/>')
    b.append(label_line(128, 72, 40, 60, "覆髄材", "露出部＋周囲 1mm 以上", "#3d4a57", "end"))
    b.append(label_line(151, 76, 262, 110, "露髄部", "綿球で止血してから", "#b33a3a"))
    b.append(label_line(186, 60, 262, 60, "象牙質は湿ったまま", "乾燥させると覆髄材が動く"))
    b.append(label_line(112, 20, 40, 20, "窩縁・エナメル質", "ここには置かない", INK2, "end"))
    return svg(282, 176, "".join(b), -18)

def _premolar(wall_top):
    root = f"M105,{wall_top} L105,120 Q110,176 150,192 Q190,176 195,120 L195,{wall_top} Z"
    inner = f"M118,{wall_top} L118,118 Q124,165 150,178 Q176,165 182,118 L182,{wall_top} Z"
    return (f'<path d="{root}" fill="{ENAMEL}" stroke="{ENAMEL_S}" stroke-width="1.5"/>'
            f'<path d="{inner}" fill="{DENTIN}"/>'
            f'<path d="M146,112 L147,174 Q150,180 153,174 L154,112 Z" fill="#e79a72"/>')

def ill_core():
    b = [_premolar(58)]
    b.append(f'<path d="M118,58 L118,84 Q130,92 146,92 L146,110 L154,110 L154,92 Q170,92 182,84 L182,58 Z" fill="{EVX}"/>')
    b.append(f'<path d="M110,58 L110,36 Q112,16 150,14 Q188,16 190,36 L190,58 Z" fill="{CR}" stroke="{CR_S}" stroke-dasharray="4 3"/>')
    b.append(f'<path d="M110,36 L190,36" stroke="{CR_S}" stroke-dasharray="3 3"/>')
    b.append(f'<path d="M104,58 L104,120" stroke="{BOND}" stroke-width="0"/>')
    # light arrows
    for x0, x1 in ((40, 98), (260, 202)):
        b.append(f'<path d="M{x0},44 L{x1},44" stroke="#e0b100" stroke-width="3" marker-end="url(#ah)"/>')
    b.insert(0, '<defs><marker id="ah" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#e0b100"/></marker></defs>')
    b.append(T(40, 34, "頬（唇）側", 12, "#7a5a00", weight=700) + T(262, 34, "舌側", 12, "#7a5a00", "end", 700))
    b.append(T(150, 62 - 36, "", 8))
    b.append(label_line(186, 24, 262, 80, "歯冠部：4mm 以下ずつ", "各層 LED 20 秒"))
    b.append(label_line(154, 104, 262, 120, "everX Flow", "根管口から 2〜3mm まで", "#0d7a54"))
    b.append(label_line(112, 80, 40, 110, "フェルール", "残存歯質（壁）", INK2, "end"))
    return svg(282, 198, "".join(b), -18)

def ill_post():
    b = [_premolar(86)]
    b.append(f'<path d="M118,86 L118,86 Q130,92 146,92 L146,120 L154,120 L154,92 Q170,92 182,86 Z" fill="#c9b8e8"/>')
    b.append(f'<path d="M110,86 L110,40 Q112,16 150,14 Q188,16 190,40 L190,86 Z" fill="#e4dcf3" stroke="#a48fd1" stroke-dasharray="4 3"/>')
    b.append(f'<rect x="146.5" y="22" width="7" height="118" rx="3" fill="#f2f2f2" stroke="#8a96a3"/>')
    for yy in range(28, 138, 8):
        b.append(f'<path d="M147,{yy} L153,{yy+4}" stroke="#c5ccd4"/>')
    b.append(label_line(153, 60, 250, 40, "トクヤマ FR ポスト", "ライトレス Ⅱ で前処理"))
    b.append(label_line(186, 70, 250, 90, "エステコア", "根管口に填入 → ポスト挿入"))
    b.append(label_line(150, 138, 250, 150, "挿入後 LED 10 秒以上", "ポストを固定したまま", "#7a5a00"))
    b.append(label_line(106, 88, 50, 110, "フェルールなし", None, INK2, "end"))
    return svg(282, 198, "".join(b), -18)

def drop(cx, cy, r, fill, stroke=None):
    st = f' stroke="{stroke}" stroke-width="1.2"' if stroke else ""
    return f'<path d="M{cx},{cy-r*1.7} C{cx+r*0.6},{cy-r*0.8} {cx+r},{cy-r*0.2} {cx+r},{cy+r*0.25} A{r},{r} 0 1 1 {cx-r},{cy+r*0.25} C{cx-r},{cy-r*0.2} {cx-r*0.6},{cy-r*0.8} {cx},{cy-r*1.7} Z" fill="{fill}"{st}/>'

def ill_mix(a=("A 液", "#f2c230"), b=("B 液", "#3b7fd9"), res=("緑色 ＝ 混和完了", "#2fa35b"), na=1, nb=1, W=390):
    s = []
    def group(x, n, lab, col):
        out = ""
        for i in range(n):
            out += drop(x + i * 22 - (n - 1) * 11, 44, 9, col)
        return out + T(x, 80, lab, 12, INK, "middle", 700) + T(x, 95, f"{n} 滴", 10.5, INK2, "middle")
    s.append(group(70, na, *a))
    s.append(T(150, 50, "＋", 18, MUTED, "middle", 700))
    s.append(group(210 if nb > 1 or na > 1 else 200, nb, *b) if False else group(215, nb, *b))
    s.append(T(290, 50, "→", 18, MUTED, "middle", 700))
    s.append(drop(345, 44, 12, res[1]) + T(345, 80, res[0], 12, INK, "middle", 700))
    return svg(W + 50, 100, "".join(s), 10)

def ill_superbond():
    s = []
    for i in range(4):
        s.append(drop(40 + i * 22, 40, 8, "#cfe3f7", "#6f9fd0"))
    s.append(T(73, 76, "モノマー液", 12, INK, "middle", 700) + T(73, 91, "4 滴", 10.5, INK2, "middle"))
    s.append(T(140, 46, "＋", 18, MUTED, "middle", 700))
    s.append(drop(185, 40, 8, "#f4b860", "#c98a2b") + T(185, 76, "キャタリスト V", 12, INK, "middle", 700) + T(185, 91, "1 滴", 10.5, INK2, "middle"))
    s.append(T(236, 46, "→", 18, MUTED, "middle", 700))
    # timer
    s.append(f'<circle cx="300" cy="40" r="22" fill="#fff" stroke="#d9480f" stroke-width="2.5"/>'
             f'<path d="M300,40 L300,18 A22,22 0 0 1 320.9,33.2 Z" fill="#ffd8c2"/>'
             f'<path d="M300,40 L300,24 M300,40 L311,46" stroke="#d9480f" stroke-width="2" stroke-linecap="round"/>')
    s.append(T(300, 76, "5 分以内に使い切る", 12, "#b33a07", "middle", 700) + T(300, 91, "硬化目安 5〜6 分", 10.5, INK2, "middle"))
    return svg(380, 100, "".join(s), 10)
