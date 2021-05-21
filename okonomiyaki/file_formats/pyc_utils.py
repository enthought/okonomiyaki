import importlib
import io
import os
import sys


def force_valid_pyc_file(py_file, pyc_file):
    """Force a .pyc file to be valid by setting the timestamp of the
       corresponding .py file to equal the timestamp in the .pyc header

    Parameters
    ----------
    py_file: str
        path to the .py file that corresponds to the .pyc file
    pyc_file: str OR file-like object
        path to the .pyc file that corresponds to the .py file
        OR
        file-like bytecode object that corresponds to the .py file
    """
    if isinstance(pyc_file, str):
        with io.FileIO(pyc_file, 'rb') as f:
            header = f.read(8)
    else:
        header = pyc_file.read(8)
    timestamp = int.from_bytes(header[4:8], 'little')
    os.utime(py_file, (timestamp, timestamp))


def cache_from_source(py_file):
    """Python 2 compatible function to return cache file (.pyc)
       from source file (.py)

    Parameters
    ----------
    py_file: str
        Path to .py file

    Returns
    -------
    str
        Path to .pyc file
    """
    if sys.version_info.major == 2:
        return '{}c'.format(pyc_file)
    else:
        return importlib.util.cache_from_source(py_file)


def source_from_cache(pyc_file):
    """Python 2 compatible function to return source file (.py)
       from cache file (.pyc)

    Parameters
    ----------
    pyc_file: str
        Path to .pyc file

    Returns
    -------
    str
        Path to .py file
    """
    if sys.version_info.major == 2:
        return pyc_file[:-1]
    else:
        return importlib.util.source_from_cache(pyc_file)
