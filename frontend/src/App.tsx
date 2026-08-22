import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "./contexts/AuthContext";
import { AppLayout } from "./components/layout/AppLayout";
import { LoginPage } from "./pages/LoginPage";
import { DashboardRoute } from "./pages/DashboardRoute";
import { TestCasesRoute } from "./pages/TestCasesRoute";
import { TestSuitesRoute } from "./pages/TestSuitesRoute";
import { AITestGeneratorRoute } from "./pages/AITestGeneratorRoute";
import { ConnectProjectPage } from "./pages/ConnectProjectPage";
import { TestRunPage } from "./pages/TestRunPage";
import { DefectsRoute } from "./pages/DefectsRoute";
import { QualityScoreRoute } from "./pages/QualityScoreRoute";
import { ReleaseReadinessRoute } from "./pages/ReleaseReadinessRoute";

// Authoritative route list — sub-project 2 spec pruned this to Testing and
// Quality only. Every path here is backed by a real page (see Sidebar.tsx).
export const ROUTE_PATHS = [
  "/dashboard",
  "/test-cases",
  "/test-suites",
  "/ai/test-generator",
  "/connect-project",
  "/test-runs/:runId",
  "/quality/defects",
  "/quality/score",
  "/quality/release-readiness",
];

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<DashboardRoute />} />
            <Route path="/test-cases" element={<TestCasesRoute />} />
            <Route path="/test-suites" element={<TestSuitesRoute />} />
            <Route path="/ai/test-generator" element={<AITestGeneratorRoute />} />
            <Route path="/connect-project" element={<ConnectProjectPage />} />
            <Route path="/test-runs/:runId" element={<TestRunPage />} />
            <Route path="/quality/defects" element={<DefectsRoute />} />
            <Route path="/quality/score" element={<QualityScoreRoute />} />
            <Route path="/quality/release-readiness" element={<ReleaseReadinessRoute />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
