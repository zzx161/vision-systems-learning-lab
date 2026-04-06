#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date

from finish_study_session import (
    CURRENT_SPRINT,
    ROOT,
    ensure_session_file,
    infer_active_lesson,
    infer_next_step,
    load_notes,
    parse_frontmatter_with_lines,
    update_note_frontmatter,
    update_session_body,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Start today's study session and refresh progress.")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--focus", default="")
    parser.add_argument("--energy", default="medium")
    parser.add_argument("--confidence-before", type=int, default=None)
    args = parser.parse_args()

    notes = load_notes()
    active_lesson = infer_active_lesson(notes)
    focus_title = args.focus or (str(active_lesson.get("title") or "") if active_lesson else "")
    next_step = infer_next_step(notes, active_lesson)
    lesson_ref = None
    if active_lesson:
        lesson_ref = str(active_lesson["path"].relative_to(ROOT))

    session_path = ensure_session_file(args.date)

    def mutate_session(meta: dict) -> None:
        meta["note_type"] = "session"
        meta["title"] = "学习记录"
        meta["date"] = args.date
        meta["status"] = "in_progress"
        meta["focus"] = focus_title
        meta["energy"] = args.energy
        meta.setdefault("minutes", 0)
        meta.setdefault("actual_minutes", 0)
        meta["next_step"] = next_step
        if args.confidence_before is not None:
            meta["confidence_before"] = args.confidence_before
        if "tags" not in meta or not meta["tags"]:
            meta["tags"] = ["study/session"]

    update_note_frontmatter(session_path, mutate_session)
    update_session_body(
        session_path,
        focus_title=focus_title,
        what_did=f"开始今天的学习，先进入《{focus_title}》" if focus_title else "开始今天的学习",
        understood="",
        fuzzy="",
        next_step=next_step,
        lesson_ref=lesson_ref,
    )

    if active_lesson:
        lesson_path = active_lesson["path"]

        def mutate_lesson(meta: dict) -> None:
            if meta.get("status") in {"", "planned"}:
                meta["status"] = "active"
            meta["last_studied"] = args.date

        update_note_frontmatter(lesson_path, mutate_lesson)

    if CURRENT_SPRINT.exists():
        def mutate_sprint(meta: dict) -> None:
            if meta.get("status") in {"", "planned"}:
                meta["status"] = "active"
        update_note_frontmatter(CURRENT_SPRINT, mutate_sprint)

    from update_progress import main as refresh_progress

    refresh_progress()
    print(session_path)


if __name__ == "__main__":
    main()
