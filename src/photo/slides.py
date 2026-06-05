"""DECK の各スライドを 1600×900 の PIL 画像として描画する。

LibreOffice に依存せず Pillow だけで PDF を組めるようにするための描画層。
写真スライドは layout.py で生成済みの画像をそのまま使う。
"""

from __future__ import annotations

from PIL import Image, ImageDraw

from .images import load_font
from .layout import CANVAS_W, CANVAS_H, BG_COLOR, ACCENT, TEXT_COLOR

MARGIN = 64


def _new() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)
    return canvas, ImageDraw.Draw(canvas)


def _decor(draw: ImageDraw.ImageDraw) -> None:
    """右上・左下にやわらかいアクセントの円を置く（資料のトーンに寄せた装飾）。"""
    light = (236, 214, 220)
    draw.ellipse([CANVAS_W - 220, -120, CANVAS_W + 80, 180], fill=light)
    draw.ellipse([-140, CANVAS_H - 200, 160, CANVAS_H + 120], fill=light)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    """日本語向けに文字単位で折り返す。"""
    lines: list[str] = []
    cur = ""
    for ch in text:
        if ch == "\n":
            lines.append(cur)
            cur = ""
            continue
        trial = cur + ch
        if draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            lines.append(cur)
            cur = ch
    lines.append(cur)
    return lines


def _draw_paragraph(
    draw: ImageDraw.ImageDraw, text: str, font, x: int, y: int,
    max_width: int, fill, line_gap: int = 10,
) -> int:
    """折り返しながら段落を描画し、次のy座標を返す。"""
    asc, desc = font.getmetrics()
    lh = asc + desc + line_gap
    for line in _wrap(draw, text, font, max_width):
        draw.text((x, y), line, font=font, fill=fill)
        y += lh
    return y


def render_title(spec: dict) -> Image.Image:
    canvas, draw = _new()
    _decor(draw)
    cx = CANVAS_W // 2
    eyebrow_font = load_font(34)
    tw = draw.textlength(spec["eyebrow"], font=eyebrow_font)
    draw.text((cx - tw / 2, 170), spec["eyebrow"], font=eyebrow_font, fill=ACCENT)
    title_font = load_font(96)
    y = 250
    for line in spec["title"].split("\n"):
        lw = draw.textlength(line, font=title_font)
        draw.text((cx - lw / 2, y), line, font=title_font, fill=TEXT_COLOR)
        y += 120
    clinic_font = load_font(30)
    cw = draw.textlength(spec["clinic"], font=clinic_font)
    draw.text((CANVAS_W - MARGIN - cw, CANVAS_H - 90), spec["clinic"],
              font=clinic_font, fill=TEXT_COLOR)
    return canvas


def render_agenda(spec: dict) -> Image.Image:
    canvas, draw = _new()
    _decor(draw)
    draw.text((MARGIN, 150), spec["title"], font=load_font(72), fill=TEXT_COLOR)
    item_font = load_font(40)
    y = 420
    for item in spec["items"]:
        draw.ellipse([CANVAS_W // 2, y + 12, CANVAS_W // 2 + 18, y + 30], fill=ACCENT)
        draw.text((CANVAS_W // 2 + 40, y), item, font=item_font, fill=TEXT_COLOR)
        y += 90
    return canvas


def render_text(spec: dict) -> Image.Image:
    canvas, draw = _new()
    _decor(draw)
    draw.text((MARGIN, 50), spec["title"], font=load_font(54), fill=TEXT_COLOR)

    body_font = load_font(30)
    head_font = load_font(32)
    max_w = CANVAS_W - MARGIN * 2
    y = 180

    for para in spec.get("body", []):
        y = _draw_paragraph(draw, para, body_font, MARGIN, y, max_w, TEXT_COLOR)
        y += 18

    for heading, text in spec.get("blocks", []):
        y += 12
        # 見出しチップ
        label = f"【{heading}】"
        lw = draw.textlength(label, font=head_font)
        draw.rectangle([MARGIN, y, MARGIN + lw + 24, y + 50], fill=(244, 224, 230))
        draw.text((MARGIN + 12, y + 6), label, font=head_font, fill=ACCENT)
        y += 64
        y = _draw_paragraph(draw, text, body_font, MARGIN, y, max_w, TEXT_COLOR)
        y += 18
    return canvas


def render_closing(spec: dict) -> Image.Image:
    canvas, draw = _new()
    _decor(draw)
    font = load_font(80)
    tw = draw.textlength(spec["title"], font=font)
    draw.text((CANVAS_W / 2 - tw / 2, CANVAS_H / 2 - 50), spec["title"],
              font=font, fill=TEXT_COLOR)
    return canvas


def render_slide(spec: dict, images: dict[str, Image.Image]) -> Image.Image:
    """1スライドを画像化して返す。"""
    t = spec["type"]
    if t == "title":
        return render_title(spec)
    if t == "agenda":
        return render_agenda(spec)
    if t == "text":
        return render_text(spec)
    if t == "closing":
        return render_closing(spec)
    if t == "photo":
        img = images.get(spec["key"])
        if img is not None:
            return img.convert("RGB") if img.mode != "RGB" else img
        # 画像欠落時のプレースホルダ
        canvas, draw = _new()
        draw.text((MARGIN, CANVAS_H // 2),
                  f"{spec['title']}（{spec.get('subtitle','')}）写真未設定",
                  font=load_font(40), fill=ACCENT)
        return canvas
    raise ValueError(f"未知のスライド種別: {t}")


def render_deck(deck: list[dict], images: dict[str, Image.Image]) -> list[Image.Image]:
    """DECK 全体を画像リストに描画する。"""
    return [render_slide(spec, images) for spec in deck]
