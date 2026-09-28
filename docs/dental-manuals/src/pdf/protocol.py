from kit import *
import art

C = {k: v[0] for k, v in CAT.items()}
EXTRA_CSS = """
.cover { page: cover; height: 297mm; display: flex; flex-direction: column; }
.hero { background: linear-gradient(135deg, #1f3a5f 0%, #2a5a8f 100%); color: #fff; padding: 22mm 16mm 12mm; position: relative; overflow: hidden; }
.hero .k { font-size: 10pt; letter-spacing: .2em; opacity: .8 }
.hero h1 { font-size: 30pt; margin: 4px 0 6px; line-height: 1.2 }
.hero p { margin: 0; opacity: .9; font-size: 10pt }
.hero svg.bg { position: absolute; right: -20px; top: -10px; width: 260px; height: 260px; opacity: .10; color: #fff }
.cbody { padding: 9mm 16mm 0; flex: 1; display: flex; flex-direction: column; gap: 10px }
.tiles { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.tile { border-radius: 12px; padding: 10px 12px; background: var(--t); border: 1px solid color-mix(in srgb, var(--c) 25%, white); }
.tile .hd { display: flex; align-items: center; gap: 8px; color: var(--c); font-weight: 900; font-size: 12.5pt; margin-bottom: 4px }
.tile .hd .bx { width: 34px; height: 34px; border-radius: 10px; background: var(--c); color: #fff; display: grid; place-items: center }
.tile .hd .bx svg { width: 22px; height: 22px }
.tile ul { margin: 0; padding: 0; list-style: none; font-size: 8.8pt; }
.tile li { display: flex; gap: 6px; padding: 2px 0; border-bottom: 1px dashed color-mix(in srgb, var(--c) 25%, white) }
.tile li:last-child { border: 0 }
.tile li span { color: var(--c); font-weight: 700; width: 34px; flex: none }
.howto { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.howto div { border-radius: 10px; background: #f5f7fa; padding: 8px 10px; font-size: 8.6pt; }
.howto b { display: block; font-size: 9.6pt; color: #1f3a5f; margin-bottom: 1px }
.iconlegend { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; }
.iconlegend div { display: flex; align-items: center; gap: 6px; font-size: 8.4pt; background: #fff; border: 1px solid #e1e6ec; border-radius: 8px; padding: 4px 6px; }
.iconlegend svg { width: 16px; height: 16px; color: #1f3a5f; }
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.stat { border-radius: 10px; border: 1px solid #e1e6ec; padding: 6px 10px; }
.stat .v { font-size: 20pt; font-weight: 900; color: #1f3a5f; line-height: 1.1 }
.stat .l { font-size: 8pt; color: #52606d }
.src { font-size: 7.2pt; color: #8a96a3; padding: 0 16mm 10mm; }
.qt td:first-child { font-weight: 700; }
.catcell { color: #fff; font-weight: 900; text-align: center; writing-mode: vertical-rl; letter-spacing: .15em; font-size: 9pt; border-radius: 6px; }
.cmp td { text-align: center; font-size: 8pt; padding: 5px 4px }
.cmp td:first-child { text-align: left; font-weight: 700; background: #f5f7fa !important; white-space: nowrap }
.cmp th { text-align: center; }
.phase { opacity: .95 }
.phase .sec .t { color: #52606d }
"""

Q2 = ("quick2", "ユニバーサルボンド Quick 2"); FE = ("fineetch37", "FineEtch37"); GB = ("gbond", "G-ボンド ユニバーサル")
ACT = ("activator", "ポーセレンボンド アクティベーター"); LL2 = ("lightless2", "ボンドマー ライトレス Ⅱ")
KC = ("katanacleaner", "カタナクリーナー"); SBU = ("sbuplus", "Scotchbond Universal Plus"); RXU = ("relyxu", "RelyX Universal")
MB = ("monobond", "Monobond Etch & Prime"); BBX = ("beautibondx", "ビューティボンド Xtreme"); BCV = ("beauticem", "BeautiCem Veneer")
CPP = ("cpp", "セラミック プライマー プラス"); SAM = ("samulti", "SA ルーティング Multi"); BL = ("beautilink", "ビューティリンク SA")
RLP = ("relyxlp", "RelyX Luting Plus")

h = []
# ================================================================ COVER
tiles = [
    ("cr", "fill", "CR 充填", [("1-1", "標準（小〜中窩洞）"), ("1-2", "大窩洞・咬合圧が高い"), ("1-3", "露髄・髄床底が近い（覆髄）"), ("1-4", "ホワイトスポット"), ("1-5", "既存 CR への追加・リペア")]),
    ("core", "post", "支台築造", [("2-1", "標準（フェルールあり）"), ("2-2", "フェルールなし（ポスト併用）"), ("2-3", "使用後の後始末")]),
    ("pros", "crown", "補綴装着", [("3-0", "5 種類の比較表"), ("3-1", "ジルコニア"), ("3-2", "e.max"), ("3-3", "e.max ベニア"), ("3-4", "CAD/CAM 冠"), ("3-5", "メタル"), ("3-6/7", "在庫消化中の 2 材料")]),
    ("sp", "shield", "特殊症例・管理", [("4", "スーパーボンド（切り札）"), ("5", "保管温度チャート"), ("6", "メーカー純正の組み合わせ")]),
]
tile_html = "".join(
    f'<div class="tile" style="--c:{CAT[k][0]};--t:{CAT[k][1]}"><div class="hd"><span class="bx">{icon(ic)}</span>{t}</div><ul>'
    + "".join(f"<li><span>{a}</span>{md(b)}</li>" for a, b in items) + "</ul></div>" for k, ic, t, items in tiles)
legend = "".join(f'<div>{icon(i)}{t}</div>' for i, t in [("apply", "塗布・擦り込み"), ("rinse", "水洗"), ("air", "エアブロー"), ("light", "LED 照射"), ("wait", "待つ・静置"),
                                                        ("etch", "エッチング"), ("blast", "サンドブラスト"), ("mix", "混和"), ("place", "装着・圧接"), ("remove", "余剰除去")])
