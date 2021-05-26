import io
import os
import struct
from collections import namedtuple


# Header is used to store data related to different sections of the .pyc header
Header = namedtuple('Header', ['magic_number', 'timestamp', 'source_size'])


# Map the Python major, minor version to magic number in .pyc header
PYC_TARGET_VERSION_TO_MAGIC_NUMBER_BASE = {
    u'2.7': 62211,
    u'3.5': 3350,
    u'3.6': 3379,
    u'3.8': 3413
}

# Python byte slices for each section of the .pyc header
PYC_PY2_HEADER_BYTE_SLICES = Header(
    magic_number=slice(0, 4), timestamp=slice(4, 8), source_size=None
)
PYC_PY35_HEADER_BYTE_SLICES = Header(
    magic_number=slice(0, 4), timestamp=slice(4, 8), source_size=slice(8, 12)
)
PYC_PY37_HEADER_BYTE_SLICES = Header(
    magic_number=slice(0, 4), timestamp=slice(8, 12), source_size=slice(12, 16)
)

# Map the Python major, minor version to byte slices in .pyc header
PYC_TARGET_VERSION_TO_HEADER_BYTE_SLICES = {
    u'2.7': PYC_PY2_HEADER_BYTE_SLICES,
    u'3.5': PYC_PY35_HEADER_BYTE_SLICES,
    u'3.6': PYC_PY35_HEADER_BYTE_SLICES,
    u'3.8': PYC_PY37_HEADER_BYTE_SLICES,
}


def get_header(pyc_file, egg_python):
    """Return a Header namedtuple with the magic_number, timestamp,
       and source_size from a .pyc file

    Parameters
    ----------
    pyc_file: str
        path to the .pyc file from which the header will be returned
    egg_python: text
        python attribute of egg spec depend, i.e. the Python version of the egg

    Returns
    -------
    Header:
        namedtuple of header values
    """
    name = os.path.basename(pyc_file)
    byte_slices = PYC_TARGET_VERSION_TO_HEADER_BYTE_SLICES.get(
        egg_python, PYC_PY37_HEADER_BYTE_SLICES
    )
    if byte_slices.source_size is None:
        header_len = byte_slices.timestamp.stop
    else:
        header_len = byte_slices.source_size.stop
    with io.FileIO(pyc_file, 'rb') as f:
        data = f.read(header_len)
    if len(data) != header_len:
        message = 'reached EOF while reading header in {}'.format(name)
        raise EOFError(message)

    kwargs = {
        field: data[getattr(byte_slices, field)] for field in Header._fields
        if getattr(byte_slices, field) is not None
    }
    for int_field in ('timestamp', 'source_size'):
        if int_field in kwargs:
            kwargs[int_field] = struct.unpack('<I', kwargs[int_field])[0]
        else:
            kwargs[int_field] = None

    return Header(**kwargs)


def validate_bytecode_header(py_file, pyc_file, egg_python):
    """Validate a .pyc file by checking the following from the .pyc header:
       - the .pyc magic number matches the magic number for the target version
       - the .pyc timestamp matches the timestamp of the corresponding .py file
       - the .pyc source size matches the source size of the .py file
         (source size is not in the Python 2.7 .pyc header, so not checked)

       This code is similar to the Python 3.6 version of
       importlib._bootstrap_external._validate_bytecode_header. As in
       _validate_bytecode_header, the function raises an error for an invalid
       .pyc file.

    Parameters
    ----------
    py_file: str
        path to the .py file that corresponds to the .pyc file
    pyc_file: str
        path to the .pyc file that corresponds to the .py file
    egg_python: text
        python attribute of egg spec depend, i.e. the Python version of the egg
    """
    name = os.path.basename(pyc_file)
    header = get_header(pyc_file, egg_python)
    base_magic_number = PYC_TARGET_VERSION_TO_MAGIC_NUMBER_BASE.get(egg_python)
    expected_magic_number = struct.pack('<H', base_magic_number) + b'\r\n'
    if header.magic_number != expected_magic_number:
        message = 'bad magic number in {}: {}'
        raise ValueError(message.format(name, header.magic_number))

    source_stats = os.stat(py_file)
    source_mtime = int(source_stats.st_mtime)
    if header.timestamp != source_mtime:
        raise ValueError('bytecode is stale for {}'.format(name))

    if egg_python.startswith(u'3'):
        source_size = source_stats.st_size & 0xFFFFFFFF
        if header.source_size != source_size:
            raise ValueError('bytecode has wrong size for {}'.format(name))


def force_valid_pyc_file(py_file, pyc_file, egg_python):
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
    egg_python: text
        python attribute of egg spec depend, i.e. the Python version of the egg
    """
    byte_slices = PYC_TARGET_VERSION_TO_HEADER_BYTE_SLICES.get(
        egg_python, PYC_PY37_HEADER_BYTE_SLICES
    )
    header_len = byte_slices.timestamp.stop
    if isinstance(pyc_file, str):
        with io.FileIO(pyc_file, 'rb') as f:
            data = f.read(header_len)
    else:
        data = pyc_file.read(header_len)

    timestamp = struct.unpack('<I', data[byte_slices.timestamp])[0]
    os.utime(py_file, (timestamp, timestamp))


def cache_from_source(py_file, egg_python):
    """Python 2 compatible function to return cache file (.pyc)
       from source file (.py)

    Parameters
    ----------
    py_file: str
        Path to .py file
    egg_python: text
        python attribute of egg spec depend, i.e. the Python version of the egg

    Returns
    -------
    str
        Path to .pyc file
    """
    if egg_python.startswith(u'3'):
        dirname, basename = os.path.split(py_file)
        basename = '{}.cpython-{}{}.pyc'.format(
            os.path.splitext(basename)[0], egg_python[0], egg_python[-1]
        )
        return os.path.join(dirname, '__pycache__', basename)
    else:
        return '{}c'.format(py_file)


def source_from_cache(pyc_file, egg_python):
    """Python 2 compatible function to return source file (.py)
       from cache file (.pyc)

    Parameters
    ----------
    pyc_file: str
        Path to .pyc file
    egg_python: text
        python attribute of egg spec depend, i.e. the Python version of the egg

    Returns
    -------
    str
        Path to .py file
    """
    if egg_python.startswith(u'3'):
        dirname, basename = os.path.split(pyc_file)
        dirname = os.path.dirname(dirname)
        basename = '.'.join(basename.split('.')[:-2]) + '.py'
        return os.path.join(dirname, basename)
    else:
        return pyc_file[:-1]
