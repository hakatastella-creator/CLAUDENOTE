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

## 月次レポート作成システム（入力フォーム型｜推奨）

数字を入力するだけで月次Excel（.xlsx）を作る単一HTML。拡張機能もインストールも不要で、
`index.html` をダブルクリックで開くだけ。合計・率は自動計算、入力は端末内に自動保存。
詳細は [`monthly-report-builder/README.md`](monthly-report-builder/README.md) を参照。

## 月次レポート出力（アポツール用 Chrome拡張｜非推奨）

アポツールの画面から月次KPIを読み取る拡張機能。アポツールで拡張機能が使えなくなる見込みのため
**非推奨**。上の入力フォーム型を使ってください。詳細は [`apotool-extension/README.md`](apotool-extension/README.md)。
