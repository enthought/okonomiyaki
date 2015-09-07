import os.path
import unittest

from okonomiyaki.utils.test_data import (
    JULIA_DEFAULT_0_3_11_RH5_64, PYTHON_CPYTHON_2_7_10_RH5_64,
)
from ..runtime_metadata import runtime_metadata_factory
from ..runtime_info import runtime_info_from_metadata, runtime_info_from_json


class TestPythonRuntimeInfoV1(unittest.TestCase):
    def test_simple(self):
        # Given
        path = PYTHON_CPYTHON_2_7_10_RH5_64
        metadata = runtime_metadata_factory(path)
        name = u"test"
        prefix = os.path.abspath(os.path.join(u"foo", u"bar"))

        # When
        runtime_info = runtime_info_from_metadata(metadata, prefix, name)

        # Then
        self.assertEqual(runtime_info.prefix, prefix)
        self.assertEqual(runtime_info.name, name)
        self.assertEqual(
            runtime_info.executable,
            os.path.join(prefix, "bin", "python")
        )

    def test_json_round_trip(self):
        # Given
        path = PYTHON_CPYTHON_2_7_10_RH5_64
        metadata = runtime_metadata_factory(path)
        name = u"test"
        prefix = os.path.abspath(os.path.join(u"foo", u"bar"))

        r_runtime_info = runtime_info_from_metadata(metadata, prefix, name)

        # When
        runtime_info = runtime_info_from_json(r_runtime_info.to_json_dict())

        # Then
        self.assertEqual(runtime_info, r_runtime_info)


class TestJuliaRuntimeInfoV1(unittest.TestCase):
    def test_simple(self):
        # Given
        path = JULIA_DEFAULT_0_3_11_RH5_64
        metadata = runtime_metadata_factory(path)
        name = u"test"
        prefix = os.path.abspath(os.path.join(u"foo", u"bar"))

        # When
        runtime_info = runtime_info_from_metadata(metadata, prefix, name)

        # Then
        self.assertEqual(runtime_info.prefix, prefix)
        self.assertEqual(runtime_info.name, name)
        self.assertEqual(
            runtime_info.executable,
            os.path.join(prefix, "bin", "julia")
        )

    def test_json_round_trip(self):
        # Given
        path = JULIA_DEFAULT_0_3_11_RH5_64
        metadata = runtime_metadata_factory(path)
        name = u"test"
        prefix = os.path.abspath(os.path.join(u"foo", u"bar"))

        r_runtime_info = runtime_info_from_metadata(metadata, prefix, name)

        # When
        runtime_info = runtime_info_from_json(r_runtime_info.to_json_dict())

        # Then
        self.assertEqual(runtime_info, r_runtime_info)
