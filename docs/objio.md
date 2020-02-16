# objio.io
Object Store I/O Functions.

This defines two functions (`gopen`, `objopen`) that can access a
large variety of object stores using a uniform interface.

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
