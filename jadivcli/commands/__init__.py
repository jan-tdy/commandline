"""Importing this package registers every built-in command.

Each submodule decorates its functions with :func:`jadivcli.registry.command`,
so simply importing them is enough to populate the registry.
"""

from . import files, merge, misc, repo, system, text  # noqa: F401

__all__ = ["files", "merge", "misc", "repo", "system", "text"]
