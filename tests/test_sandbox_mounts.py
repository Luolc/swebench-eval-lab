"""Tests for sandbox mounts + resources: merging and materialization."""

from pathlib import Path

import pytest

from swe_lab.sandbox import Inline, LocalFile, merge_mounts, Mount, SandboxError
from swe_lab.sandbox.testing import FakeBackend


def test_merge_disjoint_and_duplicate():
  a = {"a.sh": Mount(Inline(b"a"))}
  b = {"b.sh": Mount(Inline(b"b"))}
  merged = merge_mounts(a, b)
  assert set(merged) == {"a.sh", "b.sh"}
  with pytest.raises(SandboxError, match="duplicate mount target 'a.sh'"):
    merge_mounts(a, {"a.sh": Mount(Inline(b"other"))})


def test_materialize_inline_localfile_and_executable(tmp_path: Path):
  src = tmp_path / "big.bin"
  _ = src.write_bytes(b"binary!")
  workspace = tmp_path / "ws"
  workspace.mkdir()
  # The default materialize lives on the backend; FakeBackend inherits it.
  FakeBackend().materialize(
      {
          "run.sh": Mount(Inline(b"#!/bin/bash\n"), executable=True),
          "nested/dir/parser.py": Mount(Inline(b"print()")),
          "agent": Mount(LocalFile(src)),
      },
      workspace,
  )
  assert (workspace / "run.sh").read_bytes() == b"#!/bin/bash\n"
  assert (workspace / "run.sh").stat().st_mode & 0o111  # executable
  assert (workspace / "nested/dir/parser.py").read_bytes() == b"print()"
  assert (workspace / "agent").read_bytes() == b"binary!"
  assert not (workspace / "agent").stat().st_mode & 0o100


def test_materialize_missing_localfile_raises(tmp_path: Path):
  with pytest.raises(SandboxError, match="does not exist"):
    FakeBackend().materialize(
        {"agent": Mount(LocalFile(tmp_path / "absent"))}, tmp_path
    )


def test_resource_local_path():
  assert Inline(b"x").local_path() is None
  p = Path("/tmp/whatever")
  assert LocalFile(p).local_path() == p
