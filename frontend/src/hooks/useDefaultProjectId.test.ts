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

  it("returns the first project ID when API returns bare array with projects", async () => {
    // Real backend response shape: bare array
    mockApiClient.get = vi.fn().mockResolvedValue({
      data: [
        { id: "project-1", name: "Project One" },
        { id: "project-2", name: "Project Two" },
      ],
    });

    const { result } = renderHook(() => useDefaultProjectId());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.projectId).toBe("project-1");
  });

  it("returns null when API returns empty array", async () => {
    // Real backend response shape: bare empty array
    mockApiClient.get = vi.fn().mockResolvedValue({
      data: [],
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
      data: [{ id: "project-1", name: "Project One" }],
    });

    renderHook(() => useDefaultProjectId());

    await waitFor(() => {
      expect(mockApiClient.get).toHaveBeenCalledWith("/api/projects");
    });
  });

  it("correctly handles response with single project", async () => {
    // Verify it extracts id from first item correctly
    mockApiClient.get = vi.fn().mockResolvedValue({
      data: [{ id: "single-project-id", name: "Only Project" }],
    });

    const { result } = renderHook(() => useDefaultProjectId());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.projectId).toBe("single-project-id");
  });
});
