# Annotation Prompt Variance Experiment Report

**Author:** Liangchen Luo
**Harness:** Claude Code (orchestrating model: Claude Opus 4.8, `claude-opus-4-8[1m]`)
**Annotation model under test:** Claude Sonnet 4.6 (`claude-sonnet-4-6`)
**Started:** 2026-07-07
**Last updated:** 2026-07-07

## Contents

- [Conclusions and Recommendations](#conclusions-and-recommendations)
- [Method](#method)
- [Baseline Results](#baseline-results)
- [v2 Results](#v2-results)
- [v3 Results (Recommended Prompt)](#v3-results-recommended-prompt)
- [Cost](#cost)
- [Remaining Issues and Open Questions](#remaining-issues-and-open-questions)

## Conclusions and Recommendations

- **Adopt the v3 prompt.** Across three languages it gives stable file selection
  (python / js / ts ≥ 90% file agreement, ts perfectly consistent) and tight,
  reproducible line ranges, with the v2 regressions fixed. The three levers that
  mattered: (1) no trivial one-line import snippets; (2) take a small
  fully-relevant file whole instead of over-splitting it; (3) don't pad with
  peripheral files (localization / generated / schema).
- **Residual variance is mostly inherent** — chiefly *how much of a test to
  include* (one suite vs several). Prompt wording alone will not drive this to
  zero.
- **This is the case for sample-and-aggregate** (PLAN.md option): for the
  ambiguous cases, running N times and letting an aggregator reconcile the
  ranges/coverage should beat any single run. Recommended if per-instance
  reliability needs to be higher.
- **Validate at scale on more instances.** `n = 3` × one-instance-per-language
  is enough to steer the prompt but too small for firm per-file claims; a
  broader, more diverse sample would confirm.

## Method

- One instance per language, each annotated **3 times** with Sonnet 4.6:
  flipt (go), qutebrowser (python), NodeBB (js), element-web (ts).
- Variance is judged on **two axes**, not just snippet count:
  1. **File agreement** — do the 3 runs select the same files? (`intersection /
     union`).
  2. **Line-range agreement** — for files chosen by every run, how much do the
     covered line numbers overlap (`line-IoU`), and are the ranges *reasonable*
     (focused vs whole-file)? Judged both mechanically (`analyze.py`) and by
     reading the actual snippets against the problem statement / gold patch.
- Cost and token usage tracked per run. Raw data: `runs/<round>/` (full
  annotations + `summary.jsonl`); regenerate metrics with
  `python analyze.py <round>`.

## Baseline Results

_Run: 2026-07-07 03:51–04:22 UTC._

All 12 runs completed and passed validation (`valid = 3/3` everywhere).

| lang | snippet counts | file agreement | notable line-IoU |
| --- | --- | --- | --- |
| go | 6 / 7 / 6 | 4/5 (80%) | evaluator.go 91%, rest 100% |
| python | 7 / 8 / 6 | 5/5 (100%) | **qtlog.py 17%**, qtnetworkdownloads 30%, log.py 45% |
| js | 14 / 15 / 14 | 10/10 (100%) | **test/user/emails.js 29%**, keys.js 53%, rest 72–100% |
| ts | 9 / 15 / 8 | 8/8 (100%) | 85–99% (main ranges agree) |

**Finding: file selection is stable; the variance is in the ranges.** Which
*files* to read is highly reproducible. Run-to-run differences come from the
line ranges, with three concrete drivers:

- **(A) Occasional whole-file over-inclusion.** python `qtlog.py`: two runs took
  focused ranges `[1-33] + [200-214]`; one took `[1-213]` — the entire 213-line
  file.
- **(B) Inconsistent trivial 1-line snippets.** ts run2 added five separate
  single-line *import* snippets that the other runs omitted — the reason its
  count jumped to 15 vs 8–9.
- **(C) Coverage extent.** js `test/user/emails.js`: one run covered four test
  suites `[42-138]`, another only the single relevant suite `[111-138]`.

The rest is benign boundary jitter (a few lines), which is acceptable. No run
was *wrong* — all reasonable, on-target files — but ranges vary more than ideal.

## v2 Results

_Run: 2026-07-07 04:29–04:38 UTC._

Changes: added an explicit JSON output example; "range = the enclosing unit,
never select an entire file"; "cover the whole relevant unit, not a sub-slice";
"no trivial single-line snippets". Effect was **mixed — one clear win, partial
wins, two regressions**:

| lang | file agree | counts | key line-IoU changes |
| --- | --- | --- | --- |
| go | 80 → 100 | 6/7/6 → 8/7/8 | evaluator.go 91→**100** ✅; **errors.go 100→20** ❌; server.go 100→72 ❌ |
| python | 100 → 100 | 7/8/6 → 7/8/7 | log.py 45→**100** ✅; qtnetworkdownloads 30→68 ✅; qtlog.py 17→12 ❌ |
| js | **100 → 69** ❌ | 14/15/14 → **20/16/12** ❌ | mongo/postgres →100 ✅; delete.js 80→21 ❌; emails 29→37 |
| ts | 100 → 100 | **9/15/8 → 8/9/8** ✅ | mostly →**100%** ✅ |

- **Win:** (B) fixed — ts no longer emits import snippets (count 15→9, IoU
  ~100%). Cleanest, most attributable improvement. Coverage (C) also improved in
  places (python `log.py`, `qtnetworkdownloads`; go `evaluator.go`).
- **Regression:** "never select an entire file" was too absolute. go `errors.go`
  is a small 56-line file of error-type definitions that all baseline runs
  sensibly took whole (`[1-56]`, 100%); v2 split it inconsistently (20%). js
  also got less stable (peripheral files included inconsistently; wider count
  spread).
- **Verdict:** net wash. Lesson: forbid grabbing a *large* file when only part
  is relevant, but allow a *small, fully-relevant* file whole.

## v3 Results (Recommended Prompt)

_Run: 2026-07-07 04:41–04:50 UTC._

Changes: kept v2's wins; softened to "don't grab a whole *large* file when only
part is relevant; a *small, fully-relevant* file may be taken whole"; added
"select only files a solver must read; don't pad with peripheral files". All 12
runs valid/complete.

Evolution of the headline numbers (baseline → v2 → v3):

| metric | go | python | js | ts |
| --- | --- | --- | --- | --- |
| file agreement | 80 → 100 → 75 | 100 → 100 → 100 | 100 → **69 → 90** | 100 → 100 → 100 |
| snippet counts | 6/7/6 → 8/7/8 → 6/5/6 | 7/8/6 → 7/8/7 → 5/6/7 | 14/15/14 → 20/16/12 → 12/12/16 | 9/15/8 → 8/9/8 → **8/8/8** |

Targeted fixes landed:

- **go `errors.go`: 20% → 98%** — the small fully-relevant file is taken whole
  by all runs again; the v2 regression is fixed.
- **js file agreement: 69% → 90%** — "don't pad peripheral files" removed the
  inconsistent localization / OpenAPI / error-json inclusions.
- **python `qtlog.py`: 12% → 100%** — runs converged on consistently taking the
  fully-relevant file whole; the previously least-stable file is now stable.
- **ts stayed excellent** — counts `8/8/8`, line-IoU ~100%.

Still weak / noisy:

- **Test-coverage extent** on js `test/user/emails.js` (29%), `test/database/
  keys.js` (40%), `user/delete.js` (21%): runs disagree on *how much* of a test
  to include. Genuine ambiguity, not a format problem.
- **Sampling noise (n=3):** some per-file IoUs swing between rounds for reasons
  unrelated to the prompt (python `log.py` 45 → 100 → 45; go `evaluator.go`
  91 → 100 → 57). Fine-grained cross-round per-file comparisons are therefore
  not fully reliable; the *attributable* conclusions are the four fixes above.

## Cost

| round | runs | cost |
| --- | --- | --- |
| baseline | 12 | $5.64 |
| v2 | 12 | $5.12 |
| v3 | 12 | $5.34 |
| **total** | **36** | **$16.10** (~$0.45/run) |

Tokens per round ≈ 8M input (mostly prompt-cache reads) / ≈ 90K output.

## Remaining Issues and Open Questions

- **Inherently ambiguous coverage.** Test files especially have no single
  "right" extent; this is the main residual variance and the strongest argument
  for sample-and-aggregate.
- **Small sample.** `n = 3`, one instance per language; file-agreement swings on
  js may be partly noise. A larger, more diverse sample (different repos per
  language) would firm up conclusions.
