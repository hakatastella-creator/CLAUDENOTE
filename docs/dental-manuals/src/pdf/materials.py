from kit import *
import art

EXTRA_CSS = """
.cover { page: cover; height: 297mm; display: flex; flex-direction: column; }
.hero { background: linear-gradient(135deg, #1f3a5f 0%, #2a5a8f 100%); color: #fff; padding: 20mm 16mm 11mm; position: relative; overflow: hidden; }
.hero .k { font-size: 10pt; letter-spacing: .2em; opacity: .8 }
.hero h1 { font-size: 30pt; margin: 4px 0 6px; line-height: 1.2 }
.hero p { margin: 0; opacity: .9; font-size: 10pt }
.hero svg.bg { position: absolute; right: -10px; top: -10px; width: 240px; height: 240px; opacity: .10; color: #fff }
.cbody { padding: 8mm 16mm 0; flex: 1; display: flex; flex-direction: column; gap: 9px }
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.stat { border-radius: 10px; border: 1px solid #e1e6ec; padding: 6px 10px; }
.stat .v { font-size: 20pt; font-weight: 900; color: #1f3a5f; line-height: 1.1 }
.stat .l { font-size: 8pt; color: #52606d }
.h2 { font-weight: 900; font-size: 11pt; color: #1f3a5f; display: flex; align-items: center; gap: 6px; margin-top: 2px }
.keepgrid { display: grid; grid-template-columns: repeat(8, 1fr); gap: 6px; }
.kp { text-align: center; font-size: 6.6pt; line-height: 1.2; color: #3d4a57 }
.kp img { width: 100%; aspect-ratio: 3/4; object-fit: cover; border-radius: 7px; border: 2px solid #bfe3cb; display: block; margin-bottom: 2px }
.dropgrid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.dp { display: flex; gap: 8px; align-items: center; border: 1px solid #f3c2c2; background: #fff6f6; border-radius: 10px; padding: 6px; font-size: 8pt }
.dp .im { position: relative; width: 46px; flex: none }
.dp img { width: 46px; aspect-ratio: 3/4; object-fit: cover; border-radius: 6px; display: block; filter: grayscale(.7) }
.dp .im:after { content: ""; position: absolute; inset: 0; background: linear-gradient(to top right, transparent 46%, #d63939 47%, #d63939 53%, transparent 54%); }
.dp b { display: block; color: #c62828; font-size: 8.8pt }
.mx th { text-align: center; font-size: 7.4pt; padding: 4px 2px; }
.mx th.g { font-size: 7.6pt; }
.mx td { text-align: center; padding: 3px 2px; font-size: 8pt }
.mx td:first-child { text-align: left; white-space: nowrap; font-weight: 700; padding-left: 6px }
.mx td.ph { color: #8a96a3; font-weight: 500 }
.dot { display: inline-block; width: 11px; height: 11px; border-radius: 50%; background: var(--c); }
.ring { display: inline-block; width: 11px; height: 11px; border-radius: 50%; border: 2.5px solid var(--c); box-sizing: border-box }
.mat { display: grid; grid-template-columns: 62px 1fr; gap: 9px; border: 1px solid #e1e6ec; border-radius: 10px; padding: 7px 9px; break-inside: avoid; background: #fff; position: relative }
.mat.phase { background: #f7f8fa; }
.mat img, .mat .noimg { width: 62px; aspect-ratio: 3/4; object-fit: cover; border-radius: 7px; border: 1px solid #e1e6ec; display: block; background: #f4f6f8 }
.mat .noimg { display: grid; place-items: center; color: #b3bcc6 }
.mat .noimg svg { width: 26px; height: 26px }
.mat h5 { margin: 0; font-size: 10pt; line-height: 1.3 }
.mat .role { margin: 2px 0 4px; }
.mini { display: flex; flex-wrap: wrap; align-items: center; gap: 2px 3px; font-size: 7.8pt; margin: 3px 0; }
.mini .s { display: inline-flex; align-items: center; gap: 3px; background: #f3f6f9; border-radius: 6px; padding: 1px 6px 1px 3px; }
.mini .s svg { width: 12px; height: 12px; color: var(--c) }
.mini .a { color: #9aa6b2; font-size: 8pt }
.mat .cw { font-size: 7.8pt; color: #b33a07; display: flex; gap: 4px; align-items: flex-start; margin-top: 3px; line-height: 1.35 }
.mat .cw svg { width: 12px; height: 12px; flex: none; margin-top: 1px }
.mat .inf { font-size: 7.8pt; color: #52606d; line-height: 1.35 }
.pflow { display: flex; align-items: stretch; gap: 0; margin: 4px 0 8px; break-inside: avoid; }
.pflow .st { flex: 1; text-align: center; border: 1px solid #e1e6ec; border-radius: 10px; padding: 6px 4px 5px; background: #fff; font-size: 7.8pt; line-height: 1.3 }
.pflow .st img { width: 54px; aspect-ratio: 3/4; object-fit: cover; border-radius: 7px; border: 1px solid #e1e6ec; display: block; margin: 0 auto 3px }
.pflow .st .ph { width: 54px; aspect-ratio: 3/4; border-radius: 7px; margin: 0 auto 3px; display: grid; place-items: center; background: var(--t); color: var(--c) }
.pflow .st .ph svg { width: 26px; height: 26px }
.pflow .st b { display: block; font-size: 8.4pt; color: #1d2733 }
.pflow .st .k { display: inline-block; margin-bottom: 3px; font-size: 7pt; font-weight: 700; color: #fff; background: var(--c); border-radius: 99px; padding: 0 7px }
.pflow .ar { flex: none; width: 16px; display: grid; place-items: center; color: #9aa6b2; font-weight: 900 }
.ngc { display: grid; grid-template-columns: 1fr; gap: 3px; border: 1px solid #f3c2c2; border-radius: 10px; padding: 7px 10px; background: #fff; break-inside: avoid; }
.ngc .pair { display: flex; align-items: center; gap: 6px; font-weight: 700; font-size: 9pt }
.ngc .pair .x { width: 20px; height: 20px; border-radius: 50%; background: #d63939; color: #fff; display: grid; place-items: center; font-size: 10pt; flex: none }
.ngc .why { font-size: 8pt; color: #52606d }
.ngc .alt { font-size: 8pt; color: #23803d; font-weight: 700 }
.store { border-radius: 12px; padding: 10px 12px; break-inside: avoid; }
.store h5 { margin: 0 0 6px; font-size: 11pt; display: flex; align-items: center; gap: 8px }
.store h5 svg { width: 26px; height: 26px }
.store ul { margin: 0; padding: 0; list-style: none; font-size: 8.6pt }
.store li { padding: 3px 0; border-bottom: 1px dashed rgba(0,0,0,.08); display: flex; justify-content: space-between; gap: 6px }
.store li:last-child { border: 0 }
.store li span { color: #52606d; font-size: 7.8pt; white-space: nowrap }
.rule { text-align: center; border: 1px solid #e1e6ec; border-radius: 10px; padding: 8px; font-size: 8.2pt; break-inside: avoid; }
.rule .big { font-size: 16pt; font-weight: 900; color: #1f3a5f; line-height: 1.2 }
.rule svg { width: 24px; height: 24px; color: #1f3a5f }
"""

