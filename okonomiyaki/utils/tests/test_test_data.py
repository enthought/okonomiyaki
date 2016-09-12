import sys
import zipfile2

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
        win_runtimes = [f for f in dir(test_data)
                        if 'CPYTHON' in f and 'WIN' in f]

        # When/Then
        for runtime in win_runtimes:
            path_to_runtime = test_data.__dict__[runtime]
            files_in_runtime = self._get_contents_of_runtime(path_to_runtime)
            self.assertIn(
                'pythonw.exe', files_in_runtime,
                msg="'pythonw.exe' is not in {}".format(runtime)
            )
