import os

GMAIL_CLIENT_ID = os.environ.get("GMAIL_CLIENT_ID", "")
GMAIL_CLIENT_SECRET = os.environ.get("GMAIL_CLIENT_SECRET", "")
GMAIL_REFRESH_TOKEN = os.environ.get("GMAIL_REFRESH_TOKEN", "")
GMAIL_USER = os.environ.get("GMAIL_USER", "me")

CHATWORK_API_TOKEN = os.environ.get("CHATWORK_API_TOKEN", "")

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")

SUMMARY_TO_EMAIL = os.environ.get("SUMMARY_TO_EMAIL", "")

LOOKBACK_HOURS = int(os.environ.get("LOOKBACK_HOURS", "24"))
HISTORY_LIMIT = int(os.environ.get("HISTORY_LIMIT", "10"))

AUTO_SENDER_KEYWORDS = [
    "noreply", "no-reply", "no_reply", "donotreply", "do-not-reply",
    "notification", "notifications", "info@", "news@", "mailer@",
    "support@", "auto@", "alert@", "system@",
]


def require(*names):
    """処理に必要な環境変数がそろっているか確認する。

    ジョブごとに必要なものが違うため、モジュール読み込み時ではなく
    実行の入口で呼ぶ。
    """
    missing = [n for n in names if not globals().get(n)]
    if missing:
        raise SystemExit("[ERR] 環境変数が未設定です: " + ", ".join(missing))
