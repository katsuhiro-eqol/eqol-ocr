# eqol-ocr

項目特化・低価格のシンプルなAI-OCRサービス（MVP雛形）

## 設計方針

- **Phase 1（初見フォーマット解析）**: Claude API（vision）で書類を解析し、指定項目の値と
  「アンカー情報」（セクション名＋ラベル文字列＋相対位置＋bbox）を抽出する。
- **Phase 2（既知フォーマットの定常処理）**: 保存済みテンプレートの固定座標をもとに値領域を
  クロップし、Google Cloud Vision API（`document_text_detection`）で手書き文字を読み取る。
- **フォールバック**: Phase 2の抽出結果が低信頼度・空欄の場合、自動的にPhase 1へ差し戻す。

藤枝市「罹災・被災証明書交付申請書」を題材にした検証で、以下が確認済み：
- 印字ラベルはTesseract等の軽量OCRでも検出可能
- 手書きの値は軽量OCRでは読み取れず、専用の手書き対応OCR（Google Vision API等）が必要
- 同一書類内にラベルが重複する（「住所」「氏名」等）ため、`section_name` での曖昧性解消が必須

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # 各種APIキーを設定
uvicorn app.main:app --reload
```

## ディレクトリ構成

```
app/
  main.py              FastAPIアプリのエントリーポイント
  config.py            環境変数・設定
  models/schema.py      Pydanticモデル（抽出結果・テンプレート）
  routers/documents.py  アップロード・ステータス確認・CSV取得エンドポイント
  services/
    claude_vision.py   Phase1: Claude APIでの書類解析
    google_vision.py   Phase2: Google Vision APIでのOCR
    template_store.py  テンプレートの保存・読み込み
    matcher.py         アンカー情報とOCR結果の照合ロジック
    csv_export.py      CSV出力
  core/fallback.py      フォールバック判定ロジック
tests/                 テストコード（雛形のみ）
```

## 次にやること

- [ ] `app/services/claude_vision.py` に、これまで設計したプロンプトを実装
- [ ] `app/services/google_vision.py` の認証情報設定（`GOOGLE_APPLICATION_CREDENTIALS`）
- [ ] テンプレート保存先をJSONファイルからDB（PostgreSQL等）へ移行
- [ ] 藤枝市罹災証明書サンプルでのE2Eテスト
