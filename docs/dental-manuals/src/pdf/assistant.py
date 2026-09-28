from kit import *

A = os.path.join(IMG, "asst")
COL = {"daily": "#15966a", "patient": "#d9480f", "basic": "#2a78d6", "treat": "#4a3aa7", "flow": "#c2477a"}
TINT = {"daily": "#e3f5ee", "patient": "#fff1e6", "basic": "#e8f1fc", "treat": "#ecebf8", "flow": "#fbe9f1"}
for k in COL: CAT[k] = (COL[k], TINT[k], "")

EXTRA_CSS = """
.cover { page: cover; height: 297mm; display: flex; flex-direction: column; }
.hero { background: linear-gradient(135deg, #15966a 0%, #1f7a9a 100%); color: #fff; padding: 20mm 16mm 10mm; position: relative; overflow: hidden; }
.hero .k { font-size: 10pt; letter-spacing: .2em; opacity: .85 }
.hero h1 { font-size: 32pt; margin: 4px 0 6px; line-height: 1.2 }
.hero p { margin: 0; opacity: .92; font-size: 10pt }
.hero .ver { display: inline-block; margin-top: 8px; font-size: 8.5pt; background: rgba(255,255,255,.18); border-radius: 99px; padding: 2px 10px }
.cbody { padding: 7mm 16mm 0; flex: 1; display: flex; flex-direction: column; gap: 8px }
.namebox { display: flex; align-items: center; gap: 14px; }
.namebox .ln { flex: 1; border-bottom: 1.5px solid #52606d; height: 26px; }
.namebox img { width: 120px; }
.toc { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.tg { border-radius: 12px; padding: 8px 12px; background: var(--t); }
.tg h4 { margin: 0 0 4px; color: var(--c); font-size: 10.5pt; }
.tg div { display: flex; gap: 8px; padding: 2px 0; font-size: 9pt; border-bottom: 1px dashed color-mix(in srgb, var(--c) 22%, white) }
.tg div:last-child { border: 0 }
.tg div b { color: var(--c); width: 16px; flex: none }
.newflag { display: inline-block; font-size: 7pt; font-weight: 700; color: #fff; background: #d9480f; border-radius: 4px; padding: 0 5px; margin-left: 4px; vertical-align: 1px }
.philo { text-align: center; padding: 18mm 10mm 10mm; }
.philo .lb { font-size: 10pt; letter-spacing: .3em; color: #15966a; font-weight: 700 }
.philo .q { font-size: 20pt; font-weight: 900; color: #1d2733; margin: 8px 0 20px; line-height: 1.5 }
.philo .q:before, .philo .q:after { color: #15966a; }
.goal { margin: 0 auto; max-width: 150mm; background: #f5f7fa; border-radius: 14px; padding: 12px 18px; text-align: left; font-size: 10.5pt }
.goal b { color: #15966a }
.check { display: grid; grid-template-columns: 1fr 1fr; gap: 3px 14px; margin: 3px 0 6px; }
.check.one { grid-template-columns: 1fr; }
.ck { display: flex; gap: 7px; align-items: flex-start; font-size: 8.9pt; padding: 3px 4px; border-bottom: 1px dotted #dfe4ea; break-inside: avoid; }
.ck:before { content: ""; flex: none; width: 11px; height: 11px; border: 1.6px solid var(--c, #15966a); border-radius: 3px; margin-top: 3px; }
.ck.new { background: #fff6ee; border-radius: 6px; }
.ck small { display: block; }
.grp { display: flex; align-items: center; gap: 6px; font-weight: 700; color: var(--c); margin: 8px 0 2px; font-size: 9.6pt; }
.grp svg { width: 16px; height: 16px; }
.talk { display: inline-block; background: #fff; border: 1.5px solid #f2a77a; color: #b33a07; border-radius: 12px 12px 12px 2px; padding: 1px 9px; font-weight: 700; margin: 1px 0 }
.abbr { display: grid; grid-template-columns: repeat(3, 1fr); gap: 5px; }
.abbr div { display: flex; justify-content: space-between; align-items: center; border: 1px solid #e1e6ec; border-radius: 8px; padding: 3px 9px; font-size: 8.8pt }
.abbr b { font-size: 10pt; color: #2a78d6; font-family: "Noto Sans CJK JP"; }
.pic { border-radius: 9px; border: 1px solid #e1e6ec; display: block; width: 100%; object-fit: cover; }
.piccap { font-size: 7.6pt; color: #52606d; text-align: center; margin-top: 2px }
.hp { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-top: 4px }
.hp div { border-radius: 8px; padding: 5px 5px; font-size: 7.6pt; background: #f5f7fa; border-top: 4px solid var(--hc); line-height: 1.35 }
.hp b { display: block; font-size: 8.6pt; }
.twocol { display: grid; grid-template-columns: 1fr 200px; gap: 12px; align-items: start; }
.twocol.nopic { grid-template-columns: 1fr; }
.prep { display: flex; flex-wrap: wrap; gap: 3px; align-items: center; margin: 2px 0 6px; }
.prep .lbl { font-size: 7.8pt; font-weight: 700; color: #fff; background: var(--c); border-radius: 5px; padding: 1px 7px; margin-right: 3px }
.prep .it { font-size: 8pt; border: 1px solid #d5dbe2; border-radius: 99px; padding: 0 8px; background: #fff; }
.prep .it.new { border-color: #f2a77a; background: #fff6ee; color: #b33a07; font-weight: 700 }
.days { display: flex; gap: 0; margin: 4px 0 8px; }
.days div { flex: 1; text-align: center; background: var(--t); border: 1px solid color-mix(in srgb, var(--c) 30%, white); padding: 5px 3px; font-size: 8.2pt; position: relative; }
.days div:first-child { border-radius: 8px 0 0 8px } .days div:last-child { border-radius: 0 8px 8px 0 }
.days div + div { border-left: 0 }
.days b { display: block; color: var(--c); font-size: 7.4pt; }
.fc { display: flex; flex-direction: column; align-items: stretch; gap: 0; }
.fc .b { border-radius: 9px; padding: 5px 10px; background: #fff; border: 1.5px solid var(--c); font-size: 8.8pt; text-align: center; }
.fc .b b { color: var(--c) }
.fc .b small { display: block }
.fc .ar { text-align: center; color: #9aa6b2; font-size: 10pt; line-height: 1.2; }
.fc .ar small { font-size: 7.4pt }
.branch { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.side { display: flex; align-items: center; gap: 6px; }
.side .b { flex: 1 }
.side .go { flex: none; font-size: 7.8pt; color: #23803d; font-weight: 700; background: #e9f7ee; border-radius: 99px; padding: 2px 8px; white-space: nowrap }
.chg td:first-child { white-space: nowrap; font-weight: 700 }
.chg .old { color: #8a96a3; text-decoration: line-through; }
.chg .new { color: #b33a07; font-weight: 700; }
"""

