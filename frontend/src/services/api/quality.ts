import { apiClient } from "./client";

export interface QualityScoreOut {
  overall: number;
  functional: number;
  reliability: number;
  security: number;
  performance: number;
  accessibility: number;
  coverage: number;
}

export interface ReleaseReadinessOut {
  status: string;
  pass_rate: number;
  critical_defects: number;
  quality_score: number;
  gate_violations: string[];
}

export async function getQualityScore(projectId: string): Promise<QualityScoreOut> {
  const { data } = await apiClient.get<QualityScoreOut>("/api/quality/score", { params: { project_id: projectId } });
  return data;
}

export async function getReleaseReadiness(projectId: string): Promise<ReleaseReadinessOut> {
  const { data } = await apiClient.get<ReleaseReadinessOut>("/api/quality/release-readiness", { params: { project_id: projectId } });
  return data;
}
