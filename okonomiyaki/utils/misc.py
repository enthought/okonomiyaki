import ast
import contextlib
import shutil
import string
import tempfile

from .py3compat import string_types

from ..errors import OkonomiyakiError


class _AssignmentParser(ast.NodeVisitor):
    def __init__(self):
        self._data = {}

    def parse(self, s):
        self._data.clear()

        root = ast.parse(s)
        self.visit(root)
        return self._data

    def generic_visit(self, node):
        if type(node) != ast.Module:
            raise OkonomiyakiError("Unexpected expression @ line {0}".
                                   format(node.lineno))
        super(_AssignmentParser, self).generic_visit(node)

    def visit_Assign(self, node):
        try:
            value = ast.literal_eval(node.value)
        except ValueError:
            msg = ("Invalid configuration syntax at line {0}".
                   format(node.lineno))
            raise OkonomiyakiError(msg)
        else:
            for target in node.targets:
                self._data[target.id] = value


def parse_assignments(file_or_filename):
    """
    Parse files which contain only python assignements, and returns the
    corresponding dictionary name: value

    Parameters
    ----------
    file_or_filename: str, file object
        If a string, interpreted as a filename. File object otherwise.
    """
    if isinstance(file_or_filename, string_types):
        with open(file_or_filename) as fp:
            return _AssignmentParser().parse(fp.read())
    else:
        return _AssignmentParser().parse(file_or_filename.read())


@contextlib.contextmanager
def tempdir():
    d = tempfile.mkdtemp()
    try:
        yield d
    finally:
        shutil.rmtree(d)


def substitute_variables(d, local_vars):
    """Perform shell/Perl-style variable substitution.

    Every occurrence of '${name}' name is considered a variable, and variable
    is substituted by the value found in the `local_vars' dictionary.  Raise
    ValueError for any variables not found in `local_vars'.

    '$' may be escaped by using '$$'

    Parameters
    ----------
    d: dict
        (str: str) mapping, where each value will be substituted.
    local_vars: dict
        dict of variables
    """
    def _resolve(d):
        ret = {}
        for k, v in d.items():
            ret[k] = substitute_variable(v, local_vars)
        return ret

    ret = _resolve(d)
    while not ret == d:
        d = ret
        ret = _resolve(d)
    return ret


def substitute_variable(v, local_vars):
    return string.Template(v).substitute(local_vars)
