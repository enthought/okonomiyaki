import unittest

from ...errors import OkonomiyakiError
from .._arch import Arch

from .common import (mock_machine_armv71, mock_x86, mock_x86_64,
                     mock_x86_on_x86_64)


class TestArch(unittest.TestCase):
    def test_simple(self):
        # Given
        name = "x86"
        bits = 32

        # When
        arch = Arch(name)

        # Then
        self.assertEqual(arch.name, name)
        self.assertEqual(arch.bits, bits)
        self.assertEqual(str(arch), arch.name)

    def test_hashing(self):
        # Given
        name1 = "x86"
        name2 = "i386"
        name3 = "amd64"

        # When
        arch1 = Arch(name1)
        arch2 = Arch(name2)
        arch3 = Arch(name3)

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
