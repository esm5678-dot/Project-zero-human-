const { test, expect } = require('@playwright/test');
const path = require('path');
const { pathToFileURL } = require('url');

test('guided synthetic demo completes and resets', async ({ page }) => {
  await page.goto(pathToFileURL(path.resolve(__dirname, '../prototype/demo.html')).href);
  await expect(page.locator('#progress')).toHaveText('진행 0/3');
  await expect(page.locator('#two')).toBeDisabled();
  await expect(page.locator('#status')).toBeDisabled();
  await page.locator('#one').click();
  await expect(page.locator('#progress')).toHaveText('진행 1/3');
  await expect(page.locator('#out1')).toContainText('배송 문의');
  await page.locator('#two').click();
  await expect(page.locator('#progress')).toHaveText('진행 2/3');
  await expect(page.locator('#out2')).toContainText('답변 초안');
  await page.locator('#status').selectOption('완료');
  await expect(page.locator('#progress')).toHaveText('진행 3/3');
  await page.locator('#reset').click();
  await expect(page.locator('#progress')).toHaveText('진행 0/3');
  await expect(page.locator('#two')).toBeDisabled();
});

test('guided demo does not initiate outbound requests', async ({ page }) => {
  const outbound = [];
  page.on('request', request => {
    if (!request.url().startsWith('file:')) outbound.push(request.url());
  });
  await page.goto(pathToFileURL(path.resolve(__dirname, '../prototype/demo.html')).href);
  await page.locator('#one').click();
  await page.locator('#two').click();
  await page.locator('#status').selectOption('완료');
  expect(outbound).toEqual([]);
});
