const API_BASE = "http://localhost:8000";

export interface ApiError {
  endpoint: string;
  status: number;
  message: string;
  code?: string;
}

async function request<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });
    if (!res.ok) {
      const body = await res.text();
      throw {
        endpoint,
        status: res.status,
        message: body || res.statusText,
      } satisfies ApiError;
    }
    return res.json();
  } catch (err: unknown) {
    if (err && typeof err === "object" && "endpoint" in err) {
      throw err;
    }
    const e = err as Error;
    throw {
      endpoint,
      status: 0,
      message: e.message,
      code: e.cause ? String(e.cause) : undefined,
    } satisfies ApiError;
  }
}

export interface HealthResponse {
  status: string;
}

export interface PreflightResponse {
  status: string;
  search_provider: string;
  page_provider: string;
  external_providers_enabled: boolean;
  llm_provider: string;
  llm_ready: boolean;
  missing_credentials: string[];
  messages: string[];
}

export interface RunSummary {
  id: number;
  query: string;
  startup_id: string | null;
  status: string;
  created_at: string;
  completed_at: string | null;
}

export interface RecommendationRecord {
  id: string;
  run_id: number;
  technology: string;
  target_gap: string;
  technical_justification: string;
  business_justification: string;
  priority: string;
  implementation_complexity: string;
  suggested_next_action: string;
  startup_evidence_ids: string;
  nvidia_knowledge_ids: string;
}

export interface RunDetail {
  id: number;
  query: string;
  startup_id: string | null;
  status: string;
  created_at: string;
  completed_at: string | null;
  recommendations: RecommendationRecord[];
}

export interface StartupRecord {
  id: string;
  name: string;
  sector: string | null;
  product: string | null;
  description: string | null;
  founders: string;
  customers: string;
  funding: string | null;
  cited_technologies: string;
  ai_usage_summary: string | null;
  classification_label: string | null;
  classification_confidence: number | null;
  classification_rationale: string | null;
  created_at: string;
  updated_at: string;
}

export interface SubmitRunResponse {
  run_id: number;
  status: string;
}

export function fetchHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

export function fetchPreflight(): Promise<PreflightResponse> {
  return request<PreflightResponse>("/providers/preflight");
}

export function fetchRuns(): Promise<RunSummary[]> {
  return request<RunSummary[]>("/runs");
}

export function fetchRunById(id: number): Promise<RunDetail> {
  return request<RunDetail>(`/runs/${id}`);
}

export function fetchStartups(): Promise<StartupRecord[]> {
  return request<StartupRecord[]>("/startups");
}

export function fetchStartupById(id: string): Promise<StartupRecord> {
  return request<StartupRecord>(`/startups/${id}`);
}

export function submitRun(query: string): Promise<SubmitRunResponse> {
  return request<SubmitRunResponse>("/runs", {
    method: "POST",
    body: JSON.stringify({ query }),
  });
}
