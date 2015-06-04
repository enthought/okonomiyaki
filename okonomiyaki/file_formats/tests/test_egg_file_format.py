import os
import os.path
import shutil
import sys
import tempfile
import textwrap
import zipfile2

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import os.path as op

from ...errors import InvalidEggName, InvalidMetadata, UnsupportedMetadata
from ..egg import EggBuilder
from .._egg_info import (
    Requirement, Dependencies, EggMetadata, LegacySpecDepend, parse_rawspec,
    split_egg_name
)
from .._package_info import PackageInfo
from ...platforms import EPDPlatform
from ...platforms.legacy import LegacyEPDPlatform
from ...versions import EnpkgVersion

from .common import DATA_DIR, ENSTALLER_EGG, ETS_EGG, MKL_EGG, PIP_PKG_INFO


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
        pkg_info = PackageInfo("1.2", "Qt_debug", "4.8.5")
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


class TestRequirement(unittest.TestCase):
    def test_str(self):
        dependency = Requirement(name="numpy")
        r_str = "numpy"

        self.assertEqual(r_str, str(dependency))

        dependency = Requirement(name="numpy", version_string="1.7.1")
        r_str = "numpy 1.7.1"

        self.assertEqual(r_str, str(dependency))

        dependency = Requirement(name="numpy", version_string="1.7.1",
                                 build_number=1)
        r_str = "numpy 1.7.1-1"

        self.assertEqual(r_str, str(dependency))

        dependency = Requirement("numpy", "1.7.1", 1)
        r_str = "numpy 1.7.1-1"

        self.assertEqual(r_str, str(dependency))

    def test_from_spec_string(self):
        dependency = Requirement.from_spec_string("numpy")
        self.assertEqual(dependency.name, "numpy")
        self.assertEqual(dependency.version_string, "")
        self.assertEqual(dependency.build_number, -1)
        self.assertEqual(dependency.strictness, 1)

        dependency = Requirement.from_spec_string("numpy 1.7.1")
        self.assertEqual(dependency.name, "numpy")
        self.assertEqual(dependency.version_string, "1.7.1")
        self.assertEqual(dependency.build_number, -1)
        self.assertEqual(dependency.strictness, 2)

        dependency = Requirement.from_spec_string("numpy 1.7.1-2")
        self.assertEqual(dependency.name, "numpy")
        self.assertEqual(dependency.version_string, "1.7.1")
        self.assertEqual(dependency.build_number, 2)
        self.assertEqual(dependency.strictness, 3)

    def test_from_string(self):
        dependency = Requirement.from_string("numpy-1.7.1-2", 3)
        self.assertEqual(dependency.name, "numpy")
        self.assertEqual(dependency.version_string, "1.7.1")
        self.assertEqual(dependency.build_number, 2)

        dependency = Requirement.from_string("numpy-1.7.1-2", 2)
        self.assertEqual(dependency.name, "numpy")
        self.assertEqual(dependency.version_string, "1.7.1")
        self.assertEqual(dependency.build_number, -1)

        dependency = Requirement.from_string("numpy-1.7.1-2", 1)
        self.assertEqual(dependency.name, "numpy")
        self.assertEqual(dependency.version_string, "")
        self.assertEqual(dependency.build_number, -1)

        self.assertRaises(InvalidEggName, lambda:
                          Requirement.from_string("numpy"))
        self.assertRaises(InvalidEggName, lambda:
                          Requirement.from_string("numpy 1.7.1"))


