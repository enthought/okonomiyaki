import sys
import unittest
import re

from parameterized import parameterized
from packaging import tags

from ..pep425 import (
    compute_abi_tag, compute_python_tag, compute_platform_tag,
    generate_platform_tag)
from .._platform import OSKind, NameKind, FamilyKind, Platform
from .._arch import X86, X86_64, ARM, ARM64

def _system_tags():
    interp_name = tags.interpreter_name()
    if interp_name == "cp":
        for tag in tags.cpython_tags():
            yield tag
    else:
        for tag in tags.generic_tags():
            yield tag


class TestComputePEP425(unittest.TestCase):

    def setUp(self):
        self.tag = next(
            tag for tag in
            _system_tags()
            # We do not support the manylinux tag
            if 'manylinux' not in tag.platform)
        self.compatible_platforms = tuple(
            tag.platform for tag in _system_tags())

    def test_abi_tag(self):
        # Given
        executable = sys.executable

        # When
        abi_tag = compute_abi_tag(executable)

        # Then
        self.assertEqual(abi_tag, self.tag.abi)

    def test_abi_tag_default(self):
        # When
        abi_tag = compute_abi_tag()

        # Then
        self.assertEqual(abi_tag, self.tag.abi)

    def test_python_tag(self):
        # Given
        executable = sys.executable

        # When
        python_tag = compute_python_tag(executable)

        # Then
        self.assertEqual(python_tag, self.tag.interpreter)

    def test_python_tag_default(self):
        # When
        python_tag = compute_python_tag()

        # Then
        self.assertEqual(python_tag, self.tag.interpreter)

    def test_platform_tag(self):
        # Given
        executable = sys.executable

        # When
        platform_tag = compute_platform_tag(executable)

        # Then
        if sys.platform.startswith('darwin'):
            # packaging always sets the minor macos version to 0
            platform_tag = re.sub('macosx_11_.', 'macosx_11_0', platform_tag)
            platform_tag = re.sub('macosx_12_.', 'macosx_12_0', platform_tag)
        else:
            self.assertIn(platform_tag, self.compatible_platforms)

    def test_platform_tag_default(self):
        # When
        platform_tag = compute_platform_tag()

        # Then
        # Then
        if sys.platform.startswith('darwin'):
            # packaging always sets the minor macos version to 0
            platform_tag = re.sub('macosx_11_.', 'macosx_11_0', platform_tag)
            platform_tag = re.sub('macosx_12_.', 'macosx_12_0', platform_tag)
        else:
            self.assertIn(platform_tag, self.compatible_platforms)


class TestGeneratePEP425(unittest.TestCase):

    @parameterized.expand([
        (OSKind.darwin, X86, 'macosx_2_4_i386'),
        (OSKind.darwin, X86_64, 'macosx_2_4_x86_64'),
        (OSKind.darwin, ARM64, 'macosx_2_4_arm64'),
        (OSKind.linux, X86_64, 'linux_x86_64'),
        (OSKind.linux, ARM, 'linux_aarch32'),
        (OSKind.linux, ARM64, 'linux_aarch64'),
        (OSKind.linux, X86, 'linux_i686'),
        (OSKind.windows, X86, 'win32'),
        (OSKind.windows, X86_64, 'win_amd64'),
        (OSKind.windows, ARM64, 'win_arm64')])
    def test_platform_tag(self, os_kind, arch, expected):
        # Given
        platform = Platform(
            os_kind, NameKind.unknown, FamilyKind.unknown, '2.4', arch, arch)

        # When/Then
        self.assertEqual(generate_platform_tag(platform), expected)
