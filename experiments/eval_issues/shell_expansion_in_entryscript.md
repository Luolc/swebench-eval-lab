# Eval Issue: Shell Expansion of `$` in `selected_test_files_to_run`

**Date:** 2026-07-15  
**Instance under study:** `gravitational/teleport-1a77b7945a` (MongoDB protocol tests)  
**Conclusion:** Bug is real. End-to-end eval resolves identically in both buggy and fixed
versions for this instance. The subtests run anyway because the parent test name
`TestMalformedOpMsg` (no subtest suffix) is co-present in the selected list, causing
Go to select all subtests regardless of the corrupted subtest patterns. For the 731
current instances there is **zero grading impact**; `shlex.quote` is the correct fix
and eliminates the latent risk.

---

## 1. The Bug

`evaluation/runner.py:build_entryscript` interpolates the comma-separated
`selected_test_files_to_run` directly into a bash script without quoting:

```python
selected = ",".join(spec.selected_tests)
return (
    ...
    f"bash /workspace/run_script.sh {selected}"   # ← unquoted
    ...
)
```

For the teleport instance, four of the 49 selected test names contain `$`:

```
TestMalformedOpMsg/empty_$db_key
TestMalformedOpMsg/invalid_$db_value
TestMalformedOpMsg/missing_$db_key
TestMalformedOpMsg/multiple_$db_keys
```

When bash executes the entryscript, `$db_key`, `$db_value`, `$db_keys` are treated as
variable references. None are set in the container environment, so they expand to the
empty string.

---

## 2. Dataset Scope

Surveyed all 731 SWE-bench Pro instances. Exactly **1 instance** has `$` in
`selected_test_files_to_run`: `gravitational/teleport-1a77b7945a`. No instance has
`$` in both `selected_test_files_to_run` and `fail_to_pass`/`pass_to_pass`
simultaneously, so grading impact across the current dataset is **zero**.

---

## 3. End-to-End Experiment: Buggy vs Fixed

### Setup

Instance: `gravitational__teleport-1a77b7945a022ab86858029d30ac7ad0d5239d00-vee9b09...`  
Patch: gold patch (`inst.patch`, stripped of binary hunks)  
Image: `jefzda/sweap-images:gravitational.teleport-gravitational__teleport-1a77b7945a...`

Two workspaces prepared under `.cache/eval_e2e_teleport/{buggy,fixed}/`, each
containing `patch.diff`, `run_script.sh`, `parser.py`, and `entryscript.sh`.

The only difference is the `run_script.sh` invocation line in `entryscript.sh`:

**Buggy** (`build_entryscript` as-is):
```bash
bash /workspace/run_script.sh FuzzMongoRead/seed#5,...,TestMalformedOpMsg/empty_$db_key,...,TestMalformedOpMsg,...
```

**Fixed** (`shlex.quote` applied):
```bash
bash /workspace/run_script.sh 'FuzzMongoRead/seed#5,...,TestMalformedOpMsg/empty_$db_key,...,TestMalformedOpMsg,...'
```

Full entryscripts: `e2e_buggy_entryscript.sh`, `e2e_fixed_entryscript.sh`.

Docker run command (same for both, different `-v` mount):
```
docker run --rm --platform linux/amd64 \
  -v <workspace>:/workspace \
  --entrypoint /bin/bash \
  <image> \
  -c "bash /workspace/entryscript.sh"
```

Full stdout logs: `e2e_buggy_stdout.log`, `e2e_fixed_stdout.log`.  
Full output JSON: `e2e_buggy_output.json`, `e2e_fixed_output.json`.

---

### 3a. What `run_script.sh` Actually Received

The teleport `run_script.sh` splits `$1` on commas into an array and echoes it:

**Buggy — "Running selected tests:" line from stdout:**
```
TestMalformedOpMsg/empty_   TestMalformedOpMsg/invalid_   TestMalformedOpMsg/missing_   TestMalformedOpMsg/multiple_   TestMalformedOpMsg   ...
```

`$db_key`, `$db_value`, `$db_keys` were all expanded to empty string. The four
subtest names were corrupted. The parent `TestMalformedOpMsg` (no suffix) was passed
through intact, because it contains no `$`.

**Fixed — "Running selected tests:" line from stdout:**
```
TestMalformedOpMsg/empty_$db_key   TestMalformedOpMsg/invalid_$db_value   TestMalformedOpMsg/missing_$db_key   TestMalformedOpMsg/multiple_$db_keys   TestMalformedOpMsg   ...
```

All four subtest names preserved literally. Single-quoting prevented bash expansion.

---

### 3b. Go Test Regex and Why the Subtests Still Ran (Buggy)

