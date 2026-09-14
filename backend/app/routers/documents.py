import uuid

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse

from app.core.fallback import needs_fallback
from app.models.schema import (
    DocumentTemplate,
    ExtractionResult,
    OcrResultSummary,
    TemplateInfo,
)
from app.services import (
    csv_export,
    form_detector,
    google_vision,
    image_loader,
    matcher,
    ocr_result_store,
    openai_vision,
    template_store,
)
from app.services.auth import get_current_uid, is_anonymous, device_id_from_uid
from app.services import usage

router = APIRouter(prefix="/documents", tags=["documents"])


# ------------------------------------------------------------------ 使用回数

@router.get("/usage")
async def get_usage(uid: str = Depends(get_current_uid)):
    """匿名ユーザーの使用回数を返す。登録ユーザーは limited=false。"""
    if not is_anonymous(uid):
        return {"limited": False}
    device_id = device_id_from_uid(uid)
    counts = usage.get_usage(device_id)
    return {
        "limited": True,
        "phase1": {"used": counts["phase1"], "limit": usage.PHASE1_LIMIT},
        "phase2": {"used": counts["phase2"], "limit": usage.PHASE2_LIMIT},
    }


# ------------------------------------------------------------------ テンプレート

@router.post("/templates/learn")
async def learn_template(
    document_type: str = Form(...),
    fields: str = Form(...),
    file: UploadFile = None,
    uid: str = Depends(get_current_uid),
) -> DocumentTemplate:
    """Phase1: 新規フォーマットをLLMに解析させ、テンプレートとして保存する。"""
    if is_anonymous(uid):
        allowed, count, limit = usage.check_and_increment(device_id_from_uid(uid), "phase1")
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Phase1の使用上限（{limit}回）に達しました。ユーザー登録すると制限がなくなります。",
            )
    field_names = [f.strip() for f in fields.split(",") if f.strip()]
    file_bytes = await file.read()
    image = image_loader.file_to_image(file_bytes, file.filename or "")

    ocr_blocks = google_vision.full_page_ocr(image)
    cells = form_detector.detect_cells(image)
    anchors = openai_vision.analyze_document(ocr_blocks, field_names, cells=cells)
    template = DocumentTemplate(
        template_id=str(uuid.uuid4()),
        document_type=document_type,
        fields=anchors,
        owner_uid=uid,
    )
    template_store.save_template(template)
    return template


@router.get("/templates")
async def list_templates(uid: str = Depends(get_current_uid)) -> list[TemplateInfo]:
    return template_store.list_templates(uid)


@router.get("/templates/{template_id}")
async def get_template(template_id: str, uid: str = Depends(get_current_uid)) -> DocumentTemplate:
    template = template_store.load_template(template_id, uid)
    if template is None:
        raise HTTPException(status_code=404, detail="テンプレートが見つかりません")
    return template


@router.delete("/templates/{template_id}", status_code=204)
async def delete_template(template_id: str, uid: str = Depends(get_current_uid)) -> None:
    if not template_store.delete_template(template_id, uid):
        raise HTTPException(status_code=404, detail="テンプレートが見つかりません")


# ------------------------------------------------------------------ OCR 抽出

@router.post("/templates/{template_id}/extract")
async def extract_document(
    template_id: str,
    file: UploadFile = None,
    debug: bool = False,
    save: bool = True,
    uid: str = Depends(get_current_uid),
) -> ExtractionResult:
    """Phase2: 既知テンプレートを使って抽出する。
    save=true（デフォルト）の場合、結果を Firestore に保存する。
    """
    if is_anonymous(uid):
        allowed, count, limit = usage.check_and_increment(device_id_from_uid(uid), "phase2")
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Phase2の使用上限（{limit}回）に達しました。ユーザー登録すると制限がなくなります。",
            )
    template = template_store.load_template(template_id, uid)
    if template is None:
        raise HTTPException(status_code=404, detail="テンプレートが見つかりません")

    file_bytes = await file.read()
    image = image_loader.file_to_image(file_bytes, file.filename or "")

    extracted = matcher.extract_with_template(image, template, debug=debug)
    required_keys = {f.field_key for f in template.fields}
    fallback_required = needs_fallback(extracted, required_keys)

    result = ExtractionResult(
        document_id=str(uuid.uuid4()),
        template_id=template_id,
        fields=extracted,
        needs_fallback=fallback_required,
    )

    if save:
        ocr_result_store.save_result(result, uid)

    return result


# ------------------------------------------------------------------ OCR 結果管理

@router.get("/results")
async def list_results(
    uid: str = Depends(get_current_uid),
    limit: int = 50,
) -> list[OcrResultSummary]:
    return ocr_result_store.list_results(uid, limit=limit)


@router.get("/results/{document_id}")
async def get_result(
    document_id: str,
    uid: str = Depends(get_current_uid),
) -> ExtractionResult:
    result = ocr_result_store.load_result(document_id, uid)
    if result is None:
        raise HTTPException(status_code=404, detail="結果が見つかりません")
    return result


@router.delete("/results/{document_id}", status_code=204)
async def delete_result(
    document_id: str,
    uid: str = Depends(get_current_uid),
) -> None:
    if not ocr_result_store.delete_result(document_id, uid):
        raise HTTPException(status_code=404, detail="結果が見つかりません")


# ------------------------------------------------------------------ CSV エクスポート

@router.post("/export/csv", response_class=PlainTextResponse, dependencies=[Depends(get_current_uid)])
async def export_csv(result: ExtractionResult) -> str:
    return csv_export.to_csv(result)
