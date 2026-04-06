#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SESSIONS_DIR = ROOT / "logs" / "sessions"
SESSION_TEMPLATE = ROOT / "templates" / "session_template.md"
CURRENT_SPRINT = ROOT / "current_sprint.md"


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        return value.strip("'\"")


def parse_frontmatter_with_lines(path: Path) -> tuple[dict[str, Any], list[str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return {}, lines

    data: dict[str, Any] = {}
    end_idx = None
    current_list_key = None
    for i in range(1, len(lines)):
        line = lines[i]
        if line == "---":
            end_idx = i
            break
        if line.startswith("  - ") and current_list_key:
            data.setdefault(current_list_key, []).append(line[4:].strip().strip("'\""))
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
    if end_idx is None:
        return {}, lines
    return data, lines


def render_frontmatter(data: dict[str, Any]) -> list[str]:
    lines = ["---"]
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return lines


def write_frontmatter(path: Path, data: dict[str, Any], old_lines: list[str]) -> None:
    if not old_lines or old_lines[0] != "---":
        raise ValueError(f"{path} is missing frontmatter")
    end_idx = None
    for i in range(1, len(old_lines)):
        if old_lines[i] == "---":
            end_idx = i
            break
    if end_idx is None:
        raise ValueError(f"{path} has malformed frontmatter")
    body = old_lines[end_idx + 1 :]
    new_lines = render_frontmatter(data) + body
    path.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8")


def ensure_session_file(session_date: str) -> Path:
    target = SESSIONS_DIR / f"{session_date}.md"
    if target.exists():
        return target
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    template = SESSION_TEMPLATE.read_text(encoding="utf-8")
    template = template.replace("date:\n", f"date: {session_date}\n", 1)
    template = template.replace("# {{date}}", f"# {session_date}")
    target.write_text(template, encoding="utf-8")
    return target


def load_notes() -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []
    for path in sorted(ROOT.rglob("*.md")):
        if any(part.startswith(".") for part in path.parts):
            continue
        meta, _ = parse_frontmatter_with_lines(path)
        if not meta:
            continue
        meta["path"] = path
        notes.append(meta)
    return notes


def infer_active_lesson(notes: list[dict[str, Any]]) -> dict[str, Any] | None:
    active_lessons = [
        note
        for note in notes
        if note.get("note_type") == "lesson" and note.get("status") in {"active", "in_progress"}
    ]
    if active_lessons:
        active_lessons.sort(
            key=lambda n: (str(n.get("last_studied") or ""), int(n.get("lesson", 0) or 0)),
            reverse=True,
        )
        return active_lessons[0]

    planned_lessons = [
        note
        for note in notes
        if note.get("note_type") == "lesson" and int(note.get("completion", 0) or 0) < 100
    ]
    if planned_lessons:
        planned_lessons.sort(key=lambda n: int(n.get("lesson", 999) or 999))
        return planned_lessons[0]
    return None


def infer_next_step(notes: list[dict[str, Any]], active_lesson: dict[str, Any] | None) -> str:
    if active_lesson:
        title = str(active_lesson.get("title") or "")
        lesson_num = int(active_lesson.get("lesson", 0) or 0)
        related_lab = next(
            (
                note
                for note in notes
                if note.get("note_type") == "lab"
                and int(note.get("related_lesson", 0) or 0) == lesson_num
                and int(note.get("completion", 0) or 0) < 100
            ),
            None,
        )
        if related_lab and int(active_lesson.get("completion", 0) or 0) >= 30:
            return f"继续课程《{title}》，并尝试对应实验《{related_lab.get('title', '')}》"
        return f"继续课程《{title}》"
    return "继续当前冲刺内容"


def replace_section_bullets(lines: list[str], heading: str, bullets: list[str]) -> list[str]:
    start = None
    for i, line in enumerate(lines):
        if line.strip() == heading:
            start = i
            break
    if start is None:
        return lines
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break
    new_block = [heading, ""]
    if bullets:
        new_block.extend([f"- {item}" for item in bullets])
    else:
        new_block.append("- ")
    return lines[:start] + new_block + lines[end:]


def update_session_body(
    path: Path,
    focus_title: str,
    what_did: str | None,
    understood: str | None,
    fuzzy: str | None,
    next_step: str,
    lesson_ref: str | None,
) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    lines = replace_section_bullets(lines, "## Focus", [focus_title] if focus_title else [])
    if what_did:
        lines = replace_section_bullets(lines, "## What I Did", [what_did])
    if understood:
        lines = replace_section_bullets(lines, "## What I Understood Better", [understood])
    if fuzzy:
        lines = replace_section_bullets(lines, "## What Still Feels Fuzzy", [fuzzy])
    evidence = []
    if lesson_ref:
        evidence.append(f"lesson: {lesson_ref}")
    lines = replace_section_bullets(lines, "## Evidence", evidence)
    lines = replace_section_bullets(lines, "## Next Step", [next_step] if next_step else [])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def update_note_frontmatter(path: Path, mutate: callable) -> None:
    meta, lines = parse_frontmatter_with_lines(path)
    mutate(meta)
    write_frontmatter(path, meta, lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Finish today's study session and refresh progress.")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--minutes", type=int, default=30)
    parser.add_argument("--focus", default="")
    parser.add_argument("--what-did", default="")
    parser.add_argument("--understood", default="")
    parser.add_argument("--fuzzy", default="")
    parser.add_argument("--next-step", default="")
    parser.add_argument("--lesson-progress", type=int, default=None)
    parser.add_argument("--confidence-after", type=int, default=None)
    args = parser.parse_args()

    notes = load_notes()
    active_lesson = infer_active_lesson(notes)
    focus_title = args.focus or str(active_lesson.get("title") or "") if active_lesson else args.focus
    next_step = args.next_step or infer_next_step(notes, active_lesson)
    lesson_ref = None
    if active_lesson:
        lesson_ref = str(Path(active_lesson["path"]).relative_to(ROOT))

    session_path = ensure_session_file(args.date)

    def mutate_session(meta: dict[str, Any]) -> None:
        meta["note_type"] = "session"
        meta["title"] = "学习记录"
        meta["date"] = args.date
        meta["status"] = "logged"
        previous_minutes = int(meta.get("minutes", 0) or 0)
        meta["minutes"] = previous_minutes + args.minutes
        meta["actual_minutes"] = int(meta.get("actual_minutes", 0) or 0) + args.minutes
        meta["focus"] = focus_title
        meta["next_step"] = next_step
        if args.confidence_after is not None:
            meta["confidence_after"] = args.confidence_after
        if "tags" not in meta or not meta["tags"]:
            meta["tags"] = ["study/session"]

    update_note_frontmatter(session_path, mutate_session)
    update_session_body(
        session_path,
        focus_title=focus_title,
        what_did=args.what_did or (f"完成了一次 {args.minutes} 分钟的学习收尾" if args.minutes else ""),
        understood=args.understood or "",
        fuzzy=args.fuzzy or "",
        next_step=next_step,
        lesson_ref=lesson_ref,
    )

    if active_lesson:
        lesson_path = Path(active_lesson["path"])

        def mutate_lesson(meta: dict[str, Any]) -> None:
            meta["status"] = "active" if int(meta.get("completion", 0) or 0) < 100 else "done"
            meta["actual_minutes"] = int(meta.get("actual_minutes", 0) or 0) + args.minutes
            meta["last_studied"] = args.date
            if args.lesson_progress is not None:
                meta["completion"] = max(int(meta.get("completion", 0) or 0), args.lesson_progress)

        update_note_frontmatter(lesson_path, mutate_lesson)

    if CURRENT_SPRINT.exists():
        def mutate_sprint(meta: dict[str, Any]) -> None:
            meta["actual_minutes"] = int(meta.get("actual_minutes", 0) or 0) + args.minutes
            if meta.get("status") in {"", "planned"}:
                meta["status"] = "active"
        update_note_frontmatter(CURRENT_SPRINT, mutate_sprint)

    from update_progress import main as refresh_progress

    refresh_progress()
    print(session_path)


if __name__ == "__main__":
    main()
