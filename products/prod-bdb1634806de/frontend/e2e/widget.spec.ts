import { test, expect } from '@playwright/test';

test('public widget loads', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Is it safe here right now?')).toBeVisible();
});
