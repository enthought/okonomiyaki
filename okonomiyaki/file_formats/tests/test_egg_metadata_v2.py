import shutil
import tempfile
import unittest

from okonomiyaki.platforms import (
    EPDPlatform, PlatformABI, PythonABI, PythonImplementation
)
from okonomiyaki.utils.test_data import (
    MKL_10_3_RH5_X86_64, NOSE_1_3_4_RH5_X86_64, NUMPY_1_9_2_WIN_X86_64
)
from okonomiyaki.versions import EnpkgVersion, MetadataVersion
from ..egg_metadata_v2 import EggMetadataV2
from .common import ENSTALLER_EGG


M = MetadataVersion.from_string
P = EPDPlatform.from_string
V = EnpkgVersion.from_string
CP27 = PythonImplementation.from_string(u"cp27")
CP27M = PythonABI(u"cp27m")
GNU = PlatformABI(u"gnu")


class TestEggMetadata(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_v1_egg_parsing_pure_python_no_platform(self):
        # Given
        egg = ENSTALLER_EGG

        # When
        metadata = EggMetadataV2.from_egg(egg)

        # Then
        self.assertEqual(metadata.metadata_version, M(u"1.1"))
        self.assertEqual(metadata.name, "enstaller")
        self.assertEqual(metadata.version, V("4.5.0-1"))
        self.assertIsNone(metadata.epd_platform)
        self.assertIsNone(metadata.python_implementation)
        self.assertIsNone(metadata.python_abi)
        self.assertIsNone(metadata.platform_abi)
        self.assertIsNotNone(metadata.package_info)
        self.assertEqual(metadata.summary, u"")
        self.assertEqual(metadata.license, u"BSD")
        self.assertEqual(metadata.runtime_dependencies, ())
        self.assertEqual(metadata.build_dependencies, ())
        self.assertEqual(metadata.test_dependencies, ())
        self.assertEqual(metadata.provides, ())
        self.assertEqual(metadata.conflicts, ())

    def test_v1_egg_parsing_pure_python_with_platform(self):
        # Given
        egg = NOSE_1_3_4_RH5_X86_64

        # When
        metadata = EggMetadataV2.from_egg(egg)

        # Then
        self.assertEqual(metadata.metadata_version, M(u"1.3"))
        self.assertEqual(metadata.name, u"nose")
        self.assertEqual(metadata.version, V("1.3.4-1"))
        self.assertEqual(metadata.epd_platform, P(u"rh5-x86_64"))
        self.assertEqual(metadata.python_implementation, CP27)
        self.assertEqual(metadata.python_abi, CP27M)
        self.assertEqual(metadata.platform_abi, GNU)
        self.assertIsNotNone(metadata.package_info)
        self.assertEqual(
            metadata.summary,
            u"Extends the Python Unittest module with additional disocvery and "
            "running\noptions\n"
        )
        self.assertEqual(metadata.license, u"GNU LGPL")
        self.assertEqual(metadata.runtime_dependencies, ())
        self.assertEqual(metadata.build_dependencies, ())
        self.assertEqual(metadata.test_dependencies, ())
        self.assertEqual(metadata.provides, ())
        self.assertEqual(metadata.conflicts, ())

    def test_v1_egg_parsing_no_python_platform(self):
        # Given
        egg = MKL_10_3_RH5_X86_64

        # When
        metadata = EggMetadataV2.from_egg(egg)

        # Then
        self.assertEqual(metadata._raw_name, "MKL")
        self.assertEqual(metadata.name, "mkl")

        self.assertEqual(metadata.metadata_version, M(u"1.3"))
        self.assertIsNone(metadata.python_abi_tag)
        self.assertEqual(metadata.python_abi_tag_string, u'none')
        self.assertEqual(metadata.platform_tag, 'linux_x86_64')
        self.assertEqual(metadata.platform_tag_string, 'linux_x86_64')
        self.assertEqual(metadata.platform_abi, GNU)
        self.assertEqual(metadata.platform_abi_tag, u'gnu')
        self.assertEqual(metadata.platform_abi_tag_string, u'gnu')
        self.assertIsNone(metadata.python_tag)
        self.assertEqual(metadata.python_tag_string, 'none')

        self.assertEqual(metadata.runtime_dependencies, ())
        self.assertEqual(metadata.build_dependencies, ())
        self.assertEqual(metadata.test_dependencies, ())
        self.assertEqual(metadata.provides, ())
        self.assertEqual(metadata.conflicts, ())

    def test_v1_egg_parsing_python_platform(self):
        # Given
        egg = NUMPY_1_9_2_WIN_X86_64

        # When
        metadata = EggMetadataV2.from_egg(egg)

        # Then
        self.assertEqual(metadata._raw_name, "numpy")
        self.assertEqual(metadata.name, "numpy")

        self.assertEqual(metadata.metadata_version, M(u"1.3"))
        self.assertEqual(metadata.python_implementation, CP27)
        self.assertEqual(metadata.python_tag, u"cp27")
        self.assertEqual(metadata.python_tag_string, u'cp27')
        self.assertEqual(metadata.python_abi, CP27M)
        self.assertEqual(metadata.python_abi_tag, u"cp27m")
        self.assertEqual(metadata.python_abi_tag_string, u'cp27m')
        self.assertEqual(metadata.platform_tag, 'linux_x86_64')
        self.assertEqual(metadata.platform_tag_string, 'linux_x86_64')
        self.assertEqual(metadata.platform_abi, GNU)
        self.assertEqual(metadata.platform_abi_tag, u'gnu')
        self.assertEqual(metadata.platform_abi_tag_string, u'gnu')

        self.assertEqual(
            metadata.runtime_dependencies, ((u"MKL", ((u"== 10.3-1", ),)),)
        )
        self.assertEqual(metadata.build_dependencies, ())
        self.assertEqual(metadata.test_dependencies, ())
        self.assertEqual(metadata.provides, ())
        self.assertEqual(metadata.conflicts, ())
