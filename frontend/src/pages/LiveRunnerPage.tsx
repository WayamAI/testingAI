import { useState } from "react";
import { ProjectPicker } from "../components/common/ProjectPicker";
import { runLiveTests } from "../services/api/liveRunner";
import type { LiveRunOut } from "../services/api/liveRunner";

const STATUS_COLOR: Record<string, string> = {
  passed: "text-green-600", failed: "text-red-600",
  timedOut: "text-red-600", interrupted: "text-amber-600",
};

export function LiveRunnerPage() {
  const [projectId, setProjectId] = useState<string | null>(null);
  const [url, setUrl] = useState("");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<LiveRunOut | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRun = async () => {
    if (!projectId || !url) return;
    setRunning(true);
    setError(null);
    setResult(null);
    try {
      const res = await runLiveTests(projectId, url);
      setResult(res);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Live run failed");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Live Test Runner</h1>
      <p className="text-sm text-neutral-500">
        Give a running app URL — its real DOM is scanned, AI generates tests for what's actually on the
        page, and they're genuinely executed in headless Chromium with a real screenshot per test.
      </p>

      <div className="flex flex-wrap items-center gap-3">
        <ProjectPicker value={projectId} onChange={setProjectId} />
        <input
          aria-label="App URL"
          placeholder="http://localhost:5173"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="flex-1 min-w-[220px] rounded-md border border-neutral-300 dark:border-neutral-700 bg-transparent px-3 py-1.5 text-sm"
        />
        <button
          onClick={handleRun}
          disabled={!projectId || !url || running}
          className="rounded-md bg-brand-600 px-4 py-2 text-sm text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {running ? "Running…" : "Run Live Tests"}
        </button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}
      {result && (
        <div className="space-y-3">
          <div className="rounded-md bg-neutral-50 dark:bg-neutral-900 p-3 text-sm">
            <p>
              {result.passed} passed, {result.failed} failed (of {result.total}) — categories:{" "}
              {result.categories.join(", ")} — source: {result.source}
            </p>
          </div>
          {result.results.map((r, i) => (
            <div key={i} className="rounded-md border border-neutral-200 dark:border-neutral-800 p-3">
              <div className="flex items-center justify-between">
                <span className="font-medium">{r.title}</span>
                <span className={`text-sm font-medium ${STATUS_COLOR[r.status] ?? ""}`}>{r.status}</span>
              </div>
              <p className="text-xs text-neutral-500">{r.category} · {r.duration_ms}ms</p>
              {r.screenshot_path && (
                <p className="mt-1 text-xs text-neutral-400 break-all">screenshot: {r.screenshot_path}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