def mini(steps_, cat):
    c = CAT[cat][0]
    parts = [f'<span class="s">{icon(i)}{md(t)}</span>' for i, t in steps_]
    return f'<div class="mini" style="--c:{c}">' + '<span class="a">›</span>'.join(parts) + "</div>"

def mat(photo_, name, role, cat, flow, info=None, cw=None, phase=False, extra=""):
    im = f'<img src="{IMG}/{photo_}.jpg">' if photo_ else f'<div class="noimg">{icon("cube")}</div>'
    tag = chip("在庫消化後は発注しない", "gray") if phase else ""
    body = (f'<h5>{md(name)}</h5><div class="role">{chip(role, cat=cat)} {tag}{extra}</div>' + (mini(flow, cat) if flow else "")
            + (f'<div class="inf">{md(info)}</div>' if info else "") + (f'<div class="cw">{icon("warn")}<span>{md(cw)}</span></div>' if cw else ""))
    return f'<div class="mat{" phase" if phase else ""}">{im}<div>{body}</div></div>'

def pflow(items, cat="pros"):
    c, t, _ = CAT[cat]
    out = []
    for k, ph, name, sub in items:
        vis = f'<img src="{IMG}/{ph}.jpg">' if ph and not ph.startswith("@") else f'<div class="ph">{icon(ph[1:] if ph else "cube")}</div>'
        out.append(f'<div class="st"><span class="k">{md(k)}</span>{vis}<b>{md(name)}</b>{"<br>".join(md(x) for x in sub.split("<br>"))}</div>')
    return f'<div class="pflow" style="--c:{c};--t:{t}">' + '<div class="ar">▶</div>'.join(out) + "</div>"

