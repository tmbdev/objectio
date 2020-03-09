"""Increments the version number in setup.py and updates VERSION in the
root directory of the project.
"""

import re

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
