from __future__ import absolute_import

import unittest

from ..platform import Arch, Platform
from ..platform_filters import PlatformLabel

RH5_32 = Platform.from_epd_platform_string("rh5-32")
RH5_64 = Platform.from_epd_platform_string("rh5-64")
OSX_32 = Platform.from_epd_platform_string("osx-32")
WIN_64 = Platform.from_epd_platform_string("win-64")

UBUNTU_12_10_X32 = Platform("linux", "ubuntu", "debian", Arch.from_name("x86"),
                            release="12.10")
UBUNTU_14_04_X32 = Platform("linux", "ubuntu", "debian", Arch.from_name("x86"),
                            release="14.04")
UBUNTU_14_04_X64 = Platform("linux", "ubuntu", "debian",
                            Arch.from_name("x86_64"), release="14.04")


class TestPlatformLabel(unittest.TestCase):
    def test_bitwidth_only(self):
        # Given
        label = PlatformLabel(arch=Arch.from_name("x86"))

        # When/Then
        self.assertTrue(label.matches(RH5_32))
        self.assertFalse(label.matches(RH5_64))
        self.assertTrue(label.matches(OSX_32))
        self.assertFalse(label.matches(WIN_64))

    def test_os(self):
        # Given
        label = PlatformLabel(os="windows")

        # When/Then
        self.assertFalse(label.matches(RH5_32))
        self.assertFalse(label.matches(RH5_64))
        self.assertFalse(label.matches(OSX_32))
        self.assertTrue(label.matches(WIN_64))

    def test_name(self):
        # Given
        label = PlatformLabel(name="centos")

        # When/Then
        self.assertFalse(label.matches(RH5_32))
        self.assertFalse(label.matches(RH5_64))
        self.assertFalse(label.matches(OSX_32))
        self.assertFalse(label.matches(WIN_64))

    def test_specific(self):
        # Given
        label = PlatformLabel(name="ubuntu", arch=Arch.from_name("x86"),
                              release="14.04")

        # When/Then
        self.assertFalse(label.matches(RH5_32))
        self.assertFalse(label.matches(RH5_64))
        self.assertFalse(label.matches(OSX_32))
        self.assertFalse(label.matches(WIN_64))
        self.assertFalse(label.matches(UBUNTU_12_10_X32))
        self.assertTrue(label.matches(UBUNTU_14_04_X32))
        self.assertFalse(label.matches(UBUNTU_14_04_X64))
