import { useState } from "react";
import { ProjectPicker } from "../components/common/ProjectPicker";
import { runBaselineScan, listBaselineTests } from "../services/api/baseline";
import type { BaselineScanOut, GeneratedTestOut } from "../services/api/baseline";

export function BaselinePage() {
  const [projectId, setProjectId] = useState<string | null>(null);
  const [scanning, setScanning] = useState(false);
  const [scanResult, setScanResult] = useState<BaselineScanOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tests, setTests] = useState<GeneratedTestOut[] | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);

  const loadTests = async (id: string) => {
    setTests(await listBaselineTests(id));
  };

  const handleScan = async () => {
    if (!projectId) return;
    setScanning(true);
    setError(null);
    try {
      const result = await runBaselineScan(projectId);
      setScanResult(result);
      await loadTests(projectId);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Baseline scan failed");
    } finally {
      setScanning(false);
    }
  };

  const handleProjectChange = (id: string) => {
    setProjectId(id);
    setScanResult(null);
    loadTests(id);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Repo Test Baseline</h1>
      <p className="text-sm text-neutral-500">
        AI-generates categorized Playwright tests (auth/api/crud/ui_form/ui_navigation/ui_component/
        integration/edge_case/performance/accessibility) from a connected repo. Re-scanning diffs real
        commits since the last scan and appends only tests for what actually changed.
      </p>

      <div className="flex items-center gap-3">
        <ProjectPicker value={projectId} onChange={handleProjectChange} />
        <button
          onClick={handleScan}
          disabled={!projectId || scanning}
          className="rounded-md bg-brand-600 px-4 py-2 text-sm text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {scanning ? "Scanning…" : "Run Baseline Scan"}
        </button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}
      {scanResult && (
        <div className="rounded-md bg-neutral-50 dark:bg-neutral-900 p-3 text-sm">
          {scanResult.message ? (
            <p>{scanResult.message}</p>
          ) : (
            <p>
              Generated {scanResult.generated} test(s) ({scanResult.rejected_invalid_syntax} rejected for
              invalid syntax) across categories: {scanResult.categories_scanned.join(", ")} — source: {scanResult.source}
            </p>
          )}
        </div>
      )}

      {tests && tests.length > 0 && (
        <div className="space-y-2">
          <h2 className="font-medium">Generated Tests ({tests.length})</h2>
          {tests.map((t) => (
            <div key={t.id} className="rounded-md border border-neutral-200 dark:border-neutral-800 p-3">
              <button
                onClick={() => setExpanded(expanded === t.id ? null : t.id)}
                className="flex w-full items-center justify-between text-left"
              >
                <span className="font-medium">{t.title}</span>
                <span className="text-xs text-neutral-500">{t.category} · confidence {(t.confidence * 100).toFixed(0)}%</span>
              </button>
              {expanded === t.id && (
                <pre className="mt-2 overflow-x-auto rounded bg-neutral-100 dark:bg-neutral-950 p-2 text-xs">{t.code}</pre>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