def ck(items, one=False):
    out = []
    for it in items:
        new = isinstance(it, tuple) and it[0] == "NEW"
        t = it[1] if new else it
        sub = ""
        if isinstance(t, tuple): t, sub = t
        out.append(f'<div class="ck{" new" if new else ""}"><span>{md(t)}{"<span class=newflag>NEW</span>" if new else ""}'
                   f'{f"<small>{md(sub)}</small>" if sub else ""}</span></div>')
    return f'<div class="check{" one" if one else ""}">' + "".join(out) + "</div>"

def grp(ic, t, cat):
    return f'<div class="grp" style="--c:{COL[cat]}">{icon(ic)}{md(t)}</div>'

def prep(items, cat="treat"):
    its = "".join(f'<span class="it{" new" if i.startswith("!") else ""}">{md(i.lstrip("!"))}</span>' for i in items)
    return f'<div class="prep" style="--c:{COL[cat]}"><span class="lbl">準備物</span>{its}</div>'

def pic(name, cap="", h=None):
    st = f' style="height:{h}"' if h else ""
    return f'<div><img class="pic" src="{A}/{name}.jpg"{st}>{f"<div class=piccap>{md(cap)}</div>" if cap else ""}</div>'

def tx(body, side=""):
    return f'<div class="twocol{"" if side else " nopic"}"><div>{body}</div>{f"<div>{side}</div>" if side else ""}</div>'

def days(items, cat="treat"):
    return f'<div class="days" style="--c:{COL[cat]};--t:{TINT[cat]}">' + "".join(f"<div><b>{md(d)}</b>{md(t)}</div>" for d, t in items) + "</div>"

def newbox(text):
    return f'<div class="point" style="--c:#d9480f;--t:#fff1e6"><span class="lb">改訂</span><span>{md(text)}</span></div>'

h = []
# ================================================================ COVER
toc = [
    ("daily", "毎日の業務", [("A", "朝の準備＆掃除"), ("B", "夜の片づけ＆掃除"), ("G", "治療ごとの後片付け"), ("H", "感染症の患者さんの準備と片づけ")]),
    ("patient", "患者さん対応", [("C", "来院（受付）からユニット案内")]),
    ("basic", "基礎知識", [("D", "歯式"), ("E", "器具"), ("I", "レントゲン"), ("J", "歯の構造")]),
    ("treat", "治療のアシスト", [("F", "治療ごとの準備と流れ　<span class=newflag>改訂</span>")]),
    ("flow", "治療の流れ", [("K", "虫歯の進行と治療の流れ"), ("L", "歯周病の進行と治療の流れ")]),
]
h.append(f"""<section class="cover">
 <div class="hero"><div class="k">ASSISTANT MANUAL</div><h1>アシスタントマニュアル</h1>
  <p>博多ステラ歯科・矯正歯科クリニック</p><span class="ver">2026 年改訂版　｜　接着材料の統一に合わせて更新</span></div>
 <div class="cbody">
  <div class="namebox"><span style="font-weight:700">名前</span><span class="ln"></span><img src="{A}/mascot.jpg"></div>
  <div class="toc">{"".join(f'<div class="tg" style="--c:{COL[k]};--t:{TINT[k]}"><h4>{t}</h4>' + "".join(f"<div><b>{a}</b><span>{b}</span></div>" for a, b in its) + "</div>" for k, t, its in toc)}
   <div class="tg" style="--c:#d9480f;--t:#fff1e6"><h4>この版で変わったところ</h4><div><b>★</b><span>最終ページの「改訂箇所一覧」を確認</span></div><div><b>★</b><span>本文中の <span class=newflag>NEW</span> <span class=newflag>改訂</span> が変更点</span></div></div>
  </div>
  <div class="grid3">
   <div class="card"><b>① まず A・B・C</b><br><span class="muted">入職したら毎日の準備・片づけ・患者さん案内から</span></div>
   <div class="card"><b>② 次に D・E・J</b><br><span class="muted">歯式・器具・歯の構造を覚える</span></div>
   <div class="card"><b>③ そして F・K・L</b><br><span class="muted">治療のアシストと、治療全体の流れ</span></div>
  </div>
 </div>
</section>""")

# ================================================================ PHILOSOPHY
h.append(f"""<div style="break-before:page"></div><div class="philo"><div class="lb">医院理念</div>
<div class="q">『クリニックにかかわるすべての人の<br>自己実現をかなえるサポートをし、<br>幸せと笑顔を届ける』</div>
<div class="goal"><div style="font-weight:900;color:#15966a;margin-bottom:4px">行動目標</div>
症状がなくても <b>「また来たい」「また行かなきゃ」</b> と思ってもらえるクリニックにする。<br>そのためにも <b>リコール（定期健診）の大切さ</b> を伝えていく。</div></div>""")