h = []
# ================================================================ COVER + POLICY
keep = [("quick2", "Quick 2"), ("sbuplus", "SBU Plus"), ("fineetch37", "FineEtch37"), ("gbond", "G-ボンド"), ("activator", "アクティベーター"),
        ("beautibondx", "BB Xtreme"), ("lightless2", "ライトレス Ⅱ"), ("katanacleaner", "カタナクリーナー"), ("cpp", "CPP"),
        ("monobond", "Monobond E&P"), ("relyxu", "RelyX Universal"), ("samulti", "SA Multi"), ("beauticem", "BeautiCem Veneer")]
keep_extra = ["everX Flow", "TheraCal LC", "FR ポスト", "エステコア", "オキシガード Ⅱ", "スーパーボンド", "アイコン"]
h.append(f"""
<section class="cover">
 <div class="hero">{icon("cube", cls="bg")}
  <div class="k">MATERIAL GUIDE</div><h1>材料別　使用用途一覧</h1>
  <p>博多ステラ歯科・矯正歯科クリニック　院内マニュアル　｜　操作手順は『治療別 接着プロトコル集』へ</p>
 </div>
 <div class="cbody">
  <div class="stats">
   <div class="stat"><div class="v" style="color:#23803d">20</div><div class="l">残す材料（発注する）</div></div>
   <div class="stat"><div class="v" style="color:#c62828">3</div><div class="l">なくす材料（在庫消化後は発注しない）</div></div>
   <div class="stat"><div class="v">1</div><div class="l">役割ごとに使う材料は原則 1 つ</div></div>
   <div class="stat"><div class="v">10</div><div class="l">使ってはいけない組み合わせ</div></div>
  </div>
  <div class="h2">{icon("check", 18)} 残す材料（写真は院内の実物）</div>
  <div class="keepgrid">{"".join(f'<div class="kp"><img src="{IMG}/{p}.jpg">{md(n)}</div>' for p, n in keep)}
   <div class="kp" style="grid-column: span 3; display:flex; flex-wrap:wrap; gap:4px; align-content:center; justify-content:flex-start; text-align:left">
    {"".join(chip(n, "ok") for n in keep_extra)}<div style="font-size:7pt;color:#8a96a3;width:100%">↑ 写真未登録の材料</div></div>
  </div>
  <div class="h2" style="color:#c62828">{icon("x", 18)} なくす材料 → 置き換え先</div>
  <div class="dropgrid">
   <div class="dp"><div class="im"><img src="{IMG}/megabond2.jpg"></div><div><b>メガボンド 2</b>ダイレクト → <b style="display:inline;color:#23803d">Quick 2 / SBU Plus</b></div></div>
   <div class="dp"><div class="im"><img src="{IMG}/beautilink.jpg"></div><div><b>ビューティリンク SA</b>日常セメント → <b style="display:inline;color:#23803d">SA ルーティング Multi</b></div></div>
   <div class="dp"><div class="im"><img src="{IMG}/relyxlp.jpg"></div><div><b>RelyX Luting Plus</b>合着 → <b style="display:inline;color:#23803d">CPP ＋ SA Multi</b></div></div>
  </div>
  <div class="h2">{icon("book", 18)} この資料の使い方</div>
  <div class="grid3">
   <div class="card"><b>① マトリクスで探す</b><br><span class="muted">2 章：どの治療でどの材料を使うかを一覧</span></div>
   <div class="card"><b>② 材料カードで確認</b><br><span class="muted">写真・役割・使い方・注意を 1 枚に</span></div>
   <div class="card"><b>③ NG と保管を確認</b><br><span class="muted">6 章：禁止の組み合わせ　7 章：保管ルール</span></div>
  </div>
 </div>
</section>""")

