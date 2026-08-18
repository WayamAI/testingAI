import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { TestRunPage } from "./TestRunPage";
import * as executionApi from "../services/api/execution";
import * as socketHook from "../hooks/useExecutionSocket";

vi.spyOn(socketHook, "useExecutionSocket").mockReturnValue({
  status: "completed",
  events: [
    {
      type: "result",
      test_case_id: "case-1",
      status: "failed",
      error_message: "Expected 200 but got 500",
      stack_trace: "at line 42",
    },
  ],
});

// The run under view belongs to project "project-B" — deliberately NOT the
// "first" project a naive useDefaultProjectId guess would resolve to.
vi.spyOn(executionApi, "getTestRun").mockResolvedValue({
  id: "run-1",
  project_id: "project-B",
  suite_id: "suite-1",
  status: "completed",
});

vi.spyOn(executionApi, "analyzeFailure").mockResolvedValue({
  analysis: {
    root_cause: "Null pointer in checkout handler",
    confidence: 0.87,
    recommendation: "Add null guard before accessing cart total",
    affected_component: "checkout-service",
  },
  source: "demo_fallback",
});

const createDefectSpy = vi.spyOn(executionApi, "createDefect").mockResolvedValue({
  id: "defect-1",
  title: "Null pointer in checkout handler",
  severity: "high",
  priority: "high",
  status: "open",
});

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/test-runs/run-1"]}>
      <Routes>
        <Route path="/test-runs/:runId" element={<TestRunPage />} />
      </Routes>
    </MemoryRouter>
  );
}

describe("TestRunPage", () => {
  it("creates the defect using the run's real project_id, not a default-project guess", async () => {
    renderPage();

    fireEvent.click(await screen.findByRole("button", { name: /analyze with ai/i }));
    await waitFor(() => expect(screen.getByText(/Null pointer in checkout handler/)).toBeInTheDocument());

    fireEvent.click(screen.getByRole("button", { name: /create defect/i }));

    await waitFor(() => expect(createDefectSpy).toHaveBeenCalledTimes(1));
    expect(createDefectSpy).toHaveBeenCalledWith(
      expect.objectContaining({ project_id: "project-B", related_test_case_id: "case-1" })
    );

    await waitFor(() => expect(screen.getByText(/Defect created: defect-1/)).toBeInTheDocument());
  });
});
