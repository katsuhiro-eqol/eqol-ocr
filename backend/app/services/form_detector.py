"""
OpenCV を使ってフォームの罫線からセル（入力欄）を検出する。

水平線・垂直線をモルフォロジー演算で抽出し、
その位置をクラスタリングしてグリッドを再構成する。
"""

import cv2
import numpy as np
from PIL import Image


def detect_cells(image: Image.Image) -> list[dict]:
    """
    フォーム画像から罫線で囲まれた入力セルを検出する。

    Returns: [{"x0": float, "y0": float, "x1": float, "y1": float}, ...]
             座標は 0-1000 正規化。上から下・左から右の順。
    """
    img = np.array(image.convert("L"))
    H, W = img.shape

    # 暗い罫線を白に反転して二値化（OTSU で閾値自動決定）
    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 水平線：幅の 5% 以上の連続した白画素のみ残す
    h_struct = cv2.getStructuringElement(cv2.MORPH_RECT, (max(W // 20, 50), 1))
    h_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, h_struct)

    # 垂直線：高さの 10% 以上の連続した白画素のみ残す
    # 2% では住所欄の短い縦仕切りが損害記入欄まで検出されてしまうため高めに設定
    v_struct = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(H // 10, 80)))
    v_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, v_struct)

    # 線が存在する行・列をクラスタリングしてグリッド位置を確定
    h_ys = _cluster(np.where(h_lines.any(axis=1))[0])
    v_xs = _cluster(np.where(v_lines.any(axis=0))[0])

    if len(h_ys) < 2 or len(v_xs) < 2:
        print(f"[form_detector] 罫線不足: h={len(h_ys)}, v={len(v_xs)} → セルなし")
        return []

    page_area = W * H
    cells = []
    for i in range(len(h_ys) - 1):
        for j in range(len(v_xs) - 1):
            y0, y1 = h_ys[i], h_ys[i + 1]
            x0, x1 = v_xs[j], v_xs[j + 1]
            cw, ch = x1 - x0, y1 - y0
            # 極端に細いセル・ページ大半を占めるセルは除外
            if cw < 25 or ch < 10 or cw * ch > page_area * 0.6:
                continue
            cells.append({
                "x0": round(x0 / W * 1000, 1),
                "y0": round(y0 / H * 1000, 1),
                "x1": round(x1 / W * 1000, 1),
                "y1": round(y1 / H * 1000, 1),
            })

    print(f"[form_detector] h_lines={len(h_ys)}, v_lines={len(v_xs)}, cells={len(cells)}")
    return sorted(cells, key=lambda c: (c["y0"], c["x0"]))


def _cluster(positions: np.ndarray, gap: int = 8) -> list[int]:
    """隣接するピクセル位置をグループ化し、各グループの中央値を返す。"""
    if len(positions) == 0:
        return []
    groups: list[list[int]] = [[int(positions[0])]]
    for p in positions[1:]:
        if int(p) - groups[-1][-1] <= gap:
            groups[-1].append(int(p))
        else:
            groups.append([int(p)])
    return [int(np.median(g)) for g in groups]
