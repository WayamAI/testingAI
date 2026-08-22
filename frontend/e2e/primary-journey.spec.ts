import { test, expect } from "@playwright/test";

test("primary demo journey: login through release readiness", async ({ page }) => {
  await page.goto("/login");
  await page.getByRole("button", { name: /demo login/i }).click();
  await expect(page).toHaveURL(/dashboard/);
  await expect(page.getByText("Quality Score")).toBeVisible();

  await page.goto("/ai/test-generator");
  await page.getByLabel(/requirement/i).fill("Users can reset their password using their registered email.");
  await page.getByRole("button", { name: /^generate$/i }).click();
  // The brief's original assertion (`getByText(/happy path/i)`) asserts on
  // literal LLM-generated case title/type text. Against the real Ollama
  // Cloud provider (not the deterministic demo-fallback), that phrasing
  // varies run to run (observed: "happy_path", "functional", case titles
  // with no "happy" wording at all) even though generation succeeded every
  // time. AITestGeneratorPage only renders the "Create Suite from Accepted"
  // button once `cases.length > 0`, so waiting on that button is a
  // deterministic, structural proof that generation produced cases,
  // regardless of the LLM's exact wording.
  const createSuiteButton = page.getByRole("button", { name: /create suite from accepted/i });
  await expect(createSuiteButton).toBeVisible({ timeout: 15000 });
  await expect(page.getByText(/confidence \d+%/i).first()).toBeVisible();

  await createSuiteButton.click();
  await expect(page.getByText(/suite created/i)).toBeVisible({ timeout: 10000 });

  // Note: the real release-readiness route is /quality/release-readiness
  // (not /release-readiness) per App.tsx's route table.
  await page.goto("/quality/release-readiness");
  await expect(page.getByText(/READY|BLOCKED|REQUIRES_REVIEW/)).toBeVisible();
});
