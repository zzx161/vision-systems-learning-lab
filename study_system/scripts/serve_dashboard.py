#!/usr/bin/env python3
from __future__ import annotations

import html
import http.server
import re
import socket
import socketserver
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORT = 8765


def zh_title(title: str) -> str:
    mapping = {
        "Processes, Threads, Locks, and Context Switching": "进程、线程、锁与上下文切换",
        "Virtual Memory, Pages, Page Faults, and mmap": "虚拟内存、页、缺页与 mmap",
        "CPU, Cache, Locality, and Why Memory Access Dominates Performance": "CPU、缓存、局部性与内存访问性能",
        "Linux Observability for Engineers": "面向工程师的 Linux 可观测性",
        "Camera Data Path, Buffers, and Frame Lifecycle": "相机数据路径、缓冲区与帧生命周期",
        "Latency, Jitter, Frame Drops, and Synchronization": "延迟、抖动、掉帧与同步",
        "ONNX and Inference Runtime Basics for System Engineers": "面向系统工程师的 ONNX 与推理运行时基础",
        "Quantization, TensorRT, and Platform Toolchains": "量化、TensorRT 与平台工具链",
        "Profiling Deployed Inference": "已部署推理的性能分析",
        "ROS2 Basics for Vision Engineers": "视觉工程师的 ROS2 基础",
        "Calibration, Hand-Eye Calibration, and 3D Vision Awareness": "标定、手眼标定与 3D 视觉认知",
        "End-to-End Project Design": "端到端项目设计",
        "Current Sprint": "当前冲刺",
        "Study Session": "学习记录",
        "Week 1 Review": "第 1 周复盘",
        "Threads and Contention": "线程与竞争",
        "Virtual Memory, Copying, and mmap": "虚拟内存、拷贝与 mmap",
        "Cache, Locality, and False Sharing": "缓存、局部性与伪共享",
        "First Observability Practice": "第一次可观测性练习",
    }
    return mapping.get(title, title)


def zh_meta_key(key: str) -> str:
    mapping = {
        "phase": "阶段",
        "lesson": "课次",
        "track": "方向",
        "status": "状态",
        "completion": "完成度",
    }
    return mapping.get(key, key)


def zh_meta_value(key: str, value: str) -> str:
    if key == "status":
        mapping = {"planned": "未开始", "active": "进行中", "in_progress": "进行中", "done": "已完成"}
        return mapping.get(value, value)
    if key == "track":
        mapping = {
            "linux_systems": "Linux 系统",
            "linux_tools": "Linux 工具",
            "architecture": "体系结构",
            "camera_systems": "相机系统",
            "edge_deployment": "边缘部署",
            "robotics": "机器人视觉",
        }
        return mapping.get(value, value)
    return value


def ensure_dashboard() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "update_progress.py")],
        check=True,
    )


