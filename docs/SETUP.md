# セットアップ手順

毎朝 7:00 JST に Gmail と Chatwork の未読をチェックし、相手ごとの文体に合わせた返信下書きを自動生成します。
- **Gmail** → 下書きフォルダに直接保存
- **Chatwork** → 1通のサマリーメールにまとめて自分宛に送信（コピペ用）

---

## 1. Gmail API の設定

### 1-1. Google Cloud プロジェクト作成
1. https://console.cloud.google.com/ にアクセス
2. 新規プロジェクト作成（例：`reply-draft`）
3. 「APIとサービス」→「ライブラリ」→「Gmail API」を有効化

### 1-2. OAuth 同意画面
1. 「APIとサービス」→「OAuth同意画面」
2. ユーザータイプ: **外部**
3. アプリ名・サポートメール・デベロッパー連絡先を入力
4. スコープに `https://www.googleapis.com/auth/gmail.modify` を追加
5. テストユーザーに自分の Gmail アドレスを追加

### 1-3. OAuthクライアントID 作成
1. 「認証情報」→「認証情報を作成」→「OAuthクライアントID」
2. アプリケーションの種類: **デスクトップアプリ**
3. クライアントIDとシークレットをコピー

### 1-4. リフレッシュトークン取得（ローカルPCで1回だけ実行）
```bash
pip install google-auth-oauthlib
python -c "
from google_auth_oauthlib.flow import InstalledAppFlow
flow = InstalledAppFlow.from_client_config(
    {'installed': {
        'client_id': 'YOUR_CLIENT_ID',
        'client_secret': 'YOUR_CLIENT_SECRET',
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'redirect_uris': ['http://localhost']
    }},
    scopes=['https://www.googleapis.com/auth/gmail.modify']
)
creds = flow.run_local_server(port=0)
print('REFRESH TOKEN:', creds.refresh_token)
"
```
ブラウザが開くのでログイン → 表示されたリフレッシュトークンを控える。

---

## 2. Chatwork API トークン
1. Chatwork にログイン → 右上「サービス連携」→「API Token」
2. パスワードを入力してトークンを発行・コピー

---

## 3. Anthropic API キー
1. https://console.anthropic.com/ でアカウント作成
2. 「API Keys」から発行・コピー

---

## 4. GitHub Secrets 登録

リポジトリ → Settings → Secrets and variables → Actions → New repository secret

| Secret 名 | 値 |
|---|---|
| `GMAIL_CLIENT_ID` | 1-3 のクライアントID |
| `GMAIL_CLIENT_SECRET` | 1-3 のシークレット |
| `GMAIL_REFRESH_TOKEN` | 1-4 のトークン |
| `GMAIL_USER` | 自分の Gmail アドレス（例: `you@gmail.com`）|
| `CHATWORK_API_TOKEN` | 2 のトークン |
| `ANTHROPIC_API_KEY` | 3 のキー |
| `SUMMARY_TO_EMAIL` | サマリー送信先（通常は自分の Gmail）|

（オプション）Variables タブで `LOOKBACK_HOURS`（既定24）、`HISTORY_LIMIT`（既定10）、`ANTHROPIC_MODEL`（既定 `claude-sonnet-4-6`）を変更可。

---

## 5. 実行時刻の変更

`.github/workflows/daily-draft.yml` の cron 行を編集。
GitHub Actions は **UTC** なので JST から 9時間引く。

| JST | UTC | cron |
|---|---|---|
| 朝7:00 | 前日22:00 | `0 22 * * *` |
| 朝8:00 | 前日23:00 | `0 23 * * *` |
| 朝9:00 | 0:00 | `0 0 * * *` |

---

## 6. 動作確認

GitHub → Actions タブ → 「Daily Reply Draft」→ 「Run workflow」で手動実行。
ログを確認して、Gmail の下書きとサマリーメールが届けばOK。

---

## トラブルシューティング

- **`Token has been expired or revoked`**: リフレッシュトークン再取得
- **`insufficient permission`**: OAuth スコープに `gmail.modify` が含まれているか確認
- **Chatwork で何も検出されない**: API トークンが正しいか、`type: direct`（1対1）のルームに未読があるか確認
