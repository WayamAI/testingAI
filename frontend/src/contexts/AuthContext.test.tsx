import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
import { AuthProvider, useAuth, USER_KEY } from "./AuthContext";
import { TOKEN_KEY } from "../services/api/client";

function Probe() {
  const { token, user } = useAuth();
  return (
    <div>
      <span data-testid="token">{token ?? "none"}</span>
      <span data-testid="user">{user ? user.email : "none"}</span>
    </div>
  );
}

describe("AuthProvider session rehydration", () => {
  beforeEach(() => localStorage.clear());
  afterEach(cleanup);

  it("rehydrates both token and user when a valid session is stored", () => {
    localStorage.setItem(TOKEN_KEY, "stored-token");
    localStorage.setItem(
      USER_KEY,
      JSON.stringify({ id: "u1", email: "demo@wayam.ai", name: "Demo", role: "admin", organization_id: "o1" }),
    );

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );

    expect(screen.getByTestId("token").textContent).toBe("stored-token");
    expect(screen.getByTestId("user").textContent).toBe("demo@wayam.ai");
  });

  it("treats a corrupted stored user as logged out and clears both keys", () => {
    localStorage.setItem(TOKEN_KEY, "stored-token");
    localStorage.setItem(USER_KEY, "{not-json");

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );

    expect(screen.getByTestId("token").textContent).toBe("none");
    expect(screen.getByTestId("user").textContent).toBe("none");
    expect(localStorage.getItem(TOKEN_KEY)).toBeNull();
    expect(localStorage.getItem(USER_KEY)).toBeNull();
  });

  it("treats a token with no stored user as logged out", () => {
    localStorage.setItem(TOKEN_KEY, "stored-token");

    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );

    expect(screen.getByTestId("token").textContent).toBe("none");
    expect(screen.getByTestId("user").textContent).toBe("none");
  });
});
