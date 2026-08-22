import { apiClient } from "./client";

export interface SelectedTestOut {
  test_id: string;
  title: string;
  category: string;
  score: number;
  category_weight: number;
  risk_weight: number;
  reason: string;
}

export interface SkippedTestOut {
  test_id: string;
  title: string;
  category: string;
  reason: string;
}

export interface SelectionOut {
  since_commit: string;
  changed_files: string[];
  relevant_categories: string[];
  selected: SelectedTestOut[];
  skipped: SkippedTestOut[];
  estimated_tests_skipped: number;
}

export interface DuplicateOut {
  test_a_id: string;
  test_a_title: string;
  test_b_id: string;
  test_b_title: string;
  similarity: number;
}

export interface FlakyReportOut {
  test_case_id: string;
  title: string;
  flaky_score: number | null;
  run_count: number;
  status: string;
}

export async function selectTests(projectId: string): Promise<SelectionOut> {
  const { data } = await apiClient.get<SelectionOut>(`/api/testing/selection/${projectId}/select`);
  return data;
}

export async function listDuplicates(projectId: string): Promise<DuplicateOut[]> {
  const { data } = await apiClient.get<DuplicateOut[]>(`/api/testing/selection/${projectId}/duplicates`);
  return data;
}

export async function listCoverageGaps(projectId: string): Promise<string[]> {
  const { data } = await apiClient.get<string[]>(`/api/testing/selection/${projectId}/coverage-gaps`);
  return data;
}

export async function getFlakyReport(projectId: string): Promise<FlakyReportOut[]> {
  const { data } = await apiClient.get<FlakyReportOut[]>(`/api/testing/selection/${projectId}/flaky-report`);
  return data;
}
