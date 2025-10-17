# =============================
#  Flashcards_OS – Makefile
# =============================

# ---- Python / paths ----
PY := python
VENV := .venv
REQ := build/requirements.txt
BUILD_SCRIPT := build/build.py
VERSION_FILE := VERSION

# Default venv executables (Windows)
PIP := $(VENV)/Scripts/pip.exe
RUN := $(VENV)/Scripts/python.exe

# On Linux/WSL/macOS, switch to bin paths
ifeq ($(OS),Windows_NT)
	ACTIVATE := .$(VENV)/Scripts/activate
else
	PIP := $(VENV)/bin/pip
	RUN := $(VENV)/bin/python
	ACTIVATE := source $(VENV)/bin/activate
endif

# ---- Default target ----
.PHONY: all
all: build

# ---- Virtual environment ----
.PHONY: venv
venv:
	@if not exist "$(VENV)" ($(PY) -m venv "$(VENV)")

# ---- Dependencies ----
.PHONY: install
install: venv
	"$(RUN)" -m pip install -U pip
	"$(RUN)" -m pip install -r "$(REQ)"

# ---- Build deck ----
.PHONY: build
build: install
	"$(RUN)" "$(BUILD_SCRIPT)"

# ---- Clean ----
.PHONY: clean
clean:
	@if exist os_theory.apkg del /q os_theory.apkg
	@if exist os_theory-v*.apkg del /q os_theory-v*.apkg

# ---- Version bump helpers ----
.PHONY: show-version bump-patch bump-minor bump-major

show-version:
	@echo Current version: && type "$(VERSION_FILE)"

bump-patch:
	@echo Bumping patch version...
	"$(RUN)" build/bump_version.py patch > NUL
	git add "$(VERSION_FILE)"
	git commit -m "bump: patch" || echo (nothing to commit)

bump-minor:
	@echo Bumping minor version...
	"$(RUN)" build/bump_version.py minor > NUL
	git add "$(VERSION_FILE)"
	git commit -m "bump: minor" || echo (nothing to commit)

bump-major:
	@echo Bumping major version...
	"$(RUN)" build/bump_version.py major > NUL
	git add "$(VERSION_FILE)"
	git commit -m "bump: major" || echo (nothing to commit)

# ---- Tag & push release ----
.PHONY: release
release: build
	"$(RUN)" build/release_tag.py

