"""博多ステラ歯科 月次レポート（Excel）生成スクリプト

使い方:
    python monthly-report-excel/build_monthly_report.py

出力:
    monthly-report-excel/博多ステラ歯科_月次レポート.xlsx

シート構成:
    2026年10月 … 当月レポート（青字＝入力値、黒字＝数式）
    推移       … 各月シートの主要KPIを INDIRECT で一覧化（シート名を足すだけ）
    テンプレート … 入力欄が空の月次シート。コピーして翌月に使う
    使い方     … 運用手順・計算式・凡例

月次シートはどの月でもセル番地が同じなので、推移シートから同じ番地で参照できる。
"""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.series import DataPoint
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.page import PageMargins

OUT = Path(__file__).with_name("博多ステラ歯科_月次レポート.xlsx")

# ---------------------------------------------------------------- デザイン（ゴールド基調）
FONT = "游ゴシック"
GOLD_DARK = "7A5C12"   # タイトル帯
GOLD = "B8902F"        # セクション見出し
GOLD_LIGHT = "EAD9A8"  # 表ヘッダー
CREAM = "FBF6E9"       # 入力セル背景
IVORY = "FFFDF7"       # 計算セル背景（強調）
LINE = "D6C08A"        # 罫線
TEXT = "3A2E0B"        # 本文
BLUE = "0000FF"        # 入力値

thin = Side(style="thin", color=LINE)
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)

YEN = '"¥"#,##0;-"¥"#,##0;"-"'
NUM = '#,##0;-#,##0;"-"'
PCT = '0.0%;-0.0%;"-"'
PT = '+0.0"pt";-0.0"pt";"±0.0pt"'
DIFF = '+#,##0;-#,##0;"±0"'


def f(size=10, bold=False, color=TEXT):
    return Font(name=FONT, size=size, bold=bold, color=color)


def fill(c):
    return PatternFill("solid", start_color=c, end_color=c)


def kanji(ref):
    """¥11,053,540（約1,105万4千円） 形式の表示用数式（千円単位で四捨五入）"""
    t = f"ROUND(ABS({ref})/1000,0)"
    return (
        f'=IF(N({ref})=0,"",TEXT({ref},"¥#,##0")'
        f'&IF({t}=0,"","（約"&IF({t}>=10,TEXT(INT({t}/10),"#,##0")&"万","")'
        f'&IF(MOD({t},10)>0,MOD({t},10)&"千","")&"円）"))'
    )


# ---------------------------------------------------------------- 10月データ
OCT = {
    "month": "2026年10月",
    "days": 27, "points": 474089, "jihi": 6102050, "hanbai": 210600,
    "shinkan": 33, "avg_points": 1264,
    "jihi_items": [
        # (区分, 項目, 件数, 金額)
        ("補綴", "オールセラミッククラウン imp", 14, 1701700),
        ("補綴", "ジルコニアクラウン imp", 8, 717750),
        ("補綴", "スーパーエナメル imp", 5, 467500),
        ("補綴", "ジルコニアインレー imp", 9, 413898),
        ("補綴", "ジルコニアグラデーション", 2, 187000),
        ("補綴", "プロビジョナル", 2, 5500),
        ("矯正", "インビザライン モデレート", 4, 2191200),
        ("矯正", "マウスピースリテーナー（当院）", 7, 99000),
        ("矯正", "マウスピースリテーナー（他院）", 1, 44000),
        ("矯正", "プレオルソ", None, 77000),
        ("矯正", "矯正検査", 3, 66000),
        ("矯正", "リンガルリテーナー", None, 5500),
        ("矯正", "追加アライナースキャン（2回目）", None, 5500),
        ("矯正", "追加アライナースキャン（3回目）", None, 5500),
        ("その他", "自費書き換え", None, 77002),
        ("その他", "ボトックス", 3, 63800),
        ("その他", "キャンセル料", 16, 16000),
    ],
    "airflow_cnt": 15, "airflow_amt": 49500, "airflow_apotool": 2,
    # Apotool (前月, 当月)
    "apo": {
        "yoyaku": (904, 962), "cancel": (114, 129),
        "jizen": (31, 60), "toujitsu": (27, 27), "mudan": (15, 9),
        "chudan": (102, 130), "teiki": (0.905, 0.917),
    },
    "whitening": 287940,
    "memo": [
        "月売上は目標1,000万円を達成（達成率は上のKPI参照）。",
        "自費項目別合計と個人別自費請求額の差¥41,800は値引・訂正と推定。売上計算は個人別の金額を使用。",
        "エアフローは販売品目15件に対しApotoolのイベント登録が2件。登録漏れの確認が必要。",
        "キャンセル率は12.6%→13.4%に上昇。事前キャンセルが31→60件とほぼ倍増、無断は15→9件に減少。",
        "中断患者数が102→130人に増加。リコール・再来院の声かけを強化したい。",
    ],
}

