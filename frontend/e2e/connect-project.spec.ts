import { test, expect } from "@playwright/test";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

test("connect a real project and see genuine detected stack + pass/fail results", async ({ page }) => {
  await page.goto("/login");
  await page.getByRole("button", { name: /demo login/i }).click();
  await expect(page).toHaveURL(/dashboard/);

  await page.goto("/connect-project");
  await page.getByLabel(/project name/i).fill(`E2E Jest Fixture ${Date.now()}`);

  const fixtureZip = path.join(__dirname, "fixtures", "jest-fixture.zip");
  await page.getByLabel(/upload zip/i).setInputFiles(fixtureZip);
  await page.getByRole("button", { name: /^connect$/i }).click();

  // Real detection result, not a canned string.
  await expect(page.getByText("javascript/typescript · jest")).toBeVisible({ timeout: 15000 });

  const runButton = page.getByRole("button", { name: /^run tests$/i }).first();
  await expect(runButton).toBeEnabled();
  await runButton.click();

  await expect(page).toHaveURL(/test-runs\//);
  // The fixture's real suite: 2 passed, 1 intentionally failing test.
  await expect(page.getByText(/passed/i).first()).toBeVisible({ timeout: 60000 });
  await expect(page.getByText(/failed/i).first()).toBeVisible({ timeout: 60000 });
});
