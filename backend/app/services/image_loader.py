import io

from PIL import Image
from pdf2image import convert_from_bytes


def file_to_image(file_bytes: bytes, filename: str, dpi: int = 200) -> Image.Image:
    """アップロードされたファイルを PIL Image（1ページ目）に変換する。
    PDF と一般的な画像フォーマット（PNG / JPEG 等）に対応。
    """
    if filename.lower().endswith(".pdf"):
        pages = convert_from_bytes(file_bytes, dpi=dpi)
        if not pages:
            raise ValueError("PDFからページを取得できませんでした")
        return pages[0]
    return Image.open(io.BytesIO(file_bytes))
