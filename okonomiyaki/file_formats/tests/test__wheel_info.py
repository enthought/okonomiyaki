import unittest

from okonomiyaki.errors import OkonomiyakiError
from .._wheel_info import WheelInfo


class TestWheelInfo(unittest.TestCase):
    def test_pure_python(self):
        # Given
        path = "okonomiyaki-0.17.0.dev807-py2-none-any.whl"

        # When
        w_info = WheelInfo.from_path(path)

        # Then
        self.assertEqual(w_info.name, u"okonomiyaki")
        self.assertEqual(w_info.version, u"0.17.0.dev807")
        self.assertEqual(w_info.python_tags, (u"py2",))
        self.assertEqual(w_info.python_abi_tags, (u"none",))
        self.assertEqual(w_info.platforms, (u"any",))
        self.assertIsNone(w_info.build)

    def test_multi_platform(self):
        # Given
        path = (
            u"numpy-1.13.0-cp27-cp27m-macosx_10_6_intel.macosx_10_9_intel.macosx_10_9_x86_64"
            ".macosx_10_10_intel.macosx_10_10_x86_64.whl"
        )

        # When
        w_info = WheelInfo.from_path(path)

        # Then
        self.assertEqual(w_info.name, u"numpy")
        self.assertEqual(w_info.version, u"1.13.0")
        self.assertEqual(w_info.python_tags, (u"cp27",))
        self.assertEqual(w_info.python_abi_tags, (u"cp27m",))
        self.assertEqual(
            w_info.platforms,
            (u"macosx_10_6_intel", "macosx_10_9_intel", "macosx_10_9_x86_64",
             "macosx_10_10_intel", "macosx_10_10_x86_64")
        )
        self.assertIsNone(w_info.build)

    def test_invalid(self):
        # Given
        path = u"okonomiyaki-0.17.0.dev806-py2.7.egg"

        # When/Then
        with self.assertRaises(OkonomiyakiError):
            WheelInfo.from_path(path)
