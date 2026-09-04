#!/usr/bin/env python3
"""口コミ御礼台帳のページを組み立てる。

template.html には 2 つの差し込み口がある。

    %%STATE%%  … 台帳のデータ（JSON）
    %%SELF%%   … ページが自分自身を保存し直すための、テンプレート全文

公開ページは自分で自分を上書き保存する（Artifact の artifact capability）ため、
テンプレート自身をページの中に持たせておく必要がある。ここではその入れ子を作る。

    python3 build.py          # index.html（初回公開用のフラグメント）を生成
    python3 build.py --full   # full.html（ブラウザで直接開ける完全な HTML）も生成
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "template.html"

TODAY = date.today()
THIS_MONTH = TODAY.strftime("%Y-%m")

SEED = {
    "version": 1,
    "savedAt": "",
    "entries": [
        {
            "id": "sample-1",
            "date": f"{THIS_MONTH}-03",
            "chartNo": "10248",
            "name": "山田 太郎",
            "stars": 5,
            "text": "矯正の相談から装置が入るまで、毎回ていねいに説明していただきました。"
                    "痛みが出たときもすぐ対応してもらえて安心して通えています。",
            "ortho": True,
            "memo": "次回調整は月末。来院時にホワイトニングの案内をする。",
            "done": False,
            "sample": True,
        },
        {
            "id": "sample-2",
            "date": f"{THIS_MONTH}-11",
            "chartNo": "9876",
            "name": "佐藤 花子",
            "stars": 5,
            "text": "急に歯が痛くなって電話したところ、その日のうちに診ていただけました。"
                    "受付の方の対応も気持ちよかったです。",
            "ortho": False,
            "memo": "",
            "done": True,
            "sample": True,
        },
    ],
}


def escape_for_embed(text: str) -> str:
    """<script type="text/plain"> の中に HTML を丸ごと入れられるようにする。"""
    return text.replace("</script", "<\\/script")


def build_full(template: str, state: dict) -> str:
    """完全な HTML ドキュメント（ページが自分を保存し直すときの姿）。"""
    payload = json.dumps(state, ensure_ascii=False).replace("<", "\\u003c")
    filled = template.replace("%%STATE%%", payload, 1)
    return filled.replace("%%SELF%%", escape_for_embed(template), 1)


def to_fragment(document: str) -> str:
    """Artifact ツールに渡すフラグメント（doctype/html/head/body を持たない形）。"""
    head = re.search(r"<head>(.*?)</head>", document, re.S).group(1)
    # 埋め込んだテンプレートの中にも </body> があるため、最後の閉じタグまでを取る
    body = re.search(r"<body>(.*)</body>", document, re.S).group(1)
    head = re.sub(r"[ \t]*<meta[^>]*>\n?", "", head)  # charset と viewport は公開時に付く
    return head.strip() + "\n" + body.strip() + "\n"


def main() -> int:
    template = TEMPLATE.read_text(encoding="utf-8")
    for slot in ("%%STATE%%", "%%SELF%%"):
        if template.count(slot) != 1:
            print(f"template.html に {slot} がちょうど 1 つ必要です", file=sys.stderr)
            return 1

    # 入れ子にできる条件：閉じタグ以外に "</script" が現れず、逃がした形も出てこないこと。
    # （どちらかが崩れると、ページが自分自身を保存し直せなくなる）
    if template.count("</script") != template.count("</script>"):
        print('template.html の中に、閉じタグ以外の "</script" があります', file=sys.stderr)
        return 1
    if "<\\/script" in template:
        print('template.html の中に、逃がした形 "<\\/script" があります', file=sys.stderr)
        return 1

    document = build_full(template, SEED)
    (HERE / "index.html").write_text(to_fragment(document), encoding="utf-8")
    print("index.html を生成しました")

    if "--full" in sys.argv:
        (HERE / "full.html").write_text(document, encoding="utf-8")
        print("full.html を生成しました")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
