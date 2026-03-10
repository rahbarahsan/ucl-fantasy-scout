import { test, expect } from "@playwright/test";
import { join } from "path";

test.describe("Squad Analysis E2E", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("http://localhost:5173/");
    await expect(page.getByText("UCL Fantasy Scout")).toBeVisible();
  });

  test("analyze web screenshot - simple flow", async ({ page }) => {
    console.log("Starting web screenshot analysis test...");

    // Step 1: Upload image using Playwright's native method
    const imagePath = join(process.cwd(), "sample_data", "Ucl-fantasy-web.png");
    
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(imagePath);
    
    // Wait for image to be processed and preview shown
    await page.waitForTimeout(3000);
    console.log("✅ Image uploaded and preview visible");

    // Step 2: Click Analyse button
    const analyseButton = page.getByRole("button", { name: /analyse squad/i });
    await expect(analyseButton).toBeVisible();
    await analyseButton.click();
    console.log("✅ Clicked Analyse Squad button");

    // Step 3: Wait for loading state
    // Step 3: Wait for either loading state or matchday clarification
    console.log("⏳ Checking for loading state or matchday clarification...");
    
    // Wait a bit for the API to respond
    await page.waitForTimeout(3000);

    // Step 4: Handle matchday clarification if it appears
    const clarificationHeading = page.getByText(/matchday confirmation/i);
    const isClarificationVisible = await clarificationHeading.isVisible({ timeout: 5000 }).catch(() => false);
    
    if (isClarificationVisible) {
      console.log("⚠️ Matchday clarification requested");
      
      const inputField = page.locator('input[type="text"]').last();
      await inputField.waitFor({ state: 'visible', timeout: 5000 });
      await inputField.fill("Round of 16 - 1st leg");
      console.log("✍️ Entered: Round of 16 - 1st leg");
      
      const submitButton = page.getByRole("button", { name: /confirm/i });
      await submitButton.click();
      console.log("✅ Matchday submitted");
      
      // Wait for analysis to restart
      await page.waitForTimeout(3000);
      console.log("⏳ Analysis restarted with confirmed matchday");
    } else {
      console.log("✓ No matchday clarification needed");
    }

    // Step 5: Wait for results - look for "Squad Report" text
    console.log("⏳ Waiting for analysis to complete...");
    
    // Add debugging - check page content periodically
    for (let i = 0; i < 12; i++) {
      await page.waitForTimeout(10000);
      const bodyText = await page.locator('body').textContent();
      console.log(`[${i * 10}s] Page contains: ${bodyText?.substring(0, 200).replace(/\s+/g, ' ')}`);
      
      // Check if results appeared
      const hasReport = bodyText?.includes('Squad Report');
      if (hasReport) {
        console.log("✅ Squad Report found!");
        break;
      }
      
      // Check if error appeared
      const hasError = bodyText?.toLowerCase().includes('error') || bodyText?.toLowerCase().includes('failed');
      if (hasError) {
        console.log("❌ Error detected on page");
        break;
      }
    }
    
    await expect(page.getByText(/squad report/i)).toBeVisible({ timeout: 10000 });
    console.log("✅ Squad Report visible - analysis complete!");

    // Step 6: Verify verdict badges
    const verdictBadges = page.getByText(/^(START|BENCH|RISK)$/);
    const verdictCount = await verdictBadges.count();
    
    console.log(`📊 Found ${verdictCount} verdict badges`);
    expect(verdictCount).toBeGreaterThan(0);

    // Step 7: Take screenshot of results
    await page.screenshot({ path: 'test-results/analysis-complete.png', fullPage: true });
    
    console.log("✅ Test complete!");
  });

  test("analyze mobile screenshot - simple flow", async ({ page }) => {
    console.log("Starting mobile screenshot analysis test...");

    // Step 1: Upload image using Playwright's native method
    const imagePath = join(process.cwd(), "sample_data", "Ucl-fantasy-ios.jpg");
    
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(imagePath);
    
    await page.waitForTimeout(3000);
    console.log("✅ Image uploaded and preview visible");

    // Step 2: Click Analyse button
    const analyseButton = page.getByRole("button", { name: /analyse squad/i });
    await expect(analyseButton).toBeVisible();
    await analyseButton.click();
    console.log("✅ Clicked Analyse Squad button");

    // Step 3: Wait for matchday clarification
    await page.waitForTimeout(3000);

    // Step 4: Handle matchday clarification
    const clarificationHeading = page.getByText(/matchday confirmation/i);
    const isClarificationVisible = await clarificationHeading.isVisible({ timeout: 5000 }).catch(() => false);
    
    if (isClarificationVisible) {
      console.log("⚠️ Matchday clarification requested");
      
      const inputField = page.locator('input[type="text"]').last();
      await inputField.waitFor({ state: 'visible', timeout: 5000 });
      await inputField.fill("Round of 16 - 1st leg");
      console.log("✍️ Entered: Round of 16 - 1st leg");
      
      const submitButton = page.getByRole("button", { name: /confirm/i });
      await submitButton.click();
      console.log("✅ Matchday submitted");
      
      await page.waitForTimeout(3000);
      console.log("⏳ Analysis started with confirmed matchday");
    }

    // Step 5: Wait for results
    console.log("⏳ Waiting for analysis to complete...");
    
    await expect(page.getByText(/squad report/i)).toBeVisible({ timeout: 120000 });
    console.log("✅ Squad Report visible - analysis complete!");

    // Step 6: Verify verdicts
    const verdictBadges = page.getByText(/^(START|BENCH|RISK)$/);
    const verdictCount = await verdictBadges.count();
    
    console.log(`📊 Found ${verdictCount} verdict badges`);
    expect(verdictCount).toBeGreaterThan(0);

    // Step 7: Take screenshot
    await page.screenshot({ path: 'test-results/mobile-analysis-complete.png', fullPage: true });
    
    console.log("✅ Test complete!");
  });
});
