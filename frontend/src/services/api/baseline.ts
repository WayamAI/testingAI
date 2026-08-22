import { apiClient } from "./client";

export interface GeneratedTestOut {
  id: string;
  category: string;
  title: string;
  code: string;
  confidence: number;
  source: string;
  commit_sha: string | null;
  file_path: string | null;
}

export interface BaselineScanOut {
  scan_id: string | null;
  generated: number;
  rejected_invalid_syntax: number;
  source: string;
  categories_scanned: string[];
  message: string | null;
  tests: GeneratedTestOut[];
}

export async function runBaselineScan(projectId: string): Promise<BaselineScanOut> {
  const { data } = await apiClient.post<BaselineScanOut>(`/api/testing/baseline/${projectId}/scan`);
  return data;
}

export async function listBaselineTests(projectId: string): Promise<GeneratedTestOut[]> {
  const { data } = await apiClient.get<GeneratedTestOut[]>(`/api/testing/baseline/${projectId}/tests`);
  return data;
}
