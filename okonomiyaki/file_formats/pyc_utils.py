import imp
import io
import marshal
import os
import struct
import sys
from collections import namedtuple
if sys.version_info.major > 2:
    import importlib

# Header is used to store data related to different sections of the .pyc header
Header2 = namedtuple('Header2', ['magic', 'crlf', 'timestamp'])
Header3 = namedtuple('Header3', ['magic', 'crlf', 'timestamp', 'source_size'])
Header37 = namedtuple(
    'Header37', ['magic', 'crlf', 'flags', 'timestamp', 'source_size']
)

# Map the Python major, minor version to the corresponding Header namedtuple
EGG_PYTHON_TO_HEADER_CLASS = {
    u'2.7': Header2,
    u'3.0': Header3,
    u'3.1': Header3,
    u'3.2': Header3,
    u'3.3': Header3,
    u'3.4': Header3,
    u'3.5': Header3,
    u'3.6': Header3,
    u'3.7': Header37,
    u'3.8': Header37,
    u'3.9': Header37,
    u'3.10': Header37,
}

# Map the Python major, minor version to magic number in .pyc header
EGG_PYTHON_TO_MAGIC_NUMBER = {
    u'2.7': 62211,
    u'3.0': 3131,
    u'3.1': 3151,
    u'3.2': 3180,
    u'3.3': 3230,
    u'3.4': 3310,
    u'3.5': 3350,
    u'3.6': 3379,
    u'3.7': 3394,
    u'3.8': 3413,
    u'3.9': 3425,
    u'3.10': 3439,
}

# Python .pyc header formats
PYC_PY2_HEADER_STRUCT_FORMAT = '<H2sI'
PYC_PY3_HEADER_STRUCT_FORMAT = '<H2sII'
PYC_PY37_HEADER_STRUCT_FORMAT = '<H2sIII'

# Map the Python major, minor version to .pyc header format
EGG_PYTHON_TO_STRUCT_FORMAT = {
    u'2.7': PYC_PY2_HEADER_STRUCT_FORMAT,
    u'3.0': PYC_PY3_HEADER_STRUCT_FORMAT,
    u'3.1': PYC_PY3_HEADER_STRUCT_FORMAT,
    u'3.2': PYC_PY3_HEADER_STRUCT_FORMAT,
    u'3.3': PYC_PY3_HEADER_STRUCT_FORMAT,
    u'3.4': PYC_PY3_HEADER_STRUCT_FORMAT,
    u'3.5': PYC_PY3_HEADER_STRUCT_FORMAT,
    u'3.6': PYC_PY3_HEADER_STRUCT_FORMAT,
    u'3.7': PYC_PY37_HEADER_STRUCT_FORMAT,
    u'3.8': PYC_PY37_HEADER_STRUCT_FORMAT,
    u'3.9': PYC_PY37_HEADER_STRUCT_FORMAT,
    u'3.10': PYC_PY37_HEADER_STRUCT_FORMAT,
}