class TestLegacySpecDepend(unittest.TestCase):
    def test_create_from_egg1(self):
        egg = op.join(DATA_DIR, "Cython-0.19.1-1.egg")
        self._test_create_from_egg(egg)

    def test_create_from_egg2(self):
        egg = op.join(DATA_DIR, "ets-4.3.0-3.egg")
        self._test_create_from_egg(egg)

    def _test_create_from_egg(self, egg_path):
        with zipfile2.ZipFile(egg_path, "r") as zp:
            r_spec_depend = zp.read("EGG-INFO/spec/depend").decode()

        spec_depend = LegacySpecDepend.from_egg(egg_path)

        self.maxDiff = 4096
        self.assertMultiLineEqual(spec_depend.to_string(), r_spec_depend)

    def test_from_string(self):
        # Given
        r_depend = """\
metadata_version = '1.1'
name = 'Qt_debug'
version = '4.8.5'
build = 2

arch = 'x86'
platform = 'linux2'
osdist = 'RedHat_5'
python = '2.7'
packages = [
  'Qt 4.8.5',
]
"""

        # When
        depend = LegacySpecDepend.from_string(r_depend)

        # Then
        self.assertMultiLineEqual(depend.to_string(), r_depend)
        self.assertEqual(depend.packages,
                         [Requirement.from_spec_string("Qt 4.8.5")])

    def test_from_string_no_python_tag_no_default(self):
        # Given
        r_depend = """\
metadata_version = '1.1'
name = 'Qt_debug'
version = '4.8.5'
build = 2

arch = 'x86'
platform = 'linux2'
osdist = 'RedHat_5'
python = '3.2'
packages = [
  'Qt 4.8.5',
]
"""

        # When/Then
        with self.assertRaises(InvalidMetadata) as exc:
            LegacySpecDepend.from_string(r_depend)
        self.assertEqual(exc.exception.attribute, "python_tag")

    def test_to_string(self):
        # Given
        r_depend = """\
metadata_version = '1.2'
name = 'Qt_debug'
version = '4.8.5'
build = 2

arch = 'x86'
platform = 'linux2'
osdist = 'RedHat_5'
python = None
python_tag = None
packages = []
"""

        # When
        depend = LegacySpecDepend.from_string(r_depend)

        # Then
        self.assertMultiLineEqual(depend.to_string(), r_depend)
        self.assertEqual(depend.packages, [])

    def test_windows_platform(self):
        r_depend = """\
metadata_version = "1.1"
name= "Qt_debug"
version = "4.8.5"
build = 2

arch = 'x86'
platform = 'win32'
osdist = None

python = "2.7"
packages = [
]
"""
        depend = LegacySpecDepend.from_string(r_depend)

        # Then
        self.assertEqual(depend.arch, "x86")
        self.assertEqual(depend.platform, "win32")
        self.assertIsNone(depend.osdist)
        self.assertEqual(
            depend._epd_legacy_platform,
            LegacyEPDPlatform.from_epd_platform_string("win-32")
        )

    def test_format_1_3(self):
        r_depend = """\
metadata_version = "1.3"
name= "numpy_debug"
version = "1.9.2"
build = 3

arch = 'x86'
platform = 'win32'
osdist = None

python = "2.7"
python_tag = "cp27"
abi_tag = "cp27m"
platform_tag = "win32"

packages = [
]
"""
        depend = LegacySpecDepend.from_string(r_depend)

        # Then
        self.assertEqual(depend._metadata_version, "1.3")
        self.assertEqual(depend.python_tag, "cp27")
        self.assertEqual(depend.abi_tag, "cp27m")
        self.assertEqual(depend.platform_tag, "win32")

    def test_unsupported_metadata_version(self):
        # Given
        s = """\
metadata_version = "1.4"

name = "foo"
version = "1.0"
build = 1

arch = "amd64"
platform = "darwin"
osdist = None

python = "2.7"

abi_tag = "none"
platform_tag = "macosx_10_6_i386"
python_tag = "cp27"

packages = []
"""

        # When/Then
        with self.assertRaises(UnsupportedMetadata):
            LegacySpecDepend.from_string(s)


