# ZERO OPS MVP — Acceptance test plan

## Manual browser checks (pending)
1. Open `prototype/index.html` in a modern browser.
2. Click **가상 예시 3건 넣기**: expect 3 rows, categories 배송 / 예약 / 환불·취소.
3. Set one row to **완료**: summary count updates.
4. Enter an inquiry with no recognized terms: category 기타.
5. Submit empty form: validation message, no new row.
6. Export CSV: Korean UTF-8 and correct row count.
7. Delete a row, then clear all (confirm): expect 0 rows.
8. Refresh: no previous inquiries remain.
9. Open browser developer tools Network tab: no outbound requests expected.
10. Check mobile viewport and keyboard-only navigation.

## Known limitations
- Keyword matching is not a language model and may misclassify inquiries.
- Draft replies do not check real order or booking status.
- No customer messaging, authentication, persistent storage, or live integrations.
- No real customer data permitted; synthetic test records only.

## Release gate
Do not claim production readiness or solicit paying customers until browser acceptance tests pass and a human approves external outreach and privacy/legal review.
