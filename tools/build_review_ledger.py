#!/usr/bin/env python3
"""Google口コミ・プレゼント台帳の Excel テンプレートを生成する。

    python tools/build_review_ledger.py 出力先.xlsx [登録済みデータ.json]

月ごとにシートを分け（R8.9月〜R8.12月）、集計シートで合計する。
第2引数に JSON（口コミの配列）を渡すと、対象月のシートに書き込む。
患者情報を含むデータはリポジトリに置かないこと。
"""
import json
import re
import sys

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.properties import PageSetupProperties

FONT = "Meiryo"
LAST_ROW = 40                                    # 1か月あたりの入力欄
MONTHS = ["2026-09", "2026-10", "2026-11", "2026-12"]

INK = "1F3033"
ACCENT = "0E6E62"
HEAD_FILL = PatternFill("solid", fgColor="0E6E62")
PENDING_FILL = PatternFill("solid", fgColor="FCEAE0")
DONE_FILL = PatternFill("solid", fgColor="E4F1E9")
RULE = Side(style="thin", color="DCE4E1")

COLUMNS = [
    ("患者番号", 9),
    ("患者名", 14),
    ("区分", 10),
    ("プレゼント", 18),
    ("状態", 9),
    ("渡した日", 11),
    ("担当", 9),
    ("評価", 6),
    ("投稿日", 11),
    ("Google表示名", 14),
    ("備考", 20),
    ("口コミ内容", 100),
]
CENTERED = (1, 3, 5, 6, 7, 8, 9)
CAT_COL, GIFT_COL, STATUS_COL, STARS_COL, NAME_COL = 3, 4, 5, 8, 2
GIFT_ORTHO = "ホワイトニング"
GIFT_GENERAL = "物品1,000円OFF"


def era_month(month):
    """2026-09 → R8.9月"""
    y, m = (int(x) for x in month.split("-"))
    return "R{}.{}月".format(y - 2018, m)


def era_month_long(month):
    y, m = (int(x) for x in month.split("-"))
    return "令和{}年{}月".format(y - 2018, m)


def build_month_sheet(ws, month, entries):
    ws.freeze_panes = "C2"
    for col, (title, width) in enumerate(COLUMNS, start=1):
        cell = ws.cell(row=1, column=col, value=title)
        cell.font = Font(name=FONT, bold=True, size=10, color="FFFFFF")
        cell.fill = HEAD_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[get_column_letter(col)].width = width
    ws.row_dimensions[1].height = 24

    order = ["patientNo", "name", "category", "gift", "status", "givenDate",
             "staff", "stars", "postedAt", "reviewer", "note", "content"]
    for i, e in enumerate(entries):
        r = i + 2
        for c, key in enumerate(order, start=1):
            # プレゼントは区分から自動判定。「その他」で内容がある場合だけ上書きする
            if c == GIFT_COL and not e.get("gift"):
                continue
            value = e.get(key, "")
            if key == "content":
                # 改行を含むと1行表示が崩れるため、1つの段落にまとめる
                value = re.sub(r"\s*\n+\s*", " ", str(value)).strip()
            ws.cell(row=r, column=c, value=value)

    for r in range(2, LAST_ROW + 1):
        if ws.cell(row=r, column=GIFT_COL).value is None:
            ws.cell(row=r, column=GIFT_COL).value = (
                f'=IF(${get_column_letter(CAT_COL)}{r}="矯正中","{GIFT_ORTHO}",'
                f'IF(${get_column_letter(CAT_COL)}{r}="矯正以外","{GIFT_GENERAL}",""))'
            )
        for c in range(1, len(COLUMNS) + 1):
            cell = ws.cell(row=r, column=c)
            cell.font = Font(name=FONT, size=10, color=INK)
            cell.border = Border(bottom=RULE)
            cell.alignment = Alignment(
                vertical="center",
                horizontal="center" if c in CENTERED else "left",
            )
        ws.cell(row=r, column=6).number_format = "yyyy/mm/dd"
        ws.cell(row=r, column=9).number_format = "yyyy/mm/dd"
        ws.row_dimensions[r].height = 22   # 1行1件。行の高さをそろえて一覧性を優先する

    ws.auto_filter.ref = f"A1:L{LAST_ROW}"

    dv_cat = DataValidation(type="list", formula1='"矯正中,矯正以外,その他"', allow_blank=True)
    dv_cat.error = "矯正中／矯正以外／その他 から選んでください。"
    dv_status = DataValidation(type="list", formula1='"未渡し,渡し済"', allow_blank=True)
    dv_stars = DataValidation(type="list", formula1='"5,4,3,2,1"', allow_blank=True)
    for dv, col in ((dv_cat, CAT_COL), (dv_status, STATUS_COL), (dv_stars, STARS_COL)):
        ws.add_data_validation(dv)
        letter = get_column_letter(col)
        dv.add(f"{letter}2:{letter}{LAST_ROW}")

    # 状態に応じて行全体に色を付ける（未渡しが一目で分かるように）
    body = f"A2:L{LAST_ROW}"
    st = f"${get_column_letter(STATUS_COL)}2"
    ws.conditional_formatting.add(
        body, FormulaRule(formula=[f'{st}="未渡し"'], fill=PENDING_FILL, stopIfTrue=False))
    ws.conditional_formatting.add(
        body, FormulaRule(formula=[f'{st}="渡し済"'], fill=DONE_FILL, stopIfTrue=False))

    # 口コミ本文（L列）は紙に載せると読めないので、印刷はK列までにする
    ws.print_area = f"A1:K{LAST_ROW}"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    ws.print_title_rows = "1:1"