# ================================================================ 1 POLICY TABLE (compact)
h.append(chapter("1", "役割ごとの統一方針", desc="役割ごとに使う材料を 1 つに絞る", ic="check"))
pol = [
    ("ボンディング材", "Quick 2（保険）／ SBU Plus（自費）", "メガボンド 2"),
    ("支台築造", "ライトレス Ⅱ ＋ everX Flow ／ FR ポスト ＋ エステコア（フェルールなし）", ""),
    ("エッチング", "FineEtch37", ""),
    ("表面硬化（酸素阻害層）", "オキシガード Ⅱ（脱離が心配な症例のみ）", ""),
    ("ホワイトスポット", "G-ボンド ユニバーサル・アイコン", ""),
    ("CR・セラミックのリペア", "ポーセレンボンド アクティベーター（Quick 2 と混和）", ""),
    ("補綴物の洗浄", "カタナクリーナー", ""),
    ("ジルコニア・メタル内面", "セラミック プライマー プラス", ""),
    ("e.max 内面", "Monobond Etch & Prime", ""),
    ("日常のセメント（CAD/CAM・メタル）", "SA ルーティング Multi", "ビューティリンク SA ／ RelyX Luting Plus"),
    ("ジルコニア・e.max の装着", "SBU Plus ＋ RelyX Universal", ""),
    ("ベニア専用", "BeautiCem Veneer ＋ ビューティボンド Xtreme", ""),
    ("特殊症例の切り札", "スーパーボンド", ""),
]
h.append(table(["役割", "残す（発注する）", "なくす"], [[f"<b>{md(r)}</b>", chip(k, "ok", style="white-space:normal"), chip(d, "ng") if d else '<span class="muted">─</span>'] for r, k, d in pol],
               ["26%", "52%", "22%"]))
h.append(note("SBU Plus＝Scotchbond Universal Plus　CPP＝セラミック プライマー プラス　SA Multi＝SA ルーティング Multi"))

# ================================================================ 2 MATRIX
COLS = [("cr", "標準"), ("cr", "大窩洞"), ("cr", "覆髄"), ("cr", "白濁"), ("cr", "リペア"), ("core", "コア"),
        ("pros", "ジルコ<br>ニア"), ("pros", "e.max"), ("pros", "ベニア"), ("pros", "CAD/<br>CAM"), ("pros", "メタル"), ("sp", "特殊")]
M = [  # name, marks (12 chars: '●' main, '○' option/conditional, '.' none), phase?
    ("Quick 2", "●●●.●.......", False),
    ("Scotchbond Universal Plus", "○.....●●....", False),
    ("FineEtch37", "●...●..●●...", False),
    ("everX Flow", ".●...●......", False),
    ("TheraCal LC ／ ダイカル ／ ミエール", "..●.........", False),
    ("G-ボンド ユニバーサル ／ アイコン", "...●........", False),
    ("ポーセレンボンド アクティベーター", "....●......●", False),
    ("ボンドマー ライトレス Ⅱ", ".....●......", False),
    ("FR ポスト ＋ エステコア", ".....○......", False),
    ("カタナクリーナー", "......●.....", False),
    ("Monobond Etch & Prime", ".......●●...", False),
    ("RelyX Universal", "......●●.○..", False),
    ("ビューティボンド Xtreme", "........●...", False),
    ("BeautiCem Veneer", "........●...", False),
    ("セラミック プライマー プラス", ".........●●.", False),
    ("SA ルーティング Multi", ".........●●.", False),
    ("オキシガード Ⅱ", "........●..○", False),
    ("スーパーボンド", "...........●", False),
    ("メガボンド 2", "○...........", True),
    ("ビューティリンク SA", ".........○○.", True),
    ("RelyX Luting Plus", "..........○.", True),
]
def mark(ch, cat):
    c = CAT[cat][0]
    return f'<span class="dot" style="--c:{c}"></span>' if ch == "●" else f'<span class="ring" style="--c:{c}"></span>' if ch == "○" else ""
