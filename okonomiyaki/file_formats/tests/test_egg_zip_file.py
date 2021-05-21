import glob
import importlib
import io
import os
import shutil
import sys
import tempfile
import unittest
import zipfile2

from ..egg_zip_file import EggZipFile

from .common import DUMMY_PKG_VALID_EGG_36


class TestEggZipFile(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir)

    def assertPycValid(self, pyc_file):
        py_file = importlib.util.source_from_cache(pyc_file)
        statinfo = os.stat(py_file)
        try:
            importlib._bootstrap_external._validate_bytecode_header(
                io.FileIO(pyc_file, 'rb').read(),
                source_stats={'mtime': statinfo.st_mtime},
                path=pyc_file, name=os.path.basename(pyc_file)
            )
        except ImportError as e:
            self.fail(e.msg)

    def assertPycInvalid(self, pyc_file):
        py_file = importlib.util.source_from_cache(pyc_file)
        statinfo = os.stat(py_file)
        with self.assertRaises(ImportError):
            importlib._bootstrap_external._validate_bytecode_header(
                io.FileIO(pyc_file, 'rb').read(),
                source_stats={'mtime': statinfo.st_mtime},
                path=pyc_file, name=os.path.basename(pyc_file)
            )

    @unittest.skipIf(
        sys.version_info < (3, 6), 'only testing for Python 3.6 for now'
    )
    def test_valid_pyc_egg_with_zipfile2(self):
        # Given
        egg = DUMMY_PKG_VALID_EGG_36

        # When
        with zipfile2.ZipFile(egg) as zip:
            zip.extractall(self.tmpdir)

        # Then
        pyc_file = glob.glob(os.path.join(self.tmpdir, '**', '*.pyc'))[0]
        self.assertPycInvalid(pyc_file)

    @unittest.skipIf(
        sys.version_info < (3, 6), 'only testing for Python 3.6 for now'
    )
    def test_valid_pyc_egg_with_eggzipfile_default(self):
        # Given
        egg = DUMMY_PKG_VALID_EGG_36

        # When
        with EggZipFile(egg) as zip:
            zip.extractall(self.tmpdir)

        # Then
        pyc_file = glob.glob(os.path.join(self.tmpdir, '**', '*.pyc'))[0]
        self.assertPycInvalid(pyc_file)

    @unittest.skipIf(
        sys.version_info < (3, 6), 'only testing for Python 3.6 for now'
    )
    def test_valid_pyc_egg_with_eggzipfile_force(self):
        # Given
        egg = DUMMY_PKG_VALID_EGG_36

        # When
        with EggZipFile(egg) as zip:
            zip.extractall(self.tmpdir, force_valid_pyc_files=True)

        # Then
        pyc_file = glob.glob(os.path.join(self.tmpdir, '**', '*.pyc'))[0]
        self.assertPycValid(pyc_file)
