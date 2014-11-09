import re

from okonomiyaki.errors import OkonomiyakiError


_R_EGG_NAME = re.compile("""
        (?P<name>^[^.-]+)
        (-(?P<version>[^-]+))
        (-py(?P<pyver>(\d+\.\d+)))
        (-(?P<platform>.+))?
        \.egg$
""", re.VERBOSE)


def parse_filename(path):
    """
    Parse a setuptools egg.

    Returns
    -------
    name : str
        the egg name
    version : str
        the egg version
    python_version : str
        the python version
    platform : str or None
        the platform string, or None for platform-independent eggs.
    """
    m = _R_EGG_NAME.search(path)
    if m:
        platform = m.group("platform")
        return (m.group("name"), m.group("version"), m.group("pyver"),
                platform)
    else:
        raise OkonomiyakiError("Invalid egg name: {0}".format(path))
