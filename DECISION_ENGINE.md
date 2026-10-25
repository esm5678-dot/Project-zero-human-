# ZERO HUMAN — Decision Engine v0.2

## Purpose
Automatically select the next **internal** task without paid LLM calls, preserving zero additional cash spending and human approval for external actions.

## Selection
1. Read `data/task_backlog.json`.
2. Reject tasks with approval other than `internal_only` or an unrecognized action.
3. Sort eligible tasks by priority (lower is first), then stable ID.
4. Execute at most 3 allowlisted tasks per run.
5. Record a machine-readable result artifact.

## Non-goals
No AI reasoning, autonomous code generation, outbound marketing, payment, deployment, repository write, or unattended LLM invocation. Those need a separate zero-cost feasibility and risk review.

## Human approval
Never automatically convert an external task to internal-only. Customer email, publishing, purchasing and live deployment remain human-gated.
