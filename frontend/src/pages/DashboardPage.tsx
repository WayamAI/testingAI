import { useQuery } from "@tanstack/react-query";
import { getDashboard } from "../services/api/dashboard";
import { MetricCard } from "../components/dashboard/MetricCard";

export function DashboardPage({ projectId }: { projectId: string }) {
  const { data, isLoading } = useQuery({ queryKey: ["dashboard", projectId], queryFn: () => getDashboard(projectId) });

  if (isLoading || !data) return <p className="text-neutral-500">Loading dashboard…</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Dashboard</h1>
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <MetricCard label="Quality Score" value={data.quality_score} accent />
        <MetricCard label="Pass Rate" value={`${(data.pass_rate * 100).toFixed(1)}%`} />
        <MetricCard label="Total Tests" value={data.total_tests} />
        <MetricCard label="Critical Defects" value={data.critical_defects} />
        <MetricCard label="Executed" value={data.executed} />
        <MetricCard label="Passed" value={data.passed} />
        <MetricCard label="Failed" value={data.failed} />
        <MetricCard label="Flaky Tests" value={data.flaky_tests} />
      </div>
    </div>
  );
}
