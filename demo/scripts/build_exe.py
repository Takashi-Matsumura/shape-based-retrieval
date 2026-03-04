"""Build standalone executable using PyInstaller."""

import subprocess
import sys
from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parent.parent
SPEC_FILE = DEMO_DIR / "demo.spec"


def build() -> None:
    """Run PyInstaller to build the executable."""
    if not SPEC_FILE.exists():
        print(f"ERROR: Spec file not found: {SPEC_FILE}")
        sys.exit(1)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        str(SPEC_FILE),
    ]

    print(f"Building with: {' '.join(cmd)}")
    print(f"Working directory: {DEMO_DIR}")

    result = subprocess.run(cmd, cwd=str(DEMO_DIR))

    if result.returncode == 0:
        dist_dir = DEMO_DIR / "dist" / "CADSearchDemo"
        print(f"\nBuild successful!")
        print(f"Output: {dist_dir}")
        if sys.platform == "win32":
            print(f"Run: {dist_dir / 'CADSearchDemo.exe'}")
        else:
            print(f"Run: {dist_dir / 'CADSearchDemo'}")
    else:
        print(f"\nBuild failed with exit code {result.returncode}")
        sys.exit(result.returncode)


if __name__ == "__main__":
    build()
