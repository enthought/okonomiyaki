import importlib
import io
import os
import sys


# Map the Python major, minor version to timestamp start byte in .pyc header
PYC_TARGET_VERSION_TO_TS_START_BYTE = {
    (2, 7): 4,
    (3, 5): 4,
    (3, 6): 4,
    (3, 8): 8
}
# All timestamp start bytes in .pyc header are 8 up to current, so 8 is default
PYC_DEFAULT_TS_START_BYTE = 8


def force_valid_pyc_file(py_file, pyc_file, target_version_info=None):
    """Force a .pyc file to be valid by setting the timestamp of the
       corresponding .py file to equal the timestamp in the .pyc header
       (This function should be Python version independent.)

    Parameters
    ----------
    py_file: str
        path to the .py file that corresponds to the .pyc file
    pyc_file: str OR file-like object
        path to the .pyc file that corresponds to the .py file
        OR
        file-like bytecode object that corresponds to the .py file
    target_version_info: tuple(int)
        version_info tuple like sys.version_info but for target Python version
        of .pyc file
    """
    if target_version_info is None:
        target_version_info = sys.version_info
    ts_start_byte = PYC_TARGET_VERSION_TO_TS_START_BYTE.get(
        target_version_info[:2], PYC_DEFAULT_TS_START_BYTE
    )
    ts_stop_byte = ts_start_byte + 4
    if isinstance(pyc_file, str):
        with io.FileIO(pyc_file, 'rb') as f:
            header = f.read(ts_stop_byte)
    else:
        header = pyc_file.read(ts_stop_byte)
    timestamp = int.from_bytes(header[ts_start_byte:ts_stop_byte], 'little')
    os.utime(py_file, (timestamp, timestamp))


def cache_from_source(py_file, target_version_py3=True):
    """Python 2 compatible function to return cache file (.pyc)
       from source file (.py)

    Parameters
    ----------
    py_file: str
        Path to .py file
    target_version_py3: bool
        True if the target Python version of the .py file is Python 3

    Returns
    -------
    str
        Path to .pyc file
    """
    if target_version_py3:
        if sys.version_info.major == 3:
            return importlib.util.cache_from_source(py_file)
        else:
            dirname, basename = os.path.split(py_file)
            return os.path.join(dirname, '__pycache__', basename + 'c')
    else:
        return '{}c'.format(py_file)


def source_from_cache(pyc_file, target_version_py3=True):
    """Python 2 compatible function to return source file (.py)
       from cache file (.pyc)

    Parameters
    ----------
    pyc_file: str
        Path to .pyc file
    target_version_py3: bool
        True if the target Python version of the .pyc file is Python 3

    Returns
    -------
    str
        Path to .py file
    """
    if target_version_py3:
        if sys.version_info.major == 3:
            return importlib.util.source_from_cache(pyc_file)
        else:
            dirname, basename = os.path.split(pyc_file)
            dirname = os.path.dirname(dirname)
            return os.path.join(dirname, basename[:-1])
    else:
        return pyc_file[:-1]
