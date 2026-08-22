import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listProjects, createProject, connectRepo, connectZip } from "../services/api/intake";
import type { ProjectOut } from "../services/api/intake";
import { listTestSuites, createTestSuite } from "../services/api/testing";
import { createTestRun } from "../services/api/execution";
import { runSecurityScan, listSecurityFindings } from "../services/api/security";
import type { SecurityFindingOut } from "../services/api/security";
import { runApiTests } from "../services/api/apiTesting";
import type { ApiTestRunOut } from "../services/api/apiTesting";

const DETECTED_SUITE_NAME = "Detected Tests";

async function getOrCreateDetectedSuite(projectId: string): Promise<string> {
  const suites = await listTestSuites(projectId);
  const existing = suites.find((s) => s.name === DETECTED_SUITE_NAME);
  if (existing) return existing.id;
  const created = await createTestSuite(projectId, DETECTED_SUITE_NAME);
  return created.id;
}

function CapabilityBadge({ status, reason }: { status: string; reason: string | null }) {
  const label = status === "ready" ? "Connected" : status === "error" ? "Error" : status;
  const color =
    status === "ready" ? "bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-400"
    : status === "error" ? "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-400"
    : "bg-neutral-100 text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300";
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${color}`} title={reason ?? undefined}>
      {label}
    </span>
  );
}

function ProjectCard({ project, onRefresh }: { project: ProjectOut; onRefresh: () => void }) {
  const navigate = useNavigate();
  const [runStarting, setRunStarting] = useState(false);
  const [scanResult, setScanResult] = useState<{ total: number; status: Record<string, string> } | null>(null);
  const [scanFindings, setScanFindings] = useState<SecurityFindingOut[] | null>(null);
  const [scanning, setScanning] = useState(false);
  const [baseUrl, setBaseUrl] = useState("");
  const [apiTestResult, setApiTestResult] = useState<ApiTestRunOut | null>(null);
  const [apiTestError, setApiTestError] = useState<string | null>(null);
  const [testingApi, setTestingApi] = useState(false);

  const hasDetectedTests = !!project.detected_test_framework;

  const handleRun = async () => {
    setRunStarting(true);
    try {
      const suiteId = await getOrCreateDetectedSuite(project.id);
      const run = await createTestRun(suiteId);
      navigate(`/test-runs/${run.id}`);
    } finally {
      setRunStarting(false);
    }
  };

  const handleScan = async () => {
    setScanning(true);
    try {
      const summary = await runSecurityScan(project.id);
      setScanResult({ total: summary.total_findings, status: summary.provider_status });
      const findings = await listSecurityFindings(project.id);
      setScanFindings(findings);
    } finally {
      setScanning(false);
    }
  };

  const handleApiTest = async () => {
    setTestingApi(true);
    setApiTestError(null);
    setApiTestResult(null);
    try {
      const result = await runApiTests(project.id, baseUrl);
      setApiTestResult(result);
    } catch (err: any) {
      setApiTestError(err?.response?.data?.detail ?? "API testing failed");
    } finally {
      setTestingApi(false);
    }
  };

  return (
    <div className="rounded-lg border border-neutral-200 dark:border-neutral-800 p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <p className="font-medium">{project.name}</p>
          <p className="text-sm text-neutral-500">
            {project.detected_language ?? "no stack detected"}
            {project.detected_test_framework ? ` · ${project.detected_test_framework}` : ""}
          </p>
        </div>
        <CapabilityBadge status={project.intake_status} reason={project.intake_error} />
      </div>

      {project.intake_error && (
        <p className="text-sm text-amber-600 dark:text-amber-400">{project.intake_error}</p>
      )}

      <div className="flex flex-wrap gap-2">
        <button
          onClick={handleRun}
          disabled={!hasDetectedTests || runStarting}
          title={!hasDetectedTests ? "Unit/integration testing unavailable — no recognized test manifest" : undefined}
          className="rounded-md bg-brand-600 px-3 py-1.5 text-sm text-white hover:bg-brand-700 disabled:opacity-40"
        >
          {runStarting ? "Starting…" : "Run Tests"}
        </button>
        <button
          onClick={handleScan}
          disabled={scanning}
          className="rounded-md bg-neutral-900 dark:bg-neutral-100 dark:text-neutral-900 px-3 py-1.5 text-sm text-white disabled:opacity-40"
        >
          {scanning ? "Scanning…" : "Run Security Scan"}
        </button>
        <button onClick={onRefresh} className="rounded-md border border-neutral-300 dark:border-neutral-700 px-3 py-1.5 text-sm">
          Refresh
        </button>
      </div>

      {scanResult && (
        <div className="rounded-md bg-neutral-50 dark:bg-neutral-900 p-3 text-sm space-y-1">
          <p className="font-medium">{scanResult.total} finding(s)</p>
          {Object.entries(scanResult.status).map(([tool, status]) => (
            <p key={tool} className="text-neutral-500">{tool}: {status}</p>
          ))}
          {scanFindings && scanFindings.length > 0 && (
            <ul className="mt-2 space-y-1">
              {scanFindings.slice(0, 5).map((f) => (
                <li key={f.id} className="text-neutral-600 dark:text-neutral-300">
                  <span className="font-medium">{f.severity}</span> — {f.issue}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      <div className="flex flex-wrap items-center gap-2">
        <input
          aria-label="API base URL"
          placeholder="http://localhost:8000 (base URL to test discovered API against)"
          value={baseUrl}
          onChange={(e) => setBaseUrl(e.target.value)}
          className="flex-1 min-w-[220px] rounded-md border border-neutral-300 dark:border-neutral-700 bg-transparent px-2 py-1.5 text-sm"
        />
        <button
          onClick={handleApiTest}
          disabled={!baseUrl || testingApi}
          className="rounded-md border border-neutral-300 dark:border-neutral-700 px-3 py-1.5 text-sm disabled:opacity-40"
        >
          {testingApi ? "Testing…" : "Run API Tests"}
        </button>
      </div>
      {apiTestError && <p className="text-sm text-red-600">{apiTestError}</p>}
      {apiTestResult && (
        <div className="rounded-md bg-neutral-50 dark:bg-neutral-900 p-3 text-sm space-y-1">
          <p className="font-medium">{apiTestResult.endpoints_tested} endpoint(s) tested</p>
          {apiTestResult.results.map((r) => (
            <p key={r.name} className={r.status === "passed" ? "text-green-600" : "text-red-600"}>
              {r.name} — {r.status} {r.status_code ? `(HTTP ${r.status_code})` : ""}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}

export function ConnectProjectPage() {
  const [projects, setProjects] = useState<ProjectOut[] | null>(null);
  const [name, setName] = useState("");
  const [repoUrl, setRepoUrl] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = () => {
    listProjects().then((all) => setProjects(all.filter((p) => p.source === "connected")));
  };

  useEffect(refresh, []);

  const handleConnect = async () => {
    if (!name.trim() || (!repoUrl.trim() && !file)) return;
    setConnecting(true);
    setError(null);
    try {
      const project = await createProject(name.trim(), "web_application");
      if (file) {
        await connectZip(project.id, file);
      } else {
        await connectRepo(project.id, repoUrl.trim());
      }
      setName("");
      setRepoUrl("");
      setFile(null);
      refresh();
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Failed to connect project");
    } finally {
      setConnecting(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Connect Project</h1>
      <p className="text-sm text-neutral-500">
        Connect a real repository (public git URL or ZIP upload) to run its actual test suite, scan
        real dependencies/code for security findings, and test any discovered API — all against
        genuine, live-executed results, kept separate from demo data.
      </p>

      <div className="rounded-lg border border-neutral-200 dark:border-neutral-800 p-4 space-y-3">
        <label className="block text-sm font-medium" htmlFor="project-name">Project name</label>
        <input
          id="project-name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full rounded-md border border-neutral-300 dark:border-neutral-700 bg-transparent px-3 py-2 text-sm"
        />

        <label className="block text-sm font-medium" htmlFor="repo-url">Public git URL</label>
        <input
          id="repo-url"
          placeholder="https://github.com/org/repo"
          value={repoUrl}
          onChange={(e) => { setRepoUrl(e.target.value); setFile(null); }}
          disabled={!!file}
          className="w-full rounded-md border border-neutral-300 dark:border-neutral-700 bg-transparent px-3 py-2 text-sm disabled:opacity-40"
        />

        <p className="text-center text-sm text-neutral-400">— or —</p>

        <label className="block text-sm font-medium" htmlFor="project-zip">Upload ZIP</label>
        <input
          id="project-zip"
          type="file"
          accept=".zip"
          onChange={(e) => { setFile(e.target.files?.[0] ?? null); setRepoUrl(""); }}
          disabled={!!repoUrl}
          className="w-full text-sm disabled:opacity-40"
        />

        <button
          onClick={handleConnect}
          disabled={connecting || !name.trim() || (!repoUrl.trim() && !file)}
          className="rounded-md bg-brand-600 px-4 py-2 text-sm text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {connecting ? "Connecting…" : "Connect"}
        </button>
        {error && <p className="text-sm text-red-600">{error}</p>}
      </div>

      {projects === null ? (
        <p className="text-neutral-500">Loading connected projects…</p>
      ) : projects.length === 0 ? (
        <p className="text-sm text-neutral-500">No projects connected yet.</p>
      ) : (
        <div className="space-y-4">
          {projects.map((p) => (
            <ProjectCard key={p.id} project={p} onRefresh={refresh} />
          ))}
        </div>
      )}
    </div>
  );
}
