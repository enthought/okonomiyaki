import mock
import unittest

from ...errors import OkonomiyakiError

from .. import EPDPlatform
from ..epd_platform import (
    _guess_epd_platform, EPD_PLATFORM_SHORT_NAMES, applies
)
from ..legacy import _SUBDIR
from ..platform import DARWIN, LINUX, MAC_OS_X, RHEL, WINDOWS
from .._arch import Arch, X86, X86_64

from .common import (
    mock_architecture_32bit, mock_architecture_64bit, mock_centos_5_8,
    mock_centos_6_3, mock_darwin, mock_machine_x86, mock_machine_x86_64,
    mock_solaris, mock_ubuntu_raring, mock_windows, mock_x86, mock_x86_64
)


class TestEPDPlatform(unittest.TestCase):
    def test_short_names_consistency(self):
        legacy_entries = sorted([entry[0] for entry in _SUBDIR])

        self.assertEqual(EPD_PLATFORM_SHORT_NAMES, legacy_entries)

    def test_epd_platform_from_string(self):
        """Ensure every epd short platform is understood by EPDPlatform."""
        for epd_platform_string in EPD_PLATFORM_SHORT_NAMES:
            EPDPlatform.from_epd_string(epd_platform_string)

    def test_epd_platform_from_string_new_names_underscore(self):
        # Given
        archs = ("i386", "x86", "i686")

        # When
        epd_platforms = tuple(
            EPDPlatform.from_epd_string("rh5_" + arch)
            for arch in archs
        )

        # Then
        for epd_platform in epd_platforms:
            self.assertEqual(epd_platform.arch_bits, "32")

        # Given
        archs = ("amd64", "x86_64", "AMD64")

        # When
        epd_platforms = tuple(
            EPDPlatform.from_epd_string("rh5_" + arch)
            for arch in archs
        )

        # Then
        for epd_platform in epd_platforms:
            self.assertEqual(epd_platform.arch_bits, "64")

        # Given
        s = "win_x86_64"

        # When
        epd_platform = EPDPlatform.from_epd_string(s)

        # Then
        self.assertEqual(epd_platform, EPDPlatform.from_epd_string("win-64"))

        # Given
        s = "osx_x86_64"

        # When
        epd_platform = EPDPlatform.from_epd_string(s)

        # Then
        self.assertEqual(epd_platform, EPDPlatform.from_epd_string("osx-64"))

    def test_epd_platform_from_string_new_names(self):
        """Ensure every epd short platform is understood by EPDPlatform."""
        # Given
        archs = ("i386", "x86", "i686")

        # When
        epd_platforms = tuple(
            EPDPlatform.from_epd_string("rh5-" + arch)
            for arch in archs
        )

        # Then
        for epd_platform in epd_platforms:
            self.assertEqual(epd_platform.arch_bits, "32")

        # Given
        archs = ("amd64", "x86_64", "AMD64")

        # When
        epd_platforms = tuple(
            EPDPlatform.from_epd_string("rh5-" + arch)
            for arch in archs
        )

        # Then
        for epd_platform in epd_platforms:
            self.assertEqual(epd_platform.arch_bits, "64")

    @mock_darwin
    @mock_machine_x86_64
    def test_from_running_python(self):
        # When
        with mock_architecture_32bit:
            platform = EPDPlatform.from_running_python()

        # Then
        self.assertEqual(platform.short, "osx-32")

        # When
        with mock_architecture_64bit:
            platform = EPDPlatform.from_running_python()

        # Then
        self.assertEqual(platform.short, "osx-64")

    @mock_darwin
    @mock_machine_x86_64
    def test_from_running_system(self):
        # When
        with mock_architecture_32bit:
            platform = EPDPlatform.from_running_system()

        # Then
        self.assertEqual(platform.short, "osx-64")

        # When
        with mock_architecture_64bit:
            platform = EPDPlatform.from_running_system()

        # Then
        self.assertEqual(platform.short, "osx-64")

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

    def test_str(self):
        # Given
        epd_platform = EPDPlatform.from_epd_string("rh5-64")

        # When/Then
        self.assertEqual(str(epd_platform), "rh5_x86_64")

        # Given
        epd_platform = EPDPlatform.from_epd_string("osx-32")

        # When/Then
        self.assertEqual(str(epd_platform), "osx_x86")

        # Given
        s = "osx_x86"

        # When
        epd_platform = EPDPlatform.from_epd_string(s)

        # Then
        self.assertEqual(str(epd_platform), s)


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
        epd_platform = _guess_epd_platform(Arch.from_name("x86"))
        self.assertEqual(epd_platform.short, "win-32")

        epd_platform = _guess_epd_platform(Arch.from_name("amd64"))
        self.assertEqual(epd_platform.short, "win-64")

    @mock_darwin
    def test_guess_darwin_platform(self):
        # When
        with mock_machine_x86:
            epd_platform = _guess_epd_platform(Arch.from_name("x86"))

        # Then
        self.assertEqual(epd_platform.short, "osx-32")

        # When
        with mock_machine_x86:
            epd_platform = _guess_epd_platform(Arch.from_name("amd64"))

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
            epd_platform = _guess_epd_platform(Arch.from_name("x86"))
            self.assertEqual(epd_platform.short, "rh5-32")

            epd_platform = _guess_epd_platform(Arch.from_name("amd64"))
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
            epd_platform = _guess_epd_platform(Arch.from_name("x86"))
            self.assertEqual(epd_platform.short, "rh6-32")

            epd_platform = _guess_epd_platform(Arch.from_name("amd64"))
            self.assertEqual(epd_platform.short, "rh6-64")

    def test_guess_linux2_unsupported(self):
        with mock_ubuntu_raring:
            with self.assertRaises(OkonomiyakiError):
                _guess_epd_platform()

    @mock_solaris
    def test_guess_solaris_unsupported(self):
        self.assertRaises(OkonomiyakiError, _guess_epd_platform)

    def test_from_spec_depend_data(self):
        # Given
        examples = (
            (("linux2", None, "x86"),
             EPDPlatform.from_epd_string("rh5-32"),),
            (("linux2", "RedHat_3", "x86"),
             EPDPlatform.from_epd_string("rh3-32"),),
            (("linux2", "RedHat_5", "x86"),
             EPDPlatform.from_epd_string("rh5-32"),),
            (("linux2", "RedHat_5", "amd64"),
             EPDPlatform.from_epd_string("rh5-64"),),
            (("darwin", None, "x86"),
             EPDPlatform.from_epd_string("osx-32"),),
            (("darwin", None, "amd64"),
             EPDPlatform.from_epd_string("osx-64"),),
            (("win32", None, "x86"),
             EPDPlatform.from_epd_string("win-32"),),
            (("win32", None, "amd64"),
             EPDPlatform.from_epd_string("win-64"),),
        )

        # When/Then
        for args, r_platform in examples:
            platform = EPDPlatform._from_spec_depend_data(*args)
            self.assertEqual(platform, r_platform)

    def test_from_epd_platform_string(self):
        # Given
        epd_platform_string = "rh5-32"

        # When
        epd_platform = EPDPlatform.from_epd_string(epd_platform_string)

        # Then
        platform = epd_platform.platform
        self.assertEqual(platform.os, LINUX)
        self.assertEqual(platform.family, RHEL)
        self.assertEqual(platform.name, RHEL)
        self.assertEqual(platform.arch, Arch.from_name(X86))
        self.assertEqual(platform.machine, Arch.from_name(X86))

        # Given
        epd_platform_string = "win-32"

        # When
        epd_platform = EPDPlatform.from_epd_string(epd_platform_string)

        # Then
        platform = epd_platform.platform
        self.assertEqual(platform.os, WINDOWS)
        self.assertEqual(platform.family, WINDOWS)
        self.assertEqual(platform.name, WINDOWS)
        self.assertEqual(platform.arch, Arch.from_name(X86))
        self.assertEqual(platform.machine, Arch.from_name(X86))

        # Given
        epd_platform_string = "osx-64"

        # When
        epd_platform = EPDPlatform.from_epd_string(epd_platform_string)
        platform = epd_platform.platform

        # Then
        self.assertEqual(platform.os, DARWIN)
        self.assertEqual(platform.family, MAC_OS_X)
        self.assertEqual(platform.name, MAC_OS_X)
        self.assertEqual(platform.arch, Arch.from_name(X86_64))
        self.assertEqual(platform.machine, Arch.from_name(X86_64))

    def test_from_epd_platform_string_invalid(self):
        # Given
        # Invalid bitwidth
        epd_platform_string = "linux-32-1"

        # When/Then
        with self.assertRaises(OkonomiyakiError):
            EPDPlatform.from_epd_string(epd_platform_string)

        # Given
        # Invalid bitwidth
        epd_platform_string = "osx-63"

        # When/Then
        with self.assertRaises(OkonomiyakiError):
            EPDPlatform.from_epd_string(epd_platform_string)

        # Given
        # Invalid platform basename
        epd_platform_string = "netbsd-32"

        # When/Then
        with self.assertRaises(OkonomiyakiError):
            EPDPlatform.from_epd_string(epd_platform_string)
