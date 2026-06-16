"""Subprocess helpers.

Thin wrappers around :mod:`subprocess` that give the rest of the tool consistent,
friendly behaviour: a clear message when a required external program is missing,
and a reported exit code when a command fails — instead of bare tracebacks.
"""

from __future__ import annotations

import shutil
import subprocess
from typing import List, Sequence


def has_binary(name: str) -> bool:
    """Return ``True`` if ``name`` is available on ``PATH``."""
    return shutil.which(name) is not None


def require_binary(name: str, *, install_hint: str | None = None) -> bool:
    """Check that ``name`` exists, printing an install hint otherwise.

    Returns ``True`` when the binary is present and ``False`` (after printing a
    message) when it is missing.
    """
    if has_binary(name):
        return True
    hint = install_hint or f"sudo apt install {name}"
    print(f"'{name}' is not installed. Try: {hint}")
    return False


def run(args: Sequence[str], *, label: str | None = None) -> int:
    """Run ``args`` as a subprocess and return its exit code.

    The first element must be an available executable; callers that depend on an
    optional program should gate on :func:`require_binary` first. A non-zero exit
    code is reported to the user.
    """
    argv: List[str] = list(args)
    try:
        completed = subprocess.run(argv)
    except FileNotFoundError:
        print(f"Command not found: {argv[0]}")
        return 127
    except OSError as exc:
        print(f"Failed to run command: {exc}")
        return 1
    if completed.returncode != 0:
        name = label or argv[0]
        print(f"'{name}' exited with code {completed.returncode}.")
    return completed.returncode
