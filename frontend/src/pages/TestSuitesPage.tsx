import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listTestSuites } from "../services/api/testing";
import type { TestSuiteOut } from "../services/api/testing";
import { createTestRun } from "../services/api/execution";
import { EmptyState } from "../components/common/EmptyState";

export function TestSuitesPage({ projectId }: { projectId: string }) {
  const navigate = useNavigate();
  const [suites, setSuites] = useState<TestSuiteOut[] | null>(null);
  const [startingId, setStartingId] = useState<string | null>(null);

  useEffect(() => {
    listTestSuites(projectId).then(setSuites);
  }, [projectId]);

  const handleRun = async (suiteId: string) => {
    setStartingId(suiteId);
    try {
      const run = await createTestRun(suiteId);
      navigate(`/test-runs/${run.id}`);
    } finally {
      setStartingId(null);
    }
  };

  if (suites === null) {
    return <p className="text-neutral-500">Loading test suites…</p>;
  }

  if (suites.length === 0) {
    return (
      <EmptyState
        title="No test suites yet"
        description="Create a suite from AI Test Generator, or connect a real project to run its own tests."
      />
    );
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Test Suites ({suites.length})</h1>
      <div className="space-y-3">
        {suites.map((s) => (
          <div key={s.id} className="flex items-center justify-between rounded-md border border-neutral-200 dark:border-neutral-800 p-3">
            <div>
              <p className="font-medium">{s.name}</p>
              <p className="text-sm text-neutral-500">{s.test_case_ids.length} test case(s)</p>
            </div>
            <button
              onClick={() => handleRun(s.id)}
              disabled={startingId === s.id}
              className="rounded-md bg-brand-600 px-3 py-1.5 text-sm text-white hover:bg-brand-700 disabled:opacity-50"
            >
              {startingId === s.id ? "Starting…" : "Run"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
