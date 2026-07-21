# Task 05 — Eval CLI on the engine + parity

> **Status: PLANNED — pre-implementation.** Source of truth: the approved
> [spec](../spec.md), [task 02](task-02-engine-core.md) (engine),
> [task 03](task-03-a-host-backend.md) (`DockerHostBackend`), and
> [task 04](task-04-unit-test-method.md) (`compile_unit_test` / `run_unit_test`
> / `SweBenchProVerdict`). Grounded in the current eval CLI + golden verify
> (`src/swe_lab/evaluation/{__main__,verify}.py`, `.github/workflows/{eval,
> verify-golden}.yml` at `fae1738`). Open items in §8.

---

## 1. Purpose & scope

Stand up the **single CLI entry point** (`python -m swe_lab <subcommand>`) with
its first subcommand, `eval`, running one instance's grade as an engine
composition (task 04). Prove **verdict parity** with the legacy grader on real
instances — the payload for **CP1**. The old `evaluation/` package stays intact
and untouched until cutover (10b); this task adds the new path beside it.

### In scope

- `swe_lab/__main__.py`: a **table-only** dispatcher (`eval` now; `rollout`,
  `verify` land in later tasks).
- `swe_lab/cli/eval.py`: the `eval` subcommand — mirror the legacy arg surface,
  run through `compile_unit_test` + `run_unit_test` + `DockerHostBackend`.
- `eval.yml` switched to `python -m swe_lab eval …`.
- A **parity harness** (a `workflow_dispatch` job) that runs the legacy grader
  and the engine grader on the same instances and diffs their verdicts.
- Fast, Docker-free unit tests for the dispatcher + CLI wiring.

### Out of scope

- Porting `verify.py`'s **two-run base+golden sweep** (`classify`, sharding,
  aggregate) — that is 10b (`cli/verify.py`). Task 05's parity is the
  **single-grade** path (`evaluate` vs `run_unit_test`).
- `rollout` subcommand (task 07); deleting `evaluation/` (10b).
- Any `output_state`/GOLDEN_FAIL reclassification in the sweep — the verdict
  *carries* the state (task 04); the sweep consumes it at 10b.

## 2. Module layout

```
swe_lab/
  __main__.py    dispatcher table: {"eval": cli.eval.main, ...}
  cli/
    __init__.py
    eval.py      main(argv) -> int
```

Tests: `tests/test_cli_dispatch.py` (dispatcher), `tests/test_cli_eval.py`
(arg surface + wiring, engine mocked).

## 3. Dispatcher & CLI

```python
# ─── swe_lab/__main__.py ────────────────────────────────────────────────────
# Table only — every subcommand is its own module (growth guard). No argparse
# here beyond splitting off the subcommand token.
_COMMANDS: dict[str, Callable[[list[str]], int]] = {
    "eval": eval_main,
    # "rollout": rollout_main,   # task 07
    # "verify":  verify_main,    # 10b
}

def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] not in _COMMANDS:
        # print usage listing _COMMANDS, return 2
    return _COMMANDS[argv[0]](argv[1:])

# ─── swe_lab/cli/eval.py ────────────────────────────────────────────────────
def main(argv: list[str]) -> int: ...
    # argparse(prog="python -m swe_lab eval"):
    #   instance_id (positional)
    #   --dataset      default "swebench_pro"
    #   --gold         grade the instance's own gold patch
    #   --patch-file   path to a candidate .diff
    #   --timeout      float, default 1800.0
    #   --no-network   run the container offline
    #   --no-pull      skip the image pull
    # exactly one of --gold/--patch-file required (parser.error otherwise)
```

The legacy surface (`evaluation/__main__.py:32-45`) is reproduced verbatim plus
`--no-pull` (the engine backend pulls by default; the legacy CLI always pulled
via `evaluate`). Behavior parity: `--gold` → `instance.patch`; `--patch-file` →
file text; print the verdict as JSON; **exit `0` iff resolved**
(`evaluation/__main__.py:64-65`).

## 4. The eval composition

`cli/eval.py` maps the legacy `evaluate(...)` call
(`evaluation/__main__.py:61-63`) onto task 04:

```python
instance = load_dataset(args.dataset).require(args.instance_id)
# type-guard SweBenchProInstance (as evaluation/__main__.py:49-50)
sandbox_spec, unit_spec = compile_unit_test(instance, patch=patch)
backend = DockerHostBackend(network=not args.no_network, pull=not args.no_pull)
workspace = cache_root(root) / "eval_workspaces" / instance.instance_id
_, verdict = run_unit_test(
    sandbox_spec, unit_spec, backend=backend, workspace=workspace,
    timeout=args.timeout,
)
print(json.dumps({... verdict fields ...}, indent=2))
return 0 if verdict and verdict.resolved else 1
```

