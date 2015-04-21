import mock
import unittest

from okonomiyaki.errors import OkonomiyakiError

from okonomiyaki.platforms import EPDPlatform
from okonomiyaki.platforms.epd_platform import (_guess_architecture,
                                                _guess_epd_platform,
                                                EPD_PLATFORM_SHORT_NAMES,
                                                applies)
from okonomiyaki.platforms.legacy import _SUBDIR
from okonomiyaki.platforms.platform import X86, X86_64

from .common import (mock_architecture_32bit, mock_architecture_64bit,
                     mock_centos_3_5, mock_centos_5_8, mock_centos_6_3,
                     mock_darwin, mock_machine_x86, mock_machine_x86_64,
                     mock_machine_armv71, mock_solaris,
                     mock_ubuntu_raring, mock_windows, mock_x86,
                     mock_x86_64)


class TestEPDPlatform(unittest.TestCase):
    def test_short_names_consistency(self):
        legacy_entries = sorted([entry[0] for entry in _SUBDIR])

        self.assertEqual(EPD_PLATFORM_SHORT_NAMES, legacy_entries)

    def test_epd_platform_from_string(self):
        """Ensure every epd short platform is understood by EPDPlatform."""
        for epd_platform_string in EPD_PLATFORM_SHORT_NAMES:
            EPDPlatform.from_epd_string(epd_platform_string)

    def test_epd_platform_from_string_new_arch(self):
        def old_to_new_name(epd_platform_string):
            left, right = epd_platform_string.split("-")
            return "{}-{}".format(left, {"32": X86, "64": X86_64}[right])

        # Given
        name_to_platform = {}

        # When
        for old_name in EPD_PLATFORM_SHORT_NAMES:
            new_name = old_to_new_name(old_name)
            name_to_platform[old_name] = EPDPlatform.from_epd_string(new_name)

        # Then
        for old_name in name_to_platform:
            self.assertEqual(name_to_platform[old_name].short, old_name)

    def test_guessed_epd_platform(self):
        with mock_centos_5_8:
            epd_platform = EPDPlatform.from_running_system("x86")
            self.assertEqual(epd_platform.short, "rh5-32")

            epd_platform = EPDPlatform.from_running_system("amd64")
            self.assertEqual(epd_platform.short, "rh5-64")


class TestEPDPlatformApplies(unittest.TestCase):
    @mock_centos_5_8
    def test_all(self):
        with mock_x86:
            self.assertTrue(applies("all", "current"))
            self.assertFalse(applies("!all", "current"))

    @mock_centos_5_8
    def test_current_linux(self):
        with mock_x86:
            for expected_supported in ("rh5", "rh"):
                self.assertTrue(applies(expected_supported, "current"))
                self.assertFalse(applies("!" + expected_supported, "current"))

            for expected_unsupported in ("win", "win-32", "osx", "rh6", "rh3"):
                self.assertFalse(applies(expected_unsupported, "current"))
                self.assertTrue(applies("!" + expected_unsupported, "current"))

            self.assertTrue(applies("win,rh", "current"))
            self.assertFalse(applies("win,osx", "current"))
            self.assertTrue(applies("!win,osx", "current"))
            self.assertFalse(applies("!rh,osx", "current"))

            self.assertTrue(applies("rh5-32", "current"))
            self.assertFalse(applies("!rh5-32", "current"))

        with mock_x86_64:
            self.assertTrue(applies("rh5-64", "current"))
            self.assertFalse(applies("!rh5-64", "current"))

    @mock_windows
    @mock_x86
    def test_current_windows(self):
        for platform in ("rh5", "rh", "osx-32"):
            self.assertFalse(applies(platform, "current"))
        for platform in ("win", "win-32"):
            self.assertTrue(applies(platform, "current"))

    @mock_centos_5_8
    @mock_x86
    def test_applies_rh(self):
        self.assertTrue(applies("rh5-32", "rh5"))
        self.assertTrue(applies("rh5-64", "rh5"))
        self.assertFalse(applies("win-64", "rh5"))
        self.assertFalse(applies("rh6-64", "rh5"))
        self.assertTrue(applies("rh5-32", "rh"))
        self.assertTrue(applies("rh6-32", "rh"))
        self.assertFalse(applies("win-32", "rh"))


