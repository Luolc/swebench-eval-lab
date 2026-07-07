"""LLM sample-and-aggregate experiment.

For each instance in a completed round, feed the 3 independent run annotations
(snippets + descriptions) plus the task context and the real checkout to an
aggregator agent, and let it synthesize one reconciled "best" annotation. This
is the real version of the sample-and-aggregate idea (vs the mechanical
majority in `aggregate.py`).

Reuses the annotation machinery (workspace, proxy, validator). Runs on a
separate proxy port range (25000+) so it never collides with an annotation
round at 20000+. Resumable and parallel across languages.

    python experiments/prompt_variance/aggregate_llm.py <round> [model]

`<round>` is an existing round whose `runs/<round>/<lang>__run{{1,2,3}}.json`
exist (e.g. `s1-v3`). Output goes to `runs/<round>-agg-llm/`.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any

from swebench_related_files_annotation import load_dataset
from swebench_related_files_annotation.annotate.agent_validator import (
    validate_output,
)
from swebench_related_files_annotation.annotate.proxy import (
    build_proxy,
    port_for_index,
    ReverseProxy,
)
from swebench_related_files_annotation.annotate.workspace import (
    ANNOTATION_OUTPUT,
    CONTEXT_DIR,
    prepare_workspace,
    VALIDATOR_SCRIPT,
)
from swebench_related_files_annotation.datasets.swebench_pro import (
    SweBenchProInstance,
)
from swebench_related_files_annotation.paths import cache_root
from swebench_related_files_annotation.repo.provider import GitCheckoutProvider

HERE = Path(__file__).parent
LANGS = ("go", "python", "js", "ts")
AGG_BASE_PORT = 25000
CLAUDE_TIMEOUT_S = 1800.0


def _aggregator_prompt(repo: str, n: int) -> str:
  return f"""\
You are aggregating {n} independent candidate annotations for the same SWE-bench
task into a single, best annotation. Each candidate is one attempt at listing
the code a solver must READ to fix the task.

Your working directory is a read-only checkout of `{repo}` at the base commit
(no environment configured — do not build, run, or modify anything). Task
context is in `{CONTEXT_DIR}/` (problem_statement, requirements, interface,
gold_patch.diff, test_patch.diff, git_log). The {n} candidate annotations are in
`{CONTEXT_DIR}/candidates.json` — a list, each with a `snippets` array.

Produce the single best set of snippets by reconciling the candidates and
checking them against the ACTUAL repo files:
  - Keep a region if it is genuinely relevant, even if only one candidate found
    it (union the correct). But DROP over-broad ranges (e.g. a whole file when
    only part matters), irrelevant picks, and peripheral files a solver need not
    read.
  - When candidates disagree on a range, choose the tightest contiguous range
    that FULLY covers the relevant unit (function / method / class / block /
    test), from its signature to its closing line.
  - Prefer a few meaningful snippets; no trivial single-line import snippets.
  - Verify every file path and line range against this checkout.

Write the result to `{ANNOTATION_OUTPUT}` — an object with a `snippets` array;
each snippet has `file_path`, `start_line`, `end_line`, `category`
(referenced-function | context-file | useful-unit-test | interface-contract |
similar-pattern), and a one-sentence `description`. Then run

    python3 {VALIDATOR_SCRIPT}

