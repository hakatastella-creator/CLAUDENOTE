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

## アライナー来院の所要時間計算

クリンチェックを見て処置（アタッチメント除去／セット、ボタン除去／セット、IPR）を入力すると、
次回来院の予約枠を計算します（連絡文は医院のLINE定型文を使用）。
アタッチメント除去は個数で段階的に、アタッチメントセットとボタン除去は口腔を6分割したブロック単位で計算します。

- **ツール**: [`tools/aligner-time/index.html`](tools/aligner-time/index.html)（ブラウザで開くだけ）
- **受付PC用**: [`tools/aligner-time/standalone/アライナー時間計算.html`](tools/aligner-time/standalone/)（デスクトップに置いてダブルクリック）
- 使い方と時間の初期値は [`tools/aligner-time/README.md`](tools/aligner-time/README.md) を参照。
