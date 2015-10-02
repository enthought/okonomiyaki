import os
import os.path as op
import sys
import textwrap
import zipfile2

import mock

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from ...errors import InvalidEggName, InvalidMetadata, UnsupportedMetadata
from ...platforms import EPDPlatform
from ...platforms.legacy import LegacyEPDPlatform
from ...versions import EnpkgVersion, MetadataVersion

from .._egg_info import (
    Requirement, EggMetadata, LegacySpecDepend, parse_rawspec,
    split_egg_name
)

from .common import (
    BROKEN_MCCABE_EGG, DATA_DIR, ENSTALLER_EGG, ETS_EGG,
    FAKE_MEDIALOG_BOARDFILE_1_6_1_EGG, FAKE_MEDIALOG_BOARDFILE_1_6_1_PKG_INFO,
    MKL_EGG, NUMEXPR_2_2_2_EGG, PYMULTINEST_EGG, _OSX64APP_EGG,
    PYSIDE_1_0_3_EGG, XZ_5_2_0_EGG
)


M = MetadataVersion.from_string


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
        self.assertEqual(depend._metadata_version, M("1.3"))
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

    def test_blacklisted_platform(self):
        # Given
        egg = XZ_5_2_0_EGG
        sha256sum = ("ca5f2c417dd9f6354db3c2999edb441382ed11c7a034"
                     "ade1839d1871a78ab2e8")

        # When
        with mock.patch(
            "okonomiyaki.file_formats._egg_info.compute_sha256",
            return_value=sha256sum
        ):
            spec_depend = LegacySpecDepend.from_egg(egg)

        # Then
        self.assertEqual(str(spec_depend._epd_legacy_platform), "win-32")

        # When
        with mock.patch(
            "okonomiyaki.file_formats._egg_info.compute_sha256",
            return_value=sha256sum
        ):
            with zipfile2.ZipFile(egg) as zp:
                spec_depend = LegacySpecDepend.from_egg(zp)

        # Then
        self.assertEqual(str(spec_depend._epd_legacy_platform), "win-32")


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
        spec_depend._metadata_version = M("1.3")
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
        with self.assertRaises(UnsupportedMetadata):
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
        with self.assertRaises(InvalidMetadata):
            parse_rawspec(spec_s)

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
        with self.assertRaises(InvalidMetadata):
            parse_rawspec(spec_s)


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
        self.assertEqual(
            metadata.metadata_version,
            MetadataVersion.from_string("1.1")
        )
        self.assertEqual(metadata.metadata_version, M("1.1"))
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

        self.assertEqual(metadata.metadata_version, M("1.1"))
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
        self.assertEqual(metadata.metadata_version, M("1.1"))

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
        self.assertEqual(metadata.metadata_version, M("1.1"))
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

    def test_no_pkg_info(self):
        # Given
        egg = _OSX64APP_EGG

        # When
        metadata = EggMetadata.from_egg(egg)

        # Then
        self.assertEqual(metadata.name, "_osx64app")
        self.assertIsNone(metadata.pkg_info)

        # When
        with zipfile2.ZipFile(egg) as fp:
            metadata = EggMetadata.from_egg(fp)

        # Then
        self.assertEqual(metadata.name, "_osx64app")
        self.assertIsNone(metadata.pkg_info)

    def test_blacklisted_python_tag(self):
        # Given
        egg = PYSIDE_1_0_3_EGG
        sha256sum = ("5af973a78c53bfa4fe843992bc86207d5c945b06f7df576e64"
                     "463a743a558fb1")
        # When
        with mock.patch(
            "okonomiyaki.file_formats._egg_info.compute_sha256",
            return_value=sha256sum
        ):
            metadata = EggMetadata.from_egg(egg)

        # Then
        self.assertEqual(metadata.python_tag, "py27")

        # When
        with mock.patch(
            "okonomiyaki.file_formats._egg_info.compute_sha256",
            return_value=sha256sum
        ):
            with zipfile2.ZipFile(egg) as zp:
                metadata = EggMetadata.from_egg(zp)

        # Then
        self.assertEqual(metadata.python_tag, "py27")

    def test_blacklisted_platform(self):
        # Given
        egg = XZ_5_2_0_EGG
        sha256sum = ("ca5f2c417dd9f6354db3c2999edb441382ed11c7a034"
                     "ade1839d1871a78ab2e8")

        # When
        with mock.patch(
            "okonomiyaki.file_formats._egg_info.compute_sha256",
            return_value=sha256sum
        ):
            metadata = EggMetadata.from_egg(egg)

        # Then
        self.assertEqual(metadata.platform_tag, "win32")

        # When
        with mock.patch(
            "okonomiyaki.file_formats._egg_info.compute_sha256",
            return_value=sha256sum
        ):
            with zipfile2.ZipFile(egg) as zp:
                metadata = EggMetadata.from_egg(zp)

        # Then
        self.assertEqual(metadata.platform_tag, "win32")

        # Given
        egg = BROKEN_MCCABE_EGG

        # When
        with mock.patch(
            "okonomiyaki.file_formats._egg_info.compute_sha256",
        ) as mocked_compute_sha256:
            metadata = EggMetadata.from_egg(egg)

        # Then
        self.assertFalse(mocked_compute_sha256.called)

    def test_blacklisted_pkg_info(self):
        # Given
        egg = FAKE_MEDIALOG_BOARDFILE_1_6_1_EGG
        mock_sha256 = ("ab9e029caf273e4a251d3686425cd4225e1b97682749acc7a82d"
                       "c1fd15dbd060")

        # When
        with mock.patch(
            "okonomiyaki.file_formats._egg_info.compute_sha256",
            return_value=mock_sha256
        ):
            metadata = EggMetadata.from_egg(egg)

        # Then
        self.maxDiff = None
        pkg_info = metadata.pkg_info
        self.assertEqual(pkg_info.metadata_version, "1.0")
        self.assertEqual(pkg_info.name, "medialog.boardfile")
        self.assertMultiLineEqual(
            pkg_info.description, FAKE_MEDIALOG_BOARDFILE_1_6_1_PKG_INFO
        )

        # When
        with mock.patch(
            "okonomiyaki.file_formats._egg_info.compute_sha256",
            return_value=mock_sha256
        ):
            with zipfile2.ZipFile(egg) as zp:
                metadata = EggMetadata.from_egg(zp)

        # Then
        pkg_info = metadata.pkg_info
        self.assertEqual(pkg_info.metadata_version, "1.0")
        self.assertEqual(pkg_info.name, "medialog.boardfile")
        self.assertMultiLineEqual(
            pkg_info.description, FAKE_MEDIALOG_BOARDFILE_1_6_1_PKG_INFO
        )

        # Given
        # An egg not in the blacklist
        egg = BROKEN_MCCABE_EGG

        # When
        with mock.patch(
            "okonomiyaki.file_formats._egg_info.compute_sha256",
        ) as mocked_compute_sha256:
            EggMetadata.from_egg(egg)

        # Then
        self.assertFalse(mocked_compute_sha256.called)

    def test_fixed_requirement(self):
        # Given
        egg = NUMEXPR_2_2_2_EGG

        # When
        metadata = EggMetadata.from_egg(egg)

        # Then
        self.assertEqual(
            tuple(str(r) for r in metadata.runtime_dependencies),
            ("MKL 10.3", "numpy 1.8.0")
        )

    def test_strictness(self):
        # Given
        egg = PYMULTINEST_EGG

        # When/Then
        with self.assertRaises(UnicodeDecodeError):
            EggMetadata.from_egg(egg)

        # When
        metadata = EggMetadata.from_egg(egg, strict=False)

        # Then
        self.assertEqual(
            metadata.pkg_info.author_email,
            u"johannes.buchner.acad [\ufffdt] gmx.com",
        )
