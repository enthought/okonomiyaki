import unittest

from okonomiyaki.errors import InvalidEggName
from okonomiyaki.models.common import egg_name, is_egg_name_valid, split_egg_name, parse_rawspec

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
        self.assertRaises(InvalidEggName, lambda: split_egg_name("numpy-1.7.1-1"))
        self.assertRaises(InvalidEggName, lambda: split_egg_name("numpy-1.6.1"))

class TestParseRawspec(unittest.TestCase):
    def test_simple(self):
        r_spec = {'arch': 'x86',
                  'build': 1,
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
