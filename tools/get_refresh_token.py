"""
リフレッシュトークン取得スクリプト（初回1回だけ手元PCで実行）

使い方:
  1. pip install google-auth-oauthlib
  2. python tools/get_refresh_token.py
  3. 表示される指示に従い、CLIENT_ID と CLIENT_SECRET を貼り付け
  4. ブラウザが開くので Google ログイン → 「許可」
  5. 表示された REFRESH_TOKEN をコピーして GitHub Secrets に登録
"""
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def main():
    print("=" * 60)
    print("Gmail リフレッシュトークン取得ツール")
    print("=" * 60)
    client_id = input("\nクライアントIDを貼り付けてEnter: ").strip()
    client_secret = input("クライアントシークレットを貼り付けてEnter: ").strip()

    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"],
            }
        },
        scopes=SCOPES,
    )

    print("\nブラウザを開きます。Googleにログインして「許可」を押してください...")
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")

    print("\n" + "=" * 60)
    print("成功しました！下記の REFRESH TOKEN をコピーしてください：")
    print("=" * 60)
    print(creds.refresh_token)
    print("=" * 60)
    print("\nGitHub Secrets に以下の3つを登録してください：")
    print(f"  GMAIL_CLIENT_ID      = {client_id}")
    print(f"  GMAIL_CLIENT_SECRET  = {client_secret}")
    print(f"  GMAIL_REFRESH_TOKEN  = {creds.refresh_token}")


if __name__ == "__main__":
    main()
