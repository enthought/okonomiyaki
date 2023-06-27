import os.path
import shutil
import sys

import zipfile2
from hypothesis import given
from hypothesis.strategies import sampled_from


from okonomiyaki.errors import (
    InvalidMetadata, MissingMetadata, UnsupportedMetadata)
from okonomiyaki.utils import tempdir
from okonomiyaki.utils.test_data import (
    INVALID_RUNTIME_NO_METADATA_VERSION, JULIA_DEFAULT_0_3_11_RH5_X86_64,
    PYTHON_CPYTHON_2_7_10_RH5_X86_64, PYTHON_CPYTHON_2_7_10_RH5_X86_64_INVALID,
    PYTHON_PYPY_2_6_0_RH5_X86_64, R_DEFAULT_3_0_0_RH5_X86_64,
    PYTHON_CPYTHON_3_8_8_RH7_X86_64, PYTHON_CPYTHON_3_8_8_OSX_X86_64,
    PYTHON_CPYTHON_3_8_8_WIN_X86_64, PYTHON_CPYTHON_3_8_8_WIN_X86,
    PYTHON_CPYTHON_3_11_2_RH8_X86_64, PYTHON_CPYTHON_3_11_2_OSX_X86_64,
    PYTHON_CPYTHON_3_11_2_WIN_X86_64
)
from okonomiyaki.versions import MetadataVersion
from okonomiyaki.platforms import Platform, OSKind, FamilyKind, NameKind, X86_64, X86

