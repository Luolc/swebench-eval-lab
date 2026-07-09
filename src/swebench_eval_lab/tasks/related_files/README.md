# Task: related-files annotation

For each SWE-bench task instance, produce a **ground-truth** annotation of the
code a model needs to read in order to solve the task — a flat list of *code
snippets* (`file_path` + contiguous line range + `category` + `description`).
This is about *building* ground truth, **not** about scoring an agent's file
selection against the gold patch (the gold `patch` / `test_patch` are inputs the
annotator may consult, not a comparison target).

See [`PLAN.md`](../../../../PLAN.md) for the objective, schema, categories, and
current status.

## Running

Annotate one instance end to end (3 independent samples, then an aggregator
reconciles them into one annotation):

```bash
python -m swebench_eval_lab.tasks.related_files <instance_id> \
    [--model sonnet|opus] [--samples 3] [--dataset swebench_pro]
```

Roll every instance's `aggregate.json` up into the combined parquet deliverable:

```bash
python -m swebench_eval_lab.tasks.related_files.combine [--dataset swebench_pro]
```

Output lands under `outputs/related_files/<dataset>/` — see that folder's
[`README.md`](../../../../outputs/related_files/swebench_pro/README.md) for the
on-disk layout and parquet schema.

## Module map

| Module | Role |
| --- | --- |
| `schema.py` | `SnippetCategory`, `Snippet` / `Annotation`, output parsing + validation. |
| `annotation_prompt.py` | The annotation instruction; `aggregator.py` holds the reconciler prompt. |
| `agent_run.py` | Shared runner: provision workspace, invoke headless Claude Code through a per-call proxy with retries + failure classification, read/validate/store. |
| `annotator.py` / `aggregator.py` | Thin task wrappers over `agent_run` (one sample; reconcile samples). |
| `pipeline.py` | Orchestrates N samples + aggregate. |
| `workspace.py` | Provision the checkout + materialize hint files into `.annotation_context/`. |
| `agent_validator.py` | Stdlib-only validator dropped into the workspace (agent self-checks its output); the runner imports the same code post-hoc. |
| `storage.py` / `combine.py` | On-disk layout of the deliverable; combine aggregates into one parquet. |
| `__main__.py` | CLI entry point. |

Shared infrastructure (dataset loading, repo checkout, the reverse proxy, and
run-error types) lives under `swebench_eval_lab.core`.

## Experiments

Prompt-iteration and batch-QA history lives under
[`experiments/related_files/`](../../../../experiments/related_files/) — the
prompt-variance study (`prompt_variance/REPORT.md`) and the phase-1 batch QA log
(`batch_annotation/qa_log.md`).
