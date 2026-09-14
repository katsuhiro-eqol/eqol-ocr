const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

function getDeviceId(): string {
  const key = "eqol_device_id";
  try {
    let id = localStorage.getItem(key);
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem(key, id);
    }
    return id;
  } catch {
    return "fallback-device";
  }
}

function deviceHeaders(): Record<string, string> {
  return { "X-Device-Id": getDeviceId() };
}

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
  const res = await fetch(`${API_BASE}/documents/templates`, {
    headers: deviceHeaders(),
  });
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
    headers: deviceHeaders(),
    body: formData,
  });

  if (res.status === 429) {
    const data = await res.json().catch(() => ({}));
    throw new LimitExceededError(data.detail ?? "使用上限に達しました");
  }
  if (!res.ok) throw new Error("テンプレートの学習に失敗しました");
  console.log("learnDocument res:", res);
  return res.json();
}

export async function extractDocument(templateId: string, file: File, debug = false) {
  const formData = new FormData();
  formData.append("file", file);

  const url = `${API_BASE}/documents/templates/${encodeURIComponent(templateId)}/extract${debug ? "?debug=true" : ""}`;
  const res = await fetch(url, {
    method: "POST",
    headers: deviceHeaders(),
    body: formData,
  });

  if (res.status === 429) {
    const data = await res.json().catch(() => ({}));
    throw new LimitExceededError(data.detail ?? "使用上限に達しました");
  }
  if (!res.ok) throw new Error("抽出に失敗しました");
  return res.json();
}

export interface UsageInfo {
  limited: false;
}

export interface AnonymousUsageInfo {
  limited: true;
  phase1: { used: number; limit: number };
  phase2: { used: number; limit: number };
}

export async function fetchUsage(): Promise<UsageInfo | AnonymousUsageInfo> {
  try {
    const res = await fetch(`${API_BASE}/documents/usage`, {
      headers: deviceHeaders(),
    });
    if (!res.ok) return { limited: false };
    return res.json();
  } catch {
    return { limited: false };
  }
}

export class LimitExceededError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "LimitExceededError";
  }
}
