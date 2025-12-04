#!/usr/bin/env python3
import sys
from pathlib import Path


def parse_title_from_frontmatter(path: Path) -> str:
    """
    Read a Markdown file and pull the `title:` field from frontmatter.
    Fallback: use the filename stem.
    """
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return path.stem

    in_frontmatter = False
    for line in lines:
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
            else:
                break
            continue
        if in_frontmatter and line.startswith("title:"):
            # title: "Something"
            value = line.split(":", 1)[1].strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            return value
    return path.stem


def main():
    if len(sys.argv) < 2:
        print("Usage: generate_book_index.py <book_id>")
        sys.exit(1)

    book_id = sys.argv[1]
    out_base = Path("output") / book_id
    chapter_dir = out_base / "chapters"
    atomic_dir = out_base / "atomic"

    if not chapter_dir.exists():
        print(f"No chapters directory found for book_id={book_id} at {chapter_dir}")
        sys.exit(1)

    chapters = sorted(chapter_dir.glob("*.md"))
    atomics = sorted(atomic_dir.glob("*.md")) if atomic_dir.exists() else []

    lines = []
    lines.append("---")
    lines.append(f'title: "Book Index - {book_id}"')
    lines.append(f"book_id: {book_id}")
    lines.append("tags:")
    lines.append("  - textbook")
    lines.append("  - index")
    lines.append("---")
    lines.append("")

    lines.append("# Chapters")
    for ch in chapters:
        note_name = ch.stem  # filename without .md
        display_title = parse_title_from_frontmatter(ch)
        lines.append(f"- [[{note_name}|{display_title}]]")
    lines.append("")

    if atomics:
        lines.append("# Atomic Notes")
        for an in atomics:
            note_name = an.stem
            display_title = parse_title_from_frontmatter(an)
            lines.append(f"- [[{note_name}|{display_title}]]")
        lines.append("")

    # Optional Dataview section
    lines.append("# Dataview: Atomic Notes Table")
    lines.append("```dataview")
    lines.append("TABLE chapter_number, book_id, created")
    lines.append('FROM ""')
    lines.append('WHERE contains(file.tags, "atomic-note") and book_id = this.book_id')
    lines.append("SORT chapter_number asc")
    lines.append("```")
    lines.append("")

    index_path = out_base / "index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote book index: {index_path}")


if __name__ == "__main__":
    main()
