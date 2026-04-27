PYTHON = python3
NAME = main.py
ARGS ?= maps/hard/03_ultimate_challenge.txt

all: run

install:
	python -m pip install flake8 mypy pygame

run:
	$(PYTHON) $(NAME) $(ARGS)

debug:
	$(PYTHON) -m pdb $(NAME) $(ARGS)

clean:
	rm -rf Backend/__pycache__ Frontend/__pycache__ .mypy_cache

lint:
	$(PYTHON) -m flake8 . --exclude=env
	$(PYTHON) -m mypy . \
	--exclude env \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

.PHONY: all install run debug lint clean
