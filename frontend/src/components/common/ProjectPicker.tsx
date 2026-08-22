import { useEffect, useState } from "react";
import { listProjects } from "../../services/api/intake";
import type { ProjectOut } from "../../services/api/intake";

export function ProjectPicker({ value, onChange }: { value: string | null; onChange: (projectId: string) => void }) {
  const [projects, setProjects] = useState<ProjectOut[] | null>(null);

  useEffect(() => {
    listProjects().then((all) => {
      setProjects(all);
      if (!value && all.length > 0) onChange(all[0].id);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (projects === null) {
    return <p className="text-sm text-neutral-500">Loading projects…</p>;
  }

  if (projects.length === 0) {
    return <p className="text-sm text-neutral-500">No projects yet — create one from Connect Project first.</p>;
  }

  return (
    <select
      aria-label="Project"
      value={value ?? ""}
      onChange={(e) => onChange(e.target.value)}
      className="rounded-md border border-neutral-300 dark:border-neutral-700 bg-transparent px-3 py-1.5 text-sm"
    >
      {projects.map((p) => (
        <option key={p.id} value={p.id}>
          {p.name} {p.source === "connected" ? `(${p.detected_language ?? "connected"})` : "(demo)"}
        </option>
      ))}
    </select>
  );
}
