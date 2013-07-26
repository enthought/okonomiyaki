import unittest

import os.path as op

from okonomiyaki.errors import InvalidEggName
from okonomiyaki.models.egg import Dependency, LegacySpec

DATA_DIR = op.join(op.dirname(__file__), "data")

class TestDependency(unittest.TestCase):
    def test_str(self):
        dependency = Dependency(name="numpy")
        r_str = "numpy"

        self.assertEqual(r_str, str(dependency))

        dependency = Dependency(name="numpy", version_string="1.7.1")
        r_str = "numpy 1.7.1"

        self.assertEqual(r_str, str(dependency))

        dependency = Dependency(name="numpy", version_string="1.7.1", build_number=1)
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

        self.assertRaises(InvalidEggName, lambda : Dependency.from_string("numpy"))
        self.assertRaises(InvalidEggName, lambda : Dependency.from_string("numpy 1.7.1"))

class TestLegacySpec(unittest.TestCase):
    def test_depend_content(self):
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

        dependencies = [Dependency.from_string("Qt-4.8.5-2")]
        data = dict(
            name="Qt_debug",
            version="4.8.5",
            build=2,
            python="2.7",
            packages=dependencies,
            summary="Debug symbol files for Qt.",
        )
        spec = LegacySpec.from_data(data, "rh5-32", "2.7")

        self.assertEqual(spec.depend_content(), r_depend)
