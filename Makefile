#!/bin/bash

tests: virtualenv
	rm -f objio.yaml objio.yml
	. ./venv/bin/activate; python3 -m pytest

virtualenv: FORCE
	test -d venv || python3 -m venv venv
	. ./venv/bin/activate; python3 -m pip install --no-cache -r requirements.txt

docs: FORCE
	cp README.md docs/index.md
	jupyter nbconvert --to markdown notebooks/examples.ipynb
	mv notebooks/examples.md docs/examples.md
	pydocmd simple objio.io > docs/io.md
	./cmd2md obj > docs/obj.md
	#mkdocs build

clean: FORCE
	rm -rf venv

FORCE:
