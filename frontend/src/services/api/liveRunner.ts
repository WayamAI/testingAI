import { apiClient } from "./client";

export interface LiveRunResultOut {
  title: string;
  category: string;
  status: string;
  duration_ms: number;
  screenshot_path: string | null;
}

export interface LiveRunOut {
  run_id: string;
  url: string;
  categories: string[];
  source: string;
  total: number;
  passed: number;
  failed: number;
  rejected_invalid_syntax: number;
  results: LiveRunResultOut[];
}

export interface LiveRunSummaryOut {
  id: string;
  url: string;
  categories: string[];
  source: string;
  total: number;
  passed: number;
  failed: number;
}

export async function runLiveTests(projectId: string, url: string): Promise<LiveRunOut> {
  const { data } = await apiClient.post<LiveRunOut>(`/api/testing/live-runner/${projectId}/run`, { url });
  return data;
}

export async function listLiveRuns(projectId: string): Promise<LiveRunSummaryOut[]> {
  const { data } = await apiClient.get<LiveRunSummaryOut[]>(`/api/testing/live-runner/${projectId}/runs`);
  return data;
}
