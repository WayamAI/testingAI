import { useDefaultProjectId } from "../hooks/useDefaultProjectId";
import { AITestGeneratorPage } from "./AITestGeneratorPage";

/**
 * Wrapper for the `/ai/test-generator` route. Resolves the default project id
 * (the first project returned by `GET /api/projects`) and renders the real
 * AITestGeneratorPage once it's available. This is a known simplification —
 * full project-switching UI is out of scope for this phase.
 */
export function AITestGeneratorRoute() {
  const { projectId, isLoading } = useDefaultProjectId();

  if (isLoading || !projectId) {
    return <p className="text-neutral-500">Loading AI Test Generator…</p>;
  }

  return <AITestGeneratorPage projectId={projectId} />;
}
