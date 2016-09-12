import sys
import zipfile2

from okonomiyaki.runtimes.runtime_metadata import IRuntimeMetadata
from okonomiyaki.errors import UnsupportedMetadata

from .. import test_data

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestDummyPythonRuntimes(unittest.TestCase):

    def _get_contents_of_runtime(self, runtime):
        with zipfile2.ZipFile(runtime) as zp:
            return zp.namelist()

    def test_pythonw_in_dummy_runtime(self):
        """
        Ensure that pythonw.exe is included in all Windows runtimes
        """

        # Given
        runtime_paths = [getattr(test_data, attrib) for attrib in dir(test_data)
                         if isinstance(getattr(test_data, attrib), str)
                         and getattr(test_data, attrib).endswith('.runtime')]
        win_cpy_runtimes = []
        for runtime_path in runtime_paths:
            try:
                runtime_metadata = IRuntimeMetadata.factory_from_path(runtime_path)
                if (runtime_metadata.platform.os == 'windows'
                   and runtime_metadata.implementation == 'cpython'):
                    win_cpy_runtimes.append(runtime_path)
            except UnsupportedMetadata:
                continue

        # When/Then
        for win_runtime in win_cpy_runtimes:
            files_in_runtime = self._get_contents_of_runtime(win_runtime)
            self.assertIn(
                'pythonw.exe', files_in_runtime,
                msg="'pythonw.exe' is not in {0}".format(win_runtime)
            )
