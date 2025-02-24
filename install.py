import sys
import subprocess

print('Start VideoEkko Installation')

subprocess.run([sys.executable, "-m", "pip", "install", "distro==1.9.0", "rich==13.9.4"], check=True,
               capture_output=True, text=True)

import platform
import distro

from rich.console import Console
from rich.markdown import Markdown

console = Console()


def install_packages(*packages):
    subprocess.run([sys.executable, "-m", "pip", "install", *packages], check=True, capture_output=True, text=True)


def install_requirements():
    console.print(Markdown("# 👉🏻 Install requirements 👈🏻"))
    with console.status("Installing requirements..."):
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                       check=True, capture_output=True, text=True)
    console.print("> Requirements installed successfully!", style="bold green")


def check_whisper():
    console = Console()
    console.print(Markdown("# 👉🏻 Check whisper installation 👈🏻"))
    try:
        subprocess.run([sys.executable, "-m", "pip", "show", "openai-whisper"],
                       check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError:
        console.print("> Whisper is not installed. Start installing Whisper.", style="bold red")
        install_whisper()
        console.print("> Whisper installation done!\n", style="bold green")
    else:
        console.print("> whisper has installed.\n", style="bold green")


def install_whisper():
    with console.status("Installing Whisper..."):
        install_packages("-U", "openai-whisper")


def check_ffmpeg():
    console = Console()
    console.print(Markdown("# 👉🏻 Check ffmpeg installation 👈🏻"))
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
    except FileNotFoundError:
        console.print("> ffmpeg is not installed. Start installing ffmpeg.", style="bold red")
        install_ffmpeg()
        console.print("> ffmpeg installation done!\n", style="bold green")
    else:
        console.print("> ffmpeg has installed.\n", style="bold green")


def install_ffmpeg():
    console = Console()
    install_cmd = get_ffmpeg_install_cmd()

    if not install_cmd:
        console.print("> Unknown OS. Please visit the following ffmpeg page to install. https://www.ffmpeg.org",
                      style="bold red")
        raise SystemExit(1)

    with console.status("Installing ffmpeg..."):
        subprocess.run(install_cmd, capture_output=True, check=True, text=True)


def get_ffmpeg_install_cmd():
    system = platform.system()
    if system == "Windows":
        return ["choco", "install", "ffmpeg"]
    elif system == "Linux":
        os_name = distro.name()
        if os_name == 'Ubuntu' or os_name == 'Debian':
            return ["apt", "-y", "install", "ffmpeg"]
        elif os_name == 'CentOS' or os_name == 'Fedora':
            return ["yum", "-y", "install", "ffmpeg"]
    elif system == "Darwin":
        return ["brew", "install", "ffmpeg"]
    else:
        return None


def main():
    check_ffmpeg()
    check_whisper()
    install_requirements()


if __name__ == '__main__':
    main()
