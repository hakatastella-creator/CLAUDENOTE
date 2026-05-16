import os

GMAIL_CLIENT_ID = os.environ["GMAIL_CLIENT_ID"]
GMAIL_CLIENT_SECRET = os.environ["GMAIL_CLIENT_SECRET"]
GMAIL_REFRESH_TOKEN = os.environ["GMAIL_REFRESH_TOKEN"]
GMAIL_USER = os.environ.get("GMAIL_USER", "me")

CHATWORK_API_TOKEN = os.environ["CHATWORK_API_TOKEN"]

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")

SUMMARY_TO_EMAIL = os.environ["SUMMARY_TO_EMAIL"]

LOOKBACK_HOURS = int(os.environ.get("LOOKBACK_HOURS", "24"))
HISTORY_LIMIT = int(os.environ.get("HISTORY_LIMIT", "10"))

AUTO_SENDER_KEYWORDS = [
    "noreply", "no-reply", "no_reply", "donotreply", "do-not-reply",
    "notification", "notifications", "info@", "news@", "mailer@",
    "support@", "auto@", "alert@", "system@",
]