h.append(f"""
<section class="cover">
 <div class="hero">{icon("tooth", cls="bg")}
  <div class="k">BONDING PROTOCOL</div><h1>治療別　接着プロトコル集</h1>
  <p>博多ステラ歯科・矯正歯科クリニック　院内マニュアル</p>
 </div>
 <div class="cbody">
  <div class="stats">
   <div class="stat"><div class="v">4</div><div class="l">治療カテゴリ</div></div>
   <div class="stat"><div class="v">15</div><div class="l">症例別の手順</div></div>
   <div class="stat"><div class="v">4</div><div class="l">早わかりグラフ</div></div>
   <div class="stat"><div class="v">LED</div><div class="l">照射時間はすべて院内 LED 基準</div></div>
  </div>
  <div class="tiles">{tile_html}</div>
  <div class="howto">
   <div><b>① 早見表で材料を決める</b>0 章：治療と状況から、使う材料の組み合わせを選ぶ</div>
   <div><b>② アイコンの手順で操作</b>右の写真は院内の実物。黄色バッジ＝LED 照射時間</div>
   <div><b>③ オレンジ枠を必ず確認</b>失敗・脱離につながりやすいポイント</div>
  </div>
  <div><div style="font-weight:700;font-size:9pt;color:#1f3a5f;margin-bottom:4px">手順アイコンの見かた</div><div class="iconlegend">{legend}</div></div>
 </div>
 <div class="src">出典：トクヤマデンタル「接着ガイドブック」／ 松風「ビューティセム ベニア」添付文書（PMDA）／ BISCO「TheraCal LC」使用説明書 ／ 3M 技術資料 ／ クラレノリタケデンタル製品情報 ／ サンメディカル「スーパーボンド」取扱説明書 ／ ジーシー製品情報。使用前に各製品の添付文書を確認してください。　材料ごとの説明は『材料別 使用用途一覧』へ。</div>
</section>""")

# ================================================================ 0 QUICK TABLE
def qrow(cat, n, situation, chain_html, first=False, stock=False):
    cc = f'<td rowspan="{n}" class="catcell" style="background:{CAT[cat][0]}">{CAT[cat][2]}</td>' if first else ""
    st = ' style="color:#8a96a3"' if stock else ""
    return [cc + f"<td{st}>{md(situation)}</td>", f"<td{st}>{chain_html}</td>"] if first else [f"<td{st}>{md(situation)}</td>", f"<td{st}>{chain_html}</td>"]

def ch(*names, cat="cr"):
    return chain(*[chip(n, cat=cat) for n in names])

rows = []
rows.append(qrow("cr", 5, "標準（小〜中窩洞）", ch("FineEtch37（エナメル質）", "Quick 2", "CR"), True))
rows.append(qrow("cr", 5, "大窩洞・咬合圧が高い", ch("Quick 2", "everX Flow（裏層）", "CR")))
rows.append(qrow("cr", 5, "露髄・髄床底が近い", ch("ダイカル / TheraCal LC / ミエール", "Quick 2", "CR")))
rows.append(qrow("cr", 5, "ホワイトスポット（白濁）", ch("G-ボンド ユニバーサル") + " ／ " + chip("アイコン", cat="cr")))
rows.append(qrow("cr", 5, "既存 CR への追加・リペア", ch("Quick 2 ＋ アクティベーター", "CR")))
rows.append(qrow("core", 2, "標準（フェルールあり）", ch("ライトレス Ⅱ", "everX Flow", cat="core"), True))
rows.append(qrow("core", 2, "フェルールが確保できない", ch("ライトレス Ⅱ", "エステコア ＋ FR ポスト", cat="core")))
rows.append(qrow("pros", 7, "ジルコニア", ch("カタナクリーナー", "SBU Plus", "RelyX Universal", cat="pros"), True))
rows.append(qrow("pros", 7, "e.max（クラウン・インレー）", ch("Monobond E&P", "SBU Plus", "RelyX Universal", cat="pros")))
rows.append(qrow("pros", 7, "e.max ベニア（2.0mm 未満）", ch("Monobond E&P", "ビューティボンド Xtreme", "BeautiCem Veneer", cat="pros")))
rows.append(qrow("pros", 7, "CAD/CAM 冠（保険）", ch("ブラスト", "セラミック プライマー プラス", "SA ルーティング Multi", cat="pros")))
rows.append(qrow("pros", 7, "メタル（保険）", ch("ブラスト", "セラミック プライマー プラス", "SA ルーティング Multi", cat="pros")))
rows.append(qrow("pros", 7, "CAD/CAM 冠・メタル", chip("ビューティリンク SA", "gray") + "　" + chip("在庫消化中", "gray"), stock=True))
rows.append(qrow("pros", 7, "保持形態が十分な金属冠・ブリッジ", chip("RelyX Luting Plus（合着）", "gray") + "　" + chip("在庫消化中", "gray"), stock=True))
rows.append(qrow("sp", 3, "脱離の繰り返し・防湿困難・動揺歯固定", ch("スーパーボンド", cat="sp"), True))
rows.append(qrow("sp", 3, "セラミックのチッピング修理", ch("Quick 2 ＋ アクティベーター", cat="sp")))
rows.append(qrow("sp", 3, "脱離が心配な症例の仕上げ", ch("オキシガード Ⅱ（酸素阻害層対策）", cat="sp")))

h.append(chapter("0", "早見表", desc="治療と状況を選ぶ → 左から右へ材料を使う", ic="book"))
h.append(sec("0-1", "治療・状況別　使う材料の流れ"))
h.append(table(["", "状況", "使う材料（左から順に）"], rows, ["30px", "32%", "auto"], "qt"))

