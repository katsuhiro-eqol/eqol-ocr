import io

import pymupdf as fitz
from PIL import Image


def file_to_image(file_bytes: bytes, filename: str, dpi: int = 200) -> Image.Image:
    """アップロードされたファイルを PIL Image（1ページ目）に変換する。
    PDF と一般的な画像フォーマット（PNG / JPEG 等）に対応。
    """
    if filename.lower().endswith(".pdf"):
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        if not doc.page_count:
            raise ValueError("PDFからページを取得できませんでした")
        page = doc[0]
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        return Image.open(io.BytesIO(pix.tobytes("png")))
    return Image.open(io.BytesIO(file_bytes))
