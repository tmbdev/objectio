from invoke import task
import os
import re
import sys

PACKAGE = "objectio"
VENV = "venv"
PYTHON3 = f"{VENV}/bin/python3"
PIP = f"{VENV}/bin/pip"
TEMP = "objectio.yaml objectio.yml"
DOCKER = "objectiotest"

modules = "objectio objectio.io".split()
commands = "obj".split()


@task
def virtualenv(c):
    "Build the virtualenv."
    c.run(f"git config core.hooksPath .githooks")
    c.run(f"test -d {VENV} || python3 -m venv {VENV}")
    c.run(f"{PIP} install -r requirements.dev.txt")
    c.run(f"{PIP} install -r requirements.txt")


@task(virtualenv)
def test(c):
    "Run the tests."
    c.run(f"{PYTHON3} -m pytest")


@task
def newversion(c):
    "Increment the version number."
    assert "working tree clean" in c.run("git status").stdout
    text = open("setup.py").read()
    version = re.search('version *= *"([0-9.]+)"', text).group(1)
    print("old version", version)
    text = re.sub(
        r'(version *= *"[0-9]+[.][0-9]+[.])([0-9]+)"',
        lambda m: f'{m.group(1)}{1+int(m.group(2))}"',
        text,
    )
    version = re.search('version *= *"([0-9.]+)"', text).group(1)
    print("new version", version)
    with open("setup.py", "w") as stream:
        stream.write(text)
    with open("VERSION", "w") as stream:
        stream.write(version)
    c.run(f"grep 'version *=' setup.py")
    c.run(f"git add VERSION setup.py")
    c.run(f"git commit -m 'incremented version'")
    # the git push will do a test
    c.run(f"git push")


@task
def release(c):
    "Tag the current version as a release on Github."
    assert "working tree clean" in c.run("git status").stdout
    version = open("VERSION").read().strip()
    c.run(f"hub release create {version}")


pydoc_template = """
# Module `{module}`

```
{text}
```
"""

command_template = """
# Command `{command}`

```
{text}
```
"""


@task
def gendocs(c):
    "Generate docs."
    for module in "objectio objectio.io".split():
        with os.popen("{PYTHON3} -m pydoc {module}") as stream:
            text = stream.read()
        with os.popen("docs/{module}.md", "w") as stream:
            stream.write(pydoc_template.format(text=text, module=module))
    for command in commands:
        with os.popen("{command} --help ") as stream:
            text = stream.read()
        with os.popen("docs/{command}.md", "w") as stream:
            stream.write(command_template.format(text=text, command=command))


@task(gendocs)
def pubdocs(c):
    "Generate and publish docs."
    modified = os.popen("git status").readlines()
    for line in modified:
        if "modified:" in line and ".md" not in line:
            print("non-documentation file modified; commit manually", file=sys.stderr)
    c.run("git add docs/*.md README.md")
    c.run("git commit -a -m 'documentation update'")
    c.run("git push")


@task
def clean(c):
    "Remove temporary files."
    c.run(f"rm -rf {TEMP}")
    c.run(f"rm -rf build dist")


@task
def cleanall(c):
    "Remove temporary files and virtualenv."
    c.run(f"rm -rf {TEMP}")
    c.run(f"rm -rf venv build dist")


@task(test)
def twine_pypi_release(c):
    "Manually push to PyPI via Twine."
    c.run("rm -f dist/*")
    c.run("$(PYTHON3) setup.py sdist bdist_wheel")
    c.run("twine check dist/*")
    c.run("twine upload dist/*")


build_base_container = f"""
docker build -t {DOCKER}-base - <<EOF
FROM ubuntu:19.10
ENV LC_ALL=C
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -qqy update
RUN apt-get install -qqy git
RUN apt-get install -qqy python3
RUN apt-get install -qqy python3-pip
RUN apt-get install -qqy python3-venv
RUN apt-get install -qqy curl
EOF
"""


@task
def dockerbase(c):
    "Build a base container."
    c.run(build_base_container)


run_github_test = f"""
docker build -t {DOCKER}-github --no-cache - <<EOF
FROM objectiotest-base
ENV SHELL=/bin/bash
RUN git clone https://git@github.com/tmbdev/objectio.git /tmp/objectio
WORKDIR /tmp/objectio
RUN python3 -m venv venv
RUN . venv/bin/activate; pip install --no-cache-dir pytest
RUN . venv/bin/activate; pip install --no-cache-dir -r requirements.txt
RUN . venv/bin/activate; python3 -m pytest
EOF
"""


@task(dockerbase)
def githubtest(c):
    "Test the latest version on Github in a docker container."
    c.run(run_github_test)


run_pypi_test = f"""
docker build -t objectiotest --no-cache - <<EOF
FROM objectiotest-base
ENV SHELL=/bin/bash
RUN pip3 install objectio
RUN pip3 install pytest

# we clone this just to get the tests

RUN git clone https://git@github.com/tmbdev/objectio.git /tmp/objectio
WORKDIR /tmp/objectio

# we need to run the tests in the current directory
# but we want to make sure that we are using the globally
# installed libraries, so we move the subdirectory out of the way

RUN mv objectio use-installed-objectio

# note that for commands, this will test ./command, not /usr/local/bin/command

RUN python3 -m pytest
EOF
"""


@task
def pypitest(c):
    "Test the latest version on PyPI in a docker container."
    c.run(run_pypi_test)
