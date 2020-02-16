#!/bin/bash

docs: FORCE
	cp README.md docs/index.md
	jupyter nbconvert --to markdown notebooks/examples.ipynb
	mv notebooks/examples.md docs/examples.md
	pydocmd simple objio.io > docs/io.md
	./cmd2md obj > docs/obj.md
	#mkdocs build

FORCE:
