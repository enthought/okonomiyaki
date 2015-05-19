import os
import os.path
import posixpath
import zipfile

import zipfile2

from ..bundled.traitlets import HasTraits, Bool, Instance, Unicode

# those imports are for backward compatibility
from ._egg_info import (
    Dependency, EggMetadata, egg_name, is_egg_name_valid,
    parse_rawspec, split_egg_name
)  # flake8: noqa
from ._egg_info import (
    _SPEC_DEPEND_LOCATION, _USR_PREFIX_LOCATION
)


class EggBuilder(object):
    """
    Class to build eggs from an install tree. This is mostly useful to
    build eggs from non-python packages.
    """
    def __init__(self, egg_metadata, compress=True, cwd=None):
        self.cwd = cwd or os.getcwd()

        if compress is True:
            flag = zipfile.ZIP_DEFLATED
        else:
            flag = zipfile.ZIP_STORED

        self._egg_metadata = egg_metadata
        self._fp = zipfile2.ZipFile(self.path, "w", flag)

    @property
    def path(self):
        return os.path.join(self.cwd, self._egg_metadata.egg_name)

    def close(self):
        self._fp.close()

    def __enter__(self):
        return self

    def __exit__(self, *a, **kw):
        self.commit()

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
        self._write_spec_depend()
        self.close()

    def _write_spec_depend(self):
        spec_depend_string = self._egg_metadata.spec_depend_string
        self._fp.writestr(_SPEC_DEPEND_LOCATION, spec_depend_string)
