#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from datetime import date
from html import escape
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
TRACKING_DIR = ROOT / "tracking"
SNAPSHOT_PATH = TRACKING_DIR / "progress_snapshot.md"
JSON_PATH = TRACKING_DIR / "progress.json"
HTML_PATH = TRACKING_DIR / "index.html"
TODAY_PATH = TRACKING_DIR / "today.md"


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip("'\"") for item in inner.split(",")]
    try:
        return int(value)
    except ValueError:
        pass
    return value.strip("'\"")


def parse_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}

    lines = text.splitlines()
    data: dict[str, Any] = {}
    i = 1
    current_list_key = None

    while i < len(lines):
        line = lines[i]
        if line == "---":
            break

        if line.startswith("  - ") and current_list_key:
          data.setdefault(current_list_key, []).append(line[4:].strip().strip("'\""))
          i += 1
          continue

        current_list_key = None
        if ":" in line:
            key, raw = line.split(":", 1)
            key = key.strip()
            raw = raw.strip()
            if raw == "":
                if i + 1 < len(lines) and lines[i + 1].startswith("  - "):
                    data[key] = []
                    current_list_key = key
                else:
                    data[key] = ""
            else:
                data[key] = parse_scalar(raw)
        i += 1

    return data


def load_notes() -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []
    for path in sorted(ROOT.rglob("*.md")):
        if any(part.startswith(".") for part in path.parts):
            continue
        frontmatter = parse_frontmatter(path)
        if not frontmatter:
            continue
        frontmatter["path"] = str(path.relative_to(ROOT))
        frontmatter["name"] = path.stem
        notes.append(frontmatter)
    return notes


def summarize_group(notes: list[dict[str, Any]], note_type: str) -> dict[str, Any]:
    group = [note for note in notes if note.get("note_type") == note_type]
    status_counts = Counter(note.get("status", "unknown") for note in group)
    total_completion = sum(int(note.get("completion", 0) or 0) for note in group)
    avg_completion = round(total_completion / len(group), 1) if group else 0.0
    total_estimated = sum(int(note.get("estimated_minutes", 0) or 0) for note in group)
    total_actual = sum(
        int(
            note.get("actual_minutes", note.get("minutes", 0)) or 0
        )
        for note in group
    )
    return {
        "count": len(group),
        "status_counts": dict(status_counts),
        "avg_completion": avg_completion,
        "estimated_minutes": total_estimated,
        "actual_minutes": total_actual,
        "items": group,
    }


def local_file_href(path: str) -> str:
    return Path(ROOT / path).resolve().as_uri()


def dashboard_href(path: str) -> str:
    return escape(os.path.relpath(ROOT / path, start=TRACKING_DIR))


def zh_status(value: str) -> str:
    mapping = {
        "planned": "未开始",
        "active": "进行中",
        "in_progress": "进行中",
        "logged": "已记录",
        "generated": "已生成",
        "done": "已完成",
    }
    return mapping.get(value, value)


def zh_track(value: str) -> str:
    mapping = {
        "linux_systems": "Linux 系统",
        "linux_tools": "Linux 工具",
        "architecture": "体系结构",
        "camera_systems": "相机系统",
        "edge_deployment": "边缘部署",
        "robotics": "机器人视觉",
        "other": "其他",
    }
    return mapping.get(value, value)


def select_profile(notes: list[dict[str, Any]]) -> dict[str, Any] | None:
    profiles = [
        note for note in notes
        if note.get("note_type") == "profile" and note.get("status") in {"active", "in_progress", "generated", ""}
    ]
    if not profiles:
        return None
    profiles.sort(key=lambda item: (str(item.get("last_updated") or ""), str(item.get("path") or "")), reverse=True)
    return profiles[0]


def render_stat_card(title: str, count: int, avg_completion: float, estimated: int, actual: int) -> str:
    return f"""
    <section class="card stat-card">
      <div class="stat-title">{escape(title)}</div>
      <div class="stat-count">{count}</div>
      <div class="stat-meta">平均完成度：{avg_completion}%</div>
      <div class="stat-meta">预计：{estimated} 分钟</div>
      <div class="stat-meta">实际：{actual} 分钟</div>
    </section>
    """


