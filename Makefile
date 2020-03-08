#!/bin/bash

VENV=venv
PYTHON3=$(VENV)/bin/python3
PIPOPT=--no-cache-dir
PIP=$(VENV)/bin/pip $(PIPOPT)

# run the unit tests in a virtual environment

tests: venv FORCE
	rm -f objectio.yaml objectio.yml # config files that interfere with tests
	. ./venv/bin/activate; python3 -m pytest

githubtests:
	./helpers/dockertest git

pypitests:
	./helpers/dockertest pip

venv: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt requirements.dev.txt
	test -d $(VENV) || python3 -m venv $(VENV)
	$(PIP) install -r requirements.dev.txt
	$(PIP) install -r requirements.txt
	touch $(VENV)/bin/activate

bumpversion: FORCE
	cat VERSION
	awk -F. '{print $$1"."$$2"."$$3+1}' VERSION > VERSION1
	mv VERSION1 VERSION
	cat VERSION
	git add VERSION
	git commit -m 'version bump'
	git push

release: bump FORCE
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
	rm -rf venv build dist
	rm -f objectio.yaml objectio.yml # config files that interfere with tests

passwd: FORCE
	$(PYTHON3) -m keyring set https://upload.pypi.org/legacy/ tmbdev

# push a new version to pypi; commit all changes first or this will fail
# after a successful push, it will try to clone the repo into a docker container
# and execute the tests

# dist: FORCE
# 	rm -f dist/*
# 	$(PYTHON3) setup.py sdist bdist_wheel
# 	twine check dist/*
# 	twine upload dist/*

FORCE:
