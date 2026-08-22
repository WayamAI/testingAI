import { apiClient } from "./client";

export interface AttemptOut {
  id: string;
  url: string;
  original_selector: string;
  proposed_selector: string;
  ai_confidence: number;
  ai_reasoning: string;
  source: string;
  live_validation_count: number;
  status: string;
  target_file: string | null;
  target_line: number | null;
  applied: boolean;
}

export async function proposeHeal(
  projectId: string, url: string, originalSelector: string, failureContext: string
): Promise<AttemptOut> {
  const { data } = await apiClient.post<AttemptOut>(`/api/testing/self-heal/${projectId}/propose`, {
    url, original_selector: originalSelector, failure_context: failureContext,
  });
  return data;
}

export async function approveHeal(
  projectId: string, attemptId: string, targetFile: string | null, targetLine: number | null
): Promise<AttemptOut> {
  const { data } = await apiClient.post<AttemptOut>(
    `/api/testing/self-heal/${projectId}/attempts/${attemptId}/approve`,
    { target_file: targetFile, target_line: targetLine }
  );
  return data;
}

export async function rejectHeal(projectId: string, attemptId: string): Promise<AttemptOut> {
  const { data } = await apiClient.post<AttemptOut>(`/api/testing/self-heal/${projectId}/attempts/${attemptId}/reject`);
  return data;
}

export async function listHealAttempts(projectId: string): Promise<AttemptOut[]> {
  const { data } = await apiClient.get<AttemptOut[]>(`/api/testing/self-heal/${projectId}/attempts`);
  return data;
}
