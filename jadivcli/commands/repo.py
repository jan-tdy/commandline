"""Commands for downloading source archives from GitHub."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import List, Optional

from .. import proc
from ..registry import command

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
    owner = args[1] if len(args) > 1 else DEFAULT_OWNER
    if not proc.require_binary("wget"):
        return

    branch = _resolve_default_branch(owner, repo)
    branches = [branch] if branch else list(_FALLBACK_BRANCHES)

    for candidate in branches:
        url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{candidate}.zip"
        print(f"Downloading: {url}")
        if proc.run(["wget", url, "-O", f"{repo}.zip"]) == 0:
            print(f"Saved as {repo}.zip")
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
    if proc.run(["wget", url, "-O", output]) == 0:
        print(f"Saved as {output}")
