"""Chatworkのマイチャットに送った内容を、TODOリストに取り込む。

マイチャットの新着を読み、1通を1件として data/todo.csv に追記する。
「一覧」「完了 12」などのコマンドにも応答する。
GitHub Actions から数分おきに実行される想定。
"""

import re
import subprocess
import sys
from datetime import date, datetime, timezone, timedelta

import config
import chatwork_client
import todo_store
from todo_parser import parse

JST = timezone(timedelta(hours=9))
BOT_MARK = "[info][title]受付TODO[/title]"
MAX_SEEN = 300

HELP = """送りたいことをそのまま書いて送ってください。1通が1件になります。

【書き方】
・そのまま送る → 受付からのタスクとして登録
・#院長 を付ける → 院長からの依頼
・#5分 #15分 #30分 → 空き時間の目安
・「8/25まで」「明日まで」 → 期限
・改行して2行目以降を書くと、メモになります

【コマンド】
一覧 … 未完了を表示
完了 12 … 番号の件を完了に
戻す 12 … 未完了に戻す
削除 12 … 削除
ヘルプ … この案内"""


def _today():
    return datetime.now(JST).date()


def _fmt_due(value):
    if not value:
        return ""
    try:
        return date.fromisoformat(value).strftime("%-m/%-d")
    except ValueError:
        return value


def _describe(row):
    tail = []
    if row.get("kind") and row["kind"] != "受付から":
        tail.append(row["kind"])
    if row.get("due"):
        tail.append(_fmt_due(row["due"]) + "まで")
    if row.get("span"):
        tail.append(row["span"])
    suffix = "（" + "・".join(tail) + "）" if tail else ""
    return f"#{row['id']} {row['task']}{suffix}"


def list_text(rows):
    pending = [r for r in rows if r.get("done") != "1"]
    if not pending:
        return "未完了はありません。"
    lines = [_describe(r) for r in pending[:30]]
    more = f"\n…ほか {len(pending) - 30}件" if len(pending) > 30 else ""
    return f"未完了 {len(pending)}件\n" + "\n".join(lines) + more


def handle_message(text, rows, today=None):
    """1通を処理して、返信に載せる1行を返す。(返信文, 変更があったか)"""
    today = today or _today()
    body = text.strip()
    if not body:
        return "", False

    head = body.split()[0] if body.split() else ""
    if re.fullmatch(r"(ヘルプ|使い方|help)", head, re.IGNORECASE):
        return HELP, False
    if re.fullmatch(r"(一覧|リスト|list|todo)", head, re.IGNORECASE):
        return list_text(rows), False

    m = re.fullmatch(r"(完了|済|done|戻す|取消|削除)\s*[#＃]?\s*(\d+)", body, re.IGNORECASE)
    if m:
        command, task_id = m.group(1), m.group(2)
        row = todo_store.find(rows, task_id)
        if not row:
            return f"#{task_id} は見つかりませんでした。「一覧」で番号を確認してください。", False
        if re.fullmatch(r"(完了|済|done)", command, re.IGNORECASE):
            row["done"] = "1"
            row["done_at"] = datetime.now(JST).isoformat(timespec="minutes")
            return f"完了にしました：#{row['id']} {row['task']}", True
        if command in ("戻す", "取消"):
            row["done"] = "0"
            row["done_at"] = ""
            return f"未完了に戻しました：#{row['id']} {row['task']}", True
        rows.remove(row)
        return f"削除しました：#{task_id} {row['task']}", True

    parsed = parse(body, today)
    if not parsed["task"]:
        return "", False
    row = {
        "id": str(todo_store.next_id(rows)),
        "created_at": datetime.now(JST).isoformat(timespec="minutes"),
        "done": "0",
        "done_at": "",
        **parsed,
    }
    rows.append(row)
    return "登録しました：" + _describe(row), True


def _reply(room_id, lines):
    body = BOT_MARK + "\n".join(lines) + "[/info]"
    chatwork_client.send_message(room_id, body)


def main():
    config.require("CHATWORK_API_TOKEN")

    room_id = chatwork_client.my_chat_room_id()
    messages = sorted(chatwork_client.fetch_recent_messages(room_id),
                      key=lambda m: m["send_time"])
    state = todo_store.load_state()
    seen = set(state.get("seen", []))

    if not state:
        # 初回は過去のやり取りを取り込まない
        todo_store.save_state({"seen": [m["message_id"] for m in messages][-MAX_SEEN:]})
        _reply(room_id, ["受付TODOを開始しました。", "", HELP])
        print("[OK] 初回セットアップ完了（既存メッセージは取り込みませんでした）")
        return

    rows = todo_store.load()
    replies = []
    changed = False
    processed = []

    for msg in messages:
        mid = msg["message_id"]
        if mid in seen:
            continue
        processed.append(mid)
        body = msg.get("body", "")
        if body.startswith(BOT_MARK):
            continue
        line, did_change = handle_message(body, rows, _today())
        if line:
            replies.append(line)
        changed = changed or did_change

    if not processed:
        print("[OK] 新着なし")
        return

    seen.update(processed)
    todo_store.save_state({"seen": [m["message_id"] for m in messages][-MAX_SEEN:]})

    if changed:
        todo_store.save(rows)
        _rebuild_excel()

    if replies:
        _reply(room_id, replies)

    print(f"[OK] {len(processed)}件を処理しました")
    for line in replies:
        print("  " + line.replace("\n", " / ")[:120])


def _rebuild_excel():
    script = str((todo_store.DATA_DIR.parent / "tools" / "build_todo_xlsx.py"))
    try:
        subprocess.run([sys.executable, script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[WARN] エクセルの生成に失敗しました: {e}")


if __name__ == "__main__":
    main()
