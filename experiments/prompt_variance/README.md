# Prompt-variance experiment

Goal: check how the annotation prompt behaves across languages and how stable it
is run-to-run, then iterate the prompt to reduce variance. See
[`REPORT.md`](REPORT.md) for findings.

## What it does

- One instance per language (go / python / js / ts), each run **3 times**.
- Judge: (a) is each result reasonable, (b) how big is the run-to-run variance.
  Small differences (a line off, one more/fewer snippet) are acceptable; large
  divergence in the *set of snippets* means the prompt needs to be more stable.

## Instances

Chosen as the first instance of a representative repo per language:

| lang | repo | dataset idx |
| --- | --- | --- |
| go | flipt-io/flipt | 27 |
| python | qutebrowser/qutebrowser | 1 |
| js | NodeBB/NodeBB | 0 |
| ts | element-hq/element-web | 14 |

## Run

```bash
# Run (or resume) a round; <round> names the output subdir (baseline, v2, ...).
python experiments/prompt_variance/run_experiment.py <round> [model]

# Summarize variance / cost / tokens for a round.
python experiments/prompt_variance/analyze.py <round>
```

Each run's full annotation is saved to `runs/<round>/<lang>__run<k>.json` and a
compact line is appended to `runs/<round>/summary.jsonl`. Completed runs are
skipped on re-invocation, so an interrupted round can be resumed.
