import type { ExtractionResult } from "./DocumentUpload";

interface Props {
  results: ExtractionResult[];
  onClear: () => void;
}

function confBorder(c: number) {
  if (c >= 0.8) return "border-l-green-400";
  if (c >= 0.5) return "border-l-yellow-400";
  return "border-l-red-400";
}

function confBadge(c: number) {
  if (c >= 0.8) return "text-green-700 bg-green-100";
  if (c >= 0.5) return "text-yellow-700 bg-yellow-100";
  return "text-red-600 bg-red-100";
}

function getColumns(results: ExtractionResult[]): string[] {
  const seen = new Set<string>();
  const cols: string[] = [];
  for (const r of results) {
    for (const f of r.fields) {
      if (!seen.has(f.field_label_ja)) {
        seen.add(f.field_label_ja);
        cols.push(f.field_label_ja);
      }
    }
  }
  return cols;
}

function exportCSV(results: ExtractionResult[], columns: string[]) {
  const header = ["No.", ...columns];
  const rows = results.map((r, i) => [
    String(i + 1),
    ...columns.map(col => r.fields.find(f => f.field_label_ja === col)?.value ?? ""),
  ]);

  const csv = [header, ...rows]
    .map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(","))
    .join("\r\n");

  const blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `ocr_${new Date().toISOString().slice(0, 10)}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export function DetectedValues({ results, onClear }: Props) {
  const columns = getColumns(results);

  if (results.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4 text-gray-400">
        <svg className="w-16 h-16 opacity-25" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p className="text-sm">書類をアップロードすると結果がここに表示されます</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-gray-200 bg-white flex-shrink-0">
        <div>
          <h2 className="text-sm font-semibold text-gray-800">読み取り結果</h2>
          <p className="text-xs text-gray-400 mt-0.5">{results.length} 件 / {columns.length} 項目</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={onClear}
            className="rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-500 hover:bg-gray-50 hover:text-gray-700 transition-colors"
          >
            クリア
          </button>
          <button
            onClick={() => exportCSV(results, columns)}
            className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-blue-700 transition-colors shadow-sm"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            CSV 出力
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto">
        <table className="w-full text-sm border-collapse">
          <thead className="sticky top-0 z-10">
            <tr className="bg-gray-50 border-b-2 border-gray-200">
              <th className="sticky left-0 z-20 bg-gray-50 px-3 py-2.5 text-center text-xs font-semibold text-gray-400 border-r border-gray-200 w-10">
                No.
              </th>
              {columns.map(col => (
                <th
                  key={col}
                  className="px-3 py-2.5 text-left text-xs font-semibold text-gray-600 whitespace-nowrap border-r border-gray-100 last:border-r-0 min-w-[120px] max-w-[240px]"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {results.map((result, rowIdx) => {
              const fieldMap = new Map(result.fields.map(f => [f.field_label_ja, f]));
              return (
                <tr
                  key={result.document_id}
                  className={`border-b border-gray-100 last:border-b-0 hover:bg-blue-50/30 transition-colors ${
                    rowIdx % 2 === 0 ? "bg-white" : "bg-gray-50/40"
                  }`}
                >
                  <td className="sticky left-0 bg-inherit px-3 py-2 text-xs text-gray-400 font-mono text-center border-r border-gray-200 whitespace-nowrap">
                    {rowIdx + 1}
                  </td>
                  {columns.map(col => {
                    const field = fieldMap.get(col);
                    if (!field) {
                      return (
                        <td key={col} className="px-3 py-2 text-xs text-gray-300 border-r border-gray-100 last:border-r-0">
                          —
                        </td>
                      );
                    }
                    return (
                      <td
                        key={col}
                        className={`px-2 py-1.5 border-r border-gray-100 last:border-r-0 border-l-2 ${confBorder(field.confidence)}`}
                      >
                        <div className="flex items-start justify-between gap-1.5 min-w-0">
                          <span className="text-sm text-gray-800 break-all leading-snug min-w-0">
                            {field.value || <span className="text-gray-300 text-xs italic">空</span>}
                          </span>
                          <span className={`flex-shrink-0 text-[9px] font-mono px-1 py-0.5 rounded-full leading-none ${confBadge(field.confidence)}`}>
                            {(field.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
