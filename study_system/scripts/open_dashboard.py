#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "tracking" / "index.html"


def to_windows_unc(path: Path) -> str:
    result = subprocess.run(
        ["wslpath", "-w", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def main() -> None:
    if not DASHBOARD.exists():
        raise SystemExit(f"Dashboard not found: {DASHBOARD}")

    windows_path = to_windows_unc(DASHBOARD)
    explorer = shutil.which("explorer.exe") or "/mnt/c/Windows/explorer.exe"
    subprocess.run([explorer, windows_path], check=False)
    print(windows_path)


if __name__ == "__main__":
    main()
