"""
Phase2の抽出結果が信頼できるかを判定し、Phase1（LLM再解析）への
差し戻しが必要かどうかを決めるロジック。
"""

from app.config import settings
from app.models.schema import ExtractedField


def needs_fallback(fields: list[ExtractedField], required_field_keys: set[str]) -> bool:
    threshold = settings.fallback_confidence_threshold

    for field in fields:
        if field.confidence < threshold:
            return True
        if field.field_key in required_field_keys and not field.value.strip():
            return True

    found_keys = {f.field_key for f in fields}
    if not required_field_keys.issubset(found_keys):
        return True

    return False
