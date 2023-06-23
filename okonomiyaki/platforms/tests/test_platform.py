import sys

from okonomiyaki.errors import OkonomiyakiError
from .._platform import Platform

from .common import (
    mock_x86, mock_x86_64,
    mock_machine_x86_64,
    mock_architecture_64bit)
from .common import (
    mock_centos_3_5, mock_centos_5_8, mock_machine_armv71,
    mock_centos_6_3, mock_osx_10_7, mock_solaris,
    mock_osx_12_6, mock_ubuntu_raring, mock_windows_7,
    mock_windows_10, mock_windows_11, mock_mydistro_2_8,
    mock_rocky_8_8)

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestPlatformRunningPython(unittest.TestCase):

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

    @mock_windows_10
    @mock_x86_64
    def test_windows10(self):
        # When
        platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.os, "windows")
        self.assertEqual(platform.name, "windows")
        self.assertEqual(platform.family, "windows")
        self.assertEqual(platform.release, "10")
        self.assertEqual(str(platform), "Windows 10 on x86_64")

    @mock_windows_11
    @mock_x86_64
    def test_windows11(self):
        # When
        platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.os, "windows")
        self.assertEqual(platform.name, "windows")
        self.assertEqual(platform.family, "windows")
        self.assertEqual(platform.release, "11")
        self.assertEqual(str(platform), "Windows 11 on x86_64")

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

    @mock_osx_12_6
    @mock_x86_64
    def test_osx_12(self):
        # When
        platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.os, "darwin")
        self.assertEqual(platform.name, "mac_os_x")
        self.assertEqual(platform.family, "mac_os_x")
        self.assertEqual(str(platform), "Mac OS X 12.6.5 on x86_64")

    @mock_solaris
    @mock_x86_64
    def test_solaris(self):
        # When/Then
        with self.assertRaises(OkonomiyakiError):
            Platform.from_running_python()

    @mock_centos_3_5
    def test_centos_3_5(self):
        # When
        with mock_x86:
            platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.os, "linux")
        self.assertEqual(platform.name, "centos")
        self.assertEqual(platform.family, "rhel")
        self.assertEqual(platform.release, "3.5")
        self.assertEqual(str(platform), "CentOS 3.5 on x86")

        # When
        with mock_x86_64:
            platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.os, "linux")
        self.assertEqual(platform.name, "centos")
        self.assertEqual(platform.family, "rhel")
        self.assertEqual(platform.release, "3.5")
        self.assertEqual(str(platform), "CentOS 3.5 on x86_64")

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
            "Platform(os='linux', name='centos', family='rhel', release='5.8', "
            "arch='x86', machine='x86')")

    @mock_centos_6_3
    def test_centos_6_3(self):
        # When
        with mock_x86:
            platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.os, "linux")
        self.assertEqual(platform.name, "centos")
        self.assertEqual(platform.family, "rhel")
        self.assertEqual(platform.release, "6.3")
        self.assertEqual(str(platform), "CentOS 6.3 on x86")

        # When
        with mock_x86_64:
            platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.os, "linux")
        self.assertEqual(platform.name, "centos")
        self.assertEqual(platform.family, "rhel")
        self.assertEqual(platform.release, "6.3")
        self.assertEqual(str(platform), "CentOS 6.3 on x86_64")

    @mock_rocky_8_8
    def test_rocky_8_8(self):
        # When
        with mock_x86:
            platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.os, "linux")
        self.assertEqual(platform.name, "rocky")
        self.assertEqual(platform.family, "rhel")
        self.assertEqual(platform.release, "8.8")
        self.assertEqual(str(platform), "Rocky Linux 8.8 on x86")

        # When
        with mock_x86_64:
            platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.os, "linux")
        self.assertEqual(platform.name, "rocky")
        self.assertEqual(platform.family, "rhel")
        self.assertEqual(platform.release, "8.8")
        self.assertEqual(str(platform), "Rocky Linux 8.8 on x86_64")

    @mock_mydistro_2_8
    def test_mydistro_2_8(self):
        # When
        with mock_x86:
            platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.os, "linux")
        self.assertEqual(platform.name, "unknown")
        self.assertEqual(platform.family, "rhel")
        self.assertEqual(platform.release, "2.8")
        self.assertEqual(str(platform), "Unknown distribution 2.8 on x86")

        # When
        with mock_x86_64:
            platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.os, "linux")
        self.assertEqual(platform.name, "unknown")
        self.assertEqual(platform.family, "rhel")
        self.assertEqual(platform.release, "2.8")
        self.assertEqual(str(platform), "Unknown distribution 2.8 on x86_64")

    @mock_centos_6_3
    @mock_machine_armv71
    def test_centos_6_3_arm(self):
        # When/Then
        with self.assertRaises(OkonomiyakiError):
            Platform.from_running_python()

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
            "Platform(os='linux', name='ubuntu', family='debian', release='13.04', "
            "arch='x86', machine='x86')")


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
        self.assertEqual(platform.os, "windows")
        self.assertEqual(platform.arch.name, "x86_64")
        self.assertEqual(platform.machine.name, "x86_64")

        # Given
        arch_string = "x86_64"

        # When
        platform = Platform.from_running_system(arch_string)

        # Then
        self.assertEqual(platform.os, "windows")
        self.assertEqual(platform.arch.name, "x86_64")
        self.assertEqual(platform.machine.name, "x86_64")

        # Given
        arch_string = "x86"

        # When
        platform = Platform.from_running_system(arch_string)

        # Then
        self.assertEqual(platform.os, "windows")
        self.assertEqual(platform.arch.name, "x86")
        self.assertEqual(platform.machine.name, "x86_64")

    @mock_windows_7
    @mock_x86
    def test_windows7_32bit(self):
        # Given
        arch_string = None

        # When/Then
        with mock_architecture_64bit:
            platform = Platform.from_running_system(arch_string)

        # Then
        self.assertEqual(platform.os, "windows")
        self.assertEqual(platform.arch.name, "x86")
        self.assertEqual(platform.machine.name, "x86")

        # Given
        arch_string = "x86_64"

        # When/Then
        with self.assertRaises(OkonomiyakiError):
            Platform.from_running_system(arch_string)

        # Given
        arch_string = "x86"

        # When
        platform = Platform.from_running_system(arch_string)

        # Then
        self.assertEqual(platform.os, "windows")
        self.assertEqual(platform.arch.name, "x86")
        self.assertEqual(platform.machine.name, "x86")


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
