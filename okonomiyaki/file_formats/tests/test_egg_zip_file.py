import glob
import os
import shutil
import tempfile
import unittest
import zipfile2

from ..egg_zip_file import EggZipFile
from ..pyc_utils import validate_bytecode_header, source_from_cache

from .common import DUMMY_PKG_VALID_EGG_36


class TestEggZipFile(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir)

    def assertPycValid(self, pyc_file, egg_python):
        py_file = source_from_cache(pyc_file, egg_python)
        try:
            validate_bytecode_header(py_file, pyc_file, egg_python)
        except ValueError as e:
            self.fail(str(e))

    def assertPycInvalid(self, pyc_file, egg_python):
        with self.assertRaises(AssertionError):
            self.assertPycValid(pyc_file, egg_python)

    def test_valid_pyc_egg_with_zipfile2(self):
        # Given
        egg = DUMMY_PKG_VALID_EGG_36

        # When
        with zipfile2.ZipFile(egg) as zip:
            zip.extractall(self.tmpdir)

        # Then
        pyc_file = glob.glob(os.path.join(self.tmpdir, '**', '*.pyc'))[0]
        self.assertPycInvalid(pyc_file, u'3.6')

    def test_valid_pyc_egg_with_eggzipfile_default(self):
        # Given
        egg = DUMMY_PKG_VALID_EGG_36

        # When
        with EggZipFile(egg) as zip:
            zip.extractall(self.tmpdir)

        # Then
        pyc_file = glob.glob(os.path.join(self.tmpdir, '**', '*.pyc'))[0]
        self.assertPycInvalid(pyc_file, u'3.6')

    def test_valid_pyc_egg_with_eggzipfile_force(self):
        # Given
        egg = DUMMY_PKG_VALID_EGG_36

        # When
        with EggZipFile(egg) as zip:
            zip.extractall(self.tmpdir, force_valid_pyc_files=True)

        # Then
        pyc_file = glob.glob(os.path.join(self.tmpdir, '**', '*.pyc'))[0]
        self.assertPycValid(pyc_file, u'3.6')
