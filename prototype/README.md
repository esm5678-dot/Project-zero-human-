# ZERO OPS offline MVP

Open `index.html` locally in a modern browser. No install, backend, login, external dependencies, or paid API.

Features: add fictional inquiries, deterministic keyword classification, suggested reply drafts, status management, delete, CSV export with spreadsheet-formula injection mitigation.

Safety: synthetic data only; no automatic customer messaging, no storage after refresh, no real AI model calls. Never enter real personal information. This is a demo, not a production CRM.

Manual acceptance tests:
1. Open index.html and press demo: 3 records appear.
2. Verify delivery / booking / refund categories.
3. Change status to complete; totals update.
4. Export CSV; verify UTF-8 Korean content.
5. Delete a record and clear all records.
6. Refresh: records disappear.

The next stage is real user feedback, requiring explicit outreach approval.
