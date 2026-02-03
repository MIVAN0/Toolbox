import sys
import subprocess
import os

VENV_DIR = "venv"

def venv_python():
    if os.name == "nt":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")

print("Creating virtual environment...")
if not os.path.exists(VENV_DIR):
    subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])

python = venv_python()

print("Upgrading pip...")
subprocess.check_call([python, "-m", "pip", "install", "--upgrade", "pip"])

print("Installing requirements...")
subprocess.check_call([python, "-m", "pip", "install", "-r", "requirements.txt"])

print("\nInstallation complete!")
print("You can now run the app using run.py")