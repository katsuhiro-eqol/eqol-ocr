"""
OCR 抽出結果の保存・読み込み。

Firestore コレクション: /ocr_results/{document_id}
各ドキュメントに created_by（uid）フィールドを持ち、ユーザーごとにフィルタリングする。
"""

from datetime import datetime, timezone

from app.models.schema import ExtractionResult, OcrResultSummary

_COLLECTION = "ocr_results"


def save_result(result: ExtractionResult, uid: str) -> None:
    from app.services.firebase import get_db
    data = result.model_dump()
    data["created_by"] = uid
    data["created_at"] = datetime.now(timezone.utc)
    get_db().collection(_COLLECTION).document(result.document_id).set(data)


def load_result(document_id: str, uid: str) -> ExtractionResult | None:
    from app.services.firebase import get_db
    doc = get_db().collection(_COLLECTION).document(document_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    if data.get("created_by") != uid:
        return None
    return ExtractionResult(**data)


def list_results(uid: str, limit: int = 50) -> list[OcrResultSummary]:
    from app.services.firebase import get_db
    docs = (
        get_db()
        .collection(_COLLECTION)
        .where("created_by", "==", uid)
        .order_by("created_at", direction="DESCENDING")
        .limit(limit)
        .stream()
    )
    result = []
    for doc in docs:
        data = doc.to_dict()
        result.append(OcrResultSummary(
            document_id=doc.id,
            template_id=data.get("template_id"),
            created_at=data.get("created_at"),
            needs_fallback=data.get("needs_fallback", False),
        ))
    return result


def delete_result(document_id: str, uid: str) -> bool:
    from app.services.firebase import get_db
    doc_ref = get_db().collection(_COLLECTION).document(document_id)
    doc = doc_ref.get()
    if not doc.exists or doc.to_dict().get("created_by") != uid:
        return False
    doc_ref.delete()
    return True
