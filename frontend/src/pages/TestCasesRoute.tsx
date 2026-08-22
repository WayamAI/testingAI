import { useDefaultProjectId } from "../hooks/useDefaultProjectId";
import { TestCasesPage } from "./TestCasesPage";

export function TestCasesRoute() {
  const { projectId, isLoading } = useDefaultProjectId();
  if (isLoading || !projectId) {
    return <p className="text-neutral-500">Loading Test Cases…</p>;
  }
  return <TestCasesPage projectId={projectId} />;
}
