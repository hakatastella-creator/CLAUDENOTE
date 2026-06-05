"""規格写真をAIビジョンで自動分類する。

各写真について「種類（8枚法のどれか）」と「標準表示に補正するための向き変換」を
Anthropic のビジョンモデルに判定させる。APIが使えない場合はファイル名・撮影順から
推定するフォールバックを用意する。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .images import open_image, to_base64_jpeg
from .views import ViewType, STANDARD_ORDER, DEFAULT_TRANSFORM

VALID_OPS = {"none", "flip_h", "flip_v", "rotate_180", "rotate_90_cw", "rotate_90_ccw"}


@dataclass
class Classification:
    """1枚の写真の分類結果。"""

    path: Path
    view: ViewType
    transform: list[str] = field(default_factory=lambda: ["none"])
    confidence: float = 0.0
    note: str = ""
    source: str = "ai"  # ai / filename / order / manual

    @property
    def needs_review(self) -> bool:
        return self.view == ViewType.UNKNOWN or self.confidence < 0.6


_SYSTEM_PROMPT = """あなたは矯正歯科の規格写真（8枚法）を仕分けする専門アシスタントです。
渡された各画像を、次のいずれか1つに分類してください。

- face_front: 顔貌正面（口を閉じた安静位）
- face_smile: 顔貌正面（歯を見せたスマイル）
- face_profile: 側貌（横顔）
- occlusal_upper: 上顎の咬合面観（口蓋＝上あごの天井が見える。ミラー撮影で歯列がU字/V字）
- occlusal_lower: 下顎の咬合面観（舌が見える。下あごの歯列）
- intra_right: 右側方面観（患者の右側の臼歯が中心。多くはミラー像）
- intra_front: 正面面観（上下の前歯を正面から。左右対称に見える）
- intra_left: 左側方面観（患者の左側の臼歯が中心。多くはミラー像）
- unknown: いずれにも当てはまらない／判別困難

加えて、その画像を「解剖学的に正しい標準表示」へ補正するために必要な向き変換を
transform 配列（先頭から順に適用）で示してください。利用できる操作:
  none, flip_h（左右反転）, flip_v（上下反転）, rotate_180, rotate_90_cw, rotate_90_ccw

判断の目安:
- 側方面観・咬合面観はミラーで撮影されることが多く、その場合は実像に戻す反転が必要です。
- 既に正しい向きなら ["none"] を返してください。
- 患者の右側か左側かは、臼歯の見え方と中心線から判断してください。

