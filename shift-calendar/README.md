# シフトカレンダー作成

アポツールのシフト表CSVを、月ごとのシフトカレンダー（Excel）に変換します。

```
pip install openpyxl
python3 make_calendar.py shift_YYYYMMDD.csv            # CSVと同じ場所に「YYYY年M月シフト表.xlsx」
python3 make_calendar.py shift_YYYYMMDD.csv 出力.xlsx
```

- `template.xlsx` … 見た目（列幅・罫線・曜日の見出し）だけのひな形。名前は入っていません
- 作成後に Excel を読み戻して CSV と照合し、食い違いがあればエラーで止まります
- 変換ルールは [`.claude/skills/shift-calendar/SKILL.md`](../.claude/skills/shift-calendar/SKILL.md) を参照
