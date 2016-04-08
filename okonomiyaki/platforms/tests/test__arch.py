import sys

from ...errors import OkonomiyakiError
from .._arch import Arch

from .common import (mock_machine_armv71, mock_x86, mock_x86_64,
                     mock_x86_on_x86_64)

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestArch(unittest.TestCase):
    def test_simple(self):
        # Given
        name = "x86"
        bits = 32

        # When
        arch = Arch.from_name(name)

        # Then
        self.assertEqual(arch.name, name)
        self.assertEqual(arch.bits, bits)
        self.assertEqual(str(arch), arch.name)
        self.assertEqual(repr(arch), "Arch(_kind=<ArchitectureKind.x86: 0>)")

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

    def test_from_unnormalized_names(self):
        # Given
        names = ("x86", "i386", "i686")

        # When
        for name in names:
            arch = Arch.from_name(name)

            # Then
            self.assertEqual(arch.name, "x86")
            self.assertEqual(arch.bits, 32)

        # Given
        names = ("x86_64", "amd64", "AMD64")

        # When
        for name in names:
            arch = Arch.from_name(name)

            # Then
            self.assertEqual(arch.name, "x86_64")
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

    def test__legacy_name(self):
        # Given
        name = "x86_64"

        # When
        arch = Arch.from_name(name)

        # Then
        self.assertEqual(arch._legacy_name, "amd64")
