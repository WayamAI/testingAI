import { apiClient } from "./client";

export interface GeneratedTestCase {
  title: string; type: string; priority: string;
  steps: string[]; expected_result: string; ai_confidence: number;
}

export interface GenerateTestsResponse {
  cases: GeneratedTestCase[];
  source: "ai" | "demo_fallback";
}

export async function generateTests(requirementText: string): Promise<GenerateTestsResponse> {
  const { data } = await apiClient.post<GenerateTestsResponse>("/api/ai/generate-tests", { requirement_text: requirementText });
  return data;
}
