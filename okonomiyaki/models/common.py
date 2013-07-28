import json
import re

from okonomiyaki.errors import InvalidEggName

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