def render_note_list(
    notes: list[dict[str, Any]],
    empty_text: str,
    href_resolver: Callable[[str], str] = dashboard_href,
) -> str:
    if not notes:
        return f"<p class='empty'>{escape(empty_text)}</p>"

    items: list[str] = []
    for note in notes:
        title = zh_title(str(note.get("title") or note.get("name") or note.get("path")))
        note_type = str(note.get("note_type") or "")
        status = str(note.get("status") or "")
        completion = int(note.get("completion", 0) or 0)
        path = str(note.get("path") or "")
        type_mapping = {
            "lesson": "课程",
            "lab": "实验",
            "review": "复盘",
            "session": "学习记录",
            "sprint": "冲刺",
        }
        meta_parts = [part for part in [type_mapping.get(note_type, note_type), zh_status(status)] if part]
        if note_type in {"lesson", "lab", "review", "sprint"}:
            meta_parts.append(f"{completion}%")
        meta = " · ".join(meta_parts)
        items.append(
            "<li>"
            f"<a href='{href_resolver(path)}' target='_blank'>{escape(title)}</a>"
            f"<span>{escape(meta)}</span>"
            "</li>"
        )
    return "<ul class='note-list'>" + "".join(items) + "</ul>"


def render_track_minutes(track_minutes: dict[str, int]) -> str:
    if not track_minutes:
        return "<p class='empty'>No recorded study time yet.</p>"
    items = []
    for track, minutes in sorted(track_minutes.items()):
        items.append(
            f"<li><strong>{escape(zh_track(track))}</strong><span>{minutes} 分钟</span></li>"
        )
    return "<ul class='mini-list'>" + "".join(items) + "</ul>"


def render_profile_summary(profile: dict[str, Any] | None, href_resolver: Callable[[str], str] = dashboard_href) -> str:
    if not profile:
        return "<p class='empty'>还没有建立人物与工作上下文档案。</p>"

    path = str(profile.get("path") or "")
    title = zh_title(str(profile.get("title") or profile.get("name") or "上下文档案"))
    updated = str(profile.get("last_updated") or "")
    meta = f"最近更新：{escape(updated)}" if updated else "建议保持这份档案随节奏更新。"
    return (
        "<div class='profile-card'>"
        f"<p class='profile-title'><a href='{href_resolver(path)}' target='_blank'>{escape(title)}</a></p>"
        "<p class='profile-copy'>先读这份档案，再进入当前 sprint、今日建议和最近一次 session，"
        "能最快恢复“你是谁、你现在在推进什么、助手应该如何接手”的上下文。</p>"
        f"<p class='profile-meta'>{meta}</p>"
        "</div>"
    )


def render_status_breakdown(name: str, summary: dict[str, Any]) -> str:
    counts = summary.get("status_counts", {})
    if not counts:
        body = "<p class='empty'>No items.</p>"
    else:
        rows = "".join(
            f"<li><strong>{escape(zh_status(status))}</strong><span>{count}</span></li>"
            for status, count in sorted(counts.items())
        )
        body = "<ul class='mini-list'>" + rows + "</ul>"
    return f"<section class='card'><h3>{escape(name)}</h3>{body}</section>"


