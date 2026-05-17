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

## チームTODO（Notion風カンバンボード）

スタッフ全員でTODOを共有できるWebアプリ（カンバンビュー、担当者・期日・進捗・優先度・タグ・コメント履歴）。
Google Sheetsをデータ保存先、Google Apps ScriptをAPIとして利用する構成です。

- フロントエンド: [`web/`](web/)
- バックエンド（Apps Script）: [`apps_script/`](apps_script/)
- セットアップ手順: [`docs/TODO_SETUP.md`](docs/TODO_SETUP.md)