def pick_port(preferred: int) -> int:
    for port in range(preferred, preferred + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise RuntimeError("No available port found between 8765 and 8784")


def strip_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text

    lines = text.splitlines()
    metadata: dict[str, str] = {}
    idx = 1
    while idx < len(lines):
        line = lines[idx]
        if line == "---":
            idx += 1
            break
        if line.startswith("  - "):
            idx += 1
            continue
        if ":" in line:
            key, raw = line.split(":", 1)
            metadata[key.strip()] = raw.strip().strip("'\"")
        idx += 1
    body = "\n".join(lines[idx:])
    return metadata, body


def infer_title(body: str, fallback: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def convert_wikilinks(text: str, href_resolver: Callable[[str], str] | None = None) -> str:
    def repl(match: re.Match[str]) -> str:
        raw = match.group(1)
        if "|" in raw:
            target, label = raw.split("|", 1)
        else:
            target, label = raw, raw
        target = target.strip()
        label = label.strip()
        if not target.endswith(".md"):
            target = f"{target}.md"
        href = href_resolver(target) if href_resolver else target
        return f"<a href='{html.escape(href)}'>{html.escape(label)}</a>"

    return re.sub(r"\[\[([^\]]+)\]\]", repl, text)


def render_inline(text: str, href_resolver: Callable[[str], str] | None = None) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    def markdown_link(match: re.Match[str]) -> str:
        label, href = match.group(1), match.group(2)
        resolved = href_resolver(href) if href_resolver else href
        return f"<a href='{resolved}'>{label}</a>"
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", markdown_link, text)
    text = convert_wikilinks(text, href_resolver)
    return text


def render_markdown_body(text: str, href_resolver: Callable[[str], str] | None = None) -> str:
    lines = text.splitlines()
    parts: list[str] = []
    paragraph: list[str] = []
    in_code = False
    code_lines: list[str] = []
    list_type: str | None = None

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            joined = " ".join(line.strip() for line in paragraph if line.strip())
            parts.append(f"<p>{render_inline(joined, href_resolver)}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_type
        if list_type:
            parts.append(f"</{list_type}>")
            list_type = None

    for line in lines:
        if line.startswith("```"):
            flush_paragraph()
            flush_list()
            if in_code:
                parts.append(
                    "<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>"
                )
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            flush_list()
            continue

        if stripped.startswith("#"):
            flush_paragraph()
            flush_list()
            level = len(stripped) - len(stripped.lstrip("#"))
            level = max(1, min(level, 6))
            title = stripped[level:].strip()
            parts.append(f"<h{level}>{render_inline(title, href_resolver)}</h{level}>")
            continue

        if re.match(r"^[-*] ", stripped):
            flush_paragraph()
            if list_type != "ul":
                flush_list()
                list_type = "ul"
                parts.append("<ul>")
            parts.append(f"<li>{render_inline(stripped[2:].strip(), href_resolver)}</li>")
            continue

        if re.match(r"^\d+\. ", stripped):
            flush_paragraph()
            if list_type != "ol":
                flush_list()
                list_type = "ol"
                parts.append("<ol>")
            item = re.sub(r"^\d+\. ", "", stripped)
            parts.append(f"<li>{render_inline(item, href_resolver)}</li>")
            continue

        paragraph.append(line)

    flush_paragraph()
    flush_list()
    if in_code:
        parts.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
    return "\n".join(parts)


def markdown_page(
    title: str,
    path: str,
    metadata: dict[str, str],
    body_html: str,
    href_resolver: Callable[[str], str] | None = None,
    dashboard_title: str = "周志昕的学习进度面板",
) -> bytes:
    chips: list[str] = []
    for key in ("phase", "lesson", "track", "status", "completion"):
        value = metadata.get(key, "").strip()
        if value:
            chips.append(
                f"<span class='chip'>{html.escape(zh_meta_key(key))}: {html.escape(zh_meta_value(key, value))}</span>"
            )
    chips_html = "".join(chips)
    title = zh_title(title)

    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      --bg: #f4f8fb;
      --panel: #ffffff;
      --line: #d5dde7;
      --text: #122033;
      --muted: #526072;
      --accent: #0f766e;
      --accent-strong: #0b5a54;
      --hero: linear-gradient(135deg, #0f3d3a, #155e75 58%, #0f766e 100%);
      --shadow: 0 16px 32px rgba(15, 23, 42, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", "PingFang SC", "Noto Sans SC", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top right, rgba(15, 118, 110, 0.08), transparent 28%),
        radial-gradient(circle at top left, rgba(21, 94, 117, 0.08), transparent 22%),
        var(--bg);
    }}
    .shell {{
      max-width: 960px;
      margin: 0 auto;
      padding: 28px 18px 48px;
    }}
    .hero {{
      background: var(--hero);
      color: white;
      border-radius: 24px;
      padding: 24px;
      box-shadow: var(--shadow);
    }}
    .hero h1 {{
      margin: 0 0 8px;
      font-size: 30px;
    }}
    .sub {{
      color: rgba(255,255,255,0.92);
      font-size: 14px;
      margin-bottom: 14px;
    }}
    .nav {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .nav a {{
      text-decoration: none;
      color: #0f3d3a;
      background: rgba(255,255,255,0.96);
      border-radius: 999px;
      padding: 10px 14px;
      font-weight: 600;
    }}
    .meta {{
      margin-top: 14px;
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .chip {{
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(255,255,255,0.16);
      border: 1px solid rgba(255,255,255,0.22);
      color: white;
      font-size: 13px;
    }}
    article {{
      margin-top: 22px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 22px;
      padding: 28px;
      box-shadow: var(--shadow);
      line-height: 1.8;
    }}
    h1, h2, h3, h4, h5, h6 {{
      color: var(--text);
      line-height: 1.3;
      margin-top: 1.5em;
      margin-bottom: 0.6em;
    }}
    article > h1:first-child,
    article > h2:first-child {{
      margin-top: 0;
    }}
    p, li {{
      color: var(--text);
      font-size: 16px;
    }}
    ul, ol {{
      padding-left: 1.5em;
    }}
    a {{
      color: var(--accent);
      font-weight: 600;
    }}
    a:hover {{
      color: var(--accent-strong);
    }}
    code {{
      background: #eef6f7;
      color: #0f3d3a;
      padding: 2px 6px;
      border-radius: 6px;
      font-family: "Cascadia Code", "Consolas", monospace;
      font-size: 0.95em;
    }}
    pre {{
      background: #0f172a;
      color: #e2e8f0;
      padding: 16px;
      border-radius: 16px;
      overflow-x: auto;
    }}
    pre code {{
      background: transparent;
      color: inherit;
      padding: 0;
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <h1>{html.escape(title)}</h1>
      <div class="sub">{html.escape(path)}</div>
      <div class="nav">
        <a href="{html.escape(href_resolver('tracking/index.html') if href_resolver else '/tracking/index.html')}">返回学习面板</a>
        <a href="{html.escape(href_resolver('dashboard.md') if href_resolver else '/dashboard.md')}">打开总面板</a>
        <a href="{html.escape(href_resolver('tracking/progress_snapshot.md') if href_resolver else '/tracking/progress_snapshot.md')}">打开快照</a>
      </div>
      <div class="meta">{chips_html}</div>
    </section>
    <article>{body_html}</article>
  </main>
</body>
</html>
"""
    return page.encode("utf-8")


class StudyHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        requested = urllib.parse.unquote(parsed.path.lstrip("/"))
        if requested == "":
            self.send_response(302)
            self.send_header("Location", "/tracking/index.html")
            self.end_headers()
            return

        target = (ROOT / requested).resolve()
        if not str(target).startswith(str(ROOT)) or not target.exists():
            self.send_error(404, "File not found")
            return

        if target.suffix.lower() == ".md":
            self.serve_markdown(target)
            return

        self.path = "/" + requested
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def serve_markdown(self, target: Path) -> None:
        raw = target.read_text(encoding="utf-8")
        metadata, body = strip_frontmatter(raw)
        title = metadata.get("title") or infer_title(body, target.stem)
        body_html = render_markdown_body(body, lambda p: "/" + p)
        payload = markdown_page(title, str(target.relative_to(ROOT)), metadata, body_html, lambda p: "/" + p)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main() -> None:
    ensure_dashboard()
    port = pick_port(DEFAULT_PORT)

    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    handler = lambda *args, **kwargs: StudyHandler(*args, directory=str(ROOT), **kwargs)
    with ReusableTCPServer(("127.0.0.1", port), handler) as httpd:
        print(f"http://127.0.0.1:{port}/tracking/index.html", flush=True)
        httpd.serve_forever()


if __name__ == "__main__":
    main()
