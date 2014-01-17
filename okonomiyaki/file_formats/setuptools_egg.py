import re

from okonomiyaki.errors import OkonomiyakiError

_R_EGG_NAME = re.compile("""
        (?P<name>[^.-]+)
        (-(?P<version>[^-]+))?
        (-py(?P<pyver>(\d+\.\d+)))?
        \.egg
""", re.VERBOSE)

def parse_filename(path):
    m = _R_EGG_NAME.search(path)
    if m:
        return m.group("name"), m.group("version"), m.group("pyver"), None
    else:
        raise OkonomiyakiError("Invalid egg name: {0}".format(path))