# ---- blast chart
BL_C, MT_C = "#2a78d6", "#eb6834"
blast_rows = [
    dict(label="ジルコニア（3Y）", lo=0.1, hi=0.1, color=BL_C, text="0.1MPa・10mm・10 秒"),
    dict(label="高透光性ジルコニア（4Y・5Y）", lo=0.05, hi=0.1, color=BL_C, text="低圧で"),
    dict(label="ジルコニアの薄いベニア", lo=0.0, hi=0.05, color=BL_C, text="0.05 以下・15mm・5 秒"),
    dict(label="CAD/CAM 冠", lo=0.1, hi=0.2, color=BL_C, text="弱圧（必須）"),
    dict(label="メタル（銀合金・金パラ）", lo=0.3, hi=0.5, color=MT_C, text="10mm・10 秒", bold=True),
    dict(label="非貴金属（Co-Cr・チタン）", lo=0.3, hi=0.5, color=MT_C, text="", bold=True),
    dict(label="e.max・ガラスセラミックス", lo=None, text="ブラストしない → Monobond Etch & Prime"),
    dict(label="ファイバーポスト", lo=None, text="ブラストしない → ライトレス Ⅱ で前処理"),
]
h.append('<div class="nobreak">' + sec("0-2", "サンドブラスト早見グラフ（アルミナ 50µm）"))
h.append('<div class="chart"><h6>被着体ごとのブラスト圧</h6><div class="sub">バーの幅＝使ってよい圧力の範囲。メタルはセラミックス系の 3 倍以上</div>'
         f'<div class="legend"><span><i style="background:{BL_C}"></i>セラミックス・レジン系</span><span><i style="background:{MT_C}"></i>金属</span></div>'
         + art.range_chart(blast_rows, 0, 0.6, [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6], "MPa", label_w=175, note_w=120,
                           bands=[(0.3, 0.5, "#fff1e6", "金属ゾーン")]) + "</div>")
h.append(warn("毎回 **ブラスターの圧力表示を確認** する（セラミックスとメタルで 3 倍以上違う）。内面の光沢が消えるまでが目安。"))
h.append(note("ブラストできない時はリン酸で清掃。ただし **ジルコニアはカタナクリーナー**（リン酸は MDP の結合を阻害）。"))
h.append(note("支台歯エナメル質は原則ブラストしない（ノンプレップベニアのみ 27µm・低圧）。脱離した補綴物の再装着は、材質ごとの圧力で残留セメントを完全に除去。"))
h.append("</div>")

# ---- LED chart + time chart
LED = [
    ("cr", "G-ボンド ユニバーサル（白濁）", 5), ("cr", "Quick 2（ボンド）", 10), ("cr", "Quick 2 ＋ アクティベーター", 10), ("cr", "everX Flow（裏層）", 20), ("cr", "TheraCal LC（1 層ごと）", 20),
    ("core", "FR ポスト挿入後", 10), ("core", "everX Flow・歯冠部（1 層ごと）", 20),
    ("pros", "タックキュア（仮重合）", 3), ("pros", "ビューティボンド Xtreme", 5), ("pros", "BeautiCem Veneer 本重合", 10), ("pros", "RelyX Universal 本重合（各面）", 20), ("pros", "SA Multi（メタルはマージン）", 20),
]
led_rows = [dict(label=l, v=v, color=CAT[c][0], text=("2〜3 秒" if v == 3 else f"{v} 秒") + ("以上" if "SA" in l or "FR" in l else "")) for c, l, v in LED]
h.append(sec("0-3", "時間の早わかり　─「何秒照らす？」「いつまでに使う？」"))
h.append('<div class="chart"><h6>LED 照射時間</h6><div class="sub">院内の LED 照射器の基準。色は治療カテゴリ</div>'
         f'<div class="legend">' + "".join(f'<span><i style="background:{CAT[k][0]}"></i>{CAT[k][2]}</span>' for k in ("cr", "core", "pros")) + "</div>"
         + art.bar_chart(led_rows, 20, [0, 5, 10, 15, 20], "秒") + "</div>")
USE_C, WAIT_C = "#2a78d6", "#9aa6b2"
time_rows = [
    dict(label="ボトルから出した材料", lo=0, hi=5, color=USE_C, text="5 分以内に使い切る"),
    dict(label="スーパーボンド 活性化液", lo=0, hi=5, color=USE_C, text="調製後 5 分以内"),
    dict(label="G-ボンド（平皿）", lo=0, hi=7, color=USE_C, text="操作余裕 約 7 分"),
    dict(label="ライトレス Ⅱ（ブルーラバー皿）", lo=0, hi=3, color=USE_C, text="3 分"),
    dict(label="ライトレス Ⅱ（ディスポ皿）", lo=0, hi=1, color=USE_C, text="1 分"),
    dict(label="RelyX Luting Plus（照射なし）", lo=0, hi=2, color=WAIT_C, text="2 分待ってゲル化 → 除去"),
    dict(label="RelyX Luting Plus 最終硬化", lo=0, hi=5, color=WAIT_C, text="5 分まで咬ませない"),
    dict(label="スーパーボンド 硬化", lo=5, hi=6, color=WAIT_C, text="5〜6 分（クイックモノマー）"),
    dict(label="SA Multi（メタル）完全硬化", lo=0, hi=8, color=WAIT_C, text="8 分以上"),
    dict(label="エステコア 冷蔵 → 室温", lo=0, hi=20, color=WAIT_C, text="20 分以上前に出す"),
]
h.append('<div class="chart"><h6>操作できる時間・待つ時間</h6><div class="sub">青＝この時間内に使い切る　灰＝この時間は待つ</div>'
         f'<div class="legend"><span><i style="background:{USE_C}"></i>使える時間（以内）</span><span><i style="background:{WAIT_C}"></i>待つ時間</span></div>'
         + art.range_chart(time_rows, 0, 20, [0, 2, 4, 6, 8, 10, 15, 20], "分", label_w=175, note_w=135) + "</div>")