def build_reading_sheet(ws):
    """ミーティングで読むための表示用シート。

    入力は月別シートのまま。ここは対象月を選ぶと、その月の口コミを
    「見出しの帯 ＋ 本文」の2行組で並べるだけの画面。
    """
    BLOCKS = 20                       # 1か月あたりに用意する表示枠
    HEAD_FILL_OK = PatternFill("solid", fgColor="E4F1E9")
    HEAD_FILL_YET = PatternFill("solid", fgColor="FBE6DA")

    ws.column_dimensions["A"].width = 3     # 左の余白
    ws.column_dimensions["B"].width = 88    # 本文。1行が長くなりすぎない幅にする
    ws.sheet_view.showGridLines = False

    ws["B1"] = "ミーティング用"
    ws["B1"].font = Font(name=FONT, bold=True, size=16, color=ACCENT)
    ws.row_dimensions[1].height = 28

    ws["B2"] = era_month(MONTHS[0])
    ws["B2"].font = Font(name=FONT, bold=True, size=13, color=INK)
    ws["B2"].fill = PatternFill("solid", fgColor="DCEEE9")
    ws["B2"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[2].height = 24
    dv = DataValidation(type="list",
                        formula1='"' + ",".join(era_month(m) for m in MONTHS) + '"',
                        allow_blank=False)
    ws.add_data_validation(dv)
    dv.add("B2")

    name_col = get_column_letter(NAME_COL)
    status_col = get_column_letter(STATUS_COL)
    ws["B3"] = (f'="この月の口コミ "&COUNTA(INDIRECT("\'"&$B$2&"\'!{name_col}2:{name_col}{LAST_ROW}"))'
                f'&" 件　／　プレゼント未渡し "'
                f'&COUNTIF(INDIRECT("\'"&$B$2&"\'!{status_col}2:{status_col}{LAST_ROW}"),"未渡し")&" 件"')
    ws["B3"].font = Font(name=FONT, size=11, color="5A6B67")
    ws.row_dimensions[3].height = 22

    def ref(col, row_expr):
        letter = get_column_letter(col)
        return f'INDIRECT("\'"&$B$2&"\'!{letter}"&{row_expr})'

    first = 5
    for i in range(BLOCKS):
        head_row = first + i * 3
        body_row = head_row + 1
        gap_row = head_row + 2
        src = str(i + 2)              # 月別シートの2行目から順に見る

        # 見出しの帯：患者番号・氏名・評価・区分→プレゼント・渡したかどうか
        ws.cell(row=head_row, column=2, value=(
            f'=IF({ref(NAME_COL, src)}="","",'
            f'"No."&{ref(1, src)}&"　"&{ref(NAME_COL, src)}&" 様　　"&'
            f'REPT("★",{ref(STARS_COL, src)})&"　　"&{ref(CAT_COL, src)}&" → "&{ref(GIFT_COL, src)}&'
            f'"　　"&{ref(STATUS_COL, src)})'
        ))
        head = ws.cell(row=head_row, column=2)
        head.font = Font(name=FONT, bold=True, size=12, color=INK)
        head.alignment = Alignment(vertical="center", indent=1)
        ws.row_dimensions[head_row].height = 26

        # 本文：折り返して全文を出す
        ws.cell(row=body_row, column=2, value=f'=IF({ref(NAME_COL, src)}="","",{ref(12, src)})')
        body = ws.cell(row=body_row, column=2)
        body.font = Font(name=FONT, size=11, color="223330")
        body.alignment = Alignment(vertical="top", wrap_text=True, indent=1)

        ws.row_dimensions[gap_row].height = 10   # 1件ごとの余白

    last = first + BLOCKS * 3
    # 未渡しはオレンジ、渡し済は緑の帯にする（帯の行だけが色付く）
    ws.conditional_formatting.add(
        f"B{first}:B{last}",
        FormulaRule(formula=[f'ISNUMBER(SEARCH("様",$B{first}))*ISNUMBER(SEARCH("未渡し",$B{first}))'],
                    fill=HEAD_FILL_YET, stopIfTrue=True))
    ws.conditional_formatting.add(
        f"B{first}:B{last}",
        FormulaRule(formula=[f'ISNUMBER(SEARCH("様",$B{first}))*ISNUMBER(SEARCH("渡し済",$B{first}))'],
                    fill=HEAD_FILL_OK, stopIfTrue=True))

    ws.print_area = f"A1:B{last}"
    ws.page_setup.orientation = "portrait"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)


