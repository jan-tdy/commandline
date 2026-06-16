"""The interactive shell.

Implements the read-eval-print loop, persistent command history and
tab-completion, plus a small persistent settings store. Commands themselves
live in :mod:`jadivcli.commands` and register through :mod:`jadivcli.registry`.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List

from . import __version__, registry

try:  # readline gives line editing, history and completion; absent on some platforms.
    import readline
except ImportError:  # pragma: no cover - platform dependent
    readline = None  # type: ignore[assignment]

PROMPT = "jadiv> "

_CONFIG_DIR = Path(os.path.expanduser("~/.config/jadivcli"))
_DATA_DIR = Path(os.path.expanduser("~/.local/share/jadivcli"))
CONFIG_FILE = _CONFIG_DIR / "config.json"
HISTORY_FILE = _DATA_DIR / "history"


class Shell:
    """Holds session state and drives the read-eval-print loop."""

    def __init__(self) -> None:
        self.running = True
        self.settings: Dict[str, str] = self._load_settings()
        self._setup_readline()

    # -- settings ---------------------------------------------------------
    def _load_settings(self) -> Dict[str, str]:
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                return {str(k): str(v) for k, v in data.items()}
        except FileNotFoundError:
            pass
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Could not read settings: {exc}")
        return {}

    def save_settings(self) -> None:
        """Persist the in-memory settings to disk."""
        try:
            _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, "w", encoding="utf-8") as fh:
                json.dump(self.settings, fh, indent=2, sort_keys=True)
        except OSError as exc:
            print(f"Could not save settings: {exc}")

    # -- history / completion --------------------------------------------
    def _setup_readline(self) -> None:
        if readline is None:
            return
        try:
            _DATA_DIR.mkdir(parents=True, exist_ok=True)
            if HISTORY_FILE.exists():
                readline.read_history_file(str(HISTORY_FILE))
        except OSError:
            pass
        readline.set_completer(self._complete)
        readline.parse_and_bind("tab: complete")

    def _complete(self, text: str, state: int) -> str | None:
        matches = [name for name in registry.names() if name.startswith(text)]
        return matches[state] if state < len(matches) else None

    def history(self, limit: int = 10) -> List[str]:
        """Return the most recent commands from the readline history."""
        if readline is None:
            return []
        length = readline.get_current_history_length()
        start = max(1, length - limit + 1)
        return [readline.get_history_item(i) for i in range(start, length + 1)]

    def _save_history(self) -> None:
        if readline is None:
            return
        try:
            readline.write_history_file(str(HISTORY_FILE))
        except OSError:
            pass

    # -- loop -------------------------------------------------------------
    def dispatch(self, line: str) -> None:
        """Parse and execute a single command line."""
        parts = line.split()
        name, args = parts[0], parts[1:]
        cmd = registry.get(name)
        if cmd is None:
            print(f"Unknown command: {name}. Type 'help' to see what is available.")
            return
        try:
            cmd.handler(self, args)
        except KeyboardInterrupt:
            print()  # let Ctrl-C abort the current command without exiting.
        except Exception as exc:  # keep the shell alive on any command failure.
            print(f"Error while running '{name}': {exc}")

    def run(self) -> None:
        """Run the interactive loop until the user exits."""
        print(f"JadivCommandline v{__version__} — type 'help' for commands, 'exit' to quit.")
        while self.running:
            try:
                line = input(PROMPT).strip()
            except KeyboardInterrupt:
                print()  # cancel the current line, keep going.
                continue
            except EOFError:
                print()
                break
            if not line:
                continue
            self.dispatch(line)
        self._save_history()
        print("Goodbye.")


def main() -> int:
    """Console-script and ``python -m jadivcli`` entry point."""
    # Importing the commands package triggers registration of every command.
    from . import commands  # noqa: F401

    Shell().run()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
