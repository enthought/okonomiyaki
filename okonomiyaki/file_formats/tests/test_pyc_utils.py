import glob
import io
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
    DUMMY_PKG_STALE_EGG_27, DUMMY_PKG_STALE_EGG_35, DUMMY_PKG_STALE_EGG_36,
    DUMMY_PKG_STALE_EGG_38
)


EGG_PYTHON_TO_STALE_EGGS = {
    u'2.7': DUMMY_PKG_STALE_EGG_27,
    u'3.5': DUMMY_PKG_STALE_EGG_35,
    u'3.6': DUMMY_PKG_STALE_EGG_36,
    u'3.8': DUMMY_PKG_STALE_EGG_38,
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
        try:
            f()
        finally:
            shutil.rmtree(self.hypothesis_tmpdir)

    def assert_pyc_valid(self, pyc_file, egg_python):
        py_file = source_from_cache(pyc_file, egg_python)
        try:
            validate_bytecode_header(py_file, pyc_file, egg_python)
        except ValueError as e:
            self.fail(str(e))

    @given(sampled_from([u'2.7', u'3.5', u'3.6', u'3.8']))
    def test_force_valid_pyc_file(self, egg_python):
        # Given
        egg = EGG_PYTHON_TO_STALE_EGGS[egg_python]
        with zipfile2.ZipFile(egg) as zip:
            zip.extractall(self.hypothesis_tmpdir)

        if sys.version_info.major == 3:
            search_path = os.path.join(self.hypothesis_tmpdir, '**', '*.pyc')
            pyc_file = glob.glob(search_path, recursive=True)[0]
        else:
            if egg_python.startswith(u'3'):
                search_path = os.path.join(
                    self.hypothesis_tmpdir, '__pycache__', '*.pyc'
                )
            else:
                search_path = os.path.join(self.hypothesis_tmpdir, '*.pyc')
            pyc_file = glob.glob(search_path)[0]
        py_file = source_from_cache(pyc_file, egg_python)
        with self.assertRaises(AssertionError):
            self.assert_pyc_valid(pyc_file, egg_python)

        # When
        with io.FileIO(pyc_file, 'rb') as pyc:
            force_valid_pyc_file(py_file, pyc, egg_python)

        # Then
        self.assert_pyc_valid(pyc_file, egg_python)
