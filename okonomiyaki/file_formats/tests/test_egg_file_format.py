import os
import os.path
import shutil
import sys
import tempfile
import zipfile2

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import os.path as op

from ...platforms import EPDPlatform
from ...versions import EnpkgVersion

from ..egg import EggBuilder
from .._egg_info import Dependencies, EggMetadata, LegacySpecDepend
from .._package_info import PackageInfo

from .common import PIP_PKG_INFO


class TestEggBuilder(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_simple(self):
        r_files = [
            "EGG-INFO/PKG-INFO",
            "EGG-INFO/spec/depend",
            "EGG-INFO/spec/summary",
        ]
        r_spec_depend = """\
metadata_version = '1.1'
name = 'Qt_debug'
version = '4.8.5'
build = 2

arch = 'x86'
platform = 'linux2'
osdist = 'RedHat_5'
python = '2.7'
packages = []
"""

        spec_depend = LegacySpecDepend.from_string(r_spec_depend)
        pkg_info = PackageInfo("1.1", "Qt_debug", "4.8.5")
        metadata = EggMetadata._from_spec_depend(spec_depend, pkg_info, "")

        with EggBuilder(metadata, cwd=self.d) as fp:
            pass

        egg_path = op.join(self.d, "Qt_debug-4.8.5-2.egg")
        self.assertTrue(op.exists(egg_path))

        with zipfile2.ZipFile(egg_path, "r") as fp:
            self.assertEqual(set(fp.namelist()), set(r_files))
            self.assertMultiLineEqual(fp.read("EGG-INFO/spec/depend").decode(),
                                      r_spec_depend)

    def _create_fake_metadata(self):
        pkg_info = PackageInfo.from_string(PIP_PKG_INFO)
        pkg_info.version = "4.8.6"
        pkg_info.name = "Qt_debug"

        version = EnpkgVersion.from_upstream_and_build(pkg_info.version, 1)
        platform = EPDPlatform.from_epd_string("rh5-32")
        dependencies = Dependencies((), ())

        return EggMetadata(
            pkg_info.name, version, platform, "cp27", "cp27m", dependencies,
            pkg_info, pkg_info.summary
        )

    def test_reject_no_pkg_info(self):
        # Given
        version = EnpkgVersion.from_string("4.8.4-1")
        platform = EPDPlatform.from_epd_string("rh5-64")
        dependencies = Dependencies((), ())

        metadata = EggMetadata("foo", version, platform, "cp27",
                               "cp27m", dependencies, None, "")

        # When/Then
        with self.assertRaises(ValueError):
            EggBuilder(metadata)

    def test_simple_with_tree(self):
        # Given
        r_files = [
            "EGG-INFO/PKG-INFO",
            "EGG-INFO/spec/depend",
            "EGG-INFO/spec/summary",
            "EGG-INFO/usr/bin/",
            "EGG-INFO/usr/bin/exe",
        ]

        tree = os.path.join(self.d, "usr")
        exe = os.path.join(tree, "bin", "exe")
        os.makedirs(os.path.dirname(exe))
        with open(exe, "wb") as fp:
            fp.write(b"some fake executable")

        metadata = self._create_fake_metadata()

        # When
        with EggBuilder(metadata, cwd=self.d) as fp:
            fp.add_tree(tree, "EGG-INFO/usr")

        # Then
        egg_path = os.path.join(self.d, "Qt_debug-4.8.6-1.egg")
        self.assertTrue(os.path.exists(egg_path))

        with zipfile2.ZipFile(egg_path, "r") as fp:
            self.assertEqual(set(fp.namelist()), set(r_files))

    def test_add_file(self):
        # Given
        r_files = [
            "EGG-INFO/PKG-INFO",
            "EGG-INFO/spec/depend",
            "EGG-INFO/spec/summary",
            "exe",
        ]

        tree = os.path.join(self.d, "usr")
        exe = os.path.join(tree, "bin", "exe")
        os.makedirs(os.path.dirname(exe))
        with open(exe, "wb") as fp:
            fp.write(b"some fake executable")

        metadata = self._create_fake_metadata()

        # When
        with EggBuilder(metadata, cwd=self.d) as fp:
            fp.add_file(exe)

        # Then
        egg_path = os.path.join(self.d, "Qt_debug-4.8.6-1.egg")
        self.assertTrue(os.path.exists(egg_path))

        with zipfile2.ZipFile(egg_path, "r") as fp:
            self.assertEqual(set(fp.namelist()), set(r_files))

        # Given
        r_files = [
            "EGG-INFO/PKG-INFO",
            "EGG-INFO/spec/depend",
            "EGG-INFO/spec/summary",
            "bin/exe",
        ]

        # When
        with EggBuilder(metadata, cwd=self.d) as fp:
            fp.add_file(exe, "bin")

        # Then
        egg_path = os.path.join(self.d, "Qt_debug-4.8.6-1.egg")
        self.assertTrue(os.path.exists(egg_path))

        with zipfile2.ZipFile(egg_path, "r") as fp:
            self.assertEqual(set(fp.namelist()), set(r_files))

        # Given
        r_files = [
            "EGG-INFO/PKG-INFO",
            "EGG-INFO/spec/depend",
            "EGG-INFO/spec/summary",
            "foo.exe",
        ]

        # When
        with EggBuilder(metadata, cwd=self.d) as fp:
            fp.add_file_as(exe, "foo.exe")

        # Then
        egg_path = os.path.join(self.d, "Qt_debug-4.8.6-1.egg")
        self.assertTrue(os.path.exists(egg_path))

        with zipfile2.ZipFile(egg_path, "r") as fp:
            self.assertEqual(set(fp.namelist()), set(r_files))

        # Given
        r_files = [
            "EGG-INFO/PKG-INFO",
            "EGG-INFO/spec/depend",
            "EGG-INFO/spec/summary",
            "foo.exe",
        ]

        # When
        with EggBuilder(metadata, cwd=self.d) as fp:
            fp.add_data(b"data", "foo.exe")

        # Then
        egg_path = os.path.join(self.d, "Qt_debug-4.8.6-1.egg")
        self.assertTrue(os.path.exists(egg_path))

        with zipfile2.ZipFile(egg_path, "r") as fp:
            self.assertEqual(set(fp.namelist()), set(r_files))
            self.assertEqual(fp.read("foo.exe"), b"data")

    def test_simple_with_iterator(self):
        # Given
        r_files = [
            "EGG-INFO/PKG-INFO",
            "EGG-INFO/spec/depend",
            "EGG-INFO/spec/summary",
            "EGG-INFO/usr/bin/exe",
        ]

        tree = os.path.join(self.d, "usr")
        exe = os.path.join(tree, "bin", "exe")
        os.makedirs(os.path.dirname(exe))
        with open(exe, "wb") as fp:
            fp.write(b"some fake executable")

        metadata = self._create_fake_metadata()

        def it():
            yield (exe, "EGG-INFO/usr/bin/exe")

        # When
        with EggBuilder(metadata, cwd=self.d) as fp:
            fp.add_iterator(it())

        # Then
        egg_path = os.path.join(self.d, "Qt_debug-4.8.6-1.egg")
        self.assertTrue(os.path.exists(egg_path))

        with zipfile2.ZipFile(egg_path, "r") as fp:
            self.assertEqual(set(fp.namelist()), set(r_files))
