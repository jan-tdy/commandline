"""Commands for downloading source archives from GitHub."""

from __future__ import annotations

from typing import List

from .. import proc
from ..registry import command

# Default GitHub owner for the short 'apps' form.
DEFAULT_OWNER = "jan-tdy"


@command("apps", category="Repositories", usage="apps <repo> [owner]",
         help=f"Download a GitHub repo archive (default owner: {DEFAULT_OWNER}).")
def apps(shell, args: List[str]) -> None:
    if not args:
        print("Usage: apps <repo> [owner]")
        return
    repo = args[0]
    owner = args[1] if len(args) > 1 else DEFAULT_OWNER
    url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"
    if not proc.require_binary("wget"):
        return
    print(f"Downloading: {url}")
    if proc.run(["wget", url, "-O", f"{repo}.zip"]) == 0:
        print(f"Saved as {repo}.zip")


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
