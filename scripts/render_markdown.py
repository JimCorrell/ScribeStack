#!/usr/bin/env python3
import json
import sys
import re
from pathlib import Path
from datetime import datetime


def sanitize_filename(s: str) -> str:
    """Turn a title/id into a safe Obsidian filename slug."""
    return "".join(c.lower() if c.isalnum() else "-" for c in s).strip("-")


def build_atomic_index(atomic_notes):
    """
    Build a mapping:
      - atomic note id           -> slug
      - atomic note title        -> slug
      - each related_term string -> slug

    So that we can link by human names like "CTO" or "First 100 Days".
    """
    index = {}
    for note in atomic_notes:
        slug = sanitize_filename(note.get("id") or note.get("title", ""))
        note_id = note.get("id")
        title = note.get("title")
        related_terms = note.get("related_terms", [])

        if note_id:
            index[note_id] = slug
        if title:
            index[title] = slug

        for rt in related_terms:
            if rt:
                index[rt] = slug

    return index


def link_text_with_atomic_terms(text: str, atomic_index: dict) -> str:
    """
    Given a block of text and an atomic_index mapping
      name_or_id_or_related_term -> slug
    wrap occurrences of those names in [[slug|Name]].

    - Sort terms by length desc to avoid partial overlaps.
    - Use word boundaries to reduce false positives.
    """
    if not text or not atomic_index:
        return text

    terms = list(atomic_index.keys())
    terms = sorted(set(terms), key=len, reverse=True)

    result = text

    for term in terms:
        if not term or term.isspace():
            continue
        if len(term) < 3:
            # avoid turning every tiny word into a link
            continue

        slug = atomic_index[term]
        escaped = re.escape(term)
        pattern = r"\b(" + escaped + r")\b"

        def repl(match):
            word = match.group(1)
            return f"[[{slug}|{word}]]"

        result = re.sub(pattern, repl, result)

    return result


def render_chapter_md(data: dict, atomic_index: dict) -> str:
    book_id = data["book_id"]
    book_title = data["book_title"]
    ch_num = data["chapter_number"]
    ch_title = data["chapter_title"]

    lines = []
    lines.append("---")
    lines.append(f'title: "{book_title} - Chapter {ch_num}: {ch_title}"')
    lines.append(f"book_id: {book_id}")
    lines.append(f"chapter_number: {ch_num}")
    lines.append("tags:")
    lines.append("  - textbook")
    lines.append("  - technical")
    lines.append("---")
    lines.append("")

    # Summary – clickable index
    lines.append("# Summary")
    summary = data["chapter_summary"]
    linked_summary = link_text_with_atomic_terms(summary, atomic_index)
    lines.append(linked_summary)
    lines.append("")

    # Key Ideas – auto-link
    lines.append("# Key Ideas")
    for idea in data.get("key_ideas", []):
        linked_idea = link_text_with_atomic_terms(idea, atomic_index)
        lines.append(f"- {linked_idea}")
    lines.append("")

    # Key Terms – heading itself links to atomic if we can find a match
    lines.append("# Key Terms")
    for term in data.get("key_terms", []):
        term_name = term["term"]
        # first try direct mapping (e.g., "CTO", "First 100 Days")
        slug = atomic_index.get(term_name)
        heading = term_name
        if slug:
            heading = f"[[{slug}|{term_name}]]"
        lines.append(f"## {heading}")
        lines.append(term["definition"])
        lines.append("")
    lines.append("")

    # Sections – we lightly auto-link section bullet points too
    lines.append("# Sections")
    for sec in data.get("sections", []):
        lines.append(f"## {sec['title']}")
        lines.append(sec["summary"])
        lines.append("")
        for bp in sec.get("bullet_points", []):
            linked_bp = link_text_with_atomic_terms(bp, atomic_index)
            lines.append(f"- {linked_bp}")
        lines.append("")
    lines.append("")

    # Diagrams (unchanged)
    lines.append("# Diagrams")
    for diag in data.get("diagrams", []):
        lines.append(f"## {diag['title']}")
        lines.append(diag["description"])
        lines.append("")
        primary = diag.get("primary_format", "mermaid")
        mermaid = diag.get("mermaid_code", "").strip()
        ascii_art = diag.get("ascii_art", "").strip()

        if primary == "mermaid" and mermaid:
            lines.append("```mermaid")
            lines.append(mermaid)
            lines.append("```")
        elif primary == "ascii" and ascii_art:
            lines.append("```text")
            lines.append(ascii_art)
            lines.append("```")
        else:
            if mermaid:
                lines.append("```mermaid")
                lines.append(mermaid)
                lines.append("```")
            if ascii_art:
                lines.append("```text")
                lines.append(ascii_art)
                lines.append("```")
        lines.append("")
    lines.append("")

    # Atomic Notes index – one link per atomic note
    lines.append("# Atomic Notes (Index)")
    for note in data.get("atomic_notes", []):
        slug = sanitize_filename(note.get("id") or note.get("title", ""))
        lines.append(f"- [[{slug}]]")
    lines.append("")

    return "\n".join(lines)


