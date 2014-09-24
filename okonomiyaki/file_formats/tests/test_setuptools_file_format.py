import sys

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from okonomiyaki.errors import OkonomiyakiError
from okonomiyaki.file_formats.setuptools_egg import parse_filename


class TestEggBuilder(unittest.TestCase):
    def test_simple(self):
        # Given
        path = "nose-1.2.1-py2.6.egg"

        # When
        name, version, pyver, _ = parse_filename(path)

        # Then
        self.assertEqual(name, "nose")
        self.assertEqual(version, "1.2.1")
        self.assertEqual(pyver, "2.6")

    def test_enthought_egg(self):
        # Given
        path = "nose-1.2.1-1.egg"

        # When/Then
        with self.assertRaises(OkonomiyakiError):
            parse_filename(path)
