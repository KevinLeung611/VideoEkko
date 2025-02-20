import platform
import subprocess
import sys

def install_packages(*packages):
    try:
        subprocess.run(["pip", "install", "-U", *packages])
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")

def install_requirements():
    print("Installing requirements...")
    try:
        output = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True, capture_output=True)
        print(output.stdout.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        raise SystemExit("Exit installing. Fix the problem and install.py again.")

def check_whisper():
    print("Checking whisper installation...")
    try:
        subprocess.run(["pip", "show", "openai-whisper"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print("Whisper is not installed. Installing Whisper...")
    else:
        print("whisper has installed")

def check_ffmpeg():
    print("Checking ffmpeg installation...")
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        print("ffmpeg is not installed. Try following command to install ffmpeg.")

        system = platform.system()
        install_cmd = ""

        if system == "Windows":
            install_cmd = "choco install ffmpeg"
        elif system == "Linux":
            install_cmd = "sudo apt install ffmpeg"
        elif system == "Darwin":
            install_cmd = "brew install ffmpeg"

        print(f"The system is {system}, Try execute the following command: {install_cmd}")

        raise SystemExit("ffmpeg is required. Run install.py after installing ffmpeg.")
    else:
        print("ffmpeg has installed")

def main():
    check_whisper()
    check_ffmpeg()
    install_requirements()

if __name__ == '__main__':
    main()