import { useEffect, useState } from "react";
import { listDefects } from "../services/api/quality";
import type { DefectOut } from "../services/api/quality";
import { EmptyState } from "../components/common/EmptyState";

const SEVERITY_COLOR: Record<string, string> = {
  critical: "text-red-600",
  high: "text-orange-600",
  medium: "text-amber-600",
  low: "text-neutral-500",
};

export function DefectsPage({ projectId }: { projectId: string }) {
  const [defects, setDefects] = useState<DefectOut[] | null>(null);

  useEffect(() => {
    listDefects(projectId).then(setDefects);
  }, [projectId]);

  if (defects === null) {
    return <p className="text-neutral-500">Loading defects…</p>;
  }

  if (defects.length === 0) {
    return (
      <EmptyState
        title="No defects recorded"
        description="Defects created from failed test results (via AI Failure Analysis on a test run) will appear here."
      />
    );
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Defects ({defects.length})</h1>
      <div className="space-y-3">
        {defects.map((d) => (
          <div key={d.id} className="rounded-md border border-neutral-200 dark:border-neutral-800 p-3">
            <div className="flex items-center justify-between">
              <p className="font-medium">{d.title}</p>
              <span className={`text-sm font-medium ${SEVERITY_COLOR[d.severity] ?? "text-neutral-500"}`}>
                {d.severity}
              </span>
            </div>
            <p className="text-sm text-neutral-500">priority {d.priority} · status {d.status}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
