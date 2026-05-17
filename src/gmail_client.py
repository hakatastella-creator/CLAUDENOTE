import base64
import email
import re
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from datetime import datetime, timedelta, timezone

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from config import (
    GMAIL_CLIENT_ID,
    GMAIL_CLIENT_SECRET,
    GMAIL_REFRESH_TOKEN,
    GMAIL_USER,
    AUTO_SENDER_KEYWORDS,
)

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def _service():
    creds = Credentials(
        token=None,
        refresh_token=GMAIL_REFRESH_TOKEN,
        client_id=GMAIL_CLIENT_ID,
        client_secret=GMAIL_CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def _header(headers, name):
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def _decode_body(payload):
    parts = payload.get("parts")
    if parts:
        for p in parts:
            if p.get("mimeType") == "text/plain" and p.get("body", {}).get("data"):
                return base64.urlsafe_b64decode(p["body"]["data"]).decode("utf-8", errors="replace")
        for p in parts:
            text = _decode_body(p)
            if text:
                return text
        return ""
    data = payload.get("body", {}).get("data")
    if data:
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
    return ""


def _extract_email(from_header):
    m = re.search(r"<([^>]+)>", from_header)
    if m:
        return m.group(1).lower()
    return from_header.strip().lower()


def _is_automated(from_addr, headers):
    addr = from_addr.lower()
    for kw in AUTO_SENDER_KEYWORDS:
        if kw in addr:
            return True
    if _header(headers, "List-Unsubscribe"):
        return True
    if _header(headers, "Precedence").lower() in ("bulk", "list", "auto_reply"):
        return True
    if _header(headers, "Auto-Submitted") and _header(headers, "Auto-Submitted").lower() != "no":
        return True
    return False


def fetch_unread_personal(lookback_hours):
    svc = _service()
    after = int((datetime.now(timezone.utc) - timedelta(hours=lookback_hours)).timestamp())
    query = f"is:unread in:inbox after:{after} -category:promotions -category:social -category:updates"
    res = svc.users().messages().list(userId=GMAIL_USER, q=query, maxResults=50).execute()
    ids = [m["id"] for m in res.get("messages", [])]

    messages = []
    for mid in ids:
        msg = svc.users().messages().get(userId=GMAIL_USER, id=mid, format="full").execute()
        headers = msg["payload"]["headers"]
        from_h = _header(headers, "From")
        from_addr = _extract_email(from_h)
        if _is_automated(from_addr, headers):
            continue
        messages.append({
            "id": mid,
            "thread_id": msg["threadId"],
            "from": from_h,
            "from_addr": from_addr,
            "subject": _header(headers, "Subject"),
            "date": _header(headers, "Date"),
            "body": _decode_body(msg["payload"])[:5000],
        })
    return messages


def fetch_past_exchanges_with(email_addr, limit):
    """Fetch past messages with this contact (both sent and received)."""
    svc = _service()
    query = f"(from:{email_addr} OR to:{email_addr})"
    res = svc.users().messages().list(userId=GMAIL_USER, q=query, maxResults=limit * 3).execute()
    ids = [m["id"] for m in res.get("messages", [])]

    items = []
    for mid in ids[: limit * 3]:
        msg = svc.users().messages().get(userId=GMAIL_USER, id=mid, format="full").execute()
        headers = msg["payload"]["headers"]
        from_h = _header(headers, "From")
        from_addr = _extract_email(from_h)
        is_self = email_addr not in from_addr
        items.append({
            "from_addr": from_addr,
            "is_self": is_self,
            "date": _header(headers, "Date"),
            "body": _decode_body(msg["payload"])[:2000],
        })
        if len(items) >= limit:
            break
    return items


def _profile_from():
    svc = _service()
    profile = svc.users().getProfile(userId=GMAIL_USER).execute()
    return profile.get("emailAddress", GMAIL_USER)


def _build_message(to_addr, subject, body, from_addr, extra_headers=None):
    msg = MIMEText(body, "plain", "utf-8")
    msg["To"] = to_addr
    msg["From"] = from_addr
    msg["Subject"] = str(Header(subject, "utf-8"))
    for k, v in (extra_headers or {}).items():
        msg[k] = v
    return base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")


def create_draft(thread_id, to_addr, subject, body, in_reply_to_id):
    svc = _service()
    from_addr = _profile_from()
    subj = subject if subject.lower().startswith("re:") else f"Re: {subject}"
    extra = {}
    if in_reply_to_id:
        extra["In-Reply-To"] = in_reply_to_id
        extra["References"] = in_reply_to_id
    raw = _build_message(to_addr, subj, body, from_addr, extra)
    draft = svc.users().drafts().create(
        userId=GMAIL_USER,
        body={"message": {"raw": raw, "threadId": thread_id}},
    ).execute()
    return draft["id"]


def send_summary(to_addr, subject, body):
    svc = _service()
    from_addr = _profile_from()
    raw = _build_message(to_addr, subject, body, from_addr)
    svc.users().messages().send(userId=GMAIL_USER, body={"raw": raw}).execute()
