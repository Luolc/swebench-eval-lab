"""CLI: run one rollout (agent solves an instance) + optionally grade its patch.

    # solve only — writes the patch + trajectory to the run workspace
    python -m swebench_eval_lab.rollout <instance_id>

    # solve, then grade the produced patch through the eval harness
    python -m swebench_eval_lab.rollout <instance_id> --grade

Needs Docker available and CLAUDE_CODE_OAUTH_TOKEN set (inherited by reference
into the container). Prints a JSON summary; with --grade, exit 0 iff resolved.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import os

from swebench_eval_lab.core.datasets.loader import load_dataset
from swebench_eval_lab.core.datasets.swebench_pro import (
    evaluate,
    SweBenchProAdapter,
    SweBenchProInstance,
)

from .constants import DEFAULT_MODEL, OAUTH_TOKEN_ENV, PATCH_NAME
from .prompt import build_solve_prompt
from .runner import DEFAULT_TIMEOUT_S, rollout


def main() -> int:
  parser = argparse.ArgumentParser(
      prog="python -m swebench_eval_lab.rollout",
      description="Run a headless agent to solve one instance in its image.",
  )
  _ = parser.add_argument("instance_id")
  _ = parser.add_argument("--dataset", default="swebench_pro")
  _ = parser.add_argument("--model", default=DEFAULT_MODEL)
  _ = parser.add_argument(
      "--grade",
      action="store_true",
      help="grade the produced patch through the eval harness afterwards.",
  )
  _ = parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_S)
  _ = parser.add_argument(
      "--no-pull",
      action="store_true",
      help="skip docker pull (image already present locally).",
  )
  args = parser.parse_args()

  if not os.environ.get(OAUTH_TOKEN_ENV):
    parser.error(
        f"{OAUTH_TOKEN_ENV} is not set; the agent cannot authenticate."
        " Export it (e.g. from .envrc.local) before running rollout."
    )

  instance = load_dataset(args.dataset).require(args.instance_id)
  if not isinstance(instance, SweBenchProInstance):
    raise TypeError(f"Unexpected record type: {type(instance).__name__}")
  spec = SweBenchProAdapter().eval_spec(instance)
  prompt = build_solve_prompt(
      instance.problem_statement,
      requirements=instance.requirements,
      interface=instance.interface,
  )

  result = rollout(
      spec,
      prompt=prompt,
      model=args.model,
      timeout=args.timeout,
      pull=not args.no_pull,
  )

  summary: dict[str, object] = {
      "instance_id": result.instance_id,
      "is_empty_patch": result.is_empty,
      "agent_complete": result.complete,
      "exit_code": result.exit_code,
      "timed_out": result.timed_out,
      "patch_file": str(result.workspace / PATCH_NAME),
      "trajectory_dir": str(result.workspace),
  }

  resolved = False
  if args.grade:
    if result.is_empty:
      # An empty/no-op patch is a failed attempt — never grade it as a pass
      # (docs/patch-extraction.md §5.4). Skip the container round-trip.
      summary["grade"] = {"resolved": False, "skipped": "empty patch"}
    else:
      eval_result = evaluate(spec, patch=result.patch, timeout=args.timeout)
      summary["grade"] = asdict(eval_result)
      resolved = eval_result.resolved

  print(json.dumps(summary, indent=2))
  return 0 if (not args.grade or resolved) else 1


if __name__ == "__main__":
  raise SystemExit(main())
