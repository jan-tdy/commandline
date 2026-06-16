"""Commands for running scripts and editing files."""

from __future__ import annotations

import os
from typing import List

from .. import proc
from ..registry import command


@command("run_py", category="Files", usage="run_py <file.py>",
         help="Run a Python script with python3.")
def run_py(shell, args: List[str]) -> None:
    if not args:
        print("Usage: run_py <file.py>")
        return
    proc.run(["python3", args[0]])


@command("run_sh", category="Files", usage="run_sh <script.sh>",
         help="Run a shell script with bash.")
def run_sh(shell, args: List[str]) -> None:
    if not args:
        print("Usage: run_sh <script.sh>")
        return
    proc.run(["bash", args[0]])


@command("cmd", category="Files", usage="cmd <program> [args...]",
         help="Run an arbitrary external command.")
def cmd(shell, args: List[str]) -> None:
    if not args:
        print("Usage: cmd <program> [args...]")
        return
    proc.run(args)


@command("edit", category="Files", usage="edit <file>",
         help="Open a file in your editor ($EDITOR, then nano, then vi).")
def edit(shell, args: List[str]) -> None:
    if not args:
        print("Usage: edit <file>")
        return
    editor = os.environ.get("EDITOR")
    candidates = [editor] if editor else []
    candidates += ["nano", "vi"]
    for candidate in candidates:
        if candidate and proc.has_binary(candidate):
            proc.run([candidate, args[0]])
            return
    print("No editor found. Set $EDITOR or install nano/vi.")
