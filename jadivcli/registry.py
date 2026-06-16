"""Command registry.

Commands are plain functions decorated with :func:`command`. The decorator
records each command in a global registry together with its metadata (category,
usage line and help text). The shell, the ``help`` command and tab-completion
all read from this single source of truth, so they can never drift apart.

A command handler has the signature ``handler(shell, args) -> None`` where
``shell`` is the running :class:`~jadivcli.cli.Shell` and ``args`` is the list
of whitespace-separated arguments that followed the command name.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List

# A handler receives the active shell and the parsed argument list.
Handler = Callable[["object", List[str]], None]


@dataclass(frozen=True)
class Command:
    """A single registered command and its documentation."""

    name: str
    handler: Handler
    category: str
    usage: str
    help: str


# The global registry, keyed by command name.
REGISTRY: Dict[str, Command] = {}


def command(name: str, *, category: str = "General", usage: str = "", help: str = ""):
    """Register ``name`` as a command.

    Used as a decorator on a ``handler(shell, args)`` function::

        @command("whoami", category="Information", help="Show the current user.")
        def whoami(shell, args):
            ...
    """

    def decorator(handler: Handler) -> Handler:
        if name in REGISTRY:
            raise ValueError(f"Command '{name}' is already registered")
        REGISTRY[name] = Command(
            name=name,
            handler=handler,
            category=category,
            usage=usage or name,
            help=help or (handler.__doc__ or "").strip().splitlines()[0]
            if handler.__doc__
            else help,
        )
        return handler

    return decorator


def get(name: str) -> Command | None:
    """Return the registered command, or ``None`` if it does not exist."""
    return REGISTRY.get(name)


def names() -> List[str]:
    """Return all registered command names, sorted alphabetically."""
    return sorted(REGISTRY)


def by_category() -> Dict[str, List[Command]]:
    """Return commands grouped by category, each group sorted by name."""
    groups: Dict[str, List[Command]] = {}
    for cmd in REGISTRY.values():
        groups.setdefault(cmd.category, []).append(cmd)
    for group in groups.values():
        group.sort(key=lambda c: c.name)
    return dict(sorted(groups.items()))
