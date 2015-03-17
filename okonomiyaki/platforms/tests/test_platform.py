import unittest

from okonomiyaki.errors import OkonomiyakiError
from ..platform import Arch, Platform
from ..platform import DARWIN, LINUX, MAC_OS_X, RHEL, WINDOWS, X86, X86_64

from .common import (mock_machine_armv71, mock_x86, mock_x86_64,
                     mock_x86_on_x86_64, mock_machine_x86_64)
from .common import (mock_architecture_64bit, mock_centos_3_5, mock_centos_5_8,
                     mock_centos_6_3, mock_centos_7_0, mock_osx_10_7,
                     mock_solaris, mock_ubuntu_raring, mock_windows_7)


class TestArch(unittest.TestCase):
    def test_simple(self):
        # Given
        name = "x86"
        bits = 32

        # When
        arch = Arch(name, bits)

        # Then
        self.assertEqual(arch.name, name)
        self.assertEqual(arch.bits, bits)
        self.assertEqual(str(arch), arch.name)

    def test_hashing(self):
        # Given
        name = "x86"

        # When
        arch1 = Arch(name, 32)
        arch2 = Arch(name, 32)
        arch3 = Arch(name, 64)

        # Then
        self.assertEqual(arch1, arch2)
        self.assertNotEqual(arch1, arch3)
        self.assertEqual(hash(arch1), hash(arch1))
        self.assertTrue(arch1 == arch2)
        self.assertFalse(arch1 != arch2)
        self.assertTrue(arch1 != arch3)
        self.assertFalse(arch1 == arch3)

    def test_from_name(self):
        # Given
        name = "x86"

        # When
        arch = Arch.from_name(name)

        # Then
        self.assertEqual(arch.name, name)
        self.assertEqual(arch.bits, 32)

        # Given
        name = "x86_64"

        # When
        arch = Arch.from_name(name)

        # Then
        self.assertEqual(arch.name, name)
        self.assertEqual(arch.bits, 64)

    def test_from_running_python(self):
        # When
        with mock_x86:
            arch = Arch.from_running_python()

        # Then
        self.assertEqual(arch.name, "x86")
        self.assertEqual(arch.bits, 32)

        # When
        with mock_x86_64:
            arch = Arch.from_running_python()

        # Then
        self.assertEqual(arch.name, "x86_64")
        self.assertEqual(arch.bits, 64)

        # When
        with mock_x86_on_x86_64:
            arch = Arch.from_running_python()

        # Then
        self.assertEqual(arch.name, "x86")
        self.assertEqual(arch.bits, 32)

        # Given/When/Then
        with mock_machine_armv71:
            with self.assertRaises(OkonomiyakiError):
                arch = Arch.from_running_python()

    def test_from_running_system(self):
        # When
        with mock_x86:
            arch = Arch.from_running_system()

        # Then
        self.assertEqual(arch.name, "x86")
        self.assertEqual(arch.bits, 32)

        # When
        with mock_x86_64:
            arch = Arch.from_running_system()

        # Then
        self.assertEqual(arch.name, "x86_64")
        self.assertEqual(arch.bits, 64)

        # When
        with mock_x86_on_x86_64:
            arch = Arch.from_running_system()

        # Then
        self.assertEqual(arch.name, "x86_64")
        self.assertEqual(arch.bits, 64)

        # Given/When/Then
        with mock_machine_armv71:
            with self.assertRaises(OkonomiyakiError):
                arch = Arch.from_running_system()


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
        self.assertEqual(platform._epd_platform_string, "rh5-32")

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

        with self.assertRaises(OkonomiyakiError):
            self.assertEqual(platform._epd_platform_string)

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
        self.assertEqual(platform._epd_platform_string, "win-32")

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
        self.assertEqual(platform._epd_platform_string, "osx-32")


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
        self.assertEqual(platform.epd_platform.short, "rh3-32")

        # When
        with mock_x86_64:
            platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.epd_platform.short, "rh3-64")

    @mock_centos_5_8
    def test_centos_5_8(self):
        # When
        with mock_x86:
            platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.epd_platform.short, "rh5-32")

        # When
        with mock_x86_64:
            platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.epd_platform.short, "rh5-64")

    @mock_centos_6_3
    def test_centos_6_3(self):
        # When
        with mock_x86:
            platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.epd_platform.short, "rh6-32")

        # When
        with mock_x86_64:
            platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.epd_platform.short, "rh6-64")

    @mock_centos_7_0
    def test_centos_7_0(self):
        # When
        with mock_x86:
            platform = Platform.from_running_python()

        # Then
        with self.assertRaises(OkonomiyakiError):
            platform.epd_platform.short

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
            platform.epd_platform.short

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

    def test_from_epd_platform_string(self):
        # Given
        epd_platform_string = "rh5-32"

        # When
        platform = Platform.from_epd_platform_string(epd_platform_string)

        # Then
        self.assertEqual(platform.os, LINUX)
        self.assertEqual(platform.family, RHEL)
        self.assertEqual(platform.name, RHEL)
        self.assertEqual(platform.arch, Arch.from_name(X86))
        self.assertEqual(platform.machine, Arch.from_name(X86))

        # Given
        epd_platform_string = "win-32"

        # When
        platform = Platform.from_epd_platform_string(epd_platform_string)

        # Then
        self.assertEqual(platform.os, WINDOWS)
        self.assertEqual(platform.family, WINDOWS)
        self.assertEqual(platform.name, WINDOWS)
        self.assertEqual(platform.arch, Arch.from_name(X86))
        self.assertEqual(platform.machine, Arch.from_name(X86))

        # Given
        epd_platform_string = "osx-64"

        # When
        platform = Platform.from_epd_platform_string(epd_platform_string)

        # Then
        self.assertEqual(platform.os, DARWIN)
        self.assertEqual(platform.family, MAC_OS_X)
        self.assertEqual(platform.name, MAC_OS_X)
        self.assertEqual(platform.arch, Arch.from_name(X86_64))
        self.assertEqual(platform.machine, Arch.from_name(X86_64))

        # Given
        epd_platform_string = "osx"

        # When
        with mock_x86_64:
            platform = Platform.from_epd_platform_string(epd_platform_string)

        # Then
        self.assertEqual(platform.os, DARWIN)
        self.assertEqual(platform.family, MAC_OS_X)
        self.assertEqual(platform.name, MAC_OS_X)
        self.assertEqual(platform.arch, Arch.from_name(X86_64))
        self.assertEqual(platform.machine, Arch.from_name(X86_64))

        # When
        with mock_x86:
            platform = Platform.from_epd_platform_string(epd_platform_string)

        # Then
        self.assertEqual(platform.arch, Arch.from_name(X86))
        self.assertEqual(platform.machine, Arch.from_name(X86))

    def test_from_epd_platform_string_invalid(self):
        # Given
        # Invalid bitwidth
        epd_platform_string = "linux-32-1"

        # When/Then
        with self.assertRaises(OkonomiyakiError):
            Platform.from_epd_platform_string(epd_platform_string)

        # Given
        # Invalid bitwidth
        epd_platform_string = "osx-63"

        # When/Then
        with self.assertRaises(OkonomiyakiError):
            Platform.from_epd_platform_string(epd_platform_string)

        # Given
        # Invalid platform basename
        epd_platform_string = "netbsd-32"

        # When/Then
        with self.assertRaises(OkonomiyakiError):
            Platform.from_epd_platform_string(epd_platform_string)
