#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import runpy
import shutil
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "public"


def source_rel(path: str) -> PurePosixPath:
    return PurePosixPath(path)


def public_rel_for(path: str) -> PurePosixPath:
    rel = source_rel(path)
    if rel.suffix == ".md":
        return rel.with_suffix(".html")
    return rel


def href_resolver_for(from_path: str):
    from_rel = public_rel_for(from_path)
    from_dir = from_rel.parent

    def final(target: str) -> str:
        target_rel = public_rel_for(target)
        start = str(from_dir) if str(from_dir) else "."
        return str(PurePosixPath(os.path.relpath(str(target_rel), start=start)))

    return final


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    update_ns = runpy.run_path(str(ROOT / "scripts" / "update_progress.py"))
    serve_ns = runpy.run_path(str(ROOT / "scripts" / "serve_dashboard.py"))

    # Refresh derived tracking files first.
    update_ns["main"]()
    notes = update_ns["load_notes"]()

    if PUBLIC_DIR.exists():
        shutil.rmtree(PUBLIC_DIR)
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    # Dashboard pages.
    tracking_index_html = update_ns["build_html_dashboard"](
        notes,
        href_resolver=href_resolver_for("tracking/index.html"),
        dashboard_title="周志昕的公开学习站",
    )
    write_text(PUBLIC_DIR / "tracking" / "index.html", tracking_index_html)

    root_index_html = update_ns["build_html_dashboard"](
        notes,
        href_resolver=href_resolver_for("index.html"),
        dashboard_title="周志昕的公开学习站",
    )
    write_text(PUBLIC_DIR / "index.html", root_index_html)

    # Export all markdown pages as html.
    for md_path in sorted(ROOT.rglob("*.md")):
        if PUBLIC_DIR in md_path.parents:
            continue
        rel = md_path.relative_to(ROOT)
        if any(part.startswith(".") for part in rel.parts):
            continue
        if rel.parts and rel.parts[0] == "templates":
            continue
        raw = md_path.read_text(encoding="utf-8")
        metadata, body = serve_ns["strip_frontmatter"](raw)
        title = metadata.get("title") or serve_ns["infer_title"](body, md_path.stem)
        body_html = serve_ns["render_markdown_body"](body, href_resolver_for(str(rel)))
        html_page = serve_ns["markdown_page"](
            title,
            str(rel),
            metadata,
            body_html,
            href_resolver=href_resolver_for(str(rel)),
            dashboard_title="周志昕的公开学习站",
        ).decode("utf-8")
        write_text(PUBLIC_DIR / public_rel_for(str(rel)), html_page)

    # Copy JSON data for optional future use.
    progress_json = ROOT / "tracking" / "progress.json"
    if progress_json.exists():
        write_text(PUBLIC_DIR / "tracking" / "progress.json", progress_json.read_text(encoding="utf-8"))

    # GitHub Pages compatibility.
    write_text(PUBLIC_DIR / ".nojekyll", "")

    summary = {
        "public_dir": str(PUBLIC_DIR),
        "index": str(PUBLIC_DIR / "index.html"),
        "tracking_index": str(PUBLIC_DIR / "tracking" / "index.html"),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
