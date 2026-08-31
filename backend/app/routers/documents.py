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
from app.services.auth import get_current_uid

router = APIRouter(prefix="/documents", tags=["documents"])


# ------------------------------------------------------------------ テンプレート

@router.post("/templates/learn", dependencies=[Depends(get_current_uid)])
async def learn_template(
    document_type: str = Form(...),
    fields: str = Form(...),
    file: UploadFile = None,
) -> DocumentTemplate:
    """Phase1: 新規フォーマットをLLMに解析させ、テンプレートとして保存する。"""
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
    )
    template_store.save_template(template)
    return template


@router.get("/templates", dependencies=[Depends(get_current_uid)])
async def list_templates() -> list[TemplateInfo]:
    return template_store.list_templates()


@router.get("/templates/{template_id}", dependencies=[Depends(get_current_uid)])
async def get_template(template_id: str) -> DocumentTemplate:
    template = template_store.load_template(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="テンプレートが見つかりません")
    return template


@router.delete("/templates/{template_id}", status_code=204, dependencies=[Depends(get_current_uid)])
async def delete_template(template_id: str) -> None:
    template_store.delete_template(template_id)


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
    template = template_store.load_template(template_id)
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
