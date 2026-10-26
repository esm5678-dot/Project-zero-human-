# Local model feasibility check — 2026-10-26

## Observed routes

| Route | Observed evidence | Decision |
| --- | --- | --- |
| Hosted paid or free API | No provider credential, account quota, hard overage block, or billing status was available in this project's runtime. | Do not call. `config/model_policy.json` remains disabled. |
| ChatGPT/Codex subscription | `codex login status` said “Logged in using ChatGPT”; it did not show this account's included inference quota or a hard zero-spend control. | Do not automate Codex CLI calls. |
| GitHub Actions | Repository workflow has read-only permissions; it runs deterministic checks, not inference. GitHub account plan response did not establish a model entitlement or billing cap. | Do not add inference to Actions. |
| Local open model | Public Hugging Face metadata for `Qwen/Qwen2.5-0.5B-Instruct-GGUF` reported `private=false`, `gated=false`, `license=apache-2.0`. The Q4_K_M file downloaded without an account, size about 469 MiB, SHA-256 `74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db`. | Local CPU inference only; no provider API or metered inference. |

The isolated test workspace reported no GPU, existing model weights, or installed inference runtime. The local model and runtime used for verification stay outside Git. The public model download is distinct from an API free tier: it grants no cloud inference allowance. CPU work and the existing environment have economic value but this run made no new cash purchase.

Actual local run: the model selected `A`; the runner executed the offline MVP source and JavaScript syntax check successfully. The report recorded one internal task, zero external actions, zero network calls, and zero new cash spending. The existing Python safety suite passed 9 tests, and the existing Chromium suite passed 8 tests. These figures describe this run, not a guarantee about every host or future run.

## Safety boundary

`scripts/local_ai_agent.py` checks the exact model hash, sends only aggregate counts from `data/experiment_log.csv`, and invokes the model inside a bubblewrap process with no network namespace, no writable filesystem mount, and no CELLEN mount. The model chooses between two fixed internal tasks: an offline MVP check or an experiment entry count. Any other output fails closed. The parent process runs the selected allowlisted task and writes a local, ignored report. It cannot contact customers, deploy, charge, change production systems, or modify repository files. The 0.5B parameter model has limited reasoning ability; its choice is never granted arbitrary execution authority.

Reproduction requires a Linux host with `bwrap`, Python 3.12 and a compiler. Install `llama-cpp-python==0.3.36` in a dedicated virtual environment with `CC=gcc CXX=g++`, download the exact public GGUF file from `https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf` into a location outside the repository, then run `venv/bin/python scripts/local_ai_agent.py --model /absolute/path/qwen2.5-0.5b-instruct-q4_k_m.gguf`. The runner refuses other hashes. No model or environment credential is committed.

Remote or subscription based inference still needs verified account entitlement, enforceable zero overage, and explicit provider approval before anyone changes the disabled model policy.
