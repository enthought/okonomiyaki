import _ast
import ast

from ..errors import OkonomiyakiError

_TRANSLATOR = {
    _ast.List: lambda v: v.elts,
    _ast.Num: lambda v: v.n,
    _ast.Str: lambda v: v.s
}


def parse_assignments(s):
    """
    Parse a string of valid python code that consists only in a set of
    simple assignments.

    Parameters
    ----------
    s: str
        A string containing assignments only

    Example
    -------
    >>> _parse_assignments("foo = '1'\nbar = 2")
    {'foo': '1', 'bar': 2}
    """
    res = {}
    ast_result = ast.parse(s)

    for element in ast_result.body:
        if not isinstance(element, _ast.Assign):
            raise OkonomiyakiError("Invalid expression in string.")
        assignment = element
        if not len(assignment.targets) == 1:
            raise OkonomiyakiError("Invalid expression in string.")
        name = assignment.targets[0].id
        res[name] = _translator(assignment.value)
    return res


def _translator(v):
    if isinstance(v, _ast.Num) or isinstance(v, _ast.Str):
        return _TRANSLATOR[v.__class__](v)
    elif isinstance(v, _ast.List):
        return [_translator(i) for i in _TRANSLATOR[_ast.List](v)]
    elif isinstance(v, _ast.Name):
        if v.id != 'None':
            raise NotImplementedError("value of type _ast.Name which value "
                                      "!= 'None' not supported (was {0})".
                                      format(v.id))
        else:
            return None
    else:
        raise NotImplementedError("Type {0} not handled yet".format(v))
