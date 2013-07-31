import ast, _ast
import json
import re

from okonomiyaki.errors import InvalidEggName
from .constants import _SPEC_DEPEND_LOCATION, _INFO_JSON_LOCATION

_EGG_NAME_RE = re.compile("(?P<name>[\w]+)-(?P<version>[^-]+)-(?P<build>\d+)\.egg$")

def egg_name(name, version, build):
    """
    Return the egg filename (including the .egg extension) for the given
    arguments
    """
    return "{0}-{1}-{2}.egg".format(name, version, build)

def is_egg_name_valid(s):
    """
    Return True if the given string is a valid egg name (not including the
    .egg, e.g. 'Qt-4.8.5-2')
    """
    return _EGG_NAME_RE.match(s)

def split_egg_name(s):
    m = _EGG_NAME_RE.match(s)
    if m is None:
        raise InvalidEggName(s)
    else:
        name, version, build = m.groups()
        return name, version, int(build)

def _decode_none_values(data, none_keys):
    for k in none_keys:
        if k in data and data[k] is None:
            data[k] = ""
    return data

def _encode_none_values(data, none_keys):
    # XXX: hack to deal with the lack of Either in traitlets -> ''
    # translated to null in json for those keys
    for k in none_keys:
        if k in data and data[k] == "":
            data[k] = None
    return data

# info_from_z and parse_rawspec are copied from egginst.eggmeta. Unlikely to
# change soon hopefully.
def info_from_z(z):
    res = {"type": "egg"}

    arcname = _SPEC_DEPEND_LOCATION
    if arcname in z.namelist():
        res.update(parse_rawspec(z.read(arcname).decode()))

    arcname = _INFO_JSON_LOCATION
    if arcname in z.namelist():
        res.update(json.loads(z.read(arcname)))

    res['name'] = res['name'].lower().replace('-', '_')
    return res

def parse_rawspec(spec_string):
    spec = _parse_assignments(spec_string.replace('\r', ''))
    res = {}
    for k in ('name', 'version', 'build',
              'arch', 'platform', 'osdist', 'python', 'packages'):
        res[k] = spec[k]
    return res

def _parse_assignments(s):
    """Parse a string of valid python code that consists only in a set of
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
            raise ValueError()
        assignment = element
        if not len(assignment.targets) == 1:
            raise ValueError()
        name = assignment.targets[0].id
        res[name] = _translator(assignment.value)
    return res

_TRANSLATOR = {
        _ast.List: lambda v: v.elts,
        _ast.Num: lambda v: v.n,
        _ast.Str: lambda v: v.s
}

def _translator(v):
    if isinstance(v, _ast.Num) or isinstance(v, _ast.Str):
        return _TRANSLATOR[v.__class__](v)
    elif isinstance(v, _ast.List):
        return [_translator(i) for i in _TRANSLATOR[_ast.List](v)]
    elif isinstance(v, _ast.Name):
        if v.id != 'None':
            raise NotImplementedError("value of type _ast.Name which value != 'None' not supported (was {0})".format(v.id))
        else:
            return None
    else:
        raise NotImplementedError("Type {0} not handled yet".format(v))
