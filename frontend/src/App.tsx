import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "./contexts/AuthContext";
import { AppLayout } from "./components/layout/AppLayout";
import { LoginPage } from "./pages/LoginPage";
import { DashboardRoute } from "./pages/DashboardRoute";
import { QualityIntelligencePage } from "./pages/QualityIntelligencePage";
import { ActivityPage } from "./pages/ActivityPage";
import { TestCasesPage } from "./pages/TestCasesPage";
import { TestSuitesPage } from "./pages/TestSuitesPage";
import { TestPlansPage } from "./pages/TestPlansPage";
import { TestCyclesPage } from "./pages/TestCyclesPage";
import { TestExplorerPage } from "./pages/TestExplorerPage";
import { AITestGeneratorRoute } from "./pages/AITestGeneratorRoute";
import { TestRunPage } from "./pages/TestRunPage";
import { AiTestPlannerPage } from "./pages/AiTestPlannerPage";
import { AiTestOptimizerPage } from "./pages/AiTestOptimizerPage";
import { AiRegressionIntelligencePage } from "./pages/AiRegressionIntelligencePage";
import { AiFailureAnalysisPage } from "./pages/AiFailureAnalysisPage";
import { AiQualityCopilotPage } from "./pages/AiQualityCopilotPage";
import { WebTestingPage } from "./pages/WebTestingPage";
import { WebTestingBrowserTestingPage } from "./pages/WebTestingBrowserTestingPage";
import { WebTestingCrossBrowserPage } from "./pages/WebTestingCrossBrowserPage";
import { WebTestingVisualTestingPage } from "./pages/WebTestingVisualTestingPage";
import { WebTestingAccessibilityPage } from "./pages/WebTestingAccessibilityPage";
import { ApiTestingPage } from "./pages/ApiTestingPage";
import { ApiTestingCollectionsPage } from "./pages/ApiTestingCollectionsPage";
import { ApiTestingExplorerPage } from "./pages/ApiTestingExplorerPage";
import { ApiTestingContractTestingPage } from "./pages/ApiTestingContractTestingPage";
import { ApiTestingMonitoringPage } from "./pages/ApiTestingMonitoringPage";
import { MobileTestingPage } from "./pages/MobileTestingPage";
import { MobileTestingDeviceMatrixPage } from "./pages/MobileTestingDeviceMatrixPage";
import { MobileTestingAndroidPage } from "./pages/MobileTestingAndroidPage";
import { MobileTestingIosPage } from "./pages/MobileTestingIosPage";
import { PerformancePage } from "./pages/PerformancePage";
import { PerformanceLoadTestingPage } from "./pages/PerformanceLoadTestingPage";
import { PerformanceStressTestingPage } from "./pages/PerformanceStressTestingPage";
import { PerformanceSpikeTestingPage } from "./pages/PerformanceSpikeTestingPage";
import { PerformanceEnduranceTestingPage } from "./pages/PerformanceEnduranceTestingPage";
import { PerformanceScalabilityPage } from "./pages/PerformanceScalabilityPage";
import { SecurityPage } from "./pages/SecurityPage";
import { SecurityApiSecurityPage } from "./pages/SecurityApiSecurityPage";
import { SecurityAuthenticationPage } from "./pages/SecurityAuthenticationPage";
import { SecurityAuthorizationPage } from "./pages/SecurityAuthorizationPage";
import { SecurityReportsPage } from "./pages/SecurityReportsPage";
import { DataDatabaseTestingPage } from "./pages/DataDatabaseTestingPage";
import { DataValidationPage } from "./pages/DataValidationPage";
import { DataIntegrationTestingPage } from "./pages/DataIntegrationTestingPage";
import { DataMicroservicesPage } from "./pages/DataMicroservicesPage";
import { AutomationStudioPage } from "./pages/AutomationStudioPage";
import { AutomationTestsPage } from "./pages/AutomationTestsPage";
import { AutomationSchedulesPage } from "./pages/AutomationSchedulesPage";
import { AutomationPipelinesPage } from "./pages/AutomationPipelinesPage";
import { AutomationCiCdPage } from "./pages/AutomationCiCdPage";
import { QualityCoveragePage } from "./pages/QualityCoveragePage";
import { QualityRiskAnalysisPage } from "./pages/QualityRiskAnalysisPage";
import { QualityDefectsPage } from "./pages/QualityDefectsPage";
import { QualityFlakyTestsPage } from "./pages/QualityFlakyTestsPage";
import { QualityScorePage } from "./pages/QualityScorePage";
import { QualityReleaseReadinessPage } from "./pages/QualityReleaseReadinessPage";
import { QualityGatesPage } from "./pages/QualityGatesPage";
import { IntegrationsGithubPage } from "./pages/IntegrationsGithubPage";
import { IntegrationsGitlabPage } from "./pages/IntegrationsGitlabPage";
import { IntegrationsBitbucketPage } from "./pages/IntegrationsBitbucketPage";
import { IntegrationsJiraPage } from "./pages/IntegrationsJiraPage";
import { IntegrationsSlackPage } from "./pages/IntegrationsSlackPage";
import { IntegrationsTeamsPage } from "./pages/IntegrationsTeamsPage";
import { IntegrationsVercelPage } from "./pages/IntegrationsVercelPage";
import { IntegrationsAwsPage } from "./pages/IntegrationsAwsPage";
import { IntegrationsAzurePage } from "./pages/IntegrationsAzurePage";
import { IntegrationsGcpPage } from "./pages/IntegrationsGcpPage";
import { IntegrationsDockerPage } from "./pages/IntegrationsDockerPage";
import { IntegrationsKubernetesPage } from "./pages/IntegrationsKubernetesPage";
import { IntegrationsDatadogPage } from "./pages/IntegrationsDatadogPage";
import { IntegrationsSentryPage } from "./pages/IntegrationsSentryPage";
import { AdminOrganizationPage } from "./pages/AdminOrganizationPage";
import { AdminUsersPage } from "./pages/AdminUsersPage";
import { AdminTeamsPage } from "./pages/AdminTeamsPage";
import { AdminRolesPage } from "./pages/AdminRolesPage";
import { AdminApiKeysPage } from "./pages/AdminApiKeysPage";
import { AdminEnvironmentsPage } from "./pages/AdminEnvironmentsPage";
import { AdminSecretsPage } from "./pages/AdminSecretsPage";
import { AdminUsagePage } from "./pages/AdminUsagePage";
import { AdminBillingPage } from "./pages/AdminBillingPage";
import { AdminAuditLogsPage } from "./pages/AdminAuditLogsPage";
import { AdminSettingsPage } from "./pages/AdminSettingsPage";

