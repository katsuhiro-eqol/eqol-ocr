"""
LLM（OpenAI）を使う処理を集約するモジュール。

Phase 1 (analyze_document):
  Vision API の OCR ブロック一覧をテキストとして渡し、
  フィールドとラベル/値ブロックの対応を学習する。
  画像は渡さない。座標は Vision API の実測値をそのまま使う。

Phase 2 (extract_fields):
  全ページ OCR ブロック一覧とテンプレートをテキストとして渡し、
  各フィールドの値を再構成する。
  氏名フィールドは value_bbox クロップ画像を Vision LLM に送り精度を高める。
"""

import base64
import io
import json
import re

from openai import OpenAI
from PIL import Image

from app.config import settings
from app.models.schema import AnchorPosition, BBox, DocumentTemplate, FieldAnchor
from app.services.google_vision import OcrBlock, crop_by_bbox

# ------------------------------------------------------------------ Phase 1
LEARN_SYSTEM_PROMPT = """\
あなたは日本の行政書類のフィールドマッチングを行うアシスタントです。
Vision APIが検出したテキストブロック一覧と、OpenCVが検出したフォームセル一覧（各セルに含まれるOCRテキスト付き）を受け取り、
指定された各フィールドに対応するラベルと値セルを特定してください。

【絶対に守るルール】
1. anchor_label_text は必ずOCRブロック一覧の "text" として実際に存在する文字列を使用すること。
   OCRが複数ブロックに分割している場合はその中の一つを使う。存在しない文字列は作らない。
2. label_bbox の座標は必ずOCRブロック一覧の値をそのまま使用すること。自分で計算・推測しない。
3. value_cell_id はセル一覧の "cell_id" から選ぶこと（整数）。
   - セルの "texts" フィールドに値テキストが含まれているセルを選ぶこと
   - 日付・住所・氏名など値が複数セルに分散している場合は、値の先頭部分を含むセルを選ぶ
     （Python 側で同じ行の隣接セルを自動マージするため、先頭セルのみ指定すればよい）
   - anchor_position が inside_cell の場合は、ラベルと同じ行にある値セルを選ぶ。
     ラベルセル自身を選んでも構わない（ラベルと値が同一セル内にある場合）。
   - 対応するセルが見つからない場合は null を返す
4. anchor_position の定義：
   - right    : ラベルと値が同じ行にあり、値がラベルの右側にある（y座標範囲が重なる）
   - left     : ラベルと値が同じ行にあり、値がラベルの左側にある
   - below    : 値の記入欄がラベルより明確に下の行にある（y座標が重ならない）
   - above    : 値の記入欄がラベルより明確に上の行にある
   - inside_cell: ラベルと値が同じ行（y座標範囲が重なる）にある（right/left との違いは
                  ラベルと値の間に明確な位置関係がない場合）
   - no_label : 対応するラベルがない
5. value（サンプル値）の抽出ルール：
   - 記入者が記入した文字・数字・日付・住所等を value とすること
   - 日付（「令和8年8月24日」等）、数字、氏名、住所、自由記述文章はすべて value として返すこと
   - チェックボックスの選択肢テキスト（「床上浸水」「床下浸水」「全壊」「半壊」「一部損壊」等）は
     印刷済みのフォームテキストであり、value として返してはならない（"" を返すこと）
   - 「同上」「〃」も正当な記入値として返すこと
   - value_cell_id のセルに記入者の文字が見当たらない場合のみ "" を返す
6. anchor_label_text の選択ルール：
   - 同じ語（例：「被害」）が複数箇所に出現する場合は、より固有・長いフレーズを選ぶこと
   - anchor_label_text はそのフィールドを一意に識別できる最も固有のラベル語句を選ぶこと
7. 出力はJSON配列のみとし、コードブロック記号（```等）は含めないこと。
"""


def _tag_blocks_with_cells(
    ocr_blocks: list[OcrBlock], cells: list[dict]
) -> list[int | None]:
    """各 OCR ブロックの中心がどのセルに属するか cell_id を返す（属さない場合 None）。"""
    result: list[int | None] = []
    for block in ocr_blocks:
        bx = (block.x0 + block.x1) / 2
        by = (block.y0 + block.y1) / 2
        found: int | None = None
        for i, cell in enumerate(cells):
            if cell["x0"] <= bx <= cell["x1"] and cell["y0"] <= by <= cell["y1"]:
                found = i
                break
        result.append(found)
    return result


