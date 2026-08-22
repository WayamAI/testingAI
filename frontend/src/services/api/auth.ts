import { apiClient } from "./client";

export interface UserOut {
  id: string;
  email: string;
  name: string;
  role: string;
  organization_id: string;
}

export interface TokenResponse {
  access_token: string;
  user: UserOut;
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>("/api/auth/login", { email, password });
  return data;
}

export async function demoLogin(): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>("/api/auth/demo-login");
  return data;
}
