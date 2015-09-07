import os.path
import shutil
import unittest

import zipfile2

from okonomiyaki.errors import InvalidMetadata, UnsupportedMetadata
from okonomiyaki.utils import tempdir
from okonomiyaki.utils.test_data import (
    JULIA_DEFAULT_0_3_11_RH5_64, PYTHON_CPYTHON_2_7_10_RH5_64,
    PYTHON_CPYTHON_2_7_10_RH5_64_INVALID, R_DEFAULT_3_0_0_RH5_64
)

from ..runtime import (
    JuliaRuntimeMetadataV1, PythonRuntimeMetadataV1, RuntimeVersion,
    is_runtime_path_valid, runtime_metadata_factory
)


class TestPythonMetadataV1(unittest.TestCase):
    def test_simple(self):
        # Given
        path = PYTHON_CPYTHON_2_7_10_RH5_64

        # When
        metadata = PythonRuntimeMetadataV1.from_path(path)

        # Then
        self.assertTrue(is_runtime_path_valid(path))
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
        self.assertEqual(metadata.scriptsdir, "${prefix}/bin")
        self.assertEqual(
            metadata.site_packages,
            "${prefix}/lib/python2.7/site-packages"
        )

    def test_invalid(self):
        # Given
        path = "python-cpython-2.7.10-1-rh5_64.zip"

        # When/Then
        with self.assertRaises(InvalidMetadata):
            PythonRuntimeMetadataV1.from_path(path)

        # Then
        self.assertFalse(is_runtime_path_valid(path))

        # Given
        path = "python_cpython_2.7.10-1_rh5_64.runtime"

        # When/Then
        with self.assertRaises(InvalidMetadata):
            PythonRuntimeMetadataV1.from_path(path)

        # Then
        self.assertFalse(is_runtime_path_valid(path))

        # Given
        path = "python-cpython-2.7.10_rh5_x86_64.runtime"

        # When/Then
        with self.assertRaises(InvalidMetadata):
            PythonRuntimeMetadataV1.from_path(path)

        # Then
        self.assertFalse(is_runtime_path_valid(path))

        # When/Then
        with tempdir() as d:
            path = os.path.join(d, "foo.zip")
            with zipfile2.ZipFile(path, "w") as zp:
                pass

            with self.assertRaises(InvalidMetadata):
                PythonRuntimeMetadataV1.from_path(path)

            with zipfile2.ZipFile(path, "w") as zp:
                with self.assertRaises(InvalidMetadata):
                    PythonRuntimeMetadataV1.from_path(zp)


class TestJuliaRuntimeMetadataV1(unittest.TestCase):
    def test_simple(self):
        # Given
        path = JULIA_DEFAULT_0_3_11_RH5_64

        # When
        metadata = JuliaRuntimeMetadataV1.from_path(path)

        # Then
        self.assertTrue(metadata.language, "julia")
        self.assertEqual(metadata.filename, os.path.basename(path))

        self.assertEqual(metadata.language, "julia")
        self.assertEqual(metadata.implementation, "default")
        self.assertEqual(
            metadata.version,
            RuntimeVersion.from_string("0.3.11-1")
        )
        self.assertEqual(metadata.build_revision, "483dbf5279")
        self.assertEqual(metadata.executable, "${prefix}/bin/julia")
        self.assertEqual(metadata.paths, ("${prefix}/bin",))
        self.assertEqual(metadata.post_install, tuple())


class TestRuntimeMetadataFactory(unittest.TestCase):
    def test_simple(self):
        # Given
        path = PYTHON_CPYTHON_2_7_10_RH5_64

        # When
        metadata = runtime_metadata_factory(path)

        # Then
        self.assertIsInstance(metadata, PythonRuntimeMetadataV1)

        # Given
        path = JULIA_DEFAULT_0_3_11_RH5_64

        # When
        metadata = runtime_metadata_factory(path)

        # Then
        self.assertIsInstance(metadata, JuliaRuntimeMetadataV1)

        # Given
        path = JULIA_DEFAULT_0_3_11_RH5_64

        # When
        with zipfile2.ZipFile(path) as zp:
            metadata = runtime_metadata_factory(zp)

        # Then
        self.assertIsInstance(metadata, JuliaRuntimeMetadataV1)

    def test_invalid(self):
        # Given
        path = R_DEFAULT_3_0_0_RH5_64

        # When/Then
        with self.assertRaises(UnsupportedMetadata):
            runtime_metadata_factory(path)

        # Given
        path = PYTHON_CPYTHON_2_7_10_RH5_64_INVALID

        # When/Then
        with tempdir() as d:
            target = os.path.join(
                d, os.path.basename(path).replace(".invalid", "")
            )
            shutil.copy(path, target)

            with self.assertRaises(InvalidMetadata):
                runtime_metadata_factory(target)