def _build_cell_info(
    cells: list[dict], block_cell_ids: list[int | None], ocr_blocks: list[OcrBlock]
) -> list[dict]:
    """セル一覧に OCR テキストを付与する。セルに含まれるブロックの text を収集する。"""
    cell_texts: list[list[str]] = [[] for _ in cells]
    for block, cell_id in zip(ocr_blocks, block_cell_ids):
        if cell_id is not None:
            cell_texts[cell_id].append(block.text)
    return [
        {
            "cell_id": i,
            "x0": round(c["x0"], 1),
            "y0": round(c["y0"], 1),
            "x1": round(c["x1"], 1),
            "y1": round(c["y1"], 1),
            "texts": cell_texts[i],
        }
        for i, c in enumerate(cells)
    ]


def build_learn_prompt(
    ocr_blocks: list[OcrBlock], field_names: list[str], cells: list[dict]
) -> str:
    numbered = "\n".join(f"{i + 1}. {name}" for i, name in enumerate(field_names))

    # OCR ブロック一覧（ラベル bbox 取得用）
    blocks_json = json.dumps(
        [
            {
                "id": i,
                "text": b.text,
                "x0": round(b.x0, 1),
                "y0": round(b.y0, 1),
                "x1": round(b.x1, 1),
                "y1": round(b.y1, 1),
            }
            for i, b in enumerate(ocr_blocks)
        ],
        ensure_ascii=False,
    )

    if cells:
        block_cell_ids = _tag_blocks_with_cells(ocr_blocks, cells)
        cell_info = _build_cell_info(cells, block_cell_ids, ocr_blocks)
        cells_json = json.dumps(cell_info, ensure_ascii=False)
        cells_section = f"""
【フォームのセル一覧（OpenCV罫線検出・各セルに含まれるOCRテキスト付き）】
各セルの "texts" にそのセル内に存在するOCRテキストが含まれます。
値が記入されているセルを "value_cell_id" として出力してください。
{cells_json}
"""
        value_cell_instruction = '- value_cell_id: 値が含まれているセルの cell_id（整数、見つからなければ null）'
    else:
        cells_section = ""
        value_cell_instruction = '- value_cell_id: null（セル情報なし）'

    return f"""\
以下はVision APIで検出された書類上のテキストブロック一覧です（座標は0-1000正規化）：
{blocks_json}
{cells_section}
この書類から、次の{len(field_names)}項目を特定してください：
{numbered}

各項目について以下のキーを持つオブジェクトをJSON配列で出力してください：
- field_key: スネークケースの識別子（例: applicant_name）
- field_label_ja: 日本語ラベル
- value: 記入されている値テキスト（チェックボックス選択肢は除く。空欄なら空文字）
- section_name: 書類内のセクション名（同じラベルが複数箇所にある場合の区別用）
- anchor_label_text: ラベルとなるブロックのtext（OCRブロック一覧に実在する文字列）
- anchor_position: ラベルに対する値の位置（right/left/above/below/inside_cell/no_label）
- anchor_note: 補足説明（空文字可）
- label_bbox: ラベルブロックのbbox（OCRブロック一覧のx0/y0/x1/y1をそのまま使用）
{value_cell_instruction}
"""


def _parse_json(text: str) -> list[dict]:
    cleaned = re.sub(r"```(?:json)?|```", "", text).strip()
    return json.loads(cleaned)


