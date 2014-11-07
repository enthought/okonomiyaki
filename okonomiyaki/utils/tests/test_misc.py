import textwrap

from six.moves import unittest
from six import StringIO

from okonomiyaki.errors import OkonomiyakiError
from ..misc import parse_assignments


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
