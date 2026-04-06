#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "tracking" / ".server_state.json"
SERVER_SCRIPT = ROOT / "scripts" / "serve_dashboard.py"
DEFAULT_URL = "http://127.0.0.1:8765/tracking/index.html"


def explorer_path() -> str:
    return shutil.which("explorer.exe") or "/mnt/c/Windows/explorer.exe"


def read_state() -> dict[str, object] | None:
    if not STATE_PATH.exists():
        return None
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None


def write_state(payload: dict[str, object]) -> None:
    STATE_PATH.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def clear_stale_state() -> None:
    state = read_state()
    if not state:
        return
    pid = state.get("pid")
    if isinstance(pid, int) and not pid_alive(pid):
        STATE_PATH.unlink(missing_ok=True)


def url_alive(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=0.6) as response:
            return response.status == 200
    except Exception:
        return False


def start_server() -> str:
    proc = subprocess.Popen(
        [sys.executable, str(SERVER_SCRIPT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        start_new_session=True,
    )

    url = DEFAULT_URL
    deadline = time.time() + 5
    while time.time() < deadline:
        if proc.stdout is not None:
            line = proc.stdout.readline().strip()
            if line.startswith("http://"):
                url = line
                break
        time.sleep(0.1)

    if not url_alive(url):
        raise RuntimeError("Dashboard server failed to start")

    write_state({"pid": proc.pid, "url": url})
    return url


def probe_existing_server() -> str | None:
    for port in range(8765, 8785):
        url = f"http://127.0.0.1:{port}/tracking/index.html"
        if url_alive(url):
            return url
    return None


def ensure_server() -> str:
    clear_stale_state()
    state = read_state()
    if state:
        url = str(state.get("url") or DEFAULT_URL)
        if url_alive(url):
            return url
    reused = probe_existing_server()
    if reused:
        write_state({"pid": -1, "url": reused})
        return reused
    return start_server()


def main() -> None:
    url = ensure_server()
    subprocess.run([explorer_path(), url], check=False)
    print(url)


if __name__ == "__main__":
    main()