def _find_value_cell(label_bbox: BBox, anchor_position: AnchorPosition, cells: list[dict]) -> BBox | None:
    """
    検出セル一覧からフィールドの値セルを特定する。

    1. ラベル中心を含むセル（ラベルセル）を除外する。
    2. anchor_position 方向で最適なセルをスコアリングする。
       - below/above: x_overlap 必須化を撤廃。「左列ラベル＋右列値」書式でも機能するよう
         ラベル上端より上から始まるセルにペナルティを加える。
    3. below/above で候補がゼロの場合のみ right/left フォールバック。
       候補が存在する場合は primary を優先（スコールスケール差の比較を避ける）。
    """
    if not cells:
        return None

    lx0, ly0, lx1, ly1 = label_bbox.x0, label_bbox.y0, label_bbox.x1, label_bbox.y1
    lcx, lcy = (lx0 + lx1) / 2, (ly0 + ly1) / 2

    # ラベルセルを除外（ラベル中心を含むセル）
    candidates = [
        c for c in cells
        if not (c["x0"] <= lcx <= c["x1"] and c["y0"] <= lcy <= c["y1"])
    ]
    if not candidates:
        return None

    def score(c: dict, pos: AnchorPosition) -> float:
        ccx = (c["x0"] + c["x1"]) / 2
        ccy = (c["y0"] + c["y1"]) / 2

        if pos == AnchorPosition.right:
            # 同一行の右側セル：ラベルの x0 より右にあること
            if c["x0"] <= lx0:
                return float("inf")
            return abs(ccy - lcy) * 3 + max(0.0, c["x0"] - lx1)

        elif pos == AnchorPosition.left:
            if c["x1"] >= lx1:
                return float("inf")
            return abs(ccy - lcy) * 3 + max(0.0, lx0 - c["x1"])

        elif pos == AnchorPosition.below:
            # セルがラベルより完全に上にある場合は除外
            if c["y1"] <= ly0:
                return float("inf")
            # ラベル上端より上から始まるセルにはペナルティ（チェックボックス行の回避）
            starts_above_penalty = max(0.0, ly0 - c["y0"]) * 3
            # ラベル下端からのギャップ（小さいほど良い）
            vertical_gap = max(0.0, c["y0"] - ly1) * 2
            # x方向の離れ（x_overlap 必須化は撤廃：左列ラベル＋右列値の書式でも対応できるよう）
            x_gap = max(0.0, max(c["x0"], lx0) - min(c["x1"], lx1)) * 0.3
            return starts_above_penalty + vertical_gap + x_gap

        elif pos == AnchorPosition.above:
            if c["y0"] >= ly1:
                return float("inf")
            ends_below_penalty = max(0.0, c["y1"] - ly1) * 3
            vertical_gap = max(0.0, ly0 - c["y1"]) * 2
            x_gap = max(0.0, max(c["x0"], lx0) - min(c["x1"], lx1)) * 0.3
            return ends_below_penalty + vertical_gap + x_gap

        else:  # inside_cell / no_label
            return abs(ccx - lcx) + abs(ccy - lcy)

    def best_for(pos: AnchorPosition) -> tuple[float, dict] | None:
        scored = [(score(c, pos), c) for c in candidates]
        valid = [(s, c) for s, c in scored if s != float("inf")]
        return min(valid, key=lambda t: t[0]) if valid else None

    primary = best_for(anchor_position)

    # below/above のフォールバック：primary が候補ゼロの場合のみ right/left を試みる。
    # primary が存在する場合はスコアに関係なく primary を優先する。
    # （right/left のスコアと below/above のスコアは同一スケールでないため比較不可）
    fallback_pos = None
    if anchor_position == AnchorPosition.below and not primary:
        fallback_pos = AnchorPosition.right
    elif anchor_position == AnchorPosition.above and not primary:
        fallback_pos = AnchorPosition.left

    fallback = best_for(fallback_pos) if fallback_pos else None

    if primary:
        best = primary[1]
    elif fallback:
        best = fallback[1]
    else:
        # 最終手段：方向を問わず最近傍のラベル以外のセル
        best = min(
            candidates,
            key=lambda c: abs((c["x0"] + c["x1"]) / 2 - lcx) + abs((c["y0"] + c["y1"]) / 2 - lcy),
        )

    # 選択セルと同一 y 範囲の右隣接セルをすべて統合して x1 を拡張する。
    # OpenCV が狭い縦仕切りを誤検出した場合でも、実際の記入欄全体をカバーできる。
    y_tol = (best["y1"] - best["y0"]) * 0.15
    same_row_right = [
        c for c in candidates
        if c["x0"] >= best["x0"]
        and abs(c["y0"] - best["y0"]) <= y_tol
        and abs(c["y1"] - best["y1"]) <= y_tol
    ]
    if same_row_right:
        best = {**best, "x1": max(c["x1"] for c in same_row_right)}

    return BBox(x0=best["x0"], y0=best["y0"], x1=best["x1"], y1=best["y1"])


