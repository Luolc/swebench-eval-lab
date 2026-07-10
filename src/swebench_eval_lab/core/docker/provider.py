"""General Docker execution: pull an image, run a script inside a container.

Dataset-agnostic — this module only knows the ``docker`` CLI. The eval/rollout
flows use it to run the prebuilt per-instance images; *which* image and *what*
to run come from an ``EvalSpec`` / the dataset adapter, not from here.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess

# Images are linux/amd64; on Apple Silicon this runs under emulation.
DEFAULT_PLATFORM = "linux/amd64"
DEFAULT_TIMEOUT_S = 1800.0
_PULL_TIMEOUT_S = 3600.0


class DockerError(RuntimeError):
  """A ``docker`` CLI invocation failed to start or errored fatally."""


@dataclass(frozen=True)
class ContainerRun:
  """Result of one ``docker run`` (the container's own stdout/stderr)."""

  returncode: int
  stdout: str
  stderr: str
  timed_out: bool = False

  @property
  def ok(self) -> bool:
    return self.returncode == 0 and not self.timed_out


@dataclass(frozen=True)
class DockerProvider:
  """Thin wrapper over the ``docker`` CLI: pull, run a script in a container."""

  platform: str = DEFAULT_PLATFORM

  def pull(self, image_ref: str, *, timeout: float = _PULL_TIMEOUT_S) -> None:
    run = self._docker(
        ["pull", "--platform", self.platform, image_ref], timeout=timeout
    )
    if not run.ok:
      raise DockerError(
          f"docker pull {image_ref} failed:\n{run.stderr[-2000:]}"
      )

  def run_script(
      self,
      image_ref: str,
      workspace: Path,
      script_name: str,
      *,
      mount_at: str = "/workspace",
      timeout: float = DEFAULT_TIMEOUT_S,
      network: bool = True,
  ) -> ContainerRun:
    """Bind-mount ``workspace`` at ``mount_at`` and run ``script_name`` in it.

    The image's entrypoint is overridden with bash so the script runs regardless
    of what the image's default entrypoint is.
    """
    args = ["run", "--rm", "--platform", self.platform]
    if not network:
      args += ["--network", "none"]
    args += [
        "-v",
        f"{workspace}:{mount_at}",
        "--entrypoint",
        "/bin/bash",
        image_ref,
        "-c",
        f"bash {mount_at}/{script_name}",
    ]
    return self._docker(args, timeout=timeout)

  def _docker(self, args: list[str], *, timeout: float) -> ContainerRun:
    try:
      result = subprocess.run(
          ["docker", *args],
          capture_output=True,
          text=True,
          timeout=timeout,
          check=False,
      )
    except subprocess.TimeoutExpired as exc:
      out = exc.stdout if isinstance(exc.stdout, str) else ""
      err = exc.stderr if isinstance(exc.stderr, str) else ""
      return ContainerRun(124, out, err, timed_out=True)
    except FileNotFoundError as exc:
      raise DockerError("docker CLI not found on PATH") from exc
    return ContainerRun(result.returncode, result.stdout, result.stderr)
