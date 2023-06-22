import sys

import six
from hypothesis import given
from hypothesis.strategies import sampled_from

from okonomiyaki.errors import OkonomiyakiError
from okonomiyaki.versions import RuntimeVersion

from .. import EPDPlatform
from ..epd_platform import (
    EPD_PLATFORM_SHORT_NAMES, X86, X86_64, applies)
from ..legacy import _SUBDIR
from .._platform import OSKind, FamilyKind, NameKind

from .common import (
    mock_architecture_32bit, mock_architecture_64bit, mock_centos_5_8,
    mock_centos_6_3, mock_darwin, mock_machine_x86, mock_machine_x86_64,
    mock_solaris, mock_ubuntu_raring, mock_x86, mock_x86_64,
    mock_centos_7_6, mock_windows_10, mock_windows_11, mock_windows_7)

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestEPDPlatform(unittest.TestCase):

    def setUp(self):
        items = [
            platform + "-{0}".format(arch)
            for arch in ("x86", "x86_64")
            for platform in ("osx", "win", "rh5")]
        items = [
            platform + "-x86_64"
            for platform in ("rh6", "rh7", "rh8")]
        self.platform_strings = tuple(items)

    def test_short_names_consistency(self):
        legacy_entries = tuple(sorted([entry[0] for entry in _SUBDIR]))
        self.assertEqual(EPD_PLATFORM_SHORT_NAMES, legacy_entries)

    def test_epd_platform_from_legacy_short_string(self):
        for epd_platform_string in EPD_PLATFORM_SHORT_NAMES:
            _, bits = epd_platform_string.split('-')
            epd_platform = EPDPlatform.from_string(epd_platform_string)
            self.assertEqual(epd_platform.short, epd_platform_string)
            self.assertEqual(epd_platform.arch_bits, bits)

    def test_pep425_is_unicode(self):
        # When/Then
        for platform_string in self.platform_strings:
            platform = EPDPlatform.from_string(platform_string)
            self.assertIsInstance(platform.pep425_tag, six.text_type)

    def test_platform_name_is_unicode(self):
        # When/Then
        for platform_string in self.platform_strings:
            platform = EPDPlatform.from_string(platform_string)
            self.assertIsInstance(platform.platform_name, six.text_type)

    def test_str_is_unicode(self):
        # When/Then
        for platform_string in self.platform_strings:
            platform = EPDPlatform.from_string(platform_string)
            self.assertIsInstance(six.text_type(platform), six.text_type)

    def test_over_complete_strings(self):
        # When/Then
        with self.assertRaises(OkonomiyakiError):
            EPDPlatform.from_string("win_x86-64")

    def test_epd_platform_from_string_new_names(self):
        """Ensure every epd short platform is understood by EPDPlatform."""
        # Given
        archs = ("i386", "x86", "i686")

        # When
        epd_platforms = tuple(
            EPDPlatform.from_string("rh5-" + arch)
            for arch in archs)

        # Then
        for epd_platform in epd_platforms:
            self.assertEqual(epd_platform.arch_bits, "32")
            self.assertEqual(epd_platform.platform_name, "rh5")

        # Given
        archs = ("amd64", "x86_64", "AMD64")

        # When
        epd_platforms = tuple(
            EPDPlatform.from_string("win-" + arch)
            for arch in archs)

        # Then
        for epd_platform in epd_platforms:
            self.assertEqual(epd_platform.arch_bits, "64")
            self.assertEqual(epd_platform.platform_name, "win")

    def test_epd_platform_from_string_with_runtime_version(self):
        # given
        version = RuntimeVersion.from_string('3.6.5+6')

        # when/then
        epd_platform = EPDPlatform.from_string('osx-64', version)
        self.assertEqual(epd_platform.platform.release, '10.6')
        epd_platform = EPDPlatform.from_string('win-64', version)
        self.assertEqual(epd_platform.platform.release, '')

        # given
        version = RuntimeVersion.from_string('3.8.8+2')

        # when/then
        epd_platform = EPDPlatform.from_string('osx-x86_64', version)
        self.assertEqual(epd_platform.platform.release, '10.14')
        epd_platform = EPDPlatform.from_string('win-x86_64', version)
        self.assertEqual(epd_platform.platform.release, '10')

        # given
        version = RuntimeVersion.from_string('3.11.2+5')

        # when/then
        epd_platform = EPDPlatform.from_string('osx-x86_64', version)
        self.assertEqual(epd_platform.platform.release, '12.0')
        epd_platform = EPDPlatform.from_string('win-x86_64', version)
        self.assertEqual(epd_platform.platform.release, '10')

    @mock_darwin
    @mock_machine_x86_64
    def test_from_running_python_darwin(self):
        # When
        with mock_architecture_32bit:
            epd_platform = EPDPlatform.from_running_python()

        # Then
        self.assertEqual(str(epd_platform), "osx_x86")

        # When
        with mock_architecture_64bit:
            epd_platform = EPDPlatform.from_running_python()

        # Then
        self.assertEqual(str(epd_platform), "osx_x86_64")

    @mock_windows_7
    def test_from_running_system_windows_7(self):
        with mock_machine_x86:
            epd_platform = EPDPlatform.from_running_system()
            self.assertEqual(str(epd_platform), "win_x86")

            epd_platform = EPDPlatform.from_running_system('x86')
            self.assertEqual(str(epd_platform), "win_x86")

            with self.assertRaises(OkonomiyakiError):
                EPDPlatform.from_running_system('AMD64')

        with mock_machine_x86_64:
            epd_platform = EPDPlatform.from_running_system()
            self.assertEqual(str(epd_platform), "win_x86_64")

            epd_platform = EPDPlatform.from_running_system('x86')
            self.assertEqual(str(epd_platform), "win_x86")

    @mock_windows_10
    def test_from_running_system_windows_10(self):
        with mock_machine_x86:
            epd_platform = EPDPlatform.from_running_system()
            self.assertEqual(str(epd_platform), "win_x86")

            epd_platform = EPDPlatform.from_running_system('x86')
            self.assertEqual(str(epd_platform), "win_x86")

            with self.assertRaises(OkonomiyakiError):
                EPDPlatform.from_running_system('AMD64')

        with mock_machine_x86_64:
            epd_platform = EPDPlatform.from_running_system()
            self.assertEqual(str(epd_platform), "win_x86_64")

            epd_platform = EPDPlatform.from_running_system('x86')
            self.assertEqual(str(epd_platform), "win_x86")

    @mock_windows_11
    def test_from_running_system_windows_11(self):
        with mock_machine_x86:
            epd_platform = EPDPlatform.from_running_system()
            self.assertEqual(str(epd_platform), "win_x86")

            epd_platform = EPDPlatform.from_running_system('x86')
            self.assertEqual(str(epd_platform), "win_x86")

            with self.assertRaises(OkonomiyakiError):
                EPDPlatform.from_running_system('AMD64')

        with mock_machine_x86_64:
            epd_platform = EPDPlatform.from_running_system()
            self.assertEqual(str(epd_platform), "win_x86_64")

            epd_platform = EPDPlatform.from_running_system('x86')
            self.assertEqual(str(epd_platform), "win_x86")

    @mock_darwin
    def test_from_running_system_darwin(self):
        with mock_machine_x86:
            # When/Then
            epd_platform = EPDPlatform.from_running_system()
            self.assertEqual(str(epd_platform), "osx_x86")
            # When/Then
            epd_platform = EPDPlatform.from_running_system("x86")
            self.assertEqual(str(epd_platform), "osx_x86")
            # When/Then
            with self.assertRaises(OkonomiyakiError):
                EPDPlatform.from_running_system("amd64")
        # When
        with mock_machine_x86_64:
            # When/Then
            epd_platform = EPDPlatform.from_running_system()
            self.assertEqual(str(epd_platform), "osx_x86_64")
            # When/Then
            epd_platform = EPDPlatform.from_running_system('x86_64')
            self.assertEqual(str(epd_platform), "osx_x86_64")
            # When/Then
            epd_platform = EPDPlatform.from_running_system('x86')
            self.assertEqual(str(epd_platform), "osx_x86")

    @mock_centos_5_8
    def test_from_running_system_centos_5(self):
        with mock_machine_x86:
            # When/Then
            epd_platform = EPDPlatform.from_running_system()
            self.assertEqual(str(epd_platform), "rh5_x86")
            # When/Then
            epd_platform = EPDPlatform.from_running_system('x86')
            self.assertEqual(str(epd_platform), "rh5_x86")
            # When/Then
            with self.assertRaises(OkonomiyakiError):
                EPDPlatform.from_running_system('x86_64')

        with mock_machine_x86_64:
            # When/Then
            epd_platform = EPDPlatform.from_running_system()
            self.assertEqual(str(epd_platform), "rh5_x86_64")
            # When/Then
            epd_platform = EPDPlatform.from_running_system('x86')
            self.assertEqual(str(epd_platform), "rh5_x86")

    @mock_centos_6_3
    def test_from_running_system_centos_6(self):
        with mock_machine_x86:
            # When/Then
            epd_platform = EPDPlatform.from_running_system()
            self.assertEqual(str(epd_platform), "rh6_x86")
            # When/Then
            epd_platform = EPDPlatform.from_running_system('x86')
            self.assertEqual(str(epd_platform), "rh6_x86")
            # When/Then
            with self.assertRaises(OkonomiyakiError):
                EPDPlatform.from_running_system('x86_64')

        with mock_machine_x86_64:
            # When/Then
            epd_platform = EPDPlatform.from_running_system()
            self.assertEqual(str(epd_platform), "rh6_x86_64")
            # When/Then
            epd_platform = EPDPlatform.from_running_system('x86')
            self.assertEqual(str(epd_platform), "rh6_x86")

    @mock_centos_7_6
    def test_from_running_system_centos_7(self):
        with mock_machine_x86:
            # When/Then
            epd_platform = EPDPlatform.from_running_system()
            self.assertEqual(str(epd_platform), "rh7_x86")
            # When/Then
            epd_platform = EPDPlatform.from_running_system('x86')
            self.assertEqual(str(epd_platform), "rh7_x86")

        with mock_machine_x86_64:
            epd_platform = EPDPlatform.from_running_system()
            self.assertEqual(str(epd_platform), "rh7_x86_64")
            epd_platform = EPDPlatform.from_running_system('x86')
            self.assertEqual(str(epd_platform), "rh7_x86")

    @given(sampled_from((
        ("rh5_x86", None, "linux_i686"),
        ("rh5_x86_64", None, "linux_x86_64"),
        ("osx_x86", None, "macosx_10_6_i386"),
        ("osx_x86", '3.8.9+1', "macosx_10_14_i386"),
        ("osx_x86_64", None, "macosx_10_6_x86_64"),
        ("osx_x86_64", '3.8.9+1', "macosx_10_14_x86_64"),
        ("osx_x86_64", '3.11.2+1', "macosx_12_0_x86_64"),
        ("win_x86", None, "win32"),
        ("win_x86_64", None, "win_amd64"),
        ("win_x86_64", '3.9.1', "win_amd64"))))
    def test_pep425_tag(self, arguments):
        # Given
        platform_tag, version, expected = arguments
        if version is not None:
            runtime_version = RuntimeVersion.from_string(version)
        else:
            runtime_version = None
        epd_platform = EPDPlatform.from_string(platform_tag, runtime_version)

        # When/Then
        self.assertEqual(epd_platform.pep425_tag, expected)

    @given(sampled_from((
        ('linux2', None, 'i686', 'linux_i686', 'cp36', 'gnu'),
        ('linux2', 'RedHat_3', 'i386', 'linux_i386', 'cp27', 'gnu'),
        ('linux2', 'RedHat_5', 'x86', 'linux_i686', 'cp27', 'gnu'),
        ('linux2', 'RedHat_5', 'amd64', 'linux_x86_64', 'cp27', 'gnu'),
        ('linux2', 'RedHat_6', 'amd64', 'linux_x86_64', 'cp36', 'gnu'),
        ('linux2', 'RedHat_7', 'amd64', 'linux_x86_64', 'cp38', 'gnu'),
        ('darwin', None, 'x86', 'osx_10_6_x86', 'cp27', 'darwin'),
        ('darwin', None, 'amd64', 'osx_10_6_x86_64', 'cp27', 'darwin'),
        ('darwin', None, 'amd64', 'osx_10_9_x86_64', 'cp36', 'darwin'),
        ('darwin', None, 'amd64', 'osx_10_14_x86_64', 'cp38', 'darwin'),
        ('win32', None, 'x86', 'win32', 'cp27', 'msvc2008'),
        ('win32', None, 'amd64', 'win_amd64', 'cp27', 'msvc2008'),
        ('win32', None, 'x86', 'win32', 'cp36', 'msvc2015'),
        ('win32', None, 'amd64', 'win_amd64', 'cp36', 'msvc2015'),
        ('win32', None, 'x86', 'win32', 'cp38', 'msvc2019'),
        ('win32', None, 'amd64', 'win32', 'cp311', 'msvc2022'),
        ('win32', None, 'amd64', 'win_amd64', 'cp38', 'msvc2019'),
    )))
    def test_from_spec_depend_data(self, arguments):
        # when
        epd_platform = EPDPlatform._from_spec_depend_data(*arguments)
        platform, osdist, arch_name, platform_tag, python_version, platform_abi = arguments

        # then
        if '64' in arch_name:
            self.assertEqual(epd_platform.arch, X86_64)
        else:
            self.assertEqual(epd_platform.arch, X86)
        if 'linux' in platform:
            self.assertIn('linux', epd_platform.pep425_tag)
        elif 'win32' in platform:
            self.assertIn('win', epd_platform.pep425_tag)
        elif 'darwin' in platform:
            self.assertIn('osx', epd_platform.pep425_tag)


