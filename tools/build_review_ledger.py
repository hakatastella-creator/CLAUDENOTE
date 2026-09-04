#!/usr/bin/env python3
"""Google口コミ・プレゼント台帳の Excel テンプレートを生成する。

    python tools/build_review_ledger.py 出力先.xlsx [登録済みデータ.json]

第2引数に JSON（口コミの配列）を渡すと、その内容を台帳シートに書き込む。
患者情報を含むデータはリポジトリに置かないこと。
"""
import json
import sys

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.properties import PageSetupProperties

FONT = "Meiryo"
LAST_ROW = 200          # 入力欄をあらかじめ用意しておく行数
SUMMARY_MONTHS = 12

INK = "1F3033"
ACCENT = "0E6E62"
HEAD_FILL = PatternFill("solid", fgColor="DCEEE9")
PENDING_FILL = PatternFill("solid", fgColor="FAE0D4")
DONE_FILL = PatternFill("solid", fgColor="DCEFE2")
INPUT_FILL = PatternFill("solid", fgColor="FFFDF0")
THIN = Side(style="thin", color="C9D6D2")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

COLUMNS = [
    ("対象月", 10),
    ("投稿日", 11),
    ("患者番号", 10),
    ("患者名", 14),
    ("Google表示名", 14),
    ("評価", 6),
    ("区分", 11),
    ("プレゼント", 20),
    ("状態", 10),
    ("渡した日", 11),
    ("担当", 10),
    ("口コミ内容", 68),
    ("備考", 22),
]
GIFT_ORTHO = "ホワイトニング"
GIFT_GENERAL = "物品1,000円OFF"


def style_header(ws, row=1):
    for col, (title, width) in enumerate(COLUMNS, start=1):
        cell = ws.cell(row=row, column=col, value=title)
        cell.font = Font(name=FONT, bold=True, size=10, color=INK)
        cell.fill = HEAD_FILL
        cell.border = BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(col)].width = width
    ws.row_dimensions[row].height = 26


def build_ledger(ws, entries):
    ws.freeze_panes = "A2"
    style_header(ws)

    for i, e in enumerate(entries):
        r = i + 2
        ws.cell(row=r, column=1, value=e.get("month", ""))
        ws.cell(row=r, column=2, value=e.get("postedAt", ""))
        ws.cell(row=r, column=3, value=e.get("patientNo", ""))
        ws.cell(row=r, column=4, value=e.get("name", ""))
        ws.cell(row=r, column=5, value=e.get("reviewer", ""))
        ws.cell(row=r, column=6, value=e.get("stars", ""))
        ws.cell(row=r, column=7, value=e.get("category", ""))
        # 「その他」で独自のプレゼントが入っている場合だけ数式を上書きする
        if e.get("gift"):
            ws.cell(row=r, column=8, value=e["gift"])
        ws.cell(row=r, column=9, value=e.get("status", "未渡し"))
        ws.cell(row=r, column=10, value=e.get("givenDate", ""))
        ws.cell(row=r, column=11, value=e.get("staff", ""))
        ws.cell(row=r, column=12, value=e.get("content", ""))
        ws.cell(row=r, column=13, value=e.get("note", ""))
        if e.get("comment"):
            ws.cell(row=r, column=3).comment = Comment(e["comment"], "台帳")
        ws.row_dimensions[r].height = 58

    for r in range(2, LAST_ROW + 1):
        # プレゼントは区分から自動判定（「その他」のときは直接入力してよい）
        if ws.cell(row=r, column=8).value is None:
            ws.cell(row=r, column=8).value = (
                f'=IF($G{r}="矯正中","{GIFT_ORTHO}",'
                f'IF($G{r}="矯正以外","{GIFT_GENERAL}",""))'
            )
        for c in range(1, len(COLUMNS) + 1):
            cell = ws.cell(row=r, column=c)
            cell.font = Font(name=FONT, size=10, color=INK)
            cell.border = BORDER
            cell.alignment = Alignment(
                vertical="top",
                wrap_text=(c == 12),
                horizontal="center" if c in (1, 2, 3, 6, 7, 9, 10) else "left",
            )
            if c in (1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13):
                cell.fill = INPUT_FILL
        ws.cell(row=r, column=2).number_format = "yyyy/mm/dd"
        ws.cell(row=r, column=10).number_format = "yyyy/mm/dd"

    ws.auto_filter.ref = f"A1:M{LAST_ROW}"

    # 印刷（ミーティング用に配る場合）: 横向き・幅を1ページに収め、見出し行を各ページに出す
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    ws.print_title_rows = "1:1"

    dv_cat = DataValidation(type="list", formula1='"矯正中,矯正以外,その他"', allow_blank=True)
    dv_cat.error = "矯正中／矯正以外／その他 から選んでください。"
    dv_status = DataValidation(type="list", formula1='"未渡し,渡し済"', allow_blank=True)
    dv_stars = DataValidation(type="list", formula1='"5,4,3,2,1"', allow_blank=True)
    for dv, col in ((dv_cat, "G"), (dv_status, "I"), (dv_stars, "F")):
        ws.add_data_validation(dv)
        dv.add(f"{col}2:{col}{LAST_ROW}")

    rng = f"I2:I{LAST_ROW}"
    ws.conditional_formatting.add(
        rng, CellIsRule(operator="equal", formula=['"未渡し"'], fill=PENDING_FILL)
    )
    ws.conditional_formatting.add(
        rng, CellIsRule(operator="equal", formula=['"渡し済"'], fill=DONE_FILL)
    )


