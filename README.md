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

Dataset data files are gitignored and must be downloaded locally. See
[`datasets/README.md`](datasets/README.md) for the list of available datasets
and per-dataset download instructions.