h.append(sec("0-4", "失敗・脱離を防ぐ 6 つのルール"))
RULES = [
    ("x", "#c62828", "ジルコニアにリン酸を使わない", "MDP の結合を阻害する。試適後の洗浄は **カタナクリーナー**", "3-1"),
    ("blast", "#4a3aa7", "CAD/CAM 冠はブラスト＋シラン", "弱圧ブラストと **セラミック プライマー プラス** は必須工程", "3-4"),
    ("wait", "#15966a", "ライトレス Ⅱ は 30 秒以内にエア", "遅れると被膜が厚くなる。**光照射は不要**", "2-1"),
    ("rinse", "#2a78d6", "覆髄のときは乾燥させない", "象牙質は **湿ったまま**。乾くと覆髄材が動く", "1-3"),
    ("warn", "#d9480f", "白濁処置で止血剤を使わない", "G-ボンドの接着力が落ち、**水洗しても戻らない**", "1-4"),
    ("fridge", "#2a78d6", "冷蔵品は室温に戻してから", "冷えたままだと **結露** して接着力・流動性が落ちる", "5"),
]
h.append('<div class="grid3">' + "".join(
    f'<div class="card" style="border-top:4px solid {c}"><h5><span style="color:{c}">{icon(i, 18)}</span>{md(t)}</h5>'
    f'<div style="font-size:8.4pt">{md(d)}</div><div style="text-align:right;font-size:7.4pt;color:#8a96a3">→ {ref}</div></div>'
    for i, c, t, d, ref in RULES) + "</div>")

# ================================================================ 1 CR
cr = "cr"
h.append(chapter("1", "CR 充填", cr, "基本は Quick 2。エッチングはエナメル質だけ", "fill"))
h.append(sec("1-1", "標準（小〜中窩洞）", cr))
h.append(with_photos(point("エッチングは **エナメル質だけ**。Quick 2 は **待ち時間なし**。", cr) + steps([
    ("shield", "防湿", None, "ラバーダム、またはワッテ・ZOO ＋ 強力吸引"),
    ("etch", "エナメル質に FineEtch37（象牙質には置かない）", "15 秒"),
    ("rinse", "水洗 → 乾燥", "20 秒"),
    ("apply", "Quick 2 を窩洞全体に擦り込み塗布", "-待ち時間なし"),
    ("air", "強圧エアブロー", "5 秒", "液が動かなくなり、光沢が均一になるまで"),
    ("light", "光照射", "LED 10 秒"),
    ("layer", "CR を 2mm 以下ずつ積層し、各層を照射"),
    ("polish", "形態修正 → 咬合調整 → 研磨"),
], cr), [Q2, FE]))

h.append(sec("1-2", "大窩洞・咬合圧が高い症例", cr))
h.append('<div class="row"><div class="grow">' + point("1-1 の **⑥ ボンド照射まで同じ**。そのあと **everX Flow で裏層** する。", cr) + steps([
    ("fill", "everX Flow を窩洞底から 2mm 程度まで填入", "LED 20 秒"),
    ("layer", "表層は通常の CR で覆う（everX Flow を最表層に出さない）"),
    ("polish", "形態修正 → 研磨"),
], cr) + note("everX Flow は短繊維強化フロアブル。亀裂の進展を抑えるので大臼歯の大窩洞に向く。")
 + '</div><div style="width:44%">' + fig(art.ill_layering(), "断面イメージ：下から everX Flow → CR") + "</div></div>")

h.append(sec("1-3", "露髄・髄床底が近い症例（覆髄）", cr))
cap_cards = [
    ("ダイカル", "保険", "間接覆髄・髄床底が近い", "等量練和 → 最小範囲に塗布", "硬化を待つ", False),
    ("TheraCal LC", "保険", "間接覆髄・直接覆髄", "1mm 以下ずつ塗布", "LED 20 秒 / 層", True),
    ("ミエール", "自費", "非感染歯髄・2mm 以内の偶発露髄", "MTA。練和 → 露髄部に填塞", "硬化を待つ", False),
]
h.append('<div class="grid3">' + "".join(
    f'<div class="card"><h5>{n} {chip(ins, "ok" if ins == "保険" else "warn")}</h5><div style="font-size:8.3pt">{md(ind)}</div>'
    f'<div style="font-size:8.3pt;color:#52606d;margin:3px 0">{md(how)}</div>{time_pill("LED 20 秒 / 層" if led else "待" + cure[:0] + "硬化を待つ（照射なし）")}</div>'
    for n, ins, ind, how, cure, led in cap_cards) + "</div>")
h.append('<div class="row" style="margin-top:6px"><div class="grow">' + steps([
    ("shield", "ラバーダム防湿下で窩洞形成を完了"),
    ("clean", "滅菌綿球を露髄部にそっと当てて止血"),
    ("rinse", "滅菌綿球で軽く拭う。象牙質は **湿ったまま** 残す"),
    ("apply", "覆髄材を露出部に置き、健全象牙質へ **1mm 以上** 延ばす"),
    ("light", "TheraCal LC は各層照射。ダイカル・ミエールは硬化を待つ", "LED 20 秒"),
    ("layer", "Quick 2 → CR で修復"),
], cr) + '</div><div style="width:44%">' + fig(art.ill_pulpcap(), "覆髄材の置き方") + "</div></div>")
h.append(warn("**乾燥させない**（覆髄材が動く）。覆髄材はエナメル質・窩縁に置かず、口腔内に出さない。止血できない時は歯内療法を検討。"))

h.append(sec("1-4", "ホワイトスポット（レジンインフィルトレーション）", cr))
h.append(with_photos(point("G-ボンド ユニバーサルを白濁部に **しみ込ませて** 光の乱反射を抑える。", cr) + steps([
    ("clean", "無フッ素ペーストで清掃 → 水洗 → 防湿"),
    ("etch", "白濁の表層をエッチング → 水洗・乾燥", None, "条件はメーカー資料どおり"),
    ("apply", "付属の **平皿** に採取（深皿は使わない）", "-操作 約 7 分"),
    ("apply", "白濁部に塗布してしみ込ませる", "-エア不要"),
    ("light", "光照射（深い場合は 10 秒）", "LED 5 秒"),
    ("layer", "足りなければ塗布と照射をくり返す"),
    ("polish", "表面を研磨して仕上げ"),
], cr) + warn("**止血剤は使わない**。接着力が落ち、水洗しても戻らない。")
  + note("改善が限られる場合がある。術前に口腔内写真を撮り、患者に説明しておく。"), [GB]))