class TestLegacySpecDependAbi(unittest.TestCase):
    def test_default_no_python_egg(self):
        # Given
        spec_depend_string = """\
metadata_version = '1.1'
name = 'MKL'
version = '10.3'
build = 1

arch = 'amd64'
platform = 'darwin'
osdist = None
python = None
packages = []
"""

        # When
        spec_depend = LegacySpecDepend.from_string(spec_depend_string)

        # Then
        self.assertIsNone(spec_depend.abi_tag, None)

    def test_default_pure_python_egg(self):
        # Given
        spec_depend_string = """\
metadata_version = '1.1'
name = 'nose'
version = '1.3.4'
build = 1

arch = 'amd64'
platform = 'darwin'
osdist = None
python = '2.7'
packages = []
"""

        # When
        spec_depend = LegacySpecDepend.from_string(spec_depend_string)

        # Then
        self.assertEqual(spec_depend.abi_tag, "cp27m")

    def test_default_extension_python_egg(self):
        # Given
        spec_depend_string = """\
metadata_version = '1.1'
name = 'numpy'
version = '1.9.2'
build = 1

arch = 'amd64'
platform = 'darwin'
osdist = None
python = '2.7'
packages = [
  'MKL 10.3-1',
]
"""

        # When
        spec_depend = LegacySpecDepend.from_string(spec_depend_string)

        # Then
        self.assertEqual(spec_depend.abi_tag, "cp27m")

    def test_default_pure_python_egg_pypi(self):
        # Given
        spec_depend_string = """\
metadata_version = '1.1'
name = 'numpydoc'
version = '0.4'
build = 1

arch = None
platform = None
osdist = None
python = '2.7'
packages = [
  'sphinx',
]
"""

        # When
        spec_depend = LegacySpecDepend.from_string(spec_depend_string)

        # Then
        self.assertIsNone(spec_depend.abi_tag)

    def test_to_string(self):
        # Given
        r_spec_depend_string = """\
metadata_version = '1.3'
name = 'nose'
version = '1.3.4'
build = 1

arch = 'amd64'
platform = 'darwin'
osdist = None
python = '2.7'

python_tag = 'cp27'
abi_tag = 'cp27m'
platform_tag = 'macosx_10_6_x86_64'

packages = []
"""

        spec_depend_string = """\
metadata_version = '1.1'
name = 'nose'
version = '1.3.4'
build = 1

arch = 'amd64'
platform = 'darwin'
osdist = None
python = '2.7'
packages = []
"""

        # When
        spec_depend = LegacySpecDepend.from_string(spec_depend_string)
        # A bit of an hack, but this is the only way to force a specific
        # metadata version for to_string for now
        spec_depend._metadata_version = "1.3"
        spec_depend_string = spec_depend.to_string()

        # Then
        self.assertMultiLineEqual(spec_depend_string, r_spec_depend_string)


class TestLegacySpecDependPlatform(unittest.TestCase):
    def test_default_win_64(self):
        # Given
        spec_depend_string = """\
metadata_version = '1.1'
name = 'MKL'
version = '10.3'
build = 1

arch = 'amd64'
platform = 'win32'
osdist = None

python = None
packages = []
"""

        # When
        spec_depend = LegacySpecDepend.from_string(spec_depend_string)

        # Then
        self.assertEqual(spec_depend.platform_tag, "win_amd64")

    def test_default_win_32(self):
        # Given
        spec_depend_string = """\
metadata_version = '1.1'
name = 'MKL'
version = '10.3'
build = 1

arch = 'i386'
platform = 'win32'
osdist = None

python = None
packages = []
"""

        # When
        spec_depend = LegacySpecDepend.from_string(spec_depend_string)

        # Then
        self.assertEqual(spec_depend.platform_tag, "win32")

    def test_default_rh5_32(self):
        # Given
        spec_depend_string = """\
metadata_version = '1.1'
name = 'MKL'
version = '10.3'
build = 1

arch = 'i386'
platform = 'linux2'
osdist = 'RedHat_5'

python = None
packages = []
"""

        # When
        spec_depend = LegacySpecDepend.from_string(spec_depend_string)

        # Then
        self.assertEqual(spec_depend.platform_tag, "linux_i686")

    def test_default_rh5_64(self):
        # Given
        spec_depend_string = """\
metadata_version = '1.1'
name = 'MKL'
version = '10.3'
build = 1

arch = 'amd64'
platform = 'linux2'
osdist = 'RedHat_5'

python = None
packages = []
"""

        # When
        spec_depend = LegacySpecDepend.from_string(spec_depend_string)

        # Then
        self.assertEqual(spec_depend.platform_tag, "linux_x86_64")

    def test_default_all_none(self):
        # Given
        spec_depend_string = """\
metadata_version = '1.1'
name = 'MKL'
version = '10.3'
build = 1

arch = None
platform = None
osdist = None
python = None
packages = []
"""

        # When
        spec_depend = LegacySpecDepend.from_string(spec_depend_string)

        # Then
        self.assertIsNone(spec_depend.platform_tag)


