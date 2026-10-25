# Internal agent execution v0.1

This is a **deterministic** agent-style runner, not an LLM-powered autonomous company.

## What it really does
- Reads a task queue, executes three approved internal operations, and uploads results as a GitHub Actions artifact.
- Audits presence of obvious secret-like files, checks MVP source/JavaScript syntax, counts experiment log rows.
- Rejects external tasks such as sending emails unless separately implemented and approved (current runner does not implement them).
- No paid API calls, customer messaging, deployment, secrets, or repository write permission.

## Limits
- No autonomous strategy, code editing, persistent memory updates, or actual sales.
- Scheduled GitHub Actions may be delayed or suspended; verify the Actions run.
- A zero-spend claim covers new cash paid by this runner only, not existing subscriptions or GitHub's economic value.
- Static checks are not full security tests.

## Verify
Run `python3 scripts/run_agents.py` locally (requires Node.js for the MVP check) or trigger **ZERO HUMAN internal agent execution** in GitHub Actions. Expect three completed tasks and one blocked task in the artifact.
