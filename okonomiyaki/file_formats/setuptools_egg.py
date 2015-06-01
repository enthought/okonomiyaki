import os.path
import re

from ..errors import OkonomiyakiError
from ._egg_info import _get_default_python_tag
from ._package_info import PackageInfo


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


# Implement the platform string "normalization" as done by
# wheel/setuptools on the original platform string (as returned from
# distutils.util.get_platform or similar)
def _normalize_setuptools_platform_string(platform_string):
    if platform_string is not None:
        platform_string = platform_string.replace("-", "_").replace(".", "_")
    return platform_string


def _get_default_setuptools_abi(platform_string, pyver):
    """ Try to guess the ABI for setuptools eggs from the platform_string
    and pyver parts.

    Parameters
    ----------
    platform_string: str
        The platform part of the setuptools egg filename as a string. If
        None, understood as a cross platform egg (pure python).
    pyver: str
        The python version
    """
    assert pyver in ("2.6", "2.7")

    if platform_string is None:
        return None
    else:
        if (platform_string.startswith("linux")
                or platform_string.startswith("win")
                or platform_string.startswith("macosx")):
            return 'cp{0}{1}m'.format(pyver[0], pyver[2])
        else:
            msg = "Platform string {0!r} not supported".format(platform_string)
            raise ValueError(msg)


class SetuptoolsEggMetadata(object):
    @classmethod
    def from_egg(cls, path):
        filename = os.path.basename(path)
        name, version, pyver, platform = parse_filename(filename)

        python_tag = _get_default_python_tag(None, pyver)

        abi_tag = _get_default_setuptools_abi(platform, pyver)

        if platform is not None:
            platform_tag = _normalize_setuptools_platform_string(platform)
        else:
            platform_tag = platform

        pkg_info = PackageInfo.from_egg(path)

        return cls(name, version, python_tag, abi_tag, platform_tag,
                   pkg_info)

    def __init__(self, name, version, python_tag, abi_tag, platform_tag,
                 pkg_info):
        self.name = name
        self.version = version

        self.python_tag = python_tag
        self.abi_tag = abi_tag
        self.platform_tag = platform_tag

        self._pkg_info = pkg_info

    @property
    def summary(self):
        return self._pkg_info.summary
