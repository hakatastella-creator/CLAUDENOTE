"""補正済み写真を規格コラージュ・Before/After比較・確認シートに合成する。"""

from __future__ import annotations

from PIL import Image, ImageDraw

from .images import load_font
from .views import (
    ViewType,
    JP_LABEL,
    COMPOSITE_LAYOUT,
)

# キャンバス既定サイズ（16:9）と配色（資料のトーンに合わせたオフホワイト／ピンク）
CANVAS_W, CANVAS_H = 1600, 900
BG_COLOR = (246, 243, 240)
ACCENT = (216, 168, 178)
TEXT_COLOR = (74, 60, 58)
LABEL_BG = (255, 255, 255)


def _fit_contain(img: Image.Image, w: int, h: int) -> Image.Image:
    """アスペクト比を保ったまま w×h に収まる最大サイズへ縮小する。"""
    out = img.copy()
    out.thumbnail((w, h), Image.LANCZOS)
    return out


def _paste_box(
    canvas: Image.Image,
    img: Image.Image,
    box: tuple[int, int, int, int],
    *,
    label: str | None = None,
    fill_cell: bool = True,
) -> None:
    """ピクセル指定のセルboxに画像を中央配置で貼り付ける。

    fill_cell=True ならセルをカバーするようトリミング（cover）、
    False ならセル内に収める（contain）。
    """
    x, y, w, h = box
    if fill_cell:
        fitted = _cover(img, w, h)
        ox, oy = x, y
    else:
        fitted = _fit_contain(img, w, h)
        ox = x + (w - fitted.width) // 2
        oy = y + (h - fitted.height) // 2
    canvas.paste(fitted, (ox, oy))

    if label:
        _draw_label(canvas, label, (x, y))


def _cover(img: Image.Image, w: int, h: int) -> Image.Image:
    """w×h をカバーするよう拡大して中央クロップする（cover）。"""
    src_ratio = img.width / img.height
    dst_ratio = w / h
    if src_ratio > dst_ratio:
        new_h = h
        new_w = round(h * src_ratio)
    else:
        new_w = w
        new_h = round(w / src_ratio)
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - w) // 2
    top = (new_h - h) // 2
    return resized.crop((left, top, left + w, top + h))


def _draw_label(canvas: Image.Image, text: str, pos: tuple[int, int]) -> None:
    """左上に半透明の白帯ラベルを描く。"""
    draw = ImageDraw.Draw(canvas)
    font = load_font(22)
    x, y = pos
    tb = draw.textbbox((0, 0), text, font=font)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    pad = 6
    draw.rectangle([x, y, x + tw + pad * 2, y + th + pad * 2], fill=LABEL_BG)
    draw.text((x + pad, y + pad - tb[1]), text, font=font, fill=TEXT_COLOR)


def _denorm(box: tuple[float, float, float, float]) -> tuple[int, int, int, int]:
    """正規化座標(0〜1)をキャンバスのピクセル座標へ変換。"""
    x, y, w, h = box
    return (round(x * CANVAS_W), round(y * CANVAS_H),
            round(w * CANVAS_W), round(h * CANVAS_H))


def _new_canvas() -> Image.Image:
    return Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)


def _title(canvas: Image.Image, title: str, subtitle: str | None = None) -> None:
    """左上にタイトル・サブタイトルを描く。"""
    draw = ImageDraw.Draw(canvas)
    draw.text((40, 26), title, font=load_font(40), fill=TEXT_COLOR)
    if subtitle:
        draw.text((44, 84), subtitle, font=load_font(24), fill=ACCENT)


# --- 規格コラージュ（1時点） ---------------------------------------------------

def build_composite(
    images_by_view: dict[ViewType, Image.Image],
    title: str = "これまでの振り返り",
    subtitle: str | None = None,
) -> Image.Image:
    """8枚法の標準コラージュを1枚生成する。欠けている種類は空欄。"""
    canvas = _new_canvas()
    for view, box in COMPOSITE_LAYOUT.items():
        px = _denorm(box)
        img = images_by_view.get(view)
        if img is not None:
            _paste_box(canvas, img, px, fill_cell=True)
        else:
            _draw_placeholder(canvas, px, JP_LABEL[view])
    _title(canvas, title, subtitle)
    return canvas


