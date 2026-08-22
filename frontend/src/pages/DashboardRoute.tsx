import { useDefaultProjectId } from "../hooks/useDefaultProjectId";
import { DashboardPage } from "./DashboardPage";

/**
 * Wrapper for the `/dashboard` route. Resolves the default project id (the
 * first project returned by `GET /api/projects`) and renders the real
 * DashboardPage once it's available. This is a known simplification —
 * full project-switching UI is out of scope for this phase.
 */
export function DashboardRoute() {
  const { projectId, isLoading } = useDefaultProjectId();

  if (isLoading || !projectId) {
    return <p className="text-neutral-500">Loading dashboard…</p>;
  }

  return <DashboardPage projectId={projectId} />;
}