def render_atomic_md(data: dict, note: dict, atomic_index: dict) -> str:
    book_id = data["book_id"]
    ch_num = data["chapter_number"]
    ch_title = data["chapter_title"]

    note_id = note["id"]
    title = note["title"]
    summary = note["summary"]
    details = note["details"]
    related_terms = note.get("related_terms", [])

    today = datetime.today().strftime("%Y-%m-%d")
    chapter_slug = f"ch{ch_num:02d}-{sanitize_filename(ch_title)}"

    lines = []
    lines.append("---")
    lines.append(f'title: "{title}"')
    lines.append(f"book_id: {book_id}")
    lines.append(f"chapter_number: {ch_num}")
    lines.append(f'origin_chapter_title: "{ch_title}"')
    lines.append(f"note_id: {note_id}")
    lines.append(f"created: {today}")
    lines.append("tags:")
    lines.append("  - textbook")
    lines.append("  - atomic-note")
    lines.append("---")
    lines.append("")

    lines.append("# Summary")
    lines.append(summary)
    lines.append("")

    lines.append("# Details")
    lines.append(details)
    lines.append("")

    # Related Terms / Concepts – now link via the same index
    if related_terms:
        lines.append("# Related Terms / Concepts")
        for rt in related_terms:
            slug = atomic_index.get(rt)
            if slug:
                lines.append(f"- [[{slug}|{rt}]]")
            else:
                lines.append(f"- {rt}")
        lines.append("")

    # Backlink to chapter
    lines.append("# Source")
    lines.append(f"- [[{chapter_slug}]]")
    lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 3:
        print("Usage: render_markdown.py <book_id> <chapter_json_path>")
        sys.exit(1)

    book_id = sys.argv[1]
    json_path = Path(sys.argv[2])
    data = json.loads(json_path.read_text(encoding="utf-8"))

    out_base = Path("output") / book_id
    chapter_dir = out_base / "chapters"
    atomic_dir = out_base / "atomic"
    chapter_dir.mkdir(parents=True, exist_ok=True)
    atomic_dir.mkdir(parents=True, exist_ok=True)

    atomic_notes = data.get("atomic_notes", [])
    atomic_index = build_atomic_index(atomic_notes)

    # Chapter note
    ch_num = data["chapter_number"]
    ch_title = data["chapter_title"]
    chapter_fname = f"ch{ch_num:02d}-{sanitize_filename(ch_title)}.md"
    chapter_md = render_chapter_md(data, atomic_index)
    (chapter_dir / chapter_fname).write_text(chapter_md, encoding="utf-8")
    print(f"Wrote chapter note: {chapter_dir / chapter_fname}")

    # Atomic notes
    for note in atomic_notes:
        fname = sanitize_filename(note.get("id") or note.get("title", "")) + ".md"
        atomic_md = render_atomic_md(data, note, atomic_index)
        (atomic_dir / fname).write_text(atomic_md, encoding="utf-8")
        print(f"Wrote atomic note: {atomic_dir / fname}")


if __name__ == "__main__":
    main()
