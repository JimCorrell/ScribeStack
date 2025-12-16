#!/usr/bin/env python3
"""
Batch process all chapters in a book.

Usage:
    python3 scripts/batch_process.py <book_id> <book_title> [start_ch] [end_ch]

Examples:
    # Process all chapters 01-10
    python3 scripts/batch_process.py my-book "My Book Title" 01 10

    # Process chapters 05-15
    python3 scripts/batch_process.py my-book "My Book Title" 05 15

    # Process all chapters found in input/my-book/
    python3 scripts/batch_process.py my-book "My Book Title"
"""

import os
import sys
import subprocess
from pathlib import Path


def find_chapters(book_id: str) -> list[int]:
    """Find all chapter files in input/<book_id>/ and return their numbers."""
    input_dir = Path("input") / book_id

    if not input_dir.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return []

    chapters = []
    for file in sorted(input_dir.glob("chapter-*.txt")):
        try:
            # Extract chapter number from filename (e.g., "chapter-01.txt" -> 1)
            ch_num = int(file.stem.split("-")[1])
            chapters.append(ch_num)
        except (ValueError, IndexError):
            continue

    return chapters


def process_chapter(book_id: str, book_title: str, ch_num: int) -> bool:
    """Process a single chapter using make."""
    ch_num_str = f"{ch_num:02d}"
    print(f"\n📖 Processing chapter {ch_num_str}...", flush=True)

    cmd = [
        "make",
        f"BOOK_ID={book_id}",
        f"BOOK_TITLE={book_title}",
        f"CH_NUM={ch_num_str}",
        "chapter-all",
    ]

    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    if len(sys.argv) < 3:
        print("Usage: batch_process.py <book_id> <book_title> [start_ch] [end_ch]")
        print("")
        print("Examples:")
        print('  python3 scripts/batch_process.py my-book "My Book Title"')
        print('  python3 scripts/batch_process.py my-book "My Book Title" 01 10')
        print('  python3 scripts/batch_process.py my-book "My Book Title" 05 15')
        sys.exit(1)

    book_id = sys.argv[1]
    book_title = sys.argv[2]

    # Determine chapter range
    if len(sys.argv) == 5:
        # User specified start and end
        start_ch = int(sys.argv[3])
        end_ch = int(sys.argv[4])
        chapters = list(range(start_ch, end_ch + 1))
    elif len(sys.argv) == 3:
        # Auto-detect from filesystem
        chapters = find_chapters(book_id)
        if not chapters:
            print(f"❌ No chapters found in input/{book_id}/")
            sys.exit(1)
    else:
        print("❌ Invalid arguments")
        sys.exit(1)

    print(f"📚 Batch Processing: {book_title}")
    print(f"📁 Book ID: {book_id}")
    print(f"📋 Chapters: {chapters[0]:02d} - {chapters[-1]:02d}")
    print(f"📊 Total chapters: {len(chapters)}")
    print("-" * 50)

    success_count = 0
    failed_chapters = []

    for i, ch_num in enumerate(chapters, 1):
        print(f"[{i}/{len(chapters)}]", end=" ")
        if process_chapter(book_id, book_title, ch_num):
            success_count += 1
        else:
            failed_chapters.append(f"{ch_num:02d}")

    print("\n" + "-" * 50)
    print(f"✅ Completed: {success_count}/{len(chapters)} chapters")

    if failed_chapters:
        print(f"❌ Failed chapters: {', '.join(failed_chapters)}")
        print("\nRe-run failed chapters individually:")
        for ch_num in failed_chapters:
            print(
                f'  make BOOK_ID={book_id} BOOK_TITLE="{book_title}" CH_NUM={ch_num} chapter-all'
            )
        sys.exit(1)
    else:
        print("🎉 All chapters processed successfully!")
        print(f"\nNotes are in: output/{book_id}/")
        sys.exit(0)


if __name__ == "__main__":
    main()