def _infer_value_bbox(field: FieldAnchor) -> BBox:
    """セルが検出されない場合に label_bbox と anchor_position から value_bbox を推定する。"""
    lb = field.label_bbox
    if lb is None:
        return BBox(x0=0, y0=0, x1=200, y1=50)
    lw = max(lb.x1 - lb.x0, 30)
    lh = max(lb.y1 - lb.y0, 20)
    pos = field.anchor_position
    if pos == AnchorPosition.right:
        return BBox(x0=lb.x1 + 2, y0=lb.y0, x1=min(1000, lb.x1 + lw * 5), y1=lb.y1)
    if pos == AnchorPosition.left:
        return BBox(x0=max(0, lb.x0 - lw * 5), y0=lb.y0, x1=lb.x0 - 2, y1=lb.y1)
    if pos == AnchorPosition.below:
        return BBox(x0=lb.x0, y0=lb.y1 + 2, x1=lb.x1, y1=min(1000, lb.y1 + lh * 4))
    if pos == AnchorPosition.above:
        return BBox(x0=lb.x0, y0=max(0, lb.y0 - lh * 4), x1=lb.x1, y1=lb.y0 - 2)
    return BBox(x0=lb.x0, y0=lb.y0, x1=lb.x1, y1=lb.y1)


def _value_bbox_needs_inference(field: FieldAnchor) -> bool:
    """セルなし時のフォールバック用：value_bbox が None またはラベルと同座標か判定。"""
    if field.value_bbox is None:
        return True
    if field.label_bbox is None:
        return False
    lb, vb = field.label_bbox, field.value_bbox
    return (abs(lb.x0 - vb.x0) < 3 and abs(lb.y0 - vb.y0) < 3
            and abs(lb.x1 - vb.x1) < 3 and abs(lb.y1 - vb.y1) < 3)