def get_header(pyc_file, egg_python):
    """Return a Header namedtuple with the magic_number, timestamp,
       and source_size from a .pyc file

    Parameters
    ----------
    pyc_file: file-like object
        file-like bytecode object of the .pyc file
    egg_python: unicode string
        python attribute of egg spec depend, i.e. the Python version of the egg

    Returns
    -------
    Header:
        namedtuple of header values
    """
    header_struct = struct.Struct(EGG_PYTHON_TO_STRUCT_FORMAT.get(
        egg_python, PYC_PY37_HEADER_STRUCT_FORMAT
    ))
    data = pyc_file.read(header_struct.size)

    Header = EGG_PYTHON_TO_HEADER_CLASS.get(egg_python, Header37)
    return Header(*header_struct.unpack(data))


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
    egg_python: unicode string
        python attribute of egg spec depend, i.e. the Python version of the egg
    """
    name = os.path.basename(pyc_file)
    with io.FileIO(pyc_file, 'rb') as pyc:
        header = get_header(pyc, egg_python)
    magic_number = EGG_PYTHON_TO_MAGIC_NUMBER.get(egg_python)
    if header.magic != magic_number or header.crlf != b'\r\n':
        message = 'bad magic number in {}: {}'
        raise ValueError(message.format(name, header.magic))

    source_stats = os.stat(py_file)
    source_mtime = int(source_stats.st_mtime)
    if header.timestamp != source_mtime:
        raise ValueError('bytecode is stale for {}'.format(name))

    if not egg_python.startswith(u'2.'):
        source_size = source_stats.st_size & 0xFFFFFFFF
        if header.source_size != source_size:
            raise ValueError('bytecode has wrong size for {}'.format(name))


def validate_bytecode(py_file, pyc_file, egg_python):
    """Validate the bytecode of a .pyc file by compiling from the .py source
       and comparing

    Parameters
    ----------
    py_file: str
        path to the .py file that corresponds to the .pyc file
    pyc_file: str
        path to the .pyc file that corresponds to the .py file
    egg_python: unicode string
        python attribute of egg spec depend, i.e. the Python version of the egg
    """
    # Can only check bytecode for eggs with same version as system
    assert egg_python == '{}.{}'.format(*sys.version_info[:2])

    with io.FileIO(pyc_file, 'rb') as pyc:
        data = pyc.read()
    # Egg header magic should be same as system
    assert data[:4] == imp.get_magic()

    header_struct = struct.Struct(EGG_PYTHON_TO_STRUCT_FORMAT[egg_python])
    pyc_bytecode = data[header_struct.size:]

    if sys.version_info.major > 2:
        loader = importlib.machinery.SourceFileLoader('<py_compile>', py_file)
        source_bytes = loader.get_data(py_file)
        code = loader.source_to_code(source_bytes, py_file)
        py_bytecode = marshal.dumps(code)
    else:
        with open(py_file, 'U') as f:
            codestring = f.read()
        codeobject = compile(codestring, py_file)
        py_bytecode = marshal.dumps(codeobject)
    if pyc_bytecode != py_bytecode:
        raise ValueError('bytecode different from source')


def force_valid_pyc_file(py_file, pyc_file, egg_python):
    """Force a .pyc file to be valid by setting the timestamp of the
       corresponding .py file to equal the timestamp in the .pyc header
       (This function should be Python version independent.)

    Parameters
    ----------
    py_file: str
        path to the .py file that corresponds to the .pyc file
    pyc_file: file-like object
        file-like bytecode object that corresponds to the .py file
    egg_python: unicode string
        python attribute of egg spec depend, i.e. the Python version of the egg
    """
    header = get_header(pyc_file, egg_python)
    os.utime(py_file, (header.timestamp, header.timestamp))


def cache_from_source(py_file, egg_python):
    """Python 2 compatible function to return cache file (.pyc)
       from source file (.py)

    Parameters
    ----------
    py_file: str
        Path to .py file
    egg_python: unicode string
        python attribute of egg spec depend, i.e. the Python version of the egg

    Returns
    -------
    str
        Path to .pyc file
    """
    if egg_python.startswith(u'3'):
        dirname, basename = os.path.split(py_file)
        pyc = '{}.cpython-{}{}.pyc'.format(
            os.path.splitext(basename)[0], egg_python[0], egg_python[-1]
        )
        return os.path.join(dirname, '__pycache__', pyc)
    else:
        return '{}c'.format(py_file)


def source_from_cache(pyc_file, egg_python):
    """Python 2 compatible function to return source file (.py)
       from cache file (.pyc)

    Parameters
    ----------
    pyc_file: str
        Path to .pyc file
    egg_python: unicode string
        python attribute of egg spec depend, i.e. the Python version of the egg

    Returns
    -------
    str
        Path to .py file
    """
    if egg_python.startswith(u'3'):
        pyc_dirname, pyc_basename = os.path.split(pyc_file)
        py_dirname = os.path.dirname(pyc_dirname)
        py_basename = '.'.join(pyc_basename.split('.')[:-2]) + '.py'
        return os.path.join(py_dirname, py_basename)
    else:
        return pyc_file[:-1]


def get_pyc_files(search_path):
    """Return list of .pyc files by recursively searching through search_path

    Parameters
    ----------
    search_path: str
        Path to search for .pyc files

    Returns
    -------
    list (str):
        List of paths to .pyc files
    """
    pyc_files = []
    for root, dirs, files in os.walk(search_path):
        pyc_files.extend([
            os.path.join(root, f) for f in files if f.endswith('.pyc')
        ])
    return pyc_files
