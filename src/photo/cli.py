"""保定オリエンテーション資料の写真処理 CLI。

使い方:
    python -m photo.cli --initial 初診時フォルダ --current 現在フォルダ \\
        --out 出力先 --patient 長野りかこ

分類モード:
    --mode ai        AIビジョン自動判別（既定。ANTHROPIC_API_KEY が必要）
    --mode filename  ファイル名から推定
    --mode order     撮影順（STANDARD_ORDER）で割当
"""

from __future__ import annotations

import argparse
import os
import sys

from . import pipeline


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="photo",
        description="規格写真を自動分類・向き補正し、保定オリエンテーション資料を生成します。",
    )
    p.add_argument("--initial", required=True, help="初診時の写真フォルダ")
    p.add_argument("--current", required=True, help="現在の写真フォルダ")
    p.add_argument("--out", required=True, help="成果物の出力先フォルダ")
    p.add_argument("--patient", default="", help="患者名（資料タイトルに使用）")
    p.add_argument("--mode", default="ai", choices=["ai", "filename", "order"],
                   help="写真の分類方法（既定: ai）")
    p.add_argument("--model", default=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
                   help="AI分類に使うモデル")
    p.add_argument("--no-pdf", action="store_true", help="PDF変換をスキップ（PPTXのみ）")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if args.mode == "ai" and not api_key:
        print("エラー: AI分類には環境変数 ANTHROPIC_API_KEY が必要です。"
              "--mode filename / order も利用できます。", file=sys.stderr)
        return 2

    outputs = pipeline.run(
        initial_dir=args.initial,
        current_dir=args.current,
        out_dir=args.out,
        patient=args.patient,
        mode=args.mode,
        api_key=api_key,
        model=args.model,
        make_pdf=not args.no_pdf,
    )

    print(f"出力先: {outputs.out_dir}")
    print("生成ファイル:")
    for f in outputs.files:
        print(f"  - {f.name}")
    if outputs.warnings:
        print("\n確認事項:")
        for w in outputs.warnings:
            print(f"  ! {w}")
    print("\n※ AI判別の結果は『確認シート』画像で必ず目視確認してください。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
