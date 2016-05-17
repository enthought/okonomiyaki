import sys

import mock
import six

from ..python_implementation import PythonABI, PythonImplementation
from ...errors import InvalidMetadataField

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestPythonImplementation(unittest.TestCase):
    def test_from_running_python(self):
        # When
        with mock.patch(
            "okonomiyaki.platforms.python_implementation."
            "_abbreviated_implementation",
            return_value="cp"
        ):
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

    def test_errors(self):
        # Given
        s = u"cp"

        # When/Then
        with self.assertRaisesRegexp(
            InvalidMetadataField,
            r"^Invalid value for metadata field 'python_tag': u?'cp'"
        ):
            PythonImplementation.from_string(s)

        # Given
        s = u"py2"

        # When/Then
        with self.assertRaisesRegexp(
            InvalidMetadataField,
            r"^Invalid value for metadata field 'python_tag': u?'py2'$"
        ):
            PythonImplementation.from_string(s)

        # Given
        s = u"py234"

        # When/Then
        with self.assertRaisesRegexp(
            InvalidMetadataField,
            r"^Invalid value for metadata field 'python_tag': u?'py234'$"
        ):
            PythonImplementation.from_string(s)

    def test_simple(self):
        # Given
        kind = "cpython"
        major = 2
        minor = 7

        # When
        tag = PythonImplementation(kind, major, minor)

        # Then
        self.assertEqual(tag.abbreviated_implementation, "cp")
        self.assertEqual(str(tag), "cp27")
        self.assertIsInstance(six.text_type(tag), six.text_type)

    def test_abbreviations(self):
        # Given
        kinds = (("cpython", "cp"), ("python", "py"), ("pypy", "pp"),
                 ("dummy", "dummy"))
        major = 2
        minor = 7

        # When/Then
        for kind, r_abbreviated in kinds:
            tag = PythonImplementation(kind, major, minor)
            self.assertEqual(tag.abbreviated_implementation, r_abbreviated)

    def test_from_string(self):
        # Given
        tag_string = "cp27"

        # When
        tag = PythonImplementation.from_string(tag_string)

        # Then
        self.assertEqual(tag.kind, "cpython")
        self.assertEqual(tag.major, 2)
        self.assertEqual(tag.minor, 7)

        # Given
        tag_string = "python34"

        # When
        tag = PythonImplementation.from_string(tag_string)

        # Then
        self.assertEqual(tag.kind, "python")
        self.assertEqual(tag.major, 3)
        self.assertEqual(tag.minor, 4)

        # Given
        tag_string = "py3"

        # When/Then
        with self.assertRaisesRegexp(
            InvalidMetadataField,
            r"^Invalid value for metadata field 'python_tag': 'py3'$"
        ):
            PythonImplementation.from_string(tag_string)

        # Given
        tag_string = "py345"

        # When/Then
        with self.assertRaisesRegexp(
            InvalidMetadataField,
            r"^Invalid value for metadata field 'python_tag': 'py345'$"
        ):
            PythonImplementation.from_string(tag_string)


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
