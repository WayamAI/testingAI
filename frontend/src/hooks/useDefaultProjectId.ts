import { useEffect, useState } from "react";
import { apiClient } from "../services/api/client";

interface Project {
  id: string;
  name: string;
}

interface ProjectsResponse {
  data: Project[];
}

/**
 * Hook to fetch and return the default project ID (first project from the API).
 * This is a known simplification for the current phase — full project-switching UI
 * will be implemented in a later phase.
 *
 * Returns { projectId, isLoading } where:
 * - projectId: the ID of the first project, or null if loading or no projects exist
 * - isLoading: true while fetching, false once data is loaded
 */
export function useDefaultProjectId() {
  const [projectId, setProjectId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const { data } = await apiClient.get<ProjectsResponse>("/api/projects");
        const firstProject = data.data?.[0];
        setProjectId(firstProject?.id || null);
      } catch (error) {
        console.error("Failed to fetch projects:", error);
        setProjectId(null);
      } finally {
        setIsLoading(false);
      }
    };

    fetchProjects();
  }, []);

  return { projectId, isLoading };
}
