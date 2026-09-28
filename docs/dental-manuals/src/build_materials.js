const L = require("./lib");
const { d, C, CONTENT, P, chapter, caution, note, table, flow, titleBlock, img, gridBorders } = L;
const { Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, VerticalAlign, AlignmentType, TableLayoutType } = d;

const W = CONTENT;
// material card table: 写真 | 材料・用途 | 使い方 | 注意
const CW = [1250, 2350, 3200, W - 6800];

function photoCell(names) {
  const kids = names && names.length
    ? [new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0 },
        children: names.map((n) => img(n, names.length > 1 ? 34 : 58)) })]
    : [new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0 },
        children: [new TextRun({ text: "写真なし", size: 14, color: "A6A6A6" })] })];
  return new TableCell({ width: { size: CW[0], type: WidthType.DXA }, children: kids, borders: gridBorders,
    shading: { type: ShadingType.CLEAR, fill: "F4F6F8", color: "auto" }, verticalAlign: VerticalAlign.CENTER,
    margins: { top: 40, bottom: 40, left: 40, right: 40 } });
}
function txt(s, w, o = {}) {
  const lines = Array.isArray(s) ? s : [s];
  return new TableCell({ width: { size: w, type: WidthType.DXA }, borders: gridBorders, verticalAlign: VerticalAlign.CENTER,
    shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: lines.map((t, i) => new Paragraph({ spacing: { after: i < lines.length - 1 ? 30 : 0, line: 264, lineRule: "auto" },
      children: L.rich(t, { size: i === 0 ? o.size0 || 18 : 16, color: i === 0 ? o.color0 : C.gray, bold: i === 0 ? o.bold0 : undefined }) })) });
}
// items: { photo:[..], name, use, how, note, stock }
function cards(items) {
  const head = new TableRow({ tableHeader: true, children: ["写真", "材料 ／ 用途", "使い方", "注意"].map((h, i) =>
    L.cell(h, CW[i], { fill: C.navy, color: "FFFFFF", bold: true, align: AlignmentType.CENTER })) });
  const rows = items.map((m) => new TableRow({ cantSplit: true, children: [
    photoCell(m.photo),
    txt([m.name, m.use], CW[1], { bold0: true, color0: m.stock ? C.mute : C.navy, size0: 19 }),
    txt(m.how, CW[2]),
    txt(m.note, CW[3], { fill: m.warn ? C.amberBg : undefined }),
  ] }));
  return [new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: CW, layout: TableLayoutType.FIXED, rows: [head, ...rows] }),
    new Paragraph({ spacing: { after: 80 }, children: [] })];
}
const lead = (s) => P(s, { run: { color: C.gray, size: 18 }, para: { spacing: { after: 100 } } });

const keep = (t) => ({ t, fill: C.greenBg });
const drop = (t) => ({ t, fill: t === "─" ? undefined : C.redBg, color: t === "─" ? C.mute : C.red, align: t === "─" ? AlignmentType.CENTER : undefined });

