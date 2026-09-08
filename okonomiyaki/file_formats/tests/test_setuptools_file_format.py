import unittest
from unittest import mock

from parameterized import parameterized

from okonomiyaki.errors import OkonomiyakiError
from okonomiyaki.platforms import EPDPlatform
from okonomiyaki.versions import RuntimeVersion
from .. import setuptools_egg
from ..setuptools_egg import (
    SetuptoolsEggMetadata, _guess_abi_from_running_python, parse_filename)
from .common import (
    PIP_SETUPTOOLS_EGG, TRAITS_SETUPTOOLS_EGG, TRAITS_SETUPTOOLS_OSX_cp38_EGG,
    TRAITS_SETUPTOOLS_WIN_cp38_EGG, TRAITS_SETUPTOOLS_LINUX_cp38_EGG)


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
            path, platform, python_tag, abi_tag)

        # Then
        self.assertEqual(metadata.name, "pip")
        self.assertEqual(metadata.version, "7.0.3")
        self.assertEqual(metadata.python_tag, "cp34")
        self.assertEqual(metadata.abi_tag, "cp34m")
        self.assertEqual(metadata.platform_tag, "win32")

    def test_platform_specific(self):
        # Given
        path = TRAITS_SETUPTOOLS_EGG
        platform = EPDPlatform.from_epd_string("osx-64")

        # When
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

    def test_macos_cp38_egg(self):
        # Given
        path = TRAITS_SETUPTOOLS_OSX_cp38_EGG
        python = RuntimeVersion.from_string('3.8.10')
        platform = EPDPlatform.from_epd_string("osx-64", python)

        # When
        metadata = SetuptoolsEggMetadata.from_egg(path, platform)

        # Then
        self.assertEqual(metadata.name, "traits")
        self.assertEqual(metadata.version, "6.3.0.dev1702")
        self.assertEqual(metadata.python_tag, "cp38")
        self.assertEqual(metadata.abi_tag, "cp38")
        self.assertEqual(metadata.platform_tag, "macosx_10_14_x86_64")

        # When/Then
        with self.assertRaises(OkonomiyakiError):
            SetuptoolsEggMetadata.from_egg(path)

    def test_linux_cp38_egg(self):
        # Given
        path = TRAITS_SETUPTOOLS_LINUX_cp38_EGG
        python = RuntimeVersion.from_string('3.8.10')
        platform = EPDPlatform.from_epd_string("rh7-64", python)

        # When
        metadata = SetuptoolsEggMetadata.from_egg(path, platform)

        # Then
        self.assertEqual(metadata.name, "traits")
        self.assertEqual(metadata.version, "6.3.0.dev1702")
        self.assertEqual(metadata.python_tag, "cp38")
        self.assertEqual(metadata.abi_tag, "cp38")
        self.assertEqual(metadata.platform_tag, "linux_x86_64")

        # When/Then
        with self.assertRaises(OkonomiyakiError):
            SetuptoolsEggMetadata.from_egg(path)

    def test_windows_cp38_egg(self):
        # Given
        path = TRAITS_SETUPTOOLS_WIN_cp38_EGG
        python = RuntimeVersion.from_string('3.8.10')
        platform = EPDPlatform.from_epd_string("win-64", python)

        # When
        metadata = SetuptoolsEggMetadata.from_egg(path, platform)

        # Then
        self.assertEqual(metadata.name, "traits")
        self.assertEqual(metadata.version, "6.3.0.dev1702")
        self.assertEqual(metadata.python_tag, "cp38")
        self.assertEqual(metadata.abi_tag, "cp38")
        self.assertEqual(metadata.platform_tag, "win_amd64")

        # When/Then
        with self.assertRaises(OkonomiyakiError):
            SetuptoolsEggMetadata.from_egg(path)


class TestGuessAbiFromRunningPython(unittest.TestCase):

    def _guess_abi(self, config_vars, version_info):
        with mock.patch.object(
            setuptools_egg.sysconfig, "get_config_var",
            side_effect=config_vars.get,
        ), mock.patch.object(
            setuptools_egg.sys, "version_info", version_info,
        ):
            return _guess_abi_from_running_python()

    @parameterized.expand([
        ("free_threaded",
         {"Py_GIL_DISABLED": True}, (3, 14, 0, "final", 0), "cp314t"),
        ("not_free_threaded",
         {"Py_GIL_DISABLED": False}, (3, 14, 0, "final", 0), "cp314"),
        # Py_GIL_DISABLED does not exist before 3.13; a truthy value there
        # should not be trusted.
        ("ignored_before_py313",
         {"Py_GIL_DISABLED": True}, (3, 12, 0, "final", 0), "cp312"),
        ("pre_38_keeps_m_suffix",
         {}, (3, 7, 0, "final", 0), "cp37m"),
    ])
    def test_guess_abi(self, _, config_vars, version_info, expected):
        abi = self._guess_abi(config_vars, version_info)
        self.assertEqual(abi, expected)