class TestGuessEPDPlatform(unittest.TestCase):
    @mock_windows
    def test_guess_win32_platform(self):
        epd_platform = _guess_epd_platform("x86")
        self.assertEqual(epd_platform.short, "win-32")

        epd_platform = _guess_epd_platform("amd64")
        self.assertEqual(epd_platform.short, "win-64")

    @mock_darwin
    def test_guess_darwin_platform(self):
        # When
        with mock_machine_x86:
            epd_platform = _guess_epd_platform("x86")

        # Then
        self.assertEqual(epd_platform.short, "osx-32")

        # When
        with mock_machine_x86:
            epd_platform = _guess_epd_platform("amd64")

        # Then
        self.assertEqual(epd_platform.short, "osx-64")

        # When
        with mock_machine_x86:
            with mock_architecture_32bit:
                epd_platform = _guess_epd_platform()

        # Then
        self.assertEqual(epd_platform.short, "osx-32")

        # When
        with mock_machine_x86:
            with mock_architecture_64bit:
                epd_platform = _guess_epd_platform()

        # Then
        self.assertEqual(epd_platform.short, "osx-64")

        # When
        with mock_machine_x86_64:
            with mock_architecture_64bit:
                epd_platform = _guess_epd_platform()

        # Then
        self.assertEqual(epd_platform.short, "osx-64")

        # When
        with mock_machine_x86_64:
            with mock_architecture_32bit:
                epd_platform = _guess_epd_platform()

        # Then
        self.assertEqual(epd_platform.short, "osx-32")

    def test_guess_linux2_platform(self):
        with mock_centos_5_8:
            epd_platform = _guess_epd_platform("x86")
            self.assertEqual(epd_platform.short, "rh5-32")

            epd_platform = _guess_epd_platform("amd64")
            self.assertEqual(epd_platform.short, "rh5-64")

            with mock.patch("platform.machine", lambda: "x86"):
                with mock_architecture_32bit:
                    epd_platform = _guess_epd_platform()
                    self.assertEqual(epd_platform.short, "rh5-32")

            with mock.patch("platform.machine", lambda: "i386"):
                with mock_architecture_32bit:
                    epd_platform = _guess_epd_platform()
                    self.assertEqual(epd_platform.short, "rh5-32")

            with mock.patch("platform.machine", lambda: "i686"):
                with mock_architecture_32bit:
                    epd_platform = _guess_epd_platform()
                    self.assertEqual(epd_platform.short, "rh5-32")

            with mock.patch("platform.machine", lambda: "x86_64"):
                with mock_architecture_32bit:
                    epd_platform = _guess_epd_platform()
                    self.assertEqual(epd_platform.short, "rh5-32")

            with mock.patch("platform.machine", lambda: "x86_64"):
                with mock_architecture_64bit:
                    epd_platform = _guess_epd_platform()
                    self.assertEqual(epd_platform.short, "rh5-64")

        with mock_centos_6_3:
            epd_platform = _guess_epd_platform("x86")
            self.assertEqual(epd_platform.short, "rh6-32")

            epd_platform = _guess_epd_platform("amd64")
            self.assertEqual(epd_platform.short, "rh6-64")

    def test_guess_linux2_unsupported(self):
        with mock_centos_3_5:
            self.assertRaises(OkonomiyakiError, _guess_epd_platform)

        with mock_ubuntu_raring:
            self.assertRaises(OkonomiyakiError, _guess_epd_platform)

    @mock_solaris
    def test_guess_solaris_unsupported(self):
        self.assertRaises(OkonomiyakiError, _guess_epd_platform)

    @mock_machine_armv71
    def test_guess_unsupported_processor(self):
        self.assertRaises(OkonomiyakiError, _guess_architecture)