const body = [
  ...titleBlock("材料別　使用用途一覧", "博多ステラ歯科・矯正歯科クリニック　院内マニュアル　｜　操作手順の詳細は『治療別 接着プロトコル集』を参照"),
  P("**この資料の使い方**", { run: { color: C.navy, size: 21 } }),
  ...flow([
    ["① 1 章で方針を確認", "残す材料 / なくす材料"],
    ["② 治療の章で材料を探す", "写真で実物と照合"],
    ["③ 8 章で NG を確認", "使ってはいけない組み合わせ"],
  ]),

  // 1
  chapter("1", "材料の統一方針"),
  lead("役割ごとに使う材料を 1 つに絞る。右列の材料は在庫がなくなり次第、発注しない。"),
  table(["役割", "残す（発注する）", "なくす（在庫消化後は発注しない）"], [
    ["ボンディング材", keep("ユニバーサルボンド Quick 2（保険）\nScotchbond Universal Plus（自費）"), drop("メガボンド 2（ダイレクト）")],
    ["支台築造", keep("ボンドマー ライトレス Ⅱ ＋ everX Flow\nトクヤマ FR ポスト ＋ エステコア（フェルールなし）"), drop("─")],
    ["エッチング", keep("FineEtch37"), drop("─")],
    ["表面硬化（酸素阻害層）", keep("オキシガード Ⅱ（脱離が心配な症例のみ）"), drop("─")],
    ["ホワイトスポット", keep("G-ボンド ユニバーサル・アイコン"), drop("─")],
    ["CR・セラミックのリペア", keep("ポーセレンボンド アクティベーター（Quick 2 と混和）"), drop("─")],
    ["補綴物の洗浄", keep("カタナクリーナー"), drop("─")],
    ["ジルコニア・メタル内面", keep("セラミック プライマー プラス"), drop("─")],
    ["e.max 内面", keep("Monobond Etch & Prime"), drop("─")],
    ["日常のセメント（CAD/CAM・メタル）", keep("SA ルーティング Multi"), drop("ビューティリンク SA\nRelyX Luting Plus")],
    ["ジルコニア・e.max の装着", keep("Scotchbond Universal Plus ＋ RelyX Universal"), drop("─")],
    ["ベニア専用", keep("BeautiCem Veneer ＋ ビューティボンド Xtreme"), drop("─")],
    ["特殊症例の切り札", keep("スーパーボンド"), drop("─")],
  ].map((r) => r.map((c) => (typeof c === "object" && c.t.includes("\n")) ? { ...c, t: c.t.split("\n").map((x) => new Paragraph({ spacing: { after: 0 }, children: L.rich(x, { size: 18, color: c.color }) })) } : c)),
  [2600, 4200, W - 6800], { zebra: false }),

  // 2
  chapter("2", "CR 充填", true),
  cards_([
    { photo: ["quick2"], name: "ユニバーサルボンド Quick 2", use: "主力（全症例）", how: "擦り込み → 強圧エア 5 秒 → LED 10 秒", note: ["待ち時間なし", "エナメル質が多い症例は FineEtch37 を併用"] },
    { photo: ["sbuplus"], name: "Scotchbond Universal Plus", use: "第二選択・IDS", how: "20 秒擦り込み → エア 5 秒 → LED 10 秒", note: ["RelyX Universal と純正ペア", "補綴の前処理と共用できる"] },
    { photo: ["fineetch37"], name: "FineEtch37", use: "選択エッチング", how: "エナメル質のみ 15 秒 → 水洗 20 秒", note: "象牙質に長く置かない", warn: true },
    { photo: ["megabond2"], name: "メガボンド 2", use: "ダイレクト（在庫消化後は発注しない）", stock: true, how: "プライマー 20 秒 → エア → ボンド → 弱エア → LED 10 秒", note: "象牙質接着の長期成績が最も高い。深いう蝕など質を優先する症例に" },
    { photo: [], name: "everX Flow", use: "大窩洞・咬合圧が高い症例の裏層", how: "窩洞底から 2mm 程度 → 照射 → 表層は通常 CR", note: ["最表層に出さない", "短繊維強化フロアブル"], warn: true },
    { photo: [], name: "TheraCal LC", use: "露髄・髄床底が近い症例の覆髄", how: "1mm 以下で塗布 → LED 20 秒", note: "厚く塗ると硬化不良。範囲は最小限に", warn: true },
    { photo: ["gbond"], name: "G-ボンド ユニバーサル", use: "ホワイトスポットの白濁改善", how: "平皿に採取 → 白濁部に浸潤 → LED 5 秒", note: ["エアブロー不要。深皿は使わない（操作時間 7 分）", "止血剤を使うと接着力が戻らない"], warn: true },
    { photo: ["beautibondx"], name: "ビューティボンド Xtreme", use: "ベニア装着時（必須）", how: "塗布 → 弱エア 3 秒 → 強エア → LED 5 秒", note: ["BeautiCem Veneer の添付文書で指定", "CR 充填にも使える"] },
    { photo: ["activator"], name: "ポーセレンボンド アクティベーター", use: "既存 CR・セラミックのリペア", how: ["Quick 2 と 1 滴ずつ混和 → 塗布 → エア 5 秒以上 → LED 10 秒", "塗布時間：CR のみ 5 秒 ／ 歯質を含む 20 秒"], note: ["作り置きしない", "混ぜるとすぐ使える（待ち時間なし）"], warn: true },
  ]),

  // 3
  chapter("3", "支台築造（コア）"),
  cards_([
    { photo: ["lightless2"], name: "ボンドマー ライトレス Ⅱ", use: "主力（全症例の前処理）", how: ["A 液（黄）・B 液（青）各 1 滴 → 緑色を確認 → 塗布 → 30 秒以内にエア", "光照射は不要"], note: ["塗布後にポストを試適しない", "処理済みのポストと補綴物を触れさせない"], warn: true },
    { photo: [], name: "everX Flow", use: "主力（コア築造）", how: "根管口から 2〜3mm → 照射 → 歯冠部は 4mm 以下ずつ積層", note: ["光重合のみ。根管の奥に入れない", "硬化深度 5.5mm（バルクシェード）"], warn: true },
    { photo: [], name: "トクヤマ FR ポスト", use: "フェルールが確保できない症例のみ", how: "試適 → ライトレス Ⅱ で前処理 → 乾燥 → 挿入後 10 秒以上照射", note: "当院在庫は 1.4mm" },
    { photo: [], name: "混和皿", use: "ライトレス Ⅱ の混和", how: "操作可能時間　ブルーラバー：3 分 ／ ディスポ：1 分", note: "ブルーラバーはアルコール清掃で再使用。オートクレーブ不可" },
  ]),

  // 4
  chapter("4", "ジルコニア補綴のセット"),
  lead("流れ：ブラスト → カタナクリーナー → Scotchbond Universal Plus → RelyX Universal"),
  cards_([
    { photo: [], name: "サンドブラスト", use: "内面の粗造化", how: ["アルミナ 50µm ／ 0.1MPa ／ 10mm ／ 10 秒", "高透光性（4Y・5Y）は 0.05〜0.1MPa"], note: "内面の光沢が消えるまで" },
    { photo: ["katanacleaner"], name: "カタナクリーナー", use: "試適後の唾液汚染除去", how: "内面に 10 秒 → 水洗 → 乾燥", note: "リン酸は使わない（MDP の結合を阻害する）", warn: true },
    { photo: ["sbuplus"], name: "Scotchbond Universal Plus", use: "内面処理・支台歯前処理", how: ["内面：塗布 → エア 5 秒", "支台歯：20 秒擦り込み → エア 5 秒"], note: ["MDP・シラン入りでジルコニアに直接使える", "RelyX Universal 併用時は照射不要"] },
    { photo: ["relyxu"], name: "RelyX Universal", use: "ジルコニアの装着", how: "内面に塗布 → 装着 → タックキュア → 余剰除去 → 本重合", note: "ジルコニアはこの組み合わせに統一" },
  ]),

  // 5
  chapter("5", "e.max・ガラスセラミック補綴のセット"),
  cards_([
    { photo: ["monobond"], name: "Monobond Etch & Prime", use: "内面処理（エッチング＋シラン）", how: "20 秒すり込む → 40 秒置く → 水洗 → 乾燥", note: ["フッ化水素酸が不要", "ジルコニアには使えない"], warn: true },
    { photo: ["beauticem"], name: "BeautiCem Veneer", use: "ベニア（厚さ 2.0mm 未満）", how: ["光重合専用", "2〜3 秒照射で半硬化 → 余剰除去 → 本重合 LED 10 秒"], note: ["光を通す修復物のみ（ジルコニア ✕）", "ユージノール系と併用不可"], warn: true },
    { photo: ["relyxu"], name: "RelyX Universal", use: "クラウン・インレー・アンレー", how: ["デュアルキュア", "支台歯は Scotchbond Universal Plus"], note: "光が届きにくい部位でも確実に硬化" },
  ]),

  // 6
  chapter("6", "CAD/CAM 冠のセット（保険）", true),
  lead("流れ：ブラスト（弱圧）→ セラミック プライマー プラス → SA ルーティング Multi"),
  cards_([
    { photo: [], name: "サンドブラスト", use: "内面の粗造化", how: "アルミナ 50µm ／ 弱圧 0.1〜0.2MPa", note: "ブラストできない時はリン酸で確実に清掃" },
    { photo: ["cpp"], name: "セラミック プライマー プラス", use: "内面のシラン処理", how: "ブラスト・乾燥後に塗布 → エア", note: "必須工程。SA セメント単独では付かない", warn: true },
    { photo: ["samulti"], name: "SA ルーティング Multi", use: "CAD/CAM 冠の装着", how: "内面処理後に装着 → タックキュア → 余剰除去", note: "保険で使える。接着性レジンセメントは診療指針で必須" },
    { photo: ["relyxu"], name: "RelyX Universal", use: "脱離既往・保持形態が弱い症例", how: ["デュアルキュア", "支台歯は Scotchbond Universal Plus"], note: "エンドクラウンはデュアルキュア型が推奨" },
  ]),
  caution("CAD/CAM 冠に **RelyX Luting Plus は使えない**。"),

  // 7
  chapter("7", "メタル補綴のセット"),
  cards_([
    { photo: ["cpp", "samulti"], name: "セラミック プライマー プラス ＋ SA ルーティング Multi", use: "保険 FMC・ブリッジ・インレー", how: ["ブラスト（0.3〜0.5MPa）→ プライマー → 装着"], note: "統一後の標準手順。接着で脱離を減らす" },
    { photo: ["relyxlp"], name: "RelyX Luting Plus", use: "在庫消化まで", stock: true, how: "練和 → 装着", note: "接着ではなく合着。なくなり次第、上の手順へ統一" },
    { photo: ["beautilink"], name: "ビューティリンク SA", use: "在庫消化まで", stock: true, how: "ブラスト → プライマー → 装着", note: "なくなり次第、SA ルーティング Multi へ統一" },
  ]),

  // 8
  chapter("8", "使ってはいけない組み合わせ", true),
  table(["", "組み合わせ", "理由", "代わりに"], [
    ...[
      ["ジルコニア × BeautiCem Veneer", "光重合専用。添付文書は「光を通す修復物のみ」", "RelyX Universal"],
      ["BeautiCem Veneer × ユージノール系材料", "硬化・接着を阻害（添付文書）", "ユージノールを含まない仮着材"],
      ["ジルコニア × Monobond Etch & Prime", "ガラス相がなくエッチングが効かない", "Scotchbond Universal Plus"],
      ["ジルコニア × フッ化水素酸", "同上。表面が変わらず無効", "ブラスト ＋ Scotchbond Universal Plus"],
      ["ジルコニアの洗浄 × リン酸（FineEtch37）", "リン酸が吸着し MDP の結合を阻害", "カタナクリーナー"],
      ["e.max × SA セメント単独", "シラン処理がなく接着が大きく落ちる。薄いものは破折リスク", "Monobond E&P ＋ RelyX Universal"],
      ["e.max × RelyX Luting Plus", "合着では e.max の強度を保てない", "RelyX Universal"],
      ["CAD/CAM 冠 × RelyX Luting Plus", "接着性レジンセメントが診療指針で必須", "SA ルーティング Multi"],
      ["CAD/CAM 冠 × シラン処理なし", "必須工程。省くと脱離の主因", "セラミック プライマー プラス"],
      ["メーカーを跨いだボンド＋セメント", "添付文書外。脱離・破折時の説明で不利", "純正の組み合わせ"],
    ].map(([a, b, c]) => [{ t: "✕", color: C.red, bold: true, align: AlignmentType.CENTER, fill: C.redBg }, `**${a}**`, b, { t: c, color: C.green }]),
  ], [500, 3300, 3600, W - 7400]),

  // 9
  chapter("9", "保管・取扱いの共通ルール"),
  table(["項目", "内容"], [
    [{ t: "**冷蔵**", fill: "E3F2FD" }, ["セラミック プライマー プラス（2〜8℃）／ エステコア（0〜10℃）／ オキシガード Ⅱ ／ スーパーボンド ／ ポーセレンボンド アクティベーター", "使用直前に室温へ戻す（結露すると接着力が落ちる）"]],
    [{ t: "**室温・暗所**", fill: "FFF8E1" }, "ビューティセム ベニア（1〜30℃、添付文書）"],
    [{ t: "**常温**", fill: "FFF8E1" }, "RelyX Universal ／ G-ボンド ユニバーサル ／ TheraCal LC"],
    [{ t: "**冷蔵・常温どちらも可**", fill: C.greenBg }, "カタナクリーナー ／ Scotchbond Universal Plus ／ SA ルーティング Multi ／ Quick 2 ／ everX Flow ／ Monobond Etch & Prime ／ ボンドマー ライトレス Ⅱ"],
    ["**ボトルから出したら**", "溶媒が揮発して濃度が変わるため **5 分以内** に使い切る"],
    ["**チェアサイド**", "出しっぱなしにしない。エステコアは使用後すぐ冷蔵庫へ"],
    ["**使用期限**", "月 1 回の在庫チェックで全材料を確認。期限切れはすぐチェアサイドから下げる"],
  ].map(([a, b]) => [a, Array.isArray(b) ? b.map((x, i) => new Paragraph({ spacing: { after: 0 }, children: L.rich(x, { size: i ? 16 : 18, color: i ? C.gray : undefined }) })) : b]),
  [2400, W - 2400], { zebra: false }),
  note("写真は院内の実物です。材料を入れ替えたときは写真と表を更新してください。"),
];

function cards_(items) { return cards(items); }
// flatten nested arrays from cards_()
L.save(L.makeDoc("材料別 使用用途一覧", body.flat()), process.argv[2] || "材料別使用用途一覧_改訂版.docx");
