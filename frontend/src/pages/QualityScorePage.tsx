import { useQuery } from "@tanstack/react-query";
import { getQualityScore } from "../services/api/quality";
import { QualityScoreBreakdown } from "../components/quality/QualityScoreBreakdown";

export function QualityScorePage({ projectId }: { projectId: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ["quality-score", projectId],
    queryFn: () => getQualityScore(projectId),
  });

  if (isLoading || !data) return <p className="text-neutral-500">Loading quality score…</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Quality Score</h1>
      <QualityScoreBreakdown score={data} />
    </div>
  );
}