from ..runtime_metadata import (
    JuliaRuntimeMetadataV1, PythonRuntimeMetadataV1, RuntimeVersion,
    is_runtime_path_valid, runtime_metadata_factory
)

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestPythonMetadataV1(unittest.TestCase):

    def test_pypy(self):
        # Given
        path = PYTHON_PYPY_2_6_0_RH5_X86_64

        # When
        metadata = PythonRuntimeMetadataV1._from_path(path)

        # Then
        self.assertTrue(is_runtime_path_valid(path))
        self.assertEqual(metadata.filename, os.path.basename(path))

        self.assertEqual(
            metadata.metadata_version,
            MetadataVersion.from_string('1.0')
        )
        self.assertEqual(metadata.implementation, 'pypy')
        self.assertEqual(
            metadata.version,
            RuntimeVersion.from_string('2.6.0+1')
        )
        self.assertEqual(
            metadata.language_version,
            RuntimeVersion.from_string('2.7.9')
        )
        self.assertEqual(metadata.build_revision, '')
        self.assertEqual(metadata.executable, '${prefix}/bin/pypy')
        self.assertEqual(metadata.paths, ('${prefix}/bin',))
        self.assertEqual(metadata.post_install, tuple())
        self.assertEqual(metadata.scriptsdir, '${prefix}/bin')
        self.assertEqual(metadata.site_packages, '${prefix}/site-packages')
        self.assertEqual(metadata.python_tag, 'pp27')

    def test_invalid(self):
        # Given
        path = 'python-cpython-2.7.10-1-rh5_64.zip'

        # When/Then
        with self.assertRaises(InvalidMetadata):
            PythonRuntimeMetadataV1._from_path(path)

        # Then
        self.assertFalse(is_runtime_path_valid(path))

        # Given
        path = 'python_cpython_2.7.10-1_rh5_64.runtime'

        # When/Then
        with self.assertRaises(InvalidMetadata):
            PythonRuntimeMetadataV1._from_path(path)

        # Then
        self.assertFalse(is_runtime_path_valid(path))

        # Given
        path = 'python-cpython-2.7.10_rh5_x86_64.runtime'

        # When/Then
        with self.assertRaises(InvalidMetadata):
            PythonRuntimeMetadataV1._from_path(path)

        # Then
        self.assertFalse(is_runtime_path_valid(path))

        # When/Then
        with tempdir() as d:
            path = os.path.join(d, 'foo.zip')
            with zipfile2.ZipFile(path, 'w') as zp:
                pass

            with self.assertRaises(InvalidMetadata):
                PythonRuntimeMetadataV1._from_path(path)

            with zipfile2.ZipFile(path, 'w') as zp:
                with self.assertRaises(InvalidMetadata):
                    PythonRuntimeMetadataV1._from_path(zp)

    @given(
        sampled_from([
            (PYTHON_CPYTHON_2_7_10_RH5_X86_64, '2.7.10+1', '5.8'),
            (PYTHON_CPYTHON_3_8_8_RH7_X86_64, '3.8.8+1', '7.1'),
            (PYTHON_CPYTHON_3_11_2_RH8_X86_64, '3.11.2+2', '8.8')]))
    def test_cpython_gnu(self, options):
        # Given
        path, release, os_release = options
        version = RuntimeVersion.from_string(release.split('+')[0])
        release = RuntimeVersion.from_string(release)
        lib = '${{prefix}}/lib/python{0}.{1}'.format(version.major, version.minor)
        tag = 'cp{0}{1}'.format(version.major, version.minor)

        # When
        metadata = PythonRuntimeMetadataV1._from_path(path)

        # Then
        self.assertTrue(is_runtime_path_valid(path))
        self.assertEqual(metadata.filename, os.path.basename(path))
        self.assertEqual(
            metadata.metadata_version, MetadataVersion.from_string('1.0'))
        self.assertEqual(metadata.implementation, 'cpython')
        self.assertEqual(metadata.version, release)
        self.assertEqual(metadata.language_version, version)
        self.assertEqual(metadata.build_revision, '2.1.0-dev570')
        self.assertEqual(metadata.executable, '${prefix}/bin/python')
        self.assertEqual(metadata.paths, ('${prefix}/bin',))
        self.assertEqual(
            metadata.post_install,
            ('${executable}', f'{lib}/custom_tools/fix-scripts.py'))
        self.assertEqual(metadata.scriptsdir, '${prefix}/bin')
        self.assertEqual(
            metadata.site_packages, f'{lib}/site-packages')
        self.assertEqual(metadata.python_tag, tag)
        self.assertEqual(
            metadata.platform,
            Platform(
                os_kind=OSKind.linux,
                family_kind=FamilyKind.rhel,
                name_kind=NameKind.rhel,
                release=os_release,
                arch=X86_64,
                machine=X86_64))

    @given(
        sampled_from([
            (PYTHON_CPYTHON_3_8_8_OSX_X86_64, '3.8.8+1', '10.14'),
            (PYTHON_CPYTHON_3_11_2_OSX_X86_64, '3.11.2+2', '12.0')]))
    def test_cpython_darwin(self, options):
        # Given
        path, release, os_release = options
        version = RuntimeVersion.from_string(release.split('+')[0])
        release = RuntimeVersion.from_string(release)
        lib = '${{prefix}}/lib/python{0}.{1}'.format(version.major, version.minor)
        tag = 'cp{0}{1}'.format(version.major, version.minor)

        # When
        metadata = PythonRuntimeMetadataV1._from_path(path)

        # Then
        self.assertTrue(is_runtime_path_valid(path))
        self.assertEqual(metadata.filename, os.path.basename(path))
        self.assertEqual(
            metadata.metadata_version, MetadataVersion.from_string('1.0'))
        self.assertEqual(metadata.implementation, 'cpython')
        self.assertEqual(metadata.version, release)
        self.assertEqual(metadata.language_version, version)
        self.assertEqual(metadata.build_revision, '2.1.0-dev570')
        self.assertEqual(metadata.executable, '${prefix}/bin/python')
        self.assertEqual(metadata.paths, ('${prefix}/bin',))
        self.assertEqual(
            metadata.post_install,
            ('${executable}', f'{lib}/custom_tools/fix-scripts.py'))
        self.assertEqual(metadata.scriptsdir, '${prefix}/bin')
        self.assertEqual(
            metadata.site_packages, f'{lib}/site-packages')
        self.assertEqual(metadata.python_tag, tag)
        self.assertEqual(
            metadata.platform,
            Platform(
                os_kind=OSKind.darwin,
                family_kind=FamilyKind.mac_os_x,
                name_kind=NameKind.mac_os_x,
                release=os_release,
                arch=X86_64,
                machine=X86_64))

    @given(
        sampled_from([
            (PYTHON_CPYTHON_3_11_2_WIN_X86_64, '3.11.2+2', '10', X86_64),
            (PYTHON_CPYTHON_3_8_8_WIN_X86_64, '3.8.8+1', '10', X86_64),
            (PYTHON_CPYTHON_3_8_8_WIN_X86, '3.8.8+1', '10', X86)]))
    def test_cpython_windows(self, options):
        # Given
        path, release, os_release, arch = options
        version = RuntimeVersion.from_string(release.split('+')[0])
        release = RuntimeVersion.from_string(release)
        tag = 'cp{0}{1}'.format(version.major, version.minor)

        # When
        metadata = PythonRuntimeMetadataV1._from_path(path)

        # Then
        self.assertTrue(is_runtime_path_valid(path))
        self.assertEqual(metadata.filename, os.path.basename(path))
        self.assertEqual(
            metadata.metadata_version, MetadataVersion.from_string('1.0'))
        self.assertEqual(metadata.implementation, 'cpython')
        self.assertEqual(metadata.version, release)
        self.assertEqual(metadata.language_version, version)
        self.assertEqual(metadata.build_revision, '2.1.0-dev570')
        self.assertEqual(metadata.executable, '${prefix}\\python.exe')
        self.assertEqual(metadata.paths, ('${prefix}', '${prefix}\\Scripts'))
        self.assertEqual(
            metadata.post_install,
            ('${executable}',
             '${prefix}\\Lib\\custom_tools\\fix-scripts.py'))
        self.assertEqual(metadata.scriptsdir, '${prefix}\\Scripts')
        self.assertEqual(
            metadata.site_packages, '${prefix}\\Lib\\site-packages')
        self.assertEqual(metadata.python_tag, tag)
        self.assertEqual(
            metadata.platform,
            Platform(
                os_kind=OSKind.windows,
                family_kind=FamilyKind.windows,
                name_kind=NameKind.windows,
                release=os_release,
                arch=arch,
                machine=arch))


