import glob
import io
import os
import shutil
import tempfile
import unittest
import zipfile2
from datetime import datetime, timezone

from hypothesis import given
from hypothesis.strategies import sampled_from

from ..pyc_utils import (
    validate_bytecode_header, force_valid_pyc_file, cache_from_source,
    source_from_cache, get_pyc_files
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
    def test_validate_bytecode_header_valid(self, egg_python):
        # Given
        valid_egg = EGG_PYTHON_TO_VALID_EGGS[egg_python]
        with zipfile2.ZipFile(valid_egg) as zip:
            py_files = [
                f for f in zip.namelist() if f.endswith('.py')
            ]
            py_file = py_files[0]
            zip_info = zip.getinfo(py_file)
            py_path = zip.extract(zip_info, self.hypothesis_tmpdir)
            ts = datetime(*zip_info.date_time, tzinfo=timezone.utc).timestamp()
            os.utime(py_path, (ts, ts))

            pyc_file = cache_from_source(py_file, egg_python)
            if os.path.sep == '\\':
                pyc_file = pyc_file.replace('\\', '/')
            pyc_path = zip.extract(pyc_file, self.hypothesis_tmpdir)

        # When/Then
        try:
            validate_bytecode_header(py_path, pyc_path, egg_python)
        except ValueError as e:
            self.fail(str(e))


    @given(sampled_from([u'2.7', u'3.5', u'3.6', u'3.8']))
    def test_validate_bytecode_header_stale(self, egg_python):
        # Given
        stale_egg = EGG_PYTHON_TO_STALE_EGGS[egg_python]
        with zipfile2.ZipFile(stale_egg) as zip:
            py_files = [
                f for f in zip.namelist() if f.endswith('.py')
            ]
            py_file = py_files[0]
            zip_info = zip.getinfo(py_file)
            py_path = zip.extract(zip_info, self.hypothesis_tmpdir)
            ts = datetime(*zip_info.date_time, tzinfo=timezone.utc).timestamp()
            os.utime(py_path, (ts, ts))

            pyc_file = cache_from_source(py_file, egg_python)
            if os.path.sep == '\\':
                pyc_file = pyc_file.replace('\\', '/')
            pyc_path = zip.extract(pyc_file, self.hypothesis_tmpdir)

        # When/Then
        with self.assertRaises(ValueError):
            validate_bytecode_header(py_path, pyc_path, egg_python)

    @given(sampled_from([u'2.7', u'3.5', u'3.6', u'3.8']))
    def test_force_valid_pyc_file(self, egg_python):
        # Given
        egg = EGG_PYTHON_TO_STALE_EGGS[egg_python]
        with zipfile2.ZipFile(egg) as zip:
            zip.extractall(self.hypothesis_tmpdir)

        pyc_file = get_pyc_files(self.hypothesis_tmpdir)[0]
        py_file = source_from_cache(pyc_file, egg_python)
        with self.assertRaises(AssertionError):
            self.assert_pyc_valid(pyc_file, egg_python)

        # When
        with io.FileIO(pyc_file, 'rb') as pyc:
            force_valid_pyc_file(py_file, pyc, egg_python)

        # Then
        self.assert_pyc_valid(pyc_file, egg_python)

    @given(sampled_from([u'2.7', u'3.5', u'3.6', u'3.8']))
    def test_cache_from_source(self, egg_python):
        # Given
        egg = EGG_PYTHON_TO_STALE_EGGS[egg_python]
        with zipfile2.ZipFile(egg) as zip:
            zip.extractall(self.hypothesis_tmpdir)

        pyc_file = get_pyc_files(self.hypothesis_tmpdir)[0]
        py_file = glob.glob(os.path.join(self.hypothesis_tmpdir, '*.py'))[0]

        # When
        result = cache_from_source(py_file, egg_python)

        # Then
        self.assertEqual(pyc_file, result)

    @given(sampled_from([u'2.7', u'3.5', u'3.6', u'3.8']))
    def test_source_from_cache(self, egg_python):
        # Given
        egg = EGG_PYTHON_TO_STALE_EGGS[egg_python]
        with zipfile2.ZipFile(egg) as zip:
            zip.extractall(self.hypothesis_tmpdir)

        pyc_file = get_pyc_files(self.hypothesis_tmpdir)[0]
        py_file = glob.glob(os.path.join(self.hypothesis_tmpdir, '*.py'))[0]

        # When
        result = source_from_cache(pyc_file, egg_python)

        # Then
        self.assertEqual(py_file, result)
