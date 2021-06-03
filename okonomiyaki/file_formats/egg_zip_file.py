import os
import shutil
import string
import zipfile

import zipfile2
from zipfile2 import (
    PERMS_PRESERVE_NONE, PERMS_PRESERVE_SAFE, PERMS_PRESERVE_ALL
)
from zipfile2.common import text_type
from zipfile2._zipfile import is_zipinfo_symlink, _unlink_if_exists

from ._egg_info import _SPEC_DEPEND_LOCATION, parse_rawspec
from .pyc_utils import force_valid_pyc_file, cache_from_source


# Python 2 compatible enum for validate_pyc_files arg choices
FORCE_VALID_PYC_NONE, FORCE_VALID_PYC = range(2)


class EggZipFile(zipfile2.ZipFile):
    def __init__(self, *args, **kwargs):
        super(EggZipFile, self).__init__(*args, **kwargs)
        self.egg_python = self._get_egg_python()

    def _get_egg_python(self):
        """Get the Python version of the egg from the spec depend file

        Returns
        -------
        str:
            Major minor Python version, e.g. "3.6"
        """
        try:
            with self.open(_SPEC_DEPEND_LOCATION) as spec_file:
                spec_depend = parse_rawspec(spec_file.read().decode())
                return spec_depend['python']
        except Exception:
            # Fail silently and continue for .pyc file issues
            return None

    def _force_valid_pyc_file(self, member, targetpath, pwd=None):
        """Force the .pyc file to be valid by setting the mtime of the
        corresponding .py file to the value in the .pyc header

        Parameters
        ----------
        member: ZipInfo
            The ZipFile member of the .py file
        targetpath: str
            The extracted path of the .py file
        pwd: bytes
            Optional password to decrypt files that is passed to ZipFile.open
        """
        try:
            pyc_name = cache_from_source(member.filename, self.egg_python)
        except Exception:
            # Fail silently and continue for issues with .pyc files
            return
        if os.path.sep == '\\':
            pyc_name = pyc_name.replace('\\', '/')
        if pyc_name in self.namelist():
            with self.open(pyc_name, pwd=pwd) as f:
                try:
                    force_valid_pyc_file(targetpath, f, self.egg_python)
                except Exception:
                    # Fail silently and continue for .pyc file issues
                    return

    def extract(self, member, path=None, pwd=None,
                preserve_permissions=PERMS_PRESERVE_NONE,
                validate_pyc_files=FORCE_VALID_PYC_NONE):
        """Extract member from the archive to the current working
           directory. Overrides zipfile2.ZipFile extract with the addition
           of validate_pyc_files parameter.

        Parameters
        ----------
        member: zipfile.ZipInfo or str
            must be an item of the list returned by namelist() or infolist()
        path: str
            path specifies a different directory to extract to.
        pwd: bytes
            Optional password to decrypt files that is passed to ZipFile.open
        preserve_permissions: int
            controls whether permissions of zipped files are preserved or
            not. Default is PERMS_PRESERVE_NONE - do not preserve any
            permissions. Other options are to preserve safe subset of
            permissions PERMS_PRESERVE_SAFE or all permissions
            PERMS_PRESERVE_ALL.
        validate_pyc_files: FORCE_VALID_PYC_NONE or FORCE_VALID_PYC
            Forces valid .pyc files by setting the timestamp of the
            corresponding .py file to the timestamp of the bytecode header.
        """
        if not isinstance(member, zipfile.ZipInfo):
            member = self.getinfo(member)

        if path is None:
            path = os.getcwd()

        return self._extract_member(
            member, path, pwd, preserve_permissions, validate_pyc_files
        )

    def extractall(self, path=None, members=None, pwd=None,
                   preserve_permissions=PERMS_PRESERVE_NONE,
                   validate_pyc_files=FORCE_VALID_PYC_NONE):
        """Extract all members from the archive to the current working
           directory. Overrides zipfile2.ZipFile extractall with the addition
           of validate_pyc_files parameter.

        Parameters
        ----------
        path: str
            path specifies a different directory to extract to.
        members: list
            is optional and must be a subset of the list returned by
            namelist() or infolist().
        pwd: bytes
            Optional password to decrypt files that is passed to ZipFile.open
        preserve_permissions: int
            controls whether permissions of zipped files are preserved or
            not. Default is PERMS_PRESERVE_NONE - do not preserve any
            permissions. Other options are to preserve safe subset of
            permissions PERMS_PRESERVE_SAFE or all permissions
            PERMS_PRESERVE_ALL.
        validate_pyc_files: FORCE_VALID_PYC_NONE or FORCE_VALID_PYC
            Forces valid .pyc files by setting the timestamp of the
            corresponding .py file to the timestamp of the bytecode header.
        """
        if members is None:
            members = self.namelist()

        for zipinfo in members:
            self.extract(
                zipinfo, path, pwd, preserve_permissions, validate_pyc_files
            )

    def _extract_member(self, member, targetpath, pwd, preserve_permissions,
                        validate_pyc_files):
        return self._extract_member_to(
            member, member.filename, targetpath, pwd, preserve_permissions,
            validate_pyc_files
        )

    def _extract_member_to(self, member, arcname, targetpath, pwd,
                           preserve_permissions, validate_pyc_files):
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

            use_force_valid_pyc_files = all((
                validate_pyc_files == FORCE_VALID_PYC,
                member.filename.endswith('.py'),
                self.egg_python is not None
            ))
            if use_force_valid_pyc_files:
                self._force_valid_pyc_file(member, targetpath, pwd)

            return targetpath