def analyze_document(
    ocr_blocks: list[OcrBlock],
    field_names: list[str],
    cells: list[dict] | None = None,
) -> list[FieldAnchor]:
    """Phase 1: OCRブロック一覧 → FieldAnchor リスト。画像不要。

    LLM が出力する value_cell_id（セル一覧のインデックス）を使って
    Python 側で value_bbox を確定する。LLM に座標を推測させない。
    セルが検出されていない場合は従来の _find_value_cell / _infer_value_bbox で補完。
    """
    cells = cells or []
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_model,
        max_tokens=4000,
        messages=[
            {"role": "system", "content": LEARN_SYSTEM_PROMPT},
            {"role": "user", "content": build_learn_prompt(ocr_blocks, field_names, cells)},
        ],
    )
    text = response.choices[0].message.content or ""
    raw_fields = _parse_json(text)

    result = []
    for f in raw_fields:
        # value_cell_id は FieldAnchor スキーマに存在しないので先に取り出す
        value_cell_id = f.pop("value_cell_id", None)
        anchor = FieldAnchor(**f)

        # value_bbox の決定（優先度順）
        # 1) LLM が valid な value_cell_id を返した場合 → そのセルの境界を使用
        resolved_cell_id: int | None = None
        if value_cell_id is not None:
            try:
                resolved_cell_id = int(value_cell_id)
                if not (0 <= resolved_cell_id < len(cells)):
                    resolved_cell_id = None
            except (TypeError, ValueError):
                resolved_cell_id = None

        if resolved_cell_id is not None:
            cell = cells[resolved_cell_id]
            # 同一 y 範囲の右隣接セルをすべて統合して x1 を拡張する
            # （日付の年・月・日ボックスなど値が複数セルにまたがる場合に対応）
            y_tol = (cell["y1"] - cell["y0"]) * 0.15
            same_row_right = [
                c for c in cells
                if c["x0"] >= cell["x0"]
                and abs(c["y0"] - cell["y0"]) <= y_tol
                and abs(c["y1"] - cell["y1"]) <= y_tol
            ]
            x1 = max(c["x1"] for c in same_row_right) if same_row_right else cell["x1"]
            value_bbox = BBox(x0=cell["x0"], y0=cell["y0"], x1=x1, y1=cell["y1"])
            print(
                f"[phase1] {anchor.field_key}: cell_id={resolved_cell_id} → bbox={value_bbox}"
            )
        # 2) セルあり・cell_id なし → label_bbox から空間的にセルを推定（フォールバック）
        elif cells and anchor.label_bbox:
            if anchor.anchor_position == AnchorPosition.inside_cell:
                # inside_cell では _find_value_cell がラベルセルを除外してしまうため使わない。
                # ラベル中心を含むセルを探し、その行の全セルを統合して value_bbox とする。
                lbbox = anchor.label_bbox
                lcx = (lbbox.x0 + lbbox.x1) / 2
                lcy = (lbbox.y0 + lbbox.y1) / 2
                label_cell = next(
                    (c for c in cells if c["x0"] <= lcx <= c["x1"] and c["y0"] <= lcy <= c["y1"]),
                    None,
                )
                if label_cell:
                    y_tol = (label_cell["y1"] - label_cell["y0"]) * 0.15
                    same_row = [
                        c for c in cells
                        if abs(c["y0"] - label_cell["y0"]) <= y_tol
                        and abs(c["y1"] - label_cell["y1"]) <= y_tol
                    ]
                    x0 = min(c["x0"] for c in same_row)
                    x1 = max(c["x1"] for c in same_row)
                    value_bbox = BBox(
                        x0=x0, y0=label_cell["y0"], x1=x1, y1=label_cell["y1"]
                    )
                    print(
                        f"[phase1] {anchor.field_key}: inside_cell → 同行全セル統合 {value_bbox}"
                    )
                else:
                    value_bbox = _infer_value_bbox(anchor)
                    print(
                        f"[phase1] {anchor.field_key}: inside_cell ラベルセル未検出 → _infer_value_bbox {value_bbox}"
                    )
            else:
                value_bbox = _find_value_cell(anchor.label_bbox, anchor.anchor_position, cells)
                if value_bbox:
                    print(
                        f"[phase1] {anchor.field_key}: cell_id 未指定 → _find_value_cell fallback {value_bbox}"
                    )
                else:
                    value_bbox = _infer_value_bbox(anchor)
                    print(
                        f"[phase1] {anchor.field_key}: セルなし → _infer_value_bbox {value_bbox}"
                    )
        # 3) セルなし → anchor_position から推定
        elif _value_bbox_needs_inference(anchor):
            value_bbox = _infer_value_bbox(anchor)
        else:
            value_bbox = anchor.value_bbox

        result.append(anchor.model_copy(update={"value_bbox": value_bbox}))
    return result


