import { test, expect } from '@playwright/test';

test('public widget renders', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Sentinel Safety Check')).toBeVisible();
});
