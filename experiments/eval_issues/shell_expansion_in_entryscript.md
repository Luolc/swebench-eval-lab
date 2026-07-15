# Eval Issue: Shell Expansion of `$` in `selected_test_files_to_run`

**Date:** 2026-07-15  
**Status:** Bug confirmed. Grading impact: 0/731 current instances. Latent risk for future data.  
**Fix:** `shlex.quote(selected)` in `build_entryscript` (see §4).

---

## 1. Background

`evaluation/runner.py:build_entryscript` generates an in-container bash script that
runs the instance's test harness. The relevant line:

```python
selected = ",".join(spec.selected_tests)
return (
    ...
    f"bash /workspace/run_script.sh {selected}"
    ...
)
```

`spec.selected_tests` comes from the dataset field `selected_test_files_to_run`.
For some instances this field contains individual **test function / subtest names**
(e.g. Go subtests), not file paths. When those names contain `$`, bash expands
them as variable references before invoking `run_script.sh`.

---

## 2. Affected Instances (Dataset Survey)

Surveyed all 731 SWE-bench Pro instances across three fields:

| category | count | instances |
|---|---|---|
| `$` in `selected_test_files_to_run` | **1** | `gravitational/teleport-1a77b79` |
| `$` in `fail_to_pass` or `pass_to_pass` (but NOT in `selected`) | 5 | 5 × `qutebrowser` |
| overlap (`$` in `selected` AND in `fail/pass_to_pass`) | **0** | — |

Only the **teleport instance** has the bash expansion bug (its `selected_test_files_to_run`
contains the `$`-bearing names). The 5 qutebrowser instances are a separate concern
addressed in §5.

### Teleport instance detail

```
instance_id:  instance_gravitational__teleport-1a77b7945a...
```

Tests with `$` in `selected_test_files_to_run` (4 subtests):
```
TestMalformedOpMsg/empty_$db_key
TestMalformedOpMsg/invalid_$db_value
TestMalformedOpMsg/missing_$db_key
TestMalformedOpMsg/multiple_$db_keys
```

`fail_to_pass` with `$`: **none**  
`pass_to_pass` with `$`: **none**

---

## 3. Bug Reproduction

### What the entryscript currently generates

The `run_script.sh` invocation line in the generated entryscript (excerpt):
```bash
bash /workspace/run_script.sh FuzzMongoRead/seed#5,...,TestMalformedOpMsg/empty_$db_key,TestMalformedOpMsg/invalid_$db_value,...
```

When bash executes this line, `$db_key`, `$db_value`, `$db_keys` are treated as
variable references. None are set in the container environment, so they expand to
the empty string.

### Experiment — `probe_buggy.sh`

Script sent into the container (see `probe_buggy.sh` / `probe_fixed.sh` in this
directory):

```bash
#!/bin/bash
# Simulates the entryscript line — unquoted, as build_entryscript currently generates
bash /workspace/receiver.sh TestMalformedOpMsg/empty_$db_key,TestMalformedOpMsg/invalid_$db_value,TestMalformedOpMsg/missing_$db_key
```

`receiver.sh` mimics what `run_script.sh` does: reads `$1`, splits on `,`.

Run command:
```
docker run --rm --platform linux/amd64 \
  -v /tmp/eval_issue_probe:/workspace \
  --entrypoint /bin/bash \
  jefzda/sweap-images:ansible.ansible-... \
  -c "bash /workspace/probe_buggy.sh"
```

**stdout (buggy):**
```
received: TestMalformedOpMsg/empty_,TestMalformedOpMsg/invalid_,TestMalformedOpMsg/missing_
token count: 3
  token: TestMalformedOpMsg/empty_
  token: TestMalformedOpMsg/invalid_
  token: TestMalformedOpMsg/missing_
```

`$db_key`, `$db_value`, `$db_keys` are all gone. `run_script.sh` receives truncated
test names that do not match anything in the test suite.

---

## 4. Fix: `shlex.quote`

`shlex.quote` wraps the string in single quotes (the strongest bash quoting: all
characters inside are literal — `$`, `` ` ``, `*`, `[`, etc. are not expanded).

```python
import shlex
selected = shlex.quote(",".join(spec.selected_tests))
```

Generated entryscript line becomes:
```bash
bash /workspace/run_script.sh 'FuzzMongoRead/seed#5,...,TestMalformedOpMsg/empty_$db_key,...'
```

### Experiment — `probe_fixed.sh`

```bash
#!/bin/bash
# Simulates build_entryscript with shlex.quote — single-quoted arg
bash /workspace/receiver.sh 'TestMalformedOpMsg/empty_$db_key,TestMalformedOpMsg/invalid_$db_value,TestMalformedOpMsg/missing_$db_key'
```

Same docker run as above.

**stdout (fixed):**
```
received: TestMalformedOpMsg/empty_$db_key,TestMalformedOpMsg/invalid_$db_value,TestMalformedOpMsg/missing_$db_key
token count: 3
  token: TestMalformedOpMsg/empty_$db_key
  token: TestMalformedOpMsg/invalid_$db_value
  token: TestMalformedOpMsg/missing_$db_key
```

`$db_key` etc. are preserved literally. `run_script.sh` receives the correct test names.

Single-quoting also prevents bash glob-expansion of `[...]` brackets that appear
in pytest parametrize test IDs (see §5).

---

## 5. The Qutebrowser `$HOME` Case — Not a Bug

Five qutebrowser instances have `$HOME` in their `pass_to_pass` test IDs, e.g.:
```
tests/unit/config/test_configtypes.py::TestFile::test_to_py_exists_abs[File-$HOME/foobar-/home/foo/foobar]
```

However, their `selected_test_files_to_run` contains **file paths**, not test IDs:
```
tests/unit/config/test_configtypes.py
tests/unit/config/test_configfiles.py
...
```

No `$` is present in the `selected_test_files_to_run` for any of these instances.
The bash script argument is therefore:
```bash
bash /workspace/run_script.sh tests/unit/config/test_configtypes.py,...
```

pytest receives a file path, collects **all tests** in that file (including
`test_to_py_exists_abs[File-$HOME/foobar-...]`), and reports them with the
literal `$HOME` in the test ID. `parser.py` records the same literal string.
Grading compares correctly. No grading impact.

The `shlex.quote` fix is still correct practice — it protects against any future
instance where `$` appears in `selected_test_files_to_run`, and prevents
unintended glob expansion of `[...]` brackets in parametrize IDs regardless of
whether they match real filesystem paths.

---

## 6. Grading Impact Summary

| instance | bug present? | in `fail/pass_to_pass`? | grading impact |
|---|---|---|---|
| teleport-1a77b79 | **yes** — `$db_key` expands to empty | no | **none** (also covered by parent `TestMalformedOpMsg` in selected list) |
| 5 × qutebrowser | no — `selected` = file paths, no `$` | yes (`$HOME` in `pass_to_pass`) | **none** |

For the 731 current instances: **0 instances** have grading impact.  
The fix is a correctness improvement and latent-risk mitigation for future data.

---

## 7. Files

| file | description |
|---|---|
| `probe_buggy.sh` | Entryscript stand-in reproducing the bug |
| `probe_fixed.sh` | Entryscript stand-in with the fix applied |
| `receiver.sh` | Minimal `run_script.sh` stand-in (prints `$1` and tokens) |