# ================================================================ A
d = "daily"
h.append(chapter("A", "朝　診療開始前の準備＆掃除", d, "上から順にチェック", "check"))
h.append(grp("light", "電源を入れる", d) + ck([
    "コンプレッサーを ON", "寒天の機械を ON", "電気ポットでお湯をわかす",
    ("チェアーのメインスイッチ・テーブル下のスイッチ・モニターを ON", "水のバルブを開ける"),
    "加湿器に水を入れてつける", "空気清浄機の電源を入れる", "PC・X-ray の電源を入れる"]))
h.append(grp("clean", "掃除", d) + ck(["掃除機をかける"]))
h.append(grp("layer", "準備", d) + ck([
    "タービン・コントラ・ストレートの油抜き", "滅菌済みの物を乾燥させる", "保湿箱をつくる", "洗濯物を取り込む・たたむ・干す",
    ("バキュームに水を吸わせる", "1 台につき 1 リットル"), "ワッテ用のピンセット準備", "照射器を CR の BOX に入れる",
    ("NEW", ("冷蔵庫の接着材料を室温に出す", "セラミック プライマー プラス・オキシガード Ⅱ・ポーセレンボンド アクティベーター・スーパーボンド。冷えたまま使うと結露して接着力が落ちる")),
]))

# ================================================================ B
h.append(chapter("B", "夜　診療後までの片づけ＆掃除", d, "「合間」と「診療後」に分けて", "check", newpage=False))
h.append(grp("wait", "診療の合間に", d) + ck([
    "タオルの洗濯・乾燥（量が多い日）", "ワッテ缶のワッテとアルコールワッテの補充", "ゴミを集めて処分する",
    "印象用トレーをトレークリーナーから上げて洗浄", "寒天の補充", "ワッテ缶と受け皿の交換と滅菌"]))
h.append(grp("check", "診療後に", d) + ck([
    "パソコン・レントゲンの電源を消す", "空気清浄機・加湿器の電源を消す", "アルコールディスペンサーのスイッチ OFF", "寒天・ポットを待合室に置く",
    ("薬液交換", "超音波洗浄機、血液分解剤、フタラール（2〜3 日に 1 回）"), "ワッテ用のピンセットを回収して滅菌", "流しの掃除",
    "タービン・コントラ・ストレートにオイルをさす", "スピットン 3 点セットを洗浄して戻す",
    ("バイオエースでチェアーのバキュームを吸引", "スピットンにも流す（1 台につき 3 リットル）"), "器具を洗浄して滅菌", "翌日の技工物の確認と用意",
    ("チェアーのメインスイッチ・テーブル下のスイッチ・モニターを OFF", "水のバルブを閉める"), "コンプレッサーを OFF", "照射器を充電",
    ("NEW", ("接着材料を片づける", "出しっぱなしにしない。エステコアは使ったらすぐ冷蔵庫へ")),
]))
h.append(note("月 1 回の在庫チェックで、接着材料の **使用期限** を確認する。期限切れはチェアサイドから下げる。<span class=newflag>NEW</span>".replace("<span class=newflag>NEW</span>", "（新ルール）")))

# ================================================================ C
p_ = "patient"
h.append(chapter("C", "来院（受付）からユニット案内", p_, "声かけはハッキリ、笑顔で", "hand"))
h.append(steps([
    ("hand", "声をかけてチェアーへ案内する", None, "お待たせした時は必ず「大変お待たせいたしました」"),
    ("apply", "患者さんの **右側** から声をかけてエプロンをつける", None, "ビニールコーティングの面を内側に"),
    ("rinse", "リステリンを入れ、紙コップを置き、水を入れる"),
    ("layer", "バキューム・3WAY シリンジをセット"),
    ("check", "軽く問診し「少々お待ちください」と声をかけて待っていただく", None, "問診では反復・共感を行う"),
    ("book", "処置する場所のデンタルをモニターに出す", None, "なければパントモを出す"),
], p_))
h.append('<div class="grid3" style="margin-top:8px">' + "".join(f'<div class="card" style="text-align:center"><span class="talk">{t}</span><div class="muted" style="font-size:8pt;margin-top:3px">{s}</div></div>' for t, s in [
    ("○○さん、ご案内いたします", "案内のとき"), ("大変お待たせいたしました", "お待たせしたとき"), ("少々お待ちください", "問診のあと")]) + "</div>")

# ================================================================ D
b = "basic"
h.append(chapter("D", "歯式", b, "歯式用の黄緑色の紙に日付と残存歯を記入", "tooth", newpage=False))
h.append(tx(
    '<div class="grid2"><div class="card"><h5>乳歯</h5>アルファベット（A〜E）</div><div class="card"><h5>永久歯</h5>数字（1〜8）</div></div>'
    + '<div class="card" style="margin-top:6px"><b>真ん中の歯が 1 番、一番奥の親知らずが 8 番</b><br>1・2・3：前歯　4・5：小臼歯　6・7・8：大臼歯</div>'
    + warn("患者さんと向き合った歯の並びなので **左右が逆** になる。"),
    pic("shishiki", "記入例")))
h.append(sec("", "略語"))
ab = [("レジン充填", "CR"), ("メタルクラウン", "FMC"), ("インレー", "In"), ("アンレー", "On"), ("レジン前装冠", "HR"), ("虫歯", "C"),
      ("全部床義歯", "FD"), ("部分床義歯", "PD"), ("ブリッジ", "Br"), ("メタルボンド", "MB"), ("セラミックインレー", "CI"), ("オールセラミッククラウン", "ACC"),
      ("ハイブリッドインレー", "HI"), ("欠損", "×"), ("埋伏歯", "/////")]
h.append('<div class="abbr">' + "".join(f"<div><span>{a}</span><b>{b_}</b></div>" for a, b_ in ab) + "</div>")

