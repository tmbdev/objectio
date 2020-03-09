#!/bin/bash

VENV=venv
PYTHON3=$(VENV)/bin/python3
PIPOPT=--no-cache-dir
PIP=$(VENV)/bin/pip $(PIPOPT)
TEMP=objectio.yaml objectio.yml

test: venv FORCE
	rm -f $(TEMP)
	. ./venv/bin/activate; python3 -m pytest

containertest:
	./helpers/dockertest git

pypitest:
	./helpers/dockertest pip

venv: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt requirements.dev.txt
	test -d $(VENV) || python3 -m venv $(VENV)
	$(PIP) install -r requirements.dev.txt
	$(PIP) install -r requirements.txt
	touch $(VENV)/bin/activate

version: test FORCE
	. $(VENV)/bin/activate; python3 helpers/incrementversion.py
	grep 'version *=' setup.py
	git add VERSION setup.py
	git commit -m 'incremented version'
	git push

release: version FORCE
	hub release create $$(cat VERSION)

# build the virtual environment for development and testing

# build the documentation

docs: FORCE
	./helpers/gendocs
	git status | awk '/modified:/{if(index($$0, ".md")<=0)exit(1)}'
	git add docs/*.md
	git add README.md
	git status
	git commit -a -m "documentation update"
	git push

gitconfig: FORCE
	git config core.hooksPath .githooks

clean: FORCE
	rm -rf $(TEMP)
	rm -rf venv build dist

passwd: FORCE
	$(PYTHON3) -m keyring set https://upload.pypi.org/legacy/ tmbdev

manually_force_dist: test FORCE
	rm -f dist/*
	$(PYTHON3) setup.py sdist bdist_wheel
	twine check dist/*
	twine upload dist/*

FORCE:
