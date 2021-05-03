#
# Enthought product code
#
# (C) Copyright 2010-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.
#
import importlib
import importlib.util
import io
import os
import time
import zipfile
from glob import glob


def get_data(path):
    """Return the data from path as raw bytes."""
    with io.FileIO(path, 'rb') as file:
        return file.read()


def check_bytecode_from_source_or_pyc(path):
    """Check the header of the bytecode obtained from pyc_path
    against source_stats obtained from source_path.

    Echo the ImportError messages that are raised from importlib
    _validate_bytecode_header when the magic number is incorrect or the
    bytecode is found to be stale if verbose parameter is not None. EOFError
    is raised when the data is found to be truncated.

    The function _validate_bytecode_header has a new name in Python > 3.6
    because validating based on hash values has been added to importlib.

    Return empty list if check is successful and list with the error otherwise.
    """
    _, ext = os.path.splitext(path)
    if ext == '.py':
        source_path = path
        pyc_path = importlib.util.cache_from_source(path)
    elif ext == '.pyc':
        source_path = importlib.util.source_from_cache(path)
        pyc_path = path
    statinfo = os.stat(source_path)
    source_mtime_int = int(statinfo.st_mtime)
    source_mtime = time.ctime(source_mtime_int)
    data = get_data(pyc_path)
    pyc_mtime_int = int.from_bytes(data[4:8], 'little')
    pyc_mtime = time.ctime(pyc_mtime_int)
    try:
        importlib._bootstrap_external._validate_bytecode_header(
            data, source_stats={'mtime': statinfo.st_mtime},
            path=pyc_path, name=os.path.basename(pyc_path)
        )
    except ImportError as e:
        err_msg = e.args[0]
        # Add time details to stale bytecode error message
        if err_msg.startswith('bytecode is stale'):
            err_msg += ' (source_mtime={}, {}; bytecode_mtime={}, {})'.format(
                source_mtime_int, source_mtime, pyc_mtime_int, pyc_mtime
            )
        return [ImportError(err_msg)]
    except EOFError as e:
        return [e]
    else:
        return []


def check_folder_pyc_files(path):
    """Run check_bytecode_from_source_or_pyc for all files in a folder

    Return empty list if check is successful and list with errors otherwise.
    """
    failures = []
    pyc_files = glob(os.path.join(path, '**', '*.pyc'), recursive=True)
    for pyc_file in pyc_files:
        failures += check_bytecode_from_source_or_pyc(pyc_file)
    return failures


def check_egg_pyc_files(path, extractdir):
    """Run check_bytecode_from_source_or_pyc for all files in an egg

    Only .py or .pyc files are extracted from the egg.
    Return empty list if check is successful and list with errors otherwise.
    """
    with zipfile.ZipFile(path, 'r') as zip:
        for f in zip.infolist():
            _, ext = os.path.splitext(f.filename)
            if ext in ('.py', '.pyc'):
                zip.extract(f, extractdir)
                filename = os.path.join(extractdir, f.filename)
                timestamp = time.mktime(f.date_time + (0, 0, -1))
                os.utime(filename, (timestamp, timestamp))
    return check_folder_pyc_files(extractdir)