# ================================================================ E
h.append(chapter("E", "器具について", b, "名前と使い道をセットで覚える", "prep"))
h.append(sec("E-1", "基本セット", b))
h.append(tx(ck(["探針", "3WAY シリンジのチップ", "エキスカベータ（エキスカ）", "ゴム充填器（充填器）", "ピンセット", "ミラー", "バキューム"], one=True),
            pic("kihon", "上から順に")))
h.append(sec("E-2", "ハンドピース（写真の左から）", b))
h.append(pic("handpiece"))
hp = [("#9aa6b2", "ストレート", "義歯調整・補綴物セット"), ("#e34948", "5 倍速（赤）", "金属の除去。タービンと同じバー"), ("#1baf7a", "低速コントラ（緑）", "根治。ニッケルチタンのバー"),
      ("#2a78d6", "コントラ（青）", "軟化象牙質の除去・PMTC"), ("#52606d", "タービン", "虫歯の除去"), ("#b87a00", "ピコ", "口が開かない人の虫歯除去。専用バー"), ("#4a3aa7", "エアースケーラー", "歯石の除去")]
h.append('<div class="hp">' + "".join(f'<div style="--hc:{c}"><b>{n}</b>{u}</div>' for c, n, u in hp) + "</div>")
h.append(sec("E-3", "バー", b))
h.append('<div class="grid2">' + pic("bur_turbine", "タービン用のセット") + pic("bur_short", "ショートバー（右）・ピコ用（中）") +
         pic("bur_round", "コントラ用ラウンドバー（軟化象牙質除去）。**錆びるため滅菌しない**") + pic("bur_rct", "根管治療用：根管形成バー（左）・ゲーツドリル（中）・ピーソーリーマー（右）") + "</div>")

# ================================================================ F
t = "treat"
h.append(chapter("F", "治療ごとの準備と流れ", t, "準備物をそろえ、流れを先読みしてアシスト", "crown"))
h.append(newbox("接着材料の統一に合わせ、**F-1 CR・F-5 ファイバーコア・F-7 コアセット・F-10 技工物の装着** を改訂しました。"))

h.append(sec("F-1", "CR（レジン充填）", t, "改訂"))
h.append(tx(prep(["タービン", "バー", "照射器", "咬合紙", "咬合紙ホルダー", "CR BOX：う蝕検知液", "!FineEtch37", "!Quick 2（ボンド）", "CR", "マイクロブラシ"]) + steps([
    ("apply", "麻酔の準備（必要な場合）", None, "表面麻酔、浸麻用シリンジとカートリッジ、針（35G）"),
    ("prep", "虫歯の除去", None, "マイクロブラシにう蝕検知液をつけて染め出す"),
    ("etch", "**エナメル質だけ** FineEtch37 → 水洗 → 乾燥", "15 秒"),
    ("apply", "**Quick 2** を 1 滴、マイクロブラシで擦り込み（待ち時間なし）"),
    ("air", "強圧エアブロー → 光照射", "LED 10 秒"),
    ("layer", "指定シェードの CR を渡す → 光照射"),
    ("polish", "咬合紙で高さを診て咬合調整 → 研磨"),
], t), pic("prep_cr", "CR の準備") + pic("prep_cr2", "")))
h.append('<div class="grid3">'
         '<div class="card"><h5>CR の種類</h5>フロー：直接流し入れる<br>ペースト：レジン充填器で充填</div>'
         '<div class="card"><h5>ストリップス（ディスポ）</h5>隣接面の充填時に。透明で光を通す。前歯に多い。3〜4cm 幅で</div>'
         '<div class="card" style="background:#fff6ee"><h5>裏層材 <span class="newflag">改訂</span></h5>大きい虫歯：<b>everX Flow</b><br>神経に近い：<b>TheraCal LC・ダイカル</b>（保険）／ <b>ミエール</b>（自費）</div></div>')

h.append(sec("F-2", "In imp（インレー印象）", t))
h.append(days([("1 日目", "インレー印象"), ("2 日目", "インレー装着")]))
h.append(prep(["タービン", "バー", "裏層材", "デュラシール", "CR の時とほぼ同じ"]) + steps([
    ("apply", "麻酔の準備（必要な場合）"), ("prep", "検知液でチェックしながらカリエス除去 → CR で削ったところを裏層"),
    ("fill", "In 形成後、本印象（寒天＋アルジネートの連合印象）・対合歯の印象・バイト採得"),
    ("shield", "デュラシールでしみないように仮封"), ("book", "技工指示書を書く", None, "セラミックインレーはシェード確認するのでシェードガイドを用意")], t))

h.append(sec("F-3", "RCT（根管治療）", t))
h.append(days([("1 日目", "麻酔抜髄 または 感染根管処置"), ("2 日目〜", "根管治療（回数は状態による）"), ("経過が良ければ", "根管充填 → コアへ")]))
h.append(tx(prep(["タービン", "コントラ", "低速コントラ", "バー", "RCT キャビネット（ファイル・メーター）", "NC シリンジ", "EDTA シリンジ"]) + steps([
    ("apply", "麻酔の準備（必要な場合）"),
    ("prep", "根管治療", None, "タービンで歯冠部形成 → コントラ＋ラウンドバーで軟化象牙質除去 → ゲーツドリルで根管上部 → 低速コントラ＋NiTi で根尖部 → メーターと手用ファイルで拡大・清掃"),
    ("rinse", "NC・EDTA シリンジで交互洗浄", None, "バキュームでこぼれないようしっかり吸引"),
    ("air", "根管内バキュームで乾燥"), ("apply", "貼薬：カルシペックスをトレーのふちに出す"),
    ("shield", "仮封：綿球 2 個＋キャビトン（充填器の平らな方に円錐状に盛る）", None, "2 回目以降はキャビトンをエアスケーラーで除去して 2〜6 をくり返す")], t), pic("prep_rct", "RCT の準備")))

