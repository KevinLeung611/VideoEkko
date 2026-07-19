#!/usr/bin/env python3
"""VideoEkko — one-command setup script.

Usage:
  ./install.py          # full setup
  uv run install.py     # if already inside the venv
"""

import platform
import sys
import os
import subprocess
import shutil

# ── Bootstrap: re-exec inside the project venv so that rich / distro are available ──
_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.join(_PROJECT_DIR, "backend")
_VENV_PYTHON = os.path.join(_BACKEND_DIR, ".venv", "bin", "python")
if sys.executable != _VENV_PYTHON:
    subprocess.run(["uv", "sync"], check=True, cwd=_BACKEND_DIR)
    os.execv(_VENV_PYTHON, [_VENV_PYTHON, __file__])

# ── Imports (only available after bootstrap) ─────────────────────────────────────
from getpass import getpass
from rich.markdown import Markdown
from rich.console import Console
import distro

console = Console()
system = platform.system()

# ── Helpers ──────────────────────────────────────────────────────────────────────

def _run(cmd: list[str], *, silent_ok: bool = False, sudo_password: str | None = None) -> str:
    """Run a command, stream output live, and raise on failure.

    On Linux, `sudo_password` is piped to stdin for privilege escalation.
    Returns the captured stdout.
    """
    stdin = None
    if sudo_password is not None:
        stdin = subprocess.PIPE

    process = subprocess.Popen(
        cmd,
        stdin=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=_BACKEND_DIR,
    )

    if stdin is not None:
        process.stdin.write(sudo_password + "\n")
        process.stdin.flush()

    captured = []
    for line in process.stdout or []:
        console.print(line, end="")
        captured.append(line)
    for line in process.stderr or []:
        console.print(line, end="", style="bold red")

    if process.stdin:
        process.stdin.close()
    process.stdout.close() if process.stdout else None
    process.stderr.close() if process.stderr else None
    process.wait()

    if process.returncode != 0 and not silent_ok:
        console.print(f"> Command failed: {' '.join(cmd)}", style="bold red")
        raise SystemExit(1)

    return "".join(captured)


# ── Steps ────────────────────────────────────────────────────────────────────────

def check_ffmpeg():
    console.print(Markdown("#  Check ffmpeg installation "))

    # macOS: project requires ffmpeg-full (with libass for subtitle burning).
    if system == "Darwin":
        # Apple Silicon  vs  Intel
        for prefix in ("/opt/homebrew", "/usr/local"):
            ffmpeg = os.path.join(prefix, "opt", "ffmpeg-full", "bin", "ffmpeg")
            if os.path.isfile(ffmpeg):
                console.print("> ffmpeg-full found (with libass support).\n", style="bold green")
                return

        console.print("> ffmpeg-full not found. Installing via Homebrew…\n", style="yellow")
        install_ffmpeg()
        return

    # Linux / Windows — standard ffmpeg usually ships with libass.
    if shutil.which("ffmpeg"):
        console.print("> ffmpeg found.\n", style="bold green")
        return

    console.print("> ffmpeg not found. Installing…\n", style="yellow")
    install_ffmpeg()


def install_ffmpeg():
    os_name = distro.name() if system != "Windows" else "Windows"

    if os_name == "Darwin":
        cmd = ["brew", "install", "ffmpeg-full"]
    elif os_name == "Windows":
        cmd = ["choco", "install", "-y", "ffmpeg"]
    elif os_name in ("Ubuntu", "Debian"):
        cmd = ["sudo", "apt", "install", "-y", "ffmpeg"]
    elif os_name in ("CentOS", "Fedora"):
        cmd = ["sudo", "yum", "install", "-y", "ffmpeg"]
    else:
        console.print(
            "> Unrecognized OS. Please install ffmpeg manually: https://www.ffmpeg.org",
            style="bold red",
        )
        raise SystemExit(1)

    with console.status("Installing ffmpeg…"):
        _run(cmd, sudo_password=_get_linux_sudo_password())

    console.print("> ffmpeg installed!\n", style="bold green")


def check_whisper():
    console.print(Markdown("#  Check whisper installation "))
    try:
        subprocess.run(
            ["uv", "pip", "show", "openai-whisper"],
            check=True, capture_output=True, text=True, cwd=_BACKEND_DIR,
        )
        console.print("> whisper already installed.\n", style="bold green")
    except subprocess.CalledProcessError:
        console.print("> whisper not found. Installing…\n", style="yellow")
        _run(["uv", "pip", "install", "openai-whisper"])
        console.print("> whisper installed!\n", style="bold green")


def install_requirements():
    console.print(Markdown("#  Install Python dependencies "))
    with console.status("Syncing with uv…"):
        _run(["uv", "sync"])
    console.print("> Dependencies installed!\n", style="bold green")


def install_fonts():
    """Install CJK fonts on Linux (macOS ships with Heiti SC; Windows with Yahei)."""
    if system != "Linux":
        return

    os_name = distro.name()
    if os_name in ("Ubuntu", "Debian"):
        cmd = ["sudo", "apt", "install", "-y", "fonts-noto-cjk"]
    elif os_name in ("CentOS", "Fedora"):
        cmd = ["sudo", "yum", "install", "-y", "google-noto-cjk-fonts"]
    else:
        console.print(
            "> Unrecognized Linux distro. Please install Noto Sans CJK fonts manually.",
            style="yellow",
        )
        return

    console.print(Markdown("#  Install CJK fonts "))
    with console.status("Installing fonts…"):
        _run(cmd, sudo_password=password)
    console.print("> Fonts installed!\n", style="bold green")


# ── Per-run state ────────────────────────────────────────────────────────────────
password: str | None = None


def _get_linux_sudo_password() -> str | None:
    global password
    if system == "Linux" and password is None:
        password = getpass(prompt="Enter sudo password: ")
    return password


# ── Main ─────────────────────────────────────────────────────────────────────────

def main():
    print("VideoEkko — Setup")
    _get_linux_sudo_password()

    check_ffmpeg()
    check_whisper()
    install_requirements()
    install_fonts()

    console.print(Markdown("---"))
    console.print("> All done!", style="bold green")
    console.print(
        "> Run [bold]npm start[/bold] from the project root to launch the app.",
        style="bold green",
    )


if __name__ == "__main__":
    main()
