#!/usr/bin/env python3
"""受付PC用の単体HTMLを index.html から生成する。

index.html は Artifact 用（<!doctype> などの外枠は公開時に付く）なので、
ローカルのPCでダブルクリックして開けるように charset や viewport を付けた
完全なHTMLを standalone/ に書き出す。
"""

from pathlib import Path

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "index.html"
OUTPUT = BASE / "standalone" / "アライナー時間計算.html"
SPLIT_AT = '<div class="wrap">'

HEAD = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<!-- このファイルは tools/aligner-time/index.html から build_standalone.py で生成しています。
     直接編集せず、index.html を直してから再生成してください。 -->
"""

BODY_OPEN = """</head>
<body>
"""

TAIL = """
</body>
</html>
"""


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    if SPLIT_AT not in source:
        raise SystemExit(f"{SPLIT_AT} が index.html に見つかりません")
    head_part, body_part = source.split(SPLIT_AT, 1)
    html = HEAD + head_part.rstrip() + BODY_OPEN + SPLIT_AT + body_part.rstrip() + TAIL
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"生成しました: {OUTPUT.relative_to(BASE.parent.parent)}")


if __name__ == "__main__":
    main()
