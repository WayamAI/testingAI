import { useState } from "react";
import { ProjectPicker } from "../components/common/ProjectPicker";
import { selectTests, listDuplicates, listCoverageGaps, getFlakyReport } from "../services/api/testSelection";
import type { SelectionOut, DuplicateOut, FlakyReportOut } from "../services/api/testSelection";

export function TestSelectionPage() {
  const [projectId, setProjectId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [selection, setSelection] = useState<SelectionOut | null>(null);
  const [duplicates, setDuplicates] = useState<DuplicateOut[] | null>(null);
  const [gaps, setGaps] = useState<string[] | null>(null);
  const [flaky, setFlaky] = useState<FlakyReportOut[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!projectId) return;
    setLoading(true);
    setError(null);
    setSelection(null);
    try {
      const [sel, dup, gap, flakyReport] = await Promise.all([
        selectTests(projectId),
        listDuplicates(projectId),
        listCoverageGaps(projectId),
        getFlakyReport(projectId),
      ]);
      setSelection(sel);
      setDuplicates(dup);
      setGaps(gap);
      setFlaky(flakyReport);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Selection failed — has a Baseline scan run for this project?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Intelligent Test Selection & Optimization</h1>
      <p className="text-sm text-neutral-500">
        Maps real changed files (git diff since the last baseline scan) to relevant tests, weighted by real
        Defect Prediction risk scores. Plus real duplicate/coverage-gap detection, and flaky scoring that's
        honest about needing real run history.
      </p>

      <div className="flex items-center gap-3">
        <ProjectPicker value={projectId} onChange={setProjectId} />
        <button
          onClick={handleAnalyze}
          disabled={!projectId || loading}
          className="rounded-md bg-brand-600 px-4 py-2 text-sm text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {loading ? "Analyzing…" : "Analyze"}
        </button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {selection && (
        <div className="space-y-2">
          <h2 className="font-medium">Selected Tests ({selection.selected.length})</h2>
          <p className="text-sm text-neutral-500">
            Changed files: {selection.changed_files.join(", ") || "(none)"} — relevant categories:{" "}
            {selection.relevant_categories.join(", ") || "(none)"}
          </p>
          {selection.selected.map((s) => (
            <div key={s.test_id} className="rounded-md border border-neutral-200 dark:border-neutral-800 p-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="font-medium">{s.title}</span>
                <span className="text-xs text-neutral-500">score {s.score.toFixed(2)}</span>
              </div>
              <p className="text-xs text-neutral-500">{s.reason}</p>
            </div>
          ))}
          <p className="text-sm text-neutral-500">{selection.estimated_tests_skipped} test(s) skipped as not relevant.</p>
        </div>
      )}

      {duplicates && duplicates.length > 0 && (
        <div className="space-y-2">
          <h2 className="font-medium">Duplicates ({duplicates.length})</h2>
          {duplicates.map((d, i) => (
            <p key={i} className="text-sm text-neutral-600 dark:text-neutral-300">
              "{d.test_a_title}" ≈ "{d.test_b_title}" ({(d.similarity * 100).toFixed(0)}% similar)
            </p>
          ))}
        </div>
      )}

      {gaps && (
        <div>
          <h2 className="font-medium">Coverage Gaps</h2>
          <p className="text-sm text-neutral-500">
            {gaps.length === 0 ? "None — every category has at least one test." : gaps.join(", ")}
          </p>
        </div>
      )}

      {flaky && flaky.length > 0 && (
        <div className="space-y-2">
          <h2 className="font-medium">Flaky Report</h2>
          {flaky.map((f) => (
            <p key={f.test_case_id} className="text-sm text-neutral-600 dark:text-neutral-300">
              {f.title}: {f.flaky_score !== null ? `${(f.flaky_score * 100).toFixed(0)}% flaky (${f.run_count} runs)` : f.status}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
