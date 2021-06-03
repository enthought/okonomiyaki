import os
import shutil
import tempfile
import unittest
import zipfile2

from hypothesis import given
from hypothesis.strategies import sampled_from

from ..egg_zip_file import EggZipFile, FORCE_VALID_PYC
from ..pyc_utils import (
    validate_bytecode_header, cache_from_source, source_from_cache,
    get_pyc_files
)

from .common import (
    DUMMY_PKG_VALID_EGG_27, DUMMY_PKG_VALID_EGG_35, DUMMY_PKG_VALID_EGG_36,
    DUMMY_PKG_VALID_EGG_38, DUMMY_PKG_STALE_EGG_27, DUMMY_PKG_STALE_EGG_35,
    DUMMY_PKG_STALE_EGG_36, DUMMY_PKG_STALE_EGG_38,
)


EGG_PYTHON_TO_VALID_EGGS = {
    u'2.7': DUMMY_PKG_VALID_EGG_27,
    u'3.5': DUMMY_PKG_VALID_EGG_35,
    u'3.6': DUMMY_PKG_VALID_EGG_36,
    u'3.8': DUMMY_PKG_VALID_EGG_38,
}
EGG_PYTHON_TO_STALE_EGGS = {
    u'2.7': DUMMY_PKG_STALE_EGG_27,
    u'3.5': DUMMY_PKG_STALE_EGG_35,
    u'3.6': DUMMY_PKG_STALE_EGG_36,
    u'3.8': DUMMY_PKG_STALE_EGG_38,
}


class TestEggZipFile(unittest.TestCase):
    def execute_example(self, f):
        """Hypothesis custom function execution to allow a tmpdir with each
           execution of a given hypothesis value
           (self.tmpdir doesn't change between hypothesis executions.)
        """
        self.tmpdir = tempfile.mkdtemp()
        try:
            f()
        finally:
            shutil.rmtree(self.tmpdir)

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
        with EggZipFile(egg) as zip_:
            zip_egg_python = zip_.egg_python

        # Then
        self.assertEqual(egg_python, zip_egg_python)

    @given(sampled_from([u'2.7', u'3.5', u'3.6', u'3.8']))
    def test__force_valid_pyc_file(self, egg_python):
        # Given
        py_file = 'dummy_pkg.py'
        egg = EGG_PYTHON_TO_STALE_EGGS[egg_python]
        pyc_file = cache_from_source(py_file, egg_python).replace('\\', '/')

        with EggZipFile(egg) as zip_:
            py_file_info = zip_.getinfo(py_file)
            py_target_path = zip_.extract(py_file_info, self.tmpdir)
            pyc_target_path = zip_.extract(pyc_file, self.tmpdir)

            # When
            zip_._force_valid_pyc_file(py_file_info, py_target_path)

        # Then
        self.assert_pyc_valid(pyc_target_path, egg_python)

    @given(sampled_from([u'2.7', u'3.5', u'3.6', u'3.8']))
    def test_valid_pyc_egg_with_zipfile2(self, egg_python):
        # Given
        egg = EGG_PYTHON_TO_VALID_EGGS[egg_python]

        # When
        with zipfile2.ZipFile(egg) as zip_:
            zip_.extractall(self.tmpdir)

        # Then
        pyc_file = get_pyc_files(self.tmpdir)[0]
        with self.assertRaises(AssertionError):
            self.assert_pyc_valid(pyc_file, egg_python)

    @given(sampled_from([u'2.7', u'3.5', u'3.6', u'3.8']))
    def test_valid_pyc_egg_with_eggzipfile_default(self, egg_python):
        # Given
        egg = EGG_PYTHON_TO_VALID_EGGS[egg_python]

        # When
        with EggZipFile(egg) as zip_:
            zip_.extractall(self.tmpdir)

        # Then
        pyc_file = get_pyc_files(self.tmpdir)[0]
        with self.assertRaises(AssertionError):
            self.assert_pyc_valid(pyc_file, egg_python)

    @given(sampled_from([u'2.7', u'3.5', u'3.6', u'3.8']))
    def test_valid_pyc_egg_with_eggzipfile_force(self, egg_python):
        # Given
        egg = EGG_PYTHON_TO_VALID_EGGS[egg_python]

        # When
        with EggZipFile(egg) as zip_:
            zip_.extractall(
                self.tmpdir, validate_pyc_files=FORCE_VALID_PYC
            )

        # Then
        pyc_file = get_pyc_files(self.tmpdir)[0]
        self.assert_pyc_valid(pyc_file, egg_python)
