PYTHON = python3
NAME = main.py

all: run

install:
	pip install flake8 mypy

run:
	$(PYTHON) $(NAME)

debug:
	$(PYTHON) -m pdb $(NAME)

clean:
	rm -rf __pycache__ .mypy_cache

lint:
	$(PYTHON) -m flake8 . --exclude=env
	$(PYTHON) -m mypy . \
	--exclude env \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	-check-untyped-defs

.PHONY: all install run debug lint clean