h.append(sec("1-5", "既存 CR への追加・口腔内リペア", cr))
h.append(with_photos(point("Quick 2 と アクティベーター を **1 滴ずつ混ぜる** とシラン処理になり、既存 CR・セラミックに化学的に付く。", cr)
  + '<div class="fig sm">' + art.ill_mix(("Quick 2", "#1c8c8c"), ("アクティベーター", "#8fd3d0"), ("すぐ使える", "#3aa6a0")) + '<div class="cap">等量 1:1 で混和。作り置きしない</div></div>'
  + steps([
    ("prep", "既存修復物の表面をダイヤモンドポイントかブラストで粗くする"),
    ("etch", "FineEtch37 で清掃 → 水洗 → 乾燥", "5 秒"),
    ("mix", "Quick 2 と アクティベーター を 1 滴ずつ混和"),
    ("apply", "被着面に塗布", "5 秒 / 20 秒", "CR・セラミックのみ 5 秒 ／ 歯質を含む 20 秒"),
    ("air", "マイルドなエアで乾燥（液だまりを残さない）", "5 秒以上"),
    ("light", "光照射", "LED 10 秒"),
    ("layer", "CR を積層・照射 → 形態修正 → 研磨"),
], cr) + warn("**作り置きしない**（毎回 1 滴ずつ）。冷蔵品なので使用前に室温へ。")
  + note("メガボンド 2 のプライマーとも混和できる。セラミックのチッピング修理も同じ手順。"), [Q2, ACT, FE]))

# ================================================================ 2 CORE
co = "core"
h.append(chapter("2", "支台築造（コア）", co, "ライトレス Ⅱ は光照射不要。塗ったら 30 秒以内にエア", "post"))
h.append(sec("2-1", "標準（フェルールあり・ポスト不要）", co))
h.append('<div class="row"><div class="grow">' + point("ライトレス Ⅱ は **光照射不要**。塗ったら **30 秒以内** にエアブロー。", co) + steps([
    ("prep", "築造窩洞形成 → 防湿"),
    ("mix", "A 液（黄）・B 液（青）を 1 滴ずつ混和 → **緑色** で完了", None, "操作時間　ブルーラバー皿 3 分 ／ ディスポ皿 1 分"),
    ("apply", "窩洞に塗布 → すぐエアへ", "30 秒以内"),
    ("air", "弱圧（ボンド層が動かなくなるまで）→ 中〜強圧で十分乾燥", "-照射不要"),
    ("fill", "everX Flow を根管口から 2〜3mm まで填入", "LED 20 秒"),
    ("layer", "歯冠部を 4mm 以下ずつ積層", "LED 20 秒 / 層"),
    ("light", "頬（唇）側・舌側から追加照射", "LED 各 20 秒"),
    ("prep", "支台歯形成"),
], co) + '</div><div style="width:44%">' + fig(art.ill_core(), "断面イメージ：everX Flow で根管口〜歯冠部を築造")
  + fig(art.ill_mix(("A 液（黄）", "#f2c230"), ("B 液（青）", "#3b7fd9"), ("緑色 ＝ 混和完了", "#2fa35b")), "ライトレス Ⅱ の混和") + photos([LL2], True) + "</div></div>")
h.append(warn("エアブローが **30 秒より遅れる** と被膜が厚くなる。／ everX Flow は光重合のみ。**根管の奥まで入れない**（未重合が残る）。硬化深度 5.5mm。"))

h.append(sec("2-2", "フェルールが確保できない症例（ポスト併用）", co))
h.append('<div class="row"><div class="grow">' + point("**ポストも歯も同じボンド**（ライトレス Ⅱ）で処理する。", co) + steps([
    ("prep", "根管形成・築造窩洞形成 → トクヤマ FR ポストを試適"),
    ("apply", "ライトレス Ⅱ をポストに塗布 → 中圧エアで十分乾燥", "30 秒以内"),
    ("apply", "窩洞・根管内に塗布 → エアブロー", "30 秒以内"),
    ("air", "弱圧 → 中〜強圧で全体を十分乾燥"),
    ("fill", "エステコアを根管口に填入 → 空気を巻き込まないようポスト挿入"),
    ("light", "ポストを固定したまま照射", "LED 10 秒以上"),
    ("layer", "歯冠部を積層 → 2 方向から追加照射", "LED 20 秒 / 層"),
    ("prep", "支台歯形成"),
], co) + '</div><div style="width:44%">' + fig(art.ill_post(), "断面イメージ：FR ポスト ＋ エステコア") + "</div></div>")
h.append(warn("**ボンド塗布後にポストを試適しない**。処理済みのポストと補綴物を触れさせない（接着して外れなくなる）。"))
h.append('<div class="point" style="--c:#15966a;--t:#e3f5ee;margin-top:8px"><span class="lb">後始末</span><span>'
         '<b>ボトル</b>：ノズルとキャップの内側を拭いてから閉める　／　<b>混和皿</b>：ブルーラバーはアルコール清掃で再使用（' + chip("オートクレーブ不可", "ng") + '）、ディスポは使い捨て</span></div>')

# ================================================================ 3 PROSTHESES
pr = "pros"
h.append(chapter("3", "補綴物の装着", pr, "どれも「補綴物側 → 歯牙側 → 装着」の 3 段階", "crown"))
h.append(sec("3-0", "5 種類の違いがひと目でわかる比較表", pr))
ok_, ng_ = chip("必要", "ok"), chip("不要", "gray")
cmp_rows = [
    ["ブラスト", chip("0.1MPa", "ok"), ng_, ng_, chip("0.1〜0.2MPa", "ok"), chip("0.3〜0.5MPa", "warn")],
    ["内面の洗浄", chip("カタナクリーナー", cat=pr), "水洗", "トライインを洗い流す", "水洗", "水洗（汚染時エタノール）"],
    ["内面プライマー", chip("SBU Plus", cat=pr), chip("Monobond E&P", cat=pr), chip("Monobond E&P", cat=pr), chip("CPP", cat=pr), chip("CPP", cat=pr)],
    ["歯面エッチング", "─", "エナメル 15〜30 秒", "エナメル（ノンプレップ 60 秒）", "─", "─"],
    ["歯面ボンド", chip("SBU Plus", cat=pr), chip("SBU Plus", cat=pr), chip("BB Xtreme", cat=pr) + "<br><small>LED 5 秒</small>", chip("不要", "gray"), chip("不要", "gray")],
    ["セメント", chip("RelyX Universal", cat=pr), chip("RelyX Universal", cat=pr), chip("BeautiCem Veneer", cat=pr), chip("SA Multi", cat=pr), chip("SA Multi", cat=pr)],
    ["仮重合", "2〜3 秒", "2〜3 秒", "2〜3 秒（1〜2cm 離す）", "2〜3 秒", "マージン 20 秒以上"],
    ["本重合", "各面 20 秒", "各面 20 秒", "各方向 10 秒 ＋ オキシガード", "各面 20 秒以上", "完全硬化 8 分以上"],
]
h.append(table(["", "ジルコニア", "e.max", "e.max ベニア", "CAD/CAM 冠", "メタル"], cmp_rows,
               ["14%", "17%", "17%", "18%", "17%", "17%"], "cmp"))