export const ROUTE_PATHS = [
  "/dashboard",
  "/quality-intelligence",
  "/activity",
  "/test-cases",
  "/test-suites",
  "/test-plans",
  "/test-cycles",
  "/test-explorer",
  "/test-runs/:runId",
  "/ai/test-generator",
  "/ai/test-planner",
  "/ai/test-optimizer",
  "/ai/regression-intelligence",
  "/ai/failure-analysis",
  "/ai/quality-copilot",
  "/web-testing",
  "/web-testing/browser-testing",
  "/web-testing/cross-browser",
  "/web-testing/visual-testing",
  "/web-testing/accessibility",
  "/api-testing",
  "/api-testing/collections",
  "/api-testing/explorer",
  "/api-testing/contract-testing",
  "/api-testing/monitoring",
  "/mobile-testing",
  "/mobile-testing/device-matrix",
  "/mobile-testing/android",
  "/mobile-testing/ios",
  "/performance",
  "/performance/load-testing",
  "/performance/stress-testing",
  "/performance/spike-testing",
  "/performance/endurance-testing",
  "/performance/scalability",
  "/security",
  "/security/api-security",
  "/security/authentication",
  "/security/authorization",
  "/security/reports",
  "/data/database-testing",
  "/data/validation",
  "/data/integration-testing",
  "/data/microservices",
  "/automation/studio",
  "/automation/tests",
  "/automation/schedules",
  "/automation/pipelines",
  "/automation/ci-cd",
  "/quality/coverage",
  "/quality/risk-analysis",
  "/quality/defects",
  "/quality/flaky-tests",
  "/quality/score",
  "/quality/release-readiness",
  "/quality/gates",
  "/integrations/github",
  "/integrations/gitlab",
  "/integrations/bitbucket",
  "/integrations/jira",
  "/integrations/slack",
  "/integrations/teams",
  "/integrations/vercel",
  "/integrations/aws",
  "/integrations/azure",
  "/integrations/gcp",
  "/integrations/docker",
  "/integrations/kubernetes",
  "/integrations/datadog",
  "/integrations/sentry",
  "/admin/organization",
  "/admin/users",
  "/admin/teams",
  "/admin/roles",
  "/admin/api-keys",
  "/admin/environments",
  "/admin/secrets",
  "/admin/usage",
  "/admin/billing",
  "/admin/audit-logs",
  "/admin/settings",
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
            <Route path="/quality-intelligence" element={<QualityIntelligencePage />} />
            <Route path="/activity" element={<ActivityPage />} />
            <Route path="/test-cases" element={<TestCasesPage />} />
            <Route path="/test-suites" element={<TestSuitesPage />} />
            <Route path="/test-plans" element={<TestPlansPage />} />
            <Route path="/test-cycles" element={<TestCyclesPage />} />
            <Route path="/test-explorer" element={<TestExplorerPage />} />
            <Route path="/test-runs/:runId" element={<TestRunPage />} />
            <Route path="/ai/test-generator" element={<AITestGeneratorRoute />} />
            <Route path="/ai/test-planner" element={<AiTestPlannerPage />} />
            <Route path="/ai/test-optimizer" element={<AiTestOptimizerPage />} />
            <Route path="/ai/regression-intelligence" element={<AiRegressionIntelligencePage />} />
            <Route path="/ai/failure-analysis" element={<AiFailureAnalysisPage />} />
            <Route path="/ai/quality-copilot" element={<AiQualityCopilotPage />} />
            <Route path="/web-testing" element={<WebTestingPage />} />
            <Route path="/web-testing/browser-testing" element={<WebTestingBrowserTestingPage />} />
            <Route path="/web-testing/cross-browser" element={<WebTestingCrossBrowserPage />} />
            <Route path="/web-testing/visual-testing" element={<WebTestingVisualTestingPage />} />
            <Route path="/web-testing/accessibility" element={<WebTestingAccessibilityPage />} />
            <Route path="/api-testing" element={<ApiTestingPage />} />
            <Route path="/api-testing/collections" element={<ApiTestingCollectionsPage />} />
            <Route path="/api-testing/explorer" element={<ApiTestingExplorerPage />} />
            <Route path="/api-testing/contract-testing" element={<ApiTestingContractTestingPage />} />
            <Route path="/api-testing/monitoring" element={<ApiTestingMonitoringPage />} />
            <Route path="/mobile-testing" element={<MobileTestingPage />} />
            <Route path="/mobile-testing/device-matrix" element={<MobileTestingDeviceMatrixPage />} />
            <Route path="/mobile-testing/android" element={<MobileTestingAndroidPage />} />
            <Route path="/mobile-testing/ios" element={<MobileTestingIosPage />} />
            <Route path="/performance" element={<PerformancePage />} />
            <Route path="/performance/load-testing" element={<PerformanceLoadTestingPage />} />
            <Route path="/performance/stress-testing" element={<PerformanceStressTestingPage />} />
            <Route path="/performance/spike-testing" element={<PerformanceSpikeTestingPage />} />
            <Route path="/performance/endurance-testing" element={<PerformanceEnduranceTestingPage />} />
            <Route path="/performance/scalability" element={<PerformanceScalabilityPage />} />
            <Route path="/security" element={<SecurityPage />} />
            <Route path="/security/api-security" element={<SecurityApiSecurityPage />} />
            <Route path="/security/authentication" element={<SecurityAuthenticationPage />} />
            <Route path="/security/authorization" element={<SecurityAuthorizationPage />} />
            <Route path="/security/reports" element={<SecurityReportsPage />} />
            <Route path="/data/database-testing" element={<DataDatabaseTestingPage />} />
            <Route path="/data/validation" element={<DataValidationPage />} />
            <Route path="/data/integration-testing" element={<DataIntegrationTestingPage />} />
            <Route path="/data/microservices" element={<DataMicroservicesPage />} />
            <Route path="/automation/studio" element={<AutomationStudioPage />} />
            <Route path="/automation/tests" element={<AutomationTestsPage />} />
            <Route path="/automation/schedules" element={<AutomationSchedulesPage />} />
            <Route path="/automation/pipelines" element={<AutomationPipelinesPage />} />
            <Route path="/automation/ci-cd" element={<AutomationCiCdPage />} />
            <Route path="/quality/coverage" element={<QualityCoveragePage />} />
            <Route path="/quality/risk-analysis" element={<QualityRiskAnalysisPage />} />
            <Route path="/quality/defects" element={<QualityDefectsPage />} />
            <Route path="/quality/flaky-tests" element={<QualityFlakyTestsPage />} />
            <Route path="/quality/score" element={<QualityScorePage />} />
            <Route path="/quality/release-readiness" element={<QualityReleaseReadinessPage />} />
            <Route path="/quality/gates" element={<QualityGatesPage />} />
            <Route path="/integrations/github" element={<IntegrationsGithubPage />} />
            <Route path="/integrations/gitlab" element={<IntegrationsGitlabPage />} />
            <Route path="/integrations/bitbucket" element={<IntegrationsBitbucketPage />} />
            <Route path="/integrations/jira" element={<IntegrationsJiraPage />} />
            <Route path="/integrations/slack" element={<IntegrationsSlackPage />} />
            <Route path="/integrations/teams" element={<IntegrationsTeamsPage />} />
            <Route path="/integrations/vercel" element={<IntegrationsVercelPage />} />
            <Route path="/integrations/aws" element={<IntegrationsAwsPage />} />
            <Route path="/integrations/azure" element={<IntegrationsAzurePage />} />
            <Route path="/integrations/gcp" element={<IntegrationsGcpPage />} />
            <Route path="/integrations/docker" element={<IntegrationsDockerPage />} />
            <Route path="/integrations/kubernetes" element={<IntegrationsKubernetesPage />} />
            <Route path="/integrations/datadog" element={<IntegrationsDatadogPage />} />
            <Route path="/integrations/sentry" element={<IntegrationsSentryPage />} />
            <Route path="/admin/organization" element={<AdminOrganizationPage />} />
            <Route path="/admin/users" element={<AdminUsersPage />} />
            <Route path="/admin/teams" element={<AdminTeamsPage />} />
            <Route path="/admin/roles" element={<AdminRolesPage />} />
            <Route path="/admin/api-keys" element={<AdminApiKeysPage />} />
            <Route path="/admin/environments" element={<AdminEnvironmentsPage />} />
            <Route path="/admin/secrets" element={<AdminSecretsPage />} />
            <Route path="/admin/usage" element={<AdminUsagePage />} />
            <Route path="/admin/billing" element={<AdminBillingPage />} />
            <Route path="/admin/audit-logs" element={<AdminAuditLogsPage />} />
            <Route path="/admin/settings" element={<AdminSettingsPage />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