Mapping table (legacy → engine):

| Legacy | Engine |
|---|---|
| `SweBenchProAdapter().eval_spec(instance)` → `EvalSpec` (`evaluation/__main__.py:51`) | `compile_unit_test(instance, patch=…)` → `(SandboxSpec, UnitTestSpec)` |
| `evaluate(spec, patch=…, timeout=…, network=…)` (`:61-63`) | `run_unit_test(sandbox_spec, unit_spec, backend=DockerHostBackend(network=…), …)` |
| `EvalResult.resolved / .passed / .missing / .output_found` | `SweBenchProVerdict.score / .resolved / .passed / .missing / .output_state` |
| exit `0 if resolved else 1` (`:65`) | same, off `verdict.resolved` (`= score >= 1.0`) |

Note two verdict upgrades, neither of which changes the exit-code contract
(resolved ⇒ 0), so parity holds on healthy instances:
- **`score`** — the cross-dataset surface is now a scalar in [0, 1]
  (`verdict.score`), binary {0.0, 1.0} for unit-test grading; `resolved` is the
  derived `score >= 1.0`. The single-instance CLI prints both and exits off
  `resolved`; sweep aggregation (10b) will average `score`.
- **`output_state`** — legacy `output_found=True` collapses a corrupt
  `output.json` into "0 passed"; the engine verdict distinguishes
  `ok`/`absent`/`unparseable`. Printed for diagnosis.

## 5. Parity harness (the CP1 payload)

Verdict equivalence between the two graders on the same gold patch, in CI (real
Docker, native amd64):

- A `workflow_dispatch` job (extend `eval.yml` or a sibling `eval-parity.yml` —
  §8 Q1) runs, per instance id:
  - legacy: `python -m swe_lab.evaluation <id> --gold` → JSON with `resolved`,
    `passed`, `missing` (`evaluation/__main__.py:64`).
  - engine: `python -m swe_lab eval <id> --gold` → JSON verdict.
  - a small diff step asserts `resolved` (and thus `score`) matches **and** the
    `passed`/`missing` sets match; nonzero exit + a table on mismatch.
- Instance set: **flipt** (Go), **ansible** (Python) — both known to resolve
  (README progress table) — plus **one truncated-golden-names instance**
  (NodeBB / ansible / vuls) exercising the `patches.py` in-loader fix, so the
  parity covers the class that historically mis-graded.
- The verification artifact for the PR is that job's run link + the diff table
  (plan's CP1 verification).

Why not a `@pytest.mark.docker` parity test in the merge gate: flipt+ansible are
minutes each and run *twice* (both graders) — far too slow for `ci.yml`. The
merge gate keeps only the fast mocked wiring tests; the real parity is a manual
CI job the user triggers at CP1.

## 6. Design decisions

### 6.1 Table dispatcher, argparse per subcommand
The dispatcher never grows a monolithic parser (conventions: dispatcher is a
table, each subcommand its own module). Each `cli/<x>.py` owns a self-contained
`argparse` and a `main(argv) -> int`. Adding `rollout`/`verify` is one table
entry + one module.

### 6.2 Reuse task 04's compile+run; no new grading logic here
Everything grading-specific already lives in `compile_unit_test` /
`SweBenchProGrader` (task 04). The CLI is thin wiring. This is what makes the
parity meaningful — the engine path shares no code with the legacy `evaluate`,
so agreement is real cross-validation, not a tautology.

### 6.3 Legacy path stays until 10b
`evaluation/__main__.py` + `verify.py` are untouched, so the golden sweep and
`eval.yml`'s legacy fallback keep working while the engine path is proven. The
strangler holds: two independent graders coexist until CP1 clears the new one.

## 7. Dependencies

Tasks 02, 03, 04. No new runtime deps. New code lands Google-docstring'd; the
`cli/` package + `__main__.py` are new public surface with curated docstrings.

## 8. Open questions (need user confirmation)

1. **Parity workflow placement** — extend `eval.yml` with a parity mode/input,
   or add a dedicated `eval-parity.yml`? I lean dedicated (keeps `eval.yml` a
   simple single-instance runner; parity is a distinct, multi-instance job).
2. **`eval.yml` cutover timing** — switch `eval.yml`'s single-instance run to
   `python -m swe_lab eval` **in this task** (my plan), or leave `eval.yml` on
   the legacy CLI until 10b and only add the parity job now? Switching now
   exercises the new CLI in CI immediately; the legacy CLI is still reachable
   for the parity job.
3. **Dispatcher usage/help** — a hand-rolled table + usage string (my plan), or
   argparse subparsers on the top-level parser? The table keeps `__main__.py`
   trivially small and each subcommand fully independent; subparsers centralize
   `--help` but couple the modules. I recommend the table.
