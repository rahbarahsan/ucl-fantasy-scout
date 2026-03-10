import { test, expect } from "@playwright/test";
import { join } from "path";

test("Simple squad analysis test", async ({ page }) => {
  console.log("\n🚀 Starting simple test\n");

  // Navigate to app
  await page.goto("http://localhost:5173/");
  await expect(page.getByText("UCL Fantasy Scout")).toBeVisible();
  console.log("✅ App loaded");

  // Upload image
  const imagePath = join(process.cwd(), "sample_data", "Ucl-fantasy-web.png");
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles(imagePath);
  await page.waitForTimeout(2000);
  console.log("✅ Image uploaded");

  // Click Analyse button
  const analyseButton = page.getByRole("button", { name: /analyse squad/i });
  await analyseButton.click();
  console.log("✅ Clicked Analyse button");

  // Wait and check for matchday clarification
  await page.waitForTimeout(5000);
  
  const pageText = await page.locator('body').textContent();
  console.log(`\nPage content:\n${pageText?.substring(0, 500)}\n`);

  // Handle matchday clarification
  const clarificationHeading = page.getByText(/matchday confirmation needed/i);
  if (await clarificationHeading.isVisible({ timeout: 2000 }).catch(() => false)) {
    console.log("⚠️ Matchday clarification detected");
    
    const inputField = page.locator('input[type="text"]').last();
    await inputField.fill("Round of 16 - 1st leg");
    console.log("✍️ Entered matchday");
    
    const confirmButton = page.getByRole("button", { name: /confirm/i });
    await confirmButton.click();
    console.log("✅ Submitted matchday");
    
    // Wait for analysis to start
    await page.waitForTimeout(5000);
  } else {
    console.log("ℹ️  No clarification needed");
  }

  // Wait for results (or timeout)
  console.log("\n⏳ Waiting up to 2 minutes for results...\n");
  
  for (let i = 0; i < 12; i++) {
    await page.waitForTimeout(10000);
    const body = await page.locator('body').textContent();
    console.log(`[${i * 10}s] Checking for results...`);
    
    if (body?.includes('Squad Report')) {
      console.log("\n✅ SUCCESS - Squad Report found!");
      await page.screenshot({ path: 'test-results/success.png', fullPage: true });
      return;
    }
    
    if (body?.toLowerCase().includes('error')) {
      console.log("\n❌ ERROR detected");
      await page.screenshot({ path: 'test-results/error.png', fullPage: true });
      throw new Error("Analysis failed");
    }
  }

  console.log("\n⏱️ Timeout - no results after 2 minutes");
  await page.screenshot({ path: 'test-results/timeout.png', fullPage: true });
  throw new Error("Analysis timed out");
});
