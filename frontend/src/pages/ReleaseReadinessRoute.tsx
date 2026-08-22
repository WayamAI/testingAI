import { useDefaultProjectId } from "../hooks/useDefaultProjectId";
import { ReleaseReadinessPage } from "./ReleaseReadinessPage";

/**
 * Wrapper for the `/quality/release-readiness` route. Resolves the default
 * project id (the first project returned by `GET /api/projects`) and renders
 * the real ReleaseReadinessPage once it's available. This is a known
 * simplification — full project-switching UI is out of scope for this phase.
 */
export function ReleaseReadinessRoute() {
  const { projectId, isLoading } = useDefaultProjectId();

  if (isLoading || !projectId) {
    return <p className="text-neutral-500">Loading Release Readiness…</p>;
  }

  return <ReleaseReadinessPage projectId={projectId} />;
}
