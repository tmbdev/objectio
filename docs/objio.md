# objio.io

## update_yaml_with
```python
update_yaml_with(target, source)
```
Merge the source YAML tree into the target. Useful for merging config files.
## ObjioExeption
```python
ObjioExeption(self, info)
```
I/O Exceptions during objio operations.
## Pipe
```python
Pipe(self, cmd, writable, raise_errors=True, stream=None, bufsize=8192, **kw)
```
A wrapper for the pipe class that adapts it to the needs of objio.
## maybe
```python
maybe(f, default)
```
Evaluate f and return the value; return default on error.
## get_handler_for
```python
get_handler_for(url, verb)
```
Look for a handler for the url/verb combination in the config file.
## url_variables
```python
url_variables(url, pr)
```
Generate a dictionary exposing the URL components. Names follow urlparse.
## substitute_variables
```python
substitute_variables(cmd, variables)
```
Given a cmd specified either as a string or as a list, substitute the variables.
## writable
```python
writable(verb)
```
Does the given verb require a writable file descriptor?
## cmd_handler
```python
cmd_handler(url, verb, raise_errors=True, stream=None, verbose=False)
```
Given a url and verb, handle the command.
## objopen
```python
objopen(url, verb='read', stream=None)
```
Open a storage object. This always spawns a subprocess and supports all verbs.
## gopen
```python
gopen(url, filemode='rb')
```
Open a storage object. This shortcuts to open() for local files and accepts file open modes.
