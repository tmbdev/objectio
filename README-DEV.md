# Development

We're using a minimal set of tools for publishing packages:

- development and deployment environments are created with virtualenv
- the dependencies are found in `requirements.dev.txt` and `requirements.txt`
- the package is built using `setuptools`
- `PyTest` is used as the testing framework
- building, testing, releasing, etc. are handled via a Makefile (not pretty, but universal)
- packaging and releases are handled by Github workflows
- documentation is in Markdown format and generated using `mkdocs`
- documentation is published on ReadTheDocs.io via Github integration
- testing in a clean environment locally is handled via Docker

# Makefile targets

- `test`: run PyTest
- `venv`: create the virtualenv
- `version`: increment the version and push
- `release`: increment the version, push, and tag (triggers PyPI release)
- `docs`: make the docs
- `gitconfig`: update config to use .githooks
- `clean`: remove temporary files and virtualenv
- `containertest`: install from Github in a container and test
- `pypitests`: install from PyPI in a container and test

# Helpers

- `helpers/dockertest`: run tests in Docker containers
- `helpers/gendocs`: generate the doc files
- `helpers/incrementversion.py`: increment the version in `setup.py` and `VERSION`
