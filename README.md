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

## Quick Start

### 1. Setup (one-time)

```bash
./setup.sh
```

This will:

- Create a Python virtual environment
- Install all dependencies
- Create a `.env` file for your API key

Then **edit `.env` and add your OpenAI API key**:

```bash
nano .env
```

### 2. Process a chapter

Create a directory for your book and add a chapter file:

```bash
mkdir -p input/my-book
# Add chapter-01.txt, chapter-02.txt, etc. to input/my-book/
```

Then run the pipeline:

```bash
make BOOK_ID=my-book BOOK_TITLE="My Textbook Title" CH_NUM=01 chapter-all
```

### 3. Check output

Your notes are in `output/my-book/`:

- `chapters/` — chapter summaries
- `atomic/` — individual concept notes (Zettelkasten-style)

---

## Requirements

- Python 3.8+
- An OpenAI API key (get one at [platform.openai.com/api-keys](https://platform.openai.com/api-keys))
- `pip` for installing dependencies

---

## Getting Help

View available commands anytime:

```bash
make help
```

---

## Configuration

Basic configuration lives in `config.yaml`:

```yaml
default_model: "gpt-4o-mini"
```

You can extend this file to include per-book config later if you wish.

---

## Usage

### Complete Workflow Example

Here's a typical workflow for processing a full textbook from an EPUB file:

```bash
# 1. Set up once
./setup.sh
nano .env  # Add your API key

# 2. Extract chapters from EPUB
make EPUB_FILE="My Textbook.epub" BOOK_ID=my-textbook extract-epub

# 3. Process all chapters with AI
make BOOK_ID=my-textbook BOOK_TITLE="My Textbook" batch-all

# 4. Generate a table of contents
make BOOK_ID=my-textbook BOOK_TITLE="My Textbook" toc

# 5. Import into Obsidian
open output/my-textbook/index.md  # macOS
# or: xdg-open output/my-textbook/index.md  # Linux
# Then copy output/my-textbook/ into your Obsidian vault
```

### Processing from EPUB

The EPUB extractor automatically:

- Reads the book's table of contents
- Extracts each chapter as plain text
- Saves to `input/<book_id>/chapter-XX.txt`
- Filters out navigation, metadata, and very short sections
- Shows progress and word count for each chapter

**Where to put your EPUB file:**

The EPUB file can be anywhere. Three common approaches:

1. **Project root (simplest)** — Copy or move the file to your ScribeStack folder:

   ```bash
   cp ~/Downloads/My\ Book.epub .
   make EPUB_FILE="My Book.epub" BOOK_ID=my-book extract-epub
   ```

2. **Downloads folder** — Use the full path:

   ```bash
   make EPUB_FILE="~/Downloads/My Book.epub" BOOK_ID=my-book extract-epub
   ```

3. **Organized in a folder** — Create a dedicated EPUB library:

   ```bash
   mkdir -p epub-library
   cp ~/Downloads/My\ Book.epub epub-library/
   make EPUB_FILE="epub-library/My Book.epub" BOOK_ID=my-book extract-epub
   ```

**Basic usage:**

```bash
# 2. Prepare your book
mkdir -p input/my-textbook
# Add chapter-01.txt, chapter-02.txt, ... to input/my-textbook/

# 3. Process all chapters
make BOOK_ID=my-textbook BOOK_TITLE="My Textbook" batch-all

# 4. Generate table of contents
make BOOK_ID=my-textbook BOOK_TITLE="My Textbook" toc

# 5. Review the output
open output/my-textbook/index.md  # macOS
# or: xdg-open output/my-textbook/index.md  # Linux
# or: start output/my-textbook/index.md  # Windows

# 6. Import into Obsidian
# Copy output/my-textbook/ into your Obsidian vault
```

### Basic Workflow

1. **Prepare your chapter text**

   **Option A: Extract from EPUB (recommended)**

   Automatically extract chapters from an EPUB file:

   ```bash
   make EPUB_FILE="My Book.epub" BOOK_ID=my-book extract-epub
   ```

   The extractor will automatically:

   - Read the EPUB's table of contents
   - Extract each chapter as plain text
   - Save to `input/my-book/chapter-XX.txt`
   - Skip navigation and metadata sections

   **Option B: Manual chapter files**

   Place plain-text chapter files in `input/<book_id>/`:

   ```bash
   mkdir -p input/my-book
   cp chapter-01.txt input/my-book/
   ```

2. **Process the chapter**

   ```bash
   make BOOK_ID=my-book BOOK_TITLE="My Book Title" CH_NUM=01 chapter-all
   ```

   This runs:

   - `summarize_chapter.py` — Calls OpenAI to create a structured JSON summary
   - `render_markdown.py` — Renders that JSON into Markdown notes

3. **Review the output**

   Check `output/my-book/` for:

   - `chapters/ch01-<title>.md` — Full chapter summary
   - `atomic/<concept>.md` — Individual concept notes

### Processing Multiple Chapters

#### Auto-detect all chapters

If you have chapters 01-10 in `input/my-book/`, process them all at once:

```bash
make BOOK_ID=my-book BOOK_TITLE="My Book Title" batch-all
```

#### Process a specific range

Process chapters 05-15:

```bash
make BOOK_ID=my-book BOOK_TITLE="My Book Title" START_CH=05 END_CH=15 batch-range
```

#### Generate a Table of Contents

After processing chapters, automatically create an index linking all chapters and key concepts:

```bash
make BOOK_ID=my-book BOOK_TITLE="My Book Title" toc
```

This generates `output/my-book/index.md` with:

- List of all chapters with links
- Chapter summaries
- Key concepts index organized by chapter

#### Manual loop (if you prefer)

```bash
for i in {01..10}; do
  make BOOK_ID=my-book BOOK_TITLE="My Book Title" CH_NUM=$i chapter-all
done
```

The batch processor will:

- Show progress as it processes each chapter
- Report which chapters succeeded/failed
- Suggest retry commands for any that failed
- Display the output directory when complete

- Show progress as it processes each chapter
- Report which chapters succeeded/failed
- Suggest retry commands for any that failed
- Display the output directory when complete

### Output Structure

Generated notes follow a consistent structure:

**Chapter Note** (`chapters/ch01-the-basics.md`):

```markdown
---
book_id: my-book
book_title: My Book Title
chapter_number: 1
chapter_title: The Basics
---

# The Basics

## Summary

[4-8 sentence overview]

## Key Ideas

- [Idea 1]
- [Idea 2]
  ...

## Key Terms

- **Term 1**: Definition
- **Term 2**: Definition
  ...

## Sections

[Detailed section breakdowns with summaries and bullet points]

## Diagrams

[Mermaid diagrams and ASCII art]
```

**Atomic Notes** (`atomic/my-concept.md`):

```markdown
---
atomic_id: my-concept
title: My Concept
related_terms:
  - Related Concept 1
  - Related Concept 2
backlinks: []
---

# My Concept

[Definition and explanation]

## Related Concepts

- [[related-concept-1]]
- [[related-concept-2]]
```

---

## Integrations

### Obsidian

ScribeStack outputs are **Obsidian-compatible out of the box**.

1. Create a new vault (or use existing)
2. Copy `output/<book_id>` into your vault
3. Notes will automatically link via `[[wiki-style-links]]`

**Best Practices**:

- Create a folder structure: `Books/<book_id>/chapters/` and `Books/<book_id>/atomic/`
- Use Obsidian's graph view to see concept connections
- Tag notes with `#book/<book_id>` for filtering

### Logseq

Logseq also supports markdown and wiki-links:

1. Copy notes to your Logseq `pages/` directory
2. Update frontmatter format if needed (Logseq uses `::`-style metadata)

### Dendron

Dendron's hierarchy support works well with ScribeStack:

1. Copy `output/<book_id>/` to `vault/<book_id>/`
2. Rename files to Dendron's `parent.child` convention if desired

---

## Understanding the Pipeline

### 1. Summarization (`summarize_chapter.py`)

Reads your chapter text and calls OpenAI to extract:

- Chapter title & summary
- Key ideas (3-5 main concepts)
- Key terms with definitions
- Sections with summaries and bullet points
- Diagrams (Mermaid preferred, ASCII fallback)
- Atomic notes (one per important concept)

Output: `intermediate/<book_id>/chapter-XX.json`

### 2. Rendering (`render_markdown.py`)

Converts the JSON into readable Markdown:

- Creates chapter summary note with metadata
- Creates individual atomic notes for each concept
- Auto-links related concepts using `[[wiki-links]]`
- Ensures consistent frontmatter and formatting

Output: `output/<book_id>/chapters/` and `output/<book_id>/atomic/`

---

## Customization

### Modify the Prompt

Edit `prompts/chapter_prompt.txt` to customize how the model processes chapters. For example:

- Add more specific instructions for your domain
- Request different types of diagrams
- Change the structure of atomic notes

Then re-run processing for new chapters.

### Change the Model

Edit `config.yaml`:

```yaml
default_model: "gpt-4" # Use a different model
```

Available models:

- `gpt-4o-mini` (recommended for cost)
- `gpt-4` (more capable, higher cost)
- `gpt-4-turbo` (fastest)

---

## Notes

- The model is instructed to output **only JSON**; formatting and Markdown layout
  are enforced by the renderer scripts. This keeps your note style consistent.
- Diagrams are Mermaid-first, with ASCII as a fallback.
- All notes use front matter for metadata (Obsidian-compatible).
- Wiki-style links (`[[concept]]`) are auto-generated for related concepts.

---

## Troubleshooting

### Error: "API key not found"

- Make sure `.env` has your OpenAI API key
- Run `source .venv/bin/activate` if using a new terminal

### Error: "The model does not exist"

- Check `config.yaml` has a valid model name
- Current default is `gpt-4o-mini`

### Notes don't link properly in Obsidian

- Make sure notes are in the same Obsidian vault
- Check file names match exactly (case-sensitive on macOS/Linux)

---

## Roadmap

- [x] Automatic EPUB chapter extraction
- [x] Batch processing for all chapters at once
- [x] Auto-generated book index/TOC
- [ ] PDF chapter extraction
- [ ] Per-book configuration in `config.yaml`
- [ ] Additional renderers (Confluence, HTML)
- [ ] Web interface for previewing notes
- [ ] Chapter similarity detection (combine duplicates)
