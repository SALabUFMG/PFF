.ONESHELL:
.PHONY: init venv clean build install dev

VENV_DIR = .venv
VENV_BIN = $(VENV_DIR)/bin

install: init poetry-install build

init:
	python3 -m venv $(VENV_DIR)

venv:
	. $(VENV_BIN)/activate

poetry-install: venv
	pip install --upgrade pip
	pip install poetry
	poetry install

build: venv
	which python3
	python3 build_pitch_control.py build_ext --inplace

dev: install
	pre-commit install

clean:
	rm -rf $(VENV_DIR)
	find . -type f \( -name "*.so" -o -name "*.pyc" -o -name "*.pyo" -o -name "*.c" -o -name "*.cpp" \) -not -path "./pff/pitch_control/Player.cpp" -exec rm -f {} +
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf build