h.append(note("SBU Plus＝Scotchbond Universal Plus　CPP＝セラミック プライマー プラス　SA Multi＝SA ルーティング Multi　BB Xtreme＝ビューティボンド Xtreme"))
h.append('<div class="grid2" style="margin-top:6px">'
         + warn("**ジルコニアにリン酸・Monobond E&P は使わない**（MDP 阻害／ガラス相がない）。") + warn("**CAD/CAM 冠はブラスト＋シラン処理が必須**。省略は脱離の主因。") + "</div>")

def prosth(no, title, pt, lanes_def, photo_items, warns=(), notes=(), tag=None):
    out = sec(no, title, pr, tag) + '<div class="row" style="align-items:center"><div class="grow">' + point(pt, pr)
    out += "".join(warn(w) for w in warns) + "".join(note(n) for n in notes)
    out += "</div>" + photos(photo_items, True) + "</div>" + lanes(lanes_def, pr)
    return '<div class="nobreak">' + out + "</div>"

SIDE, TOOTH, SET = ("補綴物側", "crown"), ("歯牙側", "tooth"), ("装着", "place")
def L(side, st): return (side[0], side[1], st)
tooth_basic = [("clean", "仮着材を除去 → 清掃 → 防湿")]
set_rxu = [("apply", "RelyX Universal を塗布 → 装着・圧接"), ("light", "タックキュア", "LED 2〜3 秒"), ("remove", "余剰除去・隣接はフロス"),
           ("light", "本重合 各面", "LED 20 秒"), ("polish", "辺縁確認 → 研磨")]

h.append(prosth("3-1", "ジルコニア（クラウン・ブリッジ）", "洗浄は **カタナクリーナー**（リン酸 ✕）。プライマーは **SBU Plus だけ**。", [
    L(SIDE, [("blast", "サンドブラスト 50µm・10mm", "0.1MPa・10 秒", "4Y・5Y は 0.05〜0.1MPa"), ("clean", "カタナクリーナー → 水洗 → 乾燥", "10 秒"), ("apply", "SBU Plus 塗布 → エア", "5 秒", "照射なし")]),
    L(TOOTH, tooth_basic + [("apply", "SBU Plus を擦り込み", "20 秒"), ("air", "エアブロー", "5 秒", "照射不要（RelyX Universal が硬化させる）")]),
    L(SET, set_rxu)], [KC, SBU, RXU],
    warns=["セラミック プライマー プラスは **重ねない**（SBU Plus に MDP・シラン入り。膜が厚くなる）。"]))

h.append(prosth("3-2", "e.max（クラウン・インレー・アンレー）", "内面は **Monobond Etch & Prime だけ** でエッチング＋シラン。ブラスト不要。", [
    L(SIDE, [("apply", "Monobond E&P をすり込む", "20 秒"), ("wait", "静置", "待 40 秒"), ("rinse", "水洗 → 乾燥")]),
    L(TOOTH, tooth_basic + [("etch", "エナメルに FineEtch37", "15〜30 秒"), ("rinse", "水洗 → 乾燥", "20 秒"), ("apply", "SBU Plus 擦り込み → エア", "20 秒 / 5 秒")]),
    L(SET, set_rxu)], [MB, SBU, RXU]))

h.append(prosth("3-3", "e.max ベニア（BeautiCem Veneer）", "使えるのは **厚さ 2.0mm 未満・光を通す修復物だけ**。ボンドは **ビューティボンド Xtreme**（添付文書で指定）。", [
    L(SIDE, [("apply", "トライインで試適・色確認", None, "M / L / H-Value"), ("rinse", "強圧 3WAY でトライインを完全に除去", None, "水溶性。残っていないか確認"),
             ("apply", "Monobond E&P → 静置 → 水洗・乾燥", "20 秒 / 40 秒")]),
    L(TOOTH, [("clean", "仮着材除去 → 無フッ素ペーストで清掃 → 防湿"), ("etch", "FineEtch37 → 水洗 → 乾燥", None, "ノンプレップは 60 秒"),
              ("apply", "BB Xtreme をこする", "20 秒"), ("air", "弱エア 3 秒 → 強エア", None, "光沢が均一でなければやり直す"), ("light", "照射", "LED 5 秒")]),
    L(SET, [("place", "BeautiCem Veneer で装着・圧接"), ("light", "1〜2cm 離して半硬化", "LED 2〜3 秒"), ("remove", "圧接したまま余剰除去"),
            ("light", "各方向から本重合", "LED 10 秒"), ("apply", "辺縁にオキシガード Ⅱ", "LED 10 秒"), ("polish", "水洗 → マージン研磨")])], [MB, BBX, BCV]))

h.append(prosth("3-4", "CAD/CAM 冠（保険）", "**ブラスト** と **シラン処理**（CPP）は必須。省くと脱離する。", [
    L(SIDE, [("blast", "サンドブラスト 50µm", "0.1〜0.2MPa", "弱圧で"), ("rinse", "水洗 → 乾燥"), ("apply", "CPP 塗布 → 十分にエア")]),
    L(TOOTH, tooth_basic + [("check", "前処理は不要", None, "SA セメントのため")]),
    L(SET, [("apply", "SA Multi を塗布 → 装着・圧接"), ("light", "タックキュア", "LED 2〜3 秒"), ("remove", "余剰除去"), ("light", "本重合 各面", "LED 20 秒以上"), ("polish", "辺縁確認 → バリ除去")])], [CPP, SAM]))

