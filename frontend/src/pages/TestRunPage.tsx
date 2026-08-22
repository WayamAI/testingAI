import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useExecutionSocket } from "../hooks/useExecutionSocket";
import type { ExecutionEvent } from "../hooks/useExecutionSocket";
import { ExecutionTimeline } from "../components/execution/ExecutionTimeline";
import { AIInsightBadge } from "../components/ai/AIInsightBadge";
import { analyzeFailure, createDefect, getTestRun } from "../services/api/execution";
import type { FailureAnalysis } from "../services/api/execution";

interface FailureAnalysisState {
  loading: boolean;
  error: string | null;
  analysis: FailureAnalysis | null;
  source: "ai" | "demo_fallback" | null;
  defectLoading: boolean;
  defectError: string | null;
  defectId: string | null;
}

const emptyAnalysisState: FailureAnalysisState = {
  loading: false,
  error: null,
  analysis: null,
  source: null,
  defectLoading: false,
  defectError: null,
  defectId: null,
};

function keyFor(event: ExecutionEvent, index: number): string {
  return event.test_case_id ?? `event-${index}`;
}

export function TestRunPage() {
  const { runId } = useParams<{ runId: string }>();
  const { events, status } = useExecutionSocket(runId ?? "");
  const [projectId, setProjectId] = useState<string | null>(null);
  const [analyses, setAnalyses] = useState<Record<string, FailureAnalysisState>>({});

  useEffect(() => {
    if (!runId) return;
    let cancelled = false;
    getTestRun(runId)
      .then((run) => {
        if (!cancelled) setProjectId(run.project_id);
      })
      .catch(() => {
        if (!cancelled) setProjectId(null);
      });
    return () => {
      cancelled = true;
    };
  }, [runId]);

  if (!runId) {
    return <p className="text-red-600">No run id provided.</p>;
  }

  const failedResults = events
    .map((e, i) => ({ event: e, index: i }))
    .filter(({ event }) => event.type === "result" && event.status === "failed");

  const getState = (key: string): FailureAnalysisState => analyses[key] ?? emptyAnalysisState;

  const setState = (key: string, patch: Partial<FailureAnalysisState>) => {
    setAnalyses((prev) => ({ ...prev, [key]: { ...getState(key), ...patch } }));
  };

  const handleAnalyze = async (event: ExecutionEvent, key: string) => {
    setState(key, { loading: true, error: null });
    try {
      const resp = await analyzeFailure({
        error_message: event.error_message ?? "",
        stack_trace: event.stack_trace ?? "",
        test_case_title: event.test_case_id ?? "",
      });
      setState(key, { loading: false, analysis: resp.analysis, source: resp.source });
    } catch (err) {
      setState(key, { loading: false, error: err instanceof Error ? err.message : "Analysis failed" });
    }
  };

  const handleCreateDefect = async (event: ExecutionEvent, key: string) => {
    const state = getState(key);
    if (!state.analysis || !projectId) return;
    setState(key, { defectLoading: true, defectError: null });
    try {
      const defect = await createDefect({
        project_id: projectId,
        title: state.analysis.root_cause.slice(0, 80),
        description: state.analysis.recommendation,
        severity: "high",
        priority: "high",
        related_test_case_id: event.test_case_id ?? null,
      });
      setState(key, { defectLoading: false, defectId: defect.id });
    } catch (err) {
      setState(key, { defectLoading: false, defectError: err instanceof Error ? err.message : "Failed to create defect" });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Test Run {runId}</h1>
        <p className="text-sm text-neutral-500">Status: {status}</p>
      </div>

      <ExecutionTimeline events={events} />

      {failedResults.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Failures</h2>
          {failedResults.map(({ event, index }) => {
            const key = keyFor(event, index);
            const state = getState(key);
            return (
              <div key={key} className="rounded-md border border-neutral-200 dark:border-neutral-800 p-3 space-y-2">
                <div className="flex items-center justify-between">
                  <p className="font-medium">{event.test_case_id}</p>
                  {!state.analysis && (
                    <button
                      onClick={() => handleAnalyze(event, key)}
                      disabled={state.loading}
                      className="rounded-md bg-brand-600 px-3 py-1.5 text-sm text-white hover:bg-brand-700 disabled:opacity-50"
                    >
                      {state.loading ? "Analyzing…" : "Analyze with AI"}
                    </button>
                  )}
                </div>
                {event.error_message && (
                  <p className="text-sm text-red-600">{event.error_message}</p>
                )}
                {state.error && <p className="text-sm text-red-600">{state.error}</p>}

                {state.analysis && (
                  <div className="space-y-2 rounded-md bg-neutral-50 dark:bg-neutral-900 p-3">
                    <div className="flex items-center gap-2">
                      {state.source && <AIInsightBadge source={state.source} />}
                      <span className="text-xs text-neutral-500">
                        Confidence {(state.analysis.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p className="text-sm"><span className="font-medium">Root cause:</span> {state.analysis.root_cause}</p>
                    <p className="text-sm"><span className="font-medium">Recommendation:</span> {state.analysis.recommendation}</p>
                    <p className="text-sm"><span className="font-medium">Affected component:</span> {state.analysis.affected_component}</p>

                    {!state.defectId ? (
                      <button
                        onClick={() => handleCreateDefect(event, key)}
                        disabled={state.defectLoading || !projectId}
                        className="rounded-md bg-neutral-900 dark:bg-neutral-100 dark:text-neutral-900 px-3 py-1.5 text-sm text-white disabled:opacity-50"
                      >
                        {state.defectLoading ? "Creating…" : "Create Defect"}
                      </button>
                    ) : (
                      <p className="text-sm text-green-600">Defect created: {state.defectId}</p>
                    )}
                    {state.defectError && <p className="text-sm text-red-600">{state.defectError}</p>}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
