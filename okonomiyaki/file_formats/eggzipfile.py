import importlib
import io
import os
import sys
import zipfile2


def force_valid_pyc_file(py_file, pyc_file):
    header = io.FileIO(pyc_file, 'rb').read(8)
    timestamp = int.from_bytes(header[4:8], 'little')
    os.utime(py_file, (timestamp, timestamp))


class EggZipFile(zipfile2.ZipFile):
    def extractall(self, path=None, members=None, pwd=None,
                   preserve_permissions=zipfile2.PERMS_PRESERVE_NONE,
                   force_valid_pyc_files=False):
        """Extract all members from the archive to the current working
           directory. Overrides zipfile2.ZipFile extractall with the addition
           of force_valid_pyc_files parameter.

        Parameters:
        path: str
            path specifies a different directory to extract to.
        members: list
            is optional and must be a subset of the list returned by
            namelist().
        preserve_permissions: int
            controls whether permissions of zipped files are preserved or
            not. Default is PERMS_PRESERVE_NONE - do not preserve any
            permissions. Other options are to preserve safe subset of
            permissions PERMS_PRESERVE_SAFE or all permissions
            PERMS_PRESERVE_ALL.
        force_valid_pyc_files: bool
            Forces valid .pyc files by setting the timestamp of the
            corresponding .py file to the timestamp of the bytecode header.
            (This is only available for Python 3 because importlib is mostly
             non-existent for Python 2.)
        """
        if members is None:
            members = self.namelist()

        if force_valid_pyc_files:
            if sys.version_info.major == 2:
                force_valid_pyc_files = False
            else:
                map_need_to_exist_py_pyc_pairs = {}

        for zipinfo in members:
            target = self.extract(zipinfo, path, pwd, preserve_permissions)
            if force_valid_pyc_files:
                if target.endswith('.py'):
                    if target in map_need_to_exist_py_pyc_pairs:
                        pyc_file = map_need_to_exist_py_pyc_pairs.pop(target)
                        force_valid_pyc_file(target, pyc_file)
                    else:
                        pyc_file = importlib.util.cache_from_source(target)
                        map_need_to_exist_py_pyc_pairs[pyc_file] = target
                elif target.endswith('.pyc'):
                    if target in map_need_to_exist_py_pyc_pairs:
                        py_file = map_need_to_exist_py_pyc_pairs.pop(target)
                        force_valid_pyc_file(py_file, target)
                    else:
                        py_file = importlib.util.source_from_cache(target)
                        map_need_to_exist_py_pyc_pairs[py_file] = target
