import io
import os
import struct
from collections import namedtuple


# Header is used to store data related to different sections of the .pyc header
Header = namedtuple('Header', ['magic_number', 'timestamp', 'source_size'])


# Map the Python major, minor version to magic number in .pyc header
PYC_TARGET_VERSION_TO_MAGIC_NUMBER_BASE = {
    (2, 7): 62211,
    (3, 5): 3350,
    (3, 6): 3379,
    (3, 8): 3413
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
    (2, 7): PYC_PY2_HEADER_BYTE_SLICES,
    (3, 5): PYC_PY35_HEADER_BYTE_SLICES,
    (3, 6): PYC_PY35_HEADER_BYTE_SLICES,
    (3, 8): PYC_PY37_HEADER_BYTE_SLICES,
}


def get_header(pyc_file, target_version_info):
    """Return a Header namedtuple with the magic_number, timestamp,
       and source_size from a .pyc file

    Parameters
    ----------
    pyc_file: str
        path to the .pyc file from which the header will be returned
    target_version_info: tuple(int)
        version_info tuple like sys.version_info but for target Python version
        of .pyc file (Only first 2 items for major and minor version are used.)

    Returns
    -------
    Header:
        namedtuple of header values
    """
    name = os.path.basename(pyc_file)
    byte_slices = PYC_TARGET_VERSION_TO_HEADER_BYTE_SLICES.get(
        target_version_info[:2], PYC_PY37_HEADER_BYTE_SLICES
    )
    if byte_slices.source_size is None:
        header_len = byte_slices.timestamp.stop
    else:
        header_len = byte_slices.source_size.stop
    with io.FileIO(pyc_file, 'rb') as f:
        data = f.read(header_len)

    kwargs = {
        field: data[getattr(byte_slices, field)] for field in Header._fields
        if getattr(byte_slices, field) is not None
    }
    for int_field in ('timestamp', 'source_size'):
        if int_field in kwargs:
            if len(kwargs[int_field]) != 4:
                message = 'reached EOF while reading {} in {}'
                raise EOFError(message.format(int_field, name))
            kwargs[int_field] = struct.unpack('<I', kwargs[int_field])[0]
        else:
            kwargs[int_field] = None

    return Header(**kwargs)


def validate_bytecode_header(py_file, pyc_file, target_version_info):
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
    target_version_info: tuple(int)
        version_info tuple like sys.version_info but for target Python version
        of .pyc file (Only first 2 items for major and minor version are used.)
    """
    name = os.path.basename(pyc_file)
    header = get_header(pyc_file, target_version_info)
    base_magic_number = PYC_TARGET_VERSION_TO_MAGIC_NUMBER_BASE.get(
        target_version_info[:2]
    )
    expected_magic_number = struct.pack('<H', base_magic_number) + b'\r\n'
    if header.magic_number != expected_magic_number:
        message = 'bad magic number in {}: {}'
        raise ImportError(message.format(name, header.magic_number))

    source_stats = os.stat(py_file)
    source_mtime = int(source_stats.st_mtime)
    if header.timestamp != source_mtime:
        raise ImportError('bytecode is stale for {}'.format(name))

    if target_version_info[0] == 3:
        source_size = source_stats.st_size & 0xFFFFFFFF
        if header.source_size != source_size:
            raise ImportError('bytecode has wrong size for {}'.format(name))


def force_valid_pyc_file(py_file, pyc_file, target_version_info):
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
        of .pyc file (Only first 2 items for major and minor version are used.)
    """
    byte_slices = PYC_TARGET_VERSION_TO_HEADER_BYTE_SLICES.get(
        target_version_info[:2], PYC_PY37_HEADER_BYTE_SLICES
    )
    header_len = byte_slices.timestamp.stop
    if isinstance(pyc_file, str):
        with io.FileIO(pyc_file, 'rb') as f:
            data = f.read(header_len)
    else:
        data = pyc_file.read(header_len)

    timestamp = struct.unpack('<I', data[byte_slices.timestamp])[0]
    os.utime(py_file, (timestamp, timestamp))


def cache_from_source(py_file, target_version_info):
    """Python 2 compatible function to return cache file (.pyc)
       from source file (.py)

    Parameters
    ----------
    py_file: str
        Path to .py file
    target_version_info: tuple(int)
        version_info tuple like sys.version_info but for target Python version
        of .pyc file (Only first 2 items for major and minor version are used.)

    Returns
    -------
    str
        Path to .pyc file
    """
    if target_version_info[0] == 3:
        dirname, basename = os.path.split(py_file)
        basename = '{}.cpython-{}{}.pyc'.format(
            os.path.splitext(basename)[0], *target_version_info[:2]
        )
        return os.path.join(dirname, '__pycache__', basename)
    else:
        return '{}c'.format(py_file)


def source_from_cache(pyc_file, target_version_info):
    """Python 2 compatible function to return source file (.py)
       from cache file (.pyc)

    Parameters
    ----------
    pyc_file: str
        Path to .pyc file
    target_version_info: tuple(int)
        version_info tuple like sys.version_info but for target Python version
        of .pyc file (Only first item for major version is used.)

    Returns
    -------
    str
        Path to .py file
    """
    if target_version_info[0] == 3:
        dirname, basename = os.path.split(pyc_file)
        dirname = os.path.dirname(dirname)
        basename = '.'.join(basename.split('.')[:-2]) + '.py'
        return os.path.join(dirname, basename)
    else:
        return pyc_file[:-1]
