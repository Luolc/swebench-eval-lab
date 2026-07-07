# SWE-bench Pro

SWE-bench Pro is a challenging, enterprise-level dataset for testing agent
ability on long-horizon software engineering tasks. This is the **public test
split** (731 examples).

- Source: https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro
- Evaluation harness: https://github.com/scaleapi/SWE-bench_Pro-os
- Back to the datasets index: [../README.md](../README.md)

## Download

Data files are gitignored, so download the parquet locally into `data/`:

```bash
mkdir -p datasets/swebench_pro/data
curl -L -o datasets/swebench_pro/data/test-00000-of-00001.parquet \
  "https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro/resolve/main/data/test-00000-of-00001.parquet?download=true"
```

## Details

- File: `data/test-00000-of-00001.parquet` (~7.8 MB)
- Rows: 731 (the `test` split)
- Columns (16): `repo`, `instance_id`, `base_commit`, `patch`, `test_patch`,
  `problem_statement`, `requirements`, `interface`, `repo_language`,
  `fail_to_pass`, `pass_to_pass`, `issue_specificity`, `issue_categories`,
  `before_repo_set_cmd`, `selected_test_files_to_run`, `dockerhub_tag`
- Languages: Python, JavaScript, TypeScript, Go
