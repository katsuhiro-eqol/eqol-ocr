const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function pingHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`, {
      signal: AbortSignal.timeout(4000),
    });
    return res.ok;
  } catch {
    return false;
  }
}

export interface TemplateInfo {
  template_id: string;
  document_type: string;
}

export async function fetchTemplates(): Promise<TemplateInfo[]> {
  const res = await fetch(`${API_BASE}/documents/templates`);
  if (!res.ok) throw new Error("テンプレート一覧の取得に失敗しました");
  return res.json();
}

export async function learnDocument(documentType: string, fields: string, file: File) {
  const formData = new FormData();
  formData.append("document_type", documentType);
  formData.append("fields", fields);
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/documents/templates/learn`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error("テンプレートの学習に失敗しました");
  console.log("learnDocument res:", res);
  return res.json();
}

export async function extractDocument(templateId: string, file: File, debug = false) {
  const formData = new FormData();
  formData.append("file", file);

  const url = `${API_BASE}/documents/templates/${encodeURIComponent(templateId)}/extract${debug ? "?debug=true" : ""}`;
  const res = await fetch(url, { method: "POST", body: formData });

  if (!res.ok) throw new Error("抽出に失敗しました");
  return res.json();
}
