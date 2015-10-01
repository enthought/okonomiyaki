import unittest

import mock

from ..python_implementation import PythonImplementation
from ...errors import InvalidMetadata


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
        self.assertEqual(py.pep425_tag, "cp27")

        # When
        with mock.patch("sys.pypy_version_info", "pypy 1.9", create=True):
            with mock.patch("sys.version_info", (2, 7, 9, 'final', 0)):
                py = PythonImplementation.from_running_python()

        # Then
        self.assertEqual(py.pep425_tag, "pp27")

        # When
        with mock.patch("sys.platform", "java 1.7", create=True):
            with mock.patch("sys.version_info", (2, 7, 9, 'final', 0)):
                py = PythonImplementation.from_running_python()

        # Then
        self.assertEqual(py.pep425_tag, "jy27")

        # When
        with mock.patch("sys.platform", "cli", create=True):
            with mock.patch("sys.version_info", (2, 7, 9, 'final', 0)):
                py = PythonImplementation.from_running_python()

        # Then
        self.assertEqual(py.pep425_tag, "ip27")

    def test_errors(self):
        # Given
        s = "cp"

        # When/Then
        with self.assertRaises(InvalidMetadata):
            PythonImplementation.from_string(s)

        # Given
        s = "py2"

        # When/Then
        with self.assertRaises(InvalidMetadata):
            PythonImplementation.from_string(s)

        # Given
        s = "py234"

        # When/Then
        with self.assertRaises(InvalidMetadata):
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
        with self.assertRaises(InvalidMetadata):
            PythonImplementation.from_string(tag_string)

        # Given
        tag_string = "py345"

        # When/Then
        with self.assertRaises(InvalidMetadata):
            PythonImplementation.from_string(tag_string)
