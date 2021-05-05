import shutil
import tempfile
import unittest

from okonomiyaki.utils.pyc_checks import check_egg_pyc_files
from okonomiyaki.utils.test_data import (
    DUMMY_PKG_VALID_EGG, DUMMY_PKG_STALE_EGG
)


class TestPycChecks(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_egg_with_valid_pyc(self):
        # When
        failures = check_egg_pyc_files(DUMMY_PKG_VALID_EGG, self.tmpdir, True)

        # Then
        self.assertListEqual([], failures)
        self.assertEqual(0, len(failures))

    def test_egg_with_stale_pyc(self):
        # When
        failures = check_egg_pyc_files(DUMMY_PKG_STALE_EGG, self.tmpdir)

        # Then
        self.assertEqual(1, len(failures))
        failure = failures[0]
        self.assertEqual(ImportError.__name__, type(failure).__name__)
        failure_msg = failure.args[0].split(' (')[0]
        self.assertEqual(
            "bytecode is stale for 'dummy_pkg.cpython-36.pyc'", failure_msg
        )
