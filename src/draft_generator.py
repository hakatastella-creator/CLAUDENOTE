import anthropic

from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


SYSTEM_PROMPT = """あなたはユーザーの代わりにビジネス連絡の返信下書きを作成するアシスタントです。

絶対ルール:
1. 過去のやり取りからユーザー本人（is_self=true の発言）の文体・トーン・敬語レベル・語尾・改行スタイル・絵文字や顔文字の使用傾向を必ず学習し、それを忠実に再現する
2. 相手との関係性（取引先 / 同僚 / 上司 / カジュアル）を過去のやり取りから推定し、適切な距離感を保つ
3. 確定していない事実（日時、金額、約束）は絶対に勝手に作らない。必要なら「【要確認】」と明記する
4. 返信が不要・自動返信レベルの内容なら "SKIP" とだけ返す
5. 出力は返信本文のみ。前置きや説明は一切書かない
"""


def generate_reply(platform, incoming_message, past_exchanges):
    history_lines = []
    for ex in past_exchanges:
        speaker = "本人" if ex.get("is_self") else "相手"
        body = ex.get("body", "").strip().replace("\n", " ")[:500]
        history_lines.append(f"[{speaker}] {body}")
    history_text = "\n".join(history_lines) if history_lines else "（過去のやり取りなし）"

    user_prompt = f"""# プラットフォーム
{platform}

# 相手との過去のやり取り（古い順、本人の文体学習用）
{history_text}

# 今回の受信メッセージ
差出人: {incoming_message.get('from') or incoming_message.get('from_name', '')}
件名: {incoming_message.get('subject', '（なし）')}
本文:
{incoming_message.get('body', '')}

---
上記を踏まえ、本人の文体を完全に再現した返信下書きを作成してください。
返信不要なら "SKIP" のみ。"""

    resp = _client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text = resp.content[0].text.strip()
    return text
