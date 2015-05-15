import os
import posixpath
import zipfile

import os.path as op

from ..bundled.traitlets import HasTraits, Bool, Instance, Unicode

# those imports are for backward compatibility
from ._egg_info import (
    Dependency, LegacySpecDepend, egg_name, info_from_z, is_egg_name_valid,
    parse_rawspec, split_egg_name
)  # flake8: noqa
from ._egg_info import (
    _SPEC_DEPEND_LOCATION, _USR_PREFIX_LOCATION, LegacySpec
)


class EggBuilder(HasTraits):
    """
    Class to build eggs from an install tree.
    """
    compress = Bool()
    """
    True if the egg must be compressed.
    """
    cwd = Unicode()
    """
    Root directory from which paths will be resolved.
    """
    spec = Instance(LegacySpec)
    """
    Spec instance
    """

    _fp = Instance(zipfile.ZipFile)

    def __init__(self, spec, cwd=None, compress=True):
        if cwd is None:
            cwd = os.getcwd()

        super(EggBuilder, self).__init__(spec=spec, cwd=cwd, compres=compress)

        if compress is True:
            self._fp = zipfile.ZipFile(self.egg_path, "w",
                                       zipfile.ZIP_DEFLATED)
        else:
            self._fp = zipfile.ZipFile(self.egg_path, "w")

    @property
    def egg_path(self):
        return op.join(self.cwd, self.spec.egg_name)

    def close(self):
        self._write_spec_depend()
        self._fp.close()

    def __enter__(self):
        return self

    def __exit__(self, *a, **kw):
        self.close()

    def add_usr_files_iterator(self, it):
        """
        Add the given files to the egg inside the usr subdirectory (i.e. not
        in site-packages).

        Parameters
        ----------
        it: generator
            Assumed to yield pairs (path, arcname) where path is the path of
            the file to write into the archive, and arcname the archive name
            relative to the usr subdirectory, i.e. ('foo.h', 'include/foo.h')
            will write foo.h as EGG-INFO/usr/include/foo.h).
        """
        for path, arcname in it:
            self._fp.write(path, posixpath.join(_USR_PREFIX_LOCATION, arcname))

    def _write_spec_depend(self):
        self._fp.writestr(_SPEC_DEPEND_LOCATION, self.spec.depend_content())