class TestJuliaRuntimeMetadataV1(unittest.TestCase):
    def test_simple(self):
        # Given
        path = JULIA_DEFAULT_0_3_11_RH5_X86_64

        # When
        metadata = JuliaRuntimeMetadataV1._from_path(path)

        # Then
        self.assertEqual(
            metadata.metadata_version,
            MetadataVersion.from_string('1.0')
        )
        self.assertEqual(metadata.filename, os.path.basename(path))
        self.assertEqual(metadata.implementation, 'julia')
        self.assertEqual(
            metadata.version,
            RuntimeVersion.from_string('0.3.11+1')
        )
        self.assertEqual(
            metadata.language_version,
            RuntimeVersion.from_string('0.3.11')
        )
        self.assertEqual(metadata.build_revision, '483dbf5279')
        self.assertEqual(metadata.executable, '${prefix}/bin/julia')
        self.assertEqual(metadata.paths, ('${prefix}/bin',))
        self.assertEqual(metadata.post_install, tuple())


class TestRuntimeMetadataFactory(unittest.TestCase):
    def test_simple(self):
        # Given
        path = PYTHON_CPYTHON_2_7_10_RH5_X86_64

        # When
        metadata = runtime_metadata_factory(path)

        # Then
        self.assertIsInstance(metadata, PythonRuntimeMetadataV1)

        # Given
        path = JULIA_DEFAULT_0_3_11_RH5_X86_64

        # When
        metadata = runtime_metadata_factory(path)

        # Then
        self.assertIsInstance(metadata, JuliaRuntimeMetadataV1)

        # Given
        path = JULIA_DEFAULT_0_3_11_RH5_X86_64

        # When
        with zipfile2.ZipFile(path) as zp:
            metadata = runtime_metadata_factory(zp)

        # Then
        self.assertIsInstance(metadata, JuliaRuntimeMetadataV1)

    def test_invalid(self):
        # Given
        path = R_DEFAULT_3_0_0_RH5_X86_64

        # When/Then
        with self.assertRaisesRegexp(
                UnsupportedMetadata,
                r"^No support for language 'r' \(metadata version '1.0'\)"):
            runtime_metadata_factory(path)

        # Given
        path = PYTHON_CPYTHON_2_7_10_RH5_X86_64_INVALID

        # When/Then
        with tempdir() as d:
            target = os.path.join(
                d, os.path.basename(path).replace('.invalid', '')
            )
            shutil.copy(path, target)

            with self.assertRaises(InvalidMetadata):
                runtime_metadata_factory(target)

        # Given
        path = PYTHON_CPYTHON_2_7_10_RH5_X86_64

        # When/Then
        with tempdir() as d:
            target = os.path.join(d, os.path.basename(path))
            # One needs to add an archive for the zipfile to be valid on 2.6.
            with zipfile2.ZipFile(target, 'w') as zp:
                zp.writestr('dummy', b'dummy data')
            with self.assertRaises(MissingMetadata):
                runtime_metadata_factory(target)

    def test_missing_metadata(self):
        # Given
        path = INVALID_RUNTIME_NO_METADATA_VERSION

        # When/Then
        with self.assertRaisesRegexp(
                MissingMetadata,
                r"^Missing runtime metadata field 'metadata_version'$"):
            runtime_metadata_factory(path)
