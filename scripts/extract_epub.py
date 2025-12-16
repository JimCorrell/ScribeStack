#!/usr/bin/env python3
"""
Extract chapters from EPUB files into individual text files.

Uses the EPUB's table of contents to identify chapters and saves each as
a separate file in input/<book_id>/

Usage:
    python3 scripts/extract_epub.py <epub_path> <book_id>

Examples:
    python3 scripts/extract_epub.py "My Book.epub" my-book
    python3 scripts/extract_epub.py "/path/to/book.epub" my-textbook
"""

import sys
import re
from pathlib import Path
from html.parser import HTMLParser

try:
    import ebooklib
    from ebooklib import epub
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ Required packages not found. Install them with:")
    print("   pip install ebooklib beautifulsoup4")
    sys.exit(1)


class TextExtractor(HTMLParser):
    """Extract plain text from HTML."""

    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = False

    def handle_data(self, data):
        if not self.skip:
            text = data.strip()
            if text:
                self.text.append(text)

    def get_text(self):
        return "\n".join(self.text)


def extract_text_from_html(html_content: str) -> str:
    """Extract plain text from HTML content."""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        # Remove script and style tags
        for tag in soup(["script", "style"]):
            tag.decompose()
        # Get text
        text = soup.get_text(separator="\n")
        # Clean up whitespace
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(line for line in lines if line)
        return text
    except Exception:
        # Fallback to simple regex
        text = re.sub(r"<[^>]+>", "", html_content)
        text = re.sub(r"\s+", " ", text)
        return text


def get_epub_chapters(epub_path: Path) -> list[tuple[str, str]]:
    """Extract chapters from EPUB file, filtering front/back matter.

    Returns list of (chapter_title, html_content) tuples.
    """
    try:
        book = epub.read_epub(str(epub_path))
    except Exception as e:
        print(f"❌ Error reading EPUB: {e}")
        return []

    # Prefer files that look like real chapters (e.g., ch01.htm) from all documents
    all_docs = _extract_all_documents(book)
    chapter_like = [
        (title, html, name)
        for title, html, name in all_docs
        if re.search(r"ch\d+", name.lower())
    ]

    chapters = [(t, h) for t, h, _ in sorted(chapter_like, key=lambda x: x[2])]

    # Fallback to ToC-based extraction if no chapter-like files were found
    if not chapters:
        chapters = _extract_from_toc(book)
    # Last resort: use all documents
    if not chapters:
        chapters = [(t, h) for t, h, _ in all_docs]

    # Filter front/back matter using title and early content hints
    def is_front_or_back_matter(title: str, html: str) -> bool:
        t = (title or "").strip().lower()
        sample = extract_text_from_html(html)[:500].lower()
        keywords = [
            "copyright",
            "inside front cover",
            "inside back cover",
            "front matter",
            "back matter",
            "brief contents",
            "contents",
            "table of contents",
            "acknowledgments",
            "acknowledgements",
            "preface",
            "foreword",
            "index",
            "about the author",
            "references",
            "glossary",
        ]
        for kw in keywords:
            # Exact title match or title contains the keyword
            if t == kw or kw in t:
                return True
        content_hints = [
            "all rights reserved",
            "isbn",
            "no part of this",
            "printed in",
            "copyright",
            "table of contents",
            "index",
        ]
        for kw in content_hints:
            if kw in sample:
                return True
        return False

    filtered = []
    for title, html in chapters:
        if is_front_or_back_matter(title, html):
            continue
        text_preview = extract_text_from_html(html)
        if len(text_preview.split()) < 200:
            # Skip very short sections
            continue
        filtered.append((title, html))

    # If filtering removes everything, fall back to longest documents.
    if filtered:
        return filtered

    # Secondary fallback: pick top 10 longest documents that are not flagged by keywords.
    scored = []
    for title, html in chapters:
        text_preview = extract_text_from_html(html)
        words = len(text_preview.split())
        if is_front_or_back_matter(title, html):
            continue
        scored.append((words, title, html))
    scored.sort(reverse=True)

    if scored:
        return [(t, h) for _, t, h in scored[:10]]

    # Last resort: take top 10 longest regardless of keywords to avoid empty output
    longest = []
    for title, html in chapters:
        words = len(extract_text_from_html(html).split())
        longest.append((words, title, html))
    longest.sort(reverse=True)
    return [(t, h) for _, t, h in longest[:10]]


