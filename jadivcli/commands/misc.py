"""Utility, information and shell-control commands."""

from __future__ import annotations

import datetime
import getpass
import os
import random
import shutil
import socket
from typing import List

from .. import registry
from ..registry import command
from ..safemath import CalcError, evaluate


# -- shell control --------------------------------------------------------
@command("help", category="Shell", usage="help [command]",
         help="List all commands, or show details for one command.")
def help_cmd(shell, args: List[str]) -> None:
    if args:
        cmd = registry.get(args[0])
        if cmd is None:
            print(f"Unknown command: {args[0]}")
            return
        print(f"{cmd.name} — {cmd.help}")
        print(f"  Usage: {cmd.usage}")
        return
    print("Available commands:\n")
    for category, commands in registry.by_category().items():
        print(f"{category}:")
        for cmd in commands:
            print(f"  {cmd.name:<14} {cmd.help}")
        print()
    print("Type 'help <command>' for usage details.")


@command("log", category="Shell", usage="log [count]",
         help="Show recently entered commands.")
def log(shell, args: List[str]) -> None:
    limit = 10
    if args and args[0].isdigit():
        limit = int(args[0])
    entries = shell.history(limit)
    if not entries:
        print("No command history available.")
        return
    print("Command history:")
    for i, entry in enumerate(entries, start=1):
        print(f"  {i}: {entry}")


@command("set", category="Shell", usage="set [key] [value]",
         help="Show, read or store a persistent setting.")
def set_cmd(shell, args: List[str]) -> None:
    if not args:
        if not shell.settings:
            print("No settings stored. Use 'set <key> <value>' to add one.")
            return
        print("Settings:")
        for key, value in sorted(shell.settings.items()):
            print(f"  {key} = {value}")
        return
    key = args[0]
    if len(args) == 1:
        if key in shell.settings:
            print(f"{key} = {shell.settings[key]}")
        else:
            print(f"'{key}' is not set.")
        return
    value = " ".join(args[1:])
    shell.settings[key] = value
    shell.save_settings()
    print(f"{key} = {value}")


@command("clear", category="Shell", usage="clear", help="Clear the screen.")
def clear(shell, args: List[str]) -> None:
    os.system("cls" if os.name == "nt" else "clear")


@command("exit", category="Shell", usage="exit", help="Exit the shell.")
def exit_cmd(shell, args: List[str]) -> None:
    shell.running = False


@command("quit", category="Shell", usage="quit", help="Exit the shell.")
def quit_cmd(shell, args: List[str]) -> None:
    shell.running = False


# -- utilities ------------------------------------------------------------
@command("calc", category="Utilities", usage="calc <expression>",
         help="Evaluate an arithmetic expression safely.")
def calc(shell, args: List[str]) -> None:
    if not args:
        print("Usage: calc <expression>")
        return
    try:
        print(f"Result: {evaluate(' '.join(args))}")
    except CalcError as exc:
        print(f"Invalid expression: {exc}")


@command("say", category="Utilities", usage="say <text>",
         help="Print the given text.")
def say(shell, args: List[str]) -> None:
    if not args:
        print("Usage: say <text>")
        return
    print(" ".join(args))


@command("double", category="Utilities", usage="double <number>",
         help="Double an integer.")
def double(shell, args: List[str]) -> None:
    if not args or not args[0].lstrip("-").isdigit():
        print("Usage: double <number>")
        return
    value = int(args[0])
    print(f"{value} × 2 = {value * 2}")


@command("greet", category="Utilities", usage="greet",
         help="Print a friendly greeting.")
def greet(shell, args: List[str]) -> None:
    print("Hello! Welcome to JadivCommandline.")


@command("random_number", category="Utilities", usage="random_number [max]",
         help="Print a random number (default 1–100).")
def random_number(shell, args: List[str]) -> None:
    upper = 100
    if args and args[0].isdigit() and int(args[0]) > 0:
        upper = int(args[0])
    print(f"Random number: {random.randint(1, upper)}")


@command("today", category="Utilities", usage="today",
         help="Show today's date.")
def today(shell, args: List[str]) -> None:
    print(f"Today is: {datetime.datetime.now().strftime('%A, %d %B %Y')}")


# -- information ----------------------------------------------------------
@command("whoami", category="Information", usage="whoami",
         help="Show the current user.")
def whoami(shell, args: List[str]) -> None:
    print(f"User: {getpass.getuser()}")


@command("hostname", category="Information", usage="hostname",
         help="Show the machine hostname.")
def hostname(shell, args: List[str]) -> None:
    print(f"Hostname: {socket.gethostname()}")


@command("diskfree", category="Information", usage="diskfree",
         help="Show free disk space on the root filesystem.")
def diskfree(shell, args: List[str]) -> None:
    free_mb = shutil.disk_usage("/").free // (1024**2)
    print(f"Free space: {free_mb} MB")
