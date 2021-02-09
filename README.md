# legacystamps
A tiny Python module to allow easy retrieval of a cutout from the Legacy survey.

## Installation
This package can be installed simply by running `pip install legacystamps`. It can also  be installed manually with `python setup.py install`.

## Usage
To use it in a script, import and use the module as follows. To get a FITS cutout:

```python
import legacystamps
legacystamps.download(ra=ra, dec=dec, mode='fits', bands='grz', size=cutsize)
```

or to get a JPEG cutout:
```python
import legacystamps
legacystamps.download(ra=ra, dec=dec, mode='jpeg', bands='grz', size=cutsize)
```

It can also run standalone. See `legacystamps.py -h` for available options after installation.

## Requirements
The following packages are required:

* requests
* tqdm

