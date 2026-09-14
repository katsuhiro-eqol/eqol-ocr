import { useEffect, useRef, useState } from "react";
import { type AnonymousUsageInfo, type TemplateInfo, extractDocument, fetchTemplates, fetchUsage, learnDocument } from "../api/client";

export interface ExtractedField {
  field_key: string;
  field_label_ja: string;
  value: string;
  confidence: number;
  source: string;
  debug_image_b64?: string | null;
}

export interface ExtractionResult {
  document_id: string;
  template_id?: string | null;
  fields: ExtractedField[];
  needs_fallback: boolean;
}

function isExtractionResult(v: unknown): v is ExtractionResult {
  return (
    typeof v === "object" &&
    v !== null &&
    "fields" in v &&
    Array.isArray((v as ExtractionResult).fields) &&
    "document_id" in v
  );
}

const NEW_FORMAT = "新規フォーマット";

function UsageBar({ label, used, limit }: { label: string; used: number; limit: number }) {
  const remaining = limit - used;
  const pct = Math.min((used / limit) * 100, 100);
  const isWarning = remaining <= Math.ceil(limit * 0.2);
  return (
    <div className="space-y-0.5">
      <div className="flex justify-between text-xs text-gray-600">
        <span>{label}</span>
        <span className={isWarning ? "text-red-500 font-medium" : ""}>
          残り {remaining} / {limit} 回
        </span>
      </div>
      <div className="h-1.5 w-full bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${isWarning ? "bg-red-400" : "bg-blue-400"}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

interface DocumentUploadProps {
  onResult?: (r: ExtractionResult) => void;
  onIsNewFormatChange?: (isNew: boolean) => void;
  documentType: string;
  fieldList: string[];
}

export function DocumentUpload({ onResult, onIsNewFormatChange, documentType, fieldList }: DocumentUploadProps) {
  const [templateId, setTemplateId] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [templates, setTemplates] = useState<TemplateInfo[]>([]);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const [succeeded, setSucceeded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [usageInfo, setUsageInfo] = useState<AnonymousUsageInfo | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const comboboxRef = useRef<HTMLDivElement>(null);

  const isNew = templateId === NEW_FORMAT;

  const refreshUsage = () => {
    fetchUsage().then((info) => {
      setUsageInfo(info.limited ? info : null);
    });
  };

  useEffect(() => { refreshUsage(); }, []);

  useEffect(() => {
    if (!dropdownOpen) return;
    fetchTemplates()
      .then(setTemplates)
      .catch(() => setTemplates([]));
  }, [dropdownOpen]);

  useEffect(() => {
    function onPointerDown(e: PointerEvent) {
      if (comboboxRef.current && !comboboxRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, []);

  function selectTemplate(info: TemplateInfo | null) {
    const willBeNew = info === null;
    if (willBeNew) {
      setTemplateId(NEW_FORMAT);
      setDisplayName(NEW_FORMAT);
    } else {
      setTemplateId(info.template_id);
      setDisplayName(info.document_type);
    }
    setDropdownOpen(false);
    setError(null);
    setSucceeded(false);
    onIsNewFormatChange?.(willBeNew);
  }

  async function handleFile(file: File) {
    setError(null);
    setSucceeded(false);
    setFileName(file.name);

    if (!templateId) {
      setError("テンプレートを選択してください");
      return;
    }
    if (isNew && !documentType.trim()) {
      setError("書類種別を入力してください");
      return;
    }
    if (isNew && fieldList.length === 0) {
      setError("抽出項目を1つ以上追加してください");
      return;
    }

    setLoading(true);
    try {
      const data = isNew
        ? await learnDocument(documentType.trim(), fieldList.join(","), file)
        : await extractDocument(templateId, file, true);
      setSucceeded(true);
      if (!isNew && isExtractionResult(data)) {
        onResult?.(data);
      }
      refreshUsage();
    } catch (e) {
      setError(e instanceof Error ? e.message : "エラーが発生しました");
      refreshUsage();
    } finally {
      setLoading(false);
    }
  }

  function onInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  }

  function onDragOver(e: React.DragEvent) {
    e.preventDefault();
    setDragging(true);
  }

  function onDragLeave() {
    setDragging(false);
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  }

  return (
    <div className="flex flex-col items-center gap-6 p-8 w-full max-w-lg mx-auto">

      {/* テンプレート選択 */}
      <div className="w-full" ref={comboboxRef}>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          書類種別・フォーマット
        </label>
        <div className="relative">
          <button
            type="button"
            onClick={() => setDropdownOpen((o) => !o)}
            className="w-full flex items-center justify-between gap-2 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-left shadow-sm hover:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <span className={displayName ? "text-gray-900" : "text-gray-400"}>
              {displayName || "テンプレートを選択..."}
            </span>
            <svg
              className={`w-4 h-4 text-gray-400 transition-transform ${dropdownOpen ? "rotate-180" : ""}`}
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {dropdownOpen && (
            <ul className="absolute z-10 mt-1 w-full rounded-lg border border-gray-200 bg-white shadow-lg overflow-hidden">
              {/* 新規フォーマット */}
              <li>
                <button
                  type="button"
                  onClick={() => selectTemplate(null)}
                  className={`w-full px-3 py-2 text-sm text-left text-blue-600 font-medium border-b border-gray-100 hover:bg-blue-50 hover:text-blue-700 transition-colors
                    ${isNew ? "bg-blue-50" : ""}
                  `}
                >
                  ＋ {NEW_FORMAT}
                </button>
              </li>
              {/* 既存テンプレート */}
              {templates.map((t) => (
                <li key={t.template_id}>
                  <button
                    type="button"
                    onClick={() => selectTemplate(t)}
                    className={`w-full px-3 py-2 text-sm text-left text-gray-800 hover:bg-blue-50 hover:text-blue-700 transition-colors
                      ${templateId === t.template_id ? "bg-blue-50 text-blue-700" : ""}
                    `}
                  >
                    {t.document_type}
                  </button>
                </li>
              ))}
              {templates.length === 0 && (
                <li className="px-3 py-2 text-xs text-gray-400">保存済みテンプレートなし</li>
              )}
            </ul>
          )}
        </div>
      </div>

      {/* 新規フォーマット選択中の案内 */}
      {isNew && (
        <p className="w-full text-xs text-blue-600 bg-blue-50 border border-blue-200 rounded-lg px-3 py-2">
          右パネルで書類種別名と抽出項目を入力してから、書類をアップロードしてください。
        </p>
      )}

      {/* ドロップゾーン */}
      <div
        onClick={() => fileInputRef.current?.click()}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        className={`
          w-full flex flex-col items-center justify-center gap-3
          border-2 border-dashed rounded-xl p-12 cursor-pointer
          transition-colors duration-200
          ${dragging
            ? "border-blue-500 bg-blue-50 text-blue-600"
            : "border-gray-300 bg-gray-50 text-gray-500 hover:border-blue-400 hover:bg-blue-50"
          }
        `}
      >
        <svg className="w-12 h-12 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
            d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
        </svg>
        <p className="text-sm font-medium">ファイルをドロップ、またはクリックして選択</p>
        <p className="text-xs opacity-60">PNG / JPEG / PDF</p>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*,application/pdf"
          className="hidden"
          onChange={onInputChange}
        />
      </div>

      {fileName && !loading && (
        <p className="text-sm text-gray-600">
          選択中: <span className="font-medium">{fileName}</span>
        </p>
      )}

      {loading && (
        <div className="flex items-center gap-2 text-blue-500">
          <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
          </svg>
          <span className="text-sm">{isNew ? "解析・保存中..." : "解析中..."}</span>
        </div>
      )}

      {error && (
        <p className="text-sm text-red-500">{error}</p>
      )}

      {succeeded && (
        <p className="text-sm text-green-600 flex items-center gap-1.5">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          {isNew ? "テンプレートを保存しました" : "読み取り完了 — 右パネルに結果を表示しました"}
        </p>
      )}

      {usageInfo && (
        <div className="w-full border border-gray-200 rounded-lg p-3 bg-gray-50 space-y-2">
          <p className="text-xs font-medium text-gray-500">無料枠の使用回数</p>
          <UsageBar label="学習（Phase1）" used={usageInfo.phase1.used} limit={usageInfo.phase1.limit} />
          <UsageBar label="読取（Phase2）" used={usageInfo.phase2.used} limit={usageInfo.phase2.limit} />
          <p className="text-xs text-gray-400 pt-0.5">ユーザー登録で制限なし</p>
        </div>
      )}
    </div>
  );
}
