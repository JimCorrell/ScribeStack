#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()


def load_config():
    cfg_path = Path("config.yaml")
    if cfg_path.exists():
        return yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    return {"default_model": "gpt-5.1-mini"}


def load_prompt_template() -> str:
    prompt_path = Path("prompts") / "chapter_prompt.txt"
    return prompt_path.read_text(encoding="utf-8")


def summarize_chapter(
    book_id: str, book_title: str, chapter_number: int, chapter_path: Path
):
    config = load_config()
    model = config.get("default_model", "gpt-5.1-mini")
    client = OpenAI()

    prompt_template = load_prompt_template()
    chapter_text = chapter_path.read_text(encoding="utf-8")

    # Basic safeguard against extremely long chapters
    max_chars = 40_000
    if len(chapter_text) > max_chars:
        chapter_text = chapter_text[:max_chars]

    prompt = prompt_template.replace("{{CHAPTER_TEXT}}", chapter_text)

    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that outputs ONLY valid JSON objects.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content
    data = json.loads(content)

    # Enforce/override book_id, book_title, chapter_number
    data["book_id"] = book_id
    data["book_title"] = book_title
    data["chapter_number"] = int(chapter_number)

    # Basic validation
    required_fields = [
        "book_id",
        "book_title",
        "chapter_number",
        "chapter_title",
        "chapter_summary",
        "key_ideas",
        "key_terms",
        "sections",
        "diagrams",
        "atomic_notes",
    ]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field in model output: {field}")

    return data


def main():
    if len(sys.argv) < 5:
        print(
            "Usage: summarize_chapter.py <book_id> <book_title> <chapter_number> <chapter_path>"
        )
        sys.exit(1)

    book_id = sys.argv[1]
    book_title = sys.argv[2]
    chapter_number = int(sys.argv[3])
    chapter_path = Path(sys.argv[4])

    data = summarize_chapter(book_id, book_title, chapter_number, chapter_path)

    out_dir = Path("intermediate") / book_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"chapter-{chapter_number:0>2}.json"
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