head = '<tr><th rowspan="2" style="text-align:left">材料</th>' + "".join(
    f'<th colspan="{n}" class="g" style="background:{CAT[k][0]}">{CAT[k][2]}</th>' for k, n in [("cr", 5), ("core", 1), ("pros", 5), ("sp", 1)]) + "</tr><tr>" + "".join(
    f'<th style="background:{CAT[k][0]};opacity:.85">{t}</th>' for k, t in COLS) + "</tr>"
body = "".join(f'<tr><td class="{"ph" if ph else ""}">{md(n)}{" " + chip("なくす", "ng") if ph else ""}</td>' + "".join(f"<td>{mark(ch, COLS[i][0])}</td>" for i, ch in enumerate(marks)) + "</tr>" for n, marks, ph in M)
h.append(chapter("2", "治療 × 材料マトリクス", desc="どの治療でどの材料を使うかがひと目でわかる", ic="layer"))
h.append(f'<div class="legend" style="font-size:8.4pt"><span><span class="dot" style="--c:#3d4a57"></span> 主に使う</span><span><span class="ring" style="--c:#3d4a57"></span> 条件つき・第二選択</span></div>')
h.append(f'<table class="mx"><colgroup><col style="width:30%">' + '<col>' * 12 + f'</colgroup><thead>{head}</thead><tbody>{body}</tbody></table>')
h.append(note("条件つき：SBU Plus（CR の第二選択・IDS）、FR ポスト（フェルールなしのみ）、RelyX Universal（CAD/CAM 冠で脱離既往・保持形態が弱い症例）、オキシガード Ⅱ（脱離が心配な症例）。"))

# ================================================================ 3 CR / 4 CORE material cards
cr = "cr"
h.append(chapter("3", "CR 充填・歯面処理の材料", cr, "主力は Quick 2。エナメル質には FineEtch37", "fill"))
h.append('<div class="grid2">' + "".join([
    mat("quick2", "ユニバーサルボンド Quick 2", "主力（全症例）", cr, [("apply", "擦り込み"), ("air", "強エア 5 秒"), ("light", "LED 10 秒")], "待ち時間なし。エナメル質が多い症例は FineEtch37 を併用"),
    mat("sbuplus", "Scotchbond Universal Plus", "第二選択・IDS", cr, [("apply", "20 秒擦り込み"), ("air", "エア 5 秒"), ("light", "LED 10 秒")], "RelyX Universal と純正ペア。補綴の前処理と共用できる"),
    mat("fineetch37", "FineEtch37", "選択エッチング", cr, [("etch", "エナメル質 15 秒"), ("rinse", "水洗 20 秒")], None, "象牙質に長く置かない"),
    mat("gbond", "G-ボンド ユニバーサル", "ホワイトスポット", cr, [("apply", "平皿に採取"), ("apply", "白濁部に浸潤"), ("light", "LED 5 秒")], "エア不要。深皿は使わない（操作時間 約 7 分）", "止血剤を使うと接着力が戻らない"),
    mat("activator", "ポーセレンボンド アクティベーター", "CR・セラミックのリペア", cr, [("mix", "Quick 2 と 1:1"), ("apply", "5 秒 / 20 秒"), ("air", "5 秒以上"), ("light", "LED 10 秒")], "シラン処理剤。混ぜるとすぐ使える", "作り置きしない"),
    mat("beautibondx", "ビューティボンド Xtreme", "ベニア装着時（必須）", cr, [("apply", "塗布"), ("air", "弱 3 秒→強"), ("light", "LED 5 秒")], "BeautiCem Veneer の添付文書で指定。CR 充填にも使える"),
    mat(None, "everX Flow", "大窩洞の裏層・コア", cr, [("fill", "窩洞底から 2mm"), ("light", "LED 20 秒"), ("layer", "表層は CR")], "短繊維強化フロアブル", "最表層に出さない"),
    mat(None, "TheraCal LC", "覆髄（保険）", cr, [("apply", "1mm 以下"), ("light", "LED 20 秒 / 層")], "ダイカル（保険・照射なし）、ミエール（自費・MTA）も覆髄に使用", "厚く塗ると硬化不良。範囲は最小限に"),
    mat("megabond2", "メガボンド 2", "ダイレクト", cr, [("apply", "プライマー 20 秒"), ("air", "エア"), ("apply", "ボンド"), ("light", "LED 10 秒")], "象牙質接着の長期成績が最も高い", phase=True),
]) + "</div>")

