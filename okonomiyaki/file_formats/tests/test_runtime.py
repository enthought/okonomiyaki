import os.path
import unittest

import zipfile2

from okonomiyaki.errors import InvalidMetadata
from okonomiyaki.utils import tempdir
from okonomiyaki.utils.test_data import PYTHON_CPYTHON_2_7_10_RH5_64

from ..runtime import (
    RuntimeMetadataV1, RuntimeVersion, is_runtime_path_valid
)


class TestRuntimeMetadataV1(unittest.TestCase):
    def test_simple(self):
        # Given
        path = PYTHON_CPYTHON_2_7_10_RH5_64

        # When
        metadata = RuntimeMetadataV1.from_path(path)

        # Then
        self.assertTrue(metadata.language, "python")
        self.assertEqual(metadata.filename, os.path.basename(path))

        self.assertEqual(metadata.language, "python")
        self.assertEqual(metadata.implementation, "cpython")
        self.assertEqual(
            metadata.version,
            RuntimeVersion.from_string("2.7.10-1")
        )
        self.assertEqual(metadata.build_revision, "2.1.0-dev570")
        self.assertEqual(metadata.executable, "${prefix}/bin/python")
        self.assertEqual(metadata.paths, ("${prefix}/bin",))
        self.assertEqual(
            metadata.post_install,
            ("${executable}",
             "${prefix}/lib/python2.7/custom_tools/fix-scripts.py")
        )

    def test_invalid(self):
        # Given
        path = "python-cpython-2.7.10-1-rh5_64.zip"

        # When/Then
        with self.assertRaises(InvalidMetadata):
            RuntimeMetadataV1.from_path(path)

        # Then
        self.assertFalse(is_runtime_path_valid(path))

        # Given
        path = "python_cpython_2.7.10-1_rh5_64.runtime"

        # When/Then
        with self.assertRaises(InvalidMetadata):
            RuntimeMetadataV1.from_path(path)

        # Then
        self.assertFalse(is_runtime_path_valid(path))

        # Given
        path = "python-cpython-2.7.10_rh5_x86_64.runtime"

        # When/Then
        with self.assertRaises(InvalidMetadata):
            RuntimeMetadataV1.from_path(path)

        # Then
        self.assertFalse(is_runtime_path_valid(path))

        # When/Then
        with tempdir() as d:
            path = os.path.join(d, "foo.zip")
            with zipfile2.ZipFile(path, "w") as zp:
                pass

            with self.assertRaises(InvalidMetadata):
                RuntimeMetadataV1.from_path(path)

            with zipfile2.ZipFile(path, "w") as zp:
                with self.assertRaises(InvalidMetadata):
                    RuntimeMetadataV1.from_path(zp)