class TestEPDPlatformApplies(unittest.TestCase):
    def test_arch_only(self):
        # Given
        platform = "64"
        to = "rh5-64"

        # When
        s = applies(platform, to)

        # Then
        self.assertIs(s, True)

        # Given
        platform = "32"
        to = "rh5-64"

        # When
        s = applies(platform, to)

        # Then
        self.assertIs(s, False)

        # Given
        platform = "64"
        to = "rh5-32"

        # When
        s = applies(platform, to)

        # Then
        self.assertIs(s, False)

    @mock_centos_5_8
    def test_no_arch(self):
        with mock_x86:
            self.assertTrue(applies("rh5", "current"))
            self.assertFalse(applies("!rh5", "current"))

        platform = EPDPlatform.from_string("rh5-x86_64")
        self.assertTrue(applies("rh5", platform))
        self.assertFalse(applies("!rh5", platform))
        self.assertFalse(applies("rh5-32", platform))

    @mock_centos_5_8
    def test_all(self):
        with mock_x86:
            self.assertTrue(applies("all", "current"))
            self.assertFalse(applies("!all", "current"))

        platform = EPDPlatform.from_string("rh5-x86_64")
        self.assertTrue(applies("all", platform))
        self.assertFalse(applies("!all", platform))

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

    @mock_windows_7
    @mock_x86
    def test_current_windows_7(self):
        for platform in ("rh5", "rh", "osx-32"):
            self.assertFalse(applies(platform, "current"))
        for platform in ("win", "win-32"):
            self.assertTrue(applies(platform, "current"))

    @mock_windows_10
    @mock_x86
    def test_current_windows_10(self):
        for platform in ("rh5", "rh", "osx-32"):
            self.assertFalse(applies(platform, "current"))
        for platform in ("win", "win-32"):
            self.assertTrue(applies(platform, "current"))

    @mock_windows_11
    @mock_x86
    def test_current_windows_11(self):
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

    def test_guess_linux2_unsupported(self):
        with mock_ubuntu_raring:
            with self.assertRaises(OkonomiyakiError):
                EPDPlatform.from_running_system()

    @mock_solaris
    def test_guess_solaris_unsupported(self):
        with self.assertRaises(OkonomiyakiError):
            EPDPlatform.from_running_system()

    def test_from_epd_platform_string(self):
        # Given
        epd_platform_string = "rh5-x86"

        # When
        epd_platform = EPDPlatform.from_string(epd_platform_string)

        # Then
        platform = epd_platform.platform
        self.assertEqual(platform.os_kind, OSKind.linux)
        self.assertEqual(platform.family_kind, FamilyKind.rhel)
        self.assertEqual(platform.name_kind, NameKind.rhel)
        self.assertEqual(platform.arch, X86)
        self.assertEqual(platform.machine, X86)

        # Given
        epd_platform_string = "win-x86"

        # When
        epd_platform = EPDPlatform.from_string(epd_platform_string)

        # Then
        platform = epd_platform.platform
        self.assertEqual(platform.os_kind, OSKind.windows)
        self.assertEqual(platform.family_kind, FamilyKind.windows)
        self.assertEqual(platform.name_kind, NameKind.windows)
        self.assertEqual(platform.arch, X86)
        self.assertEqual(platform.machine, X86)

        # Given
        epd_platform_string = "osx-x86_64"

        # When
        epd_platform = EPDPlatform.from_string(epd_platform_string)
        platform = epd_platform.platform

        # Then
        self.assertEqual(platform.os_kind, OSKind.darwin)
        self.assertEqual(platform.family_kind, FamilyKind.mac_os_x)
        self.assertEqual(platform.name_kind, NameKind.mac_os_x)
        self.assertEqual(platform.arch, X86_64)
        self.assertEqual(platform.machine, X86_64)

    def test_from_epd_platform_string_invalid(self):
        # Given
        # Invalid bitwidth
        epd_platform_string = "linux-32-1"

        # When/Then
        with self.assertRaises(OkonomiyakiError):
            EPDPlatform.from_string(epd_platform_string)

        # Given
        # Invalid bitwidth
        epd_platform_string = "osx-63"

        # When/Then
        with self.assertRaises(OkonomiyakiError):
            EPDPlatform.from_string(epd_platform_string)

        # Given
        # Invalid platform basename
        epd_platform_string = "netbsd-32"

        # When/Then
        with self.assertRaises(OkonomiyakiError):
            EPDPlatform.from_string(epd_platform_string)

    def test_from_platform_tag(self):
        # Given
        inputs_outputs = (
            ("linux_i686", "rh5_x86"),
            ("linux_i386", "rh5_x86"),
            ("linux_x86_64", "rh5_x86_64"),
            ("win32", "win_x86"),
            ("win_amd64", "win_x86_64"),
            ("macosx_10_6_x86_64", "osx_x86_64"),
        )

        # When/Then
        for platform_tag, epd_string in inputs_outputs:
            platform = EPDPlatform._from_platform_tag(platform_tag)
            self.assertEqual(str(platform), epd_string)

        # When/Then
        with self.assertRaises(NotImplementedError):
            EPDPlatform._from_platform_tag("openbsd_i386")

        with self.assertRaises(ValueError):
            EPDPlatform._from_platform_tag("any")

        with self.assertRaises(ValueError):
            EPDPlatform._from_platform_tag(None)
