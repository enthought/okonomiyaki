import unittest

from hypothesis import given
from hypothesis.strategies import sampled_from

from okonomiyaki.file_formats import EggMetadata
from okonomiyaki.platforms import PlatformABI

from ..test_data import CP38_EGGS, CP27_EGGS


class TestDummyEggs(unittest.TestCase):

    @given(sampled_from(CP38_EGGS))
    def test_cp38_egg_metadata_valid(self, filepath):
        # when
        metadata = EggMetadata.from_egg(filepath)
        filepath = filepath.lower()

        # then
        if 'mkl' in metadata.name:
            self.assertEqual(metadata.python_tag, None)
            self.assertEqual(metadata.abi_tag, None)
        else:
            self.assertEqual(metadata.python_tag, 'cp38')
            self.assertEqual(metadata.abi_tag, 'cp38')
        if 'osx_x86_64' in filepath:
            self.assertEqual(metadata.platform_tag, 'macosx_10_14_x86_64')
            self.assertEqual(metadata.platform_abi, PlatformABI(u'darwin'))
        elif 'win_x86_64' in filepath:
            self.assertEqual(metadata.platform_tag, 'win_amd64')
            self.assertEqual(metadata.platform_abi, PlatformABI(u'msvc2019'))
        else:
            self.assertEqual(metadata.platform_tag, 'linux_x86_64')
            self.assertEqual(metadata.platform_abi, PlatformABI(u'gnu'))

    @given(sampled_from(CP27_EGGS))
    def test_cp27_egg_metadata_valid(self, filepath):
        # when
        metadata = EggMetadata.from_egg(filepath)
        filepath = filepath.lower()

        # then
        if 'mkl' in metadata.name:
            self.assertEqual(metadata.python_tag, None)
            self.assertEqual(metadata.abi_tag, None)
        else:
            self.assertIn(metadata.python_tag, 'cp27')
            self.assertIn(metadata.abi_tag, 'cp27m')
        if 'osx_x86_64' in filepath:
            self.assertEqual(metadata.platform_tag, 'macosx_10_6_x86_64')
            self.assertEqual(metadata.platform_abi, PlatformABI(u'darwin'))
        elif 'win_x86_64' in filepath:
            self.assertEqual(metadata.platform_tag, 'win_amd64')
            self.assertEqual(metadata.platform_abi, PlatformABI(u'msvc2008'))
        else:
            self.assertEqual(metadata.platform_tag, 'linux_x86_64')
            self.assertEqual(metadata.platform_abi, PlatformABI(u'gnu'))
