import shutil
import sys
import tempfile
import zipfile

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import os.path as op

from okonomiyaki.errors import InvalidEggName, InvalidMetadata
from okonomiyaki.file_formats.egg import Dependency, EggBuilder, LegacySpec, \
    LegacySpecDepend, info_from_z, parse_rawspec, split_egg_name
from okonomiyaki.utils import ZipFile

import okonomiyaki.repositories

DATA_DIR = op.join(op.dirname(okonomiyaki.repositories.__file__), "tests",
                   "data")

ENSTALLER_EGG = op.join(DATA_DIR, "enstaller-4.5.0-1.egg")


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

        data = dict(
            name="Qt_debug",
            metadata_version="1.1",
            version="4.8.5",
            build=2,
            summary="Debug symbol files for Qt.",
        )
        depend = LegacySpecDepend.from_data(data, "rh5-32", "2.7")
        spec = LegacySpec(depend=depend)

        with EggBuilder(spec, cwd=self.d) as fp:
            pass

        egg_path = op.join(self.d, "Qt_debug-4.8.5-2.egg")
        self.assertTrue(op.exists(egg_path))

        fp = zipfile.ZipFile(egg_path, "r")
        try:
            self.assertEqual(fp.namelist(), r_files)
            self.assertMultiLineEqual(fp.read("EGG-INFO/spec/depend").decode(),
                                      r_spec_depend)
        finally:
            fp.close()


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
        zp = zipfile.ZipFile(egg_path, "r")
        try:
            r_spec_depend = zp.read("EGG-INFO/spec/depend").decode()
        finally:
            zp.close()

        spec_depend = LegacySpecDepend.from_egg(egg_path, "rh5-32")

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

    def test_from_string_no_osdist_no_platform(self):
        # Given
        r_depend = """\
metadata_version = '1.1'
name = 'Qt_debug'
version = '4.8.5'
build = 2

arch = 'x86'
platform = None
osdist = None
python = '2.7'
packages = [
  'Qt 4.8.5',
]
"""
        # When/Then
        with self.assertRaises(InvalidMetadata):
            LegacySpecDepend.from_string(r_depend)

        # When
        depend = LegacySpecDepend.from_string(r_depend, "win-32")

        # Then
        self.assertMultiLineEqual(depend.arch, "x86")
        self.assertMultiLineEqual(depend.platform, "win32")

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
        data = {"name": "Qt_debug", "version": "4.8.5", "build": 2,
                "python": "", "packages": []}

        # When
        depend = LegacySpecDepend.from_data(data, "rh5-32")

        # Then
        self.assertMultiLineEqual(depend.to_string(), r_depend)


class TestLegacySpec(unittest.TestCase):
    def test_depend_content(self):
        r_depend = """\
metadata_version = '1.2'
name = 'Qt_debug'
version = '4.8.5'
build = 2

arch = 'x86'
platform = 'linux2'
osdist = 'RedHat_5'
python = '2.7'
python_tag = 'cp27'
packages = [
  'Qt 4.8.5',
]
"""

        data = dict(
            name="Qt_debug",
            version="4.8.5",
            build=2,
            python="2.7",
            packages=["Qt 4.8.5"],
            summary="Debug symbol files for Qt.",
        )
        depend = LegacySpecDepend.from_data(data, "rh5-32", "2.7")
        spec = LegacySpec(depend=depend)

        self.assertEqual(spec.depend_content(), r_depend)

    def test_windows_platform(self):
        """Test we handle None correctly in windows-specific metadata."""
        data = dict(
            name="Qt_debug",
            version="4.8.5",
            build=2,
            python="2.7",
            summary="Debug symbol files for Qt.",
        )
        depend = LegacySpecDepend.from_data(data, "win-32", "2.7")
        LegacySpec(depend=depend)

    def test_create_from_egg1(self):
        egg = op.join(DATA_DIR, "Cython-0.19.1-1.egg")
        self._test_create_from_egg(egg)

    def test_create_from_egg2(self):
        egg = op.join(DATA_DIR, "ets-4.3.0-3.egg")
        self._test_create_from_egg(egg)

    def _test_create_from_egg(self, egg_path):
        zp = zipfile.ZipFile(egg_path, "r")
        try:
            r_depend = zp.read("EGG-INFO/spec/depend").decode()
            try:
                r_lib_depend = zp.read("EGG-INFO/spec/lib-depend").decode()
            except KeyError:
                r_lib_depend = ""
        finally:
            zp.close()

        legacy = LegacySpec.from_egg(egg_path, "rh5-32")

        self.maxDiff = 4096
        self.assertMultiLineEqual(legacy.depend_content(), r_depend)
        self.assertMultiLineEqual(legacy.lib_depend_content(), r_lib_depend)


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


class TestInfoFromZ(unittest.TestCase):
    def test_with_info_json(self):
        egg = ENSTALLER_EGG

        with ZipFile(egg) as zp:
            info_from_z(zp)
