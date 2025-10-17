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
define bump_py =
import sys
M,m,p = map(int, open("VERSION").read().strip().split("."))
t = sys.argv[1]
if t == "patch": p += 1
elif t == "minor": m, p = m + 1, 0
elif t == "major": M, m, p = M + 1, 0
print(f"{M}.{m}.{p}")
endef

.PHONY: show-version bump-patch bump-minor bump-major

show-version:
	@echo Current version: && type "$(VERSION_FILE)"

bump-patch:
	@$(PY) - <<'PY'\n$(bump_py)\nPY patch > .VERSION.new && move /Y .VERSION.new "$(VERSION_FILE)"
	@git add "$(VERSION_FILE)" && git commit -m "bump: patch" || echo "(nothing to commit)"

bump-minor:
	@$(PY) - <<'PY'\n$(bump_py)\nPY minor > .VERSION.new && move /Y .VERSION.new "$(VERSION_FILE)"
	@git add "$(VERSION_FILE)" && git commit -m "bump: minor" || echo "(nothing to commit)"

bump-major:
	@$(PY) - <<'PY'\n$(bump_py)\nPY major > .VERSION.new && move /Y .VERSION.new "$(VERSION_FILE)"
	@git add "$(VERSION_FILE)" && git commit -m "bump: major" || echo "(nothing to commit)"

# ---- Tag & push release ----
.PHONY: release
release: build
	@echo Tagging release...
	@set /p VER=<"$(VERSION_FILE)"
	git tag v%VER%
	git push --tags
	@echo ✅ Tagged and pushed version v%VER%
