# Model integration feasibility — 2026-10-26

**Decision: NO-GO for unattended LLM calls.** The zero-additional-spend rule takes precedence over autonomy. A GitHub Actions runner is not itself a free LLM inference service.

## Implemented now
- `scripts/model_gate.py`: fail-closed preflight policy checker (no network calls).
- `config/model_policy.json`: model disabled by default; no provider credentials.
- `tests/test_model_gate.py`: regression tests for spend, verification, approval and data gates.

## Before enabling any real model
1. Identify provider and verify the exact account's included/free quota and overage behavior.
2. Establish a hard zero-spend enforcement mechanism (not just a cost estimate).
3. Obtain explicit approval for provider and intended tasks.
4. Set daily request and token limits and disable external customer data.
5. Keep external actions (emails, deployment, payments, production writes) human-gated.
6. Test in an isolated branch; never put API tokens in a public repository.

**Important:** passing the gate does not implement a model client, verify provider billing, or grant authorization. No autonomous model inference is enabled.

## Current fallback
Scheduled deterministic checks continue without new model costs. GitHub Actions execution and model usage are different systems.
