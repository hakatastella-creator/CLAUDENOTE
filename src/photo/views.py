"""規格写真の種類定義・向き補正ルール・コラージュレイアウト定義。

博多ステラ歯科の保定オリエンテーション資料で使う「8枚法」の規格写真を扱う。
- 顔貌3枚（正面安静・正面スマイル・側貌）
- 口腔内5枚（上顎咬合面・下顎咬合面・右側方・正面・左側方）
"""

from __future__ import annotations

from enum import Enum

from PIL import Image, ImageOps


class ViewType(str, Enum):
    """規格写真の種類。値は分類JSONやファイル名で使う英語キー。"""

    FACE_FRONT = "face_front"        # 顔貌正面（安静）
    FACE_SMILE = "face_smile"        # 顔貌正面（スマイル）
    FACE_PROFILE = "face_profile"    # 側貌
    OCCLUSAL_UPPER = "occlusal_upper"  # 上顎咬合面観
    OCCLUSAL_LOWER = "occlusal_lower"  # 下顎咬合面観
    INTRA_RIGHT = "intra_right"      # 右側方面観（頬側）
    INTRA_FRONT = "intra_front"      # 正面面観
    INTRA_LEFT = "intra_left"        # 左側方面観（頬側）
    UNKNOWN = "unknown"              # 判別不能（規格外・要手動確認）


# 日本語ラベル（コラージュ・確認シート用）
JP_LABEL: dict[ViewType, str] = {
    ViewType.FACE_FRONT: "顔貌正面",
    ViewType.FACE_SMILE: "スマイル",
    ViewType.FACE_PROFILE: "側貌",
    ViewType.OCCLUSAL_UPPER: "上顎咬合面",
    ViewType.OCCLUSAL_LOWER: "下顎咬合面",
    ViewType.INTRA_RIGHT: "右側方",
    ViewType.INTRA_FRONT: "正面",
    ViewType.INTRA_LEFT: "左側方",
    ViewType.UNKNOWN: "不明",
}

# 口腔内（ミラー撮影）の写真。顔貌は直接撮影なので含めない。
INTRAORAL_VIEWS = {
    ViewType.OCCLUSAL_UPPER,
    ViewType.OCCLUSAL_LOWER,
    ViewType.INTRA_RIGHT,
    ViewType.INTRA_FRONT,
    ViewType.INTRA_LEFT,
}

# 標準コラージュに並べる順序（左上→右下のおおよその表示順）
STANDARD_ORDER = [
    ViewType.FACE_FRONT,
    ViewType.FACE_SMILE,
    ViewType.FACE_PROFILE,
    ViewType.OCCLUSAL_UPPER,
    ViewType.INTRA_RIGHT,
    ViewType.INTRA_FRONT,
    ViewType.INTRA_LEFT,
    ViewType.OCCLUSAL_LOWER,
]


# --- 向き補正のデフォルトルール -------------------------------------------------
#
# ミラー撮影の規格写真を、解剖学的に正しい標準表示へ補正するための既定変換。
# AI分類が個別に変換を返した場合はそちらを優先し、無い場合にこの既定値を使う。
#
# 利用できる操作:
#   "none"          変換なし
#   "flip_h"        左右反転（水平ミラー）
#   "flip_v"        上下反転（垂直ミラー）
#   "rotate_180"    180度回転
#   "rotate_90_cw"  時計回り90度
#   "rotate_90_ccw" 反時計回り90度
#
# 既定の考え方:
#   - 側方面観（右/左）はミラー像のため左右反転して実像に戻す。
#   - 咬合面観は撮影ミラーの反射像のため上下反転して戻す。
#   - 顔貌・正面面観は直接撮影なので無変換。
DEFAULT_TRANSFORM: dict[ViewType, list[str]] = {
    ViewType.FACE_FRONT: ["none"],
    ViewType.FACE_SMILE: ["none"],
    ViewType.FACE_PROFILE: ["none"],
    ViewType.INTRA_FRONT: ["none"],
    ViewType.INTRA_RIGHT: ["flip_h"],
    ViewType.INTRA_LEFT: ["flip_h"],
    ViewType.OCCLUSAL_UPPER: ["flip_v"],
    ViewType.OCCLUSAL_LOWER: ["flip_v"],
    ViewType.UNKNOWN: ["none"],
}


def apply_transforms(img: Image.Image, ops: list[str]) -> Image.Image:
    """変換操作のリストを順に適用して新しい画像を返す。"""
    out = img
    for op in ops:
        if op == "none" or not op:
            continue
        elif op == "flip_h":
            out = ImageOps.mirror(out)
        elif op == "flip_v":
            out = ImageOps.flip(out)
        elif op == "rotate_180":
            out = out.rotate(180, expand=True)
        elif op == "rotate_90_cw":
            out = out.rotate(-90, expand=True)
        elif op == "rotate_90_ccw":
            out = out.rotate(90, expand=True)
        else:
            raise ValueError(f"未知の変換操作: {op}")
    return out


# --- コラージュレイアウト ------------------------------------------------------
#
# 16:9 キャンバス上の各写真の配置（正規化座標 x, y, w, h で 0.0〜1.0）。
# 資料3〜4ページ目の「顔貌を左右、口腔内5枚を中央十字」の構成を再現する。
COMPOSITE_LAYOUT: dict[ViewType, tuple[float, float, float, float]] = {
    # 左列：顔貌正面・スマイル（タイトルと重ならないよう少し下げる）
    ViewType.FACE_FRONT: (0.010, 0.150, 0.190, 0.400),
    ViewType.FACE_SMILE: (0.010, 0.570, 0.190, 0.400),
    # 右上：側貌
    ViewType.FACE_PROFILE: (0.800, 0.150, 0.190, 0.400),
    # 中央：口腔内5枚を十字配置
    ViewType.OCCLUSAL_UPPER: (0.410, 0.150, 0.190, 0.270),
    ViewType.INTRA_RIGHT: (0.215, 0.435, 0.190, 0.270),
    ViewType.INTRA_FRONT: (0.410, 0.435, 0.190, 0.270),
    ViewType.INTRA_LEFT: (0.605, 0.435, 0.190, 0.270),
    ViewType.OCCLUSAL_LOWER: (0.410, 0.720, 0.190, 0.270),
}
