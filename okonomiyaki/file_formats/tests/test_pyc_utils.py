import glob
import os
import shutil
import tempfile
import unittest
import zipfile2

from ..pyc_utils import (
    validate_bytecode_header, force_valid_pyc_file, source_from_cache
)

from .common import DUMMY_PKG_STALE_EGG_36


class TestPycUtils(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir)

    def assertPycValid(self, pyc_file):
        py_file = source_from_cache(pyc_file, (3,))
        try:
            validate_bytecode_header(py_file, pyc_file, (3, 6))
        except ImportError as e:
            self.fail(str(e))

    def assertPycInvalid(self, pyc_file):
        with self.assertRaises(AssertionError):
            self.assertPycValid(pyc_file)

    def test_force_valid_pyc_file(self):
        # Given
        egg = DUMMY_PKG_STALE_EGG_36
        with zipfile2.ZipFile(egg) as zip:
            zip.extractall(self.tmpdir)
        pyc_file = glob.glob(os.path.join(self.tmpdir, '**', '*.pyc'))[0]
        py_file = source_from_cache(pyc_file, (3,))
        self.assertPycInvalid(pyc_file)

        # When
        force_valid_pyc_file(py_file, pyc_file, (3, 6))

        # Then
        self.assertPycValid(pyc_file)
