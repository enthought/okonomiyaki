import sys

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from ...errors import OkonomiyakiError
from ...platforms import EPDPlatform
from ..setuptools_egg import SetuptoolsEggMetadata, parse_filename
from .common import PIP_SETUPTOOLS_EGG, TRAITS_SETUPTOOLS_EGG


class TestParseFilename(unittest.TestCase):
    def test_simple(self):
        # Given
        path = "nose-1.2.1-py2.6.egg"

        # When
        name, version, pyver, platform = parse_filename(path)

        # Then
        self.assertEqual(name, "nose")
        self.assertEqual(version, "1.2.1")
        self.assertEqual(pyver, "2.6")
        self.assertIsNone(platform)

    def test_simple_with_extension_osx(self):
        # Given
        path = "dc_analysis-1.0-py2.7-macosx-10.6-x86_64.egg"

        # When
        name, version, pyver, platform = parse_filename(path)

        # Then
        self.assertEqual(name, "dc_analysis")
        self.assertEqual(version, "1.0")
        self.assertEqual(pyver, "2.7")
        self.assertEqual(platform, "macosx-10.6-x86_64")

    def test_simple_with_extension(self):
        # Given
        path = "numpy-1.9.1-py2.6-win-amd64.egg"

        # When
        name, version, pyver, platform = parse_filename(path)

        # Then
        self.assertEqual(name, "numpy")
        self.assertEqual(version, "1.9.1")
        self.assertEqual(pyver, "2.6")
        self.assertEqual(platform, "win-amd64")

    def test_enthought_egg(self):
        # Given
        path = "nose-1.2.1-1.egg"

        # When/Then
        with self.assertRaises(OkonomiyakiError):
            parse_filename(path)


class TestSetuptoolsEggMetadata(unittest.TestCase):
    def test_simple(self):
        # Given
        path = PIP_SETUPTOOLS_EGG

        # When
        metadata = SetuptoolsEggMetadata.from_egg(path)

        # Then
        self.assertEqual(metadata.name, "pip")
        self.assertEqual(metadata.version, "7.0.3")
        self.assertEqual(metadata.python_tag, "cp34")
        self.assertIsNone(metadata.abi_tag)
        self.assertIsNone(metadata.platform_tag)

        # When
        metadata = SetuptoolsEggMetadata.from_egg(path, abi_tag=None)

        # Then
        self.assertEqual(metadata.name, "pip")
        self.assertEqual(metadata.version, "7.0.3")
        self.assertEqual(metadata.python_tag, "cp34")
        self.assertIsNone(metadata.abi_tag)
        self.assertIsNone(metadata.platform_tag)

        # Given
        platform = EPDPlatform.from_epd_string("win-32")
        python_tag = "cp34"
        abi_tag = "cp34m"

        # When
        metadata = SetuptoolsEggMetadata.from_egg(
            path, platform, python_tag, abi_tag,
        )

        # Then
        self.assertEqual(metadata.name, "pip")
        self.assertEqual(metadata.version, "7.0.3")
        self.assertEqual(metadata.python_tag, "cp34")
        self.assertEqual(metadata.abi_tag, "cp34m")
        self.assertEqual(metadata.platform_tag, "win32")

    def test_platform_specific(self):
        # Given
        path = TRAITS_SETUPTOOLS_EGG

        # When
        platform = EPDPlatform.from_epd_string("osx-64")
        metadata = SetuptoolsEggMetadata.from_egg(path, platform)

        # Then
        self.assertEqual(metadata.name, "traits")
        self.assertEqual(metadata.version, "4.6.0.dev235")
        self.assertEqual(metadata.python_tag, "cp27")
        self.assertEqual(metadata.abi_tag, "cp27m")
        self.assertEqual(metadata.platform_tag, "macosx_10_6_x86_64")

        # When/Then
        with self.assertRaises(OkonomiyakiError):
            SetuptoolsEggMetadata.from_egg(path)
