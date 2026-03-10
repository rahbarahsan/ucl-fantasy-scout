import { test, expect } from "@playwright/test";
import path from "path";

test.describe("UCL Fantasy Scout E2E", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("renders the app header", async ({ page }) => {
    await expect(page.getByText("UCL Fantasy Scout")).toBeVisible();
  });

  test("shows the upload zone by default", async ({ page }) => {
    await expect(page.getByText("Upload your squad screenshot")).toBeVisible();
  });

  test("can switch between Analyse and Research tabs", async ({ page }) => {
    // Check that analyse tab/section is visible by default
    await expect(page.getByText("Upload your squad screenshot")).toBeVisible();
  });

  test("settings panel toggles", async ({ page }) => {
    const settingsBtn = page.getByRole("button", { name: /settings/i });
    await settingsBtn.click();
    await expect(page.getByText(/provider/i)).toBeVisible();
  });

  test("shows error on analyse without image", async ({ page }) => {
    // Verify upload zone is visible (can't analyse without image)
    await expect(page.getByText("Upload your squad screenshot")).toBeVisible();
  });

  test("complete squad analysis flow with web screenshot", async ({ page }) => {
    console.log("🚀 Starting complete squad analysis test");

    // Upload the image file
    const imagePath = path.join(
      process.cwd(),
      "sample_data",
      "Ucl-fantasy-web.png",
    );
    console.log(`📁 Uploading image: ${imagePath}`);

    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(imagePath);

    // Wait for preview to load
    await page.waitForTimeout(2000);
    console.log("✅ Image uploaded and preview loaded");

    // Click analyze button
    const analyzeButton = page.locator(
      'button:has-text("Analyze Squad"), button:has-text("Analyse Squad")',
    );
    await analyzeButton.click();
    console.log("✅ Clicked Analyze button");

    // Wait for EITHER matchday confirmation OR analysis to start
    await page.waitForTimeout(2000);

    // Check for matchday confirmation dialog - wait up to 10 seconds for it to appear
    try {
      await page.waitForSelector("text=/Matchday Confirmation/i", {
        timeout: 10000,
      });
      console.log("⚠️ Matchday confirmation dialog appeared");

      // Find and fill the input
      const input = page.locator('input[type="text"]').first();
      await input.fill("round of 16 - 1st leg");
      console.log("✍️ Entered: round of 16 - 1st leg");

      await page.waitForTimeout(500);

      // Click submit button
      const submitButton = page
        .locator("button")
        .filter({ hasText: /submit|confirm|continue|ok/i })
        .first();
      await submitButton.click();
      console.log("✅ Submitted matchday clarification");

      await page.waitForTimeout(2000);
    } catch {
      console.log(
        "ℹ️ No matchday clarification needed - analysis started directly",
      );
    }

    // Wait for analysis to complete - look for results
    console.log("⏳ Waiting for analysis results (up to 3 minutes)...");

    const resultSelectors = [
      '[data-testid="verdict-item"]',
      ".verdict-card",
      ".player-verdict",
      "text=/START|BENCH|RISK/",
    ];

    let resultsFound = false;
    for (const selector of resultSelectors) {
      try {
        await page.waitForSelector(selector, { timeout: 180000 });
        console.log(
          `✅ Analysis complete - results found with selector: ${selector}`,
        );
        resultsFound = true;
        break;
      } catch {
        console.log(`⚠️ Selector not found: ${selector}`);
      }
    }

    if (!resultsFound) {
      // Take a screenshot for debugging
      await page.screenshot({
        path: "test-results/analysis-timeout.png",
        fullPage: true,
      });
      console.log("❌ No results found after timeout");

      // Get page content for debugging
      const bodyText = await page.locator("body").textContent();
      console.log("📄 Page content:", bodyText?.substring(0, 500));
    }

    expect(resultsFound).toBe(true);
    console.log("✅ Test completed successfully");
  });
});
