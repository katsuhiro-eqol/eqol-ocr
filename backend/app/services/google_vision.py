"""
Google Cloud Vision API ラッパー。

full_page_ocr() でページ全体を1回だけ OCR し、
単語レベルの OcrBlock リスト（正規化座標 0-1000）を返す。
座標の測定は Vision API が行うため、LLM に画像を渡す必要がない。
"""

from __future__ import annotations

import io
from dataclasses import dataclass

from google.cloud import vision
from PIL import Image

from app.models.schema import BBox


@dataclass
class OcrBlock:
    """Vision API の word レベルの OCR 結果（正規化座標 0-1000）"""

    text: str
    x0: float
    y0: float
    x1: float
    y1: float
    confidence: float

    @property
    def cx(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def cy(self) -> float:
        return (self.y0 + self.y1) / 2

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    @property
    def width(self) -> float:
        return self.x1 - self.x0


def full_page_ocr(image: Image.Image) -> list[OcrBlock]:
    """1枚の画像を document_text_detection し、単語レベルの OcrBlock リストを返す。"""
    client = vision.ImageAnnotatorClient()
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    vimg = vision.Image(content=buf.getvalue())
    response = client.document_text_detection(
        image=vimg, image_context={"language_hints": ["ja"]}
    )
    if response.error.message:
        raise RuntimeError(f"Vision API error: {response.error.message}")

    w, h = image.size
    blocks: list[OcrBlock] = []
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for para in block.paragraphs:
                for word in para.words:
                    word_text = "".join(s.text for s in word.symbols)
                    if not word_text.strip():
                        continue
                    verts = word.bounding_box.vertices
                    xs = [v.x for v in verts]
                    ys = [v.y for v in verts]
                    x0_n = min(xs) / w * 1000
                    y0_n = min(ys) / h * 1000
                    x1_n = max(xs) / w * 1000
                    y1_n = max(ys) / h * 1000
                    conf = (
                        sum(s.confidence for s in word.symbols) / len(word.symbols)
                        if word.symbols
                        else 0.0
                    )
                    blocks.append(OcrBlock(word_text, x0_n, y0_n, x1_n, y1_n, conf))

    print(f"[full_page_ocr] {len(blocks)} words detected")
    return blocks


def crop_by_bbox(image: Image.Image, bbox: BBox) -> Image.Image:
    w, h = image.size
    left = int(min(bbox.x0, bbox.x1) / 1000 * w)
    top = int(min(bbox.y0, bbox.y1) / 1000 * h)
    right = int(max(bbox.x0, bbox.x1) / 1000 * w)
    bottom = int(max(bbox.y0, bbox.y1) / 1000 * h)
    # 最低1x1ピクセルを保証
    right = max(right, left + 1)
    bottom = max(bottom, top + 1)
    return image.crop((left, top, right, bottom))
