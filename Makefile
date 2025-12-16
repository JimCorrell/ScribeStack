PYTHON := python3

BOOK_ID ?= example-book
BOOK_TITLE ?= "Example Textbook"
START_CH ?= 01
END_CH ?= 01
EPUB_FILE ?=

INPUT_DIR := input/$(BOOK_ID)
INTERMEDIATE_DIR := intermediate/$(BOOK_ID)
OUTPUT_DIR := output/$(BOOK_ID)

CH_NUM ?= 01
CH_FILE := $(INPUT_DIR)/chapter-$(CH_NUM).txt
JSON_FILE := $(INTERMEDIATE_DIR)/chapter-$(CH_NUM).json

.PHONY: chapter-json chapter-md chapter-all dirs batch-all batch-range toc extract-epub

dirs:
	@mkdir -p $(INPUT_DIR) $(INTERMEDIATE_DIR) $(OUTPUT_DIR)

chapter-json: dirs
	$(PYTHON) scripts/summarize_chapter.py $(BOOK_ID) "$(BOOK_TITLE)" $(CH_NUM) $(CH_FILE)

chapter-md: dirs
	$(PYTHON) scripts/render_markdown.py $(BOOK_ID) $(JSON_FILE)

chapter-all: chapter-json chapter-md
	@echo "Completed pipeline for chapter $(CH_NUM) of $(BOOK_ID)."

batch-all:
	@$(PYTHON) scripts/batch_process.py $(BOOK_ID) "$(BOOK_TITLE)"

batch-range:
	@$(PYTHON) scripts/batch_process.py $(BOOK_ID) "$(BOOK_TITLE)" $(START_CH) $(END_CH)

toc:
	@$(PYTHON) scripts/generate_toc.py $(BOOK_ID) "$(BOOK_TITLE)" $(OUTPUT_DIR)

extract-epub:
	@if [ -z "$(EPUB_FILE)" ]; then \
		echo "❌ EPUB_FILE not specified"; \
		echo "Usage: make EPUB_FILE=path/to/book.epub BOOK_ID=my-book extract-epub"; \
		exit 1; \
	fi
	@$(PYTHON) scripts/extract_epub.py "$(EPUB_FILE)" $(BOOK_ID)

.PHONY: help

help:
	@echo "ScribeStack — Convert textbook chapters to Obsidian-ready notes"
	@echo ""
	@echo "Usage: make [target] BOOK_ID=<id> BOOK_TITLE=\"<title>\" [options]"
	@echo ""
	@echo "Targets:"
	@echo "  extract-epub   Extract chapters from EPUB (requires EPUB_FILE=path/to/book.epub)"
	@echo "  chapter-all    Process a single chapter (requires CH_NUM=XX)"
	@echo "  batch-all      Process all chapters in input/<book_id>/"
	@echo "  batch-range    Process chapters (requires START_CH=XX END_CH=XX)"
	@echo "  toc            Generate table of contents (index.md)"
	@echo ""
	@echo "Examples:"
	@echo "  make EPUB_FILE=\"My Book.epub\" BOOK_ID=my-book extract-epub"
	@echo "  make BOOK_ID=my-book BOOK_TITLE=\"My Book\" batch-all"
	@echo "  make BOOK_ID=my-book BOOK_TITLE=\"My Book\" toc"
	@echo ""
	@echo ""
	@echo "More info: See README.md"

.PHONY: book-index

book-index:
	$(PYTHON) scripts/generate_book_index.py $(BOOK_ID)
