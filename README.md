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

## 保定オリエンテーション 写真処理ツール

矯正の規格写真（8枚法）を **AIで自動分類** し、ミラー撮影の **向きを自動補正（反転・回転）** したうえで、規格コラージュ・初診時/現在の Before/After 比較・**保定オリエンテーション資料（PDF / PowerPoint）** を自動生成します。

```bash
cd src
python -m photo.cli --initial 初診時フォルダ --current 現在フォルダ --out 出力先 --patient 患者名
```

詳細は [`docs/PHOTO.md`](docs/PHOTO.md) を参照。
