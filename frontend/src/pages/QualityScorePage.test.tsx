import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { QualityScorePage } from "./QualityScorePage";
import * as qualityApi from "../services/api/quality";

vi.spyOn(qualityApi, "getQualityScore").mockResolvedValue({
  overall: 86,
  functional: 90,
  reliability: 88,
  security: 82,
  performance: 79,
  accessibility: 95,
  coverage: 84,
});

describe("QualityScorePage", () => {
  it("renders the overall score and all sub-score breakdowns from the API", async () => {
    const client = new QueryClient();
    render(
      <QueryClientProvider client={client}>
        <QualityScorePage projectId="proj1" />
      </QueryClientProvider>
    );
    await waitFor(() => expect(screen.getAllByText("86").length).toBeGreaterThan(0));
    expect(screen.getByText("Functional")).toBeInTheDocument();
    expect(screen.getByText("Reliability")).toBeInTheDocument();
    expect(screen.getByText("Security")).toBeInTheDocument();
    expect(screen.getByText("Performance")).toBeInTheDocument();
    expect(screen.getByText("Accessibility")).toBeInTheDocument();
    expect(screen.getByText("Coverage")).toBeInTheDocument();
  });
});
