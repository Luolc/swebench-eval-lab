"""The sandboxed-task engine: one manager, five hooks, pluggable backends.

The harness-/dataset-/eval-method-agnostic core of the SandboxRun design
(``docs/horizontal/spec.md``): a ``SandboxManager`` owns a container's
lifecycle and drives composed ``SandboxObserver``s around one main action;
*solving* (rollout) and *grading* (eval) are two compositions of this one
engine. Test doubles live in :mod:`swe_lab.sandbox.testing`.
"""

from .backend import ExecResult, SandboxBackend, WORKSPACE_ENV
from .backends import DockerHostBackend
from .errors import SandboxError
from .manager import Sandbox, SandboxManager
from .mounts import Assets, merge_mounts, Mount, Mounts
from .observer import CompositeObserver, SandboxObserver
from .resources import Inline, LocalFile, Resource
from .result import Contribution, RunResult, RunStatus
from .spec import SandboxSpec

__all__ = [
    "Assets",
    "CompositeObserver",
    "Contribution",
    "DockerHostBackend",
    "ExecResult",
    "Inline",
    "LocalFile",
    "Mount",
    "Mounts",
    "Resource",
    "RunResult",
    "RunStatus",
    "Sandbox",
    "SandboxBackend",
    "SandboxError",
    "SandboxManager",
    "SandboxObserver",
    "SandboxSpec",
    "WORKSPACE_ENV",
    "merge_mounts",
]