def build_summary(ws):
    heads = ["対象月", "口コミ件数", "未渡し", "渡し済", "ホワイトニング", "物品1,000円OFF"]
    ws["A1"] = "月別の集計（各月のシートに入力すると自動で更新されます）"
    ws["A1"].font = Font(name=FONT, bold=True, size=12, color=ACCENT)
    for col, title in enumerate(heads, start=1):
        cell = ws.cell(row=3, column=col, value=title)
        cell.font = Font(name=FONT, bold=True, size=10, color="FFFFFF")
        cell.fill = HEAD_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[get_column_letter(col)].width = 16 if col == 1 else 15

    name_col = get_column_letter(NAME_COL)
    cat_col = get_column_letter(CAT_COL)
    status_col = get_column_letter(STATUS_COL)
    for i, month in enumerate(MONTHS):
        r = 4 + i
        sheet = f"'{era_month(month)}'"
        ws.cell(row=r, column=1, value=era_month_long(month))
        ws.cell(row=r, column=2, value=f'=COUNTA({sheet}!${name_col}$2:${name_col}${LAST_ROW})')
        ws.cell(row=r, column=3, value=f'=COUNTIF({sheet}!${status_col}$2:${status_col}${LAST_ROW},"未渡し")')
        ws.cell(row=r, column=4, value=f'=COUNTIF({sheet}!${status_col}$2:${status_col}${LAST_ROW},"渡し済")')
        ws.cell(row=r, column=5, value=f'=COUNTIF({sheet}!${cat_col}$2:${cat_col}${LAST_ROW},"矯正中")')
        ws.cell(row=r, column=6, value=f'=COUNTIF({sheet}!${cat_col}$2:${cat_col}${LAST_ROW},"矯正以外")')

    total = 4 + len(MONTHS)
    ws.cell(row=total, column=1, value="合計")
    for c in range(2, 7):
        letter = get_column_letter(c)
        ws.cell(row=total, column=c, value=f"=SUM({letter}4:{letter}{total - 1})")

    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)

    for r in range(4, total + 1):
        for c in range(1, 7):
            cell = ws.cell(row=r, column=c)
            cell.font = Font(name=FONT, bold=(r == total), size=10, color=INK)
            cell.border = Border(bottom=RULE)
            cell.alignment = Alignment(horizontal="center")


