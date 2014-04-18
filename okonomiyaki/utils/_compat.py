import zipfile

class ZipFile(zipfile.ZipFile):
    """
    Compatibility class to support context manager on 2.6
    """
    def __enter__(self):
        return self

    def __exit__(self, *a, **kw):
        self.close()
