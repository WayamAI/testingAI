import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DashboardPage } from "./DashboardPage";
import * as dashboardApi from "../services/api/dashboard";

vi.spyOn(dashboardApi, "getDashboard").mockResolvedValue({
  total_tests: 100, executed: 90, passed: 80, failed: 8, skipped: 2,
  flaky_tests: 7, pass_rate: 0.888, critical_defects: 1, quality_score: 86,
  recent_runs: [],
});

describe("DashboardPage", () => {
  it("renders key metrics from the API", async () => {
    const client = new QueryClient();
    render(
      <QueryClientProvider client={client}>
        <DashboardPage projectId="proj1" />
      </QueryClientProvider>
    );
    await waitFor(() => expect(screen.getByText("86")).toBeInTheDocument());
    expect(screen.getByText(/89(\.\d)?%|88\.8%/)).toBeTruthy();
  });
});