# ------------------------------------------------------------------ Phase 2
EXTRACT_SYSTEM_PROMPT = """\
あなたは日本の行政書類のOCR結果解析アシスタントです。
Vision APIが検出した全テキストブロック一覧とテンプレートを受け取り、
各フィールドの値を抽出・再構成してください。

【値を見つける手順（重要）】
各フィールドについて、以下の順序で値を特定してください：

STEP 1 — ローカルラベルの特定
  value_bbox の範囲内で anchor_label_text（または field_label_ja の意味に近いサブラベル）を探す。
  label_bbox の座標に最も近いものを使用する。
  ローカルラベルが見つかった場合は、そのラベルの anchor_position 方向にある値テキストを取得する。

STEP 2 — 値の探索
  STEP 1 でラベルが特定できた場合：ラベルの anchor_position 方向にある記入テキストを返す。
  STEP 1 でラベルが特定できない場合：value_bbox 全体から field_label_ja の意味に合う値テキストを探す。
  ・value_bbox は「おおよその位置」ヒント。手書き文字は枠を超える場合があるため下方向も確認すること。
  ・同じ value_bbox を複数フィールドが共有している場合は、field_label_ja に基づいて
    適合する種類の値テキスト（住所なら住所、電話番号なら電話番号）のみを返すこと。
  ・anchor_position が "no_label" のフィールドは value_bbox にとらわれず、
    全 OCR ブロックから field_label_ja の意味に合うテキストを探すこと。
  ・sample_value が設定されている場合は、同じ形式・種別のテキストを優先して選ぶこと。
    例：sample_value が「令和8年8月24日」なら、日付形式のテキストを全体から探す。
    元号（令和・平成等）と西暦（2026年等）は同一の日付を指す場合があるため同一視すること。

STEP 3 — チェックボックス選択肢の除外
  以下のテキストは「印刷済み選択肢」であり value として返してはならない：
  ・「全壊」「大規模半壊」「半壊」「一部損壊」「床上浸水」「床下浸水」などの被害分類語が
    3つ以上同じ y 座標付近に並んでいる場合（それらすべて）
  ・「□」「■」「✓」等のチェックマークに続く語
  ※ 「住所」「電話番号」「氏名」などの項目サブラベルと隣接する値テキストは除外しないこと

STEP 4 — テキストの統合
  OCR が複数ブロックに分割した場合は統合して1つの文字列にすること。

【フィールド種別ごとの特別ルール】
- field_label_ja に「ふりがな」を含むフィールドはひらがなまたはカタカナのみを返すこと。
  漢字・英字が含まれている場合はそれを返さず、対応するひらがな・カタカナ表記を探すこと。
  ひらがな・カタカナ表記が見つからない場合は "" を返すこと。

【値として返してはいけないもの（空欄扱い）】
- 書類に元から印刷されているセクションラベル（anchor_label_text そのもの）
- 書式上の記号：「〒」「年」「月」「日」「様」「殿」「（」「）」単独など意味をなさない文字
- 損害分類チェックボックスの選択肢テキスト（STEP 3参照）

【空欄判定】
探索範囲に記入者が書いたと判断できるテキストがない場合は value を ""（空文字）にしてください。
「同上」「〃」等も正当な記入値として返してください。

【confidence】
記入値の確信度を0.0〜1.0で推定してください。空欄と確信できる場合は1.0にしてください。

出力はJSON配列のみとし、コードブロック記号（```等）は含めないこと。
"""

NAME_VISION_SYSTEM_PROMPT = """\
あなたは日本語の手書き文字を読み取るOCRアシスタントです。
行政書類の氏名記入欄の画像から、記入された文字を正確に読み取ってください。

ルール：
- 印刷された枠線・ラベル文字（「氏名」「様」等）は無視し、手書き文字のみを返すこと
- ふりがなのヒントが与えられた場合は、それと音が一致する漢字表記を優先すること
- 記入がない・読み取れない場合は "" を返すこと
- 出力はJSONオブジェクトのみ: {"value": "...", "confidence": 0.0}
"""


def _crop_image_b64(image: Image.Image, bbox: BBox) -> str:
    """value_bbox の範囲でクロップし JPEG base64 を返す。"""
    cropped = crop_by_bbox(image, bbox)
    buf = io.BytesIO()
    cropped.save(buf, format="JPEG", quality=90)
    return base64.standard_b64encode(buf.getvalue()).decode()


def _extract_name_with_vision(
    client: OpenAI, b64: str, furigana_hint: str = ""
) -> dict | None:
    """氏名フィールドのクロップ画像を Vision LLM に送り {"value": ..., "confidence": ...} を返す。"""
    hint_text = f"\nふりがなのヒント：「{furigana_hint}」" if furigana_hint else ""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=100,
            messages=[
                {"role": "system", "content": NAME_VISION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64}",
                                "detail": "low",
                            },
                        },
                        {
                            "type": "text",
                            "text": f"画像の手書き氏名を読み取ってください。{hint_text}",
                        },
                    ],
                },
            ],
        )
        raw = resp.choices[0].message.content or ""
        raw = re.sub(r"```[a-z]*\n?", "", raw).strip().strip("`")
        return json.loads(raw)
    except Exception as e:
        print(f"[phase2] vision name extraction failed: {e}")
        return None


