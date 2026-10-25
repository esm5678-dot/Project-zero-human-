const { test, after } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const fsSync = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { chromium } = require('playwright');

const htmlPromise = fs.readFile(path.resolve(__dirname, '../prototype/index.html'));
const server = http.createServer(async (_req, response) => {
  response.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  response.end(await htmlPromise);
});
const urlPromise = new Promise(resolve => server.listen(0, '127.0.0.1', () => resolve(`http://127.0.0.1:${server.address().port}/`)));
const browserPath = process.env.CHROMIUM_PATH || (fsSync.existsSync('/usr/bin/chromium') ? '/usr/bin/chromium' : undefined);
const browserPromise = chromium.launch({ executablePath: browserPath, headless: true, args: ['--no-sandbox'] });
after(async () => { await (await browserPromise).close(); server.close(); });

async function page(options = {}, onRequest) {
  const context = await (await browserPromise).newContext({ acceptDownloads: true, ...options });
  const tab = await context.newPage();
  if (onRequest) tab.on('request', onRequest);
  await tab.goto(await urlPromise);
  return { tab, context };
}

async function add(tab, alias, message) {
  await tab.locator('#alias').fill(alias);
  await tab.locator('#message').fill(message);
  await tab.locator('#add').click();
}

test('demo, categories, status, and row deletion', async () => {
  const { tab, context } = await page();
  try {
    await tab.locator('#demo').click();
    assert.deepEqual(await tab.locator('#rows tr td:nth-child(2)').allTextContents(), ['배송', '예약', '환불/취소']);
    assert.match(await tab.locator('#stats').innerText(), /전체 3건/);
    await tab.locator('#rows select').first().selectOption('완료');
    assert.match(await tab.locator('#stats').innerText(), /완료 1건/);
    await tab.locator('#rows button').first().click();
    assert.equal(await tab.locator('#rows tr').count(), 2);
  } finally { await context.close(); }
});

test('manual registration, fallback category, validation, and length limit', async () => {
  const { tab, context } = await page();
  try {
    await tab.locator('#add').click();
    assert.equal(await tab.locator('#rows tr').count(), 0);
    assert.match(await tab.locator('#notice').innerText(), /입력/);
    await add(tab, '가상고객', '안녕하세요');
    assert.equal(await tab.locator('#rows tr td:nth-child(2)').innerText(), '기타');
    await add(tab, '가상고객', '결제 영수증 문의');
    await add(tab, '가상고객', '상품 재고 문의');
    assert.deepEqual(await tab.locator('#rows tr td:nth-child(2)').allTextContents(), ['기타', '결제', '상품']);
    await tab.locator('#alias').fill('가상고객');
    await tab.locator('#message').fill('x'.repeat(2001));
    await tab.locator('#add').click();
    assert.equal(await tab.locator('#rows tr').count(), 3);
  } finally { await context.close(); }
});

test('CSV download has BOM, Korean text, and correct row count', async () => {
  const { tab, context } = await page();
  try {
    await tab.locator('#demo').click();
    const [download] = await Promise.all([tab.waitForEvent('download'), tab.locator('#export').click()]);
    assert.equal(download.suggestedFilename(), 'zero-ops-inquiries.csv');
    const csv = await fs.readFile(await download.path(), 'utf8');
    assert.ok(csv.startsWith('\ufeffalias,category,msg,reply,status\r\n'));
    assert.equal(csv.split('\r\n').length, 4);
    assert.match(csv, /가상고객A/);
  } finally { await context.close(); }
});

test('clear confirmation and refresh remove records', async () => {
  const { tab, context } = await page();
  try {
    await tab.locator('#demo').click();
    tab.once('dialog', d => d.dismiss());
    await tab.locator('#clear').click();
    assert.equal(await tab.locator('#rows tr').count(), 3);
    tab.once('dialog', d => d.accept());
    await tab.locator('#clear').click();
    assert.equal(await tab.locator('#rows tr').count(), 0);
    await tab.locator('#demo').click();
    await tab.reload();
    assert.equal(await tab.locator('#rows tr').count(), 0);
  } finally { await context.close(); }
});

test('HTML input is rendered as text and no outbound request occurs', async () => {
  const outbound = [];
  const localUrl = await urlPromise;
  const { tab, context } = await page({}, request => { if (!request.url().startsWith(localUrl)) outbound.push(request.url()); });
  try {
    await add(tab, '<img src=x onerror="window.xss=1">', '<svg onload="window.xss=1">');
    assert.equal(await tab.evaluate(() => window.xss), undefined);
    assert.equal(await tab.locator('#rows img, #rows svg').count(), 0);
    assert.deepEqual(outbound, []);
  } finally { await context.close(); }
});

test('CSV formula cells are neutralized, including whitespace prefixes', async () => {
  const { tab, context } = await page();
  try {
    await add(tab, '=1+1', '  =1+1');
    const [download] = await Promise.all([tab.waitForEvent('download'), tab.locator('#export').click()]);
    const csv = await fs.readFile(await download.path(), 'utf8');
    assert.match(csv, /"'=1\+1"/);
    assert.equal(await tab.evaluate(() => csvCell('  =1+1')), '"\'  =1+1"');
  } finally { await context.close(); }
});

test('row controls have distinct accessible names', async () => {
  const { tab, context } = await page();
  try {
    await tab.locator('#demo').click();
    assert.equal(await tab.locator('#rows select[aria-label]').count(), 3);
    assert.equal(await tab.locator('#rows button[aria-label]').count(), 3);
    const names = await tab.locator('#rows select').evaluateAll(elements => elements.map(el => el.getAttribute('aria-label')));
    assert.equal(new Set(names).size, 3);
  } finally { await context.close(); }
});

test('mobile viewport and keyboard controls work', async () => {
  const { tab, context } = await page({ viewport: { width: 375, height: 812 } });
  try {
    assert.equal(await tab.locator('#add').isVisible(), true);
    await tab.locator('#alias').focus();
    await tab.keyboard.type('가상고객');
    await tab.keyboard.press('Tab');
    assert.equal(await tab.evaluate(() => document.activeElement.id), 'message');
    await tab.keyboard.type('예약 문의');
    await tab.keyboard.press('Tab');
    await tab.keyboard.press('Enter');
    assert.equal(await tab.locator('#rows tr').count(), 1);
  } finally { await context.close(); }
});
