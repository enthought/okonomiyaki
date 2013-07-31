import shutil
import tempfile
import unittest
import zipfile

import os.path as op

from okonomiyaki.file_formats.egg import EggBuilder
from okonomiyaki.models.egg import LegacySpec

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
            name = "Qt_debug",
            version = "4.8.5",
            build = 2,
            summary = "Debug symbol files for Qt.",
        )
        spec = LegacySpec.from_data(data, "rh5-32", "2.7")

        with EggBuilder(spec, cwd=self.d) as fp:
            pass

        egg_path = op.join(self.d, "Qt_debug-4.8.5-2.egg")
        self.assertTrue(op.exists(egg_path))

        with zipfile.ZipFile(egg_path, "r") as fp:
            self.assertEqual(fp.namelist(), r_files)
            self.assertMultiLineEqual(fp.read("EGG-INFO/spec/depend"), r_spec_depend)