class TestEggName(unittest.TestCase):
    def test_split_egg_name(self):
        egg_name = "numpy-1.7.1-1.egg"
        r_name = "numpy"
        r_version = "1.7.1"
        r_build = 1

        self.assertEqual(split_egg_name(egg_name)[0], r_name)
        self.assertEqual(split_egg_name(egg_name)[1], r_version)
        self.assertEqual(split_egg_name(egg_name)[2], r_build)

    def test_split_egg_name_invalid(self):
        self.assertRaises(InvalidEggName,
                          lambda: split_egg_name("numpy-1.7.1-1"))
        self.assertRaises(InvalidEggName,
                          lambda: split_egg_name("numpy-1.6.1"))


class TestParseRawspec(unittest.TestCase):
    def test_simple_unsupported(self):
        # Given
        spec_string = "metadata_version = '1.0'"

        # When/Then
        with self.assertRaises(UnsupportedMetadata):
            parse_rawspec(spec_string)

    def test_simple_1_2(self):
        r_spec = {'arch': 'x86',
                  'build': 1,
                  'metadata_version': "1.2",
                  'name': 'Cython',
                  'osdist': 'RedHat_5',
                  'packages': [],
                  'platform': 'linux2',
                  'python': '2.7',
                  'python_tag': 'cp27',
                  'version': '0.19.1'}

        spec_s = """\
metadata_version = '1.2'
name = 'Cython'
version = '0.19.1'
build = 1

arch = 'x86'
platform = 'linux2'
osdist = 'RedHat_5'
python = '2.7'
python_tag = 'cp27'
packages = []
"""
        spec = parse_rawspec(spec_s)
        self.assertEqual(spec, r_spec)

    def test_simple_1_1(self):
        r_spec = {'arch': 'x86',
                  'build': 1,
                  'metadata_version': "1.1",
                  'name': 'Cython',
                  'osdist': 'RedHat_5',
                  'packages': [],
                  'platform': 'linux2',
                  'python': '2.7',
                  'version': '0.19.1'}

        spec_s = """\
metadata_version = '1.1'
name = 'Cython'
version = '0.19.1'
build = 1

arch = 'x86'
platform = 'linux2'
osdist = 'RedHat_5'
python = '2.7'
packages = []
"""
        spec = parse_rawspec(spec_s)
        self.assertEqual(spec, r_spec)

    def test_with_dependencies(self):
        r_spec = {'arch': 'x86',
                  'build': 1,
                  'metadata_version': "1.1",
                  'name': 'pandas',
                  'osdist': 'RedHat_5',
                  'packages': ['numpy 1.7.1', 'python_dateutil'],
                  'platform': 'linux2',
                  'python': '2.7',
                  'version': '0.12.0'}

        spec_s = """\
metadata_version = '1.1'
name = 'pandas'
version = '0.12.0'
build = 1

arch = 'x86'
platform = 'linux2'
osdist = 'RedHat_5'
python = '2.7'
packages = [
  'numpy 1.7.1',
  'python_dateutil',
]
"""

        self.assertEqual(r_spec, parse_rawspec(spec_s))

    def test_with_none(self):
        r_spec = {'arch': 'x86',
                  'build': 1,
                  'metadata_version': "1.1",
                  'name': 'pandas',
                  'osdist': None,
                  'packages': ['numpy 1.7.1', 'python_dateutil'],
                  'platform': None,
                  'python': None,
                  'version': '0.12.0'}

        spec_s = """\
metadata_version = '1.1'
name = 'pandas'
version = '0.12.0'
build = 1

arch = 'x86'
platform = None
osdist = None
python = None
packages = [
  'numpy 1.7.1',
  'python_dateutil',
]
"""

        self.assertEqual(r_spec, parse_rawspec(spec_s))

    def test_invalid_spec_strings(self):
        # Given a spec_string without metadata_version
        spec_s = """\
name = 'pandas'
version = '0.12.0'
build = 1

arch = 'x86'
platform = None
osdist = None
python = None
packages = [
  'numpy 1.7.1',
  'python_dateutil',
]
"""

        # When/Then
        with self.assertRaises(UnsupportedMetadata) as exc:
            parse_rawspec(spec_s)

        # Given a spec_string without some other metadata in >= 1.1
        spec_s = """\
metadata_version = '1.1'
name = 'pandas'
version = '0.12.0'
build = 1

arch = 'x86'
osdist = None
python = None
packages = [
  'numpy 1.7.1',
  'python_dateutil',
]
"""

        # When/Then
        with self.assertRaises(InvalidMetadata) as exc:
            parse_rawspec(spec_s)
        self.assertEqual(exc.exception.attribute, "platform")

        # Given a spec_string without some other metadata in >= 1.2
        spec_s = """\
metadata_version = '1.2'
name = 'pandas'
version = '0.12.0'
build = 1

arch = 'x86'
osdist = None
platform = None
python = None
packages = [
  'numpy 1.7.1',
  'python_dateutil',
]
"""

        # When/Then
        with self.assertRaises(InvalidMetadata) as exc:
            parse_rawspec(spec_s)
        self.assertEqual(exc.exception.attribute, "python_tag")


