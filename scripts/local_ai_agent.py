#!/usr/bin/env python3
"""One offline, read-only AI analysis of aggregate internal experiment data."""
import argparse
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_SHA256 = "74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db"
MODEL_NAME = "qwen2.5-0.5b-instruct-q4_k_m.gguf"


def aggregate():
    log = ROOT / "data/experiment_log.csv"
    if log.is_symlink():
        raise ValueError("experiment log symlink is prohibited")
    with log.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return {"entries": len(rows), "completed_research": sum(r["status"] == "completed_research_only" for r in rows)}


def verified_model(path):
    if not path.is_file() or path.name != MODEL_NAME:
        raise ValueError("expected local public GGUF model file")
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != MODEL_SHA256:
        raise ValueError("model hash mismatch")


def infer_inner(counts):
    from llama_cpp import Llama

    model = Llama(model_path="/model.gguf", n_ctx=1024, n_threads=2, verbose=False)
    prompt = (f"Internal project counts: {counts['entries']} experiment entries and "
              f"{counts['completed_research']} research preparations. "
              "A: run offline MVP source checks. B: count experiment log entries. "
              "Which useful internal task should run next? Answer A or B only.")
    response = model.create_chat_completion(
        messages=[{"role": "system", "content": "Choose exactly one task ID from A or B. Respond with the single letter only."},
                  {"role": "user", "content": prompt}], max_tokens=5, temperature=0
    )
    print(json.dumps({"choice": response["choices"][0]["message"]["content"].strip()}))


def execute_allowlisted(choice, counts):
    if choice == "A":
        subprocess.run([sys.executable, str(ROOT / "tests/check_mvp.py")],
                       cwd=ROOT, capture_output=True, text=True, check=True, timeout=40)
        return "offline MVP source and JavaScript syntax checks passed"
    if choice == "B":
        return f"counted {counts['entries']} experiment log entries"
    raise ValueError("model chose no allowlisted task")


def run(model_path):
    verified_model(model_path)
    counts = aggregate()
    if sys.prefix == sys.base_prefix:
        raise RuntimeError("run from a dedicated virtual environment with llama-cpp-python")
    base = Path(sys.base_prefix).resolve()
    if not base.is_dir() or not (base.is_relative_to("/opt") or base.is_relative_to("/usr")):
        raise RuntimeError("isolated runtime requires a Python base under /opt or /usr")
    base_dirs = []
    if base.is_relative_to("/opt"):
        for parent in reversed(base.parents):
            if parent != Path("/"):
                base_dirs.extend(["--dir", str(parent)])
        base_dirs.extend(["--ro-bind", str(base), str(base)])
    # Only runtime, model and this script are visible; no network or writable mount.
    cmd = [
        "bwrap", "--unshare-net", "--unshare-pid", "--clearenv", "--die-with-parent",
        "--ro-bind", "/usr", "/usr", *base_dirs,
        "--symlink", "usr/lib", "/lib",
        "--symlink", "usr/lib64", "/lib64", "--dir", "/tmp",
        "--ro-bind", sys.prefix, "/runtime", "--ro-bind", str(model_path), "/model.gguf",
        "--dir", "/app", "--ro-bind", str(Path(__file__).resolve()), "/app/agent.py",
        "--proc", "/proc", "--dev", "/dev", "/runtime/bin/python",
        "/app/agent.py", "--inner", json.dumps(counts),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=True)
    choice = json.loads(result.stdout)["choice"]
    detail = execute_allowlisted(choice, counts)
    report = {"mode": "offline_local_model", "model_sha256": MODEL_SHA256,
              "input": counts, "model_choice": choice, "internal_result": detail,
              "executed_internal_tasks": 1, "external_actions": 0,
              "network_calls": 0, "new_spend_krw": 0}
    output = ROOT / "artifacts/local-ai-report.json"
    if output.parent.is_symlink() or output.is_symlink():
        raise ValueError("report symlink is prohibited")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path)
    parser.add_argument("--inner", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.inner is not None:
        infer_inner(json.loads(args.inner))
    elif args.model is None:
        parser.error("--model is required")
    else:
        run(args.model.resolve())
