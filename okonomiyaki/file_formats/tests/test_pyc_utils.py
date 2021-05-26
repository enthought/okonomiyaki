import glob
import os
import shutil
import sys
import tempfile
import unittest
import zipfile2

from hypothesis import given
from hypothesis.strategies import sampled_from

from ..pyc_utils import (
    validate_bytecode_header, force_valid_pyc_file, source_from_cache
)
from .common import (
    DUMMY_PKG_STALE_EGG_36, DUMMY_PKG_STALE_EGG_35, DUMMY_PKG_STALE_EGG_27
)


TARGET_VERSION_TO_STALE_EGGS = {
    (2, 7): DUMMY_PKG_STALE_EGG_27,
    (3, 5): DUMMY_PKG_STALE_EGG_35,
    (3, 6): DUMMY_PKG_STALE_EGG_36,
}


class TestPycUtils(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir)

    def execute_example(self, f):
        """Hypothesis custom function execution to allow a tmpdir with each
           execution of a given hypothesis value
           (self.tmpdir doesn't change between hypothesis executions.)
        """
        self.hypothesis_tmpdir = tempfile.mkdtemp()
        f()
        shutil.rmtree(self.hypothesis_tmpdir)

    def assertPycValid(self, pyc_file, target_version_info):
        py_file = source_from_cache(pyc_file, target_version_info)
        try:
            validate_bytecode_header(py_file, pyc_file, target_version_info)
        except ImportError as e:
            self.fail(str(e))

    def assertPycInvalid(self, pyc_file, target_version_info):
        with self.assertRaises(AssertionError):
            self.assertPycValid(pyc_file, target_version_info)

    @given(sampled_from([(2, 7), (3, 5), (3, 6)]))
    def test_force_valid_pyc_file(self, target_version_info):
        # Given
        egg = TARGET_VERSION_TO_STALE_EGGS[target_version_info]
        with zipfile2.ZipFile(egg) as zip:
            zip.extractall(self.hypothesis_tmpdir)

        if sys.version_info.major == 3:
            search_path = os.path.join(self.hypothesis_tmpdir, '**', '*.pyc')
            pyc_file = glob.glob(search_path, recursive=True)[0]
        else:
            if target_version_info[0] == 3:
                search_path = os.path.join(
                    self.hypothesis_tmpdir, '__pycache__', '*.pyc'
                )
            else:
                search_path = os.path.join(self.hypothesis_tmpdir, '*.pyc')
            pyc_file = glob.glob(search_path)[0]
        py_file = source_from_cache(pyc_file, target_version_info)
        self.assertPycInvalid(pyc_file, target_version_info)

        # When
        force_valid_pyc_file(py_file, pyc_file, target_version_info)

        # Then
        self.assertPycValid(pyc_file, target_version_info)