h.append(sec("F-4", "RCF（根管充填）", t))
h.append(tx(prep(["タービン", "バー", "RCT キャビネット", "RCF セット（プラガー・スプレッダー・根充用ピンセット・メインポイント・ペーパーポイント・シーラー［冷蔵庫］）", "ソルフィー", "バーナー", "根管内バキューム", "NC・EDTA シリンジ"]) + steps([
    ("remove", "仮封をエアスケーラーで除去"), ("clean", "根管清掃 → 洗浄"), ("air", "根管内バキュームと指定号数のペーパーポイントで乾燥"),
    ("fill", "根充", None, "Dr 指示の長さ・号数のメインポイントを用意 → キャナルシーラーを練和 → 完了したらプラガーでカット（口角にバキュームで煙を吸う）"),
    ("shield", "綿球・キャビトンで仮封"), ("book", "デンタル撮影")], t) + note("乳歯はビタペックスを使用。"), pic("prep_rcf", "") + pic("prep_rcf2", "")))

h.append('<div class="nobreak">' + sec("F-5", "ファイバーコア（コア築造）", t, "改訂"))
h.append(newbox("ボンドが **ボンドマー ライトレス Ⅱ** に変わり、**ボンドの光照射は不要** になりました。コアレジンは **everX Flow**（ポストなし）／ **エステコア＋FR ポスト**（歯質が少ない時）。"))
h.append(tx(prep(["タービン", "コントラ", "バー", "ラウンドバー", "ピーソーリーマー", "!ライトレス Ⅱ（A 液・B 液）", "!混和皿", "!everX Flow", "!エステコア＋FR ポスト（冷蔵庫）", "照射器"]) + steps([
    ("prep", "コア形成"),
    ("mix", "ライトレス Ⅱ の A 液（黄）・B 液（青）を 1 滴ずつ混ぜる → **緑色** になったら渡す", None, "混ぜてから使える時間：ブルーラバー皿 3 分 ／ ディスポ皿 1 分"),
    ("air", "Dr が塗布したら **30 秒以内** にエアブロー（**照射しない**）"),
    ("fill", "everX Flow を渡す → 照射", "LED 20 秒"),
    ("post", "歯質が少ない時：エステコア → FR ポストを挿入 → 照射", "LED 10 秒以上"),
    ("prep", "タービンで形態修正"),
], t) + warn("ボンドを塗った後にポストを試適しない（くっついて外れなくなる）。"), pic("prep_core", "コアの準備")) + "</div>")

h.append(sec("F-6", "コア印象", t))
h.append(prep(["タービン", "コントラ", "バー", "ラウンドバー", "ピーソーリーマー", "綿球", "デュラシール"]) + steps([
    ("prep", "コア形成"), ("fill", "コア印象：寒天（細い先）＋アルジネート", None, "対合・バイトは Dr に採るか確認"),
    ("shield", "綿球・デュラシールで仮封"), ("book", "技工指示書を記入。印象はできるだけ早く石膏を流す")], t))

h.append(sec("F-7", "コア Set", t, "改訂"))
h.append(prep(["技工物", "!サンドブラスト", "!セラミック プライマー プラス", "!SA ルーティング Multi"]) + steps([
    ("remove", "仮封を除去 → コアを試適"), ("blast", "コア内面をサンドブラスト → セラミック プライマー プラスを塗布（メタルの場合）"),
    ("place", "SA ルーティング Multi で装着")], t) + note("旧版の「ユニセム・ルーティングなど」を、統一後のセメントに変更（要確認リスト参照）。"))

h.append(sec("F-8", "CK（クラウン）の形成・印象", t))
h.append(prep(["タービン", "バー", "印象"]) + steps([
    ("prep", "タービンで Cr の形成"), ("fill", "本印象（寒天＋アルジネートの連合印象）・対合歯・バイト採得"),
    ("shield", "仮封", None, "TEK がある時はテンポラリーセメントハードで仮着。なければデュラシール（プラストシール）"),
    ("book", "技工指示書を書く", None, "HR・CAD/CAM 冠・自費セラミックはシェードガイドを用意")], t))

h.append(sec("F-9", "シリコン印象（精密印象）", t))
h.append(tx(prep(["1 次印象材（パテ）", "2 次印象材（インジェクション）", "シリコンバイト", "シリコン用トレー", "ビニールシート"]) + steps([
    ("mix", "パテ（黄ベース＋青キャタリスト）を指先で練和 → トレーに盛り、ビニールシートをのせて Dr へ"),
    ("apply", "2 次印象材を Dr に渡し、その後トレーに盛る"), ("wait", "タイマーで 5 分", "5 分"),
    ("fill", "対合はアルジネートで印象"), ("check", "シリコンバイトを採得")], t) + note("シリコン印象は石膏を流さず、そのまま梱包する。"), pic("prep_silicone", "")))

