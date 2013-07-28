import unittest

from okonomiyaki.errors import InvalidEggName
from okonomiyaki.models.common import egg_name, is_egg_name_valid, split_egg_name

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