co = "core"
h.append(chapter("4", "支台築造の材料", co, "ライトレス Ⅱ は光照射不要", "post"))
h.append('<div class="grid2">' + "".join([
    mat("lightless2", "ボンドマー ライトレス Ⅱ", "主力（全症例の前処理）", co, [("mix", "A 黄＋B 青 → 緑"), ("apply", "塗布"), ("air", "30 秒以内にエア")], "光照射不要。操作時間：ブルーラバー皿 3 分／ディスポ 1 分", "塗布後にポストを試適しない。処理済みのポストと補綴物を触れさせない"),
    mat(None, "everX Flow", "主力（コア築造）", co, [("fill", "根管口から 2〜3mm"), ("light", "LED 20 秒"), ("layer", "4mm 以下で積層")], "硬化深度 5.5mm（バルクシェード）", "光重合のみ。根管の奥に入れない"),
    mat(None, "トクヤマ FR ポスト ＋ エステコア", "フェルールがない症例のみ", co, [("apply", "ライトレス Ⅱ で前処理"), ("place", "挿入"), ("light", "LED 10 秒以上")], "当院在庫のポストは 1.4mm。エステコアは冷蔵（使用 20 分前に室温へ）"),
    mat(None, "混和皿", "ライトレス Ⅱ の混和", co, None, "ブルーラバー：操作 3 分・アルコール清掃で再使用　ディスポ：操作 1 分・使い捨て", "ブルーラバーはオートクレーブ不可"),
]) + "</div>")

# ================================================================ 5 PROSTHESES: photo flows
pr = "pros"
h.append(chapter("5", "補綴のセット　材料の流れ", pr, "写真の順に使う。セメントとプライマーの組み合わせを固定", "crown"))
flows = [
    ("ジルコニア", [("ブラスト", "@blast", "アルミナ 50µm", "0.1MPa・10mm・10 秒"), ("洗浄", "katanacleaner", "カタナクリーナー", "10 秒 → 水洗<br>リン酸 ✕"),
                    ("内面・歯面", "sbuplus", "SBU Plus", "内面 5 秒エア<br>歯面 20 秒擦り込み"), ("セメント", "relyxu", "RelyX Universal", "仮 2〜3 秒<br>本 各面 20 秒")]),
    ("e.max", [("内面", "monobond", "Monobond E&P", "20 秒 → 40 秒静置<br>ブラスト不要"), ("エナメル", "fineetch37", "FineEtch37", "15〜30 秒"),
               ("歯面", "sbuplus", "SBU Plus", "20 秒擦り込み<br>5 秒エア"), ("セメント", "relyxu", "RelyX Universal", "デュアルキュア")]),
    ("e.max ベニア", [("内面", "monobond", "Monobond E&P", "トライイン除去後"), ("エナメル", "fineetch37", "FineEtch37", "ノンプレップ 60 秒"),
                     ("歯面", "beautibondx", "BB Xtreme", "20 秒 → LED 5 秒"), ("セメント", "beauticem", "BeautiCem Veneer", "2.0mm 未満・光重合")]),
    ("CAD/CAM 冠", [("ブラスト", "@blast", "アルミナ 50µm", "弱圧 0.1〜0.2MPa<br>必須"), ("シラン", "cpp", "CPP", "塗布 → 十分にエア<br>必須"),
                   ("歯面", "@check", "前処理なし", "SA セメントのため"), ("セメント", "samulti", "SA Multi", "仮 2〜3 秒<br>本 各面 20 秒以上")]),
    ("メタル", [("ブラスト", "@blast", "アルミナ 50µm", "0.3〜0.5MPa<br>銀合金は直前に"), ("プライマー", "cpp", "CPP", "塗布 → 十分にエア"),
               ("歯面", "@check", "前処理なし", "SA セメントのため"), ("セメント", "samulti", "SA Multi", "マージン LED 20 秒以上<br>完全硬化 8 分")]),
]
for name, items in flows:
    h.append(f'<div class="nobreak"><div class="sec" style="--c:{CAT[pr][0]};margin-top:8px"><span class="t">{md(name)}</span></div>' + pflow(items) + "</div>")
