"""画像の読み込み・EXIF補正・縮小・フォントなどの共通ユーティリティ。"""

from __future__ import annotations

import base64
import io
import os
from pathlib import Path

from PIL import Image, ImageOps, ImageFont

# 対応する画像拡張子
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".webp", ".bmp", ".tif", ".tiff"}

# 日本語フォント候補（環境にある最初のものを使う）
_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf",
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def find_font_path() -> str | None:
    """利用可能な日本語フォントのパスを返す。なければ None。"""
    for path in _FONT_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """指定サイズのフォントを読み込む。日本語フォントが無ければ既定フォント。"""
    path = find_font_path()
    if path:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def list_images(folder: str | Path) -> list[Path]:
    """フォルダ直下の画像ファイルを名前順で返す。"""
    folder = Path(folder)
    if not folder.is_dir():
        raise NotADirectoryError(f"フォルダが見つかりません: {folder}")
    files = [
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    ]
    return sorted(files, key=lambda p: p.name.lower())


def open_image(path: str | Path) -> Image.Image:
    """画像を開き、EXIF回転を反映し、RGBに正規化して返す。"""
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)  # スマホ等のEXIF回転を反映
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def to_base64_jpeg(img: Image.Image, max_side: int = 768, quality: int = 80) -> str:
    """API送信用に縮小したJPEGのbase64文字列を返す。"""
    work = img.copy()
    work.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    work.save(buf, format="JPEG", quality=quality)
    return base64.b64encode(buf.getvalue()).decode("ascii")
