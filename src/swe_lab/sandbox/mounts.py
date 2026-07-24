"""Declarative staging: a resource placed into the workspace at a target path.

Every axis (dataset, harness, eval-method) declares what it needs staged as a
``Mounts`` value; the manager merges the contributions and the backend
materializes the union into the workspace before a run, replacing the imperative
per-flow staging code the engine supersedes. A duplicate target path is an
error, never a silent overwrite.

A ``Mount`` is a :class:`~swe_lab.sandbox.resources.Resource` (where the bytes
come from) plus a workspace target and an ``executable`` flag; an **asset** is
the same resource at a fixed, read-only container path (``Assets``). The
content-source kinds are defined once, in ``resources``, and reused by both.
"""

from __future__ import annotations

from dataclasses import dataclass

from .errors import SandboxError
from .resources import Resource


@dataclass(frozen=True, slots=True)
class Mount:
  """A resource staged into the workspace at its target path.

  Attributes:
    resource: Where the file's content comes from.
    executable: Whether to ``chmod +x`` the materialized file.
  """

  resource: Resource
  executable: bool = False


type Mounts = dict[str, Mount]
"""Workspace-relative target path → the mount to place there."""

type Assets = dict[str, Resource]
"""Fixed container path → a read-only resource (bind-mounted / copied by the
backend at ``up``, outside the read/write workspace)."""


def merge_mounts(*contributions: Mounts) -> Mounts:
  """Merge per-axis mount contributions into one staging set.

  Args:
    *contributions: Mount sets, one per contributor (composition extras,
      then each observer), in registration order.

  Returns:
    The union of all contributions.

  Raises:
    SandboxError: If two contributions claim the same target path.
  """
  merged: Mounts = {}
  for contribution in contributions:
    for target, mount in contribution.items():
      if target in merged:
        raise SandboxError(
            f"duplicate mount target {target!r}: two contributors claim it"
        )
      merged[target] = mount
  return merged
