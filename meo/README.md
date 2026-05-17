# MEO 口コミ自動ドラフト

Google Business Profile に新しいクチコミが入ったら、5分以内に **Chatwork へ返信ドラフトを通知**するワークフローです。

```
Googleクチコミ通知メール → Gmail → GitHub Actions(5分おき)
                                     ↓
                              Claude が返信ドラフト生成
                                     ↓
                                  Chatwork
```

## セットアップ手順

### 1. Gmail 側

1. 博多ステラ歯科の Google Business Profile のオーナー Google アカウントで Gmail を開く
2. アカウント設定で **2段階認証を有効化**
3. <https://myaccount.google.com/apppasswords> で **アプリパスワード** を発行（16文字）
4. クチコミ通知メールが届くアドレスを確認（GBPで設定済みのはず）

### 2. Chatwork 側

1. ドラフトを受け取りたいルームを作成（例: 「MEO口コミ通知」）
2. ルームURL `https://www.chatwork.com/#!rid********` の数字部分が **ROOM_ID**
3. <https://www.chatwork.com/service/packages/chatwork/subpackages/api/token.php> で **APIトークン**を発行

### 3. Anthropic API キー

1. <https://console.anthropic.com/> で API キーを発行
2. クチコミ1件あたり0.1〜1円程度の費用（Claude Opus 4.7使用時）

### 4. GitHub Secrets に登録

このリポジトリの Settings → Secrets and variables → Actions → New repository secret で以下を追加:

| 名前 | 値 |
| --- | --- |
| `GMAIL_ADDRESS` | クチコミ通知が届く Gmail アドレス |
| `GMAIL_APP_PASSWORD` | 手順1で発行した16文字のアプリパスワード |
| `ANTHROPIC_API_KEY` | Anthropic API キー |
| `CHATWORK_API_TOKEN` | Chatwork APIトークン |
| `CHATWORK_ROOM_ID` | 通知先ルームの数字ID |

### 5. 過去の返信例を登録

`meo/tone_examples.md` を開き、過去にGoogleクチコミに返信した文例を5〜10件貼り付けてコミット。
これでClaudeが院の文体・温度感を学習します。

### 6. 動作確認

GitHub の Actions タブ → 「MEO Review Watcher」 → 「Run workflow」 で手動実行できます。
Gmail にテスト用の自分宛クチコミ通知メールを送って試すのが安全です。

## カスタマイズ

- **トーンの調整**: `tone_examples.md` を編集
- **守るべきルールの追加**: `prompt.md` を編集（医療広告ガイドライン、NGワードなど）
- **通知頻度**: `.github/workflows/meo-review-watcher.yml` の cron を変更（最短5分）
- **通知先の変更**: `watch_reviews.py` の `post_to_chatwork` を差し替えればSlack/LINEにも対応可

## 運用ルール（おすすめ）

1. **必ず人間が確認してから投稿**する。ドラフトは下書きであり、自動投稿はしない設計です
2. 低評価（★1〜3）の返信は院長承認をフローに入れる
3. 1ヶ月運用したら `tone_examples.md` に実際に投稿した返信文を追記してチューニング

## トラブルシューティング

- **Actionsが空振りする** → Gmailのフィルタで「Google からの通知」が迷惑メール扱いになっていないか確認
- **ドラフトが届かない** → Actions のログで失敗ステップを確認。`GMAIL_APP_PASSWORD` の16文字にスペースが混入していることが多い
- **同じクチコミが何度もくる** → Gmail で `MEO/Processed` ラベルが付いているか確認（このラベルで重複処理を防いでいる）
