"""博多ステラ歯科 MEO 口コミ監視 & 返信ドラフト生成スクリプト.

GitHub Actions から定期実行される想定。

処理の流れ:
  1. Gmail を IMAP で開き、未処理の Google Business Profile 口コミ通知を取得
  2. メール本文から評価・投稿者名・本文を抽出
  3. tone_examples.md に書かれた過去の返信例をプロンプトに混ぜて Claude に渡し、返信ドラフトを生成
  4. Chatwork にドラフトを投稿
  5. 処理済みメールに Gmail ラベル "MEO/Processed" を付与し、再処理を防ぐ
"""

from __future__ import annotations

import email
import imaplib
import os
import re
import sys
from dataclasses import dataclass
from email.header import decode_header
from email.message import Message
from pathlib import Path

import anthropic
import requests
from bs4 import BeautifulSoup

GMAIL_HOST = "imap.gmail.com"
PROCESSED_LABEL = "MEO/Processed"

# Google からの口コミ通知メールの差出人。仕様変更で増えがちなので複数許容。
REVIEW_SENDERS = (
    "business.profile-noreply@google.com",
    "noreply-businessprofile@google.com",
    "noreply@google.com",
)

# 件名に含まれるキーワード（日英両対応）
REVIEW_SUBJECT_KEYWORDS = (
    "クチコミ",
    "口コミ",
    "レビュー",
    "new review",
    "left a review",
)

REPO_ROOT = Path(__file__).resolve().parent
TONE_EXAMPLES_PATH = REPO_ROOT / "tone_examples.md"
PROMPT_PATH = REPO_ROOT / "prompt.md"


@dataclass
class Review:
    reviewer: str
    rating: int | None
    body: str
    raw_excerpt: str


def env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        sys.exit(f"環境変数 {name} が未設定です")
    return value


def decode_mime(value: str | None) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    out = []
    for text, charset in parts:
        if isinstance(text, bytes):
            out.append(text.decode(charset or "utf-8", errors="replace"))
        else:
            out.append(text)
    return "".join(out)


def extract_body(msg: Message) -> str:
    """text/plain を優先し、無ければ text/html を平文化して返す。"""
    plain: str | None = None
    html: str | None = None
    for part in msg.walk():
        ctype = part.get_content_type()
        if part.get("Content-Disposition", "").startswith("attachment"):
            continue
        charset = part.get_content_charset() or "utf-8"
        try:
            payload = part.get_payload(decode=True)
        except Exception:
            continue
        if payload is None:
            continue
        text = payload.decode(charset, errors="replace")
        if ctype == "text/plain" and plain is None:
            plain = text
        elif ctype == "text/html" and html is None:
            html = text
    if plain:
        return plain
    if html:
        return BeautifulSoup(html, "html.parser").get_text("\n")
    return ""


def looks_like_review(msg: Message) -> bool:
    sender = decode_mime(msg.get("From", "")).lower()
    if not any(s in sender for s in REVIEW_SENDERS):
        return False
    subject = decode_mime(msg.get("Subject", "")).lower()
    return any(k.lower() in subject for k in REVIEW_SUBJECT_KEYWORDS)


def parse_review(body: str) -> Review:
    """通知メール本文から評価・投稿者・本文を抽出する。

    Google のメールは英日両方で来うる上にフォーマットが微妙に変わるので、
    完璧な抽出は諦めて、最低限「本文全体」だけは Claude に渡せるようにする。
    """
    rating: int | None = None
    m = re.search(r"([1-5])\s*(?:つ星|stars?|★)", body, re.IGNORECASE)
    if m:
        rating = int(m.group(1))
    else:
        stars = re.search(r"(★+)", body)
        if stars:
            rating = len(stars.group(1))

    reviewer = "（投稿者名不明）"
    m = re.search(r"(.+?)\s*さん(?:から|が)", body)
    if m:
        reviewer = m.group(1).strip().splitlines()[-1]
    else:
        m = re.search(r"^From:\s*(.+)$", body, re.MULTILINE)
        if m:
            reviewer = m.group(1).strip()

    # メール末尾の Google フッターを除去し、見出し的な行も削る
    cleaned = re.sub(r"https?://\S+", "", body)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()

    return Review(
        reviewer=reviewer,
        rating=rating,
        body=cleaned,
        raw_excerpt=body[:2000],
    )


