import zipfile

import six

if six.PY2:
    six.add_move(six.MovedModule("unittest", "unittest2", "unittest"))


class ZipFile(zipfile.ZipFile):
    """
    Compatibility class to support context manager on 2.6
    """
    def __enter__(self):
        return self

    def __exit__(self, *a, **kw):
        self.close()
