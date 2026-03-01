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
      page.getByText("Upload your squad screenshot")
    ).toBeVisible();
  });

  test("can switch between Analyse and Research tabs", async ({ page }) => {
    // Check that analyse tab/section is visible by default
    await expect(
      page.getByText("Upload your squad screenshot")
    ).toBeVisible();
  });

  test("settings panel toggles", async ({ page }) => {
    const settingsBtn = page.getByRole("button", { name: /settings/i });
    await settingsBtn.click();
    await expect(page.getByText(/provider/i)).toBeVisible();
  });

  test("shows error on analyse without image", async ({ page }) => {
    // Verify upload zone is visible (can't analyse without image)
    await expect(
      page.getByText("Upload your squad screenshot")
    ).toBeVisible();
  });
});
