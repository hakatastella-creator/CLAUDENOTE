#!/usr/bin/env python3
"""LINE受付TODOのGoogle側を自動セットアップする。

やること:
  1. スプレッドシートを作成
  2. そのスプレッドシートに紐づく Apps Script プロジェクトを作成
  3. line-todo/Code.gs と設定（Config.gs）を配置
  4. ウェブアプリとしてデプロイし、Webhook URL を表示

前提:
  - Google Cloud プロジェクトで Apps Script API / Google Sheets API を有効化済み
  - https://script.google.com/home/usersettings の「Google Apps Script API」がオン
  - OAuthクライアント（デスクトップアプリ）の ID とシークレット

使い方:
  # 初回
  python tools/setup_line_todo.py --token "LINEの長期アクセストークン"

  # あとから、登録を許可するLINEユーザーIDを設定（URLは変わりません）
  python tools/setup_line_todo.py --allow "U1a2b...,U9z8y..."
"""

import argparse
import json
import os
import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import AuthorizedSession

ROOT = Path(__file__).resolve().parent.parent
CODE_GS = ROOT / "line-todo" / "Code.gs"
STATE_FILE = ROOT / ".line-todo-setup.json"

SCOPES = [
    "https://www.googleapis.com/auth/script.projects",
    "https://www.googleapis.com/auth/script.deployments",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/spreadsheets",
]

# Apps Script プロジェクト側が実行時に必要とする権限
MANIFEST = {
    "timeZone": "Asia/Tokyo",
    "exceptionLogging": "STACKDRIVER",
    "runtimeVersion": "V8",
    "oauthScopes": [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/script.external_request",
        "https://www.googleapis.com/auth/script.scriptapp",
    ],
    "webapp": {"access": "ANYONE_ANONYMOUS", "executeAs": "USER_DEPLOYING"},
}

SCRIPT_API = "https://script.googleapis.com/v1"
SHEETS_API = "https://sheets.googleapis.com/v4"


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  設定を {STATE_FILE.name} に保存しました（このファイルはコミットされません）")


def authorize():
    client_id = os.environ.get("GMAIL_CLIENT_ID") or input("OAuthクライアントID: ").strip()
    client_secret = os.environ.get("GMAIL_CLIENT_SECRET") or input("OAuthクライアントシークレット: ").strip()
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
    creds = flow.run_local_server(port=0)
    return AuthorizedSession(creds)


def api(session, method, url, **kwargs):
    res = session.request(method, url, **kwargs)
    if res.status_code >= 400:
        raise SystemExit(f"[エラー] {method} {url}\n  {res.status_code} {res.text[:800]}")
    return res.json() if res.text else {}


def config_gs(token, spreadsheet_id, allowed):
    return (
        "/** tools/setup_line_todo.py が生成しました。手で編集しても構いません。 */\n"
        "const CONFIG = {\n"
        f"  LINE_CHANNEL_ACCESS_TOKEN: {json.dumps(token, ensure_ascii=False)},\n"
        f"  SPREADSHEET_ID: {json.dumps(spreadsheet_id, ensure_ascii=False)},\n"
        f"  ALLOWED_USER_IDS: {json.dumps(allowed, ensure_ascii=False)},\n"
        "};\n"
    )


def push_content(session, script_id, token, spreadsheet_id, allowed):
    files = [
        {"name": "appsscript", "type": "JSON", "source": json.dumps(MANIFEST, ensure_ascii=False, indent=2)},
        {"name": "Code", "type": "SERVER_JS", "source": CODE_GS.read_text(encoding="utf-8")},
        {"name": "Config", "type": "SERVER_JS", "source": config_gs(token, spreadsheet_id, allowed)},
    ]
    api(session, "PUT", f"{SCRIPT_API}/projects/{script_id}/content", json={"files": files})


def new_version(session, script_id, description):
    res = api(session, "POST", f"{SCRIPT_API}/projects/{script_id}/versions",
              json={"description": description})
    return res["versionNumber"]


def webapp_url(deployment):
    for ep in deployment.get("entryPoints", []):
        if ep.get("entryPointType") == "WEB_APP":
            return ep.get("webApp", {}).get("url", "")
    return ""


