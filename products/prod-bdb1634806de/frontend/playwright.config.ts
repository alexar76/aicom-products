import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  timeout: 30000,
  use: {
    baseURL: './',
    headless: true,
    trace: 'on-first-retry',
  },
});