and fix until it prints `OK`. Only finish once it prints `OK`; the output file
is your only deliverable."""


def _candidates(
    round_label: str, lang: str
) -> tuple[str, list[dict[str, Any]]]:
  runs_dir = HERE / "runs" / round_label
  files = sorted(runs_dir.glob(f"{lang}__run*.json"))
  instance_id = ""
  candidates: list[dict[str, Any]] = []
  for f in files:
    data = json.loads(f.read_text())
    instance_id = data.get("instance_id", instance_id)
    candidates.append({"snippets": data.get("snippets", [])})
  return instance_id, candidates


def _run_claude(
    prompt: str, cwd: Path, base_url: str, model: str
) -> dict[str, Any]:
  env = os.environ.copy()
  env["ANTHROPIC_BASE_URL"] = base_url
  result = subprocess.run(
      [
          "claude",
          "-p",
          prompt,
          "--model",
          model,
          "--output-format",
          "json",
          "--dangerously-skip-permissions",
      ],
      cwd=str(cwd),
      env=env,
      capture_output=True,
      text=True,
      check=False,
      timeout=CLAUDE_TIMEOUT_S,
  )
  if result.returncode != 0:
    raise RuntimeError(
        f"claude exited {result.returncode}: {result.stderr[:300]}"
    )
  parsed = json.loads(result.stdout)
  return parsed if isinstance(parsed, dict) else {}


def _aggregate_one(
    round_label: str, lang: str, model: str, out_dir: Path, summary_path: Path
) -> None:
  out_file = out_dir / f"{lang}.json"
  if out_file.exists():
    print(f"skip  {lang} (already done)", flush=True)
    return

  start = time.time()
  try:
    instance_id, candidates = _candidates(round_label, lang)
    ds = load_dataset()
    instance = ds.require(instance_id)
    if not isinstance(instance, SweBenchProInstance):
      raise TypeError(f"unexpected record type for {instance_id}")
    index = ds.index_of(instance_id)

    provider = GitCheckoutProvider()
    workspace = prepare_workspace(instance, provider)
    _ = (workspace.context_dir / "candidates.json").write_text(
        json.dumps({"candidates": candidates}, indent=2)
    )

    port = port_for_index(index, base_port=AGG_BASE_PORT)
    # Proxy logs are large and regenerable — keep them out of the committed runs
    # folder, in the gitignored cache (like the main runner).
    proxy_log = cache_root() / "proxy-logs" / f"agg-{round_label}-{lang}.jsonl"
    with ReverseProxy(port, proxy_log, build_proxy()) as proxy:
      cli = _run_claude(
          _aggregator_prompt(instance.repo, len(candidates)),
          workspace.checkout,
          proxy.base_url,
          model,
      )
    duration = round(time.time() - start, 1)

    snippets = json.loads(workspace.output_path.read_text()).get("snippets", [])
    problems = validate_output(workspace.output_path, workspace.checkout)
    _ = out_file.write_text(json.dumps({"snippets": snippets}, indent=2))
    summary: dict[str, Any] = {
        "lang": lang,
        "instance_id": instance_id,
        "agg_snippet_count": len(snippets),
        "candidate_counts": [len(c["snippets"]) for c in candidates],
        "valid": not problems,
        "cost_usd": cli.get("total_cost_usd"),
        "duration_s": duration,
    }
  except Exception as exc:  # record and continue
    summary = {
        "lang": lang,
        "error": f"{type(exc).__name__}: {exc}",
        "duration_s": round(time.time() - start, 1),
    }
    print(f"ERROR {lang}: {exc}", flush=True)

  with summary_path.open("a") as handle:
    _ = handle.write(json.dumps(summary) + "\n")
  if "error" not in summary:
    print(
        f"done  {lang}: agg={summary.get('agg_snippet_count')} "
        f"candidates={summary.get('candidate_counts')} "
        f"valid={summary.get('valid')} cost=${summary.get('cost_usd')} "
        f"{summary.get('duration_s')}s",
        flush=True,
    )


def main(round_label: str, model: str = "sonnet") -> None:
  out_dir = HERE / "runs" / f"{round_label}-agg-llm"
  out_dir.mkdir(parents=True, exist_ok=True)
  summary_path = out_dir / "summary.jsonl"
  _ = build_proxy()

  with ThreadPoolExecutor(max_workers=len(LANGS)) as pool:
    futures = [
        pool.submit(
            _aggregate_one, round_label, lang, model, out_dir, summary_path
        )
        for lang in LANGS
    ]
    for future in futures:
      future.result()


if __name__ == "__main__":
  import sys

  label = sys.argv[1] if len(sys.argv) > 1 else "v3"
  chosen_model = sys.argv[2] if len(sys.argv) > 2 else "sonnet"
  main(label, chosen_model)