h.append('<div class="nobreak">' + sec("F-10", "技工物の装着（SET）", t, "改訂"))
h.append(newbox("セメントは **補綴物の材質で決まります**。旧版の「メタル＝リライエックス（ピンク）／セラミック＝SA ルーティング（緑）」から下の表に変わりました。"))
h.append(tx(prep(["技工物", "咬合紙", "フロス", "セメント（下の表）", "ストレート", "バー"]) + steps([
    ("remove", "仮封を除去", None, "TEK はリムーバー、デュラシールはエキスカなどで"),
    ("check", "試適", None, "コンタクトに及ぶ時はフロス。咬合紙で高さを診る"),
    ("place", "下の表の材料を順番に渡す → 装着"),
    ("light", "照射して半分固め、余剰セメントを除去", "LED 2〜3 秒", "メタルは光を通さないのでマージンから 20 秒以上"),
    ("light", "本重合 → 辺縁確認", "LED 各面 20 秒"),
    ("wait", "30 分程度は食事を控えてもらう"),
], t), pic("prep_set", "SET の準備")) + "</div>")
S = lambda n: f'<img src="{IMG}/{n}.jpg" style="width:30px;height:40px;object-fit:cover;border-radius:4px;border:1px solid #e1e6ec;vertical-align:middle;margin-right:3px">'
h.append(table(["補綴物", "① 補綴物の内面", "② 歯の面", "③ セメント"], [
    ["<b>メタル（保険）</b>", S("cpp") + "ブラスト → CPP", "なし", S("samulti") + "<b>SA ルーティング Multi</b>（緑）"],
    ["<b>CAD/CAM 冠</b>", S("cpp") + "弱圧ブラスト → CPP", "なし", S("samulti") + "<b>SA ルーティング Multi</b>（緑）"],
    ["<b>ジルコニア</b>", S("katanacleaner") + "ブラスト → カタナクリーナー → SBU Plus", S("sbuplus") + "SBU Plus", S("relyxu") + "<b>RelyX Universal</b>"],
    ["<b>e.max</b>", S("monobond") + "Monobond E&P", S("sbuplus") + "FineEtch37 → SBU Plus", S("relyxu") + "<b>RelyX Universal</b>"],
    ["<b>e.max ベニア</b>", S("monobond") + "Monobond E&P", S("beautibondx") + "FineEtch37 → BB Xtreme", S("beauticem") + "<b>BeautiCem Veneer</b>"],
    ['<span class="muted">在庫がある間のみ</span>', "─", "─", S("relyxlp") + '<span class="muted">RelyX Luting Plus（ピンク）・ビューティリンク SA</span>'],
], ["16%", "30%", "24%", "30%"]))
h.append(note("CPP＝セラミック プライマー プラス　SBU Plus＝Scotchbond Universal Plus　BB Xtreme＝ビューティボンド Xtreme。詳しい手順は『治療別 接着プロトコル集』3 章。"))

h.append(sec("F-11", "義歯の作成", t))
h.append(days([("1 日目", "個人トレー印象"), ("2 日目", "個人トレーで本印象"), ("3 日目", "BT（咬合採得）"), ("4 日目", "TF（試適）"), ("5 日目", "SET（装着）")]))
h.append(note("部分入れ歯は、個人トレー印象・BT・TF を飛ばす場合もある。"))
h.append('<div class="grid2">' + "".join(f'<div class="card"><h5>{a}</h5>{md(b_)}</div>' for a, b_ in [
    ("① 個人トレー印象", "石膏を流す時はオーバー目に厚く盛る。技工指示書を記入"),
    ("② 個人トレーで本印象", "個人トレーにアドヒーシブ（印象材との接着剤）を塗布 → アルジネートで印象。石膏は前回同様に盛る。技工指示書"),
    ("③ BT", "技工物・咬合平面板・ワックススパチュラ・エバンス・コテ・パラフィンワックス・バーナー。技工指示書"),
    ("④ TF ／ ⑤ SET", "技工物・咬合紙・ストレート・バー（SET で部分入れ歯ならヤングのプライヤー）。TF は技工指示書")]) + "</div>")

h.append(sec("F-12", "抜歯・消毒・抜糸", t))
h.append(tx(prep(["表麻", "浸麻", "抜歯部位の鉗子", "ヘーベル", "鋭匙（必要時）", "持針器", "セーレ", "縫合糸", "テルプラグ", "外科用バキューム", "ガーゼ"]) + steps([
    ("apply", "表麻・浸麻"), ("prep", "ヘーベルで脱臼 → 抜歯鉗子で抜く", None, "外科用バキュームで血を吸う"),
    ("clean", "根尖病巣がある時は鋭匙で抜歯窩をきれいにする"), ("remove", "持針器と縫合糸で縫合し、セーレで切る")], t)
    + '<div class="grid2" style="margin-top:6px"><div class="card"><h5>SP（消毒）</h5>消毒用の基本セット。抜歯後数日中</div><div class="card"><h5>抜糸</h5>基本セット＋セーレ。抜歯後 1 週間</div></div>',
    pic("prep_ext", "抜歯の準備")))

# ================================================================ G
h.append(chapter("G", "治療ごとの後片付け", d, "安全第一：鋭利なものから片づける", "clean"))
h.append(ck([
    ("注射器・縫合針・メスなどは慎重に専用ボックスへ", "最初に片づける"),
    "ハンドピースのバーを外してシャーレへ → 超音波消毒槽", "ファイルなどの小器具をシャーレへ",
    ("3WAY シリンジ・ハンドピース類を外す", "タービンは水を数秒出してから外す。3WAY シリンジは小さいフタラールの容器へ"),
    "古いコップにワッテ・咬合紙・エプロンなどを入れてゴミ箱へ", "バキュームでコップの水を吸ってチップを外す",
    "使ったコップをゴミ入れ用のカップホルダーに置く", ("使用済みの基本セット・器具を消毒室の流しへ", "小器具はザル、基本セットは血液分解剤につける"),
    ("スプレーをクロスに吹きかけて拭く", "テーブル → コード類 → ライト → ユニット → 肘置き → スピットン → 隙間 の順"),
    "新しい基本セット・3WAY シリンジ・エプロンを用意", "除去した金属は専用のリサイクル BOX へ"], one=True))

# ================================================================ H
h.append(chapter("H", "感染症の患者さんの準備と片づけ", d, "触る場所はすべてカバー", "shield", newpage=False))
h.append('<div class="grid2"><div>' + grp("shield", "準備", d) + ck([
    ("Dr・アシストが触る場所はすべてラップ", "ホースにはスリーブ、ユニットにはゴミ袋、キャビネットにはエプロン"),
    "感染症用の基本セットと処置のセットを準備", "ワッテ缶は下げて、必要な分をトレーに出す"], one=True)
    + '</div><div>' + grp("clean", "片づけ", d) + ck([
    ("使った器具はデントハイドに漬け、翌日水洗いしてから滅菌", "滅菌パックの紙の部分に Ⓗ と書く"),
    ("使い捨ての物はゴミ袋にまとめる", "トレー・ワッテ・エプロン・コップなど → 感染用の白いプラスチックのゴミ箱")], one=True) + "</div></div>")

