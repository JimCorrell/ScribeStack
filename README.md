# ScribeStack

ScribeStack is a small developer-focused toolchain for turning textbook chapters
into clean, consistent Obsidian-ready Markdown notes.

It uses this basic pipeline:

1. **Input**: Plain-text chapter files (e.g., extracted from EPUB/PDF).
2. **Summarization**: A Python script calls an OpenAI model to convert the chapter
   into a structured JSON summary (chapter summary, key ideas, terms, diagrams,
   and atomic notes).
3. **Rendering**: Another Python script renders that JSON into:
   - A chapter summary note.
   - A set of atomic notes (Zettelkasten-style) for key concepts.
4. **Output**: Obsidian-ready `.md` files with consistent metadata and layout.

---

## Project Layout

```text
ScribeStack/
  README.md
  Makefile
  requirements.txt
  config.yaml
  .gitignore

  prompts/
    chapter_prompt.txt

  scripts/
    __init__.py
    summarize_chapter.py
    render_markdown.py

  input/
    example-book/
      chapter-01.txt

  intermediate/
    .gitkeep

  output/
    .gitkeep
```

- `input/` — raw chapter text files you provide.
- `intermediate/` — JSON summaries produced by the model.
- `output/` — final Markdown notes for Obsidian.
- `prompts/` — prompt templates used when calling the model.
- `scripts/` — Python tooling.

---

## Requirements

- Python 3.10+
- An OpenAI API key exported as `OPENAI_API_KEY`.
- `pip` for installing dependencies.

Install Python dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration

Basic configuration lives in `config.yaml`:

```yaml
default_model: "gpt-5.1-mini"
```

You can extend this file to include per-book config later if you wish.

---

## Usage

1. Place a chapter into `input/<book_id>/chapter-XX.txt`.

   Example provided:

   ```text
   input/example-book/chapter-01.txt
   ```

2. Run the Makefile target to summarize and render a chapter:

   ```bash
   make BOOK_ID=example-book BOOK_TITLE="Example Textbook" CH_NUM=01 chapter-all
   ```

   This will:
   - Call the model and write JSON to `intermediate/example-book/chapter-01.json`.
   - Render Markdown notes into `output/example-book/`.

3. Point Obsidian at `output/` (or copy that folder into your vault).

---

## Notes

- The model is instructed to output **only JSON**; formatting and Markdown layout
  are enforced by the renderer scripts. This keeps your note style consistent.
- Diagrams are Mermaid-first, with ASCII as a fallback.

---

## Roadmap Ideas

- Automatic EPUB/PDF chapter extraction.
- Per-book configuration in `config.yaml`.
- Batch processing for all chapters in a book.
- Additional renderers (e.g., Confluence Markdown, HTML).
