import { apiClient } from "./client";
import type { GeneratedTestCase } from "./ai";

export interface TestCaseOut {
  id: string;
  project_id: string;
  title: string;
  type: string;
  priority: string;
  status: string;
  steps: string[];
  expected_result: string;
  automation_status: string;
  source: string;
}

export interface TestSuiteOut {
  id: string;
  project_id: string;
  name: string;
  description: string;
  test_case_ids: string[];
}

export async function listTestCases(projectId: string): Promise<TestCaseOut[]> {
  const { data } = await apiClient.get<TestCaseOut[]>("/api/test-cases", { params: { project_id: projectId } });
  return data;
}

export async function listTestSuites(projectId: string): Promise<TestSuiteOut[]> {
  const { data } = await apiClient.get<TestSuiteOut[]>("/api/test-suites", { params: { project_id: projectId } });
  return data;
}

export async function createTestCase(projectId: string, requirementId: string | null, c: GeneratedTestCase) {
  const { data } = await apiClient.post("/api/test-cases", {
    project_id: projectId, requirement_id: requirementId, title: c.title,
    type: c.type, priority: c.priority, steps: c.steps,
    expected_result: c.expected_result, source: "ai_generated", ai_confidence: c.ai_confidence,
  });
  return data as { id: string };
}

export async function createTestSuite(projectId: string, name: string) {
  const { data } = await apiClient.post("/api/test-suites", { project_id: projectId, name });
  return data as { id: string };
}

export async function addCasesToSuite(suiteId: string, caseIds: string[]) {
  const { data } = await apiClient.post(`/api/test-suites/${suiteId}/add-cases`, { case_ids: caseIds });
  return data;
}
