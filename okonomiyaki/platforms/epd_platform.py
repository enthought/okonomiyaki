from __future__ import absolute_import

import platform
import sys

from ..bundled.traitlets import HasTraits, Enum
from ..errors import OkonomiyakiError

# Those lists are redundant with legacy spec. We check the consistency in our
# unit-tests
_ARCHBITS_TO_ARCH = {
    "32": "x86",
    "64": "amd64",
    "x86": "x86",
    "x86_64": "amd64",
}

PLATFORM_NAMES = [
    "osx",
    "rh3",
    "rh5",
    "rh6",
    "sol",
    "win",
]

EPD_PLATFORM_SHORT_NAMES = [
    "osx-32",
    "osx-64",
    "rh3-32",
    "rh3-64",
    "rh5-32",
    "rh5-64",
    "rh6-64",
    "sol-32",
    "sol-64",
    "win-32",
    "win-64",
]


class EPDPlatform(HasTraits):
    """
    An sane Canopy/EPD platform representation.

    Example::

        epd_platform = EPDPlatform.from_epd_string("rh5-32")
        assert epd.platform == "rh5"
        assert epd.arch_bits == "32"
        assert epd.arch == "x86"
    """
    platform = Enum(PLATFORM_NAMES)
    """
    Main name of the platform (e.g. 'rh5')
    """
    arch = Enum(["x86", "amd64"])
    """
    Actual architecture (e.g. 'x86')
    """

    @classmethod
    def from_running_system(cls, arch=None):
        """
        Attempt to create an EPDPlatform instance by guessing the running
        platform. May raise an OkonomiyakiError exception

        Parameters
        ----------
        arch: str, None
            If given, must be a valid architecture string (e.g. 'x86'). If
            None, will be guessed from the running python.
        """
        return _guess_epd_platform(arch)

    @classmethod
    def from_epd_string(cls, s):
        """
        Create a new instance from an epd platform string (e.g. 'win-32')
        """
        parts = s.split("-")
        if len(parts) != 2:
            raise OkonomiyakiError("Invalid epd string: {0}".format(s))

        platform_name, arch_bits = parts
        if arch_bits not in _ARCHBITS_TO_ARCH:
            msg = ("Invalid epd string {0!r}: invalid arch {1!r}".
                   format(s, arch_bits))
            raise OkonomiyakiError(msg)
        else:
            arch = _ARCHBITS_TO_ARCH[arch_bits]

        return cls(platform_name, arch)

    def __init__(self, platform, arch, **kw):
        super(EPDPlatform, self).__init__(platform=platform, arch=arch, **kw)

    @property
    def arch_bits(self):
        """
        The number of bits (as a string) of this epd platform.
        """
        if self.arch == "x86":
            return "32"
        else:
            return "64"

    @property
    def short(self):
        return "{0}-{1}".format(self.platform, self.arch_bits)


def applies(platform_string, to='current'):
    """ Returns True if the given platform string applies to the platform
    specified by 'to'."""
    def _parse_component(component):
        component = component.strip()

        parts = component.split("-")
        if len(parts) == 1:
            return parts[0], None
        elif len(parts) == 2:
            return parts[0], parts[1]
        else:
            raise ValueError()

    def _are_compatible(short_left, short_right):
        return short_left == short_right or \
            short_left == "rh" and short_right.startswith("rh") \
            or short_right == "rh" and short_left.startswith("rh") \
            or short_left == "all"

    if isinstance(to, str):
        if to == 'current':
            full = EPDPlatform.from_running_system()
            to_platform = full.platform
            to_arch_bits = full.arch_bits
        elif '-' in to:
            full = EPDPlatform.from_epd_string(to)
            to_platform = full.platform
            to_arch_bits = full.arch_bits
        else:
            if not (to in PLATFORM_NAMES or to == 'rh'):
                raise ValueError("Invalid 'to' argument: {0!r}".format(to))
            to_platform = to
            to_arch_bits = None

    conditions = []

    platform_string = platform_string.strip()
    if platform_string.startswith("!"):
        invert = True
        platform_string = platform_string[1:]
    else:
        invert = False

    platform_strings = [s for s in platform_string.split(",")]
    for platform_string in platform_strings:
        short, bits = _parse_component(platform_string)
        if _are_compatible(short, to_platform):
            if bits is None:
                conditions.append(True)
            else:
                conditions.append(bits == to_arch_bits or to_arch_bits is None)
        else:
            conditions.append(False)

    if invert:
        return not any(conditions)
    else:
        return any(conditions)


def _guess_architecture():
    """
    Returns the architecture of the running python.
    """
    machine = platform.machine()

    if machine in ("AMD64", "x86_64", "x86", "i386", "i686"):
        if sys.maxsize > 2 ** 32:
            return "amd64"
        else:
            return "x86"
    else:
        raise OkonomiyakiError("Unknown machine combination {0!r}".
                               format(machine))


def _guess_epd_platform(arch=None):
    if arch is None:
        arch = _guess_architecture()

    if sys.platform == "win32":
        return EPDPlatform("win", arch)
    elif sys.platform == "darwin":
        return EPDPlatform("osx", arch)
    elif sys.platform.startswith("linux"):
        name, version, _ = platform.dist()
        if name in ("centos", "redhat"):
            parts = version.split(".")
            if not len(parts) == 2:
                raise OkonomiyakiError("Could not parse rh version {0}".
                                       format(version))
            major, _ = parts
            if major == "5":
                return EPDPlatform("rh5", arch)
            elif major == "6":
                return EPDPlatform("rh6", arch)
            else:
                raise OkonomiyakiError("Unknown major version {0}".
                                       format(major))
        else:
            raise OkonomiyakiError("Could not guess platform for distribution "
                                   "{0}".format(name))
    else:
        raise OkonomiyakiError("Could not guess epd platform")
