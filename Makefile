PYTHON := python3

BOOK_ID ?= example-book
BOOK_TITLE ?= "Example Textbook"

INPUT_DIR := input/$(BOOK_ID)
INTERMEDIATE_DIR := intermediate/$(BOOK_ID)
OUTPUT_DIR := output/$(BOOK_ID)

CH_NUM ?= 01
CH_FILE := $(INPUT_DIR)/chapter-$(CH_NUM).txt
JSON_FILE := $(INTERMEDIATE_DIR)/chapter-$(CH_NUM).json

.PHONY: chapter-json chapter-md chapter-all dirs

dirs:
	@mkdir -p $(INPUT_DIR) $(INTERMEDIATE_DIR) $(OUTPUT_DIR)

chapter-json: dirs
	$(PYTHON) scripts/summarize_chapter.py $(BOOK_ID) "$(BOOK_TITLE)" $(CH_NUM) $(CH_FILE)

chapter-md: dirs
	$(PYTHON) scripts/render_markdown.py $(BOOK_ID) $(JSON_FILE)

chapter-all: chapter-json chapter-md
	@echo "Completed pipeline for chapter $(CH_NUM) of $(BOOK_ID)."

.PHONY: book-index

book-index:
	$(PYTHON) scripts/generate_book_index.py $(BOOK_ID)
