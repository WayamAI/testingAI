import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReleaseReadinessPage } from "./ReleaseReadinessPage";
import * as qualityApi from "../services/api/quality";

vi.spyOn(qualityApi, "getReleaseReadiness").mockResolvedValue({
  status: "BLOCKED", pass_rate: 0.93, critical_defects: 1, quality_score: 86,
  gate_violations: ["1 open critical defect(s) block release"],
});

describe("ReleaseReadinessPage", () => {
  it("shows BLOCKED status and the gate violation reason", async () => {
    const client = new QueryClient();
    render(
      <QueryClientProvider client={client}>
        <ReleaseReadinessPage projectId="proj1" />
      </QueryClientProvider>
    );
    await waitFor(() => expect(screen.getByText("BLOCKED")).toBeInTheDocument());
    expect(screen.getByText(/critical defect/i)).toBeInTheDocument();
  });
});
