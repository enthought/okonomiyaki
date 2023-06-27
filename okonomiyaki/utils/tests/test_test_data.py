import glob
from os.path import join
import sys

import zipfile2
from hypothesis import given
from hypothesis.strategies import sampled_from


from okonomiyaki.runtimes.runtime_metadata import IRuntimeMetadata

from ..test_data import DUMMY_RUNTIMES_DIRECTORY

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


runtime_paths = [
    join(DUMMY_RUNTIMES_DIRECTORY, f) for f
    in glob.glob(join(DUMMY_RUNTIMES_DIRECTORY, '*.runtime'))
    if 'r-3.0.0' not in f]


class TestDummyPythonRuntimes(unittest.TestCase):

    def _get_contents_of_runtime(self, runtime):
        with zipfile2.ZipFile(runtime) as zp:
            return zp.namelist()

    @given(sampled_from(runtime_paths))
    def test_reading_dummy_runtimes(self, runtime):
        # Then check the runtime is valid
        runtime_metadata = IRuntimeMetadata.factory_from_path(runtime)

        # additional checks for windows runtimes:
        if 'cpython-' in runtime and 'win_' in runtime:
            self.assertEqual(runtime_metadata.platform.os, 'windows')
            self.assertEqual(runtime_metadata.implementation, 'cpython')
            files_in_runtime = self._get_contents_of_runtime(runtime)
            self.assertIn(
                'pythonw.exe', files_in_runtime,
                msg="'pythonw.exe' is not in {0}".format(runtime))
