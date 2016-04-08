import sys

from ...errors import OkonomiyakiError
from ..epd_platform import EPDPlatform
from ..platform import Platform

from .common import (mock_machine_armv71, mock_x86, mock_x86_64,
                     mock_machine_x86_64)
from .common import (mock_architecture_64bit, mock_centos_3_5, mock_centos_5_8,
                     mock_centos_6_3, mock_osx_10_7, mock_solaris,
                     mock_ubuntu_raring, mock_windows_7)

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestPlatformRunningPython(unittest.TestCase):
    @mock_centos_5_8
    @mock_x86
    def test_centos_5_8(self):
        # When
        platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.os, "linux")
        self.assertEqual(platform.name, "centos")
        self.assertEqual(platform.family, "rhel")
        self.assertEqual(platform.release, "5.8")
        self.assertEqual(str(platform), "CentOS 5.8 on x86")
        self.assertEqual(
            repr(platform),
            "Platform(os='linux', name='centos', family='rhel', arch='x86', "
            "machine='x86')"
        )

    @mock_ubuntu_raring
    @mock_x86
    def test_ubuntu_raring(self):
        # When
        platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.os, "linux")
        self.assertEqual(platform.name, "ubuntu")
        self.assertEqual(platform.family, "debian")
        self.assertEqual(str(platform), "Ubuntu 13.04 on x86")
        self.assertEqual(
            repr(platform),
            "Platform(os='linux', name='ubuntu', family='debian', arch='x86', "
            "machine='x86')"
        )

        with self.assertRaises(OkonomiyakiError):
            EPDPlatform(platform)

    @mock_windows_7
    @mock_x86
    def test_windows7(self):
        # When
        platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.os, "windows")
        self.assertEqual(platform.name, "windows")
        self.assertEqual(platform.family, "windows")
        self.assertEqual(platform.release, "7")
        self.assertEqual(str(platform), "Windows 7 on x86")

    @mock_osx_10_7
    @mock_x86
    def test_osx_10_7(self):
        # When
        platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.os, "darwin")
        self.assertEqual(platform.name, "mac_os_x")
        self.assertEqual(platform.family, "mac_os_x")
        self.assertEqual(str(platform), "Mac OS X 10.7.5 on x86")


class TestPlatformRunningSystem(unittest.TestCase):
    @mock_windows_7
    @mock_machine_x86_64
    def test_windows7(self):
        # Given
        arch_string = None

        # When
        with mock_architecture_64bit:
            platform = Platform.from_running_system(arch_string)

        # Then
        self.assertEqual(platform.arch.name, "x86_64")
        self.assertEqual(platform.machine.name, "x86_64")

        # Given
        arch_string = "x86_64"

        # When
        platform = Platform.from_running_system(arch_string)

        # Then
        self.assertEqual(platform.arch.name, "x86_64")
        self.assertEqual(platform.machine.name, "x86_64")

        # Given
        arch_string = "x86"

        # When
        platform = Platform.from_running_system(arch_string)

        # Then
        self.assertEqual(platform.arch.name, "x86")
        self.assertEqual(platform.machine.name, "x86_64")


class TestEpdPlatform(unittest.TestCase):
    @mock_centos_3_5
    def test_centos_3_5(self):
        # When
        with mock_x86:
            platform = Platform.from_running_python()

        # Then
        self.assertEqual(EPDPlatform(platform).short, "rh3-32")

        # When
        with mock_x86_64:
            platform = Platform.from_running_python()

        # Then
        self.assertEqual(EPDPlatform(platform).short, "rh3-64")

    @mock_centos_5_8
    def test_centos_5_8(self):
        # When
        with mock_x86:
            platform = Platform.from_running_python()

        # Then
        self.assertEqual(EPDPlatform(platform).short, "rh5-32")

        # When
        with mock_x86_64:
            platform = Platform.from_running_python()

        # Then
        self.assertEqual(EPDPlatform(platform).short, "rh5-64")

    @mock_centos_6_3
    def test_centos_6_3(self):
        # When
        with mock_x86:
            platform = Platform.from_running_python()

        # Then
        self.assertEqual(EPDPlatform(platform).short, "rh6-32")

        # When
        with mock_x86_64:
            platform = Platform.from_running_python()

        # Then
        self.assertEqual(EPDPlatform(platform).short, "rh6-64")

    @mock_centos_6_3
    @mock_machine_armv71
    def test_centos_6_3_arm(self):
        # When/Then
        with self.assertRaises(OkonomiyakiError):
            Platform.from_running_python()

    @mock_ubuntu_raring
    def test_ubuntu_raring(self):
        # When
        with mock_x86:
            platform = Platform.from_running_python()

        # Then
        with self.assertRaises(OkonomiyakiError):
            EPDPlatform(platform)

    @mock_solaris
    @mock_x86_64
    def test_solaris(self):
        # When/Then
        with self.assertRaises(OkonomiyakiError):
            Platform.from_running_python()


class TestPlatform(unittest.TestCase):
    @mock_windows_7
    def test_hashing(self):
        # Given
        with mock_x86:
            win32_1 = Platform.from_running_system()
            win32_2 = Platform.from_running_system()
        with mock_x86_64:
            win64 = Platform.from_running_system()

        # When/Then
        self.assertEqual(win32_1, win32_2)
        self.assertNotEqual(win32_1, win64)
        self.assertEqual(hash(win32_1), hash(win32_1))
        self.assertTrue(win32_1 == win32_2)
        self.assertFalse(win32_1 != win32_2)
        self.assertTrue(win32_1 != win64)
        self.assertFalse(win32_1 == win64)

        self.assertNotEqual(win32_1, None)