h.append('<div class="grid2">' + warn("CAD/CAM 冠に **RelyX Luting Plus は使えない**（接着性レジンセメントが診療指針で必須）。") + warn("CAD/CAM 冠で脱離既往・保持形態が弱い症例は **RelyX Universal**（支台歯は SBU Plus）。") + "</div>")

h.append(sec("5-2", "補綴の材料カード", pr))
h.append('<div class="grid2">' + "".join([
    mat("katanacleaner", "カタナクリーナー", "試適後の唾液汚染除去", pr, [("apply", "内面 10 秒"), ("rinse", "水洗"), ("air", "乾燥")], None, "リン酸は使わない（MDP の結合を阻害）"),
    mat("sbuplus", "Scotchbond Universal Plus", "内面処理・支台歯前処理", pr, [("apply", "内面：塗布→エア 5 秒"), ("apply", "歯面：20 秒")], "MDP・シラン入り。RelyX Universal 併用時は照射不要"),
    mat("relyxu", "RelyX Universal", "ジルコニア・e.max の装着", pr, [("place", "装着"), ("light", "仮 2〜3 秒"), ("remove", "余剰除去"), ("light", "本 20 秒")], "デュアルキュア。光が届きにくい部位でも硬化"),
    mat("monobond", "Monobond Etch & Prime", "e.max 内面（エッチング＋シラン）", pr, [("apply", "20 秒すり込み"), ("wait", "40 秒"), ("rinse", "水洗・乾燥")], "フッ化水素酸が不要", "ジルコニアには使えない"),
    mat("beauticem", "BeautiCem Veneer", "ベニア（厚さ 2.0mm 未満）", pr, [("light", "仮 2〜3 秒"), ("remove", "余剰除去"), ("light", "本 10 秒")], "光重合専用", "光を通す修復物のみ（ジルコニア ✕）。ユージノール系と併用不可"),
    mat("cpp", "セラミック プライマー プラス", "CAD/CAM・メタル内面のシラン処理", pr, [("blast", "ブラスト"), ("apply", "塗布"), ("air", "十分にエア")], "冷蔵 2〜8℃。使用直前に室温へ", "必須工程。SA セメント単独では付かない"),
    mat("samulti", "SA ルーティング Multi", "日常のセメント（CAD/CAM・メタル）", pr, [("place", "装着"), ("light", "仮 2〜3 秒"), ("remove", "余剰除去"), ("light", "本 20 秒以上")], "保険で使用可。セルフアドヒーシブ（歯面の前処理不要）"),
    mat("beautilink", "ビューティリンク SA", "CAD/CAM・金属冠・ジルコニア", pr, [("blast", "ブラスト"), ("apply", "プライマー"), ("place", "装着")], "なくなり次第 SA ルーティング Multi へ", phase=True),
    mat("relyxlp", "RelyX Luting Plus", "合着（保持形態が十分な金属冠）", pr, [("mix", "練和"), ("place", "装着"), ("light", "LED 5 秒")], "接着ではなく合着", "CAD/CAM 冠・e.max・ベニアには使えない", phase=True),
]) + "</div>")

