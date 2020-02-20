# Development

## Tools

For development, we're using the following Python tools:

- Packaging: setuptools wheel
- Testing: pytest (also: coverage tox)
- Uploading to PyPI: twine keyring
- Documentation generation: mkdocs nbconvert pydoc3 (builtin)

This is a fairly minimalist set of tools for modern Python packaging.

Custom scripts:

- Automation: Makefile
- Documentation generation: gendocs
- Testing on Docker: dockergit dockerpip

## Configuration Files

Configuration:

- requirements for virtual environment: requirements.txt
- requirements for pip install: setup.py
- requirements for development: requirements.dev.txt
- .githooks for pre-push hook (git config core.hooksPath .githook)
- .github/workflows for workflows

Makefile targets

- venv: setup the virtualenv
- tests: run unit tests
- push: push to github
- dist: make a distribution on PyPI
- docs: build the docs
- githubtests: run docker test against github repo
- pypitests: run docker test against pypi package
- clean: clean temporary files, artifacts, venv
- passwd: authenticate to keyring

Most functions will likely move to Github Actions soon.
