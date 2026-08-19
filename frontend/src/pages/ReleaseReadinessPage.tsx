import { useQuery } from "@tanstack/react-query";
import { getReleaseReadiness } from "../services/api/quality";

const STATUS_STYLES: Record<string, string> = {
  READY: "bg-green-100 text-green-800",
  READY_WITH_RISK: "bg-amber-100 text-amber-800",
  REQUIRES_REVIEW: "bg-orange-100 text-orange-800",
  BLOCKED: "bg-red-100 text-red-800",
};

export function ReleaseReadinessPage({ projectId }: { projectId: string }) {
  const { data } = useQuery({ queryKey: ["release-readiness", projectId], queryFn: () => getReleaseReadiness(projectId) });
  if (!data) return <p className="text-neutral-500">Loading…</p>;

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Release Readiness</h1>
      <span className={`inline-block rounded-full px-3 py-1 text-sm font-semibold ${STATUS_STYLES[data.status]}`}>
        {data.status}
      </span>
      <p>Pass rate: {(data.pass_rate * 100).toFixed(1)}%</p>
      <p>Quality score: {data.quality_score}</p>
      {data.gate_violations.length > 0 && (
        <ul className="list-disc pl-5 text-sm text-red-600">
          {data.gate_violations.map((v, i) => <li key={i}>{v}</li>)}
        </ul>
      )}
    </div>
  );
}
