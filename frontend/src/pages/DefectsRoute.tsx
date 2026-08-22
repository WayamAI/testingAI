import { useDefaultProjectId } from "../hooks/useDefaultProjectId";
import { DefectsPage } from "./DefectsPage";

export function DefectsRoute() {
  const { projectId, isLoading } = useDefaultProjectId();
  if (isLoading || !projectId) {
    return <p className="text-neutral-500">Loading Defects…</p>;
  }
  return <DefectsPage projectId={projectId} />;
}
