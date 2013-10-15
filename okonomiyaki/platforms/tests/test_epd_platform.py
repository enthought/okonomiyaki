import mock
import unittest

from okonomiyaki.errors import OkonomiyakiError

from okonomiyaki.platforms import EPD_PLATFORM_SHORT_NAMES, EPDPlatform
from okonomiyaki.platforms.epd_platform import _guess_architecture, \
    _guess_epd_platform
from okonomiyaki.platforms.legacy import _SUBDIR


class TestEPDPlatform(unittest.TestCase):
    def test_short_names_consistency(self):
        legacy_entries = sorted([entry[0] for entry in _SUBDIR])

        self.assertEqual(EPD_PLATFORM_SHORT_NAMES, legacy_entries)

    def test_epd_platform_from_string(self):
        """Ensure every epd short platform is understood by EPDPlatform."""
        for epd_platform_string in EPD_PLATFORM_SHORT_NAMES:
            EPDPlatform.from_epd_string(epd_platform_string)

    @mock.patch("sys.platform", "linux2")
    def test_guessed_epd_platform(self):
        with mock.patch("platform.dist", lambda: ("redhat", "5.8", "Final")):
            epd_platform = EPDPlatform.from_running_system("x86")
            self.assertEqual(epd_platform.short, "rh5-32")

            epd_platform = EPDPlatform.from_running_system("amd64")
            self.assertEqual(epd_platform.short, "rh5-64")


class TestGuessEPDPlatform(unittest.TestCase):
    @mock.patch("sys.platform", "win32")
    def test_guess_win32_platform(self):
        epd_platform = _guess_epd_platform("x86")
        self.assertEqual(epd_platform.short, "win-32")

        epd_platform = _guess_epd_platform("amd64")
        self.assertEqual(epd_platform.short, "win-64")

    @mock.patch("sys.platform", "darwin")
    def test_guess_darwin_platform(self):
        epd_platform = _guess_epd_platform("x86")
        self.assertEqual(epd_platform.short, "osx-32")

        epd_platform = _guess_epd_platform("amd64")
        self.assertEqual(epd_platform.short, "osx-64")

    @mock.patch("sys.platform", "linux2")
    def test_guess_linux2_platform(self):
        with mock.patch("platform.dist", lambda: ("redhat", "5.8", "Final")):
            epd_platform = _guess_epd_platform("x86")
            self.assertEqual(epd_platform.short, "rh5-32")

            epd_platform = _guess_epd_platform("amd64")
            self.assertEqual(epd_platform.short, "rh5-64")

            with mock.patch("platform.machine", lambda: "x86"):
                with mock.patch("platform.architecture", lambda: ("32bit",)):
                    epd_platform = _guess_epd_platform()
                    self.assertEqual(epd_platform.short, "rh5-32")

            with mock.patch("platform.machine", lambda: "i386"):
                with mock.patch("platform.architecture", lambda: ("32bit",)):
                    epd_platform = _guess_epd_platform()
                    self.assertEqual(epd_platform.short, "rh5-32")

            with mock.patch("platform.machine", lambda: "i686"):
                with mock.patch("platform.architecture", lambda: ("32bit",)):
                    epd_platform = _guess_epd_platform()
                    self.assertEqual(epd_platform.short, "rh5-32")

            with mock.patch("platform.machine", lambda: "x86_64"):
                with mock.patch("platform.architecture", lambda: ("32bit",)):
                    epd_platform = _guess_epd_platform()
                    self.assertEqual(epd_platform.short, "rh5-32")

            with mock.patch("platform.machine", lambda: "x86_64"):
                with mock.patch("platform.architecture", lambda: ("64bit",)):
                    epd_platform = _guess_epd_platform()
                    self.assertEqual(epd_platform.short, "rh5-64")

        with mock.patch("platform.dist", lambda: ("centos", "6.4", "Final")):
            epd_platform = _guess_epd_platform("x86")
            self.assertEqual(epd_platform.short, "rh6-32")

            epd_platform = _guess_epd_platform("amd64")
            self.assertEqual(epd_platform.short, "rh6-64")

    @mock.patch("sys.platform", "linux2")
    def test_guess_linux2_unsupported(self):
        with mock.patch("platform.dist", lambda: ("centos", "3.5", "Final")):
            self.assertRaises(OkonomiyakiError, _guess_epd_platform)

        with mock.patch("platform.dist",
                        lambda: ("Ubuntu", "13.04", "raring")):
            self.assertRaises(OkonomiyakiError, _guess_epd_platform)

    @mock.patch("sys.platform", "sunos5")
    def test_guess_solaris_unsupported(self):
        self.assertRaises(OkonomiyakiError, _guess_epd_platform)

    @mock.patch("platform.machine", lambda: "armv71")
    def test_guess_unsupported_processor(self):
        self.assertRaises(OkonomiyakiError, _guess_architecture)