# ================================================================ 6 NG
h.append(chapter("6", "使ってはいけない組み合わせ", desc="理由と、代わりに使う材料をセットで覚える", ic="x", color="#c62828"))
NG = [
    ("ジルコニア", "BeautiCem Veneer", "光重合専用。添付文書は「光を通す修復物のみ」", "RelyX Universal"),
    ("BeautiCem Veneer", "ユージノール系材料", "硬化・接着を阻害する（添付文書）", "ユージノールを含まない材料"),
    ("ジルコニア", "Monobond Etch & Prime", "ガラス相がなくエッチングが効かない", "SBU Plus"),
    ("ジルコニア", "フッ化水素酸", "表面が変わらず無効", "ブラスト ＋ SBU Plus"),
    ("ジルコニアの洗浄", "リン酸（FineEtch37）", "リン酸が吸着し MDP の結合を阻害", "カタナクリーナー"),
    ("e.max", "SA セメント単独", "シラン処理がなく接着が大きく落ちる。薄いものは破折リスク", "Monobond E&P ＋ RelyX Universal"),
    ("e.max", "RelyX Luting Plus", "合着では e.max の強度を保てない", "RelyX Universal"),
    ("CAD/CAM 冠", "RelyX Luting Plus", "接着性レジンセメントが診療指針で必須", "SA ルーティング Multi"),
    ("CAD/CAM 冠", "シラン処理の省略", "必須工程。省くと脱離の主因", "セラミック プライマー プラス"),
    ("メーカー A のボンド", "メーカー B のセメント", "添付文書外。脱離・破折時の説明で不利", "純正の組み合わせ"),
]
h.append('<div class="grid2">' + "".join(
    f'<div class="ngc"><div class="pair">{md(a)}<span class="x">✕</span>{md(b)}</div><div class="why">{md(w)}</div><div class="alt">→ 代わりに：{md(alt)}</div></div>'
    for a, b, w, alt in NG) + "</div>")

# ================================================================ 7 STORAGE
h.append(chapter("7", "保管・取扱いのルール", desc="冷蔵品は使う前に室温へ。結露は接着力低下のもと", ic="thermo", newpage=False))
h.append('<div class="grid3">'
         '<div class="store" style="background:#eaf3fd"><h5 style="color:#2a78d6">' + icon("fridge") + '冷蔵庫</h5><ul>'
         '<li>セラミック プライマー プラス<span>2〜8℃</span></li><li>エステコア<span>0〜10℃</span></li><li>オキシガード Ⅱ<span>冷蔵</span></li>'
         '<li>スーパーボンド<span>冷蔵</span></li><li>ポーセレンボンド アクティベーター<span>冷蔵</span></li></ul>'
         '<div class="note" style="margin-top:6px">使用直前に室温へ戻す</div></div>'
         '<div class="store" style="background:#fff3e8"><h5 style="color:#d9480f">' + icon("thermo") + '常温</h5><ul>'
         '<li>ビューティセム ベニア<span>1〜30℃・暗所</span></li><li>RelyX Universal<span>常温</span></li><li>G-ボンド ユニバーサル<span>常温</span></li><li>TheraCal LC<span>20〜25℃</span></li></ul></div>'
         '<div class="store" style="background:#e9f7ee"><h5 style="color:#23803d">' + icon("check") + 'どちらでも可</h5><ul>'
         '<li>カタナクリーナー<span></span></li><li>Scotchbond Universal Plus<span></span></li><li>SA ルーティング Multi<span></span></li><li>Quick 2<span></span></li>'
         '<li>everX Flow<span></span></li><li>Monobond Etch & Prime<span></span></li><li>ボンドマー ライトレス Ⅱ<span></span></li></ul></div></div>')
h.append(sec("7-2", "毎日の取扱いルール"))
h.append('<div class="grid3">' + "".join(
    f'<div class="rule">{icon(i)}<div class="big">{md(b)}</div>{md(t)}</div>' for i, b, t in [
        ("wait", "5 分以内", "ボトルから出したら使い切る（溶媒が揮発して濃度が変わる）"),
        ("x", "出しっぱなし禁止", "チェアサイドに置きっぱなしにしない。エステコアは使用後すぐ冷蔵庫へ"),
        ("book", "月 1 回", "在庫チェックで全材料の使用期限を確認。期限切れはすぐ下げる")]) + "</div>")
h.append(warn("冷えたまま使うと **結露** し、接着力と流動性が落ちる。**朝の準備で室温に出す** 運用をスタッフで共有する。"))
h.append(note("写真は院内の実物。材料を入れ替えたときは写真と表を更新する。温度の詳細グラフは『接着プロトコル集』5 章。"))

html_out = doc("材料別 使用用途一覧", "\n".join(h)).replace("</style>", EXTRA_CSS + "</style>")
p = os.path.join(HERE, "materials.html")
open(p, "w").write(html_out)
render(p, os.path.join(HERE, "materials.pdf"))
