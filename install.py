import platform
import sys
import subprocess
from getpass import getpass

print('Start VideoEkko Installation')

subprocess.run([sys.executable, "-m", "pip", "install", "distro==1.9.0", "rich==13.9.4"],
               check=True, capture_output=True, text=True)

system = platform.system()
password = None
if system == 'Linux':
    password = getpass(prompt='Enter root password: ')


from rich.markdown import Markdown
from rich.console import Console
import distro
console = Console()


def install_packages(*packages):
    process = subprocess.Popen([sys.executable, "-m", "pip", "install", *packages],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if process.stdout:
        for line in process.stdout:
            console.print(line, end='')
    
    if process.stderr:
        for line in process.stderr:
            console.print(line, end='', style='bold red')

    process.stdout.close()
    process.stderr.close()
    process.wait()

    if process.returncode != 0:
        console.print(f'> {packages} Install failed.', style="bold red")
        raise SystemExit(1)


def install_requirements():
    console.print(Markdown("#  Install requirements "))
    with console.status("Installing requirements..."):
        process = subprocess.Popen([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if process.stdout:
            for line in process.stdout:
                console.print(line, end='')
        
        if process.stderr:
            for line in process.stderr:
                console.print(line, end='', style='bold red')

        process.stdout.close()
        process.stderr.close()
        process.wait()

    if process.returncode != 0:
        console.print('> Requirements install failed.', style="bold red")
        raise SystemExit(1)    
    else:
        console.print("> Requirements installed successfully!", style="bold green")


def check_whisper():
    console = Console()
    console.print(Markdown("#  Check whisper installation "))
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
    console.print(Markdown("#  Check ffmpeg installation "))
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
    except FileNotFoundError:
        console.print("> ffmpeg is not installed. Start installing ffmpeg.", style="bold red")
        install_ffmpeg()
        console.print("> ffmpeg installation done!\n", style="bold green")
    else:
        console.print("> ffmpeg has installed.\n", style="bold green")


def install_ffmpeg():
    install_cmd = []
    os_name = distro.name()
    if os_name == "Windows":
        install_cmd = ["choco", "install", "-y", "ffmpeg"]
    elif os_name == "Darwin":
        install_cmd = ["brew", "install", "ffmpeg"]
    elif os_name == 'Ubuntu' or os_name == 'Debian':
        install_cmd = ['sudo', 'apt', 'install', '-y', 'ffmpeg']
    elif os_name == 'CentOS' or os_name == 'Fedora':
        install_cmd = ['sudo', 'yum', 'install', '-y', 'ffmpeg']
    else:
        console.print("Unrecognized OS. Please install ffmpeg manually. https://www.ffmpeg.org", style="bold red")
        raise SystemExit(1)


    with console.status("Installing ffmpeg..."):
        process = subprocess.Popen(install_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if system == 'Linux':
            process.stdin.write(password + '\n')
            process.stdin.flush()


        if process.stdout:
            for line in process.stdout:
                console.print(line, end='')

        if process.stderr:
            for line in process.stderr:
                console.print(line, end='', style='bold red')
            

        process.stdin.close()
        process.stdout.close()
        process.stderr.close()
        process.wait()

    if process.returncode != 0:
        console.print('> ffmpeg install failed.', style="bold red")
        raise SystemExit(1)
        


def install_fonts():
    # Not Linux system skip
    if system is not 'Linux':
        return

    install_cmd = []

    if distro.name() == 'Ubuntu' or distro.name() == 'Debian':
        install_cmd = ['sudo', 'apt', 'install', '-y', 'fonts-noto-cjk']
    elif distro.name() == 'CentOS' or distro.name() == 'Fedora':
        install_cmd = ['sudo', 'yum', 'install', '-y', 'google-noto-cjk-fonts']
    else:
        console.print('Unrecognized OS. Please install Noto Sans CJK fonts manually. https://fonts.google.com', style="bold red")
        raise SystemExit(1)

    console.print(Markdown("#  Install fonts "))
    with console.status("Installing fonts..."):
        process = subprocess.Popen(install_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        process.stdin.write(password + '\n')
        process.stdin.flush()

        if process.stdout:
            for line in process.stdout:
                console.print(line, end='')

        if process.stderr:
            for line in process.stderr:
                console.print(line, end='', style="bold red")

        process.stdin.close()
        process.stdout.close()
        process.stderr.close()
        process.wait()

    if process.returncode != 0:
        console.print('> Fonts install failed.', style="bold red")
        raise SystemExit(1)
    else:
        console.print("> Fonts installed successfully!", style="bold green")
        


def main():
    check_ffmpeg()
    check_whisper()
    install_requirements()
    install_fonts()

    console.print(Markdown('----'))
    console.print("> Installation All Finished!", style="bold green")
    console.print("> Try to run 'python web.py' or 'python engine.py'. Enjoy! Thank you!", style="bold green")


if __name__ == '__main__':
    main()
