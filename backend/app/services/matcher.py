"""
Phase 2 の抽出処理。

Vision API で全ページ OCR → OCR ブロック一覧 + テンプレートを LLM に渡して
各フィールドの値を再構成する。Python による空間検索は行わない。

デバッグ時は value_bbox でクロップした画像を返す（LLM が参照した欄の範囲を可視化）。
"""

from __future__ import annotations

import base64
import io

from PIL import Image

from app.models.schema import DocumentTemplate, ExtractedField
from app.services import openai_vision
from app.services.google_vision import crop_by_bbox, full_page_ocr


def extract_with_template(
    image: Image.Image, template: DocumentTemplate, debug: bool = False
) -> list[ExtractedField]:
    # 1. 全ページOCR（1回だけ）
    blocks = full_page_ocr(image)

    # 2. LLM が OCR ブロック + テンプレートから各フィールドの値を再構成
    # 氏名フィールドは page_image を渡して Vision LLM で精度を高める
    raw_results = openai_vision.extract_fields(blocks, template, page_image=image)

    # field_key → TemplateField のマップ（debug 画像 & メタ情報取得用）
    field_map = {f.field_key: f for f in template.fields}

    results: list[ExtractedField] = []
    for item in raw_results:
        field_key = item.get("field_key", "")
        template_field = field_map.get(field_key)

        debug_image_b64: str | None = None
        if debug and template_field and template_field.value_bbox:
            cropped = crop_by_bbox(image, template_field.value_bbox)
            buf = io.BytesIO()
            cropped.save(buf, format="PNG")
            debug_image_b64 = base64.standard_b64encode(buf.getvalue()).decode()

        results.append(
            ExtractedField(
                field_key=field_key,
                field_label_ja=(
                    template_field.field_label_ja if template_field
                    else item.get("field_label_ja", field_key)
                ),
                value=item.get("value", ""),
                confidence=float(item.get("confidence", 0.0)),
                source="phase2_llm",
                debug_image_b64=debug_image_b64,
            )
        )

    return results
