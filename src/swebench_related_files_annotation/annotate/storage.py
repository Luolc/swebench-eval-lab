"""On-disk layout of the annotation deliverable.

Everything for one instance lives in a per-instance directory under a
per-dataset folder, so multiple datasets never collide. For each instance the
whole 3-sample-then-aggregate run is preserved — every candidate's annotation
and final proxy exchange, plus the aggregate's — so the result is auditable:

    annotations/<dataset>/<instance_id>/
        candidate_1.json / candidate_1.last_exchange.json
        candidate_2.json / candidate_2.last_exchange.json
        candidate_3.json / candidate_3.last_exchange.json
        aggregate.json   / aggregate.last_exchange.json   <- the deliverable

``<label>.json`` is the annotation record; ``<label>.last_exchange.json`` is the
extracted final ``cc-reverse-proxy`` record for that run.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..paths import annotations_dir, find_repo_root
from .agent_run import RunResult
from .schema import Annotation

DEFAULT_DATASET = "swebench_pro"
AGGREGATE_LABEL = "aggregate"


def instance_dir(
    instance_id: str,
    *,
    dataset: str = DEFAULT_DATASET,
    repo_root: Path | None = None,
) -> Path:
  """The directory holding one instance's artifacts."""
  root = repo_root or find_repo_root()
  return annotations_dir(root) / dataset / instance_id


def store_run(
    instance_id: str,
    label: str,
    result: RunResult,
    *,
    dataset: str = DEFAULT_DATASET,
    repo_root: Path | None = None,
) -> tuple[Path, Path]:
  """Write one run's annotation + last exchange under the instance dir.

  ``label`` is e.g. ``candidate_1`` or ``aggregate``. Returns the two paths.
  """
  return _write(
      instance_dir(instance_id, dataset=dataset, repo_root=repo_root),
      label,
      result.annotation,
      result.last_record,
  )


def candidate_label(index: int) -> str:
  return f"candidate_{index}"


def _write(
    directory: Path,
    label: str,
    annotation: Annotation,
    last_record: dict[str, object],
) -> tuple[Path, Path]:
  directory.mkdir(parents=True, exist_ok=True)
  annotation_path = directory / f"{label}.json"
  _ = annotation_path.write_text(annotation.to_json())

  last_exchange_path = directory / f"{label}.last_exchange.json"
  _ = last_exchange_path.write_text(
      json.dumps(last_record, indent=2, ensure_ascii=False) + "\n"
  )
  return annotation_path, last_exchange_path
