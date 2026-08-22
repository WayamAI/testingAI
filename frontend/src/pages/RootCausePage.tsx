import { useEffect, useState } from "react";
import { ProjectPicker } from "../components/common/ProjectPicker";
import { analyzeRootCause, listRootCauseHistory } from "../services/api/rootCause";
import type { AnalyzeResultOut, HistoryEntryOut } from "../services/api/rootCause";

export function RootCausePage() {
  const [projectId, setProjectId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [stackTrace, setStackTrace] = useState("");
  const [testCaseTitle, setTestCaseTitle] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalyzeResultOut | null>(null);
  const [analyzeError, setAnalyzeError] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryEntryOut[] | null>(null);

  useEffect(() => {
    if (projectId) listRootCauseHistory(projectId).then(setHistory);
  }, [projectId]);

  const handleAnalyze = async () => {
    if (!projectId || !errorMessage) return;
    setAnalyzing(true);
    setAnalyzeError(null);
    try {
      const res = await analyzeRootCause(projectId, errorMessage, stackTrace, testCaseTitle);
      setResult(res);
      setHistory(await listRootCauseHistory(projectId));
    } catch (err: any) {
      setAnalyzeError(err?.response?.data?.detail ?? "Analysis failed");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">AI Root Cause Analysis</h1>
      <p className="text-sm text-neutral-500">
        Correlates a failure against the project's real recent commits — ranked by file-path overlap with
        the stack trace — and feeds the real diff of the most likely commit to the AI.
      </p>

      <ProjectPicker value={projectId} onChange={setProjectId} />

      <div className="space-y-2 rounded-lg border border-neutral-200 dark:border-neutral-800 p-4">
        <label className="block text-sm font-medium" htmlFor="rc-test-title">Test case title</label>
        <input
          id="rc-test-title"
          value={testCaseTitle}
          onChange={(e) => setTestCaseTitle(e.target.value)}
          className="w-full rounded-md border border-neutral-300 dark:border-neutral-700 bg-transparent px-3 py-2 text-sm"
        />
        <label className="block text-sm font-medium" htmlFor="rc-error">Error message</label>
        <input
          id="rc-error"
          value={errorMessage}
          onChange={(e) => setErrorMessage(e.target.value)}
          className="w-full rounded-md border border-neutral-300 dark:border-neutral-700 bg-transparent px-3 py-2 text-sm"
        />
        <label className="block text-sm font-medium" htmlFor="rc-stack">Stack trace</label>
        <textarea
          id="rc-stack"
          rows={3}
          value={stackTrace}
          onChange={(e) => setStackTrace(e.target.value)}
          className="w-full rounded-md border border-neutral-300 dark:border-neutral-700 bg-transparent px-3 py-2 text-sm font-mono"
        />
        <button
          onClick={handleAnalyze}
          disabled={!projectId || !errorMessage || analyzing}
          className="rounded-md bg-brand-600 px-4 py-2 text-sm text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {analyzing ? "Analyzing…" : "Analyze"}
        </button>
        {analyzeError && <p className="text-sm text-red-600">{analyzeError}</p>}
      </div>

      {result && (
        <div className="rounded-md bg-neutral-50 dark:bg-neutral-900 p-3 text-sm space-y-1">
          <p><span className="font-medium">Root cause:</span> {result.root_cause}</p>
          <p><span className="font-medium">Confidence:</span> {(result.confidence * 100).toFixed(0)}%</p>
          <p><span className="font-medium">Affected component:</span> {result.affected_component}</p>
          <p><span className="font-medium">Recommendation:</span> {result.recommendation}</p>
          {result.git_correlation_available ? (
            result.likely_commit_sha ? (
              <p><span className="font-medium">Likely commit:</span> {result.likely_commit_sha.slice(0, 8)} — {result.likely_commit_message}</p>
            ) : (
              <p className="text-neutral-500">No specific commit correlated.</p>
            )
          ) : (
            <p className="text-neutral-500">Git correlation not available (project not connected to a git repo).</p>
          )}
          <p className="text-neutral-500">source: {result.source}</p>
        </div>
      )}

      {history && history.length > 0 && (
        <div className="space-y-2">
          <h2 className="font-medium">History ({history.length})</h2>
          {history.map((h) => (
            <div key={h.id} className="rounded-md border border-neutral-200 dark:border-neutral-800 p-3 text-sm">
              <p className="font-medium">{h.test_case_title || "(untitled)"}</p>
              <p className="text-neutral-500">{h.root_cause}</p>
              {h.likely_commit_sha && <p className="text-xs text-neutral-400">commit {h.likely_commit_sha.slice(0, 8)}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
