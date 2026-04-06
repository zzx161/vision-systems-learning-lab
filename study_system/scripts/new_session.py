#!/usr/bin/env python3
from __future__ import annotations

from datetime import date
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = ROOT / "templates" / "session_template.md"
SESSIONS_DIR = ROOT / "logs" / "sessions"


def main() -> None:
    session_date = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    target = SESSIONS_DIR / f"{session_date}.md"
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    if target.exists():
        print(target)
        return

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    template = template.replace("date:\n", f"date: {session_date}\n", 1)
    template = template.replace("# {{date}}", f"# {session_date}")
    target.write_text(template, encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
