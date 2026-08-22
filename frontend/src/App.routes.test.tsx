import { describe, it, expect } from "vitest";
import { SIDEBAR_GROUPS } from "./components/layout/Sidebar";
import { ROUTE_PATHS } from "./App";

describe("routing coverage", () => {
  it("every sidebar item has a matching route", () => {
    const sidebarPaths = SIDEBAR_GROUPS.flatMap((g) => g.items.map((i) => i.path));
    for (const path of sidebarPaths) {
      expect(ROUTE_PATHS).toContain(path);
    }
  });
});