def build_extract_prompt(ocr_blocks: list[OcrBlock], template: DocumentTemplate) -> str:
    blocks_json = json.dumps(
        [
            {
                "text": b.text,
                "x0": round(b.x0, 1),
                "y0": round(b.y0, 1),
                "x1": round(b.x1, 1),
                "y1": round(b.y1, 1),
            }
            for b in ocr_blocks
        ],
        ensure_ascii=False,
    )
    fields_json = json.dumps(
        [
            {
                "field_key": f.field_key,
                "field_label_ja": f.field_label_ja,
                "anchor_label_text": f.anchor_label_text,
                "anchor_position": f.anchor_position.value,
                "section_name": f.section_name,
                "label_bbox": f.label_bbox.model_dump() if f.label_bbox else None,
                "value_bbox": f.value_bbox.model_dump() if f.value_bbox else None,
                "sample_value": f.value if f.value else None,
            }
            for f in template.fields
        ],
        ensure_ascii=False,
    )
    return f"""\
【OCRブロック一覧（座標は0-1000正規化）】
{blocks_json}

【テンプレート（抽出対象フィールド一覧）】
{fields_json}

上記テンプレートの各フィールドについて、OCRブロックを統合・再構成して値を抽出し、
以下の形式のJSON配列を返してください：
[
  {{"field_key": "...", "value": "...", "confidence": 0.0}},
  ...
]
"""


def extract_fields(
    ocr_blocks: list[OcrBlock],
    template: DocumentTemplate,
    page_image: Image.Image | None = None,
) -> list[dict]:
    """
    Phase 2: 全ページOCRブロック + テンプレート → 各フィールドの値。
    page_image が渡された場合、氏名フィールドは value_bbox クロップを Vision LLM で再抽出する。
    戻り値: [{"field_key": str, "value": str, "confidence": float}, ...]
    """
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_model,
        max_tokens=2000,
        messages=[
            {"role": "system", "content": EXTRACT_SYSTEM_PROMPT},
            {"role": "user", "content": build_extract_prompt(ocr_blocks, template)},
        ],
    )
    text = response.choices[0].message.content or ""
    results = _parse_json(text)

    if page_image is None:
        return results

    # 氏名フィールドを Vision LLM で再抽出（ふりがなをヒントとして利用）
    field_map = {f.field_key: f for f in template.fields}
    furigana_values = {
        r["field_key"]: r.get("value", "")
        for r in results
        if "furigana" in r.get("field_key", "")
    }

    _NAME_LABELS = {"氏名", "名前"}

    for item in results:
        field_key = item.get("field_key", "")
        template_field = field_map.get(field_key)
        if not template_field or not template_field.value_bbox:
            continue
        # field_key に "name" を含み、かつ field_label_ja に氏名系の語を含むフィールドのみ対象
        # 完全一致ではなく部分一致（「窓口に来られた方の氏名」等にも対応）
        # ふりがなフィールドはひらがなのため Vision 不要
        if (
            "name" not in field_key
            or "furigana" in field_key
            or "ふりがな" in template_field.field_label_ja
            or not any(label in template_field.field_label_ja for label in _NAME_LABELS)
        ):
            continue

        # テキスト抽出結果が空欄または「同上」系の確定値であれば Vision 不要
        text_value = item.get("value", "")
        if not text_value or text_value in {"同上", "〃", "同左"}:
            continue

        # 対応するふりがなキーを推定（例: applicant_name → applicant_name_furigana）
        furigana_hint = furigana_values.get(field_key + "_furigana", "")

        b64 = _crop_image_b64(page_image, template_field.value_bbox)
        vision_result = _extract_name_with_vision(client, b64, furigana_hint)
        if vision_result and vision_result.get("value") is not None:
            print(
                f"[phase2] {field_key}: text='{item.get('value')}'"
                f" → vision='{vision_result['value']}' (furigana_hint='{furigana_hint}')"
            )
            item["value"] = vision_result["value"]
            item["confidence"] = vision_result.get("confidence", item.get("confidence", 0.0))

    # ふりがなフィールドの検証：ひらがな・カタカナ以外（漢字・英字等）が含まれる場合は空欄にする
    _HIRAGANA_RE = re.compile(r"^[ぁ-ん゙゚ァ-ヶｧ-ﾝﾞﾟーｰ・\s　]+$")
    for item in results:
        field_key = item.get("field_key", "")
        template_field = field_map.get(field_key)
        if not template_field:
            continue
        if "ふりがな" not in template_field.field_label_ja and "furigana" not in field_key:
            continue
        value = item.get("value", "")
        if value and not _HIRAGANA_RE.match(value):
            print(f"[phase2] {field_key}: ふりがな非ひらがな検出 '{value}' → 空欄")
            item["value"] = ""
            item["confidence"] = 0.0

    return results
