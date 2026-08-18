import { describe, it, expect, beforeEach, vi } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";

// Mock the apiClient before importing the hook
vi.mock("../services/api/client");

// Import after mocking
import { useDefaultProjectId } from "./useDefaultProjectId";
import { apiClient } from "../services/api/client";

const mockApiClient = apiClient as any;

describe("useDefaultProjectId", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("returns isLoading=true initially", () => {
    mockApiClient.get = vi.fn(() => new Promise(() => {})); // Never resolves

    const { result } = renderHook(() => useDefaultProjectId());

    expect(result.current.isLoading).toBe(true);
    expect(result.current.projectId).toBeNull();
  });

  it("returns the first project ID when API succeeds", async () => {
    mockApiClient.get = vi.fn().mockResolvedValue({
      data: {
        data: [
          { id: "project-1", name: "Project One" },
          { id: "project-2", name: "Project Two" },
        ],
      },
    });

    const { result } = renderHook(() => useDefaultProjectId());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.projectId).toBe("project-1");
  });

  it("returns null when projects array is empty", async () => {
    mockApiClient.get = vi.fn().mockResolvedValue({
      data: {
        data: [],
      },
    });

    const { result } = renderHook(() => useDefaultProjectId());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.projectId).toBeNull();
  });

  it("returns null and sets isLoading=false when API fails", async () => {
    mockApiClient.get = vi.fn().mockRejectedValue(new Error("API error"));

    const { result } = renderHook(() => useDefaultProjectId());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.projectId).toBeNull();
  });

  it("calls GET /api/projects on mount", async () => {
    mockApiClient.get = vi.fn().mockResolvedValue({
      data: {
        data: [{ id: "project-1", name: "Project One" }],
      },
    });

    renderHook(() => useDefaultProjectId());

    await waitFor(() => {
      expect(mockApiClient.get).toHaveBeenCalledWith("/api/projects");
    });
  });
});