出力は必ず次の形式の JSON のみ（前後の説明文やコードフェンスは不要）:
{"results": [{"index": 0, "view": "face_front", "transform": ["none"], "confidence": 0.95, "note": "理由を簡潔に"}, ...]}
index は渡した画像の順番（0始まり）に対応させること。"""


def classify_with_ai(paths: list[Path], api_key: str, model: str) -> list[Classification]:
    """Anthropic ビジョンモデルで一括分類する。"""
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)

    content: list[dict] = []
    for i, p in enumerate(paths):
        img = open_image(p)
        content.append({"type": "text", "text": f"画像 index={i}: {p.name}"})
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": to_base64_jpeg(img),
            },
        })
    content.append({
        "type": "text",
        "text": "上記すべての画像を分類し、指定の JSON 形式のみで出力してください。",
    })

    resp = client.messages.create(
        model=model,
        max_tokens=2000,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}],
    )
    text = "".join(block.text for block in resp.content if block.type == "text").strip()
    data = _parse_json(text)

    by_index: dict[int, dict] = {item.get("index", -1): item for item in data.get("results", [])}
    results: list[Classification] = []
    for i, p in enumerate(paths):
        item = by_index.get(i, {})
        results.append(_to_classification(p, item, source="ai"))
    return results


def _parse_json(text: str) -> dict:
    """モデル出力からJSONを抽出する（コードフェンス等に耐性を持たせる）。"""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"分類結果のJSONを解釈できませんでした: {text[:200]}")
    return json.loads(text[start:end + 1])


def _to_classification(path: Path, item: dict, source: str) -> Classification:
    """生のdictを検証してClassificationに変換。不正値は安全側に倒す。"""
    try:
        view = ViewType(item.get("view", "unknown"))
    except ValueError:
        view = ViewType.UNKNOWN

    transform = item.get("transform") or list(DEFAULT_TRANSFORM.get(view, ["none"]))
    if not isinstance(transform, list):
        transform = [str(transform)]
    transform = [op for op in transform if op in VALID_OPS] or ["none"]

    try:
        confidence = float(item.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0

    return Classification(
        path=path,
        view=view,
        transform=transform,
        confidence=max(0.0, min(1.0, confidence)),
        note=str(item.get("note", "")),
        source=source,
    )


# --- フォールバック分類 --------------------------------------------------------

# ファイル名に含まれるキーワード → 種類
_FILENAME_HINTS: list[tuple[tuple[str, ...], ViewType]] = [
    (("face_front", "顔貌正面", "正面顔", "rest"), ViewType.FACE_FRONT),
    (("smile", "スマイル", "笑顔"), ViewType.FACE_SMILE),
    (("profile", "側貌", "横顔"), ViewType.FACE_PROFILE),
    (("occlusal_upper", "upper", "上顎", "上咬合"), ViewType.OCCLUSAL_UPPER),
    (("occlusal_lower", "lower", "下顎", "下咬合"), ViewType.OCCLUSAL_LOWER),
    (("intra_right", "right", "右側", "右臼歯"), ViewType.INTRA_RIGHT),
    (("intra_left", "left", "左側", "左臼歯"), ViewType.INTRA_LEFT),
    (("intra_front", "front", "正面口腔", "正面面観"), ViewType.INTRA_FRONT),
]


def classify_by_filename(paths: list[Path]) -> list[Classification]:
    """ファイル名のキーワードから推定する。"""
    results = []
    for p in paths:
        name = p.name.lower()
        view = ViewType.UNKNOWN
        for keywords, vt in _FILENAME_HINTS:
            if any(k.lower() in name for k in keywords):
                view = vt
                break
        results.append(Classification(
            path=p, view=view,
            transform=list(DEFAULT_TRANSFORM.get(view, ["none"])),
            confidence=0.7 if view != ViewType.UNKNOWN else 0.0,
            note="ファイル名から推定", source="filename",
        ))
    return results


def classify_by_order(paths: list[Path]) -> list[Classification]:
    """撮影順が STANDARD_ORDER と一致している前提で割り当てる。"""
    results = []
    for i, p in enumerate(paths):
        view = STANDARD_ORDER[i] if i < len(STANDARD_ORDER) else ViewType.UNKNOWN
        results.append(Classification(
            path=p, view=view,
            transform=list(DEFAULT_TRANSFORM.get(view, ["none"])),
            confidence=0.5 if view != ViewType.UNKNOWN else 0.0,
            note=f"撮影順 {i + 1} 番目として割当", source="order",
        ))
    return results


def classify(
    paths: list[Path],
    *,
    mode: str = "ai",
    api_key: str | None = None,
    model: str | None = None,
) -> list[Classification]:
    """指定モードで分類する。

    mode:
      "ai"       AIビジョン分類（api_key, model が必要）
      "filename" ファイル名から推定
      "order"    撮影順から割当
    """
    if mode == "ai":
        if not api_key:
            raise ValueError("AI分類には ANTHROPIC_API_KEY が必要です。")
        return classify_with_ai(paths, api_key=api_key, model=model or "claude-sonnet-4-6")
    if mode == "filename":
        return classify_by_filename(paths)
    if mode == "order":
        return classify_by_order(paths)
    raise ValueError(f"未知の分類モード: {mode}")
