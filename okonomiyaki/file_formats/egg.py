import os
import os.path
import zipfile

import zipfile2

from ._egg_info import (
    _SPEC_DEPEND_LOCATION, _SPEC_SUMMARY_LOCATION
)
from ._package_info import _PKG_INFO_LOCATION


class EggBuilder(object):
    """
    Class to build eggs from an install tree. This is mostly useful to
    build eggs from non-python packages.
    """
    def __init__(self, egg_metadata, compress=True, cwd=None):
        self.cwd = cwd or os.getcwd()

        if egg_metadata.pkg_info is None:
            msg = ("EggBuilder does not accept EggMetadata instances with "
                   "a None pkg_info attribute.")
            raise ValueError(msg)

        if compress is True:
            flag = zipfile.ZIP_DEFLATED
        else:
            flag = zipfile.ZIP_STORED

        self._egg_metadata = egg_metadata
        self._fp = zipfile2.ZipFile(self.path, "w", flag)

        # Write those now so that they are at the beginning of the file.
        self._write_pkg_info()
        self._write_spec_summary()
        self._write_spec_depend()

    @property
    def path(self):
        return os.path.join(self.cwd, self._egg_metadata.egg_name)

    def close(self):
        self._fp.close()

    def __enter__(self):
        return self

    def __exit__(self, *a, **kw):
        self.commit()

    def add_iterator(self, iterator):
        """
        Add the files specified by the given iterator.

        Parameters
        ----------
        iterator: iterator
            An iterator yielding (path, arcname) pairs.
        """
        for path, arcname in iterator:
            self._fp.write(path, arcname)

    def add_file(self, path, archive_prefix=""):
        """ Add the given file to the egg, under the given archive prefix."""
        arcname = os.path.join(archive_prefix, os.path.basename(path))
        self._fp.write(path, arcname)

    def add_file_as(self, path, archive_name):
        """ Add the given file to the egg, under the given archive name."""
        self._fp.write(path, archive_name)

    def add_data(self, data, archive_name):
        """ Write the given data as the given archive name."""
        self._fp.writestr(archive_name, data)

    def add_tree(self, directory, archive_prefix=""):
        """
        Add the given directory to the egg, under the given archive_prefix.

        Parameters
        ----------
        directory: path
            A path to a directory. Every file in this directory will be
            included, recursively.
        """
        for root, dirs, files in os.walk(directory):
            for item in dirs + files:
                path = os.path.join(root, item)
                name = os.path.join(archive_prefix,
                                    os.path.relpath(path, directory))
                self._fp.write(path, name)

    def commit(self):
        """ Commit the metadata, and close the file.
        """
        self.close()

    def _write_spec_depend(self):
        spec_depend_string = self._egg_metadata.spec_depend_string
        self._fp.writestr(_SPEC_DEPEND_LOCATION, spec_depend_string)

    def _write_spec_summary(self):
        self._fp.writestr(_SPEC_SUMMARY_LOCATION, self._egg_metadata.summary)

    def _write_pkg_info(self):
        data = self._egg_metadata.pkg_info.to_string()
        self._fp.writestr(_PKG_INFO_LOCATION, data)
