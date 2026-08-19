import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { generateTests } from "../services/api/ai";
import type { GeneratedTestCase } from "../services/api/ai";
import { createTestCase, createTestSuite, addCasesToSuite } from "../services/api/testing";
import { createTestRun } from "../services/api/execution";
import { AIInsightBadge } from "../components/ai/AIInsightBadge";

export function AITestGeneratorPage({ projectId }: { projectId: string }) {
  const navigate = useNavigate();
  const [requirementText, setRequirementText] = useState("");
  const [cases, setCases] = useState<GeneratedTestCase[]>([]);
  const [source, setSource] = useState<"ai" | "demo_fallback" | null>(null);
  const [accepted, setAccepted] = useState<Set<number>>(new Set());
  const [suiteCreated, setSuiteCreated] = useState<string | null>(null);
  const [runStarting, setRunStarting] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);

  const handleGenerate = async () => {
    const resp = await generateTests(requirementText);
    setCases(resp.cases);
    setSource(resp.source);
    setAccepted(new Set(resp.cases.map((_, i) => i)));
    setSuiteCreated(null);
  };

  const handleCreateSuite = async () => {
    const caseIds: string[] = [];
    for (const i of accepted) {
      const created = await createTestCase(projectId, null, cases[i]);
      caseIds.push(created.id);
    }
    const suite = await createTestSuite(projectId, `Generated: ${requirementText.slice(0, 40)}`);
    await addCasesToSuite(suite.id, caseIds);
    setSuiteCreated(suite.id);
  };

  const handleRunSuite = async () => {
    if (!suiteCreated) return;
    setRunStarting(true);
    setRunError(null);
    try {
      const run = await createTestRun(suiteCreated);
      navigate(`/test-runs/${run.id}`);
    } catch (err) {
      setRunError(err instanceof Error ? err.message : "Failed to start run");
    } finally {
      setRunStarting(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">AI Test Generator</h1>
      <label htmlFor="requirement" className="block text-sm font-medium">Requirement</label>
      <textarea
        id="requirement"
        aria-label="requirement"
        className="w-full rounded-md border border-neutral-300 dark:border-neutral-700 bg-transparent p-3"
        rows={3}
        value={requirementText}
        onChange={(e) => setRequirementText(e.target.value)}
      />
      <button
        onClick={handleGenerate}
        className="rounded-md bg-brand-600 px-4 py-2 text-white hover:bg-brand-700"
      >
        Generate
      </button>

      {cases.length > 0 && (
        <div className="space-y-3">
          {source && <AIInsightBadge source={source} />}
          {cases.map((c, i) => (
            <div key={i} className="rounded-md border border-neutral-200 dark:border-neutral-800 p-3">
              <div className="flex items-center justify-between">
                <p className="font-medium">{c.title}</p>
                <label className="flex items-center gap-1 text-sm">
                  <input
                    type="checkbox"
                    checked={accepted.has(i)}
                    onChange={(e) => {
                      const next = new Set(accepted);
                      e.target.checked ? next.add(i) : next.delete(i);
                      setAccepted(next);
                    }}
                  />
                  Accept
                </label>
              </div>
              <p className="text-sm text-neutral-500">{c.type} · {c.priority} · confidence {(c.ai_confidence * 100).toFixed(0)}%</p>
            </div>
          ))}
          <button
            onClick={handleCreateSuite}
            disabled={accepted.size === 0}
            className="rounded-md bg-neutral-900 dark:bg-neutral-100 dark:text-neutral-900 px-4 py-2 text-white disabled:opacity-50"
          >
            Create Suite from Accepted ({accepted.size})
          </button>
          {suiteCreated && (
            <div className="space-y-2">
              <p className="text-sm text-green-600">Suite created: {suiteCreated}</p>
              <button
                onClick={handleRunSuite}
                disabled={runStarting}
                className="rounded-md bg-brand-600 px-4 py-2 text-white hover:bg-brand-700 disabled:opacity-50"
              >
                {runStarting ? "Starting run…" : "Run Suite"}
              </button>
              {runError && <p className="text-sm text-red-600">{runError}</p>}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
