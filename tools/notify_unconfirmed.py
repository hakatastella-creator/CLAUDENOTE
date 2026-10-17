#!/usr/bin/env python3
"""受付報告アプリの未確認を数えて、残っていれば Gmail で知らせる。

「ステラ受付報告」(claude.ai のアーティファクト) に保存された app-state の JSON を
受け取り、院長がまだ確認していない受付からの報告を一覧にしてメールする。
0 件のときは何も送らない。

使い方:
    python3 tools/notify_unconfirmed.py state.json
    cat state.json | python3 tools/notify_unconfirmed.py -

必要な環境変数（毎朝の返信下書き生成と同じもの）:
    GMAIL_CLIENT_ID / GMAIL_CLIENT_SECRET / GMAIL_REFRESH_TOKEN
任意:
    NOTIFY_TO_EMAIL   宛先。既定は hakata.stella@gmail.com
    APP_URL           本文に入れるアプリのURL

--dry-run を付けると送信せず本文だけ表示する（認証情報なしで確認できる）。
"""

import argparse
import base64
import datetime
import json
import os
import sys
from email.mime.text import MIMEText

DEFAULT_TO = "hakata.stella@gmail.com"
DEFAULT_APP_URL = "https://claude.ai/artifact/St9NAWan1niW27azwX2HRK"

# アプリ側の MEMBERS と対応。増やしたときはここも足す。
NAMES = {"inchou": "院長", "abiru": "阿比留", "katayama": "片山"}
DIRECTOR = "inchou"

JST = datetime.timezone(datetime.timedelta(hours=9))
WEEK = ["月", "火", "水", "木", "金", "土", "日"]
BODY_LIMIT = 60


def unconfirmed(state):
    """院長がまだ確認していない、受付からの報告を古い順で返す。"""
    out = []
    for p in state.get("posts", []):
        if not isinstance(p, dict):
            continue
        if p.get("ack"):
            continue
        if p.get("by") == DIRECTOR:
            continue          # 院長自身の投稿は対象外
        out.append(p)
    out.sort(key=lambda p: p.get("createdAt") or 0)
    return out


def jst_date(ms):
    if not ms:
        return "日付なし"
    d = datetime.datetime.fromtimestamp(ms / 1000, JST)
    return "%d/%d(%s)" % (d.month, d.day, WEEK[d.weekday()])


def one_line(post):
    name = NAMES.get(post.get("by") or "", "（不明）")
    text = " ".join((post.get("text") or "").split())
    if len(text) > BODY_LIMIT:
        text = text[:BODY_LIMIT] + "…"
    return "%s %s: %s" % (jst_date(post.get("createdAt")), name, text)


def build_message(posts, app_url):
    lines = ["院長がまだ確認していない報告が %d件 あります。" % len(posts), ""]
    lines += [one_line(p) for p in posts]
    lines += [
        "",
        "確認する → " + app_url,
        "（カードの「確認しました」を押すと、受付の画面に確認済みと出ます）",
    ]
    return "📋 受付から 未確認%d件｜確認おねがいします" % len(posts), "\n".join(lines)


def send(subject, body, to_addr):
    from google.auth.transport.requests import Request  # noqa: F401
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials(
        None,
        refresh_token=os.environ["GMAIL_REFRESH_TOKEN"],
        client_id=os.environ["GMAIL_CLIENT_ID"],
        client_secret=os.environ["GMAIL_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/gmail.modify"],
    )
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    msg = MIMEText(body, "plain", "utf-8")
    msg["To"] = to_addr
    msg["Subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("state", help="app-state の JSON ファイル。- で標準入力")
    ap.add_argument("--dry-run", action="store_true", help="送らずに本文を表示する")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.state == "-" else open(args.state, encoding="utf-8").read()
    state = json.loads(raw)

    posts = unconfirmed(state)
    if not posts:
        print("未確認0件、送信なし")
        return 0

    app_url = os.environ.get("APP_URL", DEFAULT_APP_URL)
    subject, body = build_message(posts, app_url)

    if args.dry_run:
        print("To: " + os.environ.get("NOTIFY_TO_EMAIL", DEFAULT_TO))
        print("Subject: " + subject)
        print()
        print(body)
        return 0

    missing = [k for k in ("GMAIL_CLIENT_ID", "GMAIL_CLIENT_SECRET", "GMAIL_REFRESH_TOKEN")
               if not os.environ.get(k)]
    if missing:
        print("環境変数が足りないので送信しません: " + ", ".join(missing), file=sys.stderr)
        return 2

    send(subject, body, os.environ.get("NOTIFY_TO_EMAIL", DEFAULT_TO))
    print("未確認%d件、メール送信済み" % len(posts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
