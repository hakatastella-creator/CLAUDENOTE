"""チャットに書かれた一文から、タスクの中身を読み取る。

書き方の例:
    物販コーナーのPOPを作り直す
    #院長 自費メニューの説明用紙を作る 8/25まで
    在庫チェック #15分
    明日まで リコールはがきを出す
    50枚くらい            ← 2行目以降はメモ
"""

import re
from datetime import date, timedelta

KIND_TAGS = {
    "院長": "院長から", "院長から": "院長から", "先生": "院長から",
    "受付": "受付から", "自分": "受付から",
    "定例": "定例", "毎月": "定例",
}
SPAN_TAGS = {
    "5分": "5分", "5": "5分",
    "15分": "15分", "15": "15分",
    "30分": "30分以上", "30分以上": "30分以上", "30": "30分以上",
}
DEFAULT_KIND = "受付から"

TAG_RE = re.compile(r"[#＃]([^\s#＃]+)")


def _extract_due(text, today):
    """期限らしい表記を1つ探し、(日付, 元の文字列) を返す。"""
    m = re.search(r"(今日|本日)(まで|中)?", text)
    if m:
        return today, m.group(0)

    m = re.search(r"明後日(まで|中)?", text)
    if m:
        return today + timedelta(days=2), m.group(0)

    m = re.search(r"明日(まで|中)?", text)
    if m:
        return today + timedelta(days=1), m.group(0)

    m = re.search(r"(\d{1,2})[/月](\d{1,2})日?(まで)?", text)
    if m:
        month, day = int(m.group(1)), int(m.group(2))
        try:
            due = date(today.year, month, day)
        except ValueError:
            return None, ""
        # 大きく過ぎた日付は翌年の指定とみなす（12月に「1/5」と書く場合）
        if due < today - timedelta(days=30):
            due = due.replace(year=today.year + 1)
        return due, m.group(0)

    m = re.search(r"(\d{1,2})日(まで)?", text)
    if m:
        day = int(m.group(1))
        try:
            due = date(today.year, today.month, day)
        except ValueError:
            return None, ""
        if due < today:
            due = (due.replace(day=1) + timedelta(days=32)).replace(day=day)
        return due, m.group(0)

    return None, ""


def parse(text, today=None):
    """1通のメッセージを {kind, task, due, span, note} に変換する。"""
    today = today or date.today()
    lines = text.replace("\r\n", "\n").split("\n")
    first = lines[0]
    note = "\n".join(lines[1:]).strip()

    kind = DEFAULT_KIND
    span = ""

    def _tag(match):
        nonlocal kind, span
        tag = match.group(1)
        if tag in KIND_TAGS:
            kind = KIND_TAGS[tag]
            return ""
        if tag in SPAN_TAGS:
            span = SPAN_TAGS[tag]
            return ""
        return match.group(0)

    first = TAG_RE.sub(_tag, first)

    due, matched = _extract_due(first, today)
    if matched:
        first = first.replace(matched, "", 1)

    task = re.sub(r"\s+", " ", first).strip()
    return {
        "kind": kind,
        "task": task,
        "due": due.isoformat() if due else "",
        "span": span,
        "note": note,
    }
