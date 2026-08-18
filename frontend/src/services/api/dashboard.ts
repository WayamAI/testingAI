import { apiClient } from "./client";

export interface DashboardMetrics {
  total_tests: number;
  executed: number;
  passed: number;
  failed: number;
  skipped: number;
  flaky_tests: number;
  pass_rate: number;
  critical_defects: number;
  quality_score: number;
  recent_runs: Array<{ id: string; status: string; passed: number; failed: number; total: number; created_at: string }>;
}

export async function getDashboard(projectId: string): Promise<DashboardMetrics> {
  const { data } = await apiClient.get<DashboardMetrics>("/api/dashboard", { params: { project_id: projectId } });
  return data;
}
