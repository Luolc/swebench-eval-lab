"""Single-instance annotation agent runner."""

from __future__ import annotations

from .agent_run import run_agent, RunResult
from .aggregator import aggregate_by_id, aggregate_instance
from .errors import (
    AnnotationError,
    MissingOutputError,
    RetryableError,
    UsageLimitError,
)
from .runner import annotate_by_id, annotate_instance
from .schema import Annotation, Snippet, SnippetCategory

__all__ = [
    "Annotation",
    "AnnotationError",
    "MissingOutputError",
    "RetryableError",
    "RunResult",
    "Snippet",
    "SnippetCategory",
    "UsageLimitError",
    "aggregate_by_id",
    "aggregate_instance",
    "annotate_by_id",
    "annotate_instance",
    "run_agent",
]
