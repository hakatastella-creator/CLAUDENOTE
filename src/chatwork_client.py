from datetime import datetime, timedelta, timezone

import requests

from config import CHATWORK_API_TOKEN

API_BASE = "https://api.chatwork.com/v2"


def _headers():
    return {"X-ChatWorkToken": CHATWORK_API_TOKEN}


def _get(path, params=None):
    r = requests.get(f"{API_BASE}{path}", headers=_headers(), params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def _me():
    return _get("/me")


def fetch_unread_personal(lookback_hours):
    """Fetch unread mention/DM messages in personal (1:1) rooms within window."""
    me = _me()
    my_account_id = me["account_id"]
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)

    rooms = _get("/rooms")
    results = []
    for room in rooms:
        if room.get("type") != "direct":
            continue
        if room.get("unread_num", 0) == 0 and room.get("mention_num", 0) == 0:
            continue
        room_id = room["room_id"]
        try:
            msgs = _get(f"/rooms/{room_id}/messages", params={"force": 0})
        except requests.HTTPError:
            continue
        if not msgs:
            continue
        for m in msgs:
            ts = datetime.fromtimestamp(m["send_time"], tz=timezone.utc)
            if ts < cutoff:
                continue
            if m["account"]["account_id"] == my_account_id:
                continue
            results.append({
                "room_id": room_id,
                "room_name": room.get("name", ""),
                "message_id": m["message_id"],
                "from_name": m["account"]["name"],
                "from_account_id": m["account"]["account_id"],
                "body": m["body"][:5000],
                "send_time": ts.isoformat(),
            })
    return results


def fetch_past_exchanges(room_id, limit):
    """Fetch the most recent `limit` messages in this room."""
    try:
        msgs = _get(f"/rooms/{room_id}/messages", params={"force": 1})
    except requests.HTTPError:
        return []
    me = _me()
    my_account_id = me["account_id"]
    msgs = msgs[-limit:] if len(msgs) > limit else msgs
    items = []
    for m in msgs:
        items.append({
            "is_self": m["account"]["account_id"] == my_account_id,
            "from_name": m["account"]["name"],
            "body": m["body"][:2000],
            "send_time": datetime.fromtimestamp(m["send_time"], tz=timezone.utc).isoformat(),
        })
    return items


def _post(path, data):
    r = requests.post(f"{API_BASE}{path}", headers=_headers(), data=data, timeout=30)
    r.raise_for_status()
    return r.json()


def my_chat_room_id():
    """マイチャット（自分専用のチャット）のroom_idを返す。"""
    for room in _get("/rooms"):
        if room.get("type") == "my":
            return room["room_id"]
    raise RuntimeError("マイチャットが見つかりませんでした")


def fetch_recent_messages(room_id):
    """直近のメッセージ（最大100件）を古い順で返す。未読・既読を問わない。"""
    try:
        msgs = _get(f"/rooms/{room_id}/messages", params={"force": 1})
    except requests.HTTPError:
        return []
    return msgs or []


def send_message(room_id, body):
    """メッセージを送信する。自分宛の通知は出さない。"""
    return _post(f"/rooms/{room_id}/messages", {"body": body, "self_unread": "0"})