def _flatten_toc_items(book, items):
    """Yield (title, content) for all document links in a (possibly nested) ToC."""
    for item in items:
        try:
            if isinstance(item, epub.Section):
                yield from _flatten_toc_items(book, item.subitems)
            else:
                chapter = book.get_item_with_href(item.href)
                if chapter and chapter.get_type() == ebooklib.ITEM_DOCUMENT:
                    title = item.title
                    content = chapter.content.decode("utf-8")
                    yield (title, content)
        except Exception:
            continue


def _extract_from_toc(book) -> list[tuple[str, str]]:
    """Extract chapters using EPUB table of contents, descending into nested sections."""
    try:
        toc = getattr(book, "toc", None)
        if toc:
            return list(_flatten_toc_items(book, toc))
    except Exception:
        return []
    return []


def _extract_all_documents(book) -> list[tuple[str, str, str]]:
    """Fallback: extract all document items from EPUB."""
    chapters = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            try:
                name = item.get_name()
                title = (
                    getattr(item, "title", None)
                    or name
                    or f"Chapter {len(chapters) + 1}"
                )
                content = item.content.decode("utf-8")
                chapters.append((title, content, name))
            except Exception:
                continue
    return chapters


def sanitize_title(title: str) -> str:
    """Clean up chapter titles."""
    # Remove common prefixes
    title = re.sub(r"^Chapter\s+\d+[:\s]+", "", title, flags=re.IGNORECASE)
    title = title.strip()
    return title if title else "Untitled"


def main():
    if len(sys.argv) < 3:
        print("Usage: extract_epub.py <epub_path> <book_id>")
        print("")
        print("Examples:")
        print('  python3 scripts/extract_epub.py "My Book.epub" my-book')
        print("  python3 scripts/extract_epub.py /path/to/book.epub my-textbook")
        sys.exit(1)

    epub_path = Path(sys.argv[1])
    book_id = sys.argv[2]

    if not epub_path.exists():
        print(f"❌ EPUB file not found: {epub_path}")
        sys.exit(1)

    print(f"📚 Extracting chapters from: {epub_path.name}")
    print(f"📁 Book ID: {book_id}")
    print("-" * 50)

    # Extract chapters
    chapters = get_epub_chapters(epub_path)

    if not chapters:
        print("❌ No chapters found in EPUB")
        sys.exit(1)

    print(f"📖 Found {len(chapters)} candidate content chapters (after filtering)")

    # Create output directory
    output_dir = Path("input") / book_id
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write chapter files (renumber starting at 01 for first real content)
    for i, (title, html_content) in enumerate(chapters, 1):
        ch_num = f"{i:02d}"
        ch_title = sanitize_title(title)

        # Extract text from HTML
        text_content = extract_text_from_html(html_content)

        # Skip very short chapters (likely navigation/metadata)
        if len(text_content.strip()) < 100:
            print(f"   ⏭️  Skipping chapter {ch_num} (too short): {ch_title}")
            continue

        # Write chapter file
        ch_file = output_dir / f"chapter-{ch_num}.txt"
        ch_file.write_text(text_content, encoding="utf-8")

        # Show progress
        word_count = len(text_content.split())
        print(f"   ✅ Chapter {ch_num}: {ch_title} ({word_count} words)")

    print("-" * 50)
    print(f"✅ Extracted chapters to: {output_dir}/")
    print("")
    print("Next steps:")
    print(f'  make BOOK_ID={book_id} BOOK_TITLE="Your Book Title" batch-all')
    print(f'  make BOOK_ID={book_id} BOOK_TITLE="Your Book Title" toc')


if __name__ == "__main__":
    main()
