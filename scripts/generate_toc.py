#!/usr/bin/env python3
"""
Generate a table of contents for a book from processed chapters.

Creates an index.md file that links to all chapters and organizes them.

Usage:
    python3 scripts/generate_toc.py <book_id> <book_title> [output_dir]

Examples:
    python3 scripts/generate_toc.py my-book "My Book Title"
    python3 scripts/generate_toc.py my-book "My Book Title" output/my-book
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def extract_chapter_info(json_file: Path) -> dict | None:
    """Extract chapter info from intermediate JSON file."""
    try:
        data = json.loads(json_file.read_text(encoding="utf-8"))
        return {
            "number": data.get("chapter_number"),
            "title": data.get("chapter_title"),
            "summary": data.get("chapter_summary"),
            "key_ideas": data.get("key_ideas", []),
        }
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def sanitize_filename(s: str | None) -> str:
    """Turn a title into a safe filename slug. Falls back when title missing."""
    if not s:
        return "untitled"
    return "".join(c.lower() if c.isalnum() else "-" for c in s).strip("-")


def generate_toc(book_id: str, book_title: str, output_dir: Path) -> bool:
    """Generate a table of contents for the book."""
    intermediate_dir = Path("intermediate") / book_id

    if not intermediate_dir.exists():
        print(f"❌ No chapters found in {intermediate_dir}")
        return False

    # Find all chapter JSON files
    chapter_files = sorted(intermediate_dir.glob("chapter-*.json"))
    if not chapter_files:
        print(f"❌ No chapter files found in {intermediate_dir}")
        return False

    # Extract chapter info
    chapters = []
    for json_file in chapter_files:
        info = extract_chapter_info(json_file)
        if info:
            chapters.append(info)

    if not chapters:
        print("Could not extract chapter information")
        return False

    # Build TOC content
    toc_lines = [
        "---",
        f"book_id: {book_id}",
        f"book_title: {book_title}",
        "type: toc",
        f"generated: {datetime.now().isoformat()}",
        "---",
        "",
        f"# {book_title}",
        "",
        "## Table of Contents",
        "",
    ]

    # Add chapter links
    for ch in chapters:
        ch_num = ch.get("number") or 0
        title = ch.get("title") or "Untitled Chapter"
        slug = sanitize_filename(title)
        ch_link = f"ch{int(ch_num):02d}-{slug}"

        toc_lines.append(f"### Chapter {int(ch_num)}: {title}")
        toc_lines.append(f"[[{ch_link}]]")
        toc_lines.append("")

        if ch.get("summary"):
            # Add first 160 chars of summary for more context, trimmed
            summary = (ch["summary"] or "")[:160].rstrip()
            if summary:
                toc_lines.append(f"*{summary}…*")
                toc_lines.append("")

    # Add concepts index
    toc_lines.append("---")
    toc_lines.append("")
    toc_lines.append("## Key Concepts")
    toc_lines.append("")

    # Collect all key ideas across chapters
    all_ideas = _collect_ideas(chapters)

    for idea in sorted(all_ideas.keys(), key=lambda s: s.lower()):
        ch_num = all_ideas[idea]
        toc_lines.append(f"- {idea} (Chapter {int(ch_num)})")

    toc_lines.append("")

    # Write TOC file
    output_dir.mkdir(parents=True, exist_ok=True)
    toc_file = output_dir / "toc.md"
    toc_file.write_text("\n".join(toc_lines), encoding="utf-8")

    print(f"✅ Generated table of contents: {toc_file}")
    print(f"   Chapters: {len(chapters)}")
    print(f"   Key concepts: {len(all_ideas)}")

    return True


def _collect_ideas(chapters: list[dict]) -> dict:
    """Collect all unique key ideas from chapters."""
    all_ideas = {}
    for ch in chapters:
        for idea in ch.get("key_ideas", []):
            if idea not in all_ideas:
                all_ideas[idea] = ch["number"]
    return all_ideas


def main():
    if len(sys.argv) < 3:
        print("Usage: generate_toc.py <book_id> <book_title> [output_dir]")
        print("")
        print("Examples:")
        print('  python3 scripts/generate_toc.py my-book "My Book Title"')
        print(
            '  python3 scripts/generate_toc.py my-book "My Book Title" output/my-book'
        )
        sys.exit(1)

    book_id = sys.argv[1]
    book_title = sys.argv[2]
    output_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("output") / book_id

    success = generate_toc(book_id, book_title, output_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
