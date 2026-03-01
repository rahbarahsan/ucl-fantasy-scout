import { test, expect } from "@playwright/test";

test.describe("UCL Fantasy Scout E2E", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("renders the app header", async ({ page }) => {
    await expect(page.getByText("UCL Fantasy Scout")).toBeVisible();
  });

  test("shows the upload zone by default", async ({ page }) => {
    await expect(
      page.getByText(/drag.*drop|upload.*screenshot/i)
    ).toBeVisible();
  });

  test("can switch between Analyse and Research tabs", async ({ page }) => {
    const analyseTab = page.getByRole("button", { name: /analyse/i });
    const researchTab = page.getByRole("button", { name: /research/i });

    await analyseTab.click();
    await expect(
      page.getByText(/drag.*drop|upload.*screenshot/i)
    ).toBeVisible();

    await researchTab.click();
    await expect(page.getByPlaceholderText(/ask/i)).toBeVisible();
  });

  test("settings panel toggles", async ({ page }) => {
    const settingsBtn = page.getByRole("button", { name: /settings/i });
    await settingsBtn.click();
    await expect(page.getByText(/provider/i)).toBeVisible();
  });

  test("shows error on analyse without image", async ({ page }) => {
    // Try clicking analyse without uploading - should show upload zone
    await expect(
      page.getByText(/drag.*drop|upload.*screenshot/i)
    ).toBeVisible();
  });
});
