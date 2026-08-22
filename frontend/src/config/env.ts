export const env = {
  apiUrl: import.meta.env.VITE_API_URL || "http://localhost:8000",
  demoMode: import.meta.env.VITE_DEMO_MODE === "true",
};
