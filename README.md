# CLAUDENOTE
博多ステラ歯科のCLAUDENOTE

## 毎日の返信下書き自動生成

Gmail と Chatwork の未読メッセージを毎朝チェックし、過去のやり取りから相手ごとの文体を学習した返信下書きを自動生成します。

- **Gmail**: 下書きフォルダに直接保存
- **Chatwork**: サマリーメールにまとめて自分宛に送信
- **実行**: GitHub Actions で毎朝 7:00 JST（変更可）
- **対象**: 個人からの未読のみ（自動配信は除外）
- **学習元**: その相手との直近10件のやり取り

セットアップ手順は [`docs/SETUP.md`](docs/SETUP.md) を参照。

## LINE 未返信ダッシュボード

LINE Official Account Manager の会話を Chrome 拡張でスキャンし、12時間以上未返信の会話をローカルのダッシュボードに一覧表示します。

- **スキャン**: Chrome 拡張のサイドパネルから「🔍 未返信スキャン」ボタン
- **表示**: `http://127.0.0.1:8765` でローカル起動するダッシュボード
- **閾値**: デフォルト12時間（環境変数で変更可）

セットアップ手順は [`docs/UNREPLIED_DASHBOARD.md`](docs/UNREPLIED_DASHBOARD.md) を参照。
