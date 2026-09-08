# -*- coding: utf-8 -*-
"""プレオルソ発注リスト（Excel）を生成するスクリプト。

使い方:
    python tools/make_preortho_order_list.py [出力先.xlsx]

既定の出力先は templates/preortho_order_list.xlsx。
選択肢（サイズ・タイプ・色・硬さ・進捗）は下部の MASTER を書き換えれば変更できる。
"""

import datetime
import sys

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation

FONT = "Meiryo"

# --- 配色 ---------------------------------------------------------------
TEAL_DARK = "115E69"   # タイトル帯
TEAL = "17808F"        # 見出し行
TEAL_PALE = "D7EBEF"   # 患者情報グループ
PINK_PALE = "FBDCE6"   # 装置仕様グループ
PINK_TEXT = "8E3B5B"
GREEN_PALE = "D8EBD5"  # 進捗グループ
GREEN_TEXT = "2F6B3A"
CREAM_PALE = "FCEBCF"  # 備考グループ
CREAM_TEXT = "8A6116"
BAND = "F3F9FA"        # 縞模様（偶数行）
NOTE_FILL = "FFF9EC"   # 使い方ボックス
NOTE_TEXT = "6B5B3E"
DONE_FILL = "C9E7C6"   # 「済」
DONE_TEXT = "1E6B3A"
TODO_FILL = "FDE7C7"   # 「未」
TODO_TEXT = "8A5A16"
ALERT_FILL = "FFC7CE"  # ロング＋ソフトの警告

# 発注時に選ぶ項目。院内の取り扱いに合わせて自由に増減してよい。
# 硬さは「ハード」を先頭に置くこと（サイズが「ロング」のときはハードのみ選べる仕組みのため）。
MASTER = {
    "サイズ": ["SS", "S", "ロング"],
    "タイプ": [1, 2, 3],
    "色": ["ピンク", "ブルー", "イエロー"],
    "硬さ": ["ハード", "ソフト"],
    "進捗": ["済", "未"],
}
LONG_SIZE = "ロング"  # この値を選んだ行は硬さがハード固定になる
DONE, TODO = MASTER["進捗"]

HEADERS = ["日付", "氏名", "サイズ", "タイプ", "色", "硬さ", "納品済み", "お渡し済み", "備考"]
WIDTHS = [14, 20, 10, 8, 12, 10, 12, 12, 48]
# 見出しの上に置くグループ帯：(表示名, 開始列, 終了列, 背景色, 文字色)
GROUPS = [
    ("患者情報", 1, 2, TEAL_PALE, TEAL_DARK),
    ("装置仕様", 3, 6, PINK_PALE, PINK_TEXT),
    ("進捗", 7, 8, GREEN_PALE, GREEN_TEXT),
    ("その他", 9, 9, CREAM_PALE, CREAM_TEXT),
]
# 各列に割り当てるプルダウン（MASTER のキー → 列文字）
DROPDOWNS = {"サイズ": ["C"], "タイプ": ["D"], "色": ["E"], "硬さ": ["F"], "進捗": ["G", "H"]}
STATUS_COLUMNS = DROPDOWNS["進捗"]
GROUP_EDGE_COLUMNS = (3, 7, 9)  # 縦の区切り線を引く列
ROWS = 200  # 入力できる行数

MASTER_HEADER_ROW = 4
MASTER_FIRST_ROW = MASTER_HEADER_ROW + 1
NOTE_FIRST_ROW = 4
NOTE_COUNT = 4
GROUP_ROW = NOTE_FIRST_ROW + NOTE_COUNT + 1
HEADER_ROW = GROUP_ROW + 1
FIRST_ROW = HEADER_ROW + 1
LAST_ROW = HEADER_ROW + ROWS

