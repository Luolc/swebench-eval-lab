# Datasets

This directory holds the datasets used for analysis.

Data files are **not** version-controlled: each dataset's `data/` folder is
gitignored (see the root [`.gitignore`](../.gitignore)). Only the per-dataset
READMEs are tracked, so downloads must be reproduced locally by following the
instructions in each dataset's README below.

## Available datasets

| Dataset | Description | README |
| --- | --- | --- |
| SWE-Bench Pro | Enterprise-level SWE benchmark, public test split (731 examples) | [swebench_pro/README.md](swebench_pro/README.md) |

## Layout

```
datasets/
├── README.md              # this file — index of all datasets
└── <dataset_name>/
    ├── README.md          # description + download instructions
    └── data/              # downloaded data files (gitignored)
```

## Adding a new dataset

1. Create a subfolder under `datasets/` named after the dataset.
2. Add a `README.md` in that subfolder describing the dataset and giving the
   exact download commands. Point the data at a `data/` folder inside the
   subfolder, and link back to this file.
3. Register the dataset in the **Available datasets** table above.
