# swebench-related-files-annotation

Annotation tooling for SWE-bench related files.

## Setup

### Prerequisites

- [uv](https://docs.astral.sh/uv/) for environment and dependency management
- [direnv](https://direnv.net/) for auto-activating the environment
- Python 3.13 (uv will install it automatically if missing)

### 1. Clone with submodules

```bash
git clone --recurse-submodules https://github.com/Luolc/swebench-related-files-annotation.git
cd swebench-related-files-annotation
```

If you already cloned without `--recurse-submodules`, initialize the
submodules afterwards:

```bash
git submodule update --init --recursive
```

This checks out `cc-reverse-proxy` under `submodules/`.

### 2. Set up the environment

```bash
uv sync          # create .venv and install all (incl. dev) dependencies
direnv allow     # auto-activate the venv on cd (uses .envrc)
```

If you don't use direnv, activate manually with `source .venv/bin/activate`.

Install the pre-commit hooks (ruff, pyink, isort, basedpyright, uv-lock):

```bash
uv run pre-commit install
```

### 3. Download the datasets

The `datasets/` directory is gitignored, so datasets must be downloaded
locally. Download the SWE-bench Pro public test split (731 examples) from
[Hugging Face](https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro):

```bash
mkdir -p datasets/swebench_pro
curl -L -o datasets/swebench_pro/test-00000-of-00001.parquet \
  "https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro/resolve/main/data/test-00000-of-00001.parquet?download=true"
```

The file is ~7.8 MB (16 columns, 731 rows).