h.append(prosth("3-5", "メタル（銀合金・金銀パラジウム合金）", "ブラスト圧は **セラミックの 3 倍以上**。金属は光を通さないので **マージンから照射**。", [
    L(SIDE, [("blast", "サンドブラスト 50µm・10mm", "0.3〜0.5MPa", "光沢が消えるまで。銀合金は装着直前に"), ("rinse", "水洗 → 完全乾燥", None, "唾液汚染はエタノール綿球で"), ("apply", "CPP 塗布 → 十分にエア")]),
    L(TOOTH, tooth_basic + [("check", "前処理は不要")]),
    L(SET, [("apply", "SA Multi を塗布 → 装着・圧接"), ("light", "マージンに照射", "LED 20 秒以上"), ("remove", "余剰除去"), ("wait", "完全硬化", "待 8 分以上"), ("polish", "辺縁確認 → バリ除去")])], [CPP, SAM]))

h.append('<div class="phase">')
h.append(prosth("3-6", "ビューティリンク SA", "セルフアドヒーシブ。CAD/CAM 冠・金属冠・ジルコニアに使える。", [
    L(SIDE, [("blast", "ブラスト 50〜100µm", None, "セラミック・CR 系 0.1〜0.2 ／ 金属 0.3〜0.5MPa"), ("rinse", "水洗 → 乾燥"), ("apply", "プライマー", None, "ジルコニア・メタル・CAD/CAM → CPP ／ ガラスセラミックス → ポーセレンプライマー等")]),
    L(TOOTH, tooth_basic + [("check", "前処理不要", None, "CAD/CAM でより強く付けたい時は BB Xtreme")]),
    L(SET, [("apply", "チップ装着・最初の少量は捨てる"), ("place", "塗布 → 装着・圧接"), ("light", "短時間タックキュア → 余剰除去"), ("light", "本重合", "LED 10 秒"), ("polish", "辺縁確認 → バリ除去")])], [BL],
    warns=["使用前に **ロット番号と使用期限** を確認。期限切れはチェアサイドから下げる。"], tag="在庫消化中"))

h.append(prosth("3-7", "RelyX Luting Plus（合着）", "レジン強化型グラスアイオノマー。保持形態が十分な **金属冠・ブリッジ・ジルコニア・既製ポスト** 用。", [
    L(SIDE, [("clean", "試適 → 内面を清掃 → 乾燥", None, "プライマー不要")]),
    L(TOOTH, [("clean", "仮着材を完全に除去"), ("rinse", "オイルフリーのペーストで清掃 → 水洗"), ("air", "軽く乾燥（**湿り気を残す**）")]),
    L(SET, [("mix", "クリッカー 1〜2 回 → 練和"), ("place", "塗布 → 装着・圧接"), ("light", "照射 → 余剰を一塊で除去", "LED 5 秒", "照射しない時は 2 分待つ"), ("wait", "最終硬化まで咬ませない", "待 5 分")])], [RLP],
    warns=["歯面を乾かしすぎない（過乾燥は接着不良・術後疼痛の原因）。**CAD/CAM 冠・e.max・ベニアには使えない**。"], tag="在庫消化中"))
h.append("</div>")

# ================================================================ 4 SUPERBOND
sp = "sp"
h.append(chapter("4", "スーパーボンド（切り札）", sp, "少しの水分・酸素があるほうが重合が進む", "shield"))
uses = [("x", "脱離をくり返す"), ("rinse", "防湿が難しい"), ("crown", "接着ブリッジ"), ("tooth", "動揺歯の暫間固定"), ("prep", "破折歯の接着"), ("cube", "矯正装置の接着")]
h.append(sec("4-1", "こんな時に使う", sp))
h.append('<div class="grid3">' + "".join(f'<div class="card" style="display:flex;align-items:center;gap:8px;padding:6px 10px"><span style="color:{C[sp]}">{icon(i, 20)}</span><b>{t}</b></div>' for i, t in uses) + "</div>")
h.append(sec("4-2", "筆積法の手順", sp))
h.append('<div class="row"><div class="grow">' + steps([
    ("clean", "被着歯面を清掃（仮着材・仮封材・歯垢を完全に除去）"),
    ("etch", "象牙質に 表面処理材グリーン → 水洗 → 乾燥", "10 秒"),
    ("clean", "試適した修復物は 表面処理材レッド か超音波洗浄"),
    ("apply", "プライマーを一層だけ薄く", None, "ジルコニア・ポーセレン → PZ プライマー ／ 貴金属 → V-プライマー"),
    ("mix", "活性化液をつくる：モノマー液 **4 滴 ＋ キャタリスト V 1 滴**"),
    ("apply", "被着面に活性化液を 1 層塗る"),
    ("apply", "筆積みでセメント玉をつくって塗る", None, "筆先 1mm で、ポリマー粉末をゆっくり円を描いて採る"),
    ("place", "修復物を圧接し、硬化まで保持", "待 5〜6 分"),
    ("remove", "硬化後に余剰セメントを除去"),
], sp) + '</div><div style="width:42%">' + fig(art.ill_superbond(), "活性化液の調製と使用期限") + "</div></div>")
h.append(sec("4-3", "禁忌・注意", sp))
h.append('<div class="grid2">' + "".join(
    f'<div class="card"><h5><span style="color:{c}">{icon(i, 16)}</span>{t}</h5>{md(d)}</div>' for i, c, t, d in [
        ("warn", "#d9480f", "次亜塩素酸ナトリウム", "接着強さが大きく落ちる。使うなら **表面処理材グリーンの前に、15 秒以内**"),
        ("tooth", "#1f3a5f", "装着当日", "硬化はゆっくり進む。**硬いものを噛まない** よう患者に伝える"),
        ("apply", "#1f3a5f", "筆の洗浄", "専用の **筆洗い液 Ⅱ** を使い、筆先を整えて乾燥"),
        ("fridge", "#2a78d6", "保管", "**冷蔵**。使用前に室温へ戻す")]) + "</div>")