def build_summary(ws, start_month):
    heads = ["対象月", "口コミ件数", "未渡し", "渡し済", "ホワイトニング", "物品1,000円OFF"]
    ws["A1"] = "月別の集計（台帳シートに入力すると自動で更新されます）"
    ws["A1"].font = Font(name=FONT, bold=True, size=12, color=ACCENT)
    for col, title in enumerate(heads, start=1):
        cell = ws.cell(row=3, column=col, value=title)
        cell.font = Font(name=FONT, bold=True, size=10, color=INK)
        cell.fill = HEAD_FILL
        cell.border = BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[get_column_letter(col)].width = 16 if col == 1 else 14

    year, month = (int(x) for x in start_month.split("-"))
    for i in range(SUMMARY_MONTHS):
        r = 4 + i
        y, m = year + (month - 1 + i) // 12, (month - 1 + i) % 12 + 1
        ws.cell(row=r, column=1, value=f"{y}-{m:02d}")
        ws.cell(row=r, column=2, value=f'=COUNTIF(口コミ台帳!$A$2:$A${LAST_ROW},$A{r})')
        ws.cell(row=r, column=3, value=(
            f'=COUNTIFS(口コミ台帳!$A$2:$A${LAST_ROW},$A{r},'
            f'口コミ台帳!$I$2:$I${LAST_ROW},"未渡し")'))
        ws.cell(row=r, column=4, value=(
            f'=COUNTIFS(口コミ台帳!$A$2:$A${LAST_ROW},$A{r},'
            f'口コミ台帳!$I$2:$I${LAST_ROW},"渡し済")'))
        ws.cell(row=r, column=5, value=(
            f'=COUNTIFS(口コミ台帳!$A$2:$A${LAST_ROW},$A{r},'
            f'口コミ台帳!$G$2:$G${LAST_ROW},"矯正中")'))
        ws.cell(row=r, column=6, value=(
            f'=COUNTIFS(口コミ台帳!$A$2:$A${LAST_ROW},$A{r},'
            f'口コミ台帳!$G$2:$G${LAST_ROW},"矯正以外")'))
        for c in range(1, 7):
            cell = ws.cell(row=r, column=c)
            cell.font = Font(name=FONT, size=10, color=INK)
            cell.border = BORDER
            cell.alignment = Alignment(horizontal="center")


def build_guide(ws):
    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 78
    rows = [
        ("使い方", ""),
        ("", ""),
        ("入力する場所", "「口コミ台帳」シートの2行目から、1件につき1行で入力します。"),
        ("プレゼント欄", "区分を選ぶと自動で入ります（矯正中→ホワイトニング／矯正以外→物品1,000円OFF）。"),
        ("", "区分が「その他」のときは、プレゼント欄に直接入力してください（自動の数式は消えます）。"),
        ("渡したかどうか", "状態の欄で「未渡し」「渡し済」を選びます。未渡しはオレンジ、渡し済は緑になります。"),
        ("", "渡し済にしたら、渡した日と担当も入れておくと後から確認できます。"),
        ("月例ミーティング", "見出し行の▼から対象月で絞り込み、状態で「未渡し」だけを表示すると、その場で確認できます。"),
        ("集計", "「月別集計」シートに、月ごとの件数・未渡し・渡し済が自動で出ます。"),
        ("", ""),
        ("プレゼントの基準", "矯正中の方 → ホワイトニング"),
        ("", "矯正以外の方 → 物品1,000円OFF"),
        ("", "※基準を変える場合は、この行と「口コミ台帳」シートのプレゼント欄の数式を直してください。"),
        ("", ""),
        ("記入例", "対象月 2026-09 ／ 投稿日 2026/09/03 ／ 患者番号 10428 ／ 患者名 佐藤 美咲 ／ "
                  "Google表示名 M.S ／ 評価 5 ／ 区分 矯正中 ／ プレゼント ホワイトニング（自動）／ "
                  "状態 渡し済 ／ 渡した日 2026/09/12 ／ 担当 中村"),
    ]
    for i, (label, text) in enumerate(rows, start=1):
        a = ws.cell(row=i, column=1, value=label)
        b = ws.cell(row=i, column=2, value=text)
        a.font = Font(name=FONT, bold=True, size=11 if i > 1 else 14,
                      color=ACCENT if i == 1 else INK)
        b.font = Font(name=FONT, size=10, color=INK)
        b.alignment = Alignment(vertical="top", wrap_text=True)
        if i == 15:
            ws.row_dimensions[i].height = 44


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "口コミプレゼント台帳.xlsx"
    entries = []
    if len(sys.argv) > 2:
        with open(sys.argv[2], encoding="utf-8") as fh:
            entries = json.load(fh)

    wb = Workbook()
    ledger = wb.active
    ledger.title = "口コミ台帳"
    build_ledger(ledger, entries)
    build_summary(wb.create_sheet("月別集計"), entries[0]["month"] if entries else "2026-09")
    build_guide(wb.create_sheet("使い方"))
    wb.save(out)
    print(f"saved: {out} ({len(entries)} 件)")


if __name__ == "__main__":
    main()
