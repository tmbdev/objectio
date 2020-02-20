#!/bin/bash

package: tests docs testdist

dist: FORCE
	. ./venv/bin/activate; python3 setup.py sdist bdist_wheel
	twine upload dist/*

tests: venv
	rm -f objio.yaml objio.yml
	. ./venv/bin/activate; python3 -m pytest

venv: FORCE
	test -d venv || python3 -m venv venv
	. ./venv/bin/activate; python3 -m pip install --no-cache -r requirements.dev.txt
	. ./venv/bin/activate; python3 -m pip install --no-cache -r requirements.txt

docs: FORCE
	./gendocs

clean: FORCE
	rm -rf venv

passwd: FORCE
	. ./venv/bin/activate; python3 -m keyring set https://upload.pypi.org/legacy/ tmbdev

FORCE:
