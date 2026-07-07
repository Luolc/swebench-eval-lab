"""Summarize a round's run-to-run variance from its summary.jsonl.

    python experiments/prompt_variance/analyze.py <round>

Reports, per language: how many runs were valid, the snippet counts, how much
the set of touched files agrees across runs (intersection / union), and the
cost / token totals. File-set agreement is the main variance signal — low
agreement means the prompt is unstable.
"""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
import sys
from typing import Any

HERE = Path(__file__).parent


def _load(round_label: str) -> list[dict[str, Any]]:
  path = HERE / "runs" / round_label / "summary.jsonl"
  if not path.is_file():
    raise SystemExit(f"No summary at {path}")
  return [json.loads(line) for line in path.read_text().splitlines() if line]


def _file_set(run: dict[str, Any]) -> set[str]:
  snippets = run.get("snippets")
  if not isinstance(snippets, list):
    return set()
  return {
      str(s["file_path"])
      for s in snippets
      if isinstance(s, dict) and "file_path" in s
  }


def _agreement(file_sets: list[set[str]]) -> tuple[int, int]:
  if not file_sets:
    return (0, 0)
  inter = set.intersection(*file_sets)
  union = set.union(*file_sets)
  return (len(inter), len(union))


def main(round_label: str) -> None:
  rows = _load(round_label)
  by_lang: dict[str, list[dict[str, Any]]] = defaultdict(list)
  for row in rows:
    by_lang[str(row.get("lang"))].append(row)

  total_cost = 0.0
  total_in = 0
  total_out = 0
  print(f"Round: {round_label}\n")
  for lang in sorted(by_lang):
    runs = sorted(by_lang[lang], key=lambda r: int(r.get("run", 0) or 0))
    ok = [r for r in runs if not r.get("error")]
    counts = [r.get("snippet_count") for r in ok]
    valid = sum(1 for r in ok if r.get("valid"))
    file_sets = [_file_set(r) for r in ok]
    inter, union = _agreement(file_sets)
    pct = f"{100 * inter // union}%" if union else "n/a"
    costs = [float(r.get("cost_usd") or 0) for r in ok]
    lang_cost = sum(costs)
    total_cost += lang_cost
    for r in ok:
      usage = r.get("usage") or {}
      total_in += int(usage.get("input_tokens", 0) or 0)
      total_out += int(usage.get("output_tokens", 0) or 0)

    print(f"{lang:8} runs={len(runs)} valid={valid}/{len(ok)}")
    print(f"         snippet_count={counts}")
    print(f"         file agreement (in-all/union)={inter}/{union} ({pct})")
    print(f"         cost=${lang_cost:.2f}")
    for r in runs:
      if r.get("error"):
        print(f"         run{r.get('run')}: ERROR {r.get('error')}")
      else:
        files = sorted(_file_set(r))
        print(f"         run{r.get('run')} files: {files}")
    print()

  print(
      f"TOTALS: cost=${total_cost:.2f} "
      f"input_tokens={total_in} output_tokens={total_out}"
  )


if __name__ == "__main__":
  label = sys.argv[1] if len(sys.argv) > 1 else "baseline"
  main(label)
