import { useDefaultProjectId } from "../hooks/useDefaultProjectId";
import { TestSuitesPage } from "./TestSuitesPage";

export function TestSuitesRoute() {
  const { projectId, isLoading } = useDefaultProjectId();
  if (isLoading || !projectId) {
    return <p className="text-neutral-500">Loading Test Suites…</p>;
  }
  return <TestSuitesPage projectId={projectId} />;
}
