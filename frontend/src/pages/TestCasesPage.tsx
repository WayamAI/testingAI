import { useEffect, useState } from "react";
import { listTestCases } from "../services/api/testing";
import type { TestCaseOut } from "../services/api/testing";
import { EmptyState } from "../components/common/EmptyState";

export function TestCasesPage({ projectId }: { projectId: string }) {
  const [cases, setCases] = useState<TestCaseOut[] | null>(null);

  useEffect(() => {
    listTestCases(projectId).then(setCases);
  }, [projectId]);

  if (cases === null) {
    return <p className="text-neutral-500">Loading test cases…</p>;
  }

  if (cases.length === 0) {
    return (
      <EmptyState
        title="No test cases yet"
        description="Generate test cases from a requirement in AI Test Generator, or connect a real project to discover them automatically."
      />
    );
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Test Cases ({cases.length})</h1>
      <div className="overflow-x-auto rounded-lg border border-neutral-200 dark:border-neutral-800">
        <table className="w-full text-sm">
          <thead className="bg-neutral-50 dark:bg-neutral-900 text-left text-neutral-500">
            <tr>
              <th className="px-4 py-2 font-medium">Title</th>
              <th className="px-4 py-2 font-medium">Type</th>
              <th className="px-4 py-2 font-medium">Priority</th>
              <th className="px-4 py-2 font-medium">Automation</th>
              <th className="px-4 py-2 font-medium">Source</th>
            </tr>
          </thead>
          <tbody>
            {cases.map((c) => (
              <tr key={c.id} className="border-t border-neutral-200 dark:border-neutral-800">
                <td className="px-4 py-2 font-medium">{c.title}</td>
                <td className="px-4 py-2 text-neutral-500">{c.type}</td>
                <td className="px-4 py-2 text-neutral-500">{c.priority}</td>
                <td className="px-4 py-2 text-neutral-500">{c.automation_status}</td>
                <td className="px-4 py-2 text-neutral-500">{c.source}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
