import shutil
import tempfile
import unittest
import zipfile2

from hypothesis import given
from hypothesis.strategies import sampled_from

from ..egg_zip_file import EggZipFile, FORCE_VALID_PYC
from ..pyc_utils import (
    validate_bytecode_header, source_from_cache, get_pyc_files
)

from .common import (
    DUMMY_PKG_VALID_EGG_27, DUMMY_PKG_VALID_EGG_35, DUMMY_PKG_VALID_EGG_36,
    DUMMY_PKG_VALID_EGG_38,
)


EGG_PYTHON_TO_VALID_EGGS = {
    u'2.7': DUMMY_PKG_VALID_EGG_27,
    u'3.5': DUMMY_PKG_VALID_EGG_35,
    u'3.6': DUMMY_PKG_VALID_EGG_36,
    u'3.8': DUMMY_PKG_VALID_EGG_38,
}


class TestEggZipFile(unittest.TestCase):
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
    def test__get_egg_python(self, egg_python):
        # Given
        egg = EGG_PYTHON_TO_VALID_EGGS[egg_python]

        # When
        with EggZipFile(egg) as zip:
            zip_egg_python = zip.egg_python

        # Then
        self.assertEqual(egg_python, zip_egg_python)

    @given(sampled_from([u'2.7', u'3.5', u'3.6', u'3.8']))
    def test_valid_pyc_egg_with_zipfile2(self, egg_python):
        # Given
        egg = EGG_PYTHON_TO_VALID_EGGS[egg_python]

        # When
        with zipfile2.ZipFile(egg) as zip:
            zip.extractall(self.hypothesis_tmpdir)

        # Then
        pyc_file = get_pyc_files(self.hypothesis_tmpdir)[0]
        with self.assertRaises(AssertionError):
            self.assert_pyc_valid(pyc_file, egg_python)

    @given(sampled_from([u'2.7', u'3.5', u'3.6', u'3.8']))
    def test_valid_pyc_egg_with_eggzipfile_default(self, egg_python):
        # Given
        egg = EGG_PYTHON_TO_VALID_EGGS[egg_python]

        # When
        with EggZipFile(egg) as zip:
            zip.extractall(self.hypothesis_tmpdir)

        # Then
        pyc_file = get_pyc_files(self.hypothesis_tmpdir)[0]
        with self.assertRaises(AssertionError):
            self.assert_pyc_valid(pyc_file, egg_python)

    @given(sampled_from([u'2.7', u'3.5', u'3.6', u'3.8']))
    def test_valid_pyc_egg_with_eggzipfile_force(self, egg_python):
        # Given
        egg = EGG_PYTHON_TO_VALID_EGGS[egg_python]

        # When
        with EggZipFile(egg) as zip:
            zip.extractall(
                self.hypothesis_tmpdir, validate_pyc_files=FORCE_VALID_PYC
            )

        # Then
        pyc_file = get_pyc_files(self.hypothesis_tmpdir)[0]
        self.assert_pyc_valid(pyc_file, egg_python)