NOTES = [
    f"入力は{FIRST_ROW}行目から。色の付いたセルに1件1行で入力します。",
    "サイズ・タイプ・色・硬さはセルを選ぶとプルダウンから選べます。",
    f"納品済み・お渡し済みは「{DONE}」で緑、「{TODO}」で黄色に変わります。",
    f"サイズが「{LONG_SIZE}」の行は硬さが「ハード」のみ。選択肢は「マスタ」シートで変更できます。",
]
assert len(NOTES) == NOTE_COUNT

HAIR = Side(style="hair", color="BFD4D8")
THIN = Side(style="thin", color="9FC3CA")
MEDIUM = Side(style="medium", color=TEAL)


def cell_border(top=HAIR, bottom=HAIR, left=HAIR, right=HAIR):
    return Border(top=top, bottom=bottom, left=left, right=right)


def list_name(field):
    return f"{field}_リスト"


def add_defined_names(wb):
    """プルダウンの参照先を名前で定義する。

    Excel は「別シートを直接参照する入力規則」を独自拡張として保存し直すため、
    openpyxl で開くと消えてしまう。名前経由にしておくと通常の入力規則のまま残る。
    """
    for idx, (field, values) in enumerate(MASTER.items(), start=1):
        letter = get_column_letter(idx)
        last = MASTER_FIRST_ROW + len(values) - 1
        wb.defined_names.add(
            DefinedName(
                list_name(field),
                attr_text=f"マスタ!${letter}${MASTER_FIRST_ROW}:${letter}${last}",
            )
        )
    hard_col = get_column_letter(list(MASTER).index("硬さ") + 1)
    wb.defined_names.add(
        DefinedName(
            "硬さ_ロング用",
            attr_text=f"マスタ!${hard_col}${MASTER_FIRST_ROW}",
        )
    )


def build_master(wb):
    ws = wb.create_sheet("マスタ")
    ws["A1"] = "選択肢マスタ"
    ws["A1"].font = Font(name=FONT, size=13, bold=True, color=TEAL_DARK)
    ws["A2"] = "この表を編集すると「発注リスト」のプルダウンに反映されます。"
    ws["A2"].font = Font(name=FONT, size=10, color="595959")

    for col, (name, values) in enumerate(MASTER.items(), start=1):
        letter = get_column_letter(col)
        head = ws.cell(row=MASTER_HEADER_ROW, column=col, value=name)
        head.font = Font(name=FONT, size=11, bold=True, color="FFFFFF")
        head.fill = PatternFill("solid", fgColor=TEAL)
        head.alignment = Alignment(horizontal="center", vertical="center")
        head.border = cell_border(bottom=MEDIUM)
        for i, value in enumerate(values, start=MASTER_FIRST_ROW):
            c = ws.cell(row=i, column=col, value=value)
            c.font = Font(name=FONT, size=11)
            c.alignment = Alignment(horizontal="center")
            c.border = cell_border(left=THIN, right=THIN, bottom=THIN)
            if (i - MASTER_HEADER_ROW) % 2 == 0:
                c.fill = PatternFill("solid", fgColor=BAND)
        ws.column_dimensions[letter].width = 16
    ws.row_dimensions[MASTER_HEADER_ROW].height = 20

    note_row = MASTER_FIRST_ROW + max(len(v) for v in MASTER.values()) + 1
    note = ws.cell(
        row=note_row,
        column=1,
        value=f"※ サイズが「{LONG_SIZE}」の場合、硬さは「{MASTER['硬さ'][0]}」のみ選べます。"
        "硬さの列は「ハード」を必ず先頭にしてください。",
    )
    note.font = Font(name=FONT, size=10, color=NOTE_TEXT)
    note.fill = PatternFill("solid", fgColor=NOTE_FILL)
    ws.merge_cells(start_row=note_row, start_column=1, end_row=note_row, end_column=len(MASTER))
    ws.sheet_view.showGridLines = False
    return ws


