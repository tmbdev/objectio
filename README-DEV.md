# Development

We're using a minimal set of tools for publishing packages:

- development and deployment environments are created with virtualenv
- the dependencies are found in `requirements.dev.txt` and `requirements.txt`
- the package is built using `setuptools`
- `PyTest` is used as the testing framework
- packaging and releases are handled by Github workflows
- documentation is in Markdown format and generated using `mkdocs`
- documentation is published on ReadTheDocs.io via Github integration
- testing in a clean environment locally is handled via Docker
- maintenance steps are defined in `tasks.py` and handled via `invoke`

Run `invoke --list` to see what maintenance commands are available.
