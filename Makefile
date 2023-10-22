.PHONY: init clean build install dev-init

VENV_DIR = .venv

init:
	python3 -m venv $(VENV_DIR)
	poetry install

venv:
	. $(VENV_DIR)/bin/activate

build: venv
	$(VENV_DIR)/bin/python3 build_pitch_control.py build_ext --inplace

install: init build

install-dev: install
	$(VENV_DIR)/bin/pre-commit install

clean:
	rm -rf .venv
	find . -type f \( -name "*.so" -o -name "*.pyc" -o -name "*.pyo" -o -name "*.c" -o -name "*.cpp" \) -not -path "./pitch_control/Player.cpp" -exec rm -f {} +
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf build
