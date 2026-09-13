"""
Google Vision API の生レスポンスを JSON で出力するデバッグスクリプト。

使い方:
  cd backend
  python scripts/dump_vision_raw.py <path/to/file.pdf>  [--out result.json]
"""

import argparse
import io
import json
import sys
from pathlib import Path

from google.cloud import vision
from google.protobuf.json_format import MessageToDict
from pdf2image import convert_from_bytes
from PIL import Image


def file_to_image(path: Path, dpi: int = 200) -> Image.Image:
    data = path.read_bytes()
    if path.suffix.lower() == ".pdf":
        pages = convert_from_bytes(data, dpi=dpi)
        if not pages:
            raise ValueError("PDF からページを取得できませんでした")
        return pages[0]
    return Image.open(io.BytesIO(data))


def main() -> None:
    parser = argparse.ArgumentParser(description="Vision API raw dump")
    parser.add_argument("file", type=Path, help="入力ファイル（PDF / PNG / JPEG）")
    parser.add_argument("--out", type=Path, default=None, help="出力 JSON パス（省略時は stdout）")
    args = parser.parse_args()

    image = file_to_image(args.file)
    print(f"[info] image size: {image.size}", file=sys.stderr)

    buf = io.BytesIO()
    image.save(buf, format="PNG")

    client = vision.ImageAnnotatorClient()
    vimg = vision.Image(content=buf.getvalue())
    response = client.document_text_detection(
        image=vimg, image_context={"language_hints": ["ja"]}
    )

    if response.error.message:
        print(f"[error] {response.error.message}", file=sys.stderr)
        sys.exit(1)

    raw = MessageToDict(
        response._pb,
        preserving_proto_field_name=True,
        including_default_value_fields=False,
    )

    # 読みやすさのためトップレベルに full_text も付加
    full_text = response.full_text_annotation.text
    raw["_full_text"] = full_text

    out_json = json.dumps(raw, ensure_ascii=False, indent=2)

    if args.out:
        args.out.write_text(out_json, encoding="utf-8")
        print(f"[info] saved → {args.out}", file=sys.stderr)
    else:
        print(out_json)


if __name__ == "__main__":
    main()
