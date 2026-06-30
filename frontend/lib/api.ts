const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

export type Decision = {
  department: string;
  it_access: string[];
  finance_tier: string;
};

export type BrainRule = {
  id: string;
  pattern: Record<string, string>;
  decision: Decision;
  source_case: string;
  times_applied: number;
  last_applied_at: string | null;
};

export type Approval = {
  id: string;
  question: string;
  status: "pending" | "resolved";
  facts: { name: string; role: string; location: string; source_text: string };
  options: { label: "Sales" | "Engineering"; impact: string[] }[];
};

export type AuditEvent = {
  id: string;
  case_id: string;
  event_type: string;
  summary: string;
  timestamp: string;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`${response.status} ${response.statusText}: ${detail}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  reset: () => request<{ rules: BrainRule[] }>("/api/demo/reset", { method: "POST" }),
  runDemo: () => request<{ steps: { label: string; data: unknown }[]; state: { rules: BrainRule[]; approvals: Approval[]; audit: AuditEvent[] } }>("/api/demo/run", { method: "POST" }),
  intake: (text: string) => request<unknown>("/api/workflows/intake", { method: "POST", body: JSON.stringify({ text }) }),
  approvals: () => request<{ approvals: Approval[] }>("/api/approvals"),
  resolve: (approvalId: string, decision: "Sales" | "Engineering") =>
    request<{ rule: BrainRule }>(`/api/approvals/${approvalId}/resolve`, {
      method: "POST",
      body: JSON.stringify({ decision, rationale: "At this company, Sales Engineer belongs to Sales." }),
    }),
  rules: () => request<{ rules: BrainRule[] }>("/api/brain/rules"),
  audit: () => request<{ events: AuditEvent[] }>("/api/audit"),
};
