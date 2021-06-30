import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from hypothesis import given
from hypothesis.strategies import sampled_from

from okonomiyaki.errors import OkonomiyakiError
from ..abi import default_abi


EXAMPLE_RUNTIMES = {
    ("osx_x86_64", "cpython", "2.7.10+1"): u"darwin",
    ("rh5_x86_64", "cpython", "2.7.10+1"): u"gnu",
    ("win_x86", "cpython", "2.7.10+1"): u"msvc2008",
    ("win_x86", "cpython", "3.4.3+1"): u"msvc2010",
    ("win_x86", "cpython", "3.5.0+1"): u"msvc2015",
    ("win_x86", "cpython", "3.6.0+1"): u"msvc2015",
    ("win_x86", "cpython", "3.8.8+1"): u"msvc2019",
    ("osx_x86_64", "pypy", "2.6.1+1"): u"darwin",
    ("rh5_x86_64", "pypy", "2.6.1+1"): u"gnu",
    ("win_x86", "pypy", "2.6.1+1"): u"msvc2008",
    ("osx_x86_64", "julia", "0.3.11+1"): u"darwin",
    ("rh5_x86_64", "julia", "0.3.11+1"): u"gnu",
    ("win_x86", "julia", "0.3.11+1"): u"mingw"}


class TestDefaultABI(unittest.TestCase):

    @given(sampled_from(sorted(EXAMPLE_RUNTIMES)))
    def test_basics(self, arguments):
        # when
        abi = default_abi(*arguments)

        # then
        self.assertEqual(abi, EXAMPLE_RUNTIMES[arguments])

    @given(
        sampled_from([
            ("win_x86", "cpython", "3.9.0+1"),
            ("win_x86", "pypy", "4.1.0+1"),
            ("rh5_x86_64", "r", "3.0.0+1")]))
    def test_non_supported(self, arguments):
        with self.assertRaises(OkonomiyakiError):
            default_abi(*arguments)
