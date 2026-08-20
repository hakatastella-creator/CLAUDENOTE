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

## LINEで送るだけの受付TODO

思いついたことをLINE公式アカウントに送ると、Googleスプレッドシートに1行ずつ貯まります。受付PCからでもスマホからでも同じ宛先に送るだけで登録でき、「一覧」「完了 12」などのコマンドにも対応します。

- **入力**: LINEにメッセージを送る（`#院長`、`#15分`、`8/25まで` などのタグで種別・目安時間・期限を指定）
- **蓄積**: Googleスプレッドシートの月ごとのシートに自動追記
- **仕組み**: LINE Messaging API → Google Apps Script（[`line-todo/Code.gs`](line-todo/Code.gs)）→ スプレッドシート

セットアップ手順は [`docs/LINE_TODO_SETUP.md`](docs/LINE_TODO_SETUP.md) を参照。

## 受付 手が空いたときのやることリスト

診療の合間に確認する受付業務のチェックリストです。所要時間（5分 / 10〜15分 / 30分以上）と、日次・週次・月次の定期業務でまとめています。

→ [`docs/reception-task-list.md`](docs/reception-task-list.md)