class TestEggInfo(unittest.TestCase):
    def test_simple(self):
        # Given
        egg = ENSTALLER_EGG

        # When
        metadata = EggMetadata.from_egg(egg)

        # Then
        self.assertEqual(metadata.name, "enstaller")

        # When
        with zipfile2.ZipFile(egg) as zp:
            metadata = EggMetadata.from_egg(zp)

        # Then
        self.assertEqual(metadata.name, "enstaller")
        self.assertEqual(metadata.metadata_version_info, (1, 1))
        self.assertEqual(metadata.abi_tag, None)
        self.assertEqual(metadata.abi_tag_string, 'none')
        self.assertEqual(metadata.platform_tag, None)
        self.assertEqual(metadata.platform_tag_string, 'any')
        self.assertEqual(metadata.python_tag, None)
        self.assertEqual(metadata.python_tag_string, 'none')

    def test_simple_non_python_egg(self):
        # Given
        egg = MKL_EGG

        # When
        metadata = EggMetadata.from_egg(egg)

        # Then
        self.assertEqual(metadata.egg_basename, "MKL")
        self.assertEqual(metadata.name, "mkl")

        self.assertEqual(metadata.metadata_version_info, (1, 1))
        self.assertEqual(metadata.abi_tag, None)
        self.assertEqual(metadata.abi_tag_string, 'none')
        self.assertEqual(metadata.platform_tag, 'macosx_10_6_x86_64')
        self.assertEqual(metadata.platform_tag_string, 'macosx_10_6_x86_64')
        self.assertEqual(metadata.python_tag, None)
        self.assertEqual(metadata.python_tag_string, 'none')
        self.assertEqual(metadata.runtime_dependencies, tuple())

    def test_from_cross_platform_egg(self):
        # Given
        egg = ENSTALLER_EGG

        # When
        metadata = EggMetadata.from_egg(egg)

        # Then
        self.assertEqual(metadata.egg_name, os.path.basename(egg))
        self.assertEqual(metadata.kind, "egg")
        self.assertEqual(metadata.name, "enstaller")
        self.assertEqual(metadata.version, EnpkgVersion.from_string("4.5.0-1"))
        self.assertEqual(metadata.build, 1)
        self.assertEqual(metadata.upstream_version, "4.5.0")
        self.assertIsNone(metadata.python_tag)
        self.assertEqual(metadata.metadata_version_info, (1, 1))

    def test_from_platform_egg(self):
        # Given
        egg = ETS_EGG
        r_runtime_dependencies = (
            Requirement.from_spec_string('apptools 4.2.0-2'),
            Requirement.from_spec_string('blockcanvas 4.0.3-1'),
            Requirement.from_spec_string('casuarius 1.1-1'),
            Requirement.from_spec_string('chaco 4.3.0-2'),
            Requirement.from_spec_string('codetools 4.1.0-2'),
            Requirement.from_spec_string('enable 4.3.0-5'),
            Requirement.from_spec_string('enaml 0.6.8-2'),
            Requirement.from_spec_string('encore 0.3-1'),
            Requirement.from_spec_string('envisage 4.3.0-2'),
            Requirement.from_spec_string('etsdevtools 4.0.2-1'),
            Requirement.from_spec_string('etsproxy 0.1.2-1'),
            Requirement.from_spec_string('graphcanvas 4.0.2-1'),
            Requirement.from_spec_string('mayavi 4.3.0-3'),
            Requirement.from_spec_string('pyface 4.3.0-2'),
            Requirement.from_spec_string('scimath 4.1.2-2'),
            Requirement.from_spec_string('traits 4.3.0-2'),
            Requirement.from_spec_string('traitsui 4.3.0-2'),
        )

        # When
        metadata = EggMetadata.from_egg(egg)

        # Then
        self.assertEqual(metadata.egg_name, os.path.basename(egg))
        self.assertEqual(metadata.kind, "egg")
        self.assertEqual(metadata.name, "ets")
        self.assertEqual(
            metadata.version, EnpkgVersion.from_string("4.3.0-3")
        )
        self.assertEqual(metadata.build, 3)
        self.assertEqual(metadata.upstream_version, "4.3.0")
        self.assertEqual(metadata.metadata_version_info, (1, 1))
        self.assertEqual(
            metadata.platform, EPDPlatform.from_epd_string("rh5-32")
        )
        self.assertEqual(metadata.abi_tag, 'cp27m')
        self.assertEqual(metadata.abi_tag_string, 'cp27m')
        self.assertEqual(metadata.platform_tag, 'linux_i686')
        self.assertEqual(metadata.platform_tag_string, 'linux_i686')
        self.assertEqual(metadata.python_tag, 'cp27')
        self.assertEqual(metadata.python_tag_string, 'cp27')
        self.assertEqual(metadata.runtime_dependencies, r_runtime_dependencies)

    def test_to_spec_string(self):
        # Given
        egg = ETS_EGG
        r_spec_depend_string = textwrap.dedent("""\
        metadata_version = '1.1'
        name = 'ets'
        version = '4.3.0'
        build = 3

        arch = 'x86'
        platform = 'linux2'
        osdist = 'RedHat_5'
        python = '2.7'
        packages = [
          'apptools 4.2.0-2',
          'blockcanvas 4.0.3-1',
          'casuarius 1.1-1',
          'chaco 4.3.0-2',
          'codetools 4.1.0-2',
          'enable 4.3.0-5',
          'enaml 0.6.8-2',
          'encore 0.3-1',
          'envisage 4.3.0-2',
          'etsdevtools 4.0.2-1',
          'etsproxy 0.1.2-1',
          'graphcanvas 4.0.2-1',
          'mayavi 4.3.0-3',
          'pyface 4.3.0-2',
          'scimath 4.1.2-2',
          'traits 4.3.0-2',
          'traitsui 4.3.0-2',
        ]
        """)

        # When
        metadata = EggMetadata.from_egg(egg)

        # Then
        self.assertMultiLineEqual(
            metadata.spec_depend_string, r_spec_depend_string
        )
        self.assertEqual(metadata.pkg_info.name, "ets")
        self.assertEqual(
            metadata.pkg_info.summary, "Enthought Tool Suite meta-project"
        )
        self.assertEqual(
            metadata.summary,
            "components to construct custom scientific applications\n"
        )
