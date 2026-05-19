"""未返信ダッシュボード（ローカル起動）

Chrome 拡張から POST されたスキャン結果を JSON ファイルに保存し、
12時間以上未返信の会話を一覧表示する。
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request

JST = timezone.utc  # 表示用は JS 側で localize するため UTC 保持で十分

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"
DATA_FILE = DATA_DIR / "scan.json"
THRESHOLD_HOURS = float(os.environ.get("STELLA_UNREPLIED_THRESHOLD_HOURS", "12"))

app = Flask(__name__)


@app.after_request
def add_cors(response):
    # Chrome 拡張からの POST を許可。localhost のみで起動するので公開リスクなし。
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


def _load() -> dict:
    if not DATA_FILE.exists():
        return {"scanned_at": None, "conversations": []}
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def _save(payload: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", threshold_hours=THRESHOLD_HOURS)


@app.route("/api/data", methods=["GET"])
def api_data():
    return jsonify(_load())


@app.route("/scan", methods=["POST", "OPTIONS"])
def scan():
    if request.method == "OPTIONS":
        return ("", 204)
    body = request.get_json(force=True, silent=True) or {}
    conversations = body.get("conversations", [])
    payload = {
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "conversations": conversations,
    }
    _save(payload)
    return jsonify({"ok": True, "count": len(conversations)})


def main():
    port = int(os.environ.get("STELLA_DASHBOARD_PORT", "8765"))
    # 127.0.0.1 にバインドして外部からは触れないようにする
    app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()
