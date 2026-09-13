import { useState } from "react";

export const INITIAL_FIELD_LIST = [
  "申請年月日", "申請者住所", "申請者電話番号", "申請者氏名",
  "申請者名ふりがな", "現在の連絡先", "現在の電話番号",
  "窓口に来られた方の住所", "窓口に来られた方の電話番号",
  "窓口に来られた方の氏名", "窓口に来られた方の名前ふりがな",
  "申請者との続柄", "罹災原因", "被災住家の所在地",
  "住家の被害", "住家以外の家屋への被害",
];

interface Props {
  documentType: string;
  onDocumentTypeChange: (v: string) => void;
  fieldList: string[];
  onFieldListChange: (list: string[]) => void;
}

const NOTES = [
  {
    title: "フォーマット登録用書面では検出項目は入力必須（空欄NG)",
    body: "AIはサンプル書類の記入値から検出項目位置と書式を学習します。",
  },
  {
    title: "検出項目名は書類内で一意となるように設定",
    body: "「氏名」ではなく「申請者氏名」「窓口来訪者氏名」のように、書類内で識別できる名称を使用してください。書面にその名称そのものがなくてもAIが意味を解釈します。",
  },
  {
    title: "読み取り結果に誤りが多く発生するときは",
    body: "書類の解像度が低い可能性があります。300dpi以上の解像度でスキャンした書類を使用してください。",
  },
];

const STEPS = ["書類情報を入力", "左パネルから書類をアップロード", "AI が学習・テンプレートを保存"];

export function NewFormatPanel({ documentType, onDocumentTypeChange, fieldList, onFieldListChange }: Props) {
  const [fieldInput, setFieldInput] = useState("");
  const [showGuide, setShowGuide] = useState(false);

  function addField() {
    const trimmed = fieldInput.trim();
    if (!trimmed || fieldList.includes(trimmed)) return;
    onFieldListChange([...fieldList, trimmed]);
    setFieldInput("");
  }

  function removeField(index: number) {
    onFieldListChange(fieldList.filter((_, i) => i !== index));
  }

return (
    <div className="flex flex-col h-full overflow-hidden">

      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 flex-shrink-0 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-sm font-semibold text-gray-800">新規フォーマット登録</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            書類のレイアウトを AI が学習し、以降の読み取りに自動適用します
          </p>
        </div>
        <button
          type="button"
          onClick={() => setShowGuide(true)}
          className="flex-shrink-0 flex items-center gap-1.5 rounded-lg border border-green-200 bg-green-50 px-3 py-1.5 text-xs font-medium text-green-700 hover:bg-green-100 hover:border-green-300 transition-colors"
        >
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          登録解説を見る
        </button>
      </div>

      {/* 解説画像モーダル */}
      {showGuide && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
          onClick={() => setShowGuide(false)}
        >
          <div
            className="relative max-w-4xl w-full max-h-[90vh] bg-white rounded-2xl shadow-2xl overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between px-5 py-3 border-b border-gray-200">
              <span className="text-sm font-semibold text-gray-800">OCRフォーマット登録解説</span>
              <button
                type="button"
                onClick={() => setShowGuide(false)}
                className="rounded-lg p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
                aria-label="閉じる"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="overflow-auto max-h-[calc(90vh-52px)]">
              <img
                src="/OCRフォーマット登録解説.png"
                alt="OCRフォーマット登録解説"
                className="w-full h-auto"
              />
            </div>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto px-6 py-5 flex flex-col gap-6">

        {/* Step indicator */}
        <div className="flex items-start gap-0">
          {STEPS.map((label, i) => (
            <div key={i} className="flex items-start flex-1 last:flex-none">
              <div className="flex flex-col items-center gap-1.5 flex-shrink-0">
                <div className={`w-7 h-7 rounded-full text-xs font-bold flex items-center justify-center ring-2 ${
                  i === 0
                    ? "bg-blue-600 text-white ring-blue-200"
                    : "bg-gray-100 text-gray-400 ring-gray-100"
                }`}>
                  {i + 1}
                </div>
                <span className="text-[10px] text-gray-500 text-center leading-tight whitespace-pre-line w-16">
                  {label}
                </span>
              </div>
              {i < STEPS.length - 1 && (
                <div className="flex-1 h-px bg-gray-200 mt-3.5 mx-1" />
              )}
            </div>
          ))}
        </div>

        {/* 注意事項 */}
        <div className="rounded-xl border border-amber-200 bg-amber-50 overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-amber-200 bg-amber-100/60">
            <svg className="w-4 h-4 text-amber-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd"/>
            </svg>
            <span className="text-xs font-bold text-amber-700">学習前の確認事項</span>
          </div>
          <ul className="divide-y divide-amber-100">
            {NOTES.map((note, i) => (
              <li key={i} className="px-4 py-1.5 flex gap-2.5">
                <span className="text-amber-400 font-bold text-xs mt-0.5 flex-shrink-0">•</span>
                <div>
                  <span className="text-xs font-semibold text-amber-800">{note.title}</span>
                  <span className="text-xs text-amber-700"> — {note.body}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>

        {/* 書類種別名 */}
        <div>
          <label className="block text-xs font-semibold text-gray-700 mb-1.5">
            書類種別名 <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={documentType}
            onChange={(e) => onDocumentTypeChange(e.target.value)}
            placeholder="例：藤枝市罹災・被災証明書交付申請書（第４号様式）"
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* 抽出項目 */}
        <div>
          <label className="block text-xs font-semibold text-gray-700 mb-1.5">
            抽出する項目 <span className="text-red-500">*</span>
            <span className="ml-2 font-normal text-gray-400">{fieldList.length} 項目</span>
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={fieldInput}
              onChange={(e) => setFieldInput(e.target.value)}

              placeholder="例：申請者氏名（書類内で一意となるよう項目名を設定）"
              className="flex-1 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="button"
              onClick={addField}
              disabled={!fieldInput.trim()}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              追加
            </button>
          </div>

          {fieldList.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {fieldList.map((f, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1 rounded-full bg-white border border-blue-200 px-2.5 py-1 text-xs text-blue-800"
                >
                  {f}
                  <button
                    type="button"
                    onClick={() => removeField(i)}
                    className="text-blue-300 hover:text-red-500 transition-colors leading-none ml-0.5"
                    aria-label={`${f}を削除`}
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
