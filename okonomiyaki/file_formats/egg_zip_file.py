import importlib
import io
import os
import shutil
import sys
import zipfile
import zipfile2
from zipfile2 import (
    PERMS_PRESERVE_NONE, PERMS_PRESERVE_SAFE, PERMS_PRESERVE_ALL
)
from zipfile2.common import text_type
from zipfile2._zipfile import is_zipinfo_symlink, _unlink_if_exists


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


class EggZipFile(zipfile2.ZipFile):
    def extract(self, member, path=None, pwd=None,
                preserve_permissions=PERMS_PRESERVE_NONE,
                force_valid_pyc_files=False):
        # force_valid_pyc_files not available for Python 2 for now
        if sys.version_info.major == 2:
            if force_valid_pyc_files:
                force_valid_pyc_files = False

        if not isinstance(member, zipfile.ZipInfo):
            member = self.getinfo(member)

        if path is None:
            path = os.getcwd()

        return self._extract_member(
            member, path, pwd, preserve_permissions, force_valid_pyc_files
        )

    def extractall(self, path=None, members=None, pwd=None,
                   preserve_permissions=PERMS_PRESERVE_NONE,
                   force_valid_pyc_files=False):
        """Extract all members from the archive to the current working
           directory. Overrides zipfile2.ZipFile extractall with the addition
           of force_valid_pyc_files parameter.

        Parameters
        ----------
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

        for zipinfo in members:
            self.extract(
                zipinfo, path, pwd, preserve_permissions, force_valid_pyc_files
            )

    def _extract_member(self, member, targetpath, pwd, preserve_permissions,
                        force_valid_pyc_files):
        return self._extract_member_to(
            member, member.filename, targetpath, pwd, preserve_permissions,
            force_valid_pyc_files
        )

    def _extract_member_to(self, member, arcname, targetpath, pwd,
                           preserve_permissions, force_valid_pyc_files):
        """Extract the ZipInfo object 'member' to a physical
           file on the path targetpath.
        """
        # build the destination pathname, replacing
        # forward slashes to platform specific separators.
        arcname = arcname.replace('/', os.path.sep)

        if os.path.altsep:
            arcname = arcname.replace(os.path.altsep, os.path.sep)
        # interpret absolute pathname as relative, remove drive letter or
        # UNC path, redundant separators, "." and ".." components.
        arcname = os.path.splitdrive(arcname)[1]
        arcname = os.path.sep.join(x for x in arcname.split(os.path.sep)
                                   if x not in ('', os.path.curdir,
                                                os.path.pardir))
        if os.path.sep == '\\':
            # filter illegal characters on Windows
            illegal = ':<>|"?*'
            if isinstance(arcname, text_type):
                table = dict((ord(c), ord('_')) for c in illegal)
            else:
                table = string.maketrans(illegal, '_' * len(illegal))
            arcname = arcname.translate(table)
            # remove trailing dots
            arcname = (x.rstrip('.') for x in arcname.split(os.path.sep))
            arcname = os.path.sep.join(x for x in arcname if x)

        targetpath = os.path.join(targetpath, arcname)
        targetpath = os.path.normpath(targetpath)

        # Create all upper directories if necessary.
        upperdirs = os.path.dirname(targetpath)
        if upperdirs and not os.path.exists(upperdirs):
            os.makedirs(upperdirs)

        if member.filename[-1] == '/':
            if not os.path.isdir(targetpath):
                os.mkdir(targetpath)
            return targetpath
        elif is_zipinfo_symlink(member):
            return self._extract_symlink(member, targetpath, pwd)
        else:
            source = self.open(member, pwd=pwd)
            try:
                _unlink_if_exists(targetpath)
                with open(targetpath, "wb") as target:
                    shutil.copyfileobj(source, target)
            finally:
                source.close()

            if preserve_permissions in (PERMS_PRESERVE_SAFE, PERMS_PRESERVE_ALL):
                if preserve_permissions == PERMS_PRESERVE_ALL:
                    # preserve bits 0-11: sugrwxrwxrwx, this include
                    # sticky bit, uid bit, gid bit
                    mode = member.external_attr >> 16 & 0xFFF
                elif PERMS_PRESERVE_SAFE:
                    # preserve bits 0-8 only: rwxrwxrwx
                    mode = member.external_attr >> 16 & 0x1FF
                os.chmod(targetpath, mode)

            if force_valid_pyc_files and member.filename.endswith('.py'):
                pyc_name = importlib.util.cache_from_source(member.filename)
                if os.path.sep == '\\':
                    pyc_name = pyc_name.replace('\\', '/')
                if pyc_name in self.namelist():
                    pyc_file = self.open(pyc_name, pwd=pwd)
                    try:
                        force_valid_pyc_file(targetpath, pyc_file)
                    finally:
                        pyc_file.close()

            return targetpath
