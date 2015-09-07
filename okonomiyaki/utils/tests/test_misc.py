import textwrap
import unittest

from ...errors import OkonomiyakiError
from ..misc import parse_assignments, substitute_variables
from ..py3compat import StringIO


class TestParseAssignments(unittest.TestCase):
    def test_parse_simple(self):
        r_data = {"name": "dummy", "OsDist": None}

        s = textwrap.dedent("""\
        name = "dummy"
        OsDist = None
        """)

        data = parse_assignments(StringIO(s))
        self.assertEqual(data, r_data)

    def test_parse_simple_invalid_file(self):
        with self.assertRaises(OkonomiyakiError):
            parse_assignments(StringIO("1 + 2"))


class TestSubstitute(unittest.TestCase):
    def test_simple(self):
        # Given
        data = {
            "foo": "${yolo}",
            "bar": "${yolo}/bin",
        }

        variables = {
            "yolo": "/foo/bar",
        }

        r_data = {
            "foo": "/foo/bar",
            "bar": "/foo/bar/bin",
        }

        # When
        rendered = substitute_variables(data, variables)

        # Then
        self.assertEqual(rendered, r_data)

    def test_recursive(self):
        # Given
        data = {
            "foo": "${yolo}",
            "bar": "${foo}/bin",
        }

        variables = {
            "yolo": "/foo/bar",
        }
        variables.update(data)

        r_data = {
            "foo": "/foo/bar",
            "bar": "/foo/bar/bin",
        }

        # When
        variables = substitute_variables(variables, variables)
        rendered = substitute_variables(data, variables)

        # Then
        self.assertEqual(rendered, r_data)