# 項目の並び（テンプレートでも同じ品目名を用意しておく）
TEMPLATE_ITEMS = [(c, n, None, None) for c, n, _, _ in OCT["jihi_items"]]
EXTRA_ROWS = {"補綴": 2, "矯正": 2, "その他": 2}  # 追加品目用の空行


# ---------------------------------------------------------------- 月次シート
class Cells:
    """推移シートから参照するセル番地（全月共通）"""


def build_month(ws, data, is_template=False):
    ws.sheet_view.showGridLines = False
    widths = {"A": 2, "B": 38, "C": 12, "D": 17, "E": 32, "F": 46}
    for col, w in widths.items():
        ws.column_dimensions[col].width = w

    def val(key, default=None):
        return None if is_template else data.get(key, default)

    def inp(cell, value, fmt=None):
        c = ws[cell]
        c.value = value
        c.font = f(color=BLUE)
        c.fill = fill(CREAM)
        c.border = BORDER
        if fmt:
            c.number_format = fmt
        c.alignment = Alignment(horizontal="right", vertical="center")
        return c

    def calc(cell, formula, fmt=None, bold=False, strong=False, align="right"):
        c = ws[cell]
        c.value = formula
        c.font = f(bold=bold)
        c.border = BORDER
        if strong:
            c.fill = fill(IVORY)
        if fmt:
            c.number_format = fmt
        c.alignment = Alignment(horizontal=align, vertical="center", shrink_to_fit=(align == "left"))
        return c

    def label(cell, text, bold=False, indent=0):
        c = ws[cell]
        c.value = text
        c.font = f(bold=bold)
        c.border = BORDER
        c.alignment = Alignment(vertical="center", indent=indent)
        return c

    def note(cell, text):
        c = ws[cell]
        c.value = text
        c.font = f(size=9, color="6B5A2E")
        c.border = BORDER
        c.alignment = Alignment(vertical="center", wrap_text=True)
        return c

    def section(row, title):
        ws.merge_cells(f"B{row}:F{row}")
        c = ws[f"B{row}"]
        c.value = title
        c.font = f(size=11, bold=True, color="FFFFFF")
        c.fill = fill(GOLD)
        c.alignment = Alignment(vertical="center", indent=1)
        ws.row_dimensions[row].height = 20

    def header(row, labels):
        for col, text in zip("BCDEF", labels):
            c = ws[f"{col}{row}"]
            c.value = text
            c.font = f(bold=True)
            c.fill = fill(GOLD_LIGHT)
            c.border = BORDER
            c.alignment = Alignment(horizontal="center", vertical="center")

    def blank_border(row, cols="BCDEF"):
        for col in cols:
            if ws[f"{col}{row}"].value is None:
                ws[f"{col}{row}"].border = BORDER

    # ---- タイトル
    ws.merge_cells("B1:F1")
    t = ws["B1"]
    t.value = "博多ステラ歯科　月次レポート"
    t.font = f(size=16, bold=True, color="FFFFFF")
    t.fill = fill(GOLD_DARK)
    t.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[1].height = 32

    label("B2", "対象月", bold=True)
    inp("C2", val("month"))
    ws["C2"].alignment = Alignment(horizontal="center")
    ws["D2"].value = "青字＝入力値　黒字＝数式（自動計算）"
    ws["D2"].font = f(size=9, color="6B5A2E")
    ws.merge_cells("D2:F2")

    # ---- 行番号の割り当て（全月共通の固定レイアウト）
    R = {}
    # KPI
    r = 4
    section(r, "■ KPIサマリー")
    header(r + 1, ["指標", "", "値", "表記（漢字単位）", "備考"])
    kpi_rows = ["sales", "goal", "rate", "gap", "per_day", "jihi_ratio", "shinkan", "cancel", "airflow"]
    for i, k in enumerate(kpi_rows):
        R["k_" + k] = r + 2 + i
    r = r + 2 + len(kpi_rows) + 1

    # 日計業務
    R["s1"] = r
    s1_rows = ["days", "points", "jihi", "hanbai", "shinkan", "avg_points"]
    for i, k in enumerate(s1_rows):
        R[k] = r + 2 + i
    r = r + 2 + len(s1_rows) + 1

    # 売上
    R["s2"] = r
    s2_rows = ["hoken", "jihi2", "hanbai2", "total"]
    for i, k in enumerate(s2_rows):
        R[k] = r + 2 + i
    r = r + 2 + len(s2_rows) + 1

    # 自費内訳
    R["s3"] = r
    items = TEMPLATE_ITEMS if is_template else data["jihi_items"]
    cats = ["補綴", "矯正", "その他"]
    cur = r + 2
    cat_ranges = {}
    for cat in cats:
        rows_cat = [it for it in items if it[0] == cat]
        start = cur
        cur += len(rows_cat) + EXTRA_ROWS[cat]
        cat_ranges[cat] = (start, cur - 1, rows_cat)
        R["sub_" + cat] = cur
        cur += 1
    R["item_total"] = cur
    R["item_diff"] = cur + 1
    r = cur + 3

    # エアフロー
    R["s4"] = r
    s4_rows = ["af_cnt", "af_amt", "af_unit", "af_share", "af_apo", "af_gap"]
    for i, k in enumerate(s4_rows):
        R[k] = r + 2 + i
    r = r + 2 + len(s4_rows) + 1

    # Apotool
    R["s5"] = r
    s5_rows = ["yoyaku", "cancel", "raiin", "cancel_rate", "jizen", "toujitsu", "mudan", "c_other",
               "chudan", "teiki"]
    for i, k in enumerate(s5_rows):
        R[k] = r + 2 + i
    r = r + 2 + len(s5_rows) + 1

    # 参考：ホワイトニング
    R["s6"] = r
    R["wh"] = r + 2
    R["wh_sum"] = r + 3
    r = r + 5

    # 所見
    R["s7"] = r
    R["memo_start"] = r + 1
    memo_n = 6
    r = r + 1 + memo_n + 1
    R["chart_row"] = r

    # ================================================================ 1. 日計業務
    section(R["s1"], "■ 1. 日計業務（レセコン）")
    header(R["s1"] + 1, ["項目", "単位", "値", "表記（漢字単位）", "備考"])
    s1_def = [
        ("days", "診療日数", "日", NUM, "", False),
        ("points", "合計点数", "点", NUM, "", False),
        ("jihi", "自費請求額（個人別）", "円", YEN, "売上計算に使う自費の金額", True),
        ("hanbai", "販売品目", "円", YEN, "物販（エアフロー含む）", True),
        ("shinkan", "新患", "人", NUM, "", False),
        ("avg_points", "平均点数", "点", NUM, "レセコン表示値", False),
    ]
    for key, name, unit, fmt, memo, yen in s1_def:
        row = R[key]
        label(f"B{row}", name)
        label(f"C{row}", unit).alignment = Alignment(horizontal="center")
        inp(f"D{row}", val(key), fmt)
        if yen:
            calc(f"E{row}", kanji(f"D{row}"), align="left")
        else:
            blank_border(row, "E")
        note(f"F{row}", memo)

    # ================================================================ 2. 売上
    section(R["s2"], "■ 2. 月売上（＝合計点数×10＋自費請求額＋販売品目）")
    header(R["s2"] + 1, ["区分", "構成比", "金額", "表記（漢字単位）", "計算式"])
    tot = f"D{R['total']}"
    s2_def = [
        ("hoken", "保険（合計点数×10）", f"=D{R['points']}*10", "合計点数 × 10円"),
        ("jihi2", "自費（個人別）", f"=D{R['jihi']}", "自費請求額（個人別）"),
        ("hanbai2", "販売品目", f"=D{R['hanbai']}", "販売品目"),
    ]
    for key, name, formula, memo in s2_def:
        row = R[key]
        label(f"B{row}", name)
        calc(f"C{row}", f'=IF(N({tot})=0,"",D{row}/{tot})', PCT)
        calc(f"D{row}", formula, YEN)
        calc(f"E{row}", kanji(f"D{row}"), align="left")
        note(f"F{row}", memo)
    row = R["total"]
    label(f"B{row}", "月売上 合計", bold=True)
    calc(f"C{row}", f'=IF(N({tot})=0,"",SUM(C{R["hoken"]}:C{R["hanbai2"]}))', PCT, bold=True, strong=True)
    calc(f"D{row}", f"=SUM(D{R['hoken']}:D{R['hanbai2']})", YEN, bold=True, strong=True)
    calc(f"E{row}", kanji(f"D{row}"), bold=True, strong=True, align="left")
    note(f"F{row}", "未収金は含めない")

    # ================================================================ 3. 自費内訳
    section(R["s3"], "■ 3. 自費の内訳（レセコン 自費項目別）")
    header(R["s3"] + 1, ["項目", "件数", "金額", "表記（漢字単位）", "備考"])
    for cat in cats:
        start, end, rows_cat = cat_ranges[cat]
        for i in range(end - start + 1):
            row = start + i
            if i < len(rows_cat):
                _, name, cnt, amt = rows_cat[i]
                label(f"B{row}", f"{cat}｜{name}", indent=1)
            else:
                cnt = amt = None
                c = label(f"B{row}", None, indent=1)
                c.font = f(color=BLUE)
                c.fill = fill(CREAM)
            inp(f"C{row}", None if is_template else cnt, NUM)
            inp(f"D{row}", None if is_template else amt, YEN)
            calc(f"E{row}", kanji(f"D{row}"), align="left")
            memo = ""
            if not is_template and i < len(rows_cat) and cnt is None:
                memo = "件数の記載なし（金額のみ）"
            if i >= len(rows_cat):
                memo = "追加品目があれば項目名から入力"
            note(f"F{row}", memo)
        srow = R["sub_" + cat]
        label(f"B{srow}", f"{cat} 小計", bold=True)
        calc(f"C{srow}", f"=SUM(C{start}:C{end})", NUM, bold=True, strong=True)
        calc(f"D{srow}", f"=SUM(D{start}:D{end})", YEN, bold=True, strong=True)
        calc(f"E{srow}", kanji(f"D{srow}"), bold=True, strong=True, align="left")
        note(f"F{srow}", "")
    row = R["item_total"]
    subs = ",".join(f"D{R['sub_' + c]}" for c in cats)
    label(f"B{row}", "自費項目別 合計", bold=True)
    blank_border(row, "C")
    calc(f"D{row}", f"=SUM({subs})", YEN, bold=True, strong=True)
    calc(f"E{row}", kanji(f"D{row}"), bold=True, strong=True, align="left")
    note(f"F{row}", "補綴＋矯正＋その他")
    row = R["item_diff"]
    label(f"B{row}", "差額（項目別 − 個人別）")
    blank_border(row, "C")
    calc(f"D{row}", f"=D{R['item_total']}-D{R['jihi']}", YEN)
    calc(f"E{row}", kanji(f"D{row}"), align="left")
    note(f"F{row}", "値引・訂正と推定。売上計算は個人別の自費請求額を使用")

    # ================================================================ 4. エアフロー
    section(R["s4"], "■ 4. エアフロー（毎月記録）")
    header(R["s4"] + 1, ["項目", "単位", "値", "表記（漢字単位）", "備考"])
    row = R["af_cnt"]
    label(f"B{row}", "件数（販売品目）"); label(f"C{row}", "件").alignment = Alignment(horizontal="center")
    inp(f"D{row}", val("airflow_cnt"), NUM); blank_border(row, "E"); note(f"F{row}", "レセコン 販売品目別")
    row = R["af_amt"]
    label(f"B{row}", "売上"); label(f"C{row}", "円").alignment = Alignment(horizontal="center")
    inp(f"D{row}", val("airflow_amt"), YEN); calc(f"E{row}", kanji(f"D{row}"), align="left")
    note(f"F{row}", "")
    row = R["af_unit"]
    label(f"B{row}", "単価"); label(f"C{row}", "円").alignment = Alignment(horizontal="center")
    calc(f"D{row}", f'=IF(N(D{R["af_cnt"]})=0,"",D{R["af_amt"]}/D{R["af_cnt"]})', YEN)
    calc(f"E{row}", kanji(f"D{row}"), align="left"); note(f"F{row}", "売上 ÷ 件数")
    row = R["af_share"]
    label(f"B{row}", "物販に占める割合"); label(f"C{row}", "%").alignment = Alignment(horizontal="center")
    calc(f"D{row}", f'=IF(N(D{R["hanbai"]})=0,"",D{R["af_amt"]}/D{R["hanbai"]})', PCT)
    blank_border(row, "E"); note(f"F{row}", "エアフロー売上 ÷ 販売品目")
    row = R["af_apo"]
    label(f"B{row}", "Apotool イベント登録件数"); label(f"C{row}", "件").alignment = Alignment(horizontal="center")
    inp(f"D{row}", val("airflow_apotool"), NUM); blank_border(row, "E"); note(f"F{row}", "")
    row = R["af_gap"]
    label(f"B{row}", "登録漏れ（販売件数 − 登録件数）"); label(f"C{row}", "件").alignment = Alignment(horizontal="center")
    calc(f"D{row}", f"=D{R['af_cnt']}-D{R['af_apo']}", NUM)
    blank_border(row, "E"); note(f"F{row}", "0でなければApotoolへの登録を確認")

    # ================================================================ 5. Apotool
    section(R["s5"], "■ 5. 予約・キャンセル・リコール（Apotool）")
    header(R["s5"] + 1, ["項目", "前月", "当月", "増減", "備考"])
    apo = {} if is_template else data["apo"]

    def apo_row(key, name, fmt, is_input=True, formula=None, diff_fmt=DIFF, memo=""):
        row = R[key]
        label(f"B{row}", name)
        if is_input:
            prev, curv = apo.get(key, (None, None))
            inp(f"C{row}", prev, fmt)
            inp(f"D{row}", curv, fmt)
        else:
            calc(f"C{row}", formula("C"), fmt)
            calc(f"D{row}", formula("D"), fmt)
        if diff_fmt == PT:
            calc(f"E{row}", f'=IF(OR(C{row}="",D{row}=""),"",(D{row}-C{row})*100)', PT)
        else:
            calc(f"E{row}", f'=IF(OR(C{row}="",D{row}=""),"",D{row}-C{row})', DIFF)
        note(f"F{row}", memo)

    ry, rc, rr = R["yoyaku"], R["cancel"], R["raiin"]
    apo_row("yoyaku", "総予約件数", NUM)
    apo_row("cancel", "キャンセル数", NUM)
    apo_row("raiin", "来院件数", NUM, False,
            lambda c: f'=IF({c}{ry}="","",{c}{ry}-{c}{rc})', memo="総予約件数 − キャンセル数")
    apo_row("cancel_rate", "キャンセル率", PCT, False,
            lambda c: f'=IF(N({c}{rr})+N({c}{rc})=0,"",{c}{rc}/({c}{rr}+{c}{rc}))',
            diff_fmt=PT, memo="キャンセル数 ÷（来院件数＋キャンセル数）")
    apo_row("jizen", "　うち事前キャンセル", NUM)
    apo_row("toujitsu", "　うち当日キャンセル", NUM)
    apo_row("mudan", "　うち無断キャンセル", NUM)
    apo_row("c_other", "　その他（区分外）", NUM, False,
            lambda c: f'=IF({c}{rc}="","",{c}{rc}-SUM({c}{R["jizen"]}:{c}{R["mudan"]}))',
            memo="キャンセル数 −（事前＋当日＋無断）。変更・振替などApotoolの区分外")
    apo_row("chudan", "中断患者数（人）", NUM)
    apo_row("teiki", "定期検診来院率", PCT, diff_fmt=PT, memo="Apotool表示値")

    # ================================================================ 6. 参考
    section(R["s6"], "■ 参考：ホワイトニング（株式会社ステラ・別法人）")
    header(R["s6"] + 1, ["項目", "", "金額", "表記（漢字単位）", "備考"])
    row = R["wh"]
    label(f"B{row}", "ホワイトニング 月合計"); blank_border(row, "C")
    inp(f"D{row}", val("whitening"), YEN); calc(f"E{row}", kanji(f"D{row}"), align="left")
    note(f"F{row}", "別法人のため月売上・達成率には含めない")
    row = R["wh_sum"]
    label(f"B{row}", "（参考）医院＋ステラ 合算"); blank_border(row, "C")
    calc(f"D{row}", f"=D{R['total']}+D{R['wh']}", YEN); calc(f"E{row}", kanji(f"D{row}"), align="left")
    note(f"F{row}", "グループ全体の目安")

    # ================================================================ 7. 所見
    section(R["s7"], "■ 所見・メモ（手入力）")
    memos = [] if is_template else data["memo"]
    for i in range(memo_n):
        row = R["memo_start"] + i
        ws.merge_cells(f"B{row}:F{row}")
        c = ws[f"B{row}"]
        c.value = memos[i] if i < len(memos) else None
        c.font = f(color=BLUE)
        c.fill = fill(CREAM)
        c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
        for col in "BCDEF":
            ws[f"{col}{row}"].border = BORDER
        ws.row_dimensions[row].height = 18

    # ================================================================ KPI
    section(4, "■ KPIサマリー")
    k = R
    kpi_def = [
        ("sales", "月売上", f"=D{R['total']}", YEN, True, "合計点数×10＋自費請求額＋販売品目"),
        ("goal", "月目標", 10000000, YEN, True, "目標値（変更する場合はここを入力）"),
        ("rate", "達成率", f'=IF(N(D{k["k_goal"]})=0,"",D{k["k_sales"]}/D{k["k_goal"]})', PCT, False,
         "月売上 ÷ 月目標"),
        ("gap", "目標との差", f"=D{k['k_sales']}-D{k['k_goal']}", YEN, True, "プラス＝目標超過"),
        ("per_day", "1日あたり売上", f'=IF(N(D{R["days"]})=0,"",D{k["k_sales"]}/D{R["days"]})', YEN, True,
         "月売上 ÷ 診療日数"),
        ("jihi_ratio", "自費比率（売上ベース）", f'=IF(N(D{R["total"]})=0,"",D{R["jihi2"]}/D{R["total"]})',
         PCT, False, "自費 ÷ 月売上"),
        ("shinkan", "新患", f"=D{R['shinkan']}", '#,##0"人";-#,##0"人";"-"', False, ""),
        ("cancel", "キャンセル率", f"=D{R['cancel_rate']}", PCT, False,
         "キャンセル数 ÷（来院件数＋キャンセル数）"),
        ("airflow", "エアフロー件数", f"=D{R['af_cnt']}", '#,##0"件";-#,##0"件";"-"', False, ""),
    ]
    for key, name, formula, fmt, yen, memo in kpi_def:
        row = R["k_" + key]
        label(f"B{row}", name, bold=key in ("sales", "rate"))
        blank_border(row, "C")
        if key == "goal":
            inp(f"D{row}", formula, fmt)
        else:
            calc(f"D{row}", formula, fmt, bold=key in ("sales", "rate"), strong=key in ("sales", "rate"))
        if yen:
            calc(f"E{row}", kanji(f"D{row}"), bold=key == "sales", align="left")
        else:
            blank_border(row, "E")
        note(f"F{row}", memo)
    # 月売上・達成率を大きく
    for key in ("sales", "rate"):
        ws[f"D{R['k_' + key]}"].font = f(size=12, bold=True, color=GOLD_DARK)
        ws.row_dimensions[R["k_" + key]].height = 20

    # 数式中の補足コメント
    ws[f"D{R['item_diff']}"].comment = Comment(
        "自費項目別の合計と、個人別（サマリー）の自費請求額との差。\n値引・訂正分と推定。", "月次レポート")
    ws[f"D{R['k_goal']}"].comment = Comment("院長設定の月目標 1,000万円", "月次レポート")

    # ================================================================ グラフ
    cr = R["chart_row"]
    pie = PieChart()
    pie.title = "月売上の構成"
    pie.add_data(Reference(ws, min_col=4, min_row=R["hoken"], max_row=R["hanbai2"]), titles_from_data=False)
    pie.set_categories(Reference(ws, min_col=2, min_row=R["hoken"], max_row=R["hanbai2"]))
    s = pie.series[0]
    for i, color in enumerate([GOLD_DARK, GOLD, GOLD_LIGHT]):
        pt = DataPoint(idx=i)
        pt.graphicalProperties.solidFill = color
        pt.graphicalProperties.line.solidFill = "FFFFFF"
        s.dPt.append(pt)
    s.dLbls = DataLabelList()
    s.dLbls.showPercent = True
    s.dLbls.showVal = False
    s.dLbls.showCatName = False
    s.dLbls.showSerName = False
    s.dLbls.showLeaderLines = False
    pie.height, pie.width = 7.5, 11
    ws.add_chart(pie, f"B{cr}")

    bar = BarChart()
    bar.type = "bar"
    bar.title = "自費 区分別"
    sub_rows = [R["sub_" + c] for c in cats]
    # 小計行は連続していないので、グラフ用の参照表を右側（H列〜）に置く
    ws["H" + str(cr)] = "グラフ用"
    ws["H" + str(cr)].font = f(size=8, color="A08C5A")
    for i, c in enumerate(cats):
        ws[f"H{cr + 1 + i}"] = c
        ws[f"I{cr + 1 + i}"] = f"=D{sub_rows[i]}"
        ws[f"I{cr + 1 + i}"].number_format = YEN
        for col in "HI":
            ws[f"{col}{cr + 1 + i}"].font = f(size=8, color="A08C5A")
    bar.add_data(Reference(ws, min_col=9, min_row=cr + 1, max_row=cr + 3), titles_from_data=False)
    bar.set_categories(Reference(ws, min_col=8, min_row=cr + 1, max_row=cr + 3))
    bar.series[0].graphicalProperties.solidFill = GOLD
    bar.series[0].graphicalProperties.line.solidFill = GOLD_DARK
    bar.legend = None
    bar.y_axis.numFmt = '#,##0'
    bar.y_axis.majorGridlines = None
    bar.height, bar.width = 7.5, 13
    ws.add_chart(bar, f"E{cr}")

    # ---- 印刷設定
    ws.print_area = f"A1:F{cr + 16}"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.orientation = "portrait"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_margins = PageMargins(left=0.4, right=0.4, top=0.5, bottom=0.5)
    ws.sheet_properties.tabColor = GOLD
    return R


