import sys

import mock
import six

from okonomiyaki.errors import InvalidMetadataField
from ..python_implementation import PythonABI, PythonImplementation

from hypothesis import given
from hypothesis.strategies import sampled_from


if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestPythonImplementation(unittest.TestCase):

    @given(sampled_from((
        ('2', '7', 'cp27'), ('3', '8', 'cp38'),
        ('4', '15', 'cp415'), ('3', '11', 'cp311'))))
    def test_creation(self, version):
        # Given
        kind = 'cpython'
        major, minor, r_tag = version

        # When
        tag = PythonImplementation(kind, major, minor)

        # Then
        self.assertEqual(tag.abbreviated_implementation, 'cp')
        self.assertEqual(str(tag), r_tag)
        self.assertIsInstance(six.text_type(tag), six.text_type)

    def test_from_running_python(self):
        # When
        with mock.patch(
                "okonomiyaki.platforms.python_implementation."
                "_abbreviated_implementation",
                return_value="cp"):
            with mock.patch("sys.version_info", (2, 7, 9, 'final', 0)):
                py = PythonImplementation.from_running_python()

        # Then
        self.assertEqual(py.pep425_tag, u"cp27")

        # When
        with mock.patch("sys.pypy_version_info", "pypy 1.9", create=True):
            with mock.patch("sys.version_info", (2, 7, 9, 'final', 0)):
                py = PythonImplementation.from_running_python()

        # Then
        self.assertEqual(py.pep425_tag, u"pp27")

        # When
        with mock.patch("sys.platform", "java 1.7", create=True):
            with mock.patch("sys.version_info", (2, 7, 9, 'final', 0)):
                py = PythonImplementation.from_running_python()

        # Then
        self.assertEqual(py.pep425_tag, u"jy27")

        # When
        with mock.patch("sys.platform", "cli", create=True):
            with mock.patch("sys.version_info", (2, 7, 9, 'final', 0)):
                py = PythonImplementation.from_running_python()

        # Then
        self.assertEqual(py.pep425_tag, u"ip27")

    @given(sampled_from((
        ("cpython", "cp"), ("python", "py"),
        ("pypy", "pp"), ("dummy", "dummy"))))
    def test_abbreviations(self, kinds):
        # Given
        major = 2
        minor = 7
        kind, r_abbreviated = kinds

        # When
        tag = PythonImplementation(kind, major, minor)

        # Then
        self.assertEqual(tag.abbreviated_implementation, r_abbreviated)

    @given(sampled_from((
        (2, 7, 'cp27'), (3, 8, 'cp38'),
        (3, 4, 'cpython34'), (4, 5, 'cp4_5'),
        (24, 7, 'cp24_7'),
        (4, 15, 'cp415'), (3, 11, 'cp311'))))
    def test_from_string(self, data):
        # Given
        major, minor, tag_string = data

        # When
        tag = PythonImplementation.from_string(tag_string)

        # Then
        self.assertEqual(tag.kind, "cpython")
        self.assertEqual(tag.major, major)
        if minor is not None:
            self.assertEqual(tag.minor, minor)

    @given(sampled_from(('cp2', 'py3', 'cp', 'pp4567')))
    def test_from_string_errors(self, data):
        # When/Then
        message = r"^Invalid value for metadata field 'python_tag': '{}'$"
        with self.assertRaisesRegexp(
                InvalidMetadataField, message.format(data)):
            PythonImplementation.from_string(data)


class TestPythonABI(unittest.TestCase):

    def test_pep425_tag_string_none(self):
        # Given
        abi_tag = None

        # When
        abi_tag_string = PythonABI.pep425_tag_string(abi_tag)

        # Then
        self.assertEqual(abi_tag_string, u"none")
        self.assertIsInstance(abi_tag_string, six.text_type)

    def test_pep425_tag_string(self):
        # Given
        abi_tag = PythonABI(u"cp27mu")

        # When
        abi_tag_string = PythonABI.pep425_tag_string(abi_tag)

        # Then
        self.assertEqual(abi_tag_string, u"cp27mu")
        self.assertIsInstance(abi_tag_string, six.text_type)
