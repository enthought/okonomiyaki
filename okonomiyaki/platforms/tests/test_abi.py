import sys

from ...errors import OkonomiyakiError
from ..abi import default_abi

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestDefaultABI(unittest.TestCase):
    def test_basics(self):
        # Given
        args = (
            (("osx_x86_64", "cpython", "2.7.10+1"), u"darwin"),
            (("rh5_x86_64", "cpython", "2.7.10+1"), u"gnu"),
            (("win_x86", "cpython", "2.7.10+1"), u"msvc2008"),
            (("win_x86", "cpython", "3.4.3+1"), u"msvc2010"),
            (("win_x86", "cpython", "3.5.0+1"), u"msvc2015"),
            (("win_x86", "cpython", "3.6.0+1"), u"msvc2015"),
            (("osx_x86_64", "pypy", "2.6.1+1"), u"darwin"),
            (("rh5_x86_64", "pypy", "2.6.1+1"), u"gnu"),
            (("win_x86", "pypy", "2.6.1+1"), u"msvc2008"),
            (("osx_x86_64", "julia", "0.3.11+1"), u"darwin"),
            (("rh5_x86_64", "julia", "0.3.11+1"), u"gnu"),
            (("win_x86", "julia", "0.3.11+1"), u"mingw"),
        )

        # When/Then
        for arg, r_abi in args:
            abi = default_abi(*arg)
            self.assertEqual(abi, r_abi)

    def test_non_supported(self):
        # Given
        args = (
            ("win_x86", "cpython", "3.7.0+1"),
            ("win_x86", "pypy", "4.1.0+1"),
            ("rh5_x86_64", "r", "3.0.0+1"),
        )

        # When/Then
        for arg in args:
            with self.assertRaises(OkonomiyakiError):
                default_abi(*arg)