# ---------------------------------------------------------------- 推移シート
def build_trend(ws, R, months):
    ws.sheet_view.showGridLines = False
    cols = [
        ("シート名", None, None, 14),
        ("月売上", "k_sales", YEN, 15),
        ("月売上（表記）", "KANJI", None, 30),
        ("達成率", "k_rate", PCT, 9),
        ("保険売上", "hoken", YEN, 14),
        ("自費（個人別）", "jihi2", YEN, 14),
        ("販売品目", "hanbai2", YEN, 12),
        ("合計点数", "points", NUM, 11),
        ("診療日数", "days", NUM, 9),
        ("新患", "shinkan", NUM, 7),
        ("キャンセル率", "cancel_rate", PCT, 11),
        ("エアフロー件数", "af_cnt", NUM, 12),
        ("エアフロー売上", "af_amt", YEN, 12),
        ("エアフロー物販比", "af_share", PCT, 13),
        ("中断患者数", "chudan", NUM, 10),
        ("定期検診来院率", "teiki", PCT, 13),
    ]
    last = get_column_letter(len(cols) + 1)
    ws.merge_cells(f"B1:{last}1")
    t = ws["B1"]
    t.value = "博多ステラ歯科　月次推移"
    t.font = f(size=16, bold=True, color="FFFFFF")
    t.fill = fill(GOLD_DARK)
    t.alignment = Alignment(vertical="center", indent=1)
    ws.row_dimensions[1].height = 32
    ws["B2"] = "B列に月シートの名前（例：2026年11月）を青字で入力すると、そのシートの数値を自動で読み込みます。"
    ws["B2"].font = f(size=9, color="6B5A2E")
    ws.column_dimensions["A"].width = 2

    hr = 4
    for i, (name, _, _, w) in enumerate(cols):
        col = get_column_letter(i + 2)
        ws.column_dimensions[col].width = w
        c = ws[f"{col}{hr}"]
        c.value = name
        c.font = f(bold=True, color="FFFFFF")
        c.fill = fill(GOLD)
        c.border = BORDER
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[hr].height = 30

    n_rows = 24
    for j in range(n_rows):
        row = hr + 1 + j
        name_cell = f"$B{row}"
        for i, (name, key, fmt, _) in enumerate(cols):
            col = get_column_letter(i + 2)
            c = ws[f"{col}{row}"]
            c.border = BORDER
            if key is None:
                c.value = months[j] if j < len(months) else None
                c.font = f(color=BLUE)
                c.fill = fill(CREAM)
                c.alignment = Alignment(horizontal="center")
            elif key == "KANJI":
                c.value = kanji(f"C{row}")
                c.font = f()
            else:
                ref = f"D{R[key]}"
                c.value = f'=IF({name_cell}="","",IFERROR(INDIRECT("\'"&{name_cell}&"\'!{ref}"),""))'
                c.number_format = fmt
                c.font = f()
            if j % 2 == 1 and key is not None:
                c.fill = fill(IVORY)
    ws.freeze_panes = "C5"
    ws.sheet_properties.tabColor = GOLD_LIGHT
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True


