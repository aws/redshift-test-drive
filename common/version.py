"""Tool version (short git SHA) and invocation channel for the application_name marker"""

import functools
import logging
import multiprocessing
import os
import re
import subprocess
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent  # repo root, independent of the current directory
_CHANNEL_ENV = "REDSHIFT_TEST_DRIVE_CLIENT"
_TOKEN = r"[A-Za-z0-9._-]{1,32}"
_CHANNEL_RE = re.compile(rf"^{_TOKEN}(/{_TOKEN})?$")

logger = logging.getLogger("WorkloadReplicatorLogger")


@functools.cache  # one git call per process; replay opens thousands of connections
def get_version():
    """First 7 characters of HEAD, or 'nogit' when git or .git is unavailable"""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=_ROOT,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (OSError, subprocess.SubprocessError):
        return "nogit"
    sha = out.stdout.strip()
    return sha[:7] if out.returncode == 0 and sha else "nogit"


@functools.cache  # read the environment once per process
def get_channel():
    """Channel from REDSHIFT_TEST_DRIVE_CLIENT; unset or invalid falls back to 'cli'"""
    raw = os.environ.get(_CHANNEL_ENV, "").strip()
    if not raw:
        return "cli"
    if _CHANNEL_RE.match(raw):
        return raw
    # workers re-evaluate under spawn; warn once, from the main process
    if multiprocessing.parent_process() is None:
        logger.warning(f"Ignoring invalid {_CHANNEL_ENV}={raw!r}; using channel 'cli'")
    return "cli"


def application_name(component):
    """Connect-time marker, e.g. RedshiftTestDrive-Replay/c288d94/cli"""
    return f"RedshiftTestDrive-{component}/{get_version()}/{get_channel()}"
