import { apiClient } from "./client";

export interface ApiTestResultOut {
  name: string;
  status: string;
  status_code: number | null;
  duration_ms: number;
}

export interface ApiTestRunOut {
  run_id: string;
  endpoints_tested: number;
  results: ApiTestResultOut[];
}

export async function runApiTests(projectId: string, baseUrl: string): Promise<ApiTestRunOut> {
  const { data } = await apiClient.post<ApiTestRunOut>(`/api/projects/${projectId}/api-tests`, { base_url: baseUrl });
  return data;
}
