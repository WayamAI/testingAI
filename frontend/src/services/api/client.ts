import axios from "axios";
import { env } from "../../config/env";

export const TOKEN_KEY = "wayam_token";

export const apiClient = axios.create({ baseURL: env.apiUrl });

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers = config.headers ?? {};
    (config.headers as any).Authorization = `Bearer ${token}`;
  }
  return config;
});
