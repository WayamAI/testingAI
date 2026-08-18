import { apiClient } from "./client";
import { env } from "../../config/env";

export interface TestRun {
  id: string;
  project_id: string;
  suite_id: string;
  status: string;
}

export async function createTestRun(suiteId: string): Promise<TestRun> {
  const { data } = await apiClient.post<TestRun>("/api/test-runs", { suite_id: suiteId });
  return data;
}

export async function getTestRun(runId: string): Promise<TestRun> {
  const { data } = await apiClient.get<TestRun>(`/api/test-runs/${runId}`);
  return data;
}

export function executionSocketUrl(runId: string): string {
  const wsBase = env.apiUrl.replace(/^http/, "ws");
  return `${wsBase}/ws/executions/${runId}`;
}

export interface FailureAnalysis {
  root_cause: string;
  confidence: number;
  recommendation: string;
  affected_component: string;
}

export interface AnalyzeFailureResponse {
  analysis: FailureAnalysis;
  source: "ai" | "demo_fallback";
}

export async function analyzeFailure(params: {
  error_message: string;
  stack_trace?: string;
  test_case_title?: string;
}): Promise<AnalyzeFailureResponse> {
  const { data } = await apiClient.post<AnalyzeFailureResponse>("/api/ai/analyze-failure", {
    error_message: params.error_message,
    stack_trace: params.stack_trace ?? "",
    test_case_title: params.test_case_title ?? "",
  });
  return data;
}

export interface DefectCreatePayload {
  project_id: string;
  title: string;
  description: string;
  severity: string;
  priority: string;
  related_test_result_id?: string | null;
  related_test_case_id?: string | null;
}

export async function createDefect(payload: DefectCreatePayload) {
  const { data } = await apiClient.post("/api/defects", payload);
  return data as { id: string; title: string; severity: string; priority: string; status: string };
}
