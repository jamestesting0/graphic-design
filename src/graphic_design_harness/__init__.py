import os
from pathlib import Path
import sys


def main():
    studio = Path(__file__).resolve().parent / "skills/setup-design-studio/scripts/studio.py"
    os.execv(sys.executable, [sys.executable, "-B", str(studio), *sys.argv[1:]])
