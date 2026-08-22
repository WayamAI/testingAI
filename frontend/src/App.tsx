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
import { BaselinePage } from "./pages/BaselinePage";
import { DocDrivenPage } from "./pages/DocDrivenPage";
import { LiveRunnerPage } from "./pages/LiveRunnerPage";
import { DefectPredictionPage } from "./pages/DefectPredictionPage";
import { RootCausePage } from "./pages/RootCausePage";
import { TestSelectionPage } from "./pages/TestSelectionPage";
import { SelfHealPage } from "./pages/SelfHealPage";

// Authoritative route list — sub-project 2 pruned this to Testing and
// Quality only; sub-project 3 added the 7 AI Test Intelligence pages.
// Every path here is backed by a real page (see Sidebar.tsx).
export const ROUTE_PATHS = [
  "/dashboard",
  "/test-cases",
  "/test-suites",
  "/ai/test-generator",
  "/connect-project",
  "/testing/baseline",
  "/testing/doc-driven",
  "/testing/live-runner",
  "/test-runs/:runId",
  "/quality/defects",
  "/quality/score",
  "/quality/release-readiness",
  "/quality/defect-prediction",
  "/quality/root-cause",
  "/quality/test-selection",
  "/quality/self-heal",
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
            <Route path="/testing/baseline" element={<BaselinePage />} />
            <Route path="/testing/doc-driven" element={<DocDrivenPage />} />
            <Route path="/testing/live-runner" element={<LiveRunnerPage />} />
            <Route path="/test-runs/:runId" element={<TestRunPage />} />
            <Route path="/quality/defects" element={<DefectsRoute />} />
            <Route path="/quality/score" element={<QualityScoreRoute />} />
            <Route path="/quality/release-readiness" element={<ReleaseReadinessRoute />} />
            <Route path="/quality/defect-prediction" element={<DefectPredictionPage />} />
            <Route path="/quality/root-cause" element={<RootCausePage />} />
            <Route path="/quality/test-selection" element={<TestSelectionPage />} />
            <Route path="/quality/self-heal" element={<SelfHealPage />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
