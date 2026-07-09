"""Majority-consensus aggregation over a round's 3 runs per instance.

A cheap, deterministic proxy for the sample-and-aggregate idea: instead of an
LLM aggregator, keep what the runs agree on. For each language:

- keep a file if it appears in >= 2 of the 3 runs (drops single-run outliers);
- for each kept file, keep a line if >= 2 runs covered it, then re-form
  contiguous ranges from those lines (drops over-broad ranges only one run took,
  and fills coverage two runs agreed on).

The point is to measure whether this consensus is more reasonable / stable than
a single run — i.e. whether a real (LLM) aggregator is worth building.

    python experiments/related_files/prompt_variance/aggregate.py <round>
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any

HERE = Path(__file__).parent
LANGS = ("go", "python", "js", "ts")


def _runs(round_label: str, lang: str) -> list[list[dict[str, Any]]]:
  out: list[list[dict[str, Any]]] = []
  for path in sorted((HERE / "runs" / round_label).glob(f"{lang}__run*.json")):
    out.append(json.loads(path.read_text()).get("snippets", []))
  return out


def _intervals(
    snippets: list[dict[str, Any]],
) -> dict[str, list[tuple[int, int]]]:
  by_file: dict[str, list[tuple[int, int]]] = {}
  for s in snippets:
    by_file.setdefault(str(s["file_path"]), []).append(
        (int(s["start_line"]), int(s["end_line"]))
    )
  return by_file


def _lines(intervals: list[tuple[int, int]]) -> set[int]:
  covered: set[int] = set()
  for a, b in intervals:
    covered |= set(range(a, b + 1))
  return covered


def _to_ranges(lines: set[int]) -> list[tuple[int, int]]:
  if not lines:
    return []
  ranges: list[tuple[int, int]] = []
  ordered = sorted(lines)
  start = prev = ordered[0]
  for line in ordered[1:]:
    if line == prev + 1:
      prev = line
    else:
      ranges.append((start, prev))
      start = prev = line
  ranges.append((start, prev))
  return ranges


_Intervals = dict[str, list[tuple[int, int]]]


def aggregate(
    round_label: str, lang: str
) -> tuple[_Intervals, list[_Intervals]]:
  runs = _runs(round_label, lang)
  maps = [_intervals(r) for r in runs]

  file_votes = Counter(f for m in maps for f in m)
  kept_files = [f for f, c in file_votes.items() if c >= 2]

  result: _Intervals = {}
  for f in sorted(kept_files):
    line_votes: Counter[int] = Counter()
    for m in maps:
      if f in m:
        line_votes.update(_lines(m[f]))
    consensus = {ln for ln, c in line_votes.items() if c >= 2}
    result[f] = _to_ranges(consensus)
  return result, maps


def _fmt(ranges: list[tuple[int, int]]) -> str:
  return ", ".join(f"{a}-{b}" for a, b in ranges)


def main(round_label: str) -> None:
  print(f"Aggregate (majority of 3 runs) — round {round_label}\n")
  for lang in LANGS:
    agg, maps = aggregate(round_label, lang)
    all_files = {f for m in maps for f in m}
    dropped = sorted(all_files - set(agg))
    print(f"{lang}: {len(agg)} consensus files (from {len(all_files)} seen)")
    for f in sorted(agg):
      print(f"    {f}: [{_fmt(agg[f])}]")
    if dropped:
      print(f"    dropped single-run files: {dropped}")
    print()


if __name__ == "__main__":
  main(sys.argv[1] if len(sys.argv) > 1 else "v3")