# ================================================================ I, J
h.append(chapter("I", "レントゲン", b, "3 種類の違い", "book"))
h.append('<div class="grid3">' + "".join(f'<div class="card" style="border-top:4px solid #2a78d6"><h5>{a}</h5>{md(c)}</div>' for a, c in [
    ("パノラマ（パントモ）", "口の中 **全体** のレントゲン。**初診の人は撮る**"), ("デンタル", "**部分的** なレントゲン。ホルダーを使って撮る"), ("CT", "**3 次元的** なレントゲン")]) + "</div>")
h.append(chapter("J", "歯の構造", b, "", "tooth", newpage=False))
h.append(f'<div style="display:grid;grid-template-columns:260px 1fr;gap:14px;align-items:center">{pic("tooth")}<div>'
         + table(["部位", "ポイント"], [["エナメル質", "歯の一番外側。いちばん硬い"], ["象牙質", "エナメル質の内側"], ["歯髄（血管・神経）", "いわゆる「神経」"],
                                      ["歯肉・歯槽骨・歯根膜", "歯を支える組織"], ["セメント質・根尖孔", "根の表面／根の先の穴"]], ["40%", "60%"]) + "</div></div>")
h.append(note("「ポイント」欄は図の用語の補足として追記したものです。"))

# ================================================================ K
f = "flow"
h.append(chapter("K", "虫歯の進行と治療の流れ", f, "C1 → C4 で治療が変わる", "layer"))
h.append(pic("caries", "", "110px").replace('class="pic"', 'class="pic" style="height:110px;object-fit:contain;border:0"'))
h.append('<div class="grid2">'
         '<div class="card" style="border-left:4px solid #c2477a"><h5>C1：エナメル質内まで</h5>TBI（ブラッシング指導）または CR</div>'
         f'<div class="card" style="border-left:4px solid #c2477a"><h5>C2：象牙質まで</h5>CR　または　In imp → In セット<div style="display:flex;gap:4px;margin-top:4px">{"".join(f"<img src={A}/{n}.jpg style=width:32%;border-radius:6px>" for n in ("c_cr", "c_inimp", "c_inset"))}</div></div></div>')
h.append(sec("", "C3：歯髄まで進行（根の治療 → 土台 → かぶせ物）", f))
fcw = lambda s: f'<div class="b">{s}</div>'
arr = '<div class="ar">▼</div>'
h.append('<div style="display:grid;grid-template-columns:1fr 1fr 190px;gap:12px;align-items:start">'
         '<div class="fc" style="--c:#c2477a">' + fcw("<b>生活歯</b><br>麻酔抜髄（麻抜）") + arr + fcw("根管治療（根治・RCT）<small>数回続くこともある</small>") + arr + fcw("根管充填（根充・RCF）") + "</div>"
         '<div class="fc" style="--c:#c2477a">' + fcw("<b>失活歯</b><br>感染根管処置（感処）") + arr + fcw("コア imp → コアセット<small>歯質が残っていればファイバーコア</small>") + arr + fcw("CK imp（FMC・HR など）") + arr + fcw("CK セット") + "</div>"
         + pic("crown_core", "クラウンと土台（コア）") + "</div>")
h.append(sec("", "CK（かぶせ物）の種類", f))
h.append(f'<div style="display:grid;grid-template-columns:1fr 200px;gap:12px;align-items:start"><div>'
         + table(["", "種類", "主な部位"], [
             [chip("保険", "ok"), "前装冠（HR）", "前歯部"],
             [chip("保険", "ok"), "CAD/CAM 冠 <span class='newflag'>要確認</span>", "小臼歯（現在は前歯・大臼歯も条件付きで保険適用）"],
             [chip("保険", "ok"), "FMC（メタルクラウン）", "大臼歯"],
             [chip("自費", "warn"), "オールセラミッククラウン（AC）・e.max", "─"],
             [chip("自費", "warn"), "ジルコニアクラウン（Zr）", "─"],
             [chip("自費", "warn"), "メタルボンド（MB）・ゴールドクラウン", "─"]], ["12%", "44%", "44%"]) + "</div>" + pic("crown_types") + "</div>")

h.append('<div class="nobreak">' + sec("", "C4：残根状態まで進行", f))
h.append('<div class="fc" style="--c:#c2477a;max-width:120mm;margin:0 auto 6px">' + fcw("<b>抜歯（Ext）</b>") + '<div class="ar">▼ <small>翌日</small></div>' + fcw("SP（消毒）")
         + '<div class="ar">▼ <small>1 週間後</small></div>' + fcw("抜糸") + '<div class="ar">▼ <small>約 1 か月後、次の 3 つから選ぶ</small></div></div>')
h.append('<div class="grid3">' + "".join(f'<div class="card" style="border-top:4px solid #c2477a"><h5>{a}</h5>{md(c)}</div>' for a, c in [
    ("① ブリッジ（Br）", "Br imp ＋ Br TEK セット → Br セット"),
    ("② 部分入れ歯（PD）", "（個人トレー imp）→ PD imp → PD BT → PD TF（試適）→ PD セット → 義歯調整（義調）"),
    ("③ インプラント", "抜歯後 3〜6 か月 → 1 次オペ → 約 3 か月後 2 次オペ → 2 週間後 インプラント印象 → 補綴セット")]) + "</div>")
h.append("</div>")
h.append(pic("missing", "インプラント・入れ歯・ブリッジの比較"))

