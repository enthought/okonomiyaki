import sys
import unittest

try:
    from pip import pep425tags as pip_pep425
    HAS_PIP_PEP425 = True
except ImportError as e:
    print(e)
    HAS_PIP_PEP425 = False

from ..pep425 import compute_abi_tag, compute_python_tag, compute_platform_tag


@unittest.skipIf(
    not HAS_PIP_PEP425, "Could not import pip.pep425 for comparison"
)
class TestPEP425(unittest.TestCase):
    def test_abi_tag(self):
        # Given
        executable = sys.executable
        r_abi_tag = pip_pep425.get_abi_tag()

        # When
        abi_tag = compute_abi_tag(executable)

        # Then
        self.assertEqual(abi_tag, r_abi_tag)

    def test_abi_tag_default(self):
        # Given
        r_abi_tag = pip_pep425.get_abi_tag()

        # When
        abi_tag = compute_abi_tag()

        # Then
        self.assertEqual(abi_tag, r_abi_tag)

    def test_python_tag(self):
        # Given
        executable = sys.executable
        r_python_tag = pip_pep425.get_impl_tag()

        # When
        python_tag = compute_python_tag(executable)

        # Then
        self.assertEqual(python_tag, r_python_tag)

    def test_python_tag_default(self):
        # Given
        r_python_tag = pip_pep425.get_impl_tag()

        # When
        python_tag = compute_python_tag()

        # Then
        self.assertEqual(python_tag, r_python_tag)

    def test_platform_tag(self):
        # Given
        executable = sys.executable
        r_platform_tag = pip_pep425.get_platform()

        # When
        platform_tag = compute_platform_tag(executable)

        # Then
        self.assertEqual(platform_tag, r_platform_tag)

    def test_platform_tag_default(self):
        # Given
        r_platform_tag = pip_pep425.get_platform()

        # When
        platform_tag = compute_platform_tag()

        # Then
        self.assertEqual(platform_tag, r_platform_tag)
