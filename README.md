# JadivCommandline

A modern, **shell-style command toolkit** for system management and everyday
utilities — a small interactive interpreter you can extend one command at a time.

![version](https://img.shields.io/badge/version-2.0.0-4f8cff?style=for-the-badge)
![python](https://img.shields.io/badge/python-3.8%2B-3776ab?style=for-the-badge)

---

## Features

- **🧩 Clean command registry** — every command is a small function registered
  with a decorator; `help` and tab-completion are generated from it automatically.
- **🛡 Safe by default** — the calculator uses a sandboxed arithmetic evaluator
  (no `eval`), and external commands report missing tools and failures clearly.
- **⌨️ A real shell** — line editing, persistent history and Tab completion of
  command names (via `readline`).
- **🖥 System tools** — APT package management, system status (uptime, CPU
  temperature, free disk), screenshots, reboot/shutdown.
- **📦 Handy utilities** — run Python/shell scripts, download GitHub archives,
  a safe calculator, a toy text cipher, and small information commands.
- **⚙ Persistent settings** — store simple key/value preferences across sessions.

---

## Install

```bash
git clone https://github.com/jan-tdy/commandline.git
cd commandline
pip install -r requirements.txt   # installs psutil (recommended)
```

Or install it as a package to get the `jadiv` command on your PATH:

```bash
pip install .
```

> `psutil` is optional — without it the tool still runs and reads uptime from
> `/proc` on Linux.

---

## Usage

Start the interactive shell in any of these equivalent ways:

```bash
python3 commandline.py      # run directly from the repo
python3 -m jadivcli         # run as a module
jadiv                       # after 'pip install .'
```

```text
JadivCommandline v2.0.0 — type 'help' for commands, 'exit' to quit.
jadiv> calc 2 + 2 * 3
Result: 14
jadiv> help calc
calc — Evaluate an arithmetic expression safely.
  Usage: calc <expression>
```

Type `help` for the full, categorised command list, `help <command>` for the
usage of one command, and `exit` (or `Ctrl-D`) to quit.

---

## Command reference

| Category | Commands |
|----------|----------|
| **Shell** | `help`, `log`, `set`, `clear`, `exit`, `quit` |
| **System** | `apt_update`, `apt_upgrade`, `apt_install`, `status`, `uptime`, `osinfo`, `screenshot`, `reboot`, `shutdown` |
| **Files** | `run_py`, `run_sh`, `cmd`, `edit` |
| **Repositories** | `apps`, `apps_full` |
| **Utilities** | `calc`, `say`, `double`, `greet`, `random_number`, `today` |
| **Information** | `whoami`, `hostname`, `diskfree` |
| **Text** | `cipher` *(toy obfuscation — not secure)* |

---

## State on disk

| Path | Purpose |
|------|---------|
| `~/.config/jadivcli/config.json` | persistent settings written by `set` |
| `~/.local/share/jadivcli/history` | command history (read/written by `readline`) |

---

## Adding a command

The codebase is built to grow. A new command is just a decorated function:

```python
# jadivcli/commands/misc.py
from ..registry import command

@command("ping", category="Utilities", usage="ping", help="Reply with pong.")
def ping(shell, args):
    print("pong")
```

Importing its module (already done in `jadivcli/commands/__init__.py`) registers
it, and it immediately appears in `help` and tab-completion.

---

## Install via Code Master

This repository ships a `codemaster-metadata.json`, so JadivCommandline shows up
in [**Jadiv Code Master**](https://github.com/jan-tdy/codemaster) — install and
launch it from there with one click.

---

Made by JapySoft TDY · contact: j44soft@gmail.com