def create_all(session, args, state):
    print("1/4 スプレッドシートを作成しています…")
    sheet = api(session, "POST", f"{SHEETS_API}/spreadsheets",
                json={"properties": {"title": args.title}})
    spreadsheet_id = sheet["spreadsheetId"]
    sheet_url = sheet["spreadsheetUrl"]
    print(f"  作成しました: {sheet_url}")

    print("2/4 Apps Script プロジェクトを作成しています…")
    project = api(session, "POST", f"{SCRIPT_API}/projects",
                  json={"title": f"{args.title} webhook", "parentId": spreadsheet_id})
    script_id = project["scriptId"]
    print(f"  作成しました: https://script.google.com/d/{script_id}/edit")

    print("3/4 プログラムと設定を配置しています…")
    push_content(session, script_id, args.token, spreadsheet_id, args.allow or "")
    version = new_version(session, script_id, "初回セットアップ")

    print("4/4 ウェブアプリとしてデプロイしています…")
    deployment = api(session, "POST", f"{SCRIPT_API}/projects/{script_id}/deployments",
                     json={"versionNumber": version,
                           "manifestFileName": "appsscript",
                           "description": "LINE webhook"})
    deployment_id = deployment["deploymentId"]
    url = webapp_url(deployment)
    if not url:
        deployment = api(session, "GET", f"{SCRIPT_API}/projects/{script_id}/deployments/{deployment_id}")
        url = webapp_url(deployment)

    state.update({
        "spreadsheet_id": spreadsheet_id,
        "spreadsheet_url": sheet_url,
        "script_id": script_id,
        "deployment_id": deployment_id,
        "webhook_url": url,
        "line_token": args.token,
        "allowed_user_ids": args.allow or "",
    })
    save_state(state)

    print("\n" + "=" * 64)
    print("セットアップが完了しました。残りは次の2つだけです。")
    print("=" * 64)
    print("\n【1】LINE Developers の「Messaging API設定」を開き、")
    print("     Webhook URL に次のURLを貼り付けて「更新」→「検証」を押す\n")
    print(f"     {url or '(URLを取得できませんでした。Apps Scriptの画面で確認してください)'}\n")
    print("【2】使う人それぞれがLINEで何か1通送り、返ってきたID（Uで始まる文字列）を集めて\n")
    print('     python tools/setup_line_todo.py --allow "U1a2b...,U9z8y..."\n')
    print(f"スプレッドシート: {sheet_url}")


def update_allow(session, args, state):
    script_id = state["script_id"]
    deployment_id = state["deployment_id"]
    token = args.token or state.get("line_token", "")
    if not token:
        raise SystemExit("[エラー] LINEのトークンが分かりません。--token を付けて実行してください。")

    print("設定を更新しています…")
    push_content(session, script_id, token, state["spreadsheet_id"], args.allow)
    version = new_version(session, script_id, "設定更新")

    print("デプロイを更新しています…（URLは変わりません）")
    api(session, "PUT", f"{SCRIPT_API}/projects/{script_id}/deployments/{deployment_id}",
        json={"deploymentConfig": {"scriptId": script_id,
                                   "versionNumber": version,
                                   "manifestFileName": "appsscript",
                                   "description": "LINE webhook"}})

    state["allowed_user_ids"] = args.allow
    state["line_token"] = token
    save_state(state)
    print("\n完了しました。登録したIDのLINEアカウントだけが書き込めるようになりました。")
    print(f"Webhook URL（変更なし）: {state.get('webhook_url', '')}")


def main():
    parser = argparse.ArgumentParser(description="LINE受付TODOのGoogle側を自動セットアップします")
    parser.add_argument("--token", help="LINEの長期チャネルアクセストークン")
    parser.add_argument("--allow", help="登録を許可するLINEユーザーID（カンマ区切り）")
    parser.add_argument("--title", default="受付TODO", help="スプレッドシートの名前")
    args = parser.parse_args()

    if not CODE_GS.exists():
        raise SystemExit(f"[エラー] {CODE_GS} が見つかりません。リポジトリの直下で実行してください。")

    state = load_state()

    if state.get("script_id") and args.allow is not None:
        session = authorize()
        update_allow(session, args, state)
        return

    if state.get("script_id"):
        print("すでにセットアップ済みです。")
        print(f"  スプレッドシート: {state.get('spreadsheet_url')}")
        print(f"  Webhook URL     : {state.get('webhook_url')}")
        print('\n許可するユーザーIDを設定するには --allow "U1a2b...,U9z8y..." を付けて実行してください。')
        print(f"作り直したい場合は {STATE_FILE.name} を削除してから実行してください。")
        return

    if not args.token:
        raise SystemExit(
            '[エラー] 初回は --token が必要です。\n'
            '  例: python tools/setup_line_todo.py --token "LINEの長期アクセストークン"'
        )

    session = authorize()
    create_all(session, args, state)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
