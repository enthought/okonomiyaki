import os
import sys
import zipfile2

from okonomiyaki.runtimes.runtime_metadata import IRuntimeMetadata

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
        python_runtimes = [attribute for attribute in dir(test_data)
                           if attribute.startswith('PYTHON')]
        win_runtimes = []
        for runtime in python_runtimes:
            runtime_path = getattr(test_data, runtime)
            if os.path.splitext(runtime_path)[-1] == '.runtime':
                runtime_metadata = IRuntimeMetadata.factory_from_path(runtime_path)
                if runtime_metadata.platform.os == 'windows':
                    win_runtimes.append((runtime, runtime_path))

        # When/Then
        for runtime_name, runtime_path in win_runtimes:
            files_in_runtime = self._get_contents_of_runtime(runtime_path)
            self.assertIn(
                'pythonw.exe', files_in_runtime,
                msg="'pythonw.exe' is not in {0}".format(runtime_name)
            )
