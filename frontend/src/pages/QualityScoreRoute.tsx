import { useDefaultProjectId } from "../hooks/useDefaultProjectId";
import { QualityScorePage } from "./QualityScorePage";

/**
 * Wrapper for the `/quality/score` route. Resolves the default project id
 * (the first project returned by `GET /api/projects`) and renders the real
 * QualityScorePage once it's available. This is a known simplification —
 * full project-switching UI is out of scope for this phase.
 */
export function QualityScoreRoute() {
  const { projectId, isLoading } = useDefaultProjectId();

  if (isLoading || !projectId) {
    return <p className="text-neutral-500">Loading Quality Score…</p>;
  }

  return <QualityScorePage projectId={projectId} />;
}
