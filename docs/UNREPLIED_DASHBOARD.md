# LINE 未返信ダッシュボード セットアップ

LINE Official Account Manager 上の会話を Chrome 拡張でスキャンし、
12時間以上返信していない会話をローカルのダッシュボードに一覧表示します。

## 構成

- **Chrome 拡張**（`chrome-extension/`）：LINE Manager の会話一覧を読み取り、ローカルサーバに POST
- **ローカルサーバ**（`src/dashboard/`）：Flask で `http://127.0.0.1:8765` を提供。データは `data/scan.json` に保存
- **ダッシュボード**：ブラウザで `http://127.0.0.1:8765` を開く

---

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. Chrome 拡張の再読み込み

`manifest.json` を更新したので、`chrome://extensions` で拡張機能の **再読み込み** ボタンを押してください（既にインストール済みの場合）。
初回インストール手順は [`chrome-extension/README.md`](../chrome-extension/README.md) 参照。

---

## 毎日の使い方

### 1. ダッシュボードサーバを起動

```bash
python3 -m src.dashboard.app
```

`http://127.0.0.1:8765` で待ち受けます。終了は `Ctrl+C`。

### 2. ダッシュボードを開く

ブラウザで `http://127.0.0.1:8765` を開いておく（タブを残しておけば30秒ごとに自動再読み込み）。

### 3. LINE Manager 側でスキャン

1. `https://chat.line.biz/` を開く
2. 右側のサイドパネルから **🔍 未返信スキャン** をクリック
3. 会話一覧を走査して結果をローカルサーバに送信
4. ダッシュボードに反映される

---

## ダッシュボードの見方

- **危険（赤）**：閾値の 2 倍以上（24時間以上）未返信
- **警告（オレンジ）**：閾値（12時間）以上 〜 2 倍未満
- **正常（緑）**：閾値未満、または最終発言がスタッフ

フィルタ：
- 「未返信のみ」（デフォルト）：12時間以上未返信の会話のみ
- 「最終発言が顧客の会話」：返信予定だが時間内のものも含む
- 「全件」：スキャンした全会話

---

## 設定変更

### 閾値時間を変える

環境変数 `STELLA_UNREPLIED_THRESHOLD_HOURS` で変更できます。

```bash
STELLA_UNREPLIED_THRESHOLD_HOURS=24 python3 -m src.dashboard.app
```

### ポート番号を変える

```bash
STELLA_DASHBOARD_PORT=9000 python3 -m src.dashboard.app
```

ポートを変えた場合は Chrome 拡張の `content.js` 内 `DASHBOARD_URL` と
`manifest.json` の `host_permissions` も合わせて更新してください。

---

## 制限事項

- LINE Manager の DOM 構造は UI 変更で変わるため、スキャンが取れなくなる可能性あり
  - その場合は実画面のスクリーンショットを共有してセレクタを調整
- 「最終発言が顧客かスタッフか」の判定は一覧画面のプレビュー文だけからのヒューリスティック
  - 正確な判定が必要な場合は、各会話を開いて読み取る「ディープスキャン」機能を追加実装
- ダッシュボードはローカル `127.0.0.1` のみで起動。外部公開はしません

---

## トラブルシューティング

### `エラー: Failed to fetch`

ダッシュボードサーバが起動していません。`python3 -m src.dashboard.app` を実行してください。

### スキャン結果が 0 件

LINE Manager の DOM 構造が想定と違う可能性があります。
ブラウザの DevTools で会話リスト要素のクラス名を確認し、
`content.js` の `findConversationListItems()` 内のセレクタ候補に追加してください。

### 名前や時刻が空欄

プレビュー領域のテキスト構造が想定と異なります。
画面のスクリーンショットと、対象会話アイテムの DOM HTML を共有してください。
