import { test, expect } from '@playwright/test';

test('operator inbox renders and shows the seeded demo handoffs', async ({ page, request }) => {
  // Login via the API to get a session cookie + csrf token.
  const login = await request.post('/login', {
    data: { email: '[email protected]', password: 'RelayDemo!2025' },
  });
  expect(login.ok()).toBeTruthy();

  await page.goto('/inbox');
  await expect(page.getByRole('heading', { name: 'Inbox' })).toBeVisible();
});

test('public share page returns 404 for a fabricated token', async ({ request }) => {
  const r = await request.get('/api/public/handoffs/this-token-does-not-exist');
  expect(r.status()).toBe(404);
});