def _draw_placeholder(canvas: Image.Image, box: tuple[int, int, int, int], label: str) -> None:
    """写真が無いセルに枠とラベルだけ描く。"""
    x, y, w, h = box
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([x, y, x + w, y + h], outline=ACCENT, width=2)
    font = load_font(20)
    tb = draw.textbbox((0, 0), f"{label}（無し）", font=font)
    tw = tb[2] - tb[0]
    draw.text((x + (w - tw) // 2, y + h // 2 - 10), f"{label}（無し）",
              font=font, fill=ACCENT)


# --- Before/After 比較 ---------------------------------------------------------

def build_comparison(
    initial_by_view: dict[ViewType, Image.Image],
    current_by_view: dict[ViewType, Image.Image],
    views: list[ViewType],
    title: str = "初診時と現在の比較",
    rows: int | None = None,
) -> Image.Image:
    """指定した種類について Before（左）→ After（右）を縦に並べた比較画像。"""
    canvas = _new_canvas()
    _title(canvas, title)

    n = len(views)
    rows = rows or n
    top, bottom = 150, CANVAS_H - 40
    cell_h = (bottom - top) // rows
    # 左（Before）と右（After）の2カラム。中央に矢印スペース。
    col_w = int(CANVAS_W * 0.40)
    left_x = int(CANVAS_W * 0.04)
    right_x = int(CANVAS_W * 0.56)
    pad = 12

    draw = ImageDraw.Draw(canvas)
    draw.text((left_x, 92), "Before（初診時）", font=load_font(24), fill=TEXT_COLOR)
    draw.text((right_x, 92), "After（現在）", font=load_font(24), fill=ACCENT)

    for i, view in enumerate(views):
        cy = top + i * cell_h
        box_l = (left_x, cy + pad, col_w, cell_h - pad * 2)
        box_r = (right_x, cy + pad, col_w, cell_h - pad * 2)
        bi = initial_by_view.get(view)
        bc = current_by_view.get(view)
        if bi is not None:
            _paste_box(canvas, bi, box_l, label=JP_LABEL[view], fill_cell=False)
        if bc is not None:
            _paste_box(canvas, bc, box_r, fill_cell=False)
        # 中央に矢印
        ax = left_x + col_w + 20
        ay = cy + cell_h // 2
        draw.polygon(
            [(ax, ay - 14), (ax + 40, ay), (ax, ay + 14)],
            fill=ACCENT,
        )
    return canvas


# --- 分類確認シート ------------------------------------------------------------

def build_contact_sheet(items: list[tuple[Image.Image, str]], cols: int = 4) -> Image.Image:
    """補正済みサムネイル＋判定ラベルの一覧（AI判別の目視確認用）。"""
    n = len(items)
    rows = (n + cols - 1) // cols
    cell_w, cell_h = 360, 300
    margin = 20
    label_h = 40
    width = cols * cell_w + margin * 2
    height = rows * cell_h + margin * 2 + 60
    canvas = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 16), "分類・補正の確認シート", font=load_font(32), fill=TEXT_COLOR)

    for idx, (img, label) in enumerate(items):
        r, c = divmod(idx, cols)
        x = margin + c * cell_w
        y = margin + 60 + r * cell_h
        thumb = _fit_contain(img, cell_w - 20, cell_h - label_h - 20)
        ox = x + (cell_w - thumb.width) // 2
        canvas.paste(thumb, (ox, y))
        tb = draw.textbbox((0, 0), label, font=load_font(20))
        tw = tb[2] - tb[0]
        draw.text((x + (cell_w - tw) // 2, y + cell_h - label_h),
                  label, font=load_font(20), fill=TEXT_COLOR)
    return canvas