`run_script.sh` builds the Go `-run` pattern as:
```bash
local pattern=$(IFS='|'; echo "${test_names[*]}")
go test -run "^(${pattern})$" ...
```

In the buggy run the pattern contained both the corrupted subtests and the parent:
```
^(...|TestMalformedOpMsg/empty_|TestMalformedOpMsg/invalid_|...|TestMalformedOpMsg|...)$
```

Go's test runner matches `-run` against test names hierarchically: the pattern is
split at `/` and each segment matched against the corresponding hierarchy level. For
the parent token `TestMalformedOpMsg` (no `/`), Go matches only the top-level name;
with no subtest filter, **all subtests of `TestMalformedOpMsg` run unconditionally**.

The corrupted tokens (`TestMalformedOpMsg/empty_` etc.) also appear in the pattern
but are redundant: Go's regex `^(TestMalformedOpMsg/empty_)$` splits to top=`TestMalformedOpMsg`,
sub=`empty_`; as a regex `empty_` matches `empty_$db_key` (prefix match, no end
anchor at the subtest level in practice), so those tokens would also have selected the
subtests independently. Either way the subtests run.

**This is the "silent success" the hypothesis predicted.**

---

### 3c. Results

| metric | buggy | fixed |
|---|---|---|
| Total tests in output.json | 49 | 49 |
| PASSED | **49** | **49** |
| FAILED | 0 | 0 |
| `fail_to_pass` all PASSED | ✅ | ✅ |
| `TestMalformedOpMsg/empty_$db_key` PASSED | ✅ | ✅ |
| `TestMalformedOpMsg/invalid_$db_value` PASSED | ✅ | ✅ |
| `TestMalformedOpMsg/missing_$db_key` PASSED | ✅ | ✅ |
| `TestMalformedOpMsg/multiple_$db_keys` PASSED | ✅ | ✅ |
| **resolved** | **True** | **True** |

The outputs are **identical** — same 49 tests, same pass/fail breakdown, same stdout
log line count (1333 lines each). See §3d for why.

---

### 3d. Why the Logs Are Identical

The fixed version passes the correct subtest names to `run_script.sh`, but
`TestMalformedOpMsg` (the parent, no subtest suffix) is **also** in the selected list
in both versions. In Go's test runner, a top-level pattern with no `/` suffix causes
**all subtests to run unconditionally** — the specific subtest patterns are redundant.
The set of tests that actually executes is therefore identical in both runs, and the
stdout logs differ only in the "Running selected tests:" echo line (token spelling),
not in which tests ran or their results.

The fix would change the outcome only for a future instance where `$`-bearing subtest
names are in `selected_test_files_to_run` **without** a covering parent name — in that
scenario the bug would cause those subtests to be silently skipped.

---

## 4. Root Cause Summary

The bash expansion of `$db_key` → `""` corrupts the subtest names passed to
`run_script.sh`. However, the parent test `TestMalformedOpMsg` (without a subtest
suffix) is co-present in `selected_test_files_to_run`, which causes Go's test runner
to run all subtests of `TestMalformedOpMsg` unconditionally. The corruption is
invisible to grading because:

1. The subtests still run (via the parent match).
2. The `$`-bearing subtests are not in `fail_to_pass` or `pass_to_pass`.
3. The grading check is `required_tests ⊆ passed`, and `required_tests` contains
   only `TestInvalidPayloadSize/...` — no `$` anywhere.

For a future instance where `$`-bearing test names appear in `fail_to_pass` or
`pass_to_pass` **and** no parent name provides unconditional subtest coverage, the
bug would silently corrupt grading.

---

## 5. Fix

```python
import shlex

selected = shlex.quote(",".join(spec.selected_tests))
return (
    ...
    f"bash /workspace/run_script.sh {selected}"   # single-quoted by shlex.quote
    ...
)
```

`shlex.quote` wraps the string in single quotes, which prevents bash from expanding
`$`, `` ` ``, `*`, `?`, `[`, and `\` inside the argument. This is simpler, more
idiomatic, and more complete than a manual `.replace("$", r"\$")` chain.

The fix produces identical grading results for all current 731 instances and
eliminates the latent risk for future data.

---

## 6. Files in This Directory

| file | description |
|---|---|
| `e2e_buggy_entryscript.sh` | Full entryscript as generated by current `build_entryscript` |
| `e2e_fixed_entryscript.sh` | Full entryscript with `shlex.quote` fix applied |
| `e2e_buggy_stdout.log` | Complete Go test JSON output from the buggy run |
| `e2e_fixed_stdout.log` | Complete Go test JSON output from the fixed run |
| `e2e_buggy_output.json` | Parsed grading output from the buggy run (49 PASSED) |
| `e2e_fixed_output.json` | Parsed grading output from the fixed run (49 PASSED) |
