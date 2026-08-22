import { apiClient } from "./client";

export interface ProjectOut {
  id: string;
  name: string;
  project_type: string;
  organization_id: string;
  source: "demo" | "connected";
  intake_status: string;
  intake_error: string | null;
  repo_url: string | null;
  detected_language: string | null;
  detected_test_framework: string | null;
}

export async function listProjects(): Promise<ProjectOut[]> {
  const { data } = await apiClient.get<ProjectOut[]>("/api/projects");
  return data;
}

export async function createProject(name: string, projectType: string): Promise<ProjectOut> {
  const { data } = await apiClient.post<ProjectOut>("/api/projects", { name, project_type: projectType });
  return data;
}

export async function connectRepo(projectId: string, repoUrl: string): Promise<ProjectOut> {
  const { data } = await apiClient.post<ProjectOut>(`/api/projects/${projectId}/connect-repo`, { repo_url: repoUrl });
  return data;
}

export async function connectZip(projectId: string, file: File): Promise<ProjectOut> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await apiClient.post<ProjectOut>(`/api/projects/${projectId}/connect-zip`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}
