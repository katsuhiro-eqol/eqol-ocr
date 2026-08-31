from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator


class AnchorPosition(str, Enum):
    right = "right"
    left = "left"
    above = "above"
    below = "below"
    inside_cell = "inside_cell"
    no_label = "no_label"


class BBox(BaseModel):
    """正規化座標(0-1000)の bbox。
    オブジェクト形式 {"x0":..., "y0":..., "x1":..., "y1":...} と
    配列形式 [x0, y0, x1, y1] の両方を受け付ける。
    """

    x0: float
    y0: float
    x1: float
    y1: float

    @model_validator(mode="before")
    @classmethod
    def from_list(cls, v: object) -> object:
        if isinstance(v, (list, tuple)) and len(v) == 4:
            return {"x0": v[0], "y0": v[1], "x1": v[2], "y1": v[3]}
        return v

    def as_list(self) -> list[float]:
        return [self.x0, self.y0, self.x1, self.y1]


class FieldAnchor(BaseModel):
    """Phase1でLLMが出力する、1項目分のアンカー情報"""

    field_key: str
    field_label_ja: str
    value: str
    section_name: str
    anchor_label_text: str = ""
    anchor_position: AnchorPosition
    anchor_note: str = ""
    label_bbox: Optional[BBox] = None
    value_bbox: Optional[BBox] = None

    @field_validator("anchor_label_text", "anchor_note", "value", "section_name", mode="before")
    @classmethod
    def none_to_empty_str(cls, v: object) -> str:
        return "" if v is None else v

    @field_validator("label_bbox", "value_bbox", mode="before")
    @classmethod
    def empty_list_to_none(cls, v: object) -> object:
        if isinstance(v, (list, tuple)) and len(v) != 4:
            return None
        return v


class DocumentTemplate(BaseModel):
    """書類フォーマットごとに保存するテンプレート"""

    template_id: str = ""
    document_type: str
    page_size_note: str = ""
    fields: list[FieldAnchor]


class TemplateInfo(BaseModel):
    """テンプレート一覧返却用"""

    template_id: str
    document_type: str


class ExtractedField(BaseModel):
    """Phase2実行後、1項目分の最終抽出結果"""

    field_key: str
    field_label_ja: str
    value: str
    confidence: float
    source: str  # "phase2_ocr" or "phase1_llm_fallback"
    debug_image_b64: Optional[str] = None  # debug=true 時のみ PNG base64


class ExtractionResult(BaseModel):
    document_id: str
    template_id: Optional[str] = None
    fields: list[ExtractedField]
    needs_fallback: bool = False
    created_at: Optional[datetime] = None


class OcrResultSummary(BaseModel):
    """OCR結果一覧返却用（フィールド詳細なし）"""

    document_id: str
    template_id: Optional[str] = None
    created_at: Optional[datetime] = None
    needs_fallback: bool = False