def build_sheet(wb):
    ws = wb.create_sheet("発注リスト", 0)
    ncols = len(HEADERS)
    last_letter = get_column_letter(ncols)

    for col, width in enumerate(WIDTHS, start=1):
        ws.column_dimensions[get_column_letter(col)].width = width

    # --- タイトル帯（1〜2行目）---
    ws.merge_cells(f"A1:{last_letter}1")
    ws.merge_cells(f"A2:{last_letter}2")
    title = ws["A1"]
    title.value = "プレオルソ 発注リスト"
    title.font = Font(name=FONT, size=16, bold=True, color="FFFFFF")
    title.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    subtitle = ws["A2"]
    subtitle.value = "博多ステラ歯科　業者発注用"
    subtitle.font = Font(name=FONT, size=10, color="CFE7EB")
    subtitle.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    for row in (1, 2):
        for col in range(1, ncols + 1):
            ws.cell(row=row, column=col).fill = PatternFill("solid", fgColor=TEAL_DARK)
    ws.row_dimensions[1].height = 30
    ws.row_dimensions[2].height = 18
    ws.row_dimensions[3].height = 7  # 余白

    # --- 使い方ボックス（1行1項目で短く）---
    for i, text in enumerate(NOTES):
        row = NOTE_FIRST_ROW + i
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncols)
        cell = ws.cell(row=row, column=1, value=f"▶  {text}")
        cell.font = Font(name=FONT, size=10, color=NOTE_TEXT)
        cell.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        for col in range(1, ncols + 1):
            target = ws.cell(row=row, column=col)
            target.fill = PatternFill("solid", fgColor=NOTE_FILL)
            target.border = Border(
                left=Side(style="thick", color="E8B84B") if col == 1 else None,
                top=Side(style="hair", color="E7D5AE") if i == 0 else None,
                bottom=Side(style="hair", color="E7D5AE") if i == len(NOTES) - 1 else None,
            )
        ws.row_dimensions[row].height = 19
    ws.row_dimensions[NOTE_FIRST_ROW + len(NOTES)].height = 9  # 余白

    # --- グループ帯 ---
    for name, start, end, fill, color in GROUPS:
        if end > start:
            ws.merge_cells(start_row=GROUP_ROW, start_column=start, end_row=GROUP_ROW, end_column=end)
        cell = ws.cell(row=GROUP_ROW, column=start, value=name)
        cell.font = Font(name=FONT, size=10, bold=True, color=color)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        for col in range(start, end + 1):
            target = ws.cell(row=GROUP_ROW, column=col)
            target.fill = PatternFill("solid", fgColor=fill)
            target.border = Border(
                left=Side(style="thin", color="FFFFFF") if col == start else None,
                right=Side(style="thin", color="FFFFFF") if col == end else None,
            )
    ws.row_dimensions[GROUP_ROW].height = 18

    # --- 見出し行 ---
    for col, title_text in enumerate(HEADERS, start=1):
        cell = ws.cell(row=HEADER_ROW, column=col, value=title_text)
        cell.font = Font(name=FONT, size=11, bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=TEAL)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = Border(
            bottom=MEDIUM,
            left=Side(style="thin", color="FFFFFF"),
            right=Side(style="thin", color="FFFFFF"),
        )
    ws.row_dimensions[HEADER_ROW].height = 24

    # --- 入力欄 ---
    left_aligned = (2, 9)  # 氏名・備考だけ左寄せ
    for row in range(FIRST_ROW, LAST_ROW + 1):
        banded = (row - FIRST_ROW) % 2 == 1
        for col in range(1, ncols + 1):
            cell = ws.cell(row=row, column=col)
            cell.font = Font(name=FONT, size=11)
            cell.alignment = Alignment(
                horizontal="left" if col in left_aligned else "center",
                vertical="center",
                indent=1 if col in left_aligned else 0,
            )
            cell.border = Border(
                top=HAIR,
                bottom=HAIR,
                left=THIN if col in GROUP_EDGE_COLUMNS else HAIR,
                right=THIN if col == ncols else HAIR,
            )
            if banded:
                cell.fill = PatternFill("solid", fgColor=BAND)
        ws.cell(row=row, column=1).number_format = "yyyy/mm/dd"
        ws.row_dimensions[row].height = 19

    # --- プルダウン（名前定義を参照）---
    for field in MASTER:
        if field == "硬さ":
            # サイズが「ロング」の行は「ハード」だけを選択肢にする
            source = f'=IF($C{FIRST_ROW}="{LONG_SIZE}",硬さ_ロング用,{list_name(field)})'
            message = f"サイズが「{LONG_SIZE}」の場合、硬さは「{MASTER['硬さ'][0]}」のみです。"
        else:
            source = f"={list_name(field)}"
            message = f"{field}は「マスタ」シートの選択肢から選んでください。"
        dv = DataValidation(type="list", formula1=source, allow_blank=True, showDropDown=False)
        dv.errorTitle = "入力できない値です"
        dv.error = message
        ws.add_data_validation(dv)
        for letter in DROPDOWNS[field]:
            dv.add(f"{letter}{FIRST_ROW}:{letter}{LAST_ROW}")

    # --- 納品済み・お渡し済みの色分け ---
    for letter in STATUS_COLUMNS:
        target = f"{letter}{FIRST_ROW}:{letter}{LAST_ROW}"
        ws.conditional_formatting.add(
            target,
            CellIsRule(
                operator="equal",
                formula=[f'"{DONE}"'],
                fill=PatternFill("solid", fgColor=DONE_FILL),
                font=Font(name=FONT, size=11, bold=True, color=DONE_TEXT),
            ),
        )
        ws.conditional_formatting.add(
            target,
            CellIsRule(
                operator="equal",
                formula=[f'"{TODO}"'],
                fill=PatternFill("solid", fgColor=TODO_FILL),
                font=Font(name=FONT, size=11, color=TODO_TEXT),
            ),
        )

    # --- 念のための保険：ロング＋ソフトの組み合わせが残っていたら赤く塗る ---
    ws.conditional_formatting.add(
        f"F{FIRST_ROW}:F{LAST_ROW}",
        FormulaRule(
            formula=[
                f'AND($C{FIRST_ROW}="{LONG_SIZE}",$F{FIRST_ROW}<>"",'
                f'$F{FIRST_ROW}<>"{MASTER["硬さ"][0]}")'
            ],
            fill=PatternFill("solid", fgColor=ALERT_FILL),
            font=Font(name=FONT, size=11, bold=True, color="9C0006"),
            stopIfTrue=False,
        ),
    )

    # --- 記入例（実際の発注を入れるときは上書きする）---
    example = [
        datetime.date(2026, 4, 1),
        "博多 太郎",
        "SS",
        2,
        "ピンク",
        "ソフト",
        DONE,
        TODO,
        "記入例：この行は上書きしてください",
    ]
    for col, value in enumerate(example, start=1):
        cell = ws.cell(row=FIRST_ROW, column=col, value=value)
        cell.font = Font(name=FONT, size=11, italic=True, color="9AA5A8")
    ws.cell(row=FIRST_ROW, column=1).number_format = "yyyy/mm/dd"

    # 表の右側の未使用列は非表示にして、白い余白が出ないようにする
    ws.column_dimensions.group(
        get_column_letter(ncols + 1), "XFD", outline_level=0, hidden=True
    )

    ws.freeze_panes = f"A{FIRST_ROW}"
    ws.auto_filter.ref = f"A{HEADER_ROW}:{last_letter}{LAST_ROW}"
    ws.sheet_view.showGridLines = False
    ws.print_options.horizontalCentered = True
    ws.print_title_rows = f"{HEADER_ROW}:{HEADER_ROW}"
    return ws


def build_workbook():
    wb = Workbook()
    wb.remove(wb.active)
    build_master(wb)
    build_sheet(wb)
    add_defined_names(wb)
    return wb


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "templates/preortho_order_list.xlsx"
    build_workbook().save(out)
    print(f"saved: {out}")


if __name__ == "__main__":
    main()
