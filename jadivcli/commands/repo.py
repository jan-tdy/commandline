"""Commands for downloading source archives from GitHub."""

from __future__ import annotations

import json
import os
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import List, Optional

from .. import proc
from ..registry import command

def _download_atomically(url: str, output: str) -> bool:
    """Download to a sibling temporary file and replace output only on success."""
    target = Path(output).expanduser()
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=f".{target.name}.",
            suffix=".download",
            dir=str(target.parent),
            delete=False,
        ) as fh:
            temporary = Path(fh.name)
    except OSError as exc:
        print(f"Could not prepare download for '{target}': {exc}")
        return False

    try:
        if proc.run(["wget", url, "-O", str(temporary)]) != 0:
            return False
        os.replace(temporary, target)
        return True
    except OSError as exc:
        print(f"Could not save '{target}': {exc}")
        return False
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass


# Default GitHub owner for the short 'apps' form.
DEFAULT_OWNER = "jan-tdy"

# Branches to try, in order, when the repo's default branch can't be
# resolved via the GitHub API (e.g. no network access).
_FALLBACK_BRANCHES = ("main", "master")


def _resolve_default_branch(owner: str, repo: str) -> Optional[str]:
    """Look up ``owner/repo``'s default branch via the GitHub API.

    Returns ``None`` on any failure (no network, repo not found, rate
    limiting, ...) so the caller can fall back to guessing.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}"
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.load(response)
    except (urllib.error.URLError, ValueError, OSError):
        return None
    branch = data.get("default_branch")
    return branch if isinstance(branch, str) and branch else None


@command("apps", category="Repositories", usage="apps <repo> [owner]",
         help=f"Download a GitHub repo archive (default owner: {DEFAULT_OWNER}).")
def apps(shell, args: List[str]) -> None:
    if not args:
        print("Usage: apps <repo> [owner]")
        return
    repo = args[0]
    if repo in {".", ".."} or "/" in repo or "\\" in repo:
        print("Repository name must be a single name without path separators.")
        return
    owner = args[1] if len(args) > 1 else DEFAULT_OWNER
    if not proc.require_binary("wget"):
        return

    branch = _resolve_default_branch(owner, repo)
    branches = [branch] if branch else list(_FALLBACK_BRANCHES)

    for candidate in branches:
        url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{candidate}.zip"
        print(f"Downloading: {url}")
        output = f"{repo}.zip"
        if _download_atomically(url, output):
            print(f"Saved as {output}")
            return

    print(f"Could not download '{owner}/{repo}' (tried branch(es): {', '.join(branches)}).")


@command("apps_full", category="Repositories", usage="apps_full <url> [output.zip]",
         help="Download an archive from a full URL.")
def apps_full(shell, args: List[str]) -> None:
    if not args:
        print("Usage: apps_full <url> [output.zip]")
        return
    url = args[0]
    output = args[1] if len(args) > 1 else "repo.zip"
    if not proc.require_binary("wget"):
        return
    print(f"Downloading: {url}")
    if _download_atomically(url, output):
        print(f"Saved as {output}")