# ---------------------------------------------------------------- 使い方シート
def build_howto(ws, R):
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 2
    ws.column_dimensions["B"].width = 26
    ws.column_dimensions["C"].width = 90
    ws.merge_cells("B1:C1")
    t = ws["B1"]
    t.value = "使い方（毎月の運用）"
    t.font = f(size=16, bold=True, color="FFFFFF")
    t.fill = fill(GOLD_DARK)
    t.alignment = Alignment(vertical="center", indent=1)
    ws.row_dimensions[1].height = 32

    rows = [
        ("■ 毎月の手順", None),
        ("1. シートを追加", "「テンプレート」シートのタブを右クリック →「移動またはコピー」→「コピーを作成する」に✓ → OK。"),
        ("2. 名前を変更", "コピーしたシートの名前を「2026年11月」のように変更（推移シートで使うので、この形に統一）。"),
        ("3. 入力", "青字のセル（クリーム色）だけ入力。黒字のセルは数式なので触らない。C2の対象月も忘れずに。"),
        ("4. 前月の数値", "Apotoolの「前月」列は、前月シートの「当月」列の値をそのまま転記。"),
        ("5. 推移に登録", "「推移」シートのB列の空欄に新しいシート名を入力 → 主要KPIが自動で並ぶ。"),
        ("6. 所見", "所見・メモ欄に今月のポイントを記入（先月の文章は書き換える）。"),
        ("", None),
        ("■ 凡例", None),
        ("青字・クリーム色", "入力値（レセコン・Apotoolから転記する数字）"),
        ("黒字", "数式（自動計算）"),
        ("表記（漢字単位）", "金額を「¥11,053,540（約1,105万4千円）」の形で自動表示（千円単位で四捨五入）"),
        ("", None),
        ("■ 計算式", None),
        ("月売上", "合計点数 × 10 ＋ 自費請求額（個人別） ＋ 販売品目　※未収金は含めない"),
        ("達成率", "月売上 ÷ 月目標（1,000万円）"),
        ("キャンセル率", "キャンセル数 ÷（来院件数 ＋ キャンセル数）　※来院件数＝総予約件数 − キャンセル数"),
        ("エアフロー単価", "エアフロー売上 ÷ 件数"),
        ("エアフロー物販比", "エアフロー売上 ÷ 販売品目"),
        ("自費の差額", "自費項目別の合計 − 個人別の自費請求額（値引・訂正と推定）。売上は個人別の金額で計算"),
        ("ホワイトニング", "株式会社ステラ（別法人）の参考値。月売上・達成率には含めない"),
        ("", None),
        ("■ 入力元", None),
        ("日計業務（レセコン）", "診療日数・合計点数・自費請求額（個人別）・販売品目・新患・平均点数"),
        ("自費項目別（レセコン）", "自費の各品目の件数・金額。新しい品目は各区分の空行に項目名から入力"),
        ("販売品目別（レセコン）", "エアフローの件数・金額"),
        ("Apotool", "総予約・キャンセル（事前／当日／無断）・中断患者数・定期検診来院率・エアフローのイベント登録件数"),
    ]
    r = 3
    for a, b in rows:
        if b is None and a:
            ws.merge_cells(f"B{r}:C{r}")
            c = ws[f"B{r}"]
            c.value = a
            c.font = f(size=11, bold=True, color="FFFFFF")
            c.fill = fill(GOLD)
            c.alignment = Alignment(vertical="center", indent=1)
        elif a:
            ca, cb = ws[f"B{r}"], ws[f"C{r}"]
            ca.value, cb.value = a, b
            ca.font = f(bold=True, color=BLUE if a.startswith("青字") else TEXT)
            if a.startswith("青字"):
                ca.fill = fill(CREAM)
            cb.font = f()
            cb.alignment = Alignment(wrap_text=True, vertical="center")
            for c in (ca, cb):
                c.border = BORDER
        r += 1
    ws.sheet_properties.tabColor = "A08C5A"


def main():
    wb = Workbook()
    ws_oct = wb.active
    ws_oct.title = OCT["month"]
    R = build_month(ws_oct, OCT)
    build_trend(wb.create_sheet("推移"), R, [OCT["month"]])
    R2 = build_month(wb.create_sheet("テンプレート"), {}, is_template=True)
    assert R == R2, "テンプレートと月次シートのレイアウトがずれています"
    build_howto(wb.create_sheet("使い方"), R)
    wb.save(OUT)
    print(f"saved: {OUT}")


if __name__ == "__main__":
    main()
