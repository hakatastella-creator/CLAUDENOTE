"""TODOの保存。CSV1枚をそのまま台帳として使う。"""

import csv
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CSV_PATH = DATA_DIR / "todo.csv"
STATE_PATH = DATA_DIR / "todo_state.json"

FIELDS = ["id", "created_at", "kind", "task", "due", "span", "note", "done", "done_at"]


def load():
    if not CSV_PATH.exists():
        return []
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


def save(rows):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in FIELDS})


def next_id(rows):
    ids = [int(r["id"]) for r in rows if str(r.get("id", "")).isdigit()]
    return max(ids) + 1 if ids else 1


def find(rows, task_id):
    for row in rows:
        if str(row.get("id")) == str(task_id):
            return row
    return None


def load_state():
    if not STATE_PATH.exists():
        return {}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