def load_tone_examples() -> str:
    if TONE_EXAMPLES_PATH.exists():
        return TONE_EXAMPLES_PATH.read_text(encoding="utf-8")
    return "（過去の返信例は未登録です。標準的な丁寧調で生成してください。）"


def load_prompt_template() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def generate_draft(review: Review) -> str:
    client = anthropic.Anthropic(api_key=env("ANTHROPIC_API_KEY"))
    system_prompt = load_prompt_template()
    tone = load_tone_examples()

    user_message = (
        f"# 過去の返信例（トーンの参考）\n{tone}\n\n"
        f"# 受信した口コミ\n"
        f"- 投稿者: {review.reviewer}\n"
        f"- 評価: {review.rating if review.rating else '不明'}\n"
        f"- 本文抜粋:\n{review.body}\n\n"
        "上記に対する返信ドラフトを1案生成してください。"
        "返信文のみを出力し、前置きや解説は不要です。"
    )

    resp = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return "".join(block.text for block in resp.content if block.type == "text").strip()


def post_to_chatwork(review: Review, draft: str) -> None:
    token = env("CHATWORK_API_TOKEN")
    room_id = env("CHATWORK_ROOM_ID")

    rating_label = f"{'★' * review.rating}{'☆' * (5 - review.rating)}" if review.rating else "評価不明"
    body = (
        "[info][title]新着クチコミの返信ドラフト[/title]"
        f"投稿者: {review.reviewer}\n"
        f"評価: {rating_label}\n"
        "---\n"
        f"【口コミ本文】\n{review.body[:600]}\n"
        "---\n"
        f"【返信ドラフト】\n{draft}\n"
        "[/info]"
    )

    r = requests.post(
        f"https://api.chatwork.com/v2/rooms/{room_id}/messages",
        headers={"X-ChatWorkToken": token},
        data={"body": body, "self_unread": "1"},
        timeout=15,
    )
    r.raise_for_status()


def ensure_label(imap: imaplib.IMAP4_SSL, label: str) -> None:
    typ, _ = imap.create(f'"{label}"')
    # 既存ラベルなら NO が返る。それ以外は無視。
    if typ not in ("OK", "NO"):
        print(f"ラベル作成で予期せぬ応答: {typ}", file=sys.stderr)


def main() -> int:
    user = env("GMAIL_ADDRESS")
    password = env("GMAIL_APP_PASSWORD")

    with imaplib.IMAP4_SSL(GMAIL_HOST) as imap:
        imap.login(user, password)
        ensure_label(imap, PROCESSED_LABEL)
        imap.select("INBOX")

        # 直近の未処理メールだけを対象にする（過去ログを延々と処理しないため）
        typ, data = imap.search(None, "UNSEEN", f'X-GM-RAW "newer_than:7d -label:{PROCESSED_LABEL}"')
        if typ != "OK":
            print("IMAP 検索に失敗", file=sys.stderr)
            return 1

        ids = data[0].split()
        if not ids:
            print("新着クチコミ通知はありません")
            return 0

        processed = 0
        for msg_id in ids:
            typ, msg_data = imap.fetch(msg_id, "(RFC822)")
            if typ != "OK" or not msg_data or not msg_data[0]:
                continue
            msg = email.message_from_bytes(msg_data[0][1])
            if not looks_like_review(msg):
                continue

            body = extract_body(msg)
            review = parse_review(body)
            try:
                draft = generate_draft(review)
                post_to_chatwork(review, draft)
            except Exception as exc:
                print(f"処理失敗 (uid={msg_id!r}): {exc}", file=sys.stderr)
                continue

            imap.store(msg_id, "+X-GM-LABELS", PROCESSED_LABEL)
            processed += 1

        print(f"処理件数: {processed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
