import os
import posixpath
import zipfile

import os.path as op

from ..models.egg import _SPEC_DEPEND_LOCATION, _USR_PREFIX_LOCATION


class EggBuilder(object):
    def __init__(self, spec, cwd=None, compress=True):
        """Class to build our legacy egg."""
        if cwd is None:
            cwd = os.getcwd()

        self.spec = spec

        self.egg_path = op.join(cwd, spec.egg_name)

        if compress is True:
            self._fp = zipfile.ZipFile(self.egg_path, "w",
                                       zipfile.ZIP_DEFLATED)
        else:
            self._fp = zipfile.ZipFile(self.egg_path, "w")

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
