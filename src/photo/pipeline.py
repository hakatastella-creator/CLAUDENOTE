"""フォルダ内の規格写真を分類・向き補正し、コラージュ／比較／資料を生成する一連の処理。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image

from .images import list_images, open_image
from .classify import Classification, classify
from .views import (
    ViewType,
    JP_LABEL,
    INTRAORAL_VIEWS,
    apply_transforms,
)
from . import layout, document


@dataclass
class TimepointResult:
    """1時点（初診時 or 現在）の処理結果。"""

    images_by_view: dict[ViewType, Image.Image] = field(default_factory=dict)
    classifications: list[Classification] = field(default_factory=list)
    corrected: dict[Path, Image.Image] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


# 比較ページに並べる順序
INTRAORAL_COMPARE_ORDER = [
    ViewType.OCCLUSAL_UPPER,
    ViewType.INTRA_RIGHT,
    ViewType.INTRA_FRONT,
    ViewType.INTRA_LEFT,
    ViewType.OCCLUSAL_LOWER,
]
FACE_COMPARE_ORDER = [
    ViewType.FACE_FRONT,
    ViewType.FACE_SMILE,
    ViewType.FACE_PROFILE,
]


def process_timepoint(
    folder: str | Path,
    *,
    mode: str = "ai",
    api_key: str | None = None,
    model: str | None = None,
    max_side: int = 1400,
) -> TimepointResult:
    """1フォルダ分の写真を分類・補正し、種類ごとの画像辞書を作る。"""
    paths = list_images(folder)
    if not paths:
        raise ValueError(f"画像が見つかりません: {folder}")

    classifications = classify(paths, mode=mode, api_key=api_key, model=model)
    result = TimepointResult(classifications=classifications)

    # 確信度の高いものを優先して種類→画像を確定
    best: dict[ViewType, Classification] = {}
    for c in classifications:
        img = open_image(c.path)
        img.thumbnail((max_side, max_side), Image.LANCZOS)
        corrected = apply_transforms(img, c.transform)
        result.corrected[c.path] = corrected

        if c.view == ViewType.UNKNOWN:
            result.warnings.append(f"判別不能: {c.path.name}")
            continue
        prev = best.get(c.view)
        if prev is None or c.confidence > prev.confidence:
            if prev is not None:
                result.warnings.append(
                    f"{JP_LABEL[c.view]} が重複: {prev.path.name} / {c.path.name}"
                    f" → 確信度の高い方を採用")
            best[c.view] = c

    for view, c in best.items():
        result.images_by_view[view] = result.corrected[c.path]

    # 不足している種類を警告
    return result


def contact_sheet_items(result: TimepointResult) -> list[tuple[Image.Image, str]]:
    """確認シート用の (補正済み画像, ラベル) リストを撮影フォルダ順で返す。"""
    items = []
    for c in result.classifications:
        label = f"{JP_LABEL[c.view]}  ({c.confidence:.0%})"
        if c.transform != ["none"]:
            label += "  [補正済]"
        items.append((result.corrected[c.path], label))
    return items


@dataclass
class PipelineOutputs:
    out_dir: Path
    files: list[Path] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def run(
    *,
    initial_dir: str | Path,
    current_dir: str | Path,
    out_dir: str | Path,
    patient: str = "",
    mode: str = "ai",
    api_key: str | None = None,
    model: str | None = None,
    make_pdf: bool = True,
) -> PipelineOutputs:
    """初診時・現在の2フォルダから全成果物を生成する。"""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    outputs = PipelineOutputs(out_dir=out)

    initial = process_timepoint(initial_dir, mode=mode, api_key=api_key, model=model)
    current = process_timepoint(current_dir, mode=mode, api_key=api_key, model=model)
    outputs.warnings = (
        [f"[初診時] {w}" for w in initial.warnings]
        + [f"[現在] {w}" for w in current.warnings]
    )

    title = "これまでの振り返り"
    pat = f"（{patient}様）" if patient else ""

    # 1. 規格コラージュ（初診時・現在）
    comp_initial = layout.build_composite(initial.images_by_view, title, f"初診時{pat}")
    comp_current = layout.build_composite(current.images_by_view, title, f"現在{pat}")

    # 2. Before/After 比較（口腔内・顔貌）
    cmp_intra = layout.build_comparison(
        initial.images_by_view, current.images_by_view,
        INTRAORAL_COMPARE_ORDER, title="初診時と現在の比較（口腔内）")
    cmp_face = layout.build_comparison(
        initial.images_by_view, current.images_by_view,
        FACE_COMPARE_ORDER, title="初診時と現在の比較（顔貌）")

    # 3. 確認シート
    sheet_initial = layout.build_contact_sheet(contact_sheet_items(initial))
    sheet_current = layout.build_contact_sheet(contact_sheet_items(current))

    images = {
        "composite_initial": comp_initial,
        "composite_current": comp_current,
        "comparison_intraoral": cmp_intra,
        "comparison_face": cmp_face,
    }

    # 画像を個別保存
    save_map = {
        "01_コラージュ_初診時.png": comp_initial,
        "02_コラージュ_現在.png": comp_current,
        "03_比較_口腔内.png": cmp_intra,
        "04_比較_顔貌.png": cmp_face,
        "確認シート_初診時.png": sheet_initial,
        "確認シート_現在.png": sheet_current,
    }
    for name, img in save_map.items():
        p = out / name
        img.save(p)
        outputs.files.append(p)

    # 4. 資料（編集用 PPTX ＋ 配布用 PDF）
    stem = f"保定オリエンテーション_{patient}" if patient else "保定オリエンテーション"
    pptx_path = document.build_pptx(images, out / f"{stem}.pptx")
    outputs.files.append(pptx_path)
    if make_pdf:
        pdf_path = document.build_pdf(images, out / f"{stem}.pdf")
        outputs.files.append(pdf_path)

    return outputs
