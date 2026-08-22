import { apiClient } from "./client";

export interface FileRiskScoreOut {
  file_path: string;
  change_frequency: number;
  bug_fix_ratio: number;
  churn: number;
  author_count: number;
  risk_score: number;
  risk_label: string;
}

export interface DefectPredictionScanOut {
  scan_id: string;
  files_analyzed: number;
  top_files: FileRiskScoreOut[];
  narrative: string;
  source: string;
}

export async function runDefectPrediction(projectId: string): Promise<DefectPredictionScanOut> {
  const { data } = await apiClient.post<DefectPredictionScanOut>(`/api/testing/defect-prediction/${projectId}/scan`);
  return data;
}

export async function listRiskScores(projectId: string): Promise<FileRiskScoreOut[]> {
  const { data } = await apiClient.get<FileRiskScoreOut[]>(`/api/testing/defect-prediction/${projectId}/scores`);
  return data;
}