def render_table(
    notes: list[dict[str, Any]],
    columns: list[tuple[str, str]],
    empty_text: str,
    href_resolver: Callable[[str], str] = dashboard_href,
) -> str:
    if not notes:
        return f"<p class='empty'>{escape(empty_text)}</p>"

    header = "".join(f"<th>{escape(label)}</th>" for label, _ in columns)
    rows: list[str] = []
    for note in notes:
        cells: list[str] = []
        for _, key in columns:
            if key == "title":
                title = str(note.get("title") or note.get("name") or "")
                title = zh_title(title)
                path = str(note.get("path") or "")
                value = (
                    f"<a href='{href_resolver(path)}' target='_blank'>{escape(title)}</a>"
                    if path
                    else escape(title)
                )
            else:
                raw = note.get(key, "")
                if key == "status":
                    raw = zh_status(str(raw))
                elif key == "track":
                    raw = zh_track(str(raw))
                value = escape(str(raw))
            cells.append(f"<td>{value}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return (
        "<div class='table-wrap'><table><thead><tr>"
        + header
        + "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


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


def select_active_lesson(notes: list[dict[str, Any]]) -> dict[str, Any] | None:
    active = sorted(
        [n for n in notes if n.get("note_type") == "lesson" and n.get("status") in {"active", "in_progress"}],
        key=lambda item: (str(item.get("last_studied") or ""), int(item.get("lesson", 0) or 0)),
        reverse=True,
    )
    if active:
        return active[0]
    remaining = sorted(
        [n for n in notes if n.get("note_type") == "lesson" and int(n.get("completion", 0) or 0) < 100],
        key=lambda item: int(item.get("lesson", 999) or 999),
    )
    return remaining[0] if remaining else None


def select_related_lab(notes: list[dict[str, Any]], lesson_num: int) -> dict[str, Any] | None:
    return next(
        (
            n
            for n in notes
            if n.get("note_type") == "lab"
            and int(n.get("related_lesson", 0) or 0) == lesson_num
            and int(n.get("completion", 0) or 0) < 100
        ),
        None,
    )


def build_today_note(notes: list[dict[str, Any]]) -> str:
    active_lesson = select_active_lesson(notes)
    current_sprint = next((n for n in notes if n.get("note_type") == "sprint" and n.get("status") == "active"), None)
    profile = select_profile(notes)
    session_rows = sorted(
        [note for note in notes if note.get("note_type") == "session"],
        key=lambda note: str(note.get("date") or ""),
        reverse=True,
    )

    lines: list[str] = []
    lines.append("---")
    lines.append("note_type: daily_plan")
    lines.append("title: 今日学习建议")
    lines.append(f"generated_on: {date.today().isoformat()}")
    lines.append("status: generated")
    lines.append("tags:")
    lines.append("  - study/today")
    lines.append("---")
    lines.append("")
    lines.append("# 今日学习建议")
    lines.append("")
    lines.append(f"生成日期：{date.today().isoformat()}")
    lines.append("")

    lines.append("## 开场上下文")
    lines.append("")
    if profile:
        lines.append(f"- 先读 [[{profile['path']}|{profile.get('title')}]]")
        lines.append("- 这份档案会说明你大概率在做什么、当前主线目标是什么、后续助手该怎样接手")
    else:
        lines.append("- 目前还没有人物与工作上下文档案")
    lines.append("")

    if active_lesson:
        lesson_num = int(active_lesson.get("lesson", 0) or 0)
        related_lab = select_related_lab(notes, lesson_num)
        lines.append("## 今天优先学什么")
        lines.append("")
        lines.append(f"- 主线课程：[[{active_lesson['path']}|{active_lesson.get('title')}]]")
        lines.append(f"- 当前完成度：{active_lesson.get('completion', 0)}%")
        if related_lab:
            lines.append(f"- 配套实验：[[{related_lab['path']}|{related_lab.get('title')}]]")
        lines.append("")
        lines.append("## 推荐顺序")
        lines.append("")
        lines.append(f"1. 先读 [[{active_lesson['path']}|{active_lesson.get('title')}]] 的正文和补充干货。")
        if related_lab:
            lines.append(f"2. 再做 [[{related_lab['path']}|{related_lab.get('title')}]]。")
            lines.append("3. 最后写一句你今天最清楚和最模糊的点。")
        else:
            lines.append("2. 写一句你今天最清楚的结论。")
            lines.append("3. 标出一个你还不理解的词或现象。")
        lines.append("")
    else:
        lines.append("## 今天优先学什么")
        lines.append("")
        lines.append("- 当前没有未完成课程。可以转去做复盘或项目。")
        lines.append("")

    lines.append("## 当前冲刺")
    lines.append("")
    if current_sprint:
        lines.append(f"- [[{current_sprint['path']}|{current_sprint.get('title')}]]")
    else:
        lines.append("- 当前没有活跃 sprint。")
    lines.append("")

    lines.append("## 最近一次学习记录")
    lines.append("")
    if session_rows:
        latest = session_rows[0]
        lines.append(f"- [[{latest['path']}|{latest.get('date', latest.get('title'))}]]")
        if latest.get("focus"):
            lines.append(f"- 上次重点：{latest.get('focus')}")
        if latest.get("next_step"):
            lines.append(f"- 上次留下的下一步：{latest.get('next_step')}")
    else:
        lines.append("- 还没有学习记录。建议先开始一次学习会话。")
    lines.append("")

    lines.append("## 结束学习时")
    lines.append("")
    lines.append("- 你可以直接对我说：`今天学习结束了`")
    lines.append("- 或运行：`python3 /home/zhixin/code/study_system/scripts/finish_study_session.py --minutes 30`")
    lines.append("")

    return "\n".join(lines)


def build_snapshot(notes: list[dict[str, Any]]) -> str:
    lessons = summarize_group(notes, "lesson")
    labs = summarize_group(notes, "lab")
    reviews = summarize_group(notes, "review")
    sessions = summarize_group(notes, "session")

    due_reviews = sorted(
        [
            note
            for note in notes
            if note.get("next_review") and str(note.get("next_review")) <= str(date.today())
        ],
        key=lambda item: (str(item.get("next_review")), item.get("path", "")),
    )

    active_items = [
        note
        for note in notes
        if note.get("status") in {"active", "in_progress"}
        and note.get("note_type") in {"lesson", "lab", "review", "session", "sprint"}
    ]
    profile = select_profile(notes)

    track_minutes: dict[str, int] = defaultdict(int)
    for note in notes:
        track = str(note.get("track") or "other")
        track_minutes[track] += int(note.get("actual_minutes", note.get("minutes", 0)) or 0)

    lines: list[str] = []
    lines.append("---")
    lines.append("note_type: snapshot")
    lines.append("title: Progress Snapshot")
    lines.append(f"generated_on: {date.today().isoformat()}")
    lines.append("status: generated")
    lines.append("tags:")
    lines.append("  - study/snapshot")
    lines.append("---")
    lines.append("")
    lines.append("# Progress Snapshot")
    lines.append("")
    lines.append(f"Last updated: {date.today().isoformat()}")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append("| Area | Count | Avg completion | Est. min | Actual min |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    lines.append(
        f"| Lessons | {lessons['count']} | {lessons['avg_completion']}% | {lessons['estimated_minutes']} | {lessons['actual_minutes']} |"
    )
    lines.append(
        f"| Labs | {labs['count']} | {labs['avg_completion']}% | {labs['estimated_minutes']} | {labs['actual_minutes']} |"
    )
    lines.append(
        f"| Reviews | {reviews['count']} | {reviews['avg_completion']}% | {reviews['estimated_minutes']} | {reviews['actual_minutes']} |"
    )
    lines.append(
        f"| Sessions | {sessions['count']} | {sessions['avg_completion']}% | {sessions['estimated_minutes']} | {sessions['actual_minutes']} |"
    )
    lines.append("")
    lines.append("## Status Breakdown")
    lines.append("")
    for label, summary in [("Lessons", lessons), ("Labs", labs), ("Reviews", reviews)]:
        lines.append(f"### {label}")
        if summary["status_counts"]:
            for status, count in sorted(summary["status_counts"].items()):
                lines.append(f"- {status}: {count}")
        else:
            lines.append("- no items")
        lines.append("")

    lines.append("## Active Items")
    lines.append("")
    if active_items:
        for note in active_items:
            lines.append(
                f"- [[{note['path']}|{note.get('title', note['name'])}]]"
                f" ({note.get('note_type')}, {note.get('status')}, {note.get('completion', 0)}%)"
            )
    else:
        lines.append("- no active items")
    lines.append("")

    lines.append("## Context Anchor")
    lines.append("")
    if profile:
        lines.append(f"- Read [[{profile['path']}|{profile.get('title', profile['name'])}]] before handing off work")
    else:
        lines.append("- no profile note is available yet")
    lines.append("")

    lines.append("## Review Queue")
    lines.append("")
    if due_reviews:
        for note in due_reviews:
            lines.append(
                f"- [[{note['path']}|{note.get('title', note['name'])}]] due {note.get('next_review')}"
            )
    else:
        lines.append("- no notes are due for review today")
    lines.append("")

    lines.append("## Minutes By Track")
    lines.append("")
    if track_minutes:
        for track, minutes in sorted(track_minutes.items()):
            lines.append(f"- {track}: {minutes}")
    else:
        lines.append("- no recorded study time yet")
    lines.append("")

    lines.append("## Next Recommended Actions")
    lines.append("")
    active_lesson = select_active_lesson(notes)
    if profile:
        lines.append(f"- Read [[{profile['path']}|{profile.get('title', profile['name'])}]] to recover user context quickly")
    if active_lesson:
        lines.append(f"- Continue [[{active_lesson['path']}|{active_lesson.get('title')}]]")
        related_lab = select_related_lab(notes, int(active_lesson.get("lesson", 0) or 0))
        if related_lab:
            lines.append(f"- Run [[{related_lab['path']}|{related_lab.get('title')}]]")
    lines.append("- Read `tracking/today.md` for a short study plan")
    lines.append("- Say `今天学习结束了` and I can update today’s session for you")
    lines.append("- Or run `python3 scripts/finish_study_session.py --minutes 30`")
    lines.append("")
    return "\n".join(lines)


def build_html_dashboard(
    notes: list[dict[str, Any]],
    href_resolver: Callable[[str], str] = dashboard_href,
    dashboard_title: str = "周志昕的学习进度面板",
) -> str:
    lessons = summarize_group(notes, "lesson")
    labs = summarize_group(notes, "lab")
    reviews = summarize_group(notes, "review")
    sessions = summarize_group(notes, "session")
    profile = select_profile(notes)

    due_reviews = sorted(
        [
            note
            for note in notes
            if note.get("note_type") == "review"
            and note.get("next_review")
            and str(note.get("next_review")) <= str(date.today())
        ],
        key=lambda item: (str(item.get("next_review")), item.get("path", "")),
    )

    active_items = [
        note
        for note in notes
        if note.get("status") in {"active", "in_progress"}
        and note.get("note_type") in {"lesson", "lab", "review", "session", "sprint"}
    ]

    track_minutes: dict[str, int] = defaultdict(int)
    for note in notes:
        track = str(note.get("track") or "other")
        track_minutes[track] += int(note.get("actual_minutes", 0) or 0)

    lesson_rows = sorted(
        [note for note in notes if note.get("note_type") == "lesson"],
        key=lambda note: (int(note.get("phase", 0) or 0), int(note.get("lesson", 0) or 0)),
    )
    lab_rows = sorted(
        [note for note in notes if note.get("note_type") == "lab"],
        key=lambda note: (int(note.get("phase", 0) or 0), int(note.get("related_lesson", 0) or 0)),
    )
    session_rows = sorted(
        [note for note in notes if note.get("note_type") == "session"],
        key=lambda note: str(note.get("date") or ""),
        reverse=True,
    )
    latest_session_path = "logs/sessions/2026-04-06.md"
    if session_rows:
        latest_session_path = str(session_rows[0].get("path") or latest_session_path)

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>学习进度面板</title>
  <style>
    :root {{
      --bg: #eef4f8;
      --panel: #ffffff;
      --line: #cbd5e1;
      --text: #102033;
      --muted: #475569;
      --accent: #0f766e;
      --accent-strong: #0b5a54;
      --button-bg: rgba(255,255,255,0.94);
      --button-text: #0f3d3a;
      --button-line: rgba(255,255,255,0.72);
      --warm: #9a3412;
      --shadow: 0 16px 32px rgba(15, 23, 42, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", "PingFang SC", "Noto Sans SC", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top right, rgba(15, 118, 110, 0.10), transparent 28%),
        radial-gradient(circle at top left, rgba(180, 83, 9, 0.08), transparent 22%),
        var(--bg);
    }}
    .shell {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }}
    .hero {{
      background: linear-gradient(140deg, #0f3d3a, #155e75 52%, #0f766e 100%);
      color: white;
      border-radius: 24px;
      padding: 28px;
      box-shadow: var(--shadow);
    }}
    .hero h1 {{
      margin: 0 0 8px;
      font-size: 32px;
    }}
    .hero .sub {{
      margin-top: 8px;
      font-size: 14px;
      color: rgba(255,255,255,0.85);
    }}
    .hero p {{
      margin: 0;
      color: rgba(255,255,255,0.96);
    }}
    .hero-links {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin-top: 18px;
    }}
    .hero-links a {{
      color: var(--button-text);
      text-decoration: none;
      padding: 10px 14px;
      border: 1px solid var(--button-line);
      border-radius: 999px;
      background: var(--button-bg);
      transition: background 0.18s ease, transform 0.18s ease, border-color 0.18s ease;
      box-shadow: 0 8px 18px rgba(10, 25, 41, 0.12);
    }}
    .hero-links a:hover {{
      background: #ffffff;
      border-color: #ffffff;
      transform: translateY(-1px);
    }}
    .section {{
      margin-top: 24px;
    }}
    .section h2 {{
      margin: 0 0 12px;
      font-size: 20px;
    }}
    .grid {{
      display: grid;
      gap: 16px;
    }}
    .stats {{
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    }}
    .two-col {{
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 20px;
      padding: 18px;
      box-shadow: var(--shadow);
    }}
    .stat-title {{
      color: var(--text);
      font-size: 13px;
      margin-bottom: 10px;
      letter-spacing: 0.02em;
    }}
    .stat-count {{
      font-size: 34px;
      font-weight: 700;
      color: var(--accent);
      margin-bottom: 8px;
    }}
    .stat-meta {{
      color: var(--text);
      font-size: 14px;
      margin-top: 4px;
    }}
    .note-list, .mini-list {{
      list-style: none;
      padding: 0;
      margin: 0;
    }}
    .note-list li, .mini-list li {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      padding: 10px 0;
      border-bottom: 1px solid var(--line);
      align-items: baseline;
    }}
    .note-list li:last-child, .mini-list li:last-child {{
      border-bottom: 0;
      padding-bottom: 0;
    }}
    .note-list a, table a, .hero a {{
      color: var(--accent);
      font-weight: 600;
      text-decoration: none;
    }}
    .note-list a:hover, table a:hover {{
      color: var(--accent-strong);
      text-decoration: underline;
    }}
    .note-list span, .mini-list span {{
      color: var(--text);
      white-space: nowrap;
    }}
    .table-wrap {{
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: var(--panel);
      box-shadow: var(--shadow);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 720px;
    }}
    th, td {{
      text-align: left;
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      font-size: 14px;
    }}
    th {{
      background: #eef6f8;
      color: var(--warm);
      font-weight: 700;
    }}
    tr:last-child td {{
      border-bottom: 0;
    }}
    .empty {{
      margin: 0;
      color: var(--muted);
    }}
    .profile-card {{
      display: grid;
      gap: 10px;
    }}
    .profile-title, .profile-copy, .profile-meta {{
      margin: 0;
    }}
    .profile-title a {{
      font-size: 18px;
      color: var(--accent);
      text-decoration: none;
    }}
    .profile-title a:hover {{
      color: var(--accent-strong);
      text-decoration: underline;
    }}
    .profile-copy {{
      color: var(--text);
      line-height: 1.65;
    }}
    .profile-meta {{
      color: var(--muted);
      font-size: 13px;
    }}
    .footer {{
      margin-top: 28px;
      color: var(--text);
      font-size: 13px;
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <h1>{escape(dashboard_title)}</h1>
      <p>生成日期：{escape(date.today().isoformat())}。这个页面会把课程、实验、复盘和学习记录汇总到一起。</p>
      <div class="hero-links">
        <a href="{href_resolver('operator_context.md')}" target="_blank">打开上下文档案</a>
        <a href="{href_resolver('tracking/today.md')}" target="_blank">打开今日建议</a>
        <a href="{href_resolver('dashboard.md')}" target="_blank">打开 Markdown 面板</a>
        <a href="{href_resolver('tracking/progress_snapshot.md')}" target="_blank">打开快照</a>
        <a href="{href_resolver(latest_session_path)}" target="_blank">打开最近一次学习记录</a>
      </div>
    </section>

    <section class="section">
      <h2>总览</h2>
      <div class="grid stats">
        {render_stat_card("课程", lessons["count"], lessons["avg_completion"], lessons["estimated_minutes"], lessons["actual_minutes"])}
        {render_stat_card("实验", labs["count"], labs["avg_completion"], labs["estimated_minutes"], labs["actual_minutes"])}
        {render_stat_card("复盘", reviews["count"], reviews["avg_completion"], reviews["estimated_minutes"], reviews["actual_minutes"])}
        {render_stat_card("学习记录", sessions["count"], sessions["avg_completion"], sessions["estimated_minutes"], sessions["actual_minutes"])}
      </div>
    </section>

    <section class="section">
      <div class="grid two-col">
        <section class="card">
          <h2>人物与工作上下文</h2>
          {render_profile_summary(profile, href_resolver)}
        </section>
        <section class="card">
          <h2>当前重点</h2>
          {render_note_list(active_items, "当前没有活跃项。", href_resolver)}
        </section>
        <section class="card">
          <h2>待复习</h2>
          {render_note_list(due_reviews, "今天没有到期的复习项。", href_resolver)}
        </section>
      </div>
    </section>

    <section class="section">
      <div class="grid two-col">
        {render_status_breakdown("课程状态", lessons)}
        {render_status_breakdown("实验状态", labs)}
      </div>
    </section>

    <section class="section">
      <div class="grid two-col">
        <section class="card">
          <h2>各方向学习时长</h2>
          {render_track_minutes(track_minutes)}
        </section>
        <section class="card">
          <h2>快捷入口</h2>
          <ul class="mini-list">
            <li><strong>当前 sprint</strong><span><a href="{href_resolver('current_sprint.md')}" target="_blank">打开</a></span></li>
            <li><strong>今日建议</strong><span><a href="{href_resolver('tracking/today.md')}" target="_blank">打开</a></span></li>
            <li><strong>课程总表</strong><span><a href="{href_resolver('course_plan.md')}" target="_blank">打开</a></span></li>
            <li><strong>刷新命令</strong><span><code>python3 scripts/update_progress.py</code></span></li>
          </ul>
        </section>
      </div>
    </section>

    <section class="section">
      <h2>课程列表</h2>
      {render_table(lesson_rows, [("标题", "title"), ("阶段", "phase"), ("课次", "lesson"), ("方向", "track"), ("状态", "status"), ("完成度", "completion"), ("下次复习", "next_review")], "还没有课程笔记。", href_resolver)}
    </section>

    <section class="section">
      <h2>实验列表</h2>
      {render_table(lab_rows, [("标题", "title"), ("阶段", "phase"), ("对应课次", "related_lesson"), ("方向", "track"), ("状态", "status"), ("完成度", "completion"), ("最近运行", "last_run")], "还没有实验记录。", href_resolver)}
    </section>

    <section class="section">
      <h2>学习记录</h2>
      {render_table(session_rows, [("标题", "title"), ("日期", "date"), ("分钟", "minutes"), ("重点", "focus"), ("状态", "energy"), ("下一步", "next_step")], "还没有学习记录。", href_resolver)}
    </section>

    <p class="footer">这个页面由本地 Markdown 学习系统自动生成。每次学习后运行 <code>python3 /home/zhixin/code/study_system/scripts/update_progress.py</code>，网页就会更新。</p>
  </main>
</body>
</html>
"""


def main() -> None:
    notes = load_notes()
    snapshot = build_snapshot(notes)
    today_note = build_today_note(notes)
    html = build_html_dashboard(notes)
    TRACKING_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_PATH.write_text(snapshot + "\n", encoding="utf-8")
    TODAY_PATH.write_text(today_note + "\n", encoding="utf-8")
    HTML_PATH.write_text(html, encoding="utf-8")

    payload = {
        "generated_on": date.today().isoformat(),
        "notes": notes,
        "summary": {
            "lesson": summarize_group(notes, "lesson"),
            "lab": summarize_group(notes, "lab"),
            "review": summarize_group(notes, "review"),
            "session": summarize_group(notes, "session"),
        },
    }
    JSON_PATH.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
