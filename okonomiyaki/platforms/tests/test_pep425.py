import sys
import unittest

from packaging import tags

from ..pep425 import compute_abi_tag, compute_python_tag, compute_platform_tag


def _system_tags():
    interp_name = tags.interpreter_name()
    if interp_name == "cp":
        for tag in tags.cpython_tags():
            yield tag
    else:
        for tag in tags.generic_tags():
            yield tag


class TestPEP425(unittest.TestCase):
    def test_abi_tag(self):
        # Given
        executable = sys.executable
        tag = next(_system_tags())

        # When
        abi_tag = compute_abi_tag(executable)

        # Then
        self.assertEqual(abi_tag, tag.abi)

    def test_abi_tag_default(self):
        # Given
        tag = next(_system_tags())

        # When
        abi_tag = compute_abi_tag()

        # Then
        self.assertEqual(abi_tag, tag.abi)

    def test_python_tag(self):
        # Given
        executable = sys.executable
        tag = next(_system_tags())

        # When
        python_tag = compute_python_tag(executable)

        # Then
        self.assertEqual(python_tag, tag.interpreter)

    def test_python_tag_default(self):
        # Given
        tag = next(_system_tags())

        # When
        python_tag = compute_python_tag()

        # Then
        self.assertEqual(python_tag, tag.interpreter)

    def test_platform_tag(self):
        # Given
        executable = sys.executable
        tag = next(_system_tags())

        # When
        platform_tag = compute_platform_tag(executable)

        # Then
        self.assertEqual(platform_tag, tag.platform)

    def test_platform_tag_default(self):
        # Given
        tag = next(_system_tags())

        # When
        platform_tag = compute_platform_tag()

        # Then
        self.assertEqual(platform_tag, tag.platform)
