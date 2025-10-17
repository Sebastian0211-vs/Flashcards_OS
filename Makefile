PY := python3
VENV := .venv
PIP := $(VENV)/bin/pip
RUN := $(VENV)/bin/python
REQ := build/requirements.txt
BUILD_SCRIPT := build/build.py

.PHONY: venv install build clean

venv:
	@test -d $(VENV) || $(PY) -m venv $(VENV)

install: venv
	$(PIP) install -U pip
	$(PIP) install -r $(REQ)

build: install
	$(RUN) $(BUILD_SCRIPT)

clean:
	rm -f os_theory.apkg
