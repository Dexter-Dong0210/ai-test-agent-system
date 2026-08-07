/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// @ts-expect-error  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2YTJScGFRPT06MzdmYzcwMWM=

import { defineConfig } from '@playwright/test';

// Enable insecure browser config (disabled security + CSP bypass) only when explicitly requested.
// Example: PLAYWRIGHT_INSECURE=1 npx playwright test
const insecureE2E = process.env.PLAYWRIGHT_INSECURE === '1';

// Base launch args: always enable software WebGL for sigma.js graph rendering in headless mode.
const launchArgs = [
  '--use-gl=angle',
  '--use-angle=swiftshader',
  '--enable-webgl',
  '--enable-unsafe-swiftshader',
];

if (insecureE2E) {
  // Allow cross-origin requests to gitnexus serve on a different port when explicitly enabled.
  launchArgs.unshift('--disable-web-security', '--disable-site-isolation-trials');
}

export default defineConfig({
  testDir: './e2e',
  testIgnore: ['**/manual-record.spec.ts', '**/debug-issues.spec.ts'],
  timeout: 60_000,
  retries: process.env.CI ? 1 : 0,
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'retain-on-failure',
    screenshot: 'retain-on-failure',
    video: 'retain-on-failure',
    launchOptions: {
      args: launchArgs,
    },
    // Vite dev server sets COEP require-corp for SharedArrayBuffer (LadybugDB WASM).
    // Only bypass CSP when explicitly running in insecure E2E mode.
    bypassCSP: insecureE2E,
  },
  projects: [
    {
      name: 'chromium',
      use: { browserName: 'chromium' },
    },
  ],
  reporter: [['list'], ['html', { open: 'never', outputFolder: 'playwright-report' }]],
  outputDir: 'test-results',
});
// TODO  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2YTJScGFRPT06MzdmYzcwMWM=
