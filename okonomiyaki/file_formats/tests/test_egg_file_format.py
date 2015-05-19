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

from ...errors import InvalidEggName, InvalidMetadata
from ..egg import (
    Dependency, EggBuilder, EggMetadata, parse_rawspec, split_egg_name
)
from .._egg_info import LegacySpecDepend
from ...platforms import Platform
from ...platforms.legacy import LegacyEPDPlatform
from ...versions import EnpkgVersion

from ... import repositories

DATA_DIR = op.join(op.dirname(repositories.__file__), "tests", "data")

ENSTALLER_EGG = op.join(DATA_DIR, "enstaller-4.5.0-1.egg")
ETS_EGG = op.join(DATA_DIR, "ets-4.3.0-3.egg")


class TestEggBuilder(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_simple(self):
        r_files = ["EGG-INFO/spec/depend"]
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
        metadata = EggMetadata._from_spec_depend(spec_depend, None, "")

        with EggBuilder(metadata, cwd=self.d) as fp:
            pass

        egg_path = op.join(self.d, "Qt_debug-4.8.5-2.egg")
        self.assertTrue(op.exists(egg_path))

        with zipfile2.ZipFile(egg_path, "r") as fp:
            self.assertEqual(fp.namelist(), r_files)
            self.assertMultiLineEqual(fp.read("EGG-INFO/spec/depend").decode(),
                                      r_spec_depend)


class TestDependency(unittest.TestCase):
    def test_str(self):
        dependency = Dependency(name="numpy")
        r_str = "numpy"

        self.assertEqual(r_str, str(dependency))

        dependency = Dependency(name="numpy", version_string="1.7.1")
        r_str = "numpy 1.7.1"

        self.assertEqual(r_str, str(dependency))

        dependency = Dependency(name="numpy", version_string="1.7.1",
                                build_number=1)
        r_str = "numpy 1.7.1-1"

        self.assertEqual(r_str, str(dependency))

        dependency = Dependency("numpy", "1.7.1", 1)
        r_str = "numpy 1.7.1-1"

        self.assertEqual(r_str, str(dependency))

    def test_from_spec_string(self):
        dependency = Dependency.from_spec_string("numpy")
        self.assertEqual(dependency.name, "numpy")
        self.assertEqual(dependency.version_string, "")
        self.assertEqual(dependency.build_number, -1)
        self.assertEqual(dependency.strictness, 1)

        dependency = Dependency.from_spec_string("numpy 1.7.1")
        self.assertEqual(dependency.name, "numpy")
        self.assertEqual(dependency.version_string, "1.7.1")
        self.assertEqual(dependency.build_number, -1)
        self.assertEqual(dependency.strictness, 2)

        dependency = Dependency.from_spec_string("numpy 1.7.1-2")
        self.assertEqual(dependency.name, "numpy")
        self.assertEqual(dependency.version_string, "1.7.1")
        self.assertEqual(dependency.build_number, 2)
        self.assertEqual(dependency.strictness, 3)

    def test_from_string(self):
        dependency = Dependency.from_string("numpy-1.7.1-2", 3)
        self.assertEqual(dependency.name, "numpy")
        self.assertEqual(dependency.version_string, "1.7.1")
        self.assertEqual(dependency.build_number, 2)

        dependency = Dependency.from_string("numpy-1.7.1-2", 2)
        self.assertEqual(dependency.name, "numpy")
        self.assertEqual(dependency.version_string, "1.7.1")
        self.assertEqual(dependency.build_number, -1)

        dependency = Dependency.from_string("numpy-1.7.1-2", 1)
        self.assertEqual(dependency.name, "numpy")
        self.assertEqual(dependency.version_string, "")
        self.assertEqual(dependency.build_number, -1)

        self.assertRaises(InvalidEggName, lambda:
                          Dependency.from_string("numpy"))
        self.assertRaises(InvalidEggName, lambda:
                          Dependency.from_string("numpy 1.7.1"))


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
        depend = LegacySpecDepend.from_string(r_depend)

        self.assertMultiLineEqual(depend.to_string(), r_depend)

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

    def test_windows_platform(self):
        r_legacy_epd_platform = \
            LegacyEPDPlatform.from_epd_platform_string("win-32")
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
        with self.assertRaises(InvalidMetadata):
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
        with self.assertRaises(InvalidMetadata) as exc:
            parse_rawspec(spec_s)
        self.assertEqual(exc.exception.attribute, "metadata_version")

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
        self.assertEqual(metadata.python_tag, "cp27")
        self.assertEqual(
            metadata.platform, Platform.from_epd_platform_string("rh5-32")
        )

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
