import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AITestGeneratorPage } from "./AITestGeneratorPage";
import * as aiApi from "../services/api/ai";

vi.spyOn(aiApi, "generateTests").mockResolvedValue({
  source: "demo_fallback",
  cases: [
    { title: "Password reset happy path", type: "functional", priority: "high", steps: ["a", "b"], expected_result: "ok", ai_confidence: 0.95 },
  ],
});

describe("AITestGeneratorPage", () => {
  it("generates and displays test cases with a source badge", async () => {
    const client = new QueryClient();
    render(
      <MemoryRouter>
        <QueryClientProvider client={client}>
          <AITestGeneratorPage projectId="proj1" />
        </QueryClientProvider>
      </MemoryRouter>
    );
    fireEvent.change(screen.getByLabelText(/requirement/i), { target: { value: "Users can reset their password." } });
    fireEvent.click(screen.getByRole("button", { name: /generate/i }));

    await waitFor(() => expect(screen.getByText("Password reset happy path")).toBeInTheDocument());
    expect(screen.getByText(/demo fallback/i)).toBeInTheDocument();
  });
});
