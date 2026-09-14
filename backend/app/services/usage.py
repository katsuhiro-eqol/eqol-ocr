"""
デバイスIDベースの匿名ユーザー使用回数管理。
Firestore の anonymous_usage/{device_id} に記録する。
"""

from firebase_admin import firestore as _fs

PHASE1_LIMIT = 5
PHASE2_LIMIT = 100

_LIMITS = {"phase1": PHASE1_LIMIT, "phase2": PHASE2_LIMIT}


def get_usage(device_id: str) -> dict[str, int]:
    """現在の使用回数を返す（インクリメントなし）。"""
    from app.services.firebase import get_db
    try:
        db = get_db()
        snap = db.collection("anonymous_usage").document(device_id).get()
        data = snap.to_dict() if snap.exists else {}
        return {"phase1": data.get("phase1", 0), "phase2": data.get("phase2", 0)}
    except Exception:
        return {"phase1": 0, "phase2": 0}


def check_and_increment(device_id: str, phase: str) -> tuple[bool, int, int]:
    """
    Returns (allowed, current_count, limit).
    Firestore トランザクションで安全にインクリメント。
    Firestore が使えない場合は許可（フェイルオープン）。
    """
    from app.services.firebase import get_db
    limit = _LIMITS[phase]

    try:
        db = get_db()
    except Exception:
        return True, 0, limit

    ref = db.collection("anonymous_usage").document(device_id)
    result = {"allowed": False, "count": 0}

    @_fs.transactional
    def _txn(transaction, ref):
        snap = ref.get(transaction=transaction)
        data = snap.to_dict() if snap.exists else {}
        count = data.get(phase, 0)
        if count >= limit:
            result["allowed"] = False
            result["count"] = count
            return
        transaction.set(ref, {phase: count + 1}, merge=True)
        result["allowed"] = True
        result["count"] = count + 1

    try:
        _txn(db.transaction(), ref)
    except Exception:
        return True, 0, limit

    return result["allowed"], result["count"], limit