# ================================================================ 5 STORAGE
h.append(chapter("5", "保管温度チャート", None, "冷蔵品は使う前に室温へ。結露は接着力低下のもと", "thermo"))
FR, RT = "#2a78d6", "#eb6834"
st_rows = [
    dict(label="エステコア（ペースト）", lo=0, hi=10, color=FR, text="使用 20 分前に室温へ", bold=True),
    dict(label="セラミック プライマー プラス", lo=2, hi=8, color=FR, text="使用直前に室温へ", bold=True),
    dict(label="ボンドマー ライトレス Ⅱ", lo=0, hi=25, color=RT, text="常温可"),
    dict(label="ユニバーサルボンド Quick 2", lo=2, hi=25, color=RT, text="冷蔵庫保管も可"),
    dict(label="カタナクリーナー", lo=2, hi=25, color=RT, text=""),
    dict(label="Scotchbond Universal Plus", lo=2, hi=25, color=RT, text=""),
    dict(label="SA ルーティング Multi", lo=2, hi=25, color=RT, text=""),
    dict(label="Monobond Etch & Prime", lo=2, hi=28, color=RT, text=""),
    dict(label="ビューティセム ベニア", lo=1, hi=30, color=RT, text="暗所"),
    dict(label="TheraCal LC", lo=20, hi=25, color=RT, text=""),
]
h.append('<div class="chart"><h6>保管してよい温度の範囲</h6><div class="sub">ボトル・外箱・添付文書の表記、または院内確認による。水色の帯＝冷蔵庫（2〜8℃）</div>'
         f'<div class="legend"><span><i style="background:{FR}"></i>冷蔵が必要</span><span><i style="background:{RT}"></i>常温で保管できる</span></div>'
         + art.range_chart(st_rows, 0, 30, [0, 5, 10, 15, 20, 25, 30], "℃", label_w=175, note_w=115,
                           bands=[(2, 8, "#e3f0fc", "冷蔵庫"), (15, 25, "#fff4ea", "室温")], fmt=lambda v: f"{v:g}℃") + "</div>")
h.append('<div class="grid3">'
         f'<div class="card" style="background:#eef6fe"><h5 style="color:{FR}">{icon("fridge", 18)} 冷蔵（温度表記なし）</h5>スーパーボンド<br>オキシガード Ⅱ<br>ポーセレンボンド アクティベーター<small>いずれも使用直前に室温へ</small></div>'
         f'<div class="card" style="background:#fff6ee"><h5 style="color:{RT}">{icon("thermo", 18)} 常温（温度表記なし）</h5>RelyX Universal<br>G-ボンド ユニバーサル</div>'
         f'<div class="card" style="background:#eef8f2"><h5 style="color:#15966a">{icon("check", 18)} どちらでも可</h5>everX Flow<small>冷蔵したら室温に戻す（冷えたままだと流れが悪い）</small></div></div>')
h.append(warn("冷えたまま使うと **結露** し、接着力と流動性が落ちる。**朝の準備で室温に出す** 運用をスタッフで共有する。"))
h.append(note("材料を入れ替えたら本チャートを更新する。"))

# ================================================================ 6 COMBOS
h.append(sec("6", "メーカー純正の組み合わせ"))
MK = {"クラレノリタケ": "#2a78d6", "3M": "#e34948", "松風": "#1baf7a", "ジーシー": "#eda100", "トクヤマ": "#4a3aa7", "Ivoclar": "#e87ba4", "他社": "#9aa6b2"}
def mk(name): return f'<span class="chip" style="--c:#3d4a57;--t:#fff;border-left:5px solid {MK[name]}">{name}</span>'
combos = [
    ("Quick 2", "オキシガード Ⅱ", "クラレノリタケ", "クラレノリタケ", "純正", "ok"),
    ("セラミック プライマー プラス", "SA ルーティング Multi", "クラレノリタケ", "クラレノリタケ", "純正", "ok"),
    ("Scotchbond Universal Plus", "RelyX Universal", "3M", "3M", "純正", "ok"),
    ("ビューティボンド Xtreme", "ビューティセム ベニア", "松風", "松風", "純正（添付文書指定）", "ok"),
    ("G-ボンド ユニバーサル", "everX Flow", "ジーシー", "ジーシー", "純正（切替候補）", "ok"),
    ("ボンドマー ライトレス Ⅱ", "everX Flow", "トクヤマ", "ジーシー", "跨ぎ（承知のうえで採用）", "warn"),
    ("Monobond Etch & Prime", "RelyX Universal", "Ivoclar", "3M", "跨ぎ", "warn"),
    ("ボンドマー ライトレス Ⅱ", "他社セメント", "トクヤマ", "他社", "跨ぎ", "warn"),
]
h.append('<div class="grid2">' + "".join(
    f'<div class="card" style="padding:6px 10px;border-left:4px solid {"#23803d" if k == "ok" else "#d9480f"}">'
    f'<div style="display:flex;justify-content:space-between;align-items:center;gap:6px"><b style="font-size:8.8pt">{md(a)} ＋ {md(b)}</b>{chip(j.split("（")[0], k)}</div>'
    f'<div style="margin-top:3px">{mk(ma)} {"" if ma == mb else mk(mb)}<small style="margin-left:6px">{md(j[len(j.split("（")[0]):])}</small></div></div>'
    for a, b, ma, mb, j, k in combos) + "</div>")
h.append(note("ライトレス Ⅱ ＋ everX Flow は添付文書外の組み合わせ。脱離時の説明に備え、採用判断をカルテ運用として記録しておく。"))

html_out = doc("治療別 接着プロトコル集", "\n".join(h)).replace("</style>", EXTRA_CSS + "</style>")
p = os.path.join(HERE, "protocol.html")
open(p, "w").write(html_out)
render(p, os.path.join(HERE, "protocol.pdf"))
