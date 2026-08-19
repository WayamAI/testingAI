import { MetricCard } from "../dashboard/MetricCard";
import type { QualityScoreOut } from "../../services/api/quality";

export function QualityScoreBreakdown({ score }: { score: QualityScoreOut }) {
  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
      <MetricCard label="Overall" value={score.overall} accent />
      <MetricCard label="Functional" value={score.functional} />
      <MetricCard label="Reliability" value={score.reliability} />
      <MetricCard label="Security" value={score.security} />
      <MetricCard label="Performance" value={score.performance} />
      <MetricCard label="Accessibility" value={score.accessibility} />
      <MetricCard label="Coverage" value={score.coverage} />
    </div>
  );
}
