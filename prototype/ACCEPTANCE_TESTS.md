# ZERO OPS MVP — Acceptance test plan

## Chromium browser verification (2026-10-25)

Run `npm ci && npx playwright install chromium && npm run test:browser` to repeat the automated checks. The test opens the local HTML through a loopback server; it does not publish the service.

Result: 8 browser tests passed. The existing static source check and CSV schema check also passed. Chromium covered demo data, all five named categories and fallback, status counts, input validation, CSV download and Korean text, delete and clear confirmation, refresh, keyboard use at a mobile viewport, script injection text rendering, and outbound requests. The test used synthetic records only.

Initial findings: the CSV helper did not prefix formulas after leading whitespace, and per-row status/delete controls lacked distinct accessible names. Both were fixed. The first test attempt also used a `file:` URL blocked by this test environment; the local test server resolved that setup issue. An initial CSV expectation overlooked the form's intentional whitespace trimming and was corrected.

## Manual browser checks (automated coverage above)
1. Open `prototype/index.html` in a modern browser.
2. Click **가상 예시 3건 넣기**: expect 3 rows, categories 배송 / 예약 / 환불·취소.
3. Set one row to **완료**: summary count updates.
4. Enter an inquiry with no recognized terms: category 기타.
5. Submit empty form: validation message, no new row.
6. Export CSV: Korean UTF-8 and correct row count.
7. Delete a row, then clear all (confirm): expect 0 rows.
8. Refresh: no previous inquiries remain.
9. Check outbound requests: only the loopback test page is requested.
10. Check mobile viewport and keyboard-only navigation.

## Known limitations
- Keyword matching is not a language model and may misclassify inquiries.
- Draft replies do not check real order or booking status.
- No customer messaging, authentication, persistent storage, or live integrations.
- No real customer data permitted; synthetic test records only.
- Browser automation ran in Chromium only; Firefox and Safari were not verified.
- CSV formula protection was checked against representative formula prefixes; no spreadsheet application was opened.

## Release gate
Do not claim production readiness or solicit paying customers until browser acceptance tests pass and a human approves external outreach and privacy/legal review.
