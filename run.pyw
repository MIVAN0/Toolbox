import os
import subprocess

VENV_DIR = "venv"

def venv_python():
    if os.name == "nt":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")

python = venv_python()

if not os.path.exists(python):
    print("Virtual environment not found.")
    print("Please run install.py first.")
    input("Press Enter to exit...")
    raise SystemExit

subprocess.check_call([python, "main.py"])
