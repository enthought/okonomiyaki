import unittest

from okonomiyaki.errors import OkonomiyakiError
from ..platform import Arch, Platform

from .common import (mock_machine_armv71, mock_x86, mock_x86_64,
                     mock_x86_on_x86_64, mock_machine_x86_64)
from .common import (mock_centos_5_8, mock_osx_10_7, mock_ubuntu_raring,
                     mock_windows_7)


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
        self.assertEqual(str(platform), "CentOS on x86")

    @mock_ubuntu_raring
    @mock_x86
    def test_ubuntu_raring(self):
        # When
        platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.os, "linux")
        self.assertEqual(platform.name, "ubuntu")
        self.assertEqual(platform.family, "debian")
        self.assertEqual(str(platform), "Ubuntu on x86")

    @mock_windows_7
    @mock_x86
    def test_windows7(self):
        # When
        platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.os, "windows")
        self.assertEqual(platform.name, "windows")
        self.assertEqual(platform.family, "windows")
        self.assertEqual(str(platform), "Windows on x86")

    @mock_osx_10_7
    @mock_x86
    def test_osx_10_7(self):
        # When
        platform = Platform.from_running_python()

        # Then
        self.assertEqual(platform.os, "darwin")
        self.assertEqual(platform.name, "mac_os_x")
        self.assertEqual(platform.family, "mac_os_x")
        self.assertEqual(str(platform), "Mac OS X on x86")


class TestPlatformRunningSystem(unittest.TestCase):
    @mock_windows_7
    @mock_machine_x86_64
    def test_windows7(self):
        # Given
        arch_string = None

        # When
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