def build_guide(ws):
    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 78
    rows = [
        ("使い方", ""),
        ("", ""),
        ("シートの分け方", "月ごとにシートが分かれています（R8.9月〜R8.12月）。その月のシートに1件1行で入力します。"),
        ("プレゼント欄", "区分を選ぶと自動で入ります（矯正中→ホワイトニング／矯正以外→物品1,000円OFF）。"),
        ("", "区分が「その他」のときは、プレゼント欄に直接入力してください（自動の数式は消えます）。"),
        ("渡したかどうか", "状態の欄で「未渡し」「渡し済」を選びます。未渡しはオレンジ、渡し済は緑になります。"),
        ("", "渡し済にしたら、渡した日と担当も入れておくと後から確認できます。"),
        ("月例ミーティング", "「ミーティング用」シートを開き、上の対象月を選ぶと、その月の口コミが本文つきで読みやすく並びます。"),
        ("", "入力は各月のシートで行い、読むときだけこのシートを使ってください（自動で連動します）。"),
        ("集計", "「集計」シートに、月ごとの件数・未渡し・渡し済が自動で出ます。"),
        ("口コミ本文の読み方", "本文は右端のL列にあります。1行に収めているので、全文はセルをクリックして上の入力バーで読めます。"),
        ("", "全文を表で表示したいときは、L列を選んで［表示形式］→［折り返し］をオンにしてください。"),
        ("印刷", "印刷すると口コミ本文以外のK列までが、横向き1ページ幅で出ます（見出し行は各ページに付きます）。"),
        ("", ""),
        ("プレゼントの基準", "矯正中の方 → ホワイトニング"),
        ("", "矯正以外の方 → 物品1,000円OFF"),
        ("", "※基準を変える場合は、この行と各月シートのプレゼント欄の数式を直してください。"),
        ("", ""),
        ("記入例", "患者番号 10428 ／ 患者名 佐藤 美咲 ／ 区分 矯正中 ／ プレゼント ホワイトニング（自動）／ "
                  "状態 渡し済 ／ 渡した日 2026/09/12 ／ 担当 中村"),
    ]
    for i, (label, text) in enumerate(rows, start=1):
        a = ws.cell(row=i, column=1, value=label)
        b = ws.cell(row=i, column=2, value=text)
        a.font = Font(name=FONT, bold=True, size=11 if i > 1 else 14,
                      color=ACCENT if i == 1 else INK)
        b.font = Font(name=FONT, size=10, color=INK)
        b.alignment = Alignment(vertical="top", wrap_text=True)
        if len(text) > 60:
            ws.row_dimensions[i].height = 30


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "口コミプレゼント台帳.xlsx"
    entries = []
    if len(sys.argv) > 2:
        with open(sys.argv[2], encoding="utf-8") as fh:
            entries = json.load(fh)

    wb = Workbook()
    wb.remove(wb.active)
    for month in MONTHS:
        ws = wb.create_sheet(era_month(month))
        build_month_sheet(ws, month, [e for e in entries if e.get("month") == month])
    build_reading_sheet(wb.create_sheet("ミーティング用"))
    build_summary(wb.create_sheet("集計"))
    build_guide(wb.create_sheet("使い方"))
    wb.save(out)
    print(f"saved: {out} ({len(entries)} 件 / {len(MONTHS)} か月)")


if __name__ == "__main__":
    main()
