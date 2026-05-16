import sys
import traceback
from datetime import datetime

import gmail_client
import chatwork_client
from draft_generator import generate_reply
from config import LOOKBACK_HOURS, HISTORY_LIMIT, SUMMARY_TO_EMAIL


def process_gmail():
    """Generate Gmail drafts for unread personal messages."""
    log = []
    try:
        incoming = gmail_client.fetch_unread_personal(LOOKBACK_HOURS)
    except Exception as e:
        log.append(f"[Gmail] 取得失敗: {e}")
        return log

    log.append(f"[Gmail] 対象 {len(incoming)} 件")
    for msg in incoming:
        try:
            history = gmail_client.fetch_past_exchanges_with(msg["from_addr"], HISTORY_LIMIT)
            draft = generate_reply("Gmail", msg, history)
            if draft.strip() == "SKIP":
                log.append(f"  - SKIP: {msg['from']} / {msg['subject']}")
                continue
            gmail_client.create_draft(
                thread_id=msg["thread_id"],
                to_addr=msg["from_addr"],
                subject=msg["subject"],
                body=draft,
                in_reply_to_id=msg["id"],
            )
            log.append(f"  - 下書き作成: {msg['from']} / {msg['subject']}")
        except Exception as e:
            log.append(f"  - エラー: {msg.get('from')} - {e}")
    return log


def process_chatwork():
    """Generate Chatwork reply drafts and return them as a summary."""
    log = []
    drafts = []
    try:
        incoming = chatwork_client.fetch_unread_personal(LOOKBACK_HOURS)
    except Exception as e:
        log.append(f"[Chatwork] 取得失敗: {e}")
        return log, drafts

    log.append(f"[Chatwork] 対象 {len(incoming)} 件")
    for msg in incoming:
        try:
            history = chatwork_client.fetch_past_exchanges(msg["room_id"], HISTORY_LIMIT)
            draft = generate_reply("Chatwork", msg, history)
            if draft.strip() == "SKIP":
                log.append(f"  - SKIP: {msg['from_name']}")
                continue
            drafts.append({
                "from_name": msg["from_name"],
                "room_name": msg["room_name"],
                "room_id": msg["room_id"],
                "incoming_body": msg["body"],
                "draft": draft,
            })
            log.append(f"  - 下書き生成: {msg['from_name']}")
        except Exception as e:
            log.append(f"  - エラー: {msg.get('from_name')} - {e}")
    return log, drafts


def build_summary_email(gmail_log, chatwork_log, chatwork_drafts):
    today = datetime.now().strftime("%Y-%m-%d")
    parts = [f"# 本日の返信下書きサマリー ({today})", ""]

    parts.append("## Gmail")
    parts.extend(gmail_log)
    parts.append("→ 下書きは Gmail の「下書き」フォルダで確認・送信してください。")
    parts.append("")

    parts.append("## Chatwork（手動コピペ用）")
    parts.extend(chatwork_log)
    parts.append("")

    if chatwork_drafts:
        parts.append("---")
        for i, d in enumerate(chatwork_drafts, 1):
            parts.append(f"### {i}. {d['from_name']} ({d['room_name']})")
            parts.append(f"Chatwork URL: https://www.chatwork.com/#!rid{d['room_id']}")
            parts.append("")
            parts.append("【受信内容】")
            parts.append(d["incoming_body"])
            parts.append("")
            parts.append("【返信下書き】")
            parts.append(d["draft"])
            parts.append("")
            parts.append("---")
    return "\n".join(parts)


def main():
    gmail_log = process_gmail()
    chatwork_log, chatwork_drafts = process_chatwork()
    summary = build_summary_email(gmail_log, chatwork_log, chatwork_drafts)

    print(summary)

    try:
        today = datetime.now().strftime("%Y-%m-%d")
        gmail_client.send_summary(
            to_addr=SUMMARY_TO_EMAIL,
            subject=f"[返信下書き] {today}",
            body=summary,
        )
        print("\n[OK] サマリーメール送信完了")
    except Exception:
        print("\n[ERR] サマリーメール送信失敗")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
