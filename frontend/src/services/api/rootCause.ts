import { apiClient } from "./client";

export interface AnalyzeResultOut {
  id: string;
  root_cause: string;
  confidence: number;
  recommendation: string;
  affected_component: string;
  likely_commit_sha: string | null;
  likely_commit_message: string | null;
  source: string;
  git_correlation_available: boolean;
}

export interface HistoryEntryOut {
  id: string;
  test_case_title: string;
  root_cause: string;
  confidence: number;
  likely_commit_sha: string | null;
  source: string;
}

export async function analyzeRootCause(
  projectId: string, errorMessage: string, stackTrace: string, testCaseTitle: string
): Promise<AnalyzeResultOut> {
  const { data } = await apiClient.post<AnalyzeResultOut>(`/api/testing/root-cause/${projectId}/analyze`, {
    error_message: errorMessage, stack_trace: stackTrace, test_case_title: testCaseTitle,
  });
  return data;
}

export async function listRootCauseHistory(projectId: string): Promise<HistoryEntryOut[]> {
  const { data } = await apiClient.get<HistoryEntryOut[]>(`/api/testing/root-cause/${projectId}/history`);
  return data;
}
