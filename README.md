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

## LINE返信下書きアシスタント（Chrome拡張）

LINE公式アカウントマネージャー上で、AIによる返信下書きを生成・挿入できる拡張機能。
詳細は [`chrome-extension/README.md`](chrome-extension/README.md) を参照。

## 月次レポート出力（アポツール用 Chrome拡張）

アポツールの画面（クリニックデータ／全ての予約／イベント）から月次KPIを取り込み、
Excel（.xlsx）の月次レポートを書き出す拡張機能。集計値のみを扱い、患者の個人情報は取り込みません。
詳細は [`apotool-extension/README.md`](apotool-extension/README.md) を参照。
