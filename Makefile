VENV = venv
BIN = $(VENV)/bin
PYTHON = $(BIN)/python
PIP = $(BIN)/pip

.PHONY: all venv install run debug lint lint-strict clean fclean

all: install

$(VENV)/bin/activate:
	python3 -m venv $(VENV)

venv: $(VENV)/bin/activate

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run: install
	$(PYTHON) main.py maps/easy/01_linear_path.txt

debug: install
	$(PYTHON) -m pdb main.py maps/easy/01_linear_path.txt

lint: install
	$(PYTHON) -m flake8 . --exclude '$(VENV)'
	$(PYTHON) -m mypy .

lint-strict: install
	$(PYTHON) -m flake8 . --exclude '$(VENV)'
	$(PYTHON) -m mypy . --strict

clean:
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

fclean: clean
	rm -rf $(VENV)
