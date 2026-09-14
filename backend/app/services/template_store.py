"""
テンプレートの保存・読み込み。

すべての操作に owner_uid を要求し、uid が一致するテンプレートのみ操作可能。

Firestore コレクション: /templates/{template_id}
ローカルJSON（開発用フォールバック）: {template_store_path}/{template_id}.json
"""

import json
from pathlib import Path

from app.config import settings
from app.models.schema import DocumentTemplate, TemplateInfo


def _use_firestore() -> bool:
    return bool(settings.firebase_credentials_path or settings.firebase_project_id
                or settings.firebase_credentials_json)


# ------------------------------------------------------------------ Firestore

def _fs_save(template: DocumentTemplate) -> None:
    from app.services.firebase import get_db
    get_db().collection("templates").document(template.template_id).set(
        template.model_dump()
    )


def _fs_load(template_id: str, uid: str) -> DocumentTemplate | None:
    from app.services.firebase import get_db
    doc = get_db().collection("templates").document(template_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    if data.get("owner_uid", "") != uid:
        return None
    return DocumentTemplate(**data)


def _fs_list(uid: str) -> list[TemplateInfo]:
    from app.services.firebase import get_db
    docs = (
        get_db().collection("templates")
        .where("owner_uid", "==", uid)
        .stream()
    )
    result = []
    for doc in docs:
        data = doc.to_dict()
        result.append(TemplateInfo(
            template_id=data.get("template_id", doc.id),
            document_type=data.get("document_type", doc.id),
        ))
    return result


def _fs_delete(template_id: str, uid: str) -> bool:
    from app.services.firebase import get_db
    ref = get_db().collection("templates").document(template_id)
    doc = ref.get()
    if not doc.exists or doc.to_dict().get("owner_uid", "") != uid:
        return False
    ref.delete()
    return True


# ------------------------------------------------------------------ JSON ファイル（開発用）

def _store_dir() -> Path:
    path = Path(settings.template_store_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _file_save(template: DocumentTemplate) -> None:
    file_path = _store_dir() / f"{template.template_id}.json"
    file_path.write_text(template.model_dump_json(indent=2), encoding="utf-8")


def _file_load(template_id: str, uid: str) -> DocumentTemplate | None:
    file_path = _store_dir() / f"{template_id}.json"
    if not file_path.exists():
        return None
    data = json.loads(file_path.read_text(encoding="utf-8"))
    if data.get("owner_uid", "") != uid:
        return None
    return DocumentTemplate(**data)


def _file_list(uid: str) -> list[TemplateInfo]:
    result = []
    for p in _store_dir().glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if data.get("owner_uid", "") != uid:
                continue
            result.append(TemplateInfo(
                template_id=data.get("template_id", p.stem),
                document_type=data.get("document_type", p.stem),
            ))
        except Exception:
            continue
    return result


def _file_delete(template_id: str, uid: str) -> bool:
    file_path = _store_dir() / f"{template_id}.json"
    if not file_path.exists():
        return False
    data = json.loads(file_path.read_text(encoding="utf-8"))
    if data.get("owner_uid", "") != uid:
        return False
    file_path.unlink()
    return True


# ------------------------------------------------------------------ 公開 API

def save_template(template: DocumentTemplate) -> None:
    if _use_firestore():
        _fs_save(template)
    else:
        _file_save(template)


def load_template(template_id: str, uid: str) -> DocumentTemplate | None:
    if _use_firestore():
        return _fs_load(template_id, uid)
    return _file_load(template_id, uid)


def list_templates(uid: str) -> list[TemplateInfo]:
    if _use_firestore():
        return _fs_list(uid)
    return _file_list(uid)


def delete_template(template_id: str, uid: str) -> bool:
    if _use_firestore():
        return _fs_delete(template_id, uid)
    return _file_delete(template_id, uid)