# ================================================================ L
h.append(chapter("L", "歯周病の進行と治療の流れ", f, "基本は衛生士さんが検査と治療を行う", "tooth"))
h.append(pic("perio", "歯周病の進行（P1〜P4）"))
side = lambda s, go=True: f'<div class="side">{fcw(s)}{"<span class=go>問題なければ → リコールへ</span>" if go else "<span style=width:150px></span>"}</div>'
h.append('<div class="fc" style="--c:#c2477a;max-width:150mm;margin:8px auto">'
         + side("歯周基本検査 1 回目（P 検①）", False) + arr
         + side("スケーリング（SC）<small>歯肉縁上歯石の除去</small>", False) + '<div class="ar">▼ <small>1 週後</small></div>'
         + side("歯周基本検査 2 回目（P 検②）") + arr
         + side("スケーリング＆ルートプレーニング（SRP）<small>最大 6 回に分けて</small>", False) + '<div class="ar">▼ <small>2 週後</small></div>'
         + side("歯周基本検査 3 回目（P 検③）") + arr
         + side("再 SRP<small>最大 6 回に分けて</small>", False) + '<div class="ar">▼ <small>2 週後</small></div>'
         + side("歯周精密検査 4 回目（P 検④）") + arr
         + side("フラップ手術（Fop）<small>歯周外科</small>", False) + '<div class="ar">▼ <small>2 週後</small></div>'
         + side("歯周基本検査 5 回目（P 検⑤）", False) + arr
         + '<div class="b" style="background:#e9f7ee;border-color:#23803d"><b style="color:#23803d">リコール（定期健診）</b></div></div>')
h.append('<div class="card"><h5>' + icon("check", 16) + ' P 検査の準備</h5>ポケット測定を行うので <b>プローブ</b> を用意。値は <b>iPad</b> に入力</div>')

# ================================================================ CHANGE LOG
h.append(chapter("★", "改訂箇所一覧と確認のお願い", None, "旧版（5 年以上前）からの変更点", "book", color="#d9480f"))
h.append(sec("", "今回変更したところ"))
h.append(table(["項目", "旧版", "改訂版"], [
    ["F-1 CR", '<span class="old">ボンディングを塗る → エアー → 光照射</span>', '<span class="new">FineEtch37（エナメル質のみ）→ Quick 2 → 強圧エア 5 秒 → LED 10 秒</span>'],
    ["F-1 裏層材", '<span class="old">アイオノジット・セラカル等</span>', '<span class="new">everX Flow（大窩洞）／ TheraCal LC・ダイカル・ミエール（神経に近い）</span>'],
    ["F-5 ファイバーコア", '<span class="old">ボンド塗布 → エアー → 照射 → コアレジン＋ファイバーポスト</span>', '<span class="new">ライトレス Ⅱ（混和して緑・照射不要・30 秒以内にエア）→ everX Flow ／ エステコア＋FR ポスト</span>'],
    ["F-7 コア Set", '<span class="old">ユニセム・ルーティングなどで合着</span>', '<span class="new">ブラスト → セラミック プライマー プラス → SA ルーティング Multi</span>'],
    ["F-10 SET", '<span class="old">メタル＝リライエックス（ピンク）／セラミック＝SA ルーティング（緑）</span>', '<span class="new">材質別の表（メタル・CAD/CAM＝SA Multi、ジルコニア・e.max＝RelyX Universal、ベニア＝BeautiCem Veneer）</span>'],
    ["F-10 余剰除去", '<span class="old">固まる前にスパチュラなどでふく</span>', '<span class="new">2〜3 秒照射で半分固めてから除去</span>'],
    ["A 朝の準備", "─", '<span class="new">冷蔵の接着材料を室温に出す</span>'],
    ["B 夜の片づけ", "─", '<span class="new">接着材料を片づける（エステコアはすぐ冷蔵庫）／月 1 回の使用期限チェック</span>'],
    ["医院理念", '<span class="old">患者さんが歯で一生困ることがないようにお手伝いする</span>', '<span class="new">クリニックにかかわるすべての人の自己実現をかなえるサポートをし、幸せと笑顔を届ける</span>'],
    ["全体", "文章中心・行間不揃い", "チェックリスト・手順アイコン・写真を内容の横に配置"],
], ["17%", "38%", "45%"], "chg"))
h.append(sec("", "医院で確認してほしいところ（今回の資料からは判断できない記載）"))
h.append(ck([
    ("医院理念のページの「行動目標」", "理念は新しくしたが、行動目標（リコールの大切さを伝える）は旧版のまま。新しい理念に合わせて変えるか"),
    ("K の CAD/CAM 冠の保険適用部位", "旧版は「小臼歯」。現在は前歯・大臼歯にも条件付きで拡大しているため、医院の運用に合わせて確認"),
    ("F-7 コア Set のセメント", "旧版の「ユニセム」は RelyX Unicem の可能性。統一方針に合わせ SA ルーティング Multi にしたが、ファイバーコア・メタルコアで運用が違わないか"),
    ("F-10 のセメントの色", "SA ルーティング Multi（緑）・RelyX Luting Plus（ピンク）の表記は旧版から。RelyX Universal・BeautiCem Veneer の見分け方を追記するか"),
    ("印象・薬液・消毒剤など材料以外の記載", "寒天＋アルジネートの連合印象、フタラール（2〜3 日に 1 回）、バイオエース、デントハイド、針 35G、iPad 入力などが今も同じか"),
    ("C4 のインプラントの期間・F-11 義歯の日数", "旧版どおり。現在の診療の流れと合っているか"),
], one=True))

html_out = doc("アシスタントマニュアル", "\n".join(h)).replace("</style>", EXTRA_CSS + "</style>")
p = os.path.join(HERE, "assistant.html")
open(p, "w").write(html_out)
render(p, os.path.join(HERE, "assistant.pdf"))
