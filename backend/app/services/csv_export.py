import csv
import io

from app.models.schema import ExtractionResult


def to_csv(result: ExtractionResult) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["field_key", "field_label_ja", "value", "confidence", "source"])
    for f in result.fields:
        writer.writerow([f.field_key, f.field_label_ja, f.value, f.confidence, f.source])
    return buf.getvalue()
