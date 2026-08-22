import { apiClient } from "./client";
import type { GeneratedTestOut } from "./baseline";

export interface DocDrivenResultOut {
  scenarios_extracted: number;
  tests_generated: number;
  rejected_invalid_syntax: number;
  source: string;
  scenario_source: string;
  message: string | null;
  tests: GeneratedTestOut[];
}

export interface DocUploadOut {
  id: string;
  filename: string;
  extracted_char_count: number;
  scenarios_extracted: number;
  tests_generated: number;
  source: string;
}

export async function uploadDocument(projectId: string, file: File): Promise<DocDrivenResultOut> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await apiClient.post<DocDrivenResultOut>(`/api/testing/doc-driven/${projectId}/upload`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function listDocUploads(projectId: string): Promise<DocUploadOut[]> {
  const { data } = await apiClient.get<DocUploadOut[]>(`/api/testing/doc-driven/${projectId}/uploads`);
  return data;
}
