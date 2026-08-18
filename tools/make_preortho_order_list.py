# -*- coding: utf-8 -*-
"""プレオルソ発注リスト（Excel）を生成するスクリプト。

使い方:
    python tools/make_preortho_order_list.py [出力先.xlsx]

既定の出力先は templates/preortho_order_list.xlsx。
選択肢（サイズ・タイプ・色・硬さ）は下部の MASTER を書き換えれば変更できる。
"""

import datetime
import sys

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

FONT = "Meiryo"

# 発注時に選ぶ項目。院内の取り扱いに合わせて自由に増減してよい。
# 硬さは「ハード」を先頭に置くこと（サイズが「ロング」のときはハードのみ選べる仕組みのため）。
MASTER = {
    "サイズ": ["SS", "S", "ロング"],
    "タイプ": [1, 2, 3],
    "色": ["ピンク", "ブルー", "イエロー"],
    "硬さ": ["ハード", "ソフト"],
}
LONG_SIZE = "ロング"  # この値を選んだ行は硬さがハード固定になる

HEADERS = ["日付", "氏名", "サイズ", "タイプ", "色", "硬さ", "備考"]
WIDTHS = [14, 20, 10, 8, 12, 10, 32]
ROWS = 200  # 入力できる行数

THIN = Side(style="thin", color="B0B0B0")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
INPUT_FILL = PatternFill("solid", fgColor="FFFDE7")
ALERT_FILL = PatternFill("solid", fgColor="FFC7CE")


def build_master(wb):
    ws = wb.create_sheet("マスタ")
    ws["A1"] = "選択肢マスタ（この表を編集すると「発注リスト」のプルダウンに反映されます）"
    ws["A1"].font = Font(name=FONT, size=11, bold=True)
    for col, (name, values) in enumerate(MASTER.items(), start=1):
        letter = get_column_letter(col)
        cell = ws.cell(row=2, column=col, value=name)
        cell.font = Font(name=FONT, size=11, bold=True, color="FFFFFF")
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center")
        cell.border = BORDER
        for i, value in enumerate(values, start=3):
            c = ws.cell(row=i, column=col, value=value)
            c.font = Font(name=FONT, size=11)
            c.alignment = Alignment(horizontal="center")
            c.border = BORDER
        ws.column_dimensions[letter].width = 16
    note = ws.cell(
        row=3 + max(len(v) for v in MASTER.values()) + 1,
        column=1,
        value=f"※ サイズが「{LONG_SIZE}」の場合、硬さは「{MASTER['硬さ'][0]}」のみ選べます。"
        "（硬さ列は上から順に並べ、ハードを必ず先頭にしてください）",
    )
    note.font = Font(name=FONT, size=10, color="595959")
    return ws


def build_sheet(wb):
    ws = wb.create_sheet("発注リスト", 0)
    ws["A1"] = "プレオルソ 発注リスト"
    ws["A1"].font = Font(name=FONT, size=14, bold=True)
    ws["A2"] = (
        "【使い方】5行目以降に1件1行で入力します。薄い黄色のセルが入力欄です。"
        "サイズ・タイプ・色・硬さはセルを選ぶとプルダウンから選べます"
        f"（選択肢は「マスタ」シートで変更）。サイズが「{LONG_SIZE}」の行は硬さが"
        "「ハード」のみになります。5行目は記入例なので、実際の発注を入れるときは上書きしてください。"
    )
    ws["A2"].font = Font(name=FONT, size=10, color="595959")
    ws["A2"].alignment = Alignment(vertical="center", wrap_text=True)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(HEADERS))
    ws.row_dimensions[2].height = 40

    header_row = 4
    for col, (title, width) in enumerate(zip(HEADERS, WIDTHS), start=1):
        cell = ws.cell(row=header_row, column=col, value=title)
        cell.font = Font(name=FONT, size=11, bold=True, color="FFFFFF")
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = BORDER
        ws.column_dimensions[get_column_letter(col)].width = width
    ws.row_dimensions[header_row].height = 22

    first, last = header_row + 1, header_row + ROWS
    for row in range(first, last + 1):
        for col in range(1, len(HEADERS) + 1):
            cell = ws.cell(row=row, column=col)
            cell.font = Font(name=FONT, size=11)
            cell.border = BORDER
            cell.fill = INPUT_FILL
            cell.alignment = Alignment(
                horizontal="center" if col in (1, 3, 4, 5, 6) else "left",
                vertical="center",
            )
        ws.cell(row=row, column=1).number_format = "yyyy/mm/dd"

    # プルダウン（マスタシートの列を参照）
    columns = {"サイズ": "C", "タイプ": "D", "色": "E", "硬さ": "F"}
    for idx, (name, values) in enumerate(MASTER.items(), start=1):
        letter = get_column_letter(idx)
        if name == "硬さ":
            # サイズが「ロング」の行は先頭1件（ハード）だけを選択肢にする
            source = (
                f'=OFFSET(マスタ!${letter}$3,0,0,'
                f'IF($C{first}="{LONG_SIZE}",1,{len(values)}),1)'
            )
        else:
            source = f"=マスタ!${letter}$3:${letter}${2 + len(values)}"
        dv = DataValidation(type="list", formula1=source, allow_blank=True, showDropDown=False)
        dv.errorTitle = "入力できない値です"
        dv.error = (
            f"サイズが「{LONG_SIZE}」の場合、硬さは「{values[0]}」のみです。"
            if name == "硬さ"
            else f"{name}は「マスタ」シートの選択肢から選んでください。"
        )
        ws.add_data_validation(dv)
        dv.add(f"{columns[name]}{first}:{columns[name]}{last}")

    # 念のための保険：ロング＋ソフトの組み合わせが残っていたら赤く塗る
    ws.conditional_formatting.add(
        f"F{first}:F{last}",
        FormulaRule(
            formula=[f'AND($C{first}="{LONG_SIZE}",$F{first}<>"",$F{first}<>"{MASTER["硬さ"][0]}")'],
            fill=ALERT_FILL,
            stopIfTrue=False,
        ),
    )

    # 記入例（実際の発注を入れるときは上書きする）
    example = [datetime.date(2026, 4, 1), "博多 太郎", "SS", 2, "ピンク", "ソフト", "記入例：この行は上書きしてください"]
    for col, value in enumerate(example, start=1):
        cell = ws.cell(row=first, column=col, value=value)
        cell.font = Font(name=FONT, size=11, italic=True, color="808080")
    ws.cell(row=first, column=1).number_format = "yyyy/mm/dd"

    ws.freeze_panes = f"A{first}"
    ws.auto_filter.ref = f"A{header_row}:{get_column_letter(len(HEADERS))}{last}"
    ws.sheet_view.showGridLines = False
    ws.print_options.horizontalCentered = True
    return ws


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "templates/preortho_order_list.xlsx"
    wb = Workbook()
    wb.remove(wb.active)
    build_master(wb)
    build_sheet(wb)
    wb.save(out)
    print(f"saved: {out}")


if __name__ == "__main__":
    main()
