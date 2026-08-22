import { apiClient } from "./client";

export interface SecurityFindingOut {
  id: string;
  tool: string;
  severity: string;
  file: string | null;
  line: number | null;
  issue: string;
  evidence: string | null;
  recommendation: string | null;
}

export interface ScanSummaryOut {
  scan_id: string;
  provider_status: Record<string, string>;
  total_findings: number;
}

export async function runSecurityScan(projectId: string): Promise<ScanSummaryOut> {
  const { data } = await apiClient.post<ScanSummaryOut>(`/api/projects/${projectId}/security-scans`);
  return data;
}

export async function listSecurityFindings(projectId: string): Promise<SecurityFindingOut[]> {
  const { data } = await apiClient.get<SecurityFindingOut[]>(`/api/projects/${projectId}/security-findings`);
  return data;
}
