import glob
import importlib
import io
import os
import shutil
import sys
import tempfile
import unittest
import zipfile2

from ..egg_zip_file import force_valid_pyc_file, EggZipFile

from .common import DUMMY_PKG_VALID_EGG_36, DUMMY_PKG_STALE_EGG_36


@unittest.skipIf(
    sys.version_info < (3, 6), 'only testing for Python 3.6 for now'
)
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

    def test_force_valid_pyc_file(self):
        # Given
        egg = DUMMY_PKG_STALE_EGG_36
        with zipfile2.ZipFile(egg) as zip:
            zip.extractall(self.tmpdir)
        pyc_file = glob.glob(os.path.join(self.tmpdir, '**', '*.pyc'))[0]
        py_file = importlib.util.source_from_cache(pyc_file)
        self.assertPycInvalid(pyc_file)

        # When
        force_valid_pyc_file(py_file, pyc_file)

        # Then
        self.assertPycValid(pyc_file)

    def test_valid_pyc_egg_with_zipfile2(self):
        # Given
        egg = DUMMY_PKG_VALID_EGG_36

        # When
        with zipfile2.ZipFile(egg) as zip:
            zip.extractall(self.tmpdir)

        # Then
        pyc_file = glob.glob(os.path.join(self.tmpdir, '**', '*.pyc'))[0]
        self.assertPycInvalid(pyc_file)

    def test_valid_pyc_egg_with_eggzipfile_default(self):
        # Given
        egg = DUMMY_PKG_VALID_EGG_36

        # When
        with EggZipFile(egg) as zip:
            zip.extractall(self.tmpdir)

        # Then
        pyc_file = glob.glob(os.path.join(self.tmpdir, '**', '*.pyc'))[0]
        self.assertPycInvalid(pyc_file)

    def test_valid_pyc_egg_with_eggzipfile_force(self):
        # Given
        egg = DUMMY_PKG_VALID_EGG_36

        # When
        with EggZipFile(egg) as zip:
            zip.extractall(self.tmpdir, force_valid_pyc_files=True)

        # Then
        pyc_file = glob.glob(os.path.join(self.tmpdir, '**', '*.pyc'))[0]
        self.assertPycValid(pyc_file)
