VENV = venv
BIN = $(VENV)/bin
POETRY = $(BIN)/poetry
BUILD = $(BIN)/python -m build

.PHONY: all venv install lint linst-strict clean

all: install

$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	$(BIN)/pip install poetry

# create if doesnt exist and activate venv
venv: $(VENV)/bin/activate

# install dependencies reading from pyproject.toml or poetry.lock
install: venv
	$(POETRY) install

run: install
	$(BIN)/python3 fly_in.py map.txt

debug: install
	$(BIN)/python3 -m pdb fly_in.py map.txt

build: install
	$(POETRY) run python -m build

# run mypy . with the flags ate pyproject.toml
lint: install
	$(POETRY) run flake8 . --exclude '$(VENV)'
	$(POETRY) run mypy .

# run mypy with the flags and --strict mode
lint-strict: install
	$(POETRY) run flake8 . --exclude '$(VENV)'
	$(POETRY) run mypy . --strict

clean:
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

fclean: clean
	rm -rf $(VENV)
