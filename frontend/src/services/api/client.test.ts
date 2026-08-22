import { describe, it, expect, beforeEach } from "vitest";
import { apiClient } from "./client";

describe("apiClient", () => {
  beforeEach(() => localStorage.clear());

  it("attaches Authorization header when a token is stored", async () => {
    localStorage.setItem("wayam_token", "test-token-123");
    const config = await apiClient.interceptors.request.handlers![0]!.fulfilled!({
      headers: {},
    } as any);
    expect(config.headers.Authorization).toBe("Bearer test-token-123");
  });

  it("omits Authorization header when no token is stored", async () => {
    const config = await apiClient.interceptors.request.handlers![0]!.fulfilled!({
      headers: {},
    } as any);
    expect(config.headers.Authorization).toBeUndefined();
  });
});
