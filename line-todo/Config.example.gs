/**
 * 設定ファイルの見本。
 *
 * tools/setup_line_todo.py を実行すると、この形の Config.gs が
 * Apps Script プロジェクト側に自動で作られます。
 * 手で設定する場合は、この内容を Config.gs という名前で貼り付けてください。
 * （実際の値が入った Config.gs はリポジトリにコミットしないでください）
 */
const CONFIG = {
  // LINE Developers の「Messaging API設定」で発行した長期アクセストークン
  LINE_CHANNEL_ACCESS_TOKEN: 'ここにトークン',

  // スプレッドシートURLの /d/ と /edit の間の文字列
  SPREADSHEET_ID: 'ここにスプレッドシートID',

  // 登録を許可するLINEユーザーID。カンマ区切り。空だと友だち全員が書き込めます
  ALLOWED_USER_IDS: '',
};
