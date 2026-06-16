"""System management commands: packages, status, power and screenshots."""

from __future__ import annotations

import datetime
import platform
import shutil
from typing import List

from .. import proc
from ..registry import command

try:
    import psutil
except ImportError:  # psutil is optional; we fall back to /proc where possible.
    psutil = None  # type: ignore[assignment]


def _boot_time() -> datetime.datetime | None:
    """Best-effort system boot time, with a /proc fallback when psutil is absent."""
    if psutil is not None:
        return datetime.datetime.fromtimestamp(psutil.boot_time())
    try:
        with open("/proc/uptime", "r", encoding="utf-8") as fh:
            seconds = float(fh.read().split()[0])
        return datetime.datetime.now() - datetime.timedelta(seconds=seconds)
    except (FileNotFoundError, OSError, ValueError, IndexError):
        return None


def _uptime_text() -> str:
    boot = _boot_time()
    if boot is None:
        return "unavailable"
    delta = datetime.datetime.now() - boot
    return str(delta).split(".")[0]  # drop microseconds


def _cpu_temp() -> str:
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r", encoding="utf-8") as fh:
            return f"{round(int(fh.read()) / 1000, 1)}°C"
    except (FileNotFoundError, OSError, ValueError):
        return "N/A"


@command("apt_update", category="System", usage="apt_update",
         help="Refresh the APT package index (sudo).")
def apt_update(shell, args: List[str]) -> None:
    if proc.require_binary("apt"):
        proc.run(["sudo", "apt", "update"])


@command("apt_upgrade", category="System", usage="apt_upgrade",
         help="Upgrade installed APT packages (sudo).")
def apt_upgrade(shell, args: List[str]) -> None:
    if proc.require_binary("apt"):
        proc.run(["sudo", "apt", "upgrade", "-y"])


@command("apt_install", category="System", usage="apt_install <package>",
         help="Install an APT package (sudo).")
def apt_install(shell, args: List[str]) -> None:
    if not args:
        print("Usage: apt_install <package>")
        return
    if proc.require_binary("apt"):
        proc.run(["sudo", "apt", "install", args[0], "-y"])


@command("status", category="System", usage="status",
         help="Show uptime, CPU temperature and free disk space.")
def status(shell, args: List[str]) -> None:
    free_mb = shutil.disk_usage("/").free // (1024**2)
    print("System status:")
    print(f"  Uptime:    {_uptime_text()}")
    print(f"  CPU temp:  {_cpu_temp()}")
    print(f"  Disk free: {free_mb} MB")


@command("uptime", category="System", usage="uptime",
         help="Show how long the system has been running.")
def uptime(shell, args: List[str]) -> None:
    print(f"Uptime: {_uptime_text()}")


@command("osinfo", category="System", usage="osinfo",
         help="Show operating-system platform information.")
def osinfo(shell, args: List[str]) -> None:
    print(f"OS: {platform.platform()}")


@command("screenshot", category="System", usage="screenshot [file]",
         help="Capture the screen to a PNG file (requires 'scrot').")
def screenshot(shell, args: List[str]) -> None:
    target = args[0] if args else "screenshot.png"
    if not proc.require_binary("scrot"):
        return
    print("Capturing screenshot...")
    if proc.run(["scrot", target]) == 0:
        print(f"Saved as {target}")


@command("reboot", category="System", usage="reboot",
         help="Reboot the system (sudo).")
def reboot(shell, args: List[str]) -> None:
    print("Rebooting the system...")
    proc.run(["sudo", "reboot"])


@command("shutdown", category="System", usage="shutdown",
         help="Power off the system now (sudo).")
def shutdown(shell, args: List[str]) -> None:
    print("Shutting down the system...")
    proc.run(["sudo", "shutdown", "now"])